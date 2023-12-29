import requests

def create_github_repo(token, repo_name, description=""):
    """Create a new GitHub repository."""
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {token}'}
    data = {'name': repo_name, 'description': description, 'private': False}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully.")
        return response.json()['clone_url']
    else:
        raise Exception(f"Failed to create repository: {response.content}")
