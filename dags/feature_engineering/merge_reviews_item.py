import os
import pandas as pd
import pyarrow.parquet as pq

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Function to clean and merge two DataFrames
def merge_reviews_item_data(reviews_df, item_df):
    print(reviews_df.head())
    print(item_df.head())
    # Define the mapping for sentiment string values
    sentiment_map = {
        'Mostly Positive': 4.5,
        'Very Positive': 4,
        'Positive': 3.5,
        'Mixed': 3,
        'Overwhelmingly Positive': 5,
        'Negative': 2.5,
        'Very Negative': 2,
        'Mostly Negative': 1.5,
        'Overwhelmingly Negative': 1
    }

    # Step 1: Map sentiment strings to corresponding numeric values
    item_df['sentiment'] = item_df['sentiment'].map(sentiment_map)

    # Step 2: For ids with no sentiment in item_metadata, use the sentiment_score from reviews
    item_df = item_df.merge(reviews_df[['id', 'sentiment_score']], left_on='Game_ID', right_on='id', how='left')
    item_df['sentiment'] = item_df['sentiment'].combine_first(reviews_df['sentiment_score'])
    print("This is the one")
    print(item_df.columns)
    print(item_df.head())

    # Step 3: Replace any null values in sentiment column with 3
    item_df['sentiment'] = item_df['sentiment'].fillna(3)

    # Step 4: Remove the temporary sentiment_score column and return the updated dataframe
    item_df = item_df.drop(columns=['id', 'sentiment_score'])

    print(f"Final Item Dataset: {item_df.head()}")
    return item_df

# Function to read, preprocess, merge, and save the cleaned data
def merge_reviews_item_file(file_paths):
    # Load the two parquet files into DataFrames
    reviews_df = pd.read_parquet(file_paths[0])
    item_df = pd.read_parquet(file_paths[1])

    print(f"Loaded dataframes with shapes: {reviews_df.shape} and {item_df.shape}")

    # Preprocess and merge the DataFrames
    merged_df = merge_reviews_item_data(reviews_df, item_df)

    # Define output path for the cleaned and merged DataFrame
    output_file_path = os.path.join(PROCESSED_DATA_DIR, "reviews_item_cleaned.parquet")

    # Save the merged and cleaned data to a parquet file
    merged_df.to_parquet(output_file_path, compression='snappy')

    del merged_df  # Free up memory

    print(f"Dataset preprocessed, merged, and saved to: {output_file_path}")
    return output_file_path

if __name__ == "__main__":

    file_paths = [
        "D:\\Learning\\MlOps\\Steam-Select\\data\\processed\\reviews_cleaned.parquet",
        "D:\\Learning\\MlOps\\Steam-Select\\data\\processed\\item_metadata_cleaned.parquet"
    ]

    merge_reviews_item_file(file_paths)
