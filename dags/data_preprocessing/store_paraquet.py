import os
import pandas as pd
import ast
from custom_logging import get_logger

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = get_logger('Data_Download')

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def read_from_json_to_paraquet(file_path):

    if isinstance(file_path, str):
        try:
            file_path = ast.literal_eval(file_path)  # Convert stringified list back to list
        except (SyntaxError, ValueError):
            file_path = [file_path]  # If it's not a valid list, wrap it as a list

    parquet_files = []
    print(f" the file path LIST in storeparaquet {file_path} with type as {type(file_path)}")
    for file in list(file_path):
        JSON_PATH = file
        file_name = os.path.splitext(os.path.basename(JSON_PATH))[0]
        PARQUET_PATH = os.path.join(PROCESSED_DATA_DIR, f"raw_{file_name}.parquet")
        
        chunk_size = 100000  # Process in chunks to reduce memory usage
        print(f" the file path in for loop {file}")
        # Read JSON in chunks
        chunks = pd.read_json(JSON_PATH, lines=True, chunksize=chunk_size)
        
        # Collect all chunks
        all_chunks = []
        for chunk in chunks:
            # Convert object columns to string
            for col in chunk.select_dtypes(include=['object']).columns:
                chunk[col] = chunk[col].astype(str)
            all_chunks.append(chunk)
            print(f"Processed a chunk for {file_name}")
        
        # Combine all chunks and write to parquet
        if all_chunks:
            combined_df = pd.concat(all_chunks, ignore_index=True)
            combined_df.to_parquet(PARQUET_PATH, engine='pyarrow')
            parquet_files.append(PARQUET_PATH)
            print(f"Successfully read and stored as parquet file {PARQUET_PATH}")
            logger.info(f"Successfully read and stored as parquet file {PARQUET_PATH}")
        else:
            print(f"No data found in {JSON_PATH}")
            logger.error(f"No data found in {JSON_PATH}", exc_info=True)
    
    return parquet_files


if __name__ == "__main__":
    file_path = [
        "d:\\Learning\\MlOps\\Steam-Select\\data\\raw\\item_metadata.json"
    ]
    read_from_json_to_paraquet(file_path)
