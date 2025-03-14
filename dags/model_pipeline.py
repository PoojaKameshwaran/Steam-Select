import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf
from notification import notify_failure, notify_success

# Specify the input parameters
BUCKET_NAME = "steam-select"
FILE_PATHS = ["processed/reviews_item_cleaned.parquet", "processed/bundle_data_cleaned.parquet"]
PROJECT_DIR = os.getcwd()
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

from data_preprocessing.download_data  import download_from_gcp
from model_development.rec_model import build_recommender_model

#Define the paths to project directory and the path to the key
PROJECT_DIR = os.getcwd()

# Enable xcom pickling to allow passage of tasks from one task to another.
conf.set('core', 'enable_xcom_pickling', 'True')

# Set default arguments

default_args = {
    'owner': 'MLopsProject',
    'depends_on_past': False,
    'start_date': datetime(2024,10,19),
    'retries': 0,
    'retry_delay':timedelta(minutes=5)
}

#INITIALIZE THE DAG INSTANCE
dag = DAG(
    'model_pipeline',
    default_args = default_args,
    description = 'Data Download from GCS Pipeline',
    schedule_interval = None,  # Set the schedule interval or use None for manual triggering
    catchup = False,
)

PROJECT_DIR = os.getcwd()

os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

#DEFINE A FUNCTION TO DOWNLOAD THE DATA FROM GCP
download_task = PythonOperator(
    task_id='download_processed_data_from_gcp',
    python_callable=download_from_gcp,
    op_kwargs={
        'bucket_name': BUCKET_NAME, 
        'blob_paths': FILE_PATHS,
        'PROJECT_DIR' : PROJECT_DIR,
        'DATA_DIR' : DATA_DIR
    },
    # on_success_callback=lambda context: notify_success(context, "Data Download Pipeline Succeeded!"),
    # on_failure_callback=lambda context: notify_failure(context, "Data Download Pipeline Failed."),
    dag=dag,
)

build_model_task = PythonOperator(
    task_id='feature_reviews',
    python_callable=build_recommender_model,
    # on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Feature Reviews Task Failed."),
    dag=dag,
)

# Define the task dependencies
download_task >> build_model_task
