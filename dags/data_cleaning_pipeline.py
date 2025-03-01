import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf
from notification import notify_failure, notify_success

from data_preprocessing.clean_reviews  import read_and_clean_reviews_file
from data_preprocessing.EDA_reviews  import eda_reviews_data
from data_preprocessing.clean_item  import read_and_clean_item_file
from data_preprocessing.EDA_item  import eda_item_data
from data_preprocessing.clean_bundle  import read_and_clean_bundle_file
from data_preprocessing.EDA_bundle  import eda_bundle_data
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
    'Data_Cleaning_EDA_Pipeline',
    default_args = default_args,
    description = 'MLOps Data pipeline',
    schedule_interval = None,  # Set the schedule interval or use None for manual triggering
    catchup = False,
)


clean_reviews_task = PythonOperator(
    task_id='clean_reviews',
    python_callable=read_and_clean_reviews_file,
    op_kwargs={'file_name': 'reviews.json'},
    on_failure_callback=notify_failure,
    dag=dag,
)

eda_reviews_task = PythonOperator(
    task_id='eda_reviews',
    python_callable=eda_reviews_data,
    op_kwargs={'file_path': '{{ task_instance.xcom_pull(task_ids="clean_reviews") }}'},
    on_failure_callback=notify_failure,
    dag=dag,
)

clean_item_task = PythonOperator(
    task_id='clean_item',
    python_callable=read_and_clean_item_file,
    op_kwargs={'file_name': 'item_metadata.json'},
    on_failure_callback=notify_failure,
    dag=dag,
)

eda_item_task = PythonOperator(
    task_id='eda_item',
    python_callable=eda_item_data,
    op_kwargs={'file_path': '{{ task_instance.xcom_pull(task_ids="clean_item") }}'},
    on_failure_callback=notify_failure,
    dag=dag,
)

clean_bundle_task = PythonOperator(
    task_id='clean_bundle',
    python_callable=read_and_clean_bundle_file,
    op_kwargs={'file_name': 'bundle_data.json'},
    on_failure_callback=notify_failure,
    dag=dag,
)

eda_bundle_task = PythonOperator(
    task_id='eda_bundle',
    python_callable=eda_bundle_data,
    op_kwargs={'file_path': '{{ task_instance.xcom_pull(task_ids="clean_bundle") }}'},
    on_failure_callback=notify_failure,
    dag=dag,
)

def upload_files_gcp(**kwargs):
    ti = kwargs['ti']

    # Retrieve file paths from XCom, ensuring they're always lists
    file_list_1 = ti.xcom_pull(task_ids='clean_reviews', key='return_value') or []
    file_list_2 = ti.xcom_pull(task_ids='clean_item', key='return_value') or []
    file_list_3 = ti.xcom_pull(task_ids='clean_bundle', key='return_value') or []

    # Ensure both are lists
    if isinstance(file_list_1, str):
        file_list_1 = [file_list_1]
    if isinstance(file_list_2, str):
        file_list_2 = [file_list_2]
    if isinstance(file_list_3, str):
        file_list_3 = [file_list_3]

    # Combine all files
    all_files = file_list_1 + file_list_2 + file_list_3

    # Define GCS bucket and destination folder
    bucket_name = "steam-select"
    destination_folder = "staging"

    # Call upload function
    if all_files:
        upload_multiple_files(bucket_name, destination_folder, all_files)
    else:
        print("No files to upload.")

# Define PythonOperator to trigger the upload
staging_to_gcs_task = PythonOperator(
    task_id='staging_to_gcs',
    python_callable=upload_files_gcp,
    provide_context=True,
    on_failure_callback=notify_failure,
    on_success_callback=notify_success,
    dag=dag,
)

clean_up_stage_task = PythonOperator(
    task_id='clean_up_stage',
    python_callable=clean_up_files_in_folder,
    provide_context=True,
    on_failure_callback=notify_failure,
    dag=dag,
)

clean_reviews_task >> eda_reviews_task >> staging_to_gcs_task
clean_item_task >> eda_item_task >> staging_to_gcs_task
clean_bundle_task >> eda_bundle_task >> staging_to_gcs_task
staging_to_gcs_task >> clean_up_stage_task