import os
import pandas as pd
import numpy as np
import logging
import pickle
from collections import Counter
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

# --- Global variables for evaluation ---
sample_user = None
sample_user_test_games = None
sample_user_train_games = None
sample_user_recommended_games = None

# --- Set Directories ---
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")
MODEL_SAVE_DIR = os.path.join(PROJECT_DIR, "data", "models")
FINAL_MODEL_DIR = os.path.join(MODEL_SAVE_DIR, "base_model")
os.makedirs(FINAL_MODEL_DIR, exist_ok=True)


# --- Split Train/Test Data ---
def split_train_test():
    cleaned_reviews_path = os.path.join(PROCESSED_DATA_DIR, "cleaned_reviews.parquet")
    df = pd.read_parquet(cleaned_reviews_path)
    logging.info(f"Loaded data from {cleaned_reviews_path}, shape: {df.shape}")

    eligible_users = df[df['count_games'] >= 6]['user_id'].unique()
    num_users_to_pick = max(1, int(len(eligible_users) * 0.05))
    selected_users = np.random.choice(eligible_users, size=num_users_to_pick, replace=False)

    test_set = []
    for user_id in selected_users:
        user_entries = df[df['user_id'] == user_id]
        num_test_entries = min(len(user_entries), np.random.randint(1, 4))
        test_rows = user_entries.sample(n=num_test_entries, random_state=42)
        test_set.append(test_rows)

    test_df = pd.concat(test_set) if test_set else pd.DataFrame(columns=df.columns)
    train_df = df[~df.index.isin(test_df.index)]

    train_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    test_path = os.path.join(PROCESSED_DATA_DIR, "test.csv")
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"Train data saved to: {train_path} ({len(train_df)} rows)")
    print(f"Test data saved to: {test_path} ({len(test_df)} rows)")

    return train_path, test_path

# --- Load Data ---
def load_processed_data():
    train_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    test_path = os.path.join(PROCESSED_DATA_DIR, "test.csv")
    sentiment_path = os.path.join(PROCESSED_DATA_DIR, "reviews_item_cleaned.parquet")
    # item_path = os.path.join(PROCESSED_DATA_DIR, "item_metadata.parquet")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    sentiment_df = pd.read_parquet(sentiment_path)
    # item_df = pd.read_parquet(item_path)

    return train_df, test_df, sentiment_df #, item_df

# --- Matrix + Model Building ---
def build_sparse_matrices(df):
    users = df['user_id'].unique()
    games = df['game_id'].unique()

    user_to_idx = {user: i for i, user in enumerate(users)}
    game_to_idx = {game: i for i, game in enumerate(games)}
    idx_to_user = {i: user for user, i in user_to_idx.items()}
    idx_to_game = {i: game for game, i in game_to_idx.items()}

    user_indices = [user_to_idx[user] for user in df['user_id']]
    game_indices = [game_to_idx[game] for game in df['game_id']]
    hours = df['hours'].values

    user_game_matrix = csr_matrix((hours, (user_indices, game_indices)), shape=(len(users), len(games)))
    game_user_matrix = user_game_matrix.T.tocsr()

    return user_game_matrix, game_user_matrix, user_to_idx, game_to_idx, idx_to_user, idx_to_game

def build_models(user_game_matrix, game_user_matrix, user_n, game_n, metric):
    user_model = NearestNeighbors(n_neighbors=user_n, metric=metric, algorithm='brute')
    user_model.fit(user_game_matrix)

    game_model = NearestNeighbors(n_neighbors=game_n, metric=metric, algorithm='brute')
    game_model.fit(game_user_matrix)

    return user_model, game_model

# --- Genre-Based Recommendation ---
def genre_based_recommendation(genres, sentiment_df, k=10, exclude_games=None):
    if not genres or 'genres' not in sentiment_df.columns:
        return []
    if exclude_games is None:
        exclude_games = []

    game_scores = {}
    for _, row in sentiment_df.iterrows():
        game_id = row['Game_ID']
        if pd.isna(game_id) or game_id in exclude_games:
            continue

        game_genres = row['genres']
        if not isinstance(game_genres, list):
            continue

        matching_genres = set(genres).intersection(set(game_genres))
        match_score = len(matching_genres) / len(genres)

        sentiment_weight = 1.0
        if pd.notna(row.get('sentiment')):
            sentiment_weight = row['sentiment'] / 5.0

        if len(matching_genres) > 0:
            game_scores[game_id] = match_score * sentiment_weight

    sorted_games = sorted(game_scores.items(), key=lambda x: x[1], reverse=True)
    return [game_id for game_id, _ in sorted_games[:k]]

# --- Hybrid Recommendation ---
def hybrid_recommendations(user_id, input_game_ids, df, user_model, game_model,
                          user_game_matrix, user_to_idx, game_to_idx, idx_to_user,
                          idx_to_game, game_user_matrix, missing_game_genres=None,
                          sentiment_df=None, k=10):
    valid_game_ids = [g for g in input_game_ids if g in game_to_idx]
    missing_games = [g for g in input_game_ids if g not in game_to_idx]
    if not valid_game_ids and not missing_game_genres:
        return []

    if user_id not in user_to_idx:
        similar_users = []
        for game_id in valid_game_ids:
            game_players = df[df['game_id'] == game_id]['user_id'].unique()
            similar_users.extend(game_players)
        user_counts = Counter(similar_users)
        top_similar_users = [user for user, _ in user_counts.most_common(20)]

        user_based_recs = {}
        for sim_user in top_similar_users:
            user_games = df[df['user_id'] == sim_user]
            for _, row in user_games.iterrows():
                game_id = row['game_id']
                if game_id in valid_game_ids:
                    continue
                score = min(np.log1p(row['hours']) / 10, 1.0)
                user_based_recs[game_id] = max(user_based_recs.get(game_id, 0), score)

        sorted_recs = sorted(user_based_recs.items(), key=lambda x: x[1], reverse=True)
        recommendations = [game for game, _ in sorted_recs]
    else:
        user_idx = user_to_idx[user_id]
        user_vector = user_game_matrix[user_idx:user_idx+1]
        _, user_indices = user_model.kneighbors(user_vector)

        game_recommendations = {}
        for game_id in valid_game_ids:
            game_idx = game_to_idx[game_id]
            game_vector = game_user_matrix[game_idx:game_idx+1]
            distances, indices = game_model.kneighbors(game_vector)
            for idx, dist in zip(indices[0], distances[0]):
                similar_game = idx_to_game[idx]
                if similar_game != game_id:
                    game_recommendations[similar_game] = max(game_recommendations.get(similar_game, 0), 1 - dist)

        similar_users = [idx_to_user[idx] for idx in user_indices[0] if idx_to_user[idx] != user_id]
        user_based_recs = {}
        for sim_user in similar_users:
            user_games = df[df['user_id'] == sim_user]
            for _, row in user_games.iterrows():
                game_id = row['game_id']
                if game_id in valid_game_ids:
                    continue
                score = min(np.log1p(row['hours']) / 10, 1.0)
                user_based_recs[game_id] = max(user_based_recs.get(game_id, 0), score)

        hybrid_recs = {}
        for game, score in game_recommendations.items():
            hybrid_recs[game] = 0.4 * score
        for game, score in user_based_recs.items():
            hybrid_recs[game] = hybrid_recs.get(game, 0) + 0.6 * score

        sorted_recs = sorted(hybrid_recs.items(), key=lambda x: x[1], reverse=True)
        recommendations = [game for game, _ in sorted_recs]

    if (missing_games or len(recommendations) < k) and missing_game_genres and sentiment_df is not None:
        genre_recommendations = genre_based_recommendation(
            missing_game_genres, sentiment_df, k=k*2,
            exclude_games=valid_game_ids + recommendations
        )
        for game_id in genre_recommendations:
            if game_id not in recommendations:
                recommendations.append(game_id)

    return [int(game_id) for game_id in recommendations[:k]]

# --- Wrapper ---
def run_hybrid_recommendation_system(train_df, user_n, game_n, metric):
    user_game_matrix, game_user_matrix, user_to_idx, game_to_idx, idx_to_user, idx_to_game = build_sparse_matrices(train_df)
    user_model, game_model = build_models(user_game_matrix, game_user_matrix, user_n, game_n, metric)

    def get_recommendations(user_id, input_game_ids, missing_game_genres=None, sentiment_df=None, k=5):
        return hybrid_recommendations(
            user_id, input_game_ids, train_df,
            user_model, game_model,
            user_game_matrix, user_to_idx, game_to_idx,
            idx_to_user, idx_to_game, game_user_matrix,
            missing_game_genres, sentiment_df, k
        )

    return get_recommendations, user_to_idx, game_to_idx, idx_to_user, idx_to_game

# --- Evaluation ---
def evaluate_genre_recommendations(get_recommendations, train_df, test_df, sentiment_df, k=10, n_users=None):
    global sample_user, sample_user_test_games, sample_user_train_games, sample_user_recommended_games

    game_genre_mapping = sentiment_df.set_index('Game_ID')['genres'].to_dict()
    unique_users_games_test = test_df.groupby('user_id')['game_id'].apply(list).to_dict()
    unique_users_games_train = train_df.groupby('user_id')['game_id'].apply(list).to_dict()

    test_users = list(unique_users_games_test.keys())
    if n_users is not None:
        test_users = np.random.choice(test_users, size=min(n_users, len(test_users)), replace=False)

    print(f"Evaluating on {len(test_users)} users out of {len(unique_users_games_test)} total users")

    train_genre_precision = []
    train_genre_recall = []
    train_genre_hit_rate = 0
    test_genre_precision = []
    test_genre_recall = []
    test_genre_hit_rate = 0
    evaluated_users = 0

    for user_id in test_users:
        if user_id not in unique_users_games_train:
            continue
        train_games = unique_users_games_train[user_id]
        test_games = unique_users_games_test[user_id]
        if len(train_games) == 0 or len(test_games) == 0:
            continue

        train_genres = {g for game in train_games for g in game_genre_mapping.get(game, [])}
        test_genres = {g for game in test_games for g in game_genre_mapping.get(game, [])}
        if not train_genres or not test_genres:
            continue

        try:
            recommendations = get_recommendations(user_id, train_games)
        except Exception as e:
            print(f"Error for user {user_id}: {e}")
            continue

        recommended_genres = {g for game in recommendations for g in game_genre_mapping.get(game, [])}
        if not recommended_genres:
            continue

        # Train metrics
        train_rel = train_genres.intersection(recommended_genres)
        train_genre_precision.append(len(train_rel) / len(recommended_genres))
        train_genre_recall.append(len(train_rel) / len(train_genres))
        if len(train_rel) > 0:
            train_genre_hit_rate += 1

        # Test metrics
        test_rel = test_genres.intersection(recommended_genres)
        test_genre_precision.append(len(test_rel) / len(recommended_genres))
        test_genre_recall.append(len(test_rel) / len(test_genres))
        if len(test_rel) > 0:
            test_genre_hit_rate += 1

        evaluated_users += 1
        sample_user = user_id
        sample_user_test_games = test_games
        sample_user_train_games = train_games
        sample_user_recommended_games = recommendations

    metrics = {
        'train_genre_precision': np.mean(train_genre_precision) if train_genre_precision else 0,
        'train_genre_recall': np.mean(train_genre_recall) if train_genre_recall else 0,
        'train_genre_hit_rate': train_genre_hit_rate / evaluated_users if evaluated_users else 0,
        'test_genre_precision': np.mean(test_genre_precision) if test_genre_precision else 0,
        'test_genre_recall': np.mean(test_genre_recall) if test_genre_recall else 0,
        'test_genre_hit_rate': test_genre_hit_rate / evaluated_users if evaluated_users else 0,
        'num_evaluated_users': evaluated_users
    }

    print("\nEvaluation Results:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
    print(f"\nSample User: {sample_user}")
    print(f"Train Games: {sample_user_train_games}")
    print(f"Test Games: {sample_user_test_games}")
    print(f"Recommended Games: {sample_user_recommended_games}")

    return metrics

def wrapper_build_model_function():
    # cleaned_reviews_path = os.path.join(PROCESSED_DATA_DIR, "cleaned_reviews.parquet")
    split_train_test()
    user_n = 20
    game_n = 10
    metric = 'cosine'
    train_df, test_df, sentiment_df = load_processed_data()
    get_recommendations, *_ = run_hybrid_recommendation_system(train_df, user_n, game_n, metric)

    metrics = evaluate_genre_recommendations(
        get_recommendations, train_df, test_df, sentiment_df, k=10, n_users=10
    )
    # Build and capture actual models and mappings
    user_game_matrix, game_user_matrix, user_to_idx, game_to_idx, idx_to_user, idx_to_game = build_sparse_matrices(train_df)
    user_model, game_model = build_models(user_game_matrix, game_user_matrix, user_n, game_n, metric)

    # Save actual model components
    best_model_path = os.path.join(FINAL_MODEL_DIR, "model_v1.pkl")
    best_model_object = {
        "user_model": user_model,
        "game_model": game_model,
        "user_game_matrix": user_game_matrix,
        "game_user_matrix": game_user_matrix,
        "user_to_idx": user_to_idx,
        "game_to_idx": game_to_idx,
        "idx_to_user": idx_to_user,
        "idx_to_game": idx_to_game,
        "metrics": metrics
    }

    with open(best_model_path, "wb") as f:
         pickle.dump(best_model_object, f)
    print(f"✅ Saved best model object to: {best_model_path}")


# --- MAIN ---
if __name__ == "__main__":
    wrapper_build_model_function()