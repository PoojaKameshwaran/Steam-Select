import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf
from notification import notify_failure, notify_success


from data_preprocessing.download_data  import download_from_gcp
from data_preprocessing.store_paraquet import read_from_json_to_paraquet

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
    'data_download_pipeline',
    default_args = default_args,
    description = 'Data Download from GCS Pipeline',
    schedule_interval = None,  # Set the schedule interval or use None for manual triggering
    catchup = False,
)

PROJECT_DIR = os.getcwd()
DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

#DEFINE A FUNCTION TO DOWNLOAD THE DATA FROM GCP
download_task = PythonOperator(
    task_id='download_data_from_gcp',
    python_callable=download_from_gcp,
    op_kwargs={
        'bucket_name': 'steam-select', 
        'blob_paths': ["raw/item_metadata.json", "raw/bundle_data.json", "raw/reviews.json"],
        'PROJECT_DIR' : PROJECT_DIR,
        'DATA_DIR' : DATA_DIR
    },
    on_success_callback=lambda context: notify_success(context, "Data Download Pipeline Succeeded!"),
    on_failure_callback=lambda context: notify_failure(context, "Data Download Pipeline Failed."),
    dag=dag,
)


# Define the task dependencies
download_task
