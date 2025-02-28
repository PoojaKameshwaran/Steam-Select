import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow import configuration as conf

from data_preprocessing.clean_reviews  import read_and_clean_reviews_file
from data_preprocessing.EDA_reviews  import eda_reviews_data

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
    dag=dag,
)

eda_reviews_task = PythonOperator(
    task_id='eda_reviews',
    python_callable=eda_reviews_data,
    op_kwargs={'file_path': '{{ task_instance.xcom_pull(task_ids="read_json_data") }}'},
    dag=dag,
)