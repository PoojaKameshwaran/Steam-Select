import yaml
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook


# Load schema.yml
SCHEMA_FILE = "/opt/airflow/dags/data_import/schema.yml"
with open(SCHEMA_FILE, "r") as f:
    schema = yaml.safe_load(f)

SNOWFLAKE_DATABASE = schema["database"]
SNOWFLAKE_SCHEMA = schema["schema"]

def cleanup_tables():
    
    # Fetch Snowflake connection from Airflow
    snowflake_hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
    conn = snowflake_hook.get_conn()
    cur = conn.cursor()
    
    for table_name, table_data in schema["tables"].items():
        drop_query = f"DROP TABLE IF EXISTS {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name};"
        cur.execute(drop_query)
        print(f"Dropped table: {table_name}")
    
    cur.close()
    conn.close()
    print("Cleanup completed.")

if __name__ == "__main__":
    cleanup_tables()
