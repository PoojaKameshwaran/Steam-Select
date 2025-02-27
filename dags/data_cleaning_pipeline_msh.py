import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf

from data_preprocessing.download_data  import download_from_gcp
from data_preprocessing.read_json import read_from_json
from data_preprocessing.cleaning_item import clean_item_metadata
from data_preprocessing.preprocess_item import preprocess_item_metadata

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
    'Data_Preprocessing',
    default_args = default_args,
    description = 'MLOps Data pipeline',
    schedule_interval = None,  # Set the schedule interval or use None for manual triggering
    catchup = False,
)


#DEFINE A FUNCTION TO DOWNLOAD THE DATA FROM GCP
download_task = PythonOperator(
    task_id='download_data_from_gcp',
    python_callable=download_from_gcp,
    op_kwargs={'bucket_name': 'steam-select', 'blob_path':'raw/item_metadata.json'},
    dag=dag,
)

#DEFINE A FUNCTION TO LOAD THE DATA LOCALLY AND SAVE AS PARAQUET
read_json_task = PythonOperator(
    task_id='read_json_data',
    python_callable=read_from_json,
    op_kwargs={'file_path': '{{ task_instance.xcom_pull(task_ids="download_data_from_gcp") }}'},
    dag=dag,
)

#DEFINE A FUNCTION CLEAN THE ITEM DATA
clean_item_metadata_task = PythonOperator(
    task_id='clean_item_metadata',
    python_callable=clean_item_metadata,
    op_kwargs={'file_path': '{{ task_instance.xcom_pull(task_ids="read_json_data") }}'},
    dag=dag,
)

#DEFINE A FUNCTION PREPROCESS THE ITEM DATA
preprocess_item_metadata_task = PythonOperator(
    task_id='preprocess_item_metadata',
    python_callable=preprocess_item_metadata,
    op_kwargs={'file_path': '{{ task_instance.xcom_pull(task_ids="clean_item_metadata") }}'},
    dag=dag,
)

# Define the task dependencies
download_task >> read_json_task >> clean_item_metadata_task >> preprocess_item_metadata_task