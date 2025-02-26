import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def read_from_json(file_name):
    JSON_PATH= os.path.join(RAW_DATA_DIR,file_name+".json")
    PARQUET_PATH = os.path.join(PROCESSED_DATA_DIR,"raw_"+file_name+".parquet")

    # Read DataFrame from JSON file
    df = pd.read_json(JSON_PATH, lines=True)
    # print(df.info())

    # Convert object columns to string to avoid conversion errors
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str)

    # Save as Parquet
    df.to_parquet(PARQUET_PATH, engine='pyarrow')
    print(f"Successfully read and stored as paraquet file {PARQUET_PATH}")
    # Remove DataFrame from memory
    del df

    return PARQUET_PATH

if __name__ == "__main__":

    print("Running locally")
    read_from_json("item_metadata")