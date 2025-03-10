import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from notification import notify_failure, notify_success

from data_validation.validate_data import read_and_validate_file
from data_validation.anomaly_detection import read_and_detect_anomalies

# Define DAG arguments
default_args = {
    "owner": "MLopsProject",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 19),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

# Initialize DAG
dag = DAG(
    "data_validation_pipeline",
    default_args=default_args,
    description="Data Validation and Anomaly Detection Pipeline",
    schedule_interval=None,
    catchup=False,
)

# Validation tasks
validate_item_task = PythonOperator(
    task_id="validate_item_data",
    python_callable=read_and_validate_file,
    op_kwargs={"file_name": "item_metadata.json"},
    on_failure_callback=lambda context: notify_failure(context, "Data Validation Pipeline : Validate Item Data Task Failed."),
    dag=dag,
)

validate_reviews_task = PythonOperator(
    task_id="validate_reviews_data",
    python_callable=read_and_validate_file,
    op_kwargs={"file_name": "reviews.json"},
    on_failure_callback=lambda context: notify_failure(context, "Data Validation Pipeline : Validate Reviews Data Task Failed."),
    dag=dag,
)

validate_bundle_task = PythonOperator(
    task_id="validate_bundle_data",
    python_callable=read_and_validate_file,
    op_kwargs={"file_name": "bundle_data.json"},
    on_failure_callback=lambda context: notify_failure(context, "Data Validation Pipeline : Validate Bundle Data Task Failed."),
    dag=dag,
)

# Anomaly detection tasks
anomaly_item_task = PythonOperator(
    task_id="detect_anomalies_item",
    python_callable=read_and_detect_anomalies,
    op_kwargs={"file_name": "item_metadata.json"},
    on_failure_callback=lambda context: notify_failure(context, "Data Validation Pipeline : Anomaly Item Data Task Failed."),
    dag=dag,
)

anomaly_reviews_task = PythonOperator(
    task_id="detect_anomalies_reviews",
    python_callable=read_and_detect_anomalies,
    op_kwargs={"file_name": "reviews.json"},
    on_failure_callback=lambda context: notify_failure(context, "Data Validation Pipeline : Anomaly Reviews Data Task Failed."),
    on_success_callback=lambda context: notify_success(context, "Data Validation Pipeline Succeeded!"),
    dag=dag,
)

# Set task dependencies
validate_item_task >> anomaly_item_task
validate_reviews_task >> anomaly_reviews_task
validate_bundle_task
validate_item_task
