import pandas as pd
import yaml
import snowflake.connector
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

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

    # formatting the date
    df["date"] = pd.to_datetime(df["date"], unit="ms").dt.date

    # Landscape of null values
    print("Summary of null values\n")
    print(df.isnull().sum())

    # most of the records did not have compensation values, therefore dropping
    # username is available for all reviews, so dropping user_id which has many empty values and is redundant
    # page, page_order and early access are not necessary for our usecase especially in terms of reviews
    df.drop(columns = ['compensation', 'user_id', 'page_order', 'page', 'early_access'], inplace = True)
    print("Cleaning up non-essential features : compensation, user_id, page_order, page and early_access...")
    print("Dataset after dropping non-essential features...")
    print(df.head())

    # typecasting, null / NaN value handling
    print("Null / NaN value handling and typecasting...")
    df['products'] = df['products'].fillna(0).astype('int64')
    df['found_funny'] = df['found_funny'].fillna(0).astype('int64')
    df['hours'] = df['hours'].fillna(0.0)
    print("Dataset after typecasting, null/NaN value handling")
    print(df.head())

    # renaming column names
    print("Renaming column names for ease of use and reference to other tables...")
    df.columns = ['date', 'found_funny', 'hours', 'item_id', 'item_count', 'review', 'username']

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

    query = f"SELECT * FROM {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.REVIEWS_DATA LIMIT 10000" 
    
    # using chunking to batch load since it is a large file
    chunk_size = 1000
    chunks = pd.read_sql(query, conn, chunksize=chunk_size)

    # Process each chunk separately
    df_list = []
    for chunk in chunks:
        df_list.append(chunk)

    # Concatenate cleaned chunks into final DataFrame
    df= pd.concat(df_list, ignore_index=True)
    conn.close()
    df.columns = [column.lower() for column in df.columns]
    df_cleaned = clean_data(df)
    return df_cleaned

# Example usage
if __name__ == "__main__":
    df_clean = extract_and_clean_data()

