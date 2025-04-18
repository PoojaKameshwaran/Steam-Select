# import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'MLopsProject',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 19),
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'master_pipeline',
    default_args=default_args,
    description='Master DAG to orchestrate the entire data pipeline',
    schedule_interval=None,
    catchup=False
)

# Start and End Operators
start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Function to create TriggerDagRunOperator with unique run_id
def trigger_dag(task_id, dag_id):
    return TriggerDagRunOperator(
        task_id=task_id,
        trigger_dag_id=dag_id,
        wait_for_completion=True,  # Ensure next DAG starts only after previous one finishes
        # run_id=f"triggered__{pendulum.now().int_timestamp}",  # Unique run_id for every trigger
        dag=dag
    )

# Trigger DAGs
trigger_data_download = trigger_dag('trigger_data_download', 'data_download_pipeline')
trigger_data_validation = trigger_dag('trigger_data_validation', 'data_validation_pipeline')
trigger_data_cleaning = trigger_dag('trigger_data_cleaning', 'data_cleaning_EDA_pipeline')
trigger_feature_engineering = trigger_dag('trigger_feature_engineering', 'feature_engineering_pipeline')
trigger_model_pipeline = trigger_dag('trigger_model_pipeline', 'model_pipeline')

# Define dependencies
start >> trigger_data_download >> trigger_data_validation >> trigger_data_cleaning >> trigger_feature_engineering >> trigger_model_pipeline >> end
