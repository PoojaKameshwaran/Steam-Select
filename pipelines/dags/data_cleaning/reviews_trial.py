import pandas as pd
import json
import logging
from google.cloud import storage
from io import StringIO
from airflow.providers.google.cloud.hooks.gcs import GCSHook

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to clean the DataFrame
def clean_data(df):
    logging.info("Starting data cleaning process...")
    
    # Drop duplicate records
    df = df.drop_duplicates()
    
    # Trim whitespace from string columns
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())
    
    # Convert timestamp to date format
    df["date"] = pd.to_datetime(df["date"], unit="ms").dt.date
    
    logging.info("Summary of null values before cleaning:\n%s", df.isnull().sum())
    
    # Drop non-essential columns
    df.drop(columns=['compensation', 'user_id','username', 'products', 'page_order', 'page', 'early_access'], inplace=True)
    logging.info("Dropped non-essential columns: compensation, user_id, username, products, page_order, page, and early_access")
    
    # Handle missing values and typecast columns
    df['found_funny'] = df['found_funny'].fillna(0).astype('int64')
    df['hours'] = df['hours'].fillna(0.0)
    logging.info("Handled missing values and typecasted relevant columns.")
    
    # Rename columns for better readability
    df.columns = ['date', 'found_funny', 'hours', 'item_id', 'item_count', 'review']
    logging.info("Renamed columns for consistency and readability.")
    
    logging.info("Data cleaning completed.")
    return df

# Function to read JSON file from GCS in chunks
def read_json_from_gcs(bucket_name, file_name, chunk_size=10000):
    logging.info("Reading JSON file from GCS in chunks: gs://%s/%s", bucket_name, file_name)

    gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")

    # Stream file content
    file_content = gcs_hook.download(bucket_name, file_name)

    # Decode bytes to string and process line by line
    batch = []
    for i, line in enumerate(file_content.decode("utf-8").splitlines()):
        batch.append(json.loads(line.strip()))

        # Yield a chunk of data every `chunk_size` lines
        if (i + 1) % chunk_size == 0:
            yield pd.DataFrame(batch)
            batch = []  # Clear batch

    # Yield any remaining data
    if batch:
        yield pd.DataFrame(batch)

# Function to process and store cleaned data back to GCS
def process_and_store_gcs(bucket_name, input_file, output_file, chunk_size= 10000):
    logging.info("Starting streaming data processing...")

    gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")

    for chunk in read_json_from_gcs(bucket_name, input_file, chunk_size=chunk_size):
        logging.info("Processing a chunk of size %d...", len(chunk))
        df_cleaned = clean_data(chunk)  # Clean the chunk

        # Convert to JSON (append mode)
        cleaned_json = df_cleaned.to_json(orient="records", lines=True)

        # Upload each chunk separately (append mode)
        gcs_hook.upload(bucket_name, output_file, data=cleaned_json, mime_type="application/json")
    
    logging.info("Finished processing and storing cleaned data in GCS.")

# Example usage
if __name__ == "__main__":
    BUCKET_NAME = "steam-select"
    INPUT_FILE = "reviews.json"
    OUTPUT_FILE = "cleaned/cleaned_reviews.json"
    process_and_store_gcs(BUCKET_NAME, INPUT_FILE, OUTPUT_FILE)

