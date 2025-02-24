import yaml
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from snowflake.connector.cursor import SnowflakeCursor


def create_integ(schema, cur):
    # creating storage integration and stage to perform bulk loading
    SNOWFLAKE_INTEGRATION = schema['integration']
    GCS_BUCKET = schema['gcs_bucket']

    create_integ_sql = f"""
        CREATE STORAGE INTEGRATION IF NOT EXISTS {SNOWFLAKE_INTEGRATION}
        TYPE = EXTERNAL_STAGE
        STORAGE_PROVIDER = 'GCS'
        ENABLED = TRUE
        STORAGE_ALLOWED_LOCATIONS = ('gcs://{GCS_BUCKET}/');
    """
    cur.execute(create_integ_sql)
    print("Snowflake Storage Integration Check : Passed")

def create_stage(schema, cur):
    # pulling parameters from schema file to create a stage in case it does not exist
    SNOWFLAKE_STAGE = schema['stage']
    SNOWFLAKE_INTEGRATION = schema['integration']
    GCS_BUCKET = schema['gcs_bucket']

    create_stage_sql = f"""
        CREATE STAGE IF NOT EXISTS {SNOWFLAKE_STAGE}
        STORAGE_INTEGRATION = {SNOWFLAKE_INTEGRATION}
        URL = 'gcs://{GCS_BUCKET}/'
        FILE_FORMAT = (TYPE = JSON);
    """
    cur.execute(create_stage_sql)
    print("Snowflake Stage Check : Passed")

def create_tables():
    # for creating snowflake and gcp connections
    snowflake_hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
    gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")
    
    # reading the schema file
    SCHEMA_FILE = "/opt/airflow/dags/data_import/schema.yml"
    with open(SCHEMA_FILE, "r") as f:
        schema = yaml.safe_load(f)

    # Establish Snowflake connection
    conn = snowflake_hook.get_conn()
    cur = conn.cursor()
    
    create_integ(schema, cur)
    create_stage(schema, cur)

    SNOWFLAKE_SCHEMA = schema['schema']
    SNOWFLAKE_DATABASE = schema['database']

    # Loop through tables and load data using Snowflake Staging
    for table_name, table_data in schema["tables"].items():
        columns = table_data["columns"]
        column_definitions = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])

        create_query = f"""
        CREATE TABLE IF NOT EXISTS {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name} (
            {column_definitions}
        );
        """

        
        cur.execute(create_query)
        print(f"{table_name} CREATED SUCCESSFULLY")
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
