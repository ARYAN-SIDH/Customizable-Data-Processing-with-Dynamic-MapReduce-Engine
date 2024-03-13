# sentiment_analysis.py

# Import necessary libraries
from pyspark.sql import SparkSession
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .getOrCreate()

# Load the tweets from Azure Blob Storage
tweets_df = spark.read.json("wasbs://<container_name>@<storage_account_name>.blob.core.windows.net/twitter-data/*.json")

# Initialize the sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Function to compute sentiment score for a text
def get_sentiment_score(text):
    return sia.polarity_scores(text)['compound']

# Register the UDF
spark.udf.register("get_sentiment_score", get_sentiment_score)

# Compute sentiment score for each tweet
sentiment_score_df = tweets_df.selectExpr("id_str", "text", "get_sentiment_score(text) as sentiment_score")

# Convert sentiment score to label
sentiment_score_df = sentiment_score_df.withColumn("label", (sentiment_score_df["sentiment_score"] > 0).cast("integer"))

# Split data into training and testing sets
train_data, test_data = sentiment_score_df.randomSplit([0.8, 0.2], seed=123)

# Create pipeline for sentiment analysis using machine learning
tokenizer = Tokenizer(inputCol="text", outputCol="words")
hashing_tf = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="rawFeatures")
idf = IDF(inputCol=hashing_tf.getOutputCol(), outputCol="features")
lr = LogisticRegression(maxIter=10, regParam=0.01)
pipeline = Pipeline(stages=[tokenizer, hashing_tf, idf, lr])

# Train the model
model = pipeline.fit(train_data)

# Make predictions
predictions = model.transform(test_data)

# Evaluate the model
accuracy = predictions.filter(predictions.label == predictions.prediction).count() / float(test_data.count())
print("Accuracy:", accuracy)

# Write the results to Azure Blob Storage
predictions.write.mode('overwrite').json("wasbs://<container_name>@<storage_account_name>.blob.core.windows.net/twitter-sentiment")

# Stop SparkSession
spark.stop()
