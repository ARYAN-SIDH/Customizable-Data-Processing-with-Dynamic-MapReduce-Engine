# visualization.py

import matplotlib.pyplot as plt
import pandas as pd
from azure.storage.blob import BlobServiceClient
import json
from datetime import datetime

# Azure Blob Storage connection string
connection_string = "<your_connection_string>"
container_name = "twitter-sentiment"

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Read predictions from Azure Blob Storage
blob_list = container_client.list_blobs()
sentiments = []

for blob in blob_list:
    blob_client = container_client.get_blob_client(blob)
    blob_data = blob_client.download_blob().readall().decode("utf-8")
    predictions = json.loads(blob_data)
    sentiments.extend(predictions)

# Extract sentiment scores and timestamps
sentiment_scores = [row["prediction"] for row in sentiments]
timestamps = [datetime.strptime(row["created_at"], "%a %b %d %H:%M:%S %z %Y") for row in sentiments]

# Convert to DataFrame
df = pd.DataFrame({"Timestamp": timestamps, "Sentiment": sentiment_scores})

# Plot sentiment distribution
plt.figure(figsize=(12, 6))
df["Sentiment"].value_counts().plot(kind='bar', color=['skyblue', 'salmon'], edgecolor='black', alpha=0.7)
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.title('Sentiment Distribution')
plt.xticks([0, 1], ['Negative', 'Positive'], rotation=0)
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot sentiment proportion (pie chart)
plt.figure(figsize=(8, 8))
df["Sentiment"].value_counts().plot(kind='pie', labels=['Positive', 'Negative'], autopct='%1.1f%%', colors=['skyblue', 'salmon'], startangle=140)
plt.title('Sentiment Proportion')
plt.axis('equal')
plt.show()

# Plot sentiment over time (time series)
plt.figure(figsize=(12, 6))
df.set_index('Timestamp').resample('H').mean().plot(marker='o', color='teal')
plt.xlabel('Time')
plt.ylabel('Sentiment Score')
plt.title('Sentiment Over Time')
plt.grid(True)
plt.show()
