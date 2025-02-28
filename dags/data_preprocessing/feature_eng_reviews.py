from download_data import download_from_gcp
import os
import dask.dataframe as dd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd

# Ensure VADER lexicon is available
nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer once (avoiding reloading for each row)
sia = SentimentIntensityAnalyzer()

# Function to calculate sentiment score
def get_sentiment_score(text):
    """Assigns a sentiment score (1-5) based on VADER's compound score."""
    if pd.isna(text) or not isinstance(text, str):
        return 3  # Neutral score for missing values
    
    sentiment = sia.polarity_scores(text)["compound"]
    
    if sentiment <= -0.6:
        return 1  # Very Negative
    elif sentiment <= -0.2:
        return 2  # Negative
    elif sentiment <= 0.2:
        return 3  # Neutral
    elif sentiment <= 0.6:
        return 4  # Positive
    else:
        return 5  # Very Positive

if __name__ == "__main__":
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Set up project directories
    DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Downloading Processed REVIEWS...")
    download_from_gcp("steam-select", "staging/reviews.parquet", PROJECT_DIR, DATA_DIR)
    print("Successfully loaded REVIEWS to processed.")

    # File paths
    input_file = os.path.join(DATA_DIR, "reviews.parquet")
    output_file = os.path.join(DATA_DIR, "reviews_sentiment.parquet")

    # Load data using Dask
    df = dd.read_parquet(input_file)

    # Apply sentiment analysis using map_partitions (more efficient than map)
    df["sentiment_score"] = df["review"].map_partitions(
        lambda series: series.apply(get_sentiment_score),
        meta=("sentiment_score", "int")
    )

    # Drop review text to save memory
    df = df.drop(columns=["review"])

    # Group by product_id and compute rounded mean sentiment score
    df_grouped = df.groupby("id")["sentiment_score"].mean().round().astype("int").reset_index()

    # Convert to Pandas for efficient saving
    df_grouped = df_grouped.compute()

    # Write output to Parquet with compression
    df_grouped.to_parquet(output_file, compression="snappy", index=False)

    print("Sentiment analysis complete. Grouped file saved to:", output_file)