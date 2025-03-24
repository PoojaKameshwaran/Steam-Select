import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf
from notification import notify_failure, notify_success
from model_development.push_model_to_mlflow import log_model_to_mlflow
from model_development.select_and_push_best_model import select_and_push_best_model
from model_development.bias import run_bias_analysis
from model_development.sensitivity_analysis import run_sensitivity_analysis

# Specify the input parameters
BUCKET_NAME = "steam-select"
FILE_PATHS = ["processed/reviews_item_cleaned.parquet", "processed/cleaned_reviews.parquet"]
PROJECT_DIR = os.getcwd()
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
base_model_path = os.path.join(PROJECT_DIR, "data", "models", "base_model", "model_v1.pkl")

from data_preprocessing.download_data  import download_from_gcp
from model_development.build_model import wrapper_build_model_function
from model_development.hyperparameter_tuning import tuning_task
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
    description = 'Pipeline to build, tune and push model',
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
    on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Download Processed Data from GCP Task Failed."),
    dag=dag,
)

build_hybrid_model_task = PythonOperator(
   task_id='build_hybrid_model',
   python_callable=wrapper_build_model_function,
   on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Build Hybrid Model Task Failed."),
   dag=dag,
)

push_model_task = PythonOperator(
    task_id='push_model_to_mlflow',
    python_callable=log_model_to_mlflow,
    op_kwargs={
        'model_path': os.path.join(os.getcwd(), "data", "models", "base_model"),
        'model_name': "model_v1.pkl",
        'experiment_name': "steam_games_recommender",
        'run_name': "steam_games_recommender_v1"
    },
    on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Push Base Model Task Failed."),
    dag=dag
)

hyperparameter_tuning_task = PythonOperator(
   task_id='hyperparameter_tuning',
   python_callable=tuning_task,
   on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Hyperparameter Tuning Task Failed."),
   dag=dag,
)

push_tuned_model_task = PythonOperator(
    task_id='push_tuned_model_to_mlflow',
    python_callable=log_model_to_mlflow,
    op_kwargs={
        'model_path': os.path.join(os.getcwd(), "data", "models", "tuned_model"),
        'model_name': "tuned_model_v1.pkl",
        'experiment_name': "steam_games_recommender",
        'run_name': "steam_games_recommender_v2"
    },
    on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Push Tuned Model Task Failed."),
    dag=dag
)

select_and_push_best_model_task = PythonOperator(
    task_id='select_and_push_best_model',
    python_callable=select_and_push_best_model,
    on_success_callback=lambda context: notify_success(context, "Model Pipeline Succeeded!"),
    on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Select and Push Best Model Task Failed."),
    dag=dag
)

model_sensitivity_analysis_task = PythonOperator(
   task_id='model_sensitivity_analysis',
   python_callable=run_sensitivity_analysis,
   on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Model Sensitivity Analysis Task Failed."),
   dag=dag,
)

model_bias_analysis_task = PythonOperator(
   task_id='model_bias_analysis',
   python_callable=run_bias_analysis,
   on_failure_callback=lambda context: notify_failure(context, "Model Pipeline : Model Bias Analysis Task Failed."),
   dag=dag,
)

# Define the task dependencies
download_processed_data_from_gcp_task >> build_hybrid_model_task >> push_model_task >> hyperparameter_tuning_task >> model_sensitivity_analysis_task >> model_bias_analysis_task >> push_tuned_model_task >> select_and_push_best_model_task

