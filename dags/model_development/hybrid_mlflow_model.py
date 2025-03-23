import mlflow.pyfunc
import pickle

class HybridRecommenderWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        with open(context.artifacts["model"], "rb") as f:
            self.model_object = pickle.load(f)

    def predict(self, context, model_input):
        """
        model_input: dict with keys: user_id, input_game_ids, genres
        """
        return self.model_object["get_recommendations"](
            user_id=model_input["user_id"],
            input_game_ids=model_input["input_game_ids"],
            missing_game_genres=model_input.get("genres", []),
            sentiment_df=model_input.get("sentiment_df")
        )