import os
import pickle
import mlflow
import mlflow.pyfunc

# --- Define the model wrapper class ---
class HybridRecommenderWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        model_path = os.path.join(context.artifacts["model_dir"], "model_v1.pkl")
        with open(model_path, "rb") as f:
            model_data = pickle.load(f)
        self.model = model_data
        self.get_recommendations = model_data.get("get_recommendations")

    def predict(self, context, model_input):
        """
        model_input: Dict with keys:
          - user_id: string or int
          - input_game_ids: list of game ids
          - missing_game_genres: list of genres (optional)
          - sentiment_df: pd.DataFrame with 'genres' and 'sentiment' columns
          - k: number of recommendations (optional, default = 5)
        """
        return self.get_recommendations(
            model_input["user_id"],
            model_input["input_game_ids"],
            missing_game_genres=model_input.get("missing_game_genres"),
            sentiment_df=model_input.get("sentiment_df"),
            k=model_input.get("k", 5)
        )


# --- Wrapper function to log model to MLflow ---
def log_model_to_mlflow(model_path: str, model_name: str, experiment_name: str = "steam_games_recommender", run_name: str = "baseline_v1"):
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name):
        # Load the model object
        full_model_path = os.path.join(model_path, model_name)
        with open(full_model_path, "rb") as f:
            model_object = pickle.load(f)

        # Log metrics (optional)
        metrics = model_object.get("metrics", {})
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                mlflow.log_metric(key, value)

        # Log and register the model in MLflow
        mlflow.pyfunc.log_model(
            artifact_path="hybrid_recommender",
            python_model=HybridRecommenderWrapper(),
            artifacts={"model_dir": model_path},
            registered_model_name="steam_games_recommender"  # ✅ Consistent model name
        )

        print("✅ Model logged and registered to MLflow successfully!")


# --- MAIN ---
if __name__ == "__main__":
    model_path = os.path.join(os.getcwd(), "data", "models", "base_model")
    log_model_to_mlflow(model_path, "model_v1.pkl")