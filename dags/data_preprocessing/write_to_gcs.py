import os
from google.cloud import storage

# Define paths
PROJECT_DIR = os.getcwd()
KEY_PATH = os.path.join(PROJECT_DIR, "config", "key.json")

# Authenticate with GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

def upload_to_gcp(bucket_name, source_file_path, destination_blob_name):
    """
    Uploads a file to Google Cloud Storage.

    :param bucket_name: GCS bucket name
    :param source_file_path: Local path to the file to upload
    :param destination_blob_name: Target path in GCS bucket
    """
    try:
        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_filename(source_file_path)
        print(f"File {source_file_path} uploaded to {destination_blob_name} in bucket {bucket_name}.")
    
    except Exception as e:
        print(f"Error uploading file to GCS: {e}")


if __name__ == "__main__":

    print("Running locally")
    # print("Uploading ITEM_METADATA")
    # upload_to_gcp("steam-select","staging/item_metadata.parquet")
    # print("Successfully uploaded ITEM_METADATA to staging")
    # print("Uploading BUNDLE_DATA")
    # upload_to_gcp("steam-select", "staging/bundle_data.parquet")
    # print("Successfully uploaded ITEM_METADATA to staging")
    print("Uploading REVIEWS")
    upload_to_gcp("steam-select", "staging/reviews.parquet")
    print("Successfully loaded REVIEWS to staging")