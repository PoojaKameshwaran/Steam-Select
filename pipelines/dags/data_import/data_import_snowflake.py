# steam_reviews_loader.py
import pandas as pd
import ast
import snowflake.connector as snow
from snowflake.connector.pandas_tools import write_pandas
import os
from dotenv import load_dotenv
import tempfile
import gzip

# def read_json_file(file_path):
#     data = []
#     with open(file_path, 'r', encoding='ISO-8859–1') as file:
#         for line in file:
#             data.append(ast.literal_eval(line))
#     return pd.DataFrame(data)

def read_json_file(file_path):
    data = []
    try:
        with gzip.open(file_path, 'rt', encoding='ISO-8859–1') as file:
            for line in file:
                data.append(ast.literal_eval(line))
    except Exception as e:
        print(f"Error reading gzipped file: {e}")
        # Fallback to regular file reading if not gzipped
        with open(file_path, 'r', encoding='ISO-8859–1') as file:
            for line in file:
                data.append(ast.literal_eval(line))
    return pd.DataFrame(data).fillna('None').astype(str)

def write_to_snowflake(df, database, schema, table_name, sep=',', compression='gzip', index=False):
    load_dotenv(override=True)
    
    conn = snow.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
    )
    
    cur = conn.cursor()
    
    try:
        # Create database if not exists
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cur.execute(f"USE DATABASE {database}")
        
        # Create schema if not exists
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        cur.execute(f"USE SCHEMA {schema}")
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv.gz', delete=False) as tmp_file:
            # Write DataFrame directly with pandas
            df.to_csv(
                tmp_file.name,
                sep=sep,
                compression=compression,
                index=index,
                encoding='utf-8'
            )
            
            # Create optimized file format
            cur.execute("""
            CREATE OR REPLACE FILE FORMAT optimized_csv_format
                TYPE = CSV
                FIELD_DELIMITER = ','
                PARSE_HEADER = TRUE
                NULL_IF = ('NULL', 'null', '')
                EMPTY_FIELD_AS_NULL = TRUE
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                ENCODING = 'UTF8'
            """)
            
            # Create internal stage
            cur.execute("CREATE STAGE IF NOT EXISTS temp_stage FILE_FORMAT = optimized_csv_format")
            
            # Upload to stage
            cur.execute(f"""
            PUT file://{tmp_file.name} @temp_stage
            AUTO_COMPRESS = FALSE
            SOURCE_COMPRESSION = {compression.upper()}
            """)
            
            # Create table if not exists
            columns = ', '.join([f"{col} VARCHAR" for col in df.columns])
            cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            
            # Copy into table
            cur.execute(f"""
            COPY INTO {table_name}
            FROM @temp_stage
            FILE_FORMAT = optimized_csv_format
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            PURGE = TRUE
            """)
            
            # Cleanup
            cur.execute("DROP STAGE IF EXISTS temp_stage")
            os.remove(tmp_file.name)
            
        print("Data Import Successful")
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise
        
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    # This will run when file is executed directly
    # file_path = 'data/raw/steam_games_metadata/australian_user_reviews.json'
    file_path = 'data/raw/steam_games_metadata/steam_games_item_metadata.json'
    df = read_json_file(file_path)
    write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "ITEM_METADATA")
    
    # file_path = 'data/raw/bundle_data/bundle_data.json'
    # df = read_json_file(file_path)
    # write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "BUNDLE_DATA")

    # file_path = 'data/raw/steam_reviews/steam_new.json'
    # df = read_json_file(file_path)
    # write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "REVIEWS_DATA")
