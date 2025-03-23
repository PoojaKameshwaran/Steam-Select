import os
import pandas as pd
import numpy as np
import datetime

from build_model import run_hybrid_recommendation_system, load_processed_data, evaluate_genre_recommendations


# --- Step 1: Slice Users by Activity Level ---
def get_user_activity_slices(df, threshold=10):
    user_activity = df.groupby('user_id').size()
    low_activity_users = user_activity[user_activity <= threshold].index
    high_activity_users = user_activity[user_activity > threshold].index
    return low_activity_users, high_activity_users


# --- Step 2: Evaluate Model Separately for Each Group ---
def evaluate_user_slices(train_df, test_df, sentiment_df, get_recommendations):
    low_users, high_users = get_user_activity_slices(train_df)

    print("\n🔹 Evaluating Low Activity Users:")
    low_test_df = test_df[test_df['user_id'].isin(low_users)]
    low_metrics = evaluate_genre_recommendations(get_recommendations, train_df, low_test_df, sentiment_df, k=10, n_users=10)

    print("\n🔹 Evaluating High Activity Users:")
    high_test_df = test_df[test_df['user_id'].isin(high_users)]
    high_metrics = evaluate_genre_recommendations(get_recommendations, train_df, high_test_df, sentiment_df, k=10, n_users=10)

    return low_metrics, high_metrics


# --- Step 3: Save Metrics to logs/bias_results.csv ---
def log_metrics_to_csv(low_metrics, high_metrics, output_filename="bias_results.csv"):
    # Locate root directory (steam-select/)
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(PROJECT_DIR, "dags","model_development")
    os.makedirs(log_dir, exist_ok=True)

    # Output file path
    output_path = os.path.join(log_dir, output_filename)

    # Create DataFrame
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([
        {"timestamp": timestamp, "group": "low_activity", **low_metrics},
        {"timestamp": timestamp, "group": "high_activity", **high_metrics}
    ])

    # Append or write new
    if os.path.exists(output_path):
        df.to_csv(output_path, mode='a', header=False, index=False)
    else:
        df.to_csv(output_path, index=False)

    print(f"\n✅ Bias metrics saved to: {output_path}")


# --- Step 4: Main Runner ---
def run_bias_analysis():
    print("📦 Loading data and model...")
    train_df, test_df, sentiment_df = load_processed_data()
    get_recommendations, *_ = run_hybrid_recommendation_system(train_df)

    print("🧪 Running bias detection...")
    low_metrics, high_metrics = evaluate_user_slices(train_df, test_df, sentiment_df, get_recommendations)

    print("\n📊 Summary of Bias Evaluation:")
    print("Low Activity Users:", low_metrics)
    print("High Activity Users:", high_metrics)

    log_metrics_to_csv(low_metrics, high_metrics)


# --- CLI Entry Point ---
if __name__ == "__main__":
    run_bias_analysis()

