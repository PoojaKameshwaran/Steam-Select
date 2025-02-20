import yaml
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.google.cloud.hooks.gcs import GCSHook

# Load schema.yml
with open("schema.yml", "r") as file:
    schema = yaml.safe_load(file)

# Fetch connections from Airflow
snowflake_hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")

# Establish Snowflake connection
conn = snowflake_hook.get_conn()
cur = conn.cursor()

# Extract Snowflake details
SNOWFLAKE_DATABASE = schema["database"]
SNOWFLAKE_SCHEMA = schema["schema"]
SNOWFLAKE_INTEGRATION = schema["integration"]
SNOWFLAKE_STAGE = schema["stage"]

# GCS bucket name
GCS_BUCKET = schema["gcs_bucket"]

# creating storage integration and stage to perform bulk loading
create_integ_sql = f"""
    CREATE STORAGE INTEGRATION IF NOT EXISTS {SNOWFLAKE_INTEGRATION}
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'GCS'
    ENABLED = TRUE
    STORAGE_ALLOWED_LOCATIONS = ('gcs://{GCS_BUCKET}/');
"""
cur.execute(create_integ_sql)
print("Snowflake Storage Integration Check : Passed")

create_stage_sql = f"""
    CREATE STAGE IF NOT EXISTS {SNOWFLAKE_STAGE}
    STORAGE_INTEGRATION = {SNOWFLAKE_INTEGRATION}
    URL = 'gcs://{GCS_BUCKET}/'
    FILE_FORMAT = (TYPE = JSON);
"""
cur.execute(create_stage_sql)
print("Snowflake Stage Check : Passed")

# Loop through tables and load data using Snowflake Staging
for table_name, table_data in schema["tables"].items():
    file_name = table_data["file_name"]
    gcs_path = f"@{SNOWFLAKE_STAGE}/{file_name}"  
    print(f"Loading from GCS Path : {gcs_path}")
    print(f"Loading data from GCS for table: {table_name}")

    # Copy data from GCS to Snowflake
    copy_query = f"""
    COPY INTO {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name}
    FROM '{gcs_path}'
    FILE_FORMAT = (TYPE = 'JSON', STRIP_OUTER_ARRAY = TRUE)
    MATCH_BY_COLUMN_NAME = 'CASE_INSENSITIVE'
    FORCE = TRUE;
    """

    cur.execute(copy_query)
    print(f"Loaded into {table_name} successfully")

# Close connection
cur.close()
conn.close()
print("Data load into all tables via stage integration : SUCCESSFUL!")