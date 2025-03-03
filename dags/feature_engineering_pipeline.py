import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf
from notification import notify_failure, notify_success

from data_preprocessing.download_data  import download_from_gcp
from feature_engineering.feature_reviews import feature_engineering_cleaned_reviews_file
from feature_engineering.feature_item import feature_engineering_cleaned_item_file
from feature_engineering.feature_bundle import feature_engineering_cleaned_bundle_file
from feature_engineering.merge_reviews_item import merge_reviews_item_file
from data_preprocessing.write_to_gcs import upload_multiple_files
from data_preprocessing.cleanup_stage import clean_up_files_in_folder

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
    'feature_engineering_pipeline',
    default_args = default_args,
    description = 'Data Cleaning & EDA Pipeline',
    schedule_interval = None,  # Set the schedule interval or use None for manual triggering
    catchup = False,
)

PROJECT_DIR = os.getcwd()
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

#DEFINE A FUNCTION TO DOWNLOAD THE DATA FROM GCP
download_cleaned_data_task = PythonOperator(
    task_id='download_processed_data',
    python_callable=download_from_gcp,
    op_kwargs={
        'bucket_name': 'steam-select', 
        'blob_paths': ["staging/item_metadata.parquet", "staging/bundle_data.parquet", "staging/reviews.parquet"],
        'PROJECT_DIR' : PROJECT_DIR,
        'DATA_DIR' : DATA_DIR
    },
    on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Download Cleaned Data Task Failed."),
    dag=dag,
)

feature_reviews_task = PythonOperator(
    task_id='feature_reviews',
    python_callable=feature_engineering_cleaned_reviews_file,
    op_kwargs={'file_name': 'reviews.parquet'},
    on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Feature Reviews Task Failed."),
    dag=dag,
)

feature_item_task = PythonOperator(
    task_id='feature_item',
    python_callable=feature_engineering_cleaned_item_file,
    op_kwargs={'file_name': 'item_metadata.parquet'},
    on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Feature Item Task Failed."),
    dag=dag,
)

feature_bundle_task = PythonOperator(
    task_id='feature_bundle',
    python_callable=feature_engineering_cleaned_bundle_file,
    op_kwargs={'file_name': 'bundle_data.parquet'},
    on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Feature Bundle Task Failed."),
    dag=dag,
)

def merge_reviews_item_function(**kwargs):
    ti = kwargs['ti']

    # Retrieve file paths from XCom, ensuring they're always lists
    file_list_1 = ti.xcom_pull(task_ids='feature_reviews', key='return_value') or []
    file_list_2 = ti.xcom_pull(task_ids='feature_item', key='return_value') or []
 
    # Ensure both are lists
    if isinstance(file_list_1, str):
        file_list_1 = [file_list_1]
    if isinstance(file_list_2, str):
        file_list_2 = [file_list_2]

    # Combine all files
    all_files = file_list_1 + file_list_2

    # Call function
    merge_reviews_item_file(all_files)

merge_reviews_item_task = PythonOperator(
    task_id='merge_reviews_item',
    python_callable=merge_reviews_item_function,
    provide_context=True,
    on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Merge Reviews Item Task Failed."),
    dag=dag,
)

def upload_files_gcp(**kwargs):
    ti = kwargs['ti']

    # Retrieve file paths from XCom, ensuring they're always lists
    file_list_1 = os.path.join(DATA_DIR, "reviews_item_cleaned.parquet") or []
    file_list_2 = os.path.join(DATA_DIR, "bundle_data_cleaned.parquet") or []

    # Ensure both are lists
    if isinstance(file_list_1, str):
        file_list_1 = [file_list_1]
    if isinstance(file_list_2, str):
        file_list_2 = [file_list_2]

    # Combine all files
    all_files = file_list_1 + file_list_2

    # Define GCS bucket and destination folder
    bucket_name = "steam-select"
    destination_folder = "processed"

    # Call upload function
    if all_files:
        upload_multiple_files(bucket_name, destination_folder, all_files)
    else:
        print("No files to upload.")

processed_to_gcs_task = PythonOperator(
    task_id='processed_to_gcs',
    python_callable=upload_files_gcp,
    provide_context=True,
    on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Upload to gcs Task Failed."),
    on_success_callback=lambda context: notify_success(context, "Feature Engineering Pipeline Succeeded!"),
    dag=dag,
)

clean_up_processed_task = PythonOperator(
    task_id='clean_up_processed',
    python_callable=clean_up_files_in_folder,
    provide_context=True,
    on_failure_callback=lambda context: notify_failure(context, "Feature Engineering Pipeline : Cleanup processed Task Failed."),
    dag=dag,
)

download_cleaned_data_task >> feature_reviews_task >> merge_reviews_item_task >> processed_to_gcs_task
download_cleaned_data_task >> feature_item_task >> merge_reviews_item_task >> processed_to_gcs_task
download_cleaned_data_task >> feature_bundle_task >> processed_to_gcs_task
processed_to_gcs_task >> clean_up_processed_task