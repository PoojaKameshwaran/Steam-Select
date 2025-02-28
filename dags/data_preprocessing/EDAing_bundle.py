import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import Counter

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def EDA_bundle(file_path):
    PARQUET_INPUT_PATH = file_path
    # Change the name of the file for temp storage
    PARQUET_OUTPUT_PATH = os.path.join(PROCESSED_DATA_DIR, "EDA_bundle.parquet") 

    # Read DataFrame from Parquet file
    df = pd.read_parquet(PARQUET_INPUT_PATH, engine='pyarrow')
    print(f"Read Parquet file with shape {df.shape}")

    
    # ----- Visualize Price Distribution -----
    plt.figure(figsize=(8, 5))
    sns.histplot(df["bundle_final_price"], bins=30, kde=True)
    plt.xlabel("Final Bundle Price ($)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Bundle Prices")
    plt.show()

    # ----- Price vs. Discount Scatter Plot -----
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=df["bundle_price"], y=df["bundle_discount"], alpha=0.7)
    plt.xlabel("Bundle Price ($)")
    plt.ylabel("Discount (%)")
    plt.title("Bundle Price vs. Discount")
    plt.show()

    # ----- Box Plot of Prices (Detecting Outliers) -----
    plt.figure(figsize=(8, 5))
    sns.boxplot(x=df["bundle_final_price"])
    plt.xlabel("Final Bundle Price ($)")
    plt.title("Box Plot of Bundle Final Prices")
    plt.show()

    # ----- Distribution of Bundle Sizes (Number of Items per Bundle) -----

    df["total_items"] = df["items"].apply(lambda x: len(eval(x)) if isinstance(x, str) else len(x))
    plt.figure(figsize=(8, 5))
    sns.histplot(df["total_items"], bins=20, kde=True)
    plt.xlabel("Number of Items in Bundle")
    plt.ylabel("Count")
    plt.title("Distribution of Bundle Sizes")
    plt.show()

    # ----- Top 10 Most Expensive Bundles -----
    top_expensive = df.sort_values(by="bundle_final_price", ascending=False).head(10)

    plt.figure(figsize=(10, 5))
    sns.barplot(y=top_expensive["bundle_name"], x=top_expensive["bundle_final_price"])
    plt.xlabel("Final Price ($)")
    plt.ylabel("Bundle Name")
    plt.title("Top 10 Most Expensive Bundles")
    plt.show()

    # ----- Relationship Between Discount & Number of Items -----
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=df["total_items"], y=df["bundle_discount"], alpha=0.7)
    plt.xlabel("Number of Items in Bundle")
    plt.ylabel("Discount (%)")
    plt.title("Number of Items vs. Discount")
    plt.show()

    # Save as Parquet
    df.to_parquet(PARQUET_OUTPUT_PATH, engine='pyarrow')
    print(f"Cleaned df stored as Parquet file: {PARQUET_OUTPUT_PATH}")
    print(os.path.dirname(os.path.abspath(PARQUET_OUTPUT_PATH)))
    print(os.path.splitext(os.path.basename(PARQUET_OUTPUT_PATH))[0])

    # Remove DataFrame from memory
    del df

    return PARQUET_OUTPUT_PATH

if __name__ == "__main__":
    print("Running locally")
    EDA_bundle("C:\\Users\\Shruthi\\Desktop\\Northeastern files\\ML Ops\\Steam Project\\Steam-Select\\data\\processed\\cleaned_bundle.parquet")
