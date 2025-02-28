import os
import ast
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def clean_bundle(file_path):
    PARQUET_INPUT_PATH = file_path
    PARQUET_OUTPUT_PATH = os.path.join(PROCESSED_DATA_DIR, "cleaned_bundle.parquet")

    # Read DataFrame from PARQUET file
    df = pd.read_parquet(PARQUET_INPUT_PATH, engine='pyarrow')
    print(f"Read PARQUET file with shape {df.shape}")

    # Do the necessary data cleaning here
    print("\n📌 Initial Data Info:")
    print(df.info())

    print(df.shape())

    df = df.applymap(lambda x: str(x) if isinstance(x, (list, dict)) else x)
    df.drop_duplicates(inplace=True)

    # 2️⃣ Handle missing values
    missing_values = df.isnull().sum()
    print("\n🔍 Missing Values Before Cleaning:")
    print(missing_values)

    print("\n📌 Fixing Data Types...")

    # 3️⃣ Convert `bundle_final_price` & `bundle_price` to float
    df["bundle_final_price"] = df["bundle_final_price"].replace(r'[\$,]', '', regex=True).astype(float)
    df["bundle_price"] = df["bundle_price"].replace(r'[\$,]', '', regex=True).astype(float)

    # Convert `bundle_discount` to float
    df["bundle_discount"] = df["bundle_discount"].astype(str).str.replace('%', '').astype(float)

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

    # Save as Parquet
    df.to_parquet(PARQUET_OUTPUT_PATH, engine='pyarrow')
    print(f"Cleaned df stored as PARQUET file {PARQUET_OUTPUT_PATH}")
    print(os.path.dirname(os.path.abspath(PARQUET_OUTPUT_PATH)))
    print(os.path.splitext(os.path.basename(PARQUET_OUTPUT_PATH))[0])

    # Remove DataFrame from memory
    del df

    return PARQUET_OUTPUT_PATH

if __name__ == "__main__":
    print("Running locally")
    clean_bundle("C:\\Users\\Shruthi\\Desktop\\Northeastern files\\ML Ops\\Steam Project\\Steam-Select\\data\\processed\\bundle_data.parquet")
