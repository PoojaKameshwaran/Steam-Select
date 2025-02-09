import os
import pandas as pd
import snowflake.connector as snow
from dotenv import load_dotenv

def read_from_snowflake(database, schema, table_name):
    
    load_dotenv(override=True)
    
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
        
        # Read data into DataFrame
        query = f"SELECT * FROM {table_name} LIMIT 50000"
        df = pd.read_sql(query, conn)
        
        print(f"Successfully read {len(df)} rows from {database}.{schema}.{table_name}")
        
        return df
        
    except Exception as e:
        print(f"Error reading from Snowflake: {str(e)}")
        return None
        
    finally:
        # Close connections
        cur.close()
        conn.close()

if __name__ == "__main__":
    
    df = read_from_snowflake(
        database="STEAM_FULL",
        schema="RAW_DATA",
        table_name="ITEM_METADATA"
    )
    print(df.shape)
    print(df.head())