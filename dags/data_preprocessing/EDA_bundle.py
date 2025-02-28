import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

def eda_bundle_data(file_path):
    # Load your dataset
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the data file (assuming it's at root/data/processed/reviews.json)
    data_file_path = file_path

    df = pd.read_parquet(data_file_path)  # Update the file path if needed

    # Create a folder to save the visualizations
    output_folder = os.path.join(script_dir, '..', 'visualizations', 'reviews' )
    os.makedirs(output_folder, exist_ok=True)

    # Log findings
    logging.info("Data Overview:")
    logging.info(f"{df.info()}")

    logging.info("Missing Values:")
    missing_values = df.isnull().sum()
    logging.info(f"{missing_values}")


    # DO THE VISUALIZATION HERE

    

    # Log additional findings after plotting
    logging.info(f"Visualizations saved in the '{output_folder}' folder.")

    return None

if __name__ == "__main__":
    eda_bundle_data("d:\\Learning\\MlOps\\Steam-Select\\data\\processed\\bundle_data.parquet")

