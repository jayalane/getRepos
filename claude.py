import os
import requests
import git
from pathlib import Path

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

def get_authenticated_user(token):
    """Get the username of the authenticated user."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code == 200:
        return response.json().get('login')
    return None

def get_org_repos(org, token):
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {
        "Authorization": f"token {token}",
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
            print(f"Error fetching repos for org {org}: {response.status_code}/{response.text}")
            break
    return repos

def get_user_repos(username, token):
    auth_user = get_authenticated_user(token)
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Use /user/repos for authenticated user (includes private repos)
    # Use /users/{username}/repos for other users (public only)
    if auth_user and auth_user.lower() == username.lower():
        url = "https://api.github.com/user/repos"
        params = "affiliation=owner&"
    else:
        url = f"https://api.github.com/users/{username}/repos"
        params = ""

    repos = []
    page = 1
    while True:
        response = requests.get(f"{url}?{params}page={page}&per_page=100", headers=headers)
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
    Path(base_path).mkdir(parents=True, exist_ok=True)
    repo_path = Path(base_path) / repo['name']
    # Create authenticated URL for private repo access
    clone_url = repo['clone_url'].replace('https://', f'https://{token}@')

    if repo_path.exists():
        print(f"Updating existing repo: {repo['name']}")
        try:
            git_repo = git.Repo(repo_path)
            origin = git_repo.remotes.origin
            # Update remote URL with token for private repos
            origin.set_url(clone_url)
            origin.fetch()
            origin.pull()
        except git.GitCommandError as e:
            print(f"Error updating repo {repo['name']}: {e}")
    else:
        print(f"Cloning new repo: {repo['name']}")
        try:
            git.Repo.clone_from(clone_url, repo_path)
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

    orgs_file = Path('orgs.txt')
    if orgs_file.exists():
        orgs = read_file('orgs.txt').split('\n')
        for org in orgs:
            if not org:
                continue
            print(f"Syncing repositories for org: {org}")
            repos = get_org_repos(org, token)
            for repo in repos:
                sync_repo(repo, token, base_path / org)

if __name__ == "__main__":
    main()
