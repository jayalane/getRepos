import requests
import os
import subprocess

def clone_or_update_repo(repo_url, target_dir):
    """Clones a repo if it doesn't exist, otherwise fetches/pulls updates."""
    if os.path.exists(target_dir):
        subprocess.run(["git", "-C", target_dir, "fetch", "origin"], check=True)
        subprocess.run(["git", "-C", target_dir, "pull"], check=True)
        print(f"Updated: {repo_url}")
    else:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        print(f"Cloned: {repo_url}")

# Read credentials
with open("secret.txt", "r") as f:
    token = f.read().strip()
with open("users.txt", "r") as f:
    users = [line.strip() for line in f if line.strip()]

headers = {"Authorization": f"{token}"}

# Iterate through users
for user in users:
    # Get list of repositories for the user
    repos_url = f"https://api.github.com/users/{user}/repos"
    response = requests.get(repos_url, headers=headers)
    response.raise_for_status()
    repos = response.json()

    # Iterate through repositories
    for repo in repos:
        clone_or_update_repo(repo["clone_url"], repo["name"])
