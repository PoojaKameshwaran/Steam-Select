from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 2, 23),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

# Define DAG
with DAG(
    "data_ingestion_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    cleanup_tables_task = BashOperator(
        task_id="cleanup_tables",
        bash_command="python /opt/airflow/dags/data_import/cleanup_tables.py",
    )

    create_tables_task = BashOperator(
        task_id="create_tables",
        bash_command="python /opt/airflow/dags/data_import/create_tables.py",
    )

    load_data_task = BashOperator(
        task_id="load_data",
        bash_command="python /opt/airflow/dags/data_import/load_tables.py",
    )

    # Define workflow
    cleanup_tables_task >> create_tables_task >> load_data_task
