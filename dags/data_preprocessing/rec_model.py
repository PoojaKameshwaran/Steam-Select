import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from difflib import get_close_matches
import os

def preprocess_data(item_df):
    """
    Convert the genres list into a string format suitable for TF-IDF processing.
    """
    item_df['genre_str'] = item_df['genres'].apply(lambda x: ' '.join(x))
    return item_df

def build_tfidf_model(item_df):
    """
    Create a TF-IDF matrix from the genre data.
    """
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(item_df['genre_str'])
    return tfidf_matrix, tfidf

def find_closest_games(user_games, item_df):
    """
    Find the closest matching games from the dataset.
    """
    matched_games = []
    for game in user_games:
        matches = get_close_matches(game, item_df['Game'].tolist(), n=1, cutoff=0.6)
        if matches:
            matched_games.append(matches[0])
    return matched_games

def get_genre_based_recommendations(user_games, item_df, top_n=5):
    """
    Recommend games based on shared genres if no exact matches are found.
    """
    genre_counts = {}
    for game in user_games:
        game_row = item_df[item_df['Game'] == game]
        if not game_row.empty:
            genres = game_row.iloc[0]['genres']
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    if not genre_counts:
        return []
    
    sorted_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)
    filtered_games = item_df[item_df['genres'].apply(lambda g: any(genre in g for genre in sorted_genres))]
    filtered_games = filtered_games.sort_values(by=['sentiment'], ascending=False)
    return filtered_games['Game'].head(top_n).tolist()

def get_game_recommendations(user_games, item_df, tfidf_matrix, top_n=5):
    """
    Recommend similar games based on linear kernel (optimized cosine similarity) and sentiment scores.
    """
    matched_games = find_closest_games(user_games, item_df)
    if not matched_games:
        return get_genre_based_recommendations(user_games, item_df, top_n)
    
    game_indices = item_df[item_df['Game'].isin(matched_games)].index.tolist()
    if not game_indices:
        return "No matching games found in dataset. Please check your input."
    
    # Compute similarity scores using a memory-efficient method
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    similarity_scores = cosine_sim[game_indices].mean(axis=0)  # Average similarity across input games
    
    # Rank games by similarity, excluding input games
    similar_games_indices = similarity_scores.argsort()[::-1]
    recommended_games = []
    for idx in similar_games_indices:
        if item_df.iloc[idx]['Game'] not in matched_games:
            recommended_games.append((item_df.iloc[idx]['Game'], item_df.iloc[idx]['sentiment']))
        if len(recommended_games) >= top_n * 2:  # Retrieve more to filter by sentiment
            break
    
    # Sort by sentiment score and return top N games
    recommended_games = sorted(recommended_games, key=lambda x: x[1], reverse=True)[:top_n]
    return [game[0] for game in recommended_games]

# Load Data
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Set up project directories
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
file_path = os.path.join(DATA_DIR, "reviews_item_cleaned.parquet")
item_df = pd.read_parquet(file_path)

item_df = preprocess_data(item_df)
tfidf_matrix, _ = build_tfidf_model(item_df)

# Example Usage
user_games = ["Lost Summoner Kitty", "Ironbound"]
recommendations = get_game_recommendations(user_games, item_df, tfidf_matrix)
print("Recommended Games:", recommendations)
