import os
import pandas as pd
import re
from custom_logging import get_logger

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = get_logger('Data_Cleaning')

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Function to clean the DataFrame
def clean_item_data(df):
    # PLACE YOUR CODE HERE FOR CLEANING
    columns_to_drop = [
        'tags', 'reviews_url', 'specs', 'price', 'url',
        'publisher', 'release_date', 'discount_price',
        'metascore', 'developer', 'title', 'early_access'
    ]
    df = df.drop(columns=columns_to_drop, errors='ignore')  # Ignore errors if columns don't exist

    print("\n📌 Data Shape Before Cleaning:", df.shape)
    print(df.head())

    # Info about the dataset
    print("\n📌 Data Info:")
    print(df.info())

    # Convert unhashable columns (lists) to tuples
    for col in ['genres']:  # Adjust based on actual list-type columns
        df[col] = df[col].apply(lambda x: tuple(x) if isinstance(x, list) else x)

    df['id'] = df['id'].astype('Int64')

    # Check for duplicates
    print("\n📌 Checking for Duplicates:")
    print(df.duplicated().sum())

    # Check and Handle missing values
    print("\n📌 Checking Missing Values:")
    print(df.isnull().sum())

    # Drop rows with missing values in critical columns
    df = df.dropna(subset=['app_name', 'genres'])

    rename_mapping = {
        "id": "Game_ID",
        "app_name": "Game"
    }
    df.rename(columns=rename_mapping, inplace=True)


    # Function to clean sentiment column
    def clean_sentiment(value):
        if isinstance(value, str) and re.search(r'unknown|\d+ user reviews', value, re.IGNORECASE):
            return "Mixed"
        return value

    # Apply cleaning function
    df['sentiment'] = df['sentiment'].apply(clean_sentiment)


    print(f"The shape of the item data after cleaned {df.shape}")

    return df

# Function to read the file in batches
def read_and_clean_item_file(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(RAW_DATA_DIR, file_name)
    file_name_without_ext = os.path.splitext(os.path.basename(data_file_path))[0]
    chunk_size = 100000
    chunks = pd.read_json(data_file_path, orient='records', lines=True, chunksize=chunk_size)
    
    cleaned_chunks = [clean_item_data(chunk) for chunk in chunks]
    
    cleaned_df = pd.concat(cleaned_chunks, ignore_index=True)
    
    write_to_path = os.path.join(PROCESSED_DATA_DIR, file_name_without_ext + '.parquet')
    
    try:
        cleaned_df.to_parquet(write_to_path, compression='snappy')
    except Exception as e:
        for col in cleaned_df.select_dtypes(include=['object']).columns:
            cleaned_df[col] = cleaned_df[col].astype(str)
        
        # Retry saving after converting object columns to string
        cleaned_df.to_parquet(write_to_path, compression='snappy')
    
    print("Dataset cleaned successfully...")
    logger.info("Dataset cleaned successfully - Item")
    print("Dataset loaded to data/processed")
    logger.info("Dataset loaded to data/processed - Item")
    
    # Remove DataFrame from memory
    del cleaned_df

    return write_to_path

if __name__ == "__main__":
    read_and_clean_item_file('item_metadata.json')