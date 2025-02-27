# import os
# from datetime import datetime, timedelta
# from airflow import DAG
# from airflow.operators.bash import BashOperator


# # Set default arguments

# default_args = {
#     'owner': 'MLopsProject',
#     'depends_on_past': False,
#     'start_date': datetime(2024,10,19),
#     'retries': 0,
#     'retry_delay':timedelta(minutes=5)
# }

# #INITIALIZE THE DAG INSTANCE
# dag = DAG(
#     'data_cleaning_eda_pipeline',
#     default_args = default_args,
#     description = 'Data Cleaning and EDA Pipeline',
#     schedule_interval = None,  # Set the schedule interval or use None for manual triggering
#     catchup = False,
# )

# clean_reviews_task = BashOperator(
#     task_id='clean_reviews_task',
#     bash_command="python /opt/airflow/dags/data_preprocessing/clean_reviews.py",
#     dag = dag
# )

# eda_reviews_task = BashOperator(
#     task_id='eda_reviews_task',
#     bash_command="/usr/local/bin/python /opt/airflow/dags/data_preprocessing/EDA_reviews.py"
# )

# # clean_bundle_task = BashOperator(
# #     task_id='clean_bundle_task',
# #     bash_command="python /opt/airflow/dags/data_preprocessing/clean_bundle_data.py"
# # )

# # eda_bundle_task = BashOperator(
# #     task_id='eda_bundle_task',
# #     bash_command="python /opt/airflow/dags/data_preprocessing/EDA_bundle_data.py"
# # )

# # clean_items_task = BashOperator(
# #     task_id='clean_items_task',
# #     bash_command="python /opt/airflow/dags/data_preprocessing/clean_item_metadata.py"
# # )

# # eda_items_task = BashOperator(
# #     task_id='eda_items_task',
# #     bash_command="python /opt/airflow/dags/data_preprocessing/EDA_item_metadata.py"
# # )

# write_to_stage_task = BashOperator(
#     task_id='write_to_stage_task',
#     bash_command="python /opt/airflow/dags/data_preprocessing/write_to_gcs.py"
# )

# clean_up_stage_task = BashOperator(
#     task_id='clean_up_stage',
#     bash_command="python /opt/airflow/dags/data_preprocessing/cleanup_stage.py"
# )

# # Define task dependencies
# # clean_bundle_task >> eda_bundle_task >> write_to_stage_task
# # clean_items_task >> eda_items_task >> write_to_stage_task
# clean_reviews_task >> eda_reviews_task >> write_to_stage_task
