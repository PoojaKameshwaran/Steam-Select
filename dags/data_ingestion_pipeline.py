import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

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
download_task = BashOperator(
    task_id='download_data_from_gcp',
    bash_command = "python /opt/airflow/dags/data_preprocessing/download_data.py"
)

# Define task dependencies
download_task