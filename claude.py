import os
import requests
import git
from pathlib import Path

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

def get_user_repos(username, token):
    url = f"https://api.github.com/users/{username}/repos"
    print("Token is", token)
    headers = {
        "Authorization": f"{token}",
        "Accept": "application/vnd.github.v3+json"
    }
    repos = []
    page = 1
    while True:
        response = requests.get(f"{url}?page={page}&per_page=100", headers=headers)
        if response.status_code == 200:
            page_repos = response.json()
            if not page_repos:
                break
            repos.extend(page_repos)
            page += 1
        else:
            print(f"Error fetching repos for {username}: {response.status_code}/{response.text}")
            break
    return repos

def sync_repo(repo, token, base_path):
    repo_path = Path(base_path) / repo['name']
    if repo_path.exists():
        print(f"Updating existing repo: {repo['name']}")
        try:
            git_repo = git.Repo(repo_path)
            origin = git_repo.remotes.origin
            origin.fetch()
            origin.pull()
        except git.GitCommandError as e:
            print(f"Error updating repo {repo['name']}: {e}")
    else:
        print(f"Cloning new repo: {repo['name']}")
        try:
            git.Repo.clone_from(repo['clone_url'], repo_path, env={'GIT_ASKPASS': 'echo', 'GIT_USERNAME': 'token', 'GIT_PASSWORD': token})
        except git.GitCommandError as e:
            print(f"Error cloning repo {repo['name']}: {e}")

def main():
    token = read_file('secret.txt')
    usernames = read_file('users.txt').split('\n')
    base_path = Path('github_repos')
    base_path.mkdir(exist_ok=True)

    for username in usernames:
        print(f"Syncing repositories for user: {username}")
        repos = get_user_repos(username, token)
        for repo in repos:
            sync_repo(repo, token, base_path / username)

if __name__ == "__main__":
    main()
