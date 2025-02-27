import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging


# Load your dataset
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the data file (assuming it's at root/data/processed/reviews.json)
data_file_path = os.path.join(script_dir, '..', '..', 'data', 'processed', 'reviews.parquet')

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


# Visualizations

# 1. Counts of reviews per product_id
review_counts = df['product_id'].value_counts().reset_index()
review_counts.columns = ['product_id', 'review_count']

# Plot the counts of reviews per product_id
plt.figure(figsize=(12, 6))
sns.barplot(x='product_id', y='review_count', data=review_counts.head(20))  # Display top 20 product_ids with most reviews
plt.title('Top 20 Product IDs by Review Count')
plt.xlabel('Product ID')
plt.ylabel('Number of Reviews')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'review_counts_per_product.png'))
plt.close()
logging.info("Top 20 product review counts plot saved as 'review_counts_per_product.png'.")

# 2. Distribution of review counts
plt.figure(figsize=(10, 6))
sns.histplot(review_counts['review_count'], kde=True)
plt.title('Distribution of Review Counts per Product')
plt.xlabel('Number of Reviews per Product')
plt.ylabel('Frequency')
plt.savefig(os.path.join(output_folder, 'review_counts_distribution.png'))
plt.close()
logging.info("Review counts distribution plot saved as 'review_counts_distribution.png'.")

# Log additional findings after plotting
logging.info(f"Visualizations saved in the '{output_folder}' folder.")

