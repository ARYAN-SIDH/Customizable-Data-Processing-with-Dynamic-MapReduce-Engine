# preprocessing.py

import re
import string
import html
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from spellchecker import SpellChecker
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

def preprocess_text(text, azure_key, azure_endpoint):
    # Remove HTML tags
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    
    # Tokenization with TweetTokenizer
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    tokens = tokenizer.tokenize(text)
    
    # Remove punctuation and lowercase
    tokens = [token.lower() for token in tokens if token not in string.punctuation]
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Remove rare words
    word_frequency = nltk.FreqDist(tokens)
    rare_words = set(word for word in tokens if word_frequency[word] < 5)
    tokens = [token for token in tokens if token not in rare_words]
    
    # Handle negations
    negation_words = ['not', 'no', 'never']
    negated = False
    cleaned_tokens = []
    for token in tokens:
        if token in negation_words:
            negated = True
        elif negated and token not in string.punctuation:
            token = "not_" + token
        cleaned_tokens.append(token)
    
    # Lemmatization using part-of-speech tagging
    lemmatizer = WordNetLemmatizer()
    tagged_tokens = nltk.pos_tag(cleaned_tokens)
    preprocessed_tokens = []
    for token, tag in tagged_tokens:
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        preprocessed_tokens.append(lemmatizer.lemmatize(token, pos=pos))

    contractions = {
        "n't": "not",
        "'s": "is",
        "'re": "are",
        "'m": "am",
        "'ll": "will",
        "'ve": "have",
        "'d": "would"
    }
    tokens = [contractions.get(token, token) for token in tokens]
    
    # Handle abbreviations and misspelled words
    spell = SpellChecker()
    corrected_tokens = [spell.correction(token) for token in preprocessed_tokens]
    
    # Join tokens back into a single string
    preprocessed_text = ' '.join(corrected_tokens)
    
    # Check language using Azure Text Analytics
    azure_credential = AzureKeyCredential(azure_key)
    text_analytics_client = TextAnalyticsClient(endpoint=azure_endpoint, credential=azure_credential)
    language_detection = text_analytics_client.detect_language(documents=[preprocessed_text])
    
    # If language is not English, return None
    if language_detection[0].primary_language.name != "English":
        return None
    
    return preprocessed_text
