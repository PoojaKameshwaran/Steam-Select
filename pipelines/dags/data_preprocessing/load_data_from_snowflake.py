import os
import pandas as pd
import snowflake.connector as snow
from dotenv import load_dotenv
from pathlib import Path

def read_from_snowflake(database, schema, table_name):

    # Detect if running inside Airflow Docker
    if os.path.exists("/opt/airflow"):  
        BASE_DIR = "/opt/airflow/steam-select" 
    else:
        
        current_dir = os.path.abspath(os.path.dirname(__file__))
        
        while os.path.basename(current_dir).lower() != "steam-select":
            current_dir = os.path.dirname(current_dir)
            if current_dir == os.path.dirname(current_dir): 
                raise Exception("Could not find the 'steam-select' directory.")

        BASE_DIR = current_dir 

    # Construct the .env file path
    ENV_PATH = os.path.join(BASE_DIR, ".env")

    # Load the .env file
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
        print(f".env file loaded from: {ENV_PATH}")
    else:
        raise Exception(f"No .env file found at {ENV_PATH}")
    
    # Establish connection
    conn = snow.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
    )
    
    try:
        # Create cursor
        cur = conn.cursor()
        
        # Set context
        cur.execute(f"USE DATABASE {database}")
        cur.execute(f"USE SCHEMA {schema}")
        
        # Execute query
        query = f"SELECT * FROM {table_name} LIMIT 10000"
        cur.execute(query)
        
        df = cur.fetch_pandas_all()
        
        print(f"Successfully read {len(df)} rows from {database}.{schema}.{table_name}")
        return df
        
    except Exception as e:
        print(f"Error reading from Snowflake: {str(e)}")
        return None
        
    finally:
        cur.close()
        conn.close()


# if __name__ == "__main__":
    
#     df = read_from_snowflake(
#         database="STEAM_FULL",
#         schema="RAW_DATA",
#         table_name="ITEM_METADATA"
#     )
#     print(df.shape)
#     print(df.head())