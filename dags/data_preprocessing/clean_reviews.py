import os
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
    df.drop_duplicates(inplace = True)

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
    # only product_id and text are necessary for our usecase especially in terms of reviews
    df.drop(columns = ['compensation', 'user_id', 'username', 'found_funny', \
                       'hours', 'page_order', 'page', 'early_access', 'products'], inplace = True)
    print("Cleaning up non-essential features : compensation, user_id, page_order, page, early_access etc...")
    print("Dataset after dropping non-essential features...")
    print(df.head())

    # Typecasting
    # No null handling needed since product_id has no null values
    print("Null / NaN value handling and typecasting...")
    df['product_id'] = df['product_id'].fillna(0).astype('int64')
    print("Dataset after typecasting, null/NaN value handling")
    print(df.head())

    # renaming column names
    print("Renaming column names for ease of use and reference to other tables...")
    df.columns = ['id', 'review']

    print("Dataset after data cleaning...")
    print(df.head())

    return df

if __name__ == "__main__":

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the data file (assuming it's at root/data/processed/reviews.json)
    data_file_path = os.path.join(script_dir, '..', '..', 'data', 'raw', 'reviews.json')

    chunk_size = 100000
    chunks = pd.read_json(data_file_path, orient='records', lines=True, chunksize=chunk_size)
    
    cleaned_chunks = []
    for chunk in chunks:
        cleaned_chunk = clean_data(chunk)
        cleaned_chunks.append(cleaned_chunk)

    cleaned_df = pd.concat(cleaned_chunks, ignore_index=True)

    write_to_path = data_file_path = os.path.join(script_dir, '..', '..', 'data', 'processed', 'reviews.json')
    cleaned_df.to_json(write_to_path, orient = 'records', lines = True)
    print("Dataset cleaned successfully...")
    print("Dataset loaded to data/processed")

