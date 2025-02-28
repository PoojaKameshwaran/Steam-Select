import os 
import pandas as pd
import ast

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Function to clean the DataFrame
def clean_bundle_data(df):
    # PLACE YOUR CODE HERE FOR CLEANING
    
    # Do the necessary data cleaning here
    print("\n📌 Initial Data Info:")
    print(df.info())

    df = df.applymap(lambda x: str(x) if isinstance(x, (list, dict)) else x)
    df.drop_duplicates(inplace=True)
    
    # Handle missing values
    missing_values = df.isnull().sum()
    print("\n🔍 Missing Values Before Cleaning:")
    print(missing_values)

    print("\n📌 Fixing Data Types...")

    # Convert `bundle_final_price` & `bundle_price` to float
    df["bundle_final_price"] = df["bundle_final_price"].replace(r'[\$,]', '', regex=True).astype(float)
    df["bundle_price"] = df["bundle_price"].replace(r'[\$,]', '', regex=True).astype(float)

    df["bundle_discount"] = df["bundle_discount"].astype(str).str.replace('%', '').astype(float)

    # Convert `bundle_id` to integer
    df["bundle_id"] = df["bundle_id"].astype(int)

    # Convert `items` column (currently a JSON-like string) into a list of dictionaries
    df["items"] = df["items"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Verify Fixed Data
    print("\n✅ Data Types After Fixing:")
    print(df.dtypes)

    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    print(df.describe())

    print(f"The shape of the bundle data after cleaned {df.shape}")

    return df

# Function to read the file in batches
def read_and_clean_bundle_file(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(RAW_DATA_DIR, file_name)
    file_name_without_ext = os.path.splitext(os.path.basename(data_file_path))[0]
    chunk_size = 100000
    chunks = pd.read_json(data_file_path, orient='records', lines=True, chunksize=chunk_size)
    
    cleaned_chunks = [clean_bundle_data(chunk) for chunk in chunks]
    
    cleaned_df = pd.concat(cleaned_chunks, ignore_index=True)
    
    write_to_path = os.path.join(PROCESSED_DATA_DIR, file_name_without_ext + '.parquet')
    
    try:
        cleaned_df.to_parquet(write_to_path, compression='snappy')
    except Exception as e:
        for col in cleaned_df.select_dtypes(include=['object']).columns:
            cleaned_df[col] = cleaned_df[col].astype(str)
        
        # Retry saving after converting object columns to string
        cleaned_df.to_parquet(write_to_path, compression='snappy')
    
    print("Dataset cleaned successfully...")
    print("Dataset loaded to data/processed")
    
    # Remove DataFrame from memory
    del cleaned_df

    return write_to_path

if __name__ == "__main__":
    read_and_clean_bundle_file('bundle_data.json')
