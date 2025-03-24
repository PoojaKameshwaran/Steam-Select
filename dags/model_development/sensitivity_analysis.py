import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

def run_sensitivity_analysis():
    # Set up directories
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODEL_SAVE_DIR = os.path.join(PROJECT_DIR, "data", "models")
    FINAL_MODEL_DIR = os.path.join(MODEL_SAVE_DIR, "tuned_model")
    SENSITIVITY_DIR = os.path.join(PROJECT_DIR, "dags", "bias_sensitivity_analysis")
    os.makedirs(SENSITIVITY_DIR, exist_ok=True)

    # Load the tuned model
    model_path = os.path.join(FINAL_MODEL_DIR, "tuned_model_v1.pkl")
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)

    # Extract model components
    user_model = model_data['user_model']
    game_model = model_data['game_model']
    user_game_matrix = model_data['user_game_matrix']
    game_user_matrix = model_data['game_user_matrix']
    idx_to_game = model_data['idx_to_game']

    # Feature importance analysis with SHAP
    # Sample a small subset for faster processing
    sample_size = min(50, user_game_matrix.shape[0])
    sample_indices = np.random.choice(user_game_matrix.shape[0], sample_size, replace=False)
    sample_matrix = user_game_matrix[sample_indices].toarray()

    # Modify your model_predict function to ensure compatible output shape
    def model_predict(x):
        # Ensure output shape matches input samples
        distances, _ = user_model.kneighbors(x, return_distance=True)
        # Return first neighbor distance for each sample
        return distances[:, 0]  # This should match the number of samples in x

    # Use fewer samples or a different explainer
    explainer = shap.Explainer(model_predict, sample_matrix[:10])
    # Or
    explainer = shap.KernelExplainer(model_predict, sample_matrix[:10], link="identity")

    # Create explainer with a small subset of data
    explainer = shap.KernelExplainer(model_predict, sample_matrix[:10])

    # Calculate SHAP values for a few samples
    shap_values = explainer.shap_values(sample_matrix[:5], nsamples=100)

    # Create and save summary plot
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, sample_matrix[:5], show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(SENSITIVITY_DIR, 'shap_feature_importance.png'))
    plt.close()

    print(f"✅ SHAP analysis completed and saved to {SENSITIVITY_DIR}")

    # Save feature importance scores
    feature_importance = np.abs(shap_values).mean(0)
    top_features_idx = np.argsort(-feature_importance)[:20]
    top_features = [(idx_to_game.get(i, f"GameID_{i}"), feature_importance[i]) 
                    for i in top_features_idx]

    # Save to CSV
    pd.DataFrame(top_features, columns=['Game', 'Importance']).to_csv(
        os.path.join(SENSITIVITY_DIR, 'feature_importance.csv'), index=False)

    print("✅ Feature importance analysis completed successfully")

# --- CLI Entry Point ---
if __name__ == "__main__":
    run_sensitivity_analysis()
