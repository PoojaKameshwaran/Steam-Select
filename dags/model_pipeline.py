import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf
from notification import notify_failure, notify_success
from model_development.push_model_to_mlflow import log_model_to_mlflow

# Specify the input parameters
BUCKET_NAME = "steam-select"
FILE_PATHS = ["processed/reviews_item_cleaned.parquet", "processed/cleaned_reviews.parquet"]
PROJECT_DIR = os.getcwd()
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
base_model_path = os.path.join(PROJECT_DIR, "data", "models", "base_model", "model_v1.pkl")

from data_preprocessing.download_data  import download_from_gcp
from model_development.build_model import wrapper_build_model_function
#from model_development.rec_model import build_recommender_model


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
    description = 'Model Build Pipeline',
    schedule_interval = None,  # Set the schedule interval or use None for manual triggering
    catchup = False,
)

PROJECT_DIR = os.getcwd()

os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

#DEFINE A FUNCTION TO DOWNLOAD THE DATA FROM GCP
download_processed_data_from_gcp_task = PythonOperator(
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

build_hybrid_model_task = PythonOperator(
   task_id='build_hybrid_model',
   python_callable=wrapper_build_model_function,
    # on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Feature Reviews Task Failed."),
   dag=dag,
)

push_model_task = PythonOperator(
    task_id='push_model_to_mlflow',
    python_callable=log_model_to_mlflow,
    op_kwargs={
        'model_path': os.path.join(os.getcwd(), "data", "models", "base_model"),
        'experiment_name': "steam_games_recommender",
        'run_name': "steam_games_recommender_v1"
    },
    dag=dag
)

# Define the task dependencies
download_processed_data_from_gcp_task >> build_hybrid_model_task >> push_model_task