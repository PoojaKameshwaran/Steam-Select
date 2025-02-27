import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def preprocess_item_metadata(file_path):
    PARQUET_INPUT_PATH= file_path
    #change the name of the file for temp storage
    PARQUET_OUTPUT_PATH = os.path.join(PROCESSED_DATA_DIR,"preprocessed_data_item.parquet") 

    # Read DataFrame from PARAQUET file
    df = pd.read_parquet(PARQUET_INPUT_PATH, engine='pyarrow')
    print(f"Read paraquet file with shape {df.shape}")

    # Do the necessary data cleaning here
    

    # Save as Parquet
    df.to_parquet(PARQUET_OUTPUT_PATH, engine='pyarrow')
    print(f"Cleaned df stored as paraquet file {PARQUET_OUTPUT_PATH}")
    print(os.path.dirname(os.path.abspath(PARQUET_OUTPUT_PATH)))
    print(os.path.splitext(os.path.basename(PARQUET_OUTPUT_PATH))[0])
    # Remove DataFrame from memory
    del df

    return PARQUET_OUTPUT_PATH

if __name__ == "__main__":

    print("Running locally")
    preprocess_item_metadata("d:\\Learning\\MlOps\\Steam-Select\\data\\processed\\cleaned_data_item.parquet")