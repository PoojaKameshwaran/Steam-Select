import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from custom_logging import get_logger

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = get_logger('Data_Cleaning')

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Function to clean the DataFrame
def clean_users_data(df):
    # Drop duplicate records
    user_df = df.drop_duplicates(subset=['username', 'product_id']).copy()

    # Reset the index to create a user_id column starting from 1
    # user_df.reset_index(drop=True, inplace=True)
    # user_df['user_id'] = user_df.index + 1

    # Rename 'product_id' to 'game_id'
    user_df.rename(columns={'product_id': 'game_id'}, inplace=True)

    # Encoding user_id and game_id
    user_encoder = LabelEncoder()
    # game_encoder = LabelEncoder()

    user_df['user_id'] = user_encoder.fit_transform(user_df['username'])
    # user_df['game_id'] = game_encoder.fit_transform(user_df['product_id'])

    # # user_df = user_df.dropna()

    # Select relevant columns
    user_df = user_df[['user_id', 'username', 'game_id', 'hours']]
    user_df = user_df.dropna()

    # Count unique game_id for each user_id
    user_df['count_games'] = user_df.groupby('user_id')['game_id'].transform('nunique')

    return df

# Function to read the file in batches
def read_and_clean_users_file(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(RAW_DATA_DIR, file_name)
    file_name_without_ext = os.path.splitext(os.path.basename(data_file_path))[0]
    chunk_size = 100000
    chunks = pd.read_json(data_file_path, orient='records', lines=True, chunksize=chunk_size)
    
    cleaned_chunks = [clean_users_data(chunk) for chunk in chunks]
    
    cleaned_df = pd.concat(cleaned_chunks, ignore_index=True)
    
    write_to_path = os.path.join(PROCESSED_DATA_DIR, 'users_cleaned' + '.parquet')
    
    try:
        cleaned_df.to_parquet(write_to_path, compression='snappy')
    except Exception as e:
        for col in cleaned_df.select_dtypes(include=['object']).columns:
            cleaned_df[col] = cleaned_df[col].astype(str)
        
        # Retry saving after converting object columns to string
        cleaned_df.to_parquet(write_to_path, compression='snappy')
    
    print("Dataset cleaned successfully...")
    logger.info("Dataset cleaned successfully - Users")
    print("Dataset loaded to data/processed")
    logger.info("Dataset loaded to data/processed - Users")
    
    # Remove DataFrame from memory
    del cleaned_df

    return write_to_path


if __name__ == "__main__":
    read_and_clean_users_file('reviews.json')
