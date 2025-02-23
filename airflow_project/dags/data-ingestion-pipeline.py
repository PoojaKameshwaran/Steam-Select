from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import yaml

# Define default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 2, 20),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define DAG
with DAG(
    "data_ingestion_pipeline",
    default_args=default_args,
    schedule_interval=None,  # Set None to trigger manually or define cron
    catchup=False,
) as dag:

    # Task 1: Run create_tables.py
    create_tables_task = BashOperator(
        task_id="create_tables",
        bash_command="python /opt/airflow/dags/scripts/create_tables.py",
    )

    # Task 2: Run load_tables.py
    load_tables_task = BashOperator(
        task_id="load_tables",
        bash_command="python /opt/airflow/dags/scripts/load_tables.py",
    )

    # Define task sequence
    create_tables_task >> load_tables_task
