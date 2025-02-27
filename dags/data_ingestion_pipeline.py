import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from data_preprocessing.download_data  import download_from_gcp

#Define the paths to project directory and the path to the key
PROJECT_DIR = os.getcwd()

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
    'data_ingestion_pipeline',
    default_args = default_args,
    description = 'Data Ingestion from GCS',
    schedule_interval = None,  # Set the schedule interval or use None for manual triggering
    catchup = False,
)


#DEFINE A FUNCTION TO DOWNLOAD THE DATA FROM GCP
download_task = PythonOperator(
    task_id='download_data_from_gcp',
    python_callable=download_from_gcp,
    dag=dag,
)

# Define task dependencies
download_task