import tweepy
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from io import BytesIO
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Function to authenticate with Twitter API
def authenticate_twitter_api(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

# Function to collect tweets using Twitter API
def collect_tweets(api, query, max_tweets):
    tweets = []
    for tweet in tweepy.Cursor(api.search, q=query, tweet_mode='extended').items(max_tweets):
        tweets.append(tweet._json)
    return tweets

# Function for text preprocessing
def preprocess_text(text):
    # Remove special characters and URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    
    # Tokenization
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    
    # Stemming
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    
    # Join tokens back into a single string
    preprocessed_text = ' '.join(stemmed_tokens)
    
    return preprocessed_text

# Function to upload data to Azure Blob Storage
def upload_data_to_blob_storage(connection_string, container_name, data):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Define a unique name for the blob
    blob_name = "twitter_data.json"

    # Convert data to JSON format
    json_data = json.dumps(data)

    # Convert JSON data to bytes
    bytes_data = json_data.encode('utf-8')

    # Upload data to blob storage
    try:
        with BytesIO(bytes_data) as data_stream:
            container_client.upload_blob(name=blob_name, data=data_stream)
        print("Data uploaded successfully to Azure Blob Storage.")
    except Exception as e:
        print(f"An error occurred while uploading data to Azure Blob Storage: {str(e)}")

# Twitter API credentials
consumer_key = "<your_consumer_key>"
consumer_secret = "<your_consumer_secret>"
access_token = "<your_access_token>"
access_token_secret = "<your_access_token_secret>"

# Azure Blob Storage connection string
connection_string = "<your_connection_string>"

# Query parameters for Twitter API
query = "#datascience"  # Example query
max_tweets = 1000  # Example maximum number of tweets to collect

# Authenticate with Twitter API
api = authenticate_twitter_api(consumer_key, consumer_secret, access_token, access_token_secret)

# Collect tweets
tweets = collect_tweets(api, query, max_tweets)

# Preprocess tweets
preprocessed_tweets = []
for tweet in tweets:
    preprocessed_tweet = preprocess_text(tweet['full_text'])
    preprocessed_tweets.append(preprocessed_tweet)

# Upload data to Azure Blob Storage
upload_data_to_blob_storage(connection_string, "twitter-data", preprocessed_tweets)
