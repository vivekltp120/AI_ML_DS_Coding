__author__ = "Vivek"
__author_email__ = "vivekltp120@gmail.com"

import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

# Load the plain text data
with open("/media/vivek/WD_HD/Machine_Learning/MachineLearning2018/DataCorpus/research_and_wiki_data/English/Wikipedia_data/wiki_en.txt"
, 'r') as f:
    texts = f.readlines()

# Clean the unstructured text data
def clean_unstructured_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'\@\w+|\#', '', text)  # Remove mentions and hashtags
    text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters and numbers
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces and strip leading/trailing spaces
    return text

texts = [clean_unstructured_text(text) for text in texts]

# Convert text to TF-IDF features
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(texts)


#### Step 2: Apply Clustering

# Define the number of clusters (this is a hyperparameter you need to choose)
num_clusters = 5

# Apply K-means clustering
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(X)

# Get cluster assignments
clusters = kmeans.predict(X)

# Optionally, you can add cluster assignments back to the text data
texts_with_clusters = list(zip(texts, clusters))

# Save results to a file

with open('text_clusters.txt', 'w') as f:
    for text, cluster in texts_with_clusters:
        f.write(f"Cluster {cluster}: {text}\n")

### Example 2: Pre-training for Future Supervised Tasks

#If you plan to use the text data for supervised learning in the future, you can pre-train embeddings with models like BERT or word2vec using unsupervised text.

#### Step 1: Load and Preprocess Plain Text Data

from transformers import BertTokenizer, BertModel
import torch

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to convert text to BERT embeddings
def get_bert_embeddings(texts):
    encoded_inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**encoded_inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()  # Mean pooling

# Get BERT embeddings for the text data
embeddings = get_bert_embeddings(texts)
