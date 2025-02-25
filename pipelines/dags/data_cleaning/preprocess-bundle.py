import json
import logging
from google.cloud import storage
from io import StringIO
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from gcs_actions import read_data_from_gcs
import dask.dataframe as dd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Example usage
if __name__ == "__main__":
    BUCKET_NAME = "steam-select"
    INPUT_FILE = "raw/bundle_data.json"
    df = read_data_from_gcs(BUCKET_NAME, INPUT_FILE)
    print(df.head())