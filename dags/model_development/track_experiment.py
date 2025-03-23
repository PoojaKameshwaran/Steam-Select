import mlflow
from build_model import (
    split_train_test,
    load_processed_data,
    run_hybrid_recommendation_system,
    evaluate_genre_recommendations
)

def run_experiment():
    # Set experiment name (create if not exists)
    mlflow.set_experiment("Hybrid-Recommender")

    with mlflow.start_run():
        # ✅ Track hyperparameters
        mlflow.log_param("top_k", 10)
        mlflow.log_param("n_neighbors_user", 20)
        mlflow.log_param("n_neighbors_game", 10)

        # 📦 Run model training and evaluation
        split_train_test()
        train_df, test_df, sentiment_df = load_processed_data()
        get_recommendations, *_ = run_hybrid_recommendation_system(train_df)

        # 📊 Evaluate & log metrics
        metrics = evaluate_genre_recommendations(
            get_recommendations, train_df, test_df, sentiment_df, k=10, n_users=10
        )

        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        print("✅ Experiment tracked with MLflow!")

if __name__ == "__main__":
    run_experiment()
