import yaml
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

# Load schema.yml
with open("/opt/airflow/dags/scripts/schema.yml", "r") as file:
    schema = yaml.safe_load(file)

# Fetch Snowflake connection from Airflow
snowflake_hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
conn = snowflake_hook.get_conn()
cur = conn.cursor()

# Extract database details from schema.yml
SNOWFLAKE_DATABASE = schema["database"]
SNOWFLAKE_SCHEMA = schema["schema"]

# creating database and schema if they do not exist
create_db_sql = f"""
    CREATE DATABASE IF NOT EXISTS {SNOWFLAKE_DATABASE};
"""
cur.execute(create_db_sql)

create_sch_sql = f"""
    CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA};
"""
cur.execute(create_sch_sql)

# Loop through tables in schema.yml and create them in Snowflake
for table_name, table_data in schema["tables"].items():
    columns = table_data["columns"]
    column_definitions = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    
    drop_table_sql = f"""
        DROP TABLE IF EXISTS {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name};
    """
    cur.execute(drop_table_sql)
    print(f"{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name} CLEANED")

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{table_name} (
        {column_definitions}
    );
    """
    
    print(f"Creating table: {table_name}")
    cur.execute(create_table_sql)

# Close connection
cur.close()
conn.close()
print("Tables created successfully.")
