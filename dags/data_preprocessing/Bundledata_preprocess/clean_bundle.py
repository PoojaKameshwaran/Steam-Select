import os
import pandas as pd
import yaml
import ast  
import snowflake.connector
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook


# Snowflake Connection using Airflow Hook
def get_snowflake_connection():
    hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
    return hook.get_conn()


# Function to clean the DataFrame
def clean_data(df):
    print("\n📌 Initial Data Info:")
    print(df.info())

    # 1️⃣ Remove duplicate rows
    df.drop_duplicates(inplace=True)  

    # 2️⃣ Handle missing values
    missing_values = df.isnull().sum()
    print("\n🔍 Missing Values Before Cleaning:")
    print(missing_values)

    print("\n📌 Fixing Data Types...")

    # 3️⃣ Convert `bundle_final_price` & `bundle_price` to float
    df["bundle_final_price"] = df["bundle_final_price"].replace(r'[\$,]', '', regex=True).astype(float)
    df["bundle_price"] = df["bundle_price"].replace(r'[\$,]', '', regex=True).astype(float)

    # Convert `bundle_discount` to float (some values are decimals)
    df["bundle_discount"] = df["bundle_discount"].str.replace('%', '').astype(float)

    # If you want it as an integer (rounded):
    df["bundle_discount"] = df["bundle_discount"].round().astype(int)

    # 4️⃣ Convert `bundle_id` to integer
    df["bundle_id"] = df["bundle_id"].astype(int)

    # 5️⃣ Convert `items` column (currently a JSON-like string) into a list of dictionaries
    df["items"] = df["items"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # ----------------- Verify Fixed Data -----------------
    print("\n✅ Data Types After Fixing:")
    print(df.dtypes)

    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    print(df.describe())

    return df  


if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the data file (assuming it's at root/data/raw/bundledata.json)
    data_file_path = os.path.join(script_dir, '..', '..', 'data', 'raw', 'bundledata.json')

    # Load data (assuming JSON format)
    try:
        df = pd.read_json(data_file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        exit(1)

    # Clean the dataset
    df = clean_data(df)

    # Define processed file path
    write_to_path = os.path.join(script_dir, '..', '..', 'data', 'processed', 'bundledata.parquet')

    # Save the cleaned dataset
    df.to_parquet(write_to_path, compression='snappy')

    print("✅ Dataset cleaned successfully...")
    print("✅ Dataset loaded to data/processed")