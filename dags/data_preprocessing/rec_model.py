import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import os

# -------------------- STEP 1: MODEL IMPLEMENTATION -------------------- #

def preprocess_data(item_df):
    """Prepare data by creating a genre string and normalizing sentiment scores."""
    item_df['genre_str'] = item_df['genres'].apply(lambda x: ' '.join(x))
    scaler = MinMaxScaler()
    item_df['normalized_sentiment'] = scaler.fit_transform(item_df[['sentiment']])
    return item_df, scaler

def build_tfidf_model(item_df):
    """Creates a TF-IDF matrix based on game genres and applies dimensionality reduction."""
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(item_df['genre_str'])

    # Get number of available features
    n_features = tfidf_matrix.shape[1]

    # Set SVD components dynamically
    n_components = min(100, n_features - 1) if n_features > 1 else 1  # Avoid zero or negative components

    # Apply SVD for dimensionality reduction
    svd = TruncatedSVD(n_components=n_components)
    reduced_matrix = svd.fit_transform(tfidf_matrix)

    return csr_matrix(reduced_matrix), tfidf, svd


def zero_shot_recommendation(steam_game_genres, item_df, tfidf_matrix, top_n=5):
    """Handles cases where a game is not found in the dataset by using genre-based matching."""
    genre_str = ' '.join(steam_game_genres)
    tfidf_vectorizer = TfidfVectorizer()
    new_vector = tfidf_vectorizer.fit_transform([genre_str])
    cosine_sim = cosine_similarity(new_vector, tfidf_matrix).flatten()
    similar_games_indices = cosine_sim.argsort()[::-1][:top_n]
    return item_df.iloc[similar_games_indices]['Game'].tolist()

def get_game_recommendations(user_games, item_df, tfidf_matrix, top_n=5):
    """Recommend games based on optimized cosine similarity and sentiment scores."""
    game_indices = item_df[item_df['Game'].isin(user_games)].index.tolist()
    if not game_indices:
        return "No matching games found in dataset. Performing zero-shot recommendation.", zero_shot_recommendation(user_games, item_df, tfidf_matrix, top_n)
    
    # Compute similarity scores with optimized sparse matrix computation
    cosine_sim = cosine_similarity(tfidf_matrix[game_indices], tfidf_matrix).mean(axis=0)
    
    # Rank games by similarity, excluding input games
    similar_games_indices = cosine_sim.argsort()[::-1]
    recommended_games = []
    for idx in similar_games_indices:
        if item_df.iloc[idx]['Game'] not in user_games:
            recommended_games.append((item_df.iloc[idx]['Game'], item_df.iloc[idx]['normalized_sentiment']))
        if len(recommended_games) >= top_n * 2:  # Retrieve more to filter by sentiment
            break
    
    # Sort by sentiment score and return top N games
    recommended_games = sorted(recommended_games, key=lambda x: x[1], reverse=True)[:top_n]
    return [game[0] for game in recommended_games]

# -------------------- STEP 2: MODEL SAVING -------------------- #

def save_model(tfidf_matrix, tfidf, scaler, svd, filename='recommender_model.pkl'):
    """Saves the model components to a file."""
    with open(filename, 'wb') as file:
        pickle.dump((tfidf_matrix, tfidf, scaler, svd), file)

# -------------------- STEP 3: MODEL EVALUATION -------------------- #

def evaluate_model(recommended_games, item_df, all_games, user_games):
    """Evaluates the model using sentiment-weighted NDCG, diversity, serendipity, and coverage scores."""
    def ndcg(recommended_games, item_df):
        def dcg(scores):
            return np.sum(scores / np.log2(np.arange(2, len(scores) + 2)))
        
        sentiments = np.array([item_df[item_df['Game'] == game]['normalized_sentiment'].values[0] for game in recommended_games if game in item_df['Game'].values])
        dcg_value = dcg(sentiments)
        idcg_value = dcg(sorted(sentiments, reverse=True))
        return dcg_value / idcg_value if idcg_value > 0 else 0
    
    def diversity_score(recommended_games, item_df):
        unique_genres = set()
        for game in recommended_games:
            genres = item_df[item_df['Game'] == game]['genres'].values
            if len(genres) > 0:
                unique_genres.update(genres[0])
        return len(unique_genres) / len(recommended_games) if recommended_games else 0
    
    def serendipity_score(recommended_games, user_games):
        surprising_games = [game for game in recommended_games if game not in user_games]
        return len(surprising_games) / len(recommended_games) if recommended_games else 0
    
    def coverage_score(all_games, recommended_games):
        unique_recommended = set(recommended_games)
        return len(unique_recommended) / len(all_games) if all_games else 0
    
    return {
        "NDCG": ndcg(recommended_games, item_df),
        "Diversity Score": diversity_score(recommended_games, item_df),
        "Serendipity Score": serendipity_score(recommended_games, user_games),
        "Coverage Score": coverage_score(all_games, recommended_games)
    }

# -------------------- STEP 4: MODEL FINE-TUNING -------------------- #

def fine_tune_model(item_df, tfidf_matrix, penalty_factor=0.2):
    """Applies fine-tuning techniques to improve recommendations."""
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    adjusted_scores = cosine_sim - (penalty_factor * cosine_sim.std())
    
    # Apply TSNE for non-linear dimensionality reduction
    tsne = TSNE(n_components=2, perplexity=30, random_state=42)
    embedded_matrix = tsne.fit_transform(tfidf_matrix.toarray())
    
    return np.clip(adjusted_scores, 0, 1), embedded_matrix

# -------------------- STEP 5: RETRAIN AND SAVE UPDATED MODEL -------------------- #

def retrain_and_save_model(item_df, filename='recommender_model_v2.pkl'):
    """Rebuilds and saves the improved model with fine-tuning."""
    item_df, scaler = preprocess_data(item_df)
    tfidf_matrix, tfidf, svd = build_tfidf_model(item_df)
    adjusted_scores, embedded_matrix = fine_tune_model(item_df, tfidf_matrix)
    save_model(adjusted_scores, tfidf, scaler, svd, filename)
    return tfidf_matrix, tfidf, scaler, svd, embedded_matrix

if __name__ == "__main__":
    # Load Data
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Set up project directories
    DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
    file_path = os.path.join(DATA_DIR, "reviews_item_cleaned.parquet")
    item_df = pd.read_parquet(file_path)

    # Example Usage
    user_games = ["Lost Summoner Kitty", "Ironbound"]
    item_df, scaler = preprocess_data(item_df)
    tfidf_matrix, tfidf, svd = build_tfidf_model(item_df)
    recommendations = get_game_recommendations(user_games, item_df, tfidf_matrix)
    print("Recommended Games:", recommendations)

    all_games = list(item_df['Game'].unique())+
    metrics = evaluate_model(recommendations, item_df, all_games, user_games)
    for metric in metrics.keys():
        print(f"{metric} : {metrics[metric]}")
    save_model(tfidf_matrix, tfidf, scaler, svd, filename='recommender_model_v1.pkl')

    tfidf_matrix, tfidf, scaler, svd, embedded_matrix = retrain_and_save_model(item_df, filename='recommender_model_v2.pkl')
    recommendations = get_game_recommendations(user_games, item_df, tfidf_matrix)
    print("Recommended Games:", recommendations)

    all_games = list(item_df['Game'].unique())
    metrics = evaluate_model(recommendations, item_df, all_games, user_games)
    for metric in metrics.keys():
        print(f"{metric} : {metrics[metric]}")

    print("Models saved appropriately, choose the best model")