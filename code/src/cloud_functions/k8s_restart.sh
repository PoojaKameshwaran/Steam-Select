#!/bin/bash

# Get cluster credentials
gcloud container clusters get-credentials steam-select-clusters --region=us-east1 --project=poojaproject

# Restart the flask-app deployment
kubectl rollout restart deployment flask-app

echo "Flask deployment restart triggered successfully"