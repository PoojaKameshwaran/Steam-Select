import os
import pandas as pd
import re
import yaml
import ast  

# Function to clean text values
def clean_text(s):
    if re.search(r'\d+\s+user review', s, re.IGNORECASE):
        return "unknown"
    else:
        return s.strip().lower()


# Function to clean sentiment values
def clean_sentiment(s):
    if pd.isna(s):
        return "unknown"
    return s.strip().lower()


# Function to clean the DataFrame
def clean_data(df):
    print("\n📌 Data Shape Before Cleaning:", df.shape)
    print(df.head())

    # Info about the dataset
    print("\n📌 Data Info:")
    print(df.info())

    # Check for duplicate values
    print("\n📌 Checking for Duplicates:")
    print(df.duplicated().sum())

    # Check and Handle missing values
    print("\n📌 Checking Missing Values:")
    print(df.isnull().sum())

    # Drop rows with missing values in critical columns
    df = df.dropna(subset=['app_name', 'genres'])

    # Drop unnecessary columns
    columns_to_drop = [
        'tags', 'reviews_url', 'specs', 'price', 'url',
        'publisher', 'release_date', 'discount_price',
        'metascore', 'developer', 'title', 'early_access'
    ]
    df = df.drop(columns=columns_to_drop, errors='ignore')  # Ignore errors if columns don't exist

    rename_mapping = {
        "ID": "Game_ID",
        "app_name": "Game"
    }
    df.rename(columns=rename_mapping, inplace=True)
    
    # Handle missing values in sentiment column
    df['sentiment'] = df['sentiment'].fillna("unknown").apply(clean_sentiment)

    print("\n📌 Missing Values After Cleaning:")
    print(df.isnull().sum())

    # Sentiment mapping to numerical scores
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

    print("\n✅ Sentiment Mapping Applied:")
    print(df[['sentiment', 'sentiment_score']].head())

    return df  # Return the cleaned DataFrame


