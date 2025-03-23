import os
import tempfile
import mlflow
from mlflow.tracking import MlflowClient
from google.cloud import storage


def select_and_push_best_model():
    model_name = "steam_games_recommender"  # must match your registered model name

    # Set up MLflow client
    client = MlflowClient()
    experiment = client.get_experiment_by_name("steam_games_recommender")
    if experiment is None:
        raise Exception("❌ Experiment 'steam_games_recommender' not found in MLflow.")
    
    experiment_id = experiment.experiment_id

    # Get best run
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        order_by=["metrics.test_genre_precision DESC"],
        max_results=1
    )
    if not runs:
        raise Exception("❌ No runs found in experiment.")

    best_run = runs[0]
    run_id = best_run.info.run_id
    print("✅ Best run ID:", run_id)

    # Promote the best model version to Production
    registered_versions = client.search_model_versions(f"run_id='{run_id}'")
    if not registered_versions:
        raise Exception(f"❌ No registered model version found for run_id: {run_id}")

    version = registered_versions[0].version
    print(f"🚀 Promoting model version {version} to 'Production'")

    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Production",
        archive_existing_versions=True
    )

    # Download entire artifact directory
    local_dir = tempfile.mkdtemp()
    hybrid_model_dir = os.path.join(local_dir, "hybrid_recommender")
    mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="hybrid_recommender", dst_path=local_dir)

    if not os.path.exists(hybrid_model_dir):
        raise Exception(f"❌ hybrid_recommender folder not found at {hybrid_model_dir}")

    print(f"📁 Downloaded model directory to {hybrid_model_dir}")

    # Upload the entire folder to GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket("steam-select")
    destination_prefix = "best_model/hybrid_recommender"

    for root, _, files in os.walk(hybrid_model_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, hybrid_model_dir)
            blob_path = os.path.join(destination_prefix, relative_path)
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
            print(f"✅ Uploaded {blob_path}")

    print(f"🎉 Entire model folder uploaded to GCS at: gs://steam-select/{destination_prefix}/")

if __name__ == "__main__":
    select_and_push_best_model()
