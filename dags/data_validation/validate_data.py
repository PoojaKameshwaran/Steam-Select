import os
import pandas as pd
import logging
import json
import numpy as np 

# Define paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "dags", "Data_validation_reports")
LOG_DIR = os.path.join(PROJECT_DIR,"logs")

# Ensure necessary directories exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Define logger (Fixing the "logger not defined" error)
logger = logging.getLogger("data_validation")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "validation.log"), mode="a")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def validate_data(df, file_name):
    """Perform data validation checks and log issues."""
    issues = []

    # Convert list-type or dictionary-type columns to strings before checking duplicates
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
    # ✅ Fix for columns like 'price' that mix numbers & strings
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")  # Convert to numeric, set errors to NaN


    

    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        issues.append(f"Missing values found in {file_name}: \n{missing_values}")

    # Check for duplicate rows (after fixing unhashable types)
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        issues.append(f"{duplicate_count} duplicate rows found in {file_name}")

    # Check numerical columns for negative values
    for col in df.select_dtypes(include=['number']).columns:
        negatives = (df[col] < 0).sum()
        if negatives > 0:
            issues.append(f"{negatives} negative values found in {col} of {file_name}")

    # Log validation issues
    if issues:
        with open(os.path.join(PROCESSED_DATA_DIR, "validation_report.txt"), "a") as report:
            report.write("\n".join(issues) + "\n")
        logger.warning(f"Validation issues detected in {file_name}")  
    else:
        logger.info(f"{file_name} passed validation checks.")  
    return None  # Return validated DataFrame

def read_and_validate_file(file_name):
    """Read a JSON file and validate the data."""
    file_path = os.path.join(RAW_DATA_DIR, file_name)
    
    # Check if file exists before loading
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    df = pd.read_json(file_path, orient="records", lines=True)
    return validate_data(df, file_name)
if __name__=="__main__":
    read_and_validate_file("item_metadata.json")
    



