import os
import pandas as pd
import pyarrow.parquet as pq

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Function to clean the DataFrame
def feature_df_bundle_data(df):
    # PLACE YOUR CODE HERE FOR CLEANING

    # Add new features (Feature Engineering)
    if "release_date" in df.columns:
        df["release_year"] = pd.to_datetime(df["release_date"], errors='coerce').dt.year

    # Extract total number of items in each bundle
    df["total_items"] = df["items"].apply(lambda x: len(x) if isinstance(x, list) else 0)

    # Extract unique game genres from bundles
    df["unique_genres"] = df["items"].apply(lambda x: list(set([item["genre"] for item in x if "genre" in item])) if isinstance(x, list) else [])

    # Count unique genres per bundle
    df["num_unique_genres"] = df["unique_genres"].apply(len)

    # Identify High Discount Bundles (More than 50% off)
    df["high_discount_flag"] = df["bundle_discount"].apply(lambda x: 1 if x > 50 else 0)

    # Calculate Price per Game in the Bundle
    df["price_per_item"] = df.apply(lambda row: row["bundle_final_price"] / row["total_items"] if row["total_items"] > 0 else 0, axis=1)

    # Calculate Average Discount Per Item
    df["avg_discount_per_item"] = df.apply(lambda row: row["bundle_discount"] / row["total_items"] if row["total_items"] > 0 else 0, axis=1)

    print(f"The shape of the item data after preprocessed {df.shape}")

    return df

# Function to read the file in batches
def feature_engineering_cleaned_bundle_file(file_name):
    data_file_path = os.path.join(PROCESSED_DATA_DIR, file_name)
    write_to_path = os.path.join(PROCESSED_DATA_DIR, file_name.replace('.parquet', '_cleaned.parquet'))

    parquet_file = pq.ParquetFile(data_file_path)
    
    num_row_groups = parquet_file.num_row_groups
    print(f"Total row groups in parquet file: {num_row_groups}")

    cleaned_chunks = []
    for i in range(num_row_groups):  # Iterate over row groups instead of rows
        chunk = parquet_file.read_row_group(i).to_pandas()
        cleaned_chunk = feature_df_bundle_data(chunk)  # Apply cleaning function
        cleaned_chunks.append(cleaned_chunk)

    cleaned_df = pd.concat(cleaned_chunks, ignore_index=True)
    
    # Save cleaned data
    cleaned_df.to_parquet(write_to_path, compression='snappy')

    del cleaned_df
    
    print("Dataset preprocessed and saved to:", write_to_path)

    return write_to_path

if __name__ == "__main__":
    feature_engineering_cleaned_bundle_file('bundle_data.parquet')
