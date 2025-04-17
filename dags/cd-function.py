import requests
import os

def trigger_deploy(event, context):
    github_token = os.environ.get("GITHUB_TOKEN")
    github_repo = os.environ.get("GITHUB_REPO")
    github_branch = os.environ.get("GITHUB_BRANCH", "deploy-automation")
    github_workflow = os.environ.get("GITHUB_WORKFLOW", "deploy.yaml")

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{github_repo}/actions/workflows/{github_workflow}/dispatches"

    data = {
        "ref": github_branch
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"GitHub Action triggered, status: {response.status_code}")
