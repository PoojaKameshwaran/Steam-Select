import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from collections import Counter

def eda_item_data(file_path):
    print(file_path)
    # Load your dataset
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the data file
    data_file_path = file_path

    df = pd.read_parquet(data_file_path)  # Update the file path if needed

    # Create a folder to save the visualizations
    output_folder = os.path.join(script_dir, '..', 'visualizations', 'reviews')
    os.makedirs(output_folder, exist_ok=True)

    # Log findings
    logging.info("Data Overview:")
    logging.info(f"{df.info()}")

    logging.info("Missing Values:")
    missing_values = df.isnull().sum()
    logging.info(f"{missing_values}")

    # PLACE YOUR CODE HERE FOR VISUALIZATION

    plt.figure(figsize=(8, 5))
    sns.histplot(df['sentiment_score'], bins=10, kde=True, color="green")
    plt.title("Sentiment Score Distribution")
    plt.xlabel("Sentiment Score")
    plt.ylabel("Count")
    plt.show()

    # Most Common Games Based on Sentiment Score
    top_games = df.groupby("Game")["sentiment_score"].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=top_games.values, y=top_games.index, palette="coolwarm")
    plt.title("Top 10 Games by Sentiment Score")
    plt.xlabel("Average Sentiment Score")
    plt.ylabel("Game")
    plt.show()

    # Sentiment Score vs. Game_ID Analysis
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x=df["Game_ID"], y=df["sentiment_score"], alpha=0.5, color="purple")
    plt.title("Sentiment Score vs. Game ID")
    plt.xlabel("Game ID")
    plt.ylabel("Sentiment Score")
    plt.show()

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

    # Plot the top 10 genres
    plt.figure(figsize=(10, 5))
    sns.barplot(x=genre_df["Count"].head(10), y=genre_df["Genre"].head(10), palette="coolwarm")
    plt.xlabel("Count")
    plt.ylabel("Genre")
    plt.title("Top 10 Most Common Game Genres")
    plt.show()

    # Log additional findings after plotting
    logging.info(f"Visualizations saved in the '{output_folder}' folder.")

    return None

if __name__ == "__main__":
    eda_item_data("C:\\Users\\Shruthi\\Desktop\\Northeastern files\\ML Ops\\Steam Project\\Steam-Select\\data\\processed\\item_metadata.parquet")
