import pickle
import os
import sys
import pandas as pd
import requests
import random
import numpy as np

from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # Adjust based on actual depth
sys.path.append(str(PROJECT_ROOT))

# Now use absolute import
from dags.model_development.build_model import hybrid_recommendations

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_FILE_PATH = os.path.join(PROJECT_DIR, "data", "models", "base_model", "model_v1.pkl")
PROCESSED_PATH = os.path.join(PROJECT_DIR, "data", "processed")
DF_PATH = os.path.join(PROCESSED_PATH, "train.csv")
SENTIMENT_PATH = os.path.join(PROCESSED_PATH, "reviews_item_cleaned.parquet")

def get_genre_from_gameid(game_ids):
    url = "https://store.steampowered.com/api/appdetails"

    genre_gameid_mapping = {}

    for game_id in game_ids:
        params = {
            "appids": game_id
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # print(data)
            # print("data is here", data[str(game_id)]["data"]["type"])
            if data[str(game_id)]["success"]:
                # genre_gameid_mapping[game_id] = 
                # print(data[str(game_id)]["data"]["genres"])
                genre_list = data[str(game_id)]["data"]["genres"]
                genres = []
                # print()
                for genre in genre_list:
                    genres.append(genre["description"])
                genre_gameid_mapping[game_id] = genres
            else:
                print("No genres found for the game id :",game_id)
        else:
            print("API Key is not working. Status Code:", response.status_code)
    return list(set(genre for genres in genre_gameid_mapping.values() for genre in genres))


def recommend_games_from_model(game_ids, missing_game_genres, user_id=None, k=5):

    try:
        # Load the saved model
        with open(MODEL_FILE_PATH, 'rb') as file:
            model = pickle.load(file)
        
        # Extract components from the loaded model
        user_model = model['user_model']
        game_model = model['game_model']
        user_game_matrix = model['user_game_matrix']
        game_user_matrix = model['game_user_matrix']
        user_to_idx = model['user_to_idx']
        game_to_idx = model['game_to_idx']
        idx_to_user = model['idx_to_user']
        idx_to_game = model['idx_to_game']
        trained = pd.read_csv(DF_PATH)
        sentiment = pd.read_parquet(SENTIMENT_PATH)

        # Validate input game IDs
        valid_game_ids = [game for game in game_ids if game in game_to_idx]

        # Initialize a list to store recommendations
        max_game_recommend = []

        # Select a random user if user_id is None
        user_ids = trained['user_id'].unique()

        # If user_id is None, assign a random user_id from trained using numpy
        user_id = user_id if user_id is not None else np.random.choice(user_ids)

        # Debug: Print the selected user_id
        # print("Selected user_id:", user_id)

        # Generate recommendations using hybrid logic
        while len(max_game_recommend) < k:
            recommendations = hybrid_recommendations(
                user_id=user_id,
                input_game_ids=valid_game_ids,
                df=trained,
                user_model=user_model,
                game_model=game_model,
                user_game_matrix=user_game_matrix,
                user_to_idx=user_to_idx,
                game_to_idx=game_to_idx,
                idx_to_user=idx_to_user,
                idx_to_game=idx_to_game,
                game_user_matrix=game_user_matrix,
                missing_game_genres=missing_game_genres,
                sentiment_df=sentiment,
                k=k
            )
            max_game_recommend.extend(recommendations)
            if len(max_game_recommend) < k:
                # Randomly choose a new user_id to ensure variety in recommendations
                user_id = np.random.choice(user_ids)
                # print("New random user_id for the next recommendation:", user_id)

        return max_game_recommend[:3]  # Ensure we return only the top 'k' recommendations

    except Exception as e:
        print(f"An error occurred: {e}")
        return []



# Example usage
if __name__ == "__main__":
    # user_id = 249288  # Replace with actual user ID
    game_ids = [578080, 1282270, 3241660]  # Replace with actual list of game IDs
    # Get recommendations
    recommended_games = recommend_games_from_model(game_ids, get_genre_from_gameid(game_ids))
    print("Recommended Games:", recommended_games)
