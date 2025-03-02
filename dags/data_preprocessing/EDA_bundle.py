import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from custom_logging import get_logger

logger = get_logger('EDA')


def eda_bundle_data(file_path):
    # Load your dataset
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the data file
    data_file_path = file_path

    df = pd.read_parquet(data_file_path)  # Update the file path if needed

    # Create a folder to save the visualizations
    output_folder = os.path.join(script_dir, '..', 'visualizations', 'bundle')
    os.makedirs(output_folder, exist_ok=True)

    # Log findings
    logger.info("Data Overview:")
    logger.info(f"{df.info()}")

    logger.info("Missing Values:")
    missing_values = df.isnull().sum()
    logger.info(f"{missing_values}")

    # PLACE YOUR CODE HERE FOR VISUALIZATION

    plt.figure(figsize=(8, 5))
    sns.histplot(df["bundle_final_price"], bins=30, kde=True)
    plt.xlabel("Final Bundle Price ($)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Bundle Prices")
    plt.savefig(os.path.join(output_folder, 'Distribution of Bundle Prices.png'))
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=df["bundle_price"], y=df["bundle_discount"], alpha=0.7)
    plt.xlabel("Bundle Price ($)")
    plt.ylabel("Discount (%)")
    plt.title("Bundle Price vs. Discount")
    plt.savefig(os.path.join(output_folder, 'Bundle Price vs. Discount.png'))
    plt.close()

    # Box Plot of Prices (Detecting Outliers)
    plt.figure(figsize=(8, 5))
    sns.boxplot(x=df["bundle_final_price"])
    plt.xlabel("Final Bundle Price ($)")
    plt.title("Box Plot of Bundle Final Prices")
    plt.savefig(os.path.join(output_folder, 'Box Plot of Bundle Final Prices.png'))
    plt.close()

    df["total_items"] = df["items"].apply(lambda x: len(eval(x)) if isinstance(x, str) else len(x))

    # Distribution of Bundle Sizes (Number of Items per Bundle)
    plt.figure(figsize=(8, 5))
    sns.histplot(df["total_items"], bins=20, kde=True)
    plt.xlabel("Number of Items in Bundle")
    plt.ylabel("Count")
    plt.title("Distribution of Bundle Sizes")
    plt.savefig(os.path.join(output_folder, 'Distribution of Bundle Sizes.png'))
    plt.show()

    top_expensive = df.sort_values(by="bundle_final_price", ascending=False).head(10)
    plt.figure(figsize=(10, 5))
    sns.barplot(y=top_expensive["bundle_name"], x=top_expensive["bundle_final_price"])
    plt.xlabel("Final Price ($)")
    plt.ylabel("Bundle Name")
    plt.title("Top 10 Most Expensive Bundles")
    plt.savefig(os.path.join(output_folder, 'Top 10 Most Expensive Bundles.png'))
    plt.show()

    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=df["total_items"], y=df["bundle_discount"], alpha=0.7)
    plt.xlabel("Number of Items in Bundle")
    plt.ylabel("Discount (%)")
    plt.title("Number of Items vs. Discount")
    plt.savefig(os.path.join(output_folder, 'Number of Items vs. Discount.png'))
    plt.show()

    # Log additional findings after plotting
    logger.info(f"Visualizations saved in the '{output_folder}' folder.")

    return None

if __name__ == "__main__":
    eda_bundle_data("C:\\Users\\Shruthi\\Desktop\\Northeastern files\\ML Ops\\Steam Project\\Steam-Select\\data\\processed\\bundle_data.parquet")
