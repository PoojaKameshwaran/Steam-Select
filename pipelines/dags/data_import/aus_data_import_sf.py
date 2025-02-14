import pandas as pd
import json
import gzip
import os
import snowflake.connector as snow
from snowflake.connector.pandas_tools import write_pandas
import getpass

def read_json_file(file_path):
    """
    Reads a JSON or GZIP-compressed JSON file and returns a properly formatted DataFrame.
    """

    try:
        # Attempt to read as a gzipped JSON file
        with gzip.open(file_path, 'rt', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
    except (OSError, gzip.BadGzipFile):
        # Fallback: Read as a regular JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

    return pd.DataFrame(data).fillna('None').astype(str)

def get_snowflake_connection():
    """
    Prompts the user for Snowflake credentials at runtime.
    """
    user = input("Enter your Snowflake username: ")
    password = getpass.getpass("Enter your Snowflake password: ")
    account = input("Enter your Snowflake account (e.g., xyz123.region.cloud): ")
    warehouse = input("Enter your Snowflake warehouse: ")
    database = input("Enter your Snowflake database: ")
    schema = input("Enter your Snowflake schema: ")

    return {
        "user": user,
        "password": password,
        "account": account,
        "warehouse": warehouse,
        "database": database,
        "schema": schema
    }

def write_to_snowflake(df, config, table_name):
    """
    Connects to Snowflake, creates the database/schema/table if not exists, and loads the DataFrame.
    """
    conn = snow.connect(
        user=config["user"],
        password=config["password"],
        account=config["account"],
        warehouse=config["warehouse"]
    )

    cur = conn.cursor()

    # Create database and schema if they do not exist
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']}")
    cur.execute(f"USE DATABASE {config['database']}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {config['schema']}")
    cur.execute(f"USE SCHEMA {config['schema']}")

    # Write DataFrame to Snowflake
    write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        auto_create_table=True
    )

    cur.close()
    conn.close()
    print("✅ Data successfully loaded into Snowflake!")

if __name__ == "__main__":
    # Prompt user for file path
    file_path = r""C:\Users\pooja\Desktop\NEU\Spring '25\IE 7374\aus_user_reviews.json""

    # Read and parse JSON data
    df = read_json_file(file_path)

    # Prompt user for Snowflake credentials
    config = get_snowflake_connection()

    # Table name input
    table_name = input("Enter the Snowflake table name: ").strip()

    # Load data into Snowflake
    write_to_snowflake(df, config, table_name)
