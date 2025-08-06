__author__ = "Vivek"
__author_email__ = "vivekltp120@gmail.com"
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tf.keras.preprocessing.text import Tokenizer
from tf.keras.preprocessing.sequence import pad_sequences

# Function to clean the text
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'<[^>]+>', ' ', text)  # Remove HTML tags
    text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters and numbers
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.strip()

# Load the dataset
data_path="/media/vivek/WD_HD/Machine_Learning/MachineLearning2018/DataCorpus/research_and_wiki_data/English/Wikipedia_data/wiki_en.txt"

data = pd.read_csv('data_path')

# Sample dataset columns: reviewText, label (1 for positive, 0 for negative)

# Clean the text data
data['cleaned_review'] = data['reviewText'].apply(clean_text)

# Prepare the text and labels
reviews = data['cleaned_review'].values
labels = data['label'].values

# Encode labels
le = LabelEncoder()
labels = le.fit_transform(labels)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(reviews, labels, test_size=0.2, random_state=42)

# Tokenize and pad sequences
max_words = 10000  # Max number of words to keep, based on word frequency
max_len = 100  # Max length of sequences

tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(X_train)

X_train_seq = tokenizer.texts_to_sequences(X_train)
X_test_seq = tokenizer.texts_to_sequences(X_test)

X_train_pad = pad_sequences(X_train_seq, maxlen=max_len)
X_test_pad = pad_sequences(X_test_seq, maxlen=max_len)




# Build the model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=max_words, output_dim=128, input_length=max_len),
    tf.keras.layers.SpatialDropout1D(0.2),  # Dropout to prevent overfitting on noisy data
    tf.keras.layers.LSTM(128, return_sequences=True),  # LSTM to capture sequential dependencies
    tf.keras.layers.GlobalMaxPooling1D(),
    tf.keras.layers.Dense(128, activation='relu'),  # Fully connected layer
    tf.keras.layers.Dropout(0.5),  # Add dropout for regularization
    tf.keras.layers.Dense(1, activation='sigmoid')  # Binary classification
])

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Summary of the model
model.summary()






# Train the model
history = model.fit(X_train_pad, y_train, epochs=8, batch_size=32, validation_split=0.2)

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test_pad, y_test)
print(f"Test Accuracy: {test_acc}")



model.save('unstructured_text_classification_model.h5')

