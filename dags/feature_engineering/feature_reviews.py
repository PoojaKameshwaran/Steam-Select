import os
import pandas as pd
import pyarrow.parquet as pq

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Function to clean the DataFrame
def feature_df_reviews_data(df):











    # PLACE YOUR CODE HERE FOR CLEANING







    
    print(f"The shape of the item data after preprocessed {df.shape}")

    return df

# Function to read the file in batches
def feature_engineering_cleaned_reviews_file(file_name):
    data_file_path = os.path.join(PROCESSED_DATA_DIR, file_name)
    write_to_path = os.path.join(PROCESSED_DATA_DIR, file_name.replace('.parquet', '_cleaned.parquet'))

    parquet_file = pq.ParquetFile(data_file_path)
    
    num_row_groups = parquet_file.num_row_groups
    print(f"Total row groups in parquet file: {num_row_groups}")

    cleaned_chunks = []
    for i in range(num_row_groups):  # Iterate over row groups instead of rows
        chunk = parquet_file.read_row_group(i).to_pandas()
        cleaned_chunk = feature_df_reviews_data(chunk)  # Apply cleaning function
        cleaned_chunks.append(cleaned_chunk)

    cleaned_df = pd.concat(cleaned_chunks, ignore_index=True)
    
    # Save cleaned data
    cleaned_df.to_parquet(write_to_path, compression='snappy')

    del cleaned_df
    
    print("Dataset preprocessed and saved to:", write_to_path)

    return write_to_path


if __name__ == "__main__":
    feature_engineering_cleaned_reviews_file('reviews.parquet')