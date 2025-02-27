import os
from google.cloud import storage

# Define paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY_PATH = os.path.join(PROJECT_DIR, "config", "key.json")

# Authenticate with GCP
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

def upload_large_file_to_gcp(bucket_name, source_file_path, destination_blob_name, chunk_size=10 * 1024 * 1024):
    """
    Uploads a large file to Google Cloud Storage using chunked and resumable upload.

    :param bucket_name: GCS bucket name
    :param source_file_path: Local path to the file to upload
    :param destination_blob_name: Target path in GCS bucket
    :param chunk_size: Chunk size for upload (default: 10MB)
    """
    try:
        # Initialize GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Set chunk size for large file uploads
        blob.chunk_size = chunk_size  # 10MB chunks

        # Upload the file with a resumable upload
        with open(source_file_path, "rb") as file_obj:
            blob.upload_from_file(file_obj, rewind=True)
        
        print(f"File {source_file_path} uploaded to {destination_blob_name} in bucket {bucket_name}.")

    except Exception as e:
        print(f"Error uploading file to GCS: {e}")


if __name__ == "__main__":
    print("Running locally")
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the data file (assuming it's at: root/data/processed/reviews.parquet)
    folder_path = os.path.join(script_dir, '..', '..', 'data', 'processed')

    # Upload Reviews file using optimized large file upload
    print("Uploading REVIEWS")
    source_file = os.path.join(folder_path, "reviews.parquet")
    print(source_file)
    
    upload_large_file_to_gcp("steam-select", source_file, "staging/reviews.parquet")
    print("Successfully uploaded REVIEWS to staging")