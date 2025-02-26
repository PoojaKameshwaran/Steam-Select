import pandas as pd
import yaml
import snowflake.connector
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from snowflake.connector.pandas_tools import pd_writer

# Snowflake Connection using Airflow Hook
def get_snowflake_connection():
    hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
    return hook.get_conn()

# Function to clean the DataFrame
def clean_data(df):
    # Drop duplicate records
    df = df.drop_duplicates()

    # Trim whitespace from string columns
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

    # Formatting the date
    df["date"] = pd.to_datetime(df["date"], unit="ms").dt.date

    # Landscape of null values
    print("Summary of null values\n")
    print(df.isnull().sum())

    # Dropping unnecessary columns
    df.drop(columns = ['compensation', 'user_id', 'page_order', 'page', 'products', 'early_access'], inplace = True)
    print("Cleaning up non-essential features : compensation, user_id, products, page_order, page and early_access...")
    print("Dataset after dropping non-essential features...")
    print(df.head())

    # Typecasting, null/NaN value handling
    df['found_funny'] = df['found_funny'].fillna(0).astype('int64')
    df['hours'] = df['hours'].fillna(0.0)
    print("Dataset after typecasting, null/NaN value handling")
    print(df.head())

    # Renaming column names
    df.columns = ['date', 'found_funny', 'hours', 'item_id', 'review', 'username']
    print("Dataset after data cleaning...")
    print(df.head())

    return df

# Main function to extract, clean, and return DataFrame
def extract_and_clean_data():
    conn = get_snowflake_connection()

    # Load schema.yml
    SCHEMA_FILE = "/opt/airflow/dags/data_import/schema.yml"
    with open(SCHEMA_FILE, "r") as f:
        schema = yaml.safe_load(f)
    
    SNOWFLAKE_DATABASE = schema['database']
    SNOWFLAKE_SCHEMA = schema['schema']

    query = f"SELECT * FROM {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.REVIEWS_DATA LIMIT 100000"

    # Using chunking to batch load since it is a large file
    chunk_size = 1000
    chunks = pd.read_sql(query, conn, chunksize=chunk_size)

    # Process each chunk separately
    df_list = []
    for chunk in chunks:
        df_list.append(chunk)

    # Concatenate cleaned chunks into final DataFrame
    df = pd.concat(df_list, ignore_index=True)
    conn.close()

    df.columns = [column.lower() for column in df.columns]
    df_cleaned = clean_data(df)
    
    return df_cleaned

# Function to create schema, table, and load data into Snowflake
def create_schema_and_load_data(df_cleaned):
    conn = get_snowflake_connection()
    
    # Load schema.yml to get database and schema details
    SCHEMA_FILE = "/opt/airflow/dags/data_import/schema.yml"
    with open(SCHEMA_FILE, "r") as f:
        schema = yaml.safe_load(f)
    
    SNOWFLAKE_DATABASE = schema['database']
    SNOWFLAKE_SCHEMA = schema['schema'] + "_CLEANED"

    # Create the schema if it does not exist
    create_schema_query = f"""
    CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA};
    """
    with conn.cursor() as cur:
        cur.execute(create_schema_query)

    # Create the table if it does not exist
    create_table_query = f"""
    CREATE OR REPLACE TABLE {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.cleaned_reviews_data (
        date DATE,
        found_funny INT,
        hours FLOAT,
        item_id INT,
        review STRING,
        username STRING
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_table_query)

    # Load the cleaned DataFrame into Snowflake using pandas' pd_writer
    # Snowflake's pd_writer method should be used for inserting data into Snowflake
    df_cleaned.to_sql(
        'REVIEWS_DATA', 
        con=conn, 
        schema=SNOWFLAKE_SCHEMA, 
        if_exists='replace', 
        index=False, 
        method=pd_writer
    )

    print("Data successfully loaded into Snowflake.")
    conn.close()

# Example usage
if __name__ == "__main__":
    df_clean = extract_and_clean_data()
    create_schema_and_load_data(df_clean)
