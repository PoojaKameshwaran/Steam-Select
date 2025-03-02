import os
import pandas as pd
import dask.dataframe as dd
import pyarrow.parquet as pq
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from custom_logging import get_logger

# Initialize logger
logger = get_logger("feature_engineering")

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Ensure VADER lexicon is available
nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer once (avoiding reloading for each row)
sia = SentimentIntensityAnalyzer()

# Function to round the mean to the closest predefined sentiment value
def round_to_closest(value, sentiment_values):
    return min(sentiment_values, key=lambda x: abs(x - value))

def feature_df_reviews_data(df):
    """Processes the DataFrame to add sentiment score and aggregate by product ID."""
    try:
        logger.info("Starting feature engineering on reviews data.")
        
        # Convert to a dask dataframe for fast processing
        dask_df = dd.from_pandas(df, npartitions=4)  # You can set the number of partitions

        # Apply sentiment analysis using map_partitions (more efficient than map)
        dask_df["sentiment_score"] = dask_df["review"].map_partitions(
            lambda series: series.apply(get_sentiment_score),
            meta=("sentiment_score", "int")
        )

        # Drop review text to save memory
        dask_df = dask_df.drop(columns=["review"])

        # Define the predefined sentiment values
        sentiment_values = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]

        # Apply the rounding function
        df_grouped = dask_df.groupby("id")["sentiment_score"].mean().apply(lambda x: round_to_closest(x, sentiment_values)).reset_index()

        logger.info(f"Feature engineering completed.")
        
        # Convert to Pandas for efficient saving
        df_grouped = df_grouped.compute()
        return df_grouped
    except Exception as e:
        logger.error(f"Error during feature engineering: {str(e)}", exc_info=True)
        raise

def get_sentiment_score(text):
    """Assigns a sentiment score (1-5) based on VADER's compound score."""
    try:
        if pd.isna(text) or not isinstance(text, str):
            return 3  # Neutral score for missing values
        
        sentiment = sia.polarity_scores(text)["compound"]
        
        # Mapping sentiment based on predefined ranges
        if sentiment <= -0.8:
            return 1  # Overwhelmingly Negative
        elif sentiment <= -0.6:
            return 1.5  # Mostly Negative
        elif sentiment <= -0.4:
            return 2  # Very Negative
        elif sentiment <= -0.2:
            return 2.5  # Negative
        elif sentiment <= 0:
            return 3  # Mixed/Neutral
        elif sentiment <= 0.2:
            return 3.5  # Positive
        elif sentiment <= 0.4:
            return 4  # Very Positive
        elif sentiment <= 0.6:
            return 4.5  # Mostly Positive
        else:
            return 5  # Overwhelmingly Positive
    except Exception as e:
        logger.error(f"Error computing sentiment score: {str(e)}", exc_info=True)
        return 3  # Default to neutral in case of error

def feature_engineering_cleaned_reviews_file(file_name):
    """Reads the Parquet file in chunks, applies feature engineering, and saves the output."""
    try:
        data_file_path = os.path.join(PROCESSED_DATA_DIR, file_name)
        write_to_path = os.path.join(PROCESSED_DATA_DIR, file_name.replace('.parquet', '_cleaned.parquet'))

        logger.info(f"Processing file: {data_file_path}")
        parquet_file = pq.ParquetFile(data_file_path)
        num_row_groups = parquet_file.num_row_groups
        logger.info(f"Total row groups in parquet file: {num_row_groups}")

        cleaned_chunks = []
        for i in range(num_row_groups):  # Iterate over row groups instead of rows
            logger.info(f"Processing row group {i + 1} of {num_row_groups}")
            chunk = parquet_file.read_row_group(i).to_pandas()
            cleaned_chunk = feature_df_reviews_data(chunk)  # Apply cleaning function
            cleaned_chunks.append(cleaned_chunk)

        cleaned_df = pd.concat(cleaned_chunks, ignore_index=True)
        
        # Save cleaned data
        cleaned_df.to_parquet(write_to_path, compression='snappy')
        del cleaned_df
        
        logger.info(f"Dataset preprocessed and saved to: {write_to_path}")
        return write_to_path
    except Exception as e:
        logger.error(f"Error in feature engineering pipeline: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting feature engineering script.")
        feature_engineering_cleaned_reviews_file('reviews.parquet')
        logger.info("Feature engineering script completed successfully.")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}", exc_info=True)
