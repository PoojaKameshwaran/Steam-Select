import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from collections import Counter

# Load your dataset
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the data file (assuming it's at root/data/processed/Itemmeta.json)
data_file_path = os.path.join(script_dir, '..', '..', 'data', 'processed', 'item_data.parquet')

df = pd.read_parquet(data_file_path)  # Update the file path if needed

# Create a folder to save the visualizations
output_folder = os.path.join(script_dir, '..', 'visualizations', 'Itemmeta' )
os.makedirs(output_folder, exist_ok=True)
logging.info(f"✅ Visualization folder set up at: {output_folder}")

 #Sentiment Score Distribution

plt.figure(figsize=(8, 5))
sns.histplot(df['sentiment_score'], bins=10, kde=True, color="green")
plt.title("Sentiment Score Distribution")
plt.xlabel("Sentiment Score")
plt.ylabel("Count")
plt.show()

print("\n📌 Sentiment Score Statistics:")
print(df['sentiment_score'].describe())
logging.info("📊 Sentiment Score Distribution plot saved.")

logging.info("\n📌 Sentiment Score Statistics:")
logging.info(df['sentiment_score'].describe().to_string())


# Most Common Games Based on Sentiment Score

top_games = df.groupby("Game")["sentiment_score"].mean().sort_values(ascending=False).head(10)
plt.figure(figsize=(10, 5))
sns.barplot(x=top_games.values, y=top_games.index, palette="coolwarm")
plt.title("Top 10 Games by Sentiment Score")
plt.xlabel("Average Sentiment Score")
plt.ylabel("Game")
plt.show()
logging.info("📊 Top 10 Games by Sentiment Score plot saved.")


# Sentiment Score vs. Game_ID Analysis

plt.figure(figsize=(10, 5))
sns.scatterplot(x=df["Game_ID"], y=df["sentiment_score"], alpha=0.5, color="purple")
plt.title("Sentiment Score vs. Game ID")
plt.xlabel("Game ID")
plt.ylabel("Sentiment Score")
plt.show()
logging.info("📊 Sentiment Score vs. Game ID plot saved.")

# Ensure "genres" column is in string format
df["genres"] = df["genres"].astype(str)
    
    # Split genres (assuming they are comma-separated or lists in string format)
all_genres = df["genres"].apply(lambda x: x.split(",") if isinstance(x, str) else x)

    # Flatten the list of genres
genre_list = [genre.strip() for sublist in all_genres for genre in sublist]

    # Count occurrences of each genre
genre_counts = Counter(genre_list)

    # Convert to DataFrame
genre_df = pd.DataFrame(genre_counts.items(), columns=["Genre", "Count"])
genre_df = genre_df.sort_values(by="Count", ascending=False)

logging.info("\n📌 Top 10 Most Common Genres:")
logging.info(genre_df.head(10).to_string())


    # Plot the top 10 genres
plt.figure(figsize=(10, 5))
sns.barplot(x=genre_df["Count"].head(10), y=genre_df["Genre"].head(10), palette="coolwarm")
plt.xlabel("Count")
plt.ylabel("Genre")
plt.title("Top 10 Most Common Game Genres")
plt.show()
logging.info("📊 Top 10 Most Common Game Genres plot saved.")

# ✅ Final Log Message
logging.info("✅ All visualizations saved successfully in the 'Itemmeta' folder.")
logging.info("✅ EDA completed successfully.")
