from model_development.build_model import *


MODEL_SAVE_DIR = os.path.join(PROJECT_DIR, "data", "models")
FINAL_MODEL_DIR = os.path.join(MODEL_SAVE_DIR, "tuned_model")
os.makedirs(FINAL_MODEL_DIR, exist_ok=True)


def tune_hyperparams(
    train_df,
    test_df,
    sentiment_df,
    user_n_neighbors_list=[10, 20, 30, 50],
    game_n_neighbors_list=[10, 20],
    metrics=['cosine', 'euclidean', 'manhattan', 'minkowski'],
    k_recs=20,
    n_eval_users=10
):
    """
    Perform a simple grid search over (user_n_neighbors, game_n_neighbors, metric)
    using your existing run_hybrid_recommendation_system and evaluate_genre_recommendations,
    and return ONLY the best parameter set (plus its metrics).

    Parameters
    ----------
    train_df : pd.DataFrame
        Your training set with columns like ['user_id', 'game_id', 'hours'].
    test_df : pd.DataFrame
        Your test set with the same columns.
    sentiment_df : pd.DataFrame
        DataFrame containing game metadata such as ['Game_ID', 'genres'].
    user_n_neighbors_list : list of int
        Possible values for the number of neighbors in the user-based KNN.
    game_n_neighbors_list : list of int
        Possible values for the number of neighbors in the item-based KNN.
    metrics : list of str
        Distance metrics to try (e.g., ['cosine', 'euclidean']).
    k_recs : int
        Number of recommendations to generate (and evaluate) for each user.
    n_eval_users : int or None
        Number of users to evaluate from test_df; None = evaluate all test users.

    Returns
    -------
    best_params : dict or None
        A single dictionary containing the best combination of hyperparameters,
        along with the evaluation metrics (e.g., 'test_genre_hit_rate').
        Returns None if all attempts failed.
    """

    best_params = None  # Will store the best hyperparams (and metrics) encountered
    best_score = -1.0   # Track the highest 'test_genre_hit_rate'

    # Try every combination of user_n_neighbors, game_n_neighbors, and metric.
    for metric in metrics:
        for user_n in user_n_neighbors_list:
            for game_n in game_n_neighbors_list:
                print(f"\n[Grid Search] (user_n={user_n}, game_n={game_n}, metric='{metric}')")

                # 1. Build the hybrid recommender using your existing helper.
                try:
                    get_recommendations, user_to_idx, game_to_idx, idx_to_user, idx_to_game = \
                        run_hybrid_recommendation_system(train_df, user_n, game_n, metric)
                except TypeError as e:
                    print(
                        f"Make sure run_hybrid_recommendation_system accepts "
                        f"user_n_neighbors, game_n_neighbors, and distance_metric. Error: {e}"
                    )
                    continue
                except Exception as e:
                    print(f"Error building hybrid system: {e}")
                    continue

                # 2. Evaluate with your existing evaluation function.
                try:
                    eval_metrics = evaluate_genre_recommendations(
                        get_recommendations=get_recommendations,
                        train_df=train_df,
                        test_df=test_df,
                        sentiment_df=sentiment_df,
                        k=k_recs,
                        n_users=n_eval_users
                    )
                except Exception as e:
                    print(f"Error during evaluation: {e}")
                    continue

                # 3. Check if this combination is better than our current best
                current_score = eval_metrics.get('test_genre_precision', 0.0)
                if current_score > best_score:
                    best_score = current_score
                    best_params = {
                        'user_neighbors': user_n,
                        'game_neighbors': game_n,
                        'metric': metric,
                        **eval_metrics
                    }

    # If we never found a valid combination, best_params would remain None.
    if best_params is None:
        print("\nNo tuning results produced (all attempts may have failed).")
    else:
        print("\nBest hyperparameters by test_genre_precision:")
        print(best_params)

    return best_params


def tuning_task():
    train_df, test_df, sentiment_df = load_processed_data()
    best_params = tune_hyperparams(train_df, test_df, sentiment_df)
    user_n = best_params['user_neighbors']
    game_n = best_params['game_neighbors']
    metric = best_params['metric'] 
    user_game_matrix, game_user_matrix, user_to_idx, game_to_idx, idx_to_user, idx_to_game = build_sparse_matrices(train_df)
    user_model, game_model = build_models(user_game_matrix, game_user_matrix, user_n, game_n, metric)

    best_model_path = os.path.join(FINAL_MODEL_DIR, "tuned_model_v1.pkl")
    best_model_object = {
        "user_model": user_model,
        "game_model": game_model,
        "user_game_matrix": user_game_matrix,
        "game_user_matrix": game_user_matrix,
        "user_to_idx": user_to_idx,
        "game_to_idx": game_to_idx,
        "idx_to_user": idx_to_user,
        "idx_to_game": idx_to_game,
        "metrics": metric
    }

    with open(best_model_path, "wb") as f:
         pickle.dump(best_model_object, f)
    print(f"✅ Saved best model object to: {best_model_path}")