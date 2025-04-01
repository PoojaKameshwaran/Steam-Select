import os
from google.cloud import storage

try:
    from custom_logging import get_logger
    logger = get_logger('Data_Download')
except:
    import logging as logger

def download_from_gcp(bucket_name, blob_paths, PROJECT_DIR, DATA_DIR):
    try:
        # Set environment variables for authentication
        KEY_PATH = os.path.join(PROJECT_DIR, "config", "key.json")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH
        
        # Google Cloud setup
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        downloaded_files = []
        
        for blob_path in blob_paths:
            blob = bucket.blob(blob_path)
            
            if not blob.exists():
                print(f"Blob {blob_path} does not exist.")
                logger.error(f"Blob {blob_path} does not exist.", exc_info=True)
                continue
            
            # Extract filename from blob path
            filename = os.path.basename(blob_path)
            
            # Download the file directly to the specified folder
            destination_file_path = os.path.join(DATA_DIR, filename)
            blob.download_to_filename(destination_file_path)
            
            print(f"Successfully downloaded {blob_path} to {destination_file_path}")
            logger.info(f"Successfully downloaded {blob_path} to {destination_file_path}")
            downloaded_files.append(destination_file_path)
        
        return downloaded_files
    except Exception as e:
        print(f"Error: {e}")
        logger.error("Failed to download data", exc_info=True)
        return []

if __name__ == "__main__":
    
    blob_paths = ["raw/item_metadata.json","raw/bundle_data.json"]

    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Set up project directories
    DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
    os.makedirs(DATA_DIR, exist_ok=True)

    downloaded_files = download_from_gcp("steam-select", blob_paths, PROJECT_DIR, DATA_DIR)

