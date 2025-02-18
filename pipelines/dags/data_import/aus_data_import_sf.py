import snowflake.connector
import getpass

# Get Snowflake credentials from user input
user = input("Enter your Snowflake username: ")
password = getpass.getpass("Enter your Snowflake password: ")
account = input("Enter your Snowflake account (e.g., xy12345.us-east-1): ")
warehouse = input("Enter your Snowflake warehouse: ")
database = input("Enter your Snowflake database: ")
schema = input("Enter your Snowflake schema: ")

# GCS Bucket and Integration details
GCS_STAGE_NAME = "my_gcs_stage"
GCS_BUCKET_URL = "gcs://steam-select/"
GCS_INTEGRATION_NAME = "my_gcs_integration" 
TABLE_NAME = "aus_reviews_raw"

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=user,
    password=password,
    account=account,
    warehouse=warehouse,
    database=database,
    schema=schema
)

cur = conn.cursor()

try:
    # Create Table (if not exists) with updated schema
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            review_id NUMBER,
            user_url VARCHAR,
            user_id VARCHAR,
            funny NUMBER,
            posted VARCHAR,
            last_edited VARCHAR,
            item_id NUMBER,
            helpful NUMBER,
            recommend BOOLEAN,
            review VARCHAR
        );
    """)

    # Create External Stage (if not exists)
    cur.execute(f"""
        CREATE STAGE IF NOT EXISTS {GCS_STAGE_NAME}
        URL = '{GCS_BUCKET_URL}'
        STORAGE_INTEGRATION = {GCS_INTEGRATION_NAME};
    """)

    # Copy JSON data into Snowflake Table
    cur.execute(f"""
        COPY INTO {TABLE_NAME}
        FROM @{GCS_STAGE_NAME}/formatted_reviews.csv
        FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1, RECORD_DELIMITER = '\n');
    """)

    print("Data successfully loaded into Snowflake.")

finally:
    cur.close()
    conn.close()
