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

def upload_multiple_files(bucket_name, destination_folder, file_path_names):
    """
    Uploads multiple files to Google Cloud Storage.

    :param bucket_name: GCS bucket name
    :param destination_folder: Target folder in GCS bucket
    :param file_path_names: List of local file paths to upload
    """
    for file_path in file_path_names:
        file_name = os.path.basename(file_path)
        destination_blob_name = os.path.join(destination_folder, file_name)
        upload_large_file_to_gcp(bucket_name, file_path, destination_blob_name)

if __name__ == "__main__":
    
    file_paths = [
        # "d:\\Learning\\MlOps\\Steam-Select\\data\\processed\\raw_item_metadata.parquet"
        ""
    ]
    # Upload files using the modularized function
    upload_multiple_files("steam-select", "staging", file_paths)
    print("Successfully uploaded files to staging")
