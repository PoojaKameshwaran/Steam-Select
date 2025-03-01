import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Function to clean the DataFrame
def clean_reviews_data(df):
    # Drop duplicate records
    df.drop_duplicates(inplace=True)

    # Trim whitespace from string columns
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

    # Formatting the date
    df["date"] = pd.to_datetime(df["date"], unit="ms").dt.date

    # Drop non-essential features
    df.drop(columns=['compensation', 'user_id', 'username', 'found_funny',
                     'hours', 'page_order', 'page', 'early_access', 'products', 'date'], inplace=True)
    
    # Typecasting
    df['product_id'] = df['product_id'].fillna(0).astype('int64')
    
    # Renaming column names
    df.columns = ['id', 'review']

    return df

# Function to read the file in batches
def read_and_clean_reviews_file(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(RAW_DATA_DIR, file_name)
    file_name_without_ext = os.path.splitext(os.path.basename(data_file_path))[0]
    chunk_size = 100000
    chunks = pd.read_json(data_file_path, orient='records', lines=True, chunksize=chunk_size)
    
    cleaned_chunks = [clean_reviews_data(chunk) for chunk in chunks]
    
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
    print("Dataset loaded to data/processed")
    
    # Remove DataFrame from memory
    del cleaned_df

    return write_to_path


if __name__ == "__main__":
    read_and_clean_reviews_file('reviews.json')
