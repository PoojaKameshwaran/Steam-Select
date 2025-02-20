import yaml
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

# Load schema.yml
with open("schema.yml", "r") as file:
    schema = yaml.safe_load(file)

# Fetch Snowflake connection from Airflow
snowflake_hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
conn = snowflake_hook.get_conn()
cur = conn.cursor()

# Extract database details from schema.yml
SNOWFLAKE_DATABASE = schema["database"]
SNOWFLAKE_SCHEMA = schema["schema"]

# Loop through tables in schema.yml and create them in Snowflake
for table_name, table_data in schema["tables"].items():
    columns = table_data["columns"]
    column_definitions = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    
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
