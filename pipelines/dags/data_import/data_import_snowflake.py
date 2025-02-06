# steam_reviews_loader.py
import pandas as pd
import ast
import snowflake.connector as snow
from snowflake.connector.pandas_tools import write_pandas
import os
from dotenv import load_dotenv
import json
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

def write_to_snowflake(df, database, schema, table_name):
    load_dotenv(override=True)
    # print("Helooooooooooooo")
    # print(os.getenv('SNOWFLAKE_ACCOUNT'))
    conn = snow.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
    )
    
    cur = conn.cursor()
    
    # Create database if not exists
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    cur.execute(f"USE DATABASE {database}")
    
    # Create schema if not exists
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    cur.execute(f"USE SCHEMA {schema}")
    
    # Write DataFrame with auto table creation
    write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        auto_create_table=True
    )
    
    cur.close()
    conn.close()

    print("Data Import Successfull")

if __name__ == "__main__":
    # This will run when file is executed directly
    # file_path = 'data/raw/steam_games_metadata/australian_user_reviews.json'
    # file_path = 'data/raw/steam_games_metadata/steam_games_item_metadata.json'
    # df = read_json_file(file_path)
    # write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "ITEM_METADATA")
    
    # file_path = 'data/raw/bundle_data/bundle_data.json'
    # df = read_json_file(file_path)
    # write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "BUNDLE_DATA")

    file_path = 'data/raw/steam_reviews/steam_new.json'
    df = read_json_file(file_path)
    write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "REVIEWS_DATA")
