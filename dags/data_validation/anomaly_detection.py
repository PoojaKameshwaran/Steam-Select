import os
import pandas as pd
import json
import logging

# Define paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "dags","Data_validation_reports")
DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")

# Ensure necessary directories exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logger
logger = logging.getLogger("anomaly_detection")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "anomaly.log"), mode="a")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def detect_anomalies(df, file_name):
    """Detect anomalies in numerical and categorical data."""
    results = {"issues": {}}

    # Check for negative values in numerical columns
    for col in df.select_dtypes(include=['number']).columns:
        negatives = (df[col] < 0).sum()
        if negatives > 0:
            results["issues"][f"{col}_negative"] = f"{negatives} negative values in {col}"
            logger.warning(f"{negatives} negative values detected in {col}")

    # Check for unexpected categorical values
    allowed_values = {
        "marital": ["married", "single", "divorced"],
        "education": ["primary", "secondary", "tertiary", "unknown"],
        "loan": ["yes", "no"],
    }

    for col, expected_values in allowed_values.items():
        if col in df.columns:
            invalid_values = set(df[col].unique()) - set(expected_values)
            if invalid_values:
                results["issues"][f"{col}_invalid"] = f"Unexpected values found: {invalid_values}"
                logger.warning(f"Unexpected values detected in {col}: {invalid_values}")

    # Save results
    output_json = os.path.join(PROCESSED_DATA_DIR, "anomaly_results.json")
    with open(output_json, "w") as f:
        json.dump(results, f, indent=4)

    logger.info("Anomaly detection complete. Results saved.")
    return results

def read_and_detect_anomalies(file_name):
    """Load and analyze file for anomalies."""
    file_path = os.path.join(DATA_DIR, file_name)
    df = pd.read_json(file_path, orient="records", lines=True)
    return detect_anomalies(df, file_name)

if __name__ == "__main__":
    read_and_detect_anomalies("item_metadata.json")
