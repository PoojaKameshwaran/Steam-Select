import os
from google.cloud import storage

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)

def download_from_gcp(bucket_name, blob_path):
    try:
        # Set environment variables for authentication
        KEY_PATH = os.path.join(PROJECT_DIR, "config", "key.json")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH
        print(PROJECT_DIR)
        # Google Cloud setup
        try:
            storage_client = storage.Client()
        except Exception as e:
            return None

        bucket = storage_client.bucket(bucket_name)

        # Get the specific blob
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            return None
        
        # Extract filename from blob path
        filename = os.path.basename(blob_path)
        
        # Download the file directly to the specified folder
        destination_file_path = os.path.join(DATA_DIR, filename)
        blob.download_to_filename(destination_file_path)
        
        print(f"Successfully loaded at {destination_file_path}")
        return destination_file_path
    
    except Exception as e:
        return None

if __name__ == "__main__":

    print("Running locally")
    download_from_gcp("steam-select","raw/reviews.json")