import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging


# Load your dataset
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the data file (assuming it's at root/data/processed/bundledata.json)
data_file_path = os.path.join(script_dir, '..', '..', 'data', 'processed', 'bundledata.parquet')

df = pd.read_parquet(data_file_path)  # Update the file path if needed

# Create a folder to save the visualizations
output_folder = os.path.join(script_dir, '..', 'visualizations', 'bundledata' )
os.makedirs(output_folder, exist_ok=True)

# Visualizations

from collections import Counter

all_genres = [genre for sublist in df["unique_genres"] for genre in sublist]
genre_counts = pd.DataFrame(Counter(all_genres).most_common(), columns=["Genre", "Count"])

plt.figure(figsize=(10,5))
sns.barplot(x=genre_counts["Genre"][:10], y=genre_counts["Count"][:10])
plt.xticks(rotation=45)
plt.xlabel("Genre")
plt.ylabel("Number of Bundles")
plt.title("Top 10 Most Common Game Genres in Bundles")
plt.show()

#Visualize Price Distribution

plt.figure(figsize=(8,5))
sns.histplot(df["bundle_final_price"], bins=30, kde=True)
plt.xlabel("Final Bundle Price ($)")
plt.ylabel("Frequency")
plt.title("Distribution of Bundle Prices")
plt.show()

# Price vs. Discount Scatter Plot

plt.figure(figsize=(8,5))
sns.scatterplot(x=df["bundle_price"], y=df["bundle_discount"], alpha=0.7)
plt.xlabel("Bundle Price ($)")
plt.ylabel("Discount (%)")
plt.title("Bundle Price vs. Discount")
plt.show()

#Box Plot of Prices (Detecting Outliers)

plt.figure(figsize=(8,5))
sns.boxplot(x=df["bundle_final_price"])
plt.xlabel("Final Bundle Price ($)")
plt.title("Box Plot of Bundle Final Prices")
plt.show()

# Distribution of Bundle Sizes (Number of Items per Bundle)
#Purpose: Identifies how many games are typically included in a bundle.
plt.figure(figsize=(8,5))
sns.histplot(df["total_items"], bins=20, kde=True)
plt.xlabel("Number of Items in Bundle")
plt.ylabel("Count")
plt.title("Distribution of Bundle Sizes")
plt.show()


#Top 10 Most Expensive Bundles
# Purpose: Identifies the highest-priced game bundles.
top_expensive = df.sort_values(by="bundle_final_price", ascending=False).head(10)

plt.figure(figsize=(10,5))
sns.barplot(y=top_expensive["bundle_name"], x=top_expensive["bundle_final_price"])
plt.xlabel("Final Price ($)")
plt.ylabel("Bundle Name")
plt.title("Top 10 Most Expensive Bundles")
plt.show()

#Relationship Between Discount & Number of Items
# Purpose: Do larger bundles get higher discounts?

plt.figure(figsize=(8,5))
sns.scatterplot(x=df["total_items"], y=df["bundle_discount"], alpha=0.7)
plt.xlabel("Number of Items in Bundle")
plt.ylabel("Discount (%)")
plt.title("Number of Items vs. Discount")
plt.show()

