import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from data_preprocessing.load_data_from_snowflake import read_from_snowflake

# Define the tables to load
TABLES = [
    {"name": "REVIEWS", "schema": "RAW_DATA"},
    {"name": "ITEM_METADATA", "schema": "RAW_DATA"},
    {"name": "BUNDLE_DATA", "schema": "RAW_DATA"}
]

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'snowflake_parallel_load',
    default_args=default_args,
    description='Load multiple Snowflake tables in parallel',
    schedule_interval='@daily',
    catchup=False,
    concurrency=3,
) as dag:

    def load_table(**context):
        table_name = context['table_name']
        schema = context['schema']
        df = read_from_snowflake(
            database="STEAM_FULL",
            schema=schema,
            table_name=table_name
        )
        return f"Loaded {table_name} with shape {df.shape if df is not None else 'None'}"

    # Create tasks dynamically for each table
    tasks = []
    for table in TABLES:
        task = PythonOperator(
            task_id=f"load_{table['name'].lower()}",
            python_callable=load_table,
            op_kwargs={
                'table_name': table['name'],
                'schema': table['schema']
            }
        )
        tasks.append(task)
