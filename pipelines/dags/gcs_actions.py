import dask.dataframe as dd
import io
import logging
from airflow.providers.google.cloud.hooks.gcs import GCSHook
import pickle
import json
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_data_from_gcs(bucket_name, blob_name, chunk_size=500000):
    """
    Reads a CSV or JSON file directly into a Dask DataFrame from Google Cloud Storage.
    
    Args:
    bucket_name (str): Name of the GCS bucket.
    blob_name (str): The specific blob (file path in GCS) to read.
    chunk_size (int): Number of rows to process per chunk.

    Returns:
    dask.dataframe.DataFrame: Dask DataFrame read from the file.
    """
    logging.info(f"Attempting to read from GCS: {bucket_name}/{blob_name}")
    hook = GCSHook(gcp_conn_id='google_cloud_default')
    data = hook.download(bucket_name, blob_name)

    # Determine file type based on extension
    if blob_name.endswith('.csv'):
        df = dd.read_csv(io.StringIO(data), blocksize=chunk_size)
    elif blob_name.endswith('.json'):
        df = dd.read_json(io.StringIO(data), blocksize=chunk_size, orient='records', lines=True)
    else:
        logging.error(f"Unsupported file format: {blob_name}")
        raise ValueError("Unsupported file format. Only .csv and .json are supported.")
    
    logging.info(f"Successfully read data from {blob_name}")
    return df

def save_data_to_gcs(df, bucket_name, file_name):
    """Save a Dask DataFrame as a CSV or JSON file in Google Cloud Storage."""
    hook = GCSHook(gcp_conn_id='google_cloud_default')

    # Write Dask dataframe to a temporary file
    if file_name.endswith('.csv'):
        df.to_csv('/tmp/output-*.csv', index=False, single_file=True)
        content_type = 'text/csv'
    elif file_name.endswith('.json'):
        df.to_json('/tmp/output-*.json', orient='records', lines=True, single_file=True)
        content_type = 'application/json'
    else:
        logging.error(f"Unsupported file format for saving: {file_name}")
        raise ValueError("Unsupported file format. Only .csv and .json are supported.")
    
    # Upload the resulting file to GCS
    local_file_path = '/tmp/output-*.csv' if file_name.endswith('.csv') else '/tmp/output-*.json'
    hook.upload(bucket_name, file_name, local_file_path, content_type=content_type)
    logging.info(f"Saved {file_name} to GCS.")

def save_plot_to_gcs(bucket_name, plot_name):
    """Save the current matplotlib plot to Google Cloud Storage in a specific folder."""
    hook = GCSHook(gcp_conn_id='google_cloud_default')
    plot_image = io.BytesIO()
    plt.savefig(plot_image, format='png')
    plot_image.seek(0)
    hook.upload(bucket_name, f"weather_data_plots/{plot_name}.png", plot_image, content_type='image/png')
    logging.info(f"Plot {plot_name} saved to GCS in folder weather_data_plots.")

def save_object_to_gcs(bucket_name, object_data, destination_path):
    """Save a Python object to GCS as a pickle file."""
    hook = GCSHook(gcp_conn_id='google_cloud_default')
    try:
        with io.BytesIO() as f:
            pickle.dump(object_data, f)
            f.seek(0)
            hook.upload(bucket_name, destination_path, f, content_type='application/octet-stream')
        logging.info(f"Object saved to GCS at {destination_path}")
    except Exception as e:
        logging.error(f"Failed to save object to GCS at {destination_path}: {e}")

def load_object_from_gcs(bucket_name, source_path):
    """Load a Python object from a pickle file in GCS."""
    hook = GCSHook(gcp_conn_id='google_cloud_default')
    try:
        data = hook.download(bucket_name, source_path)
        with io.BytesIO(data) as f:
            return pickle.load(f)
    except Exception as e:
        logging.error(f"Failed to load object from GCS at {source_path}: {e}")
        return None

def save_model_to_gcs(model, bucket_name, file_name):
    """
    Save a trained model as a pickle file in Google Cloud Storage.
    """
    logging.info(f"Saving model to GCS bucket {bucket_name} at {file_name}")
    
    # Initialize the GCSHook
    hook = GCSHook(gcp_conn_id='google_cloud_default')
    
    # Serialize the model into a pickle object
    output = io.BytesIO()
    pickle.dump(model, output)
    output.seek(0)
    
    # Upload the pickle object to GCS
    hook.upload(bucket_name, file_name, output, content_type='application/octet-stream')
    logging.info(f"Model successfully saved to GCS: gs://{bucket_name}/{file_name}")

def upload_to_gcs(bucket_name, source_path, destination_blob):
    """
    Upload files to Google Cloud Storage.
    """
    try:
        hook = GCSHook(gcp_conn_id='google_cloud_default')
        hook.upload(bucket_name, destination_blob, source_path)
        logging.info(f"Uploaded {source_path} to {bucket_name}/{destination_blob}")
    except Exception as e:
        logging.error(f"Error uploading {source_path} to GCS: {e}")
        raise