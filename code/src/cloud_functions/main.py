import pickle
import io
from datetime import datetime, timezone
from google.cloud import bigquery, storage

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
