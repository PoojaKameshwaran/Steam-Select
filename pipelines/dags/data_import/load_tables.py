from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.google.cloud.hooks.gcs import GCSHook
import yaml

# Load schema.yml
with open("/opt/airflow/dags/data_import/schema.yml", "r") as file:
    schema = yaml.safe_load(file)

SNOWFLAKE_STAGE = schema['stage']
SNOWFLAKE_DATABASE = schema['database']


def load_data():

    # Load schema.yml
    with open("/opt/airflow/dags/data_import/schema.yml", "r") as file:
        schema = yaml.safe_load(file)

    # loading the parameters from schema file 
    SNOWFLAKE_STAGE = schema['stage']
    SNOWFLAKE_DATABASE = schema['database']
    SNOWFLAKE_SCHEMA = schema['schema']

    # Fetch connections from Airflow
    snowflake_hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
    gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")

    # Establish Snowflake connection
    conn = snowflake_hook.get_conn()
    cur = conn.cursor()
    

    for table_name, table_data in schema["tables"].items():
        file_name = table_data["file_name"]
        file_path = f"@{SNOWFLAKE_STAGE}/{file_name}"
        copy_query = f"""
            COPY INTO {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
            FROM {file_path}
            FILE_FORMAT = (TYPE = 'JSON', STRIP_OUTER_ARRAY = TRUE)
            MATCH_BY_COLUMN_NAME = 'CASE_INSENSITIVE'
            FORCE = TRUE;
        """
        cur.execute(copy_query)
        print(f"Loaded data into: {table_name}")
    
    cur.close()
    conn.close()
    print("Data loading completed.")

if __name__ == "__main__":
    load_data()

