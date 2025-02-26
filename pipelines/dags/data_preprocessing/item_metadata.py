import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np

def clean_sentiment(s):
    if re.search(r'\d+\s+user review', s, re.IGNORECASE):
        return "unknown"
    else:
        return s.strip().lower()


df = pd.read_csv(r"C:\GitHub\Steam-Select\data\raw\ITEM_METADATA.csv")
print(df.shape)
print(df.head())

# Info about the dataset
print(df.info())

# Check for duplicate values
print(df.duplicated())

# Check and Handle missing values
print(df.isnull().sum())
df = df.dropna(subset=['app_name', 'genres'])
df = df.drop(columns=['tags', 'reviews_url', 'specs', 'price', 'url', 'publisher', 'release_date', 'discount_price', 'metascore', 'developer', 'title', 'early_access'])
df['sentiment'] = df['sentiment'].fillna("unknown").apply(clean_sentiment)
print(df.isnull().sum())

sentiment_mapping = {
    'unknown': -4,
    'overwhelmingly negative': -3,
    'very negative': -2,
    'mostly negative': -1,
    'negative': -1,
    'mixed': 0,
    'positive': 1,
    'mostly positive': 2,
    'very positive': 3,
    'overwhelmingly positive': 4
}
df['sentiment_score'] = df['sentiment'].map(sentiment_mapping)
print(df[['sentiment', 'sentiment_score']].head())

