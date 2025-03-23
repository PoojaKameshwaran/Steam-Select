import os
import pandas as pd
import numpy as np
from build_model import (
    load_processed_data,
    build_sparse_matrices,
    build_models,
    hybrid_recommendations,
    evaluate_genre_recommendations
)

# Set up output log directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SENSITIVITY_DIR = os.path.join(PROJECT_DIR, "dags", "bias_sensitivity_analysis")
os.makedirs(SENSITIVITY_DIR, exist_ok=True)
CSV_PATH = os.path.join(SENSITIVITY_DIR, "sensitivity_analysis.csv")

def run_sensitivity_analysis():
    print("📦 Loading data...")
    train_df, test_df, sentiment_df = load_processed_data()
    user_game_matrix, game_user_matrix, user_to_idx, game_to_idx, idx_to_user, idx_to_game = build_sparse_matrices(train_df)

    print("🧪 Starting hyperparameter sensitivity tests...")

    # Sensitivity analysis settings
    neighbor_settings = [10, 20, 30]
    distance_metrics = ['cosine', 'euclidean']
    hybrid_weights = [(0.3, 0.7), (0.5, 0.5), (0.7, 0.3)]
    k_values = [5, 10]

    results = []

    for metric in distance_metrics:
        for n_neighbors in neighbor_settings:
            # Build models with current neighbor + metric config
            user_model, game_model = build_models(user_game_matrix, game_user_matrix, n_neighbors, n_neighbors, metric)

            for user_weight, game_weight in hybrid_weights:
                for k in k_values:
                    print(f"\n➡️ Testing with neighbors={n_neighbors}, metric={metric}, weights=({user_weight},{game_weight}), k={k}")

                    def get_recommendations(user_id, input_game_ids, missing_game_genres=None, sentiment_df=None, top_k=k):
                        # hybrid_recommendations must use passed weights
                        return hybrid_recommendations(
                            user_id, input_game_ids, train_df,
                            user_model, game_model,
                            user_game_matrix, user_to_idx, game_to_idx,
                            idx_to_user, idx_to_game, game_user_matrix,
                            missing_game_genres, sentiment_df, top_k,
                            user_weight=user_weight, game_weight=game_weight
                        )

                    try:
                        metrics = evaluate_genre_recommendations(
                            get_recommendations, train_df, test_df, sentiment_df,
                            k=k, n_users=10
                        )
                    except Exception as e:
                        print(f"❌ Evaluation failed: {e}")
                        continue

                    row = {
                        "n_neighbors": n_neighbors,
                        "metric": metric,
                        "user_weight": user_weight,
                        "game_weight": game_weight,
                        "top_k": k,
                        **metrics
                    }

                    results.append(row)

    df = pd.DataFrame(results)
    df.to_csv(CSV_PATH, index=False)
    print(f"\n✅ Sensitivity analysis results saved to: {CSV_PATH}")

if __name__ == "__main__":
    run_sensitivity_analysis()
