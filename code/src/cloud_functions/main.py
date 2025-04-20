import pickle
import io
import requests
from datetime import datetime, timezone
from google.cloud import bigquery, storage
import google.auth
import google.auth.transport.requests

def gcs_trigger(event, context):
    bucket_name = event['bucket']
    file_name = event['name']

    if "best_model/hybrid_recommender/artifacts/base_model/model_v1.pkl" not in file_name:
        return

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    data = blob.download_as_bytes()
    model_obj = pickle.loads(io.BytesIO(data).read())

    metrics = model_obj.get("metrics", {})
    if not metrics:
        raise ValueError("No 'metrics' found in pickle.")

    metrics["ingestion_time"] = datetime.now(timezone.utc).isoformat() 
    metrics["source_file"] = file_name

    bq_client = bigquery.Client()
    table_id = "poojaproject.Steam_select.model_metrics"
    errors = bq_client.insert_rows_json(table_id, [metrics])
    if errors:
        raise RuntimeError(f"BigQuery insert error: {errors}")
    print(f"Inserted metrics from {file_name} into BigQuery.")
    
    # Execute the Cloud Run job via the REST API
    try:
        # Get credentials for the API request
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        
        # Construct the API URL
        job_name = "flask-restart-job"
        region = "us-east1"
        project_id = "poojaproject"
        
        run_job_url = f"https://{region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/{project_id}/jobs/{job_name}:run"
        
        # Set headers with authentication
        headers = {
            'Authorization': f'Bearer {credentials.token}',
            'Content-Type': 'application/json'
        }
        
        # Execute the job
        response = requests.post(run_job_url, headers=headers, json={})
        
        if response.status_code in [200, 201, 202]:
            print(f"Successfully triggered Flask app restart job")
        else:
            print(f"Failed to trigger job. Status: {response.status_code}, Response: {response.text}")
            
    except Exception as e:
        print(f"Error triggering restart job: {str(e)}")
    
    print("Model metrics processing completed")
    return "Processing completed successfully"