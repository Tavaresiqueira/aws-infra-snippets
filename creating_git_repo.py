import requests
import subprocess
import os
import shutil

def create_github_repo(token: str, repo_name: str, description: str = "") -> str:
    """
    Creates a new GitHub repository.

    Parameters:
        token: The GitHub access token to authenticate the request.
        repo_name: The name of the repository to be created.
        description: The description of the repository (default: "").
    
    Returns:
        The clone URL of the newly created repository.
    
    Raises:
        Exception: If the repository creation fails.
    """
    url = 'https://api.github.com/user/repos'
    headers = {'Authorization': f'token {token}'}
    data = {'name': repo_name, 'description': description, 'private': False}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully.")
        return response.json()['clone_url']
    else:
        raise Exception(f"Failed to create repository: {response.content}")


def push_code_to_repo(clone_url: str, directory_path: str, main_py_path : str) -> None:
    """
    Pushes the code to a Git repository.

    Args:
        clone_url: The URL of the repository to clone.
        directory_path: The path of the local directory to initialize as a Git repository.

    Raises:
        Exception: If there is an error in pushing the code.

    Returns:
        None
    """
    try:
        # Create temporary directory for the repository
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        # Copy main.py to the directory
        shutil.copy(main_py_path, directory_path)

        # Initialize the local directory as a Git repository
        subprocess.run(["git", "init"], cwd=directory_path, check=True)

        # Create .gitignore file for Python
        with open(os.path.join(directory_path, '.gitignore'), 'w') as gitignore:
            gitignore.write("*.pyc\n__pycache__/\n.env\n")

        # Create MIT License file
        with open(os.path.join(directory_path, 'LICENSE'), 'w') as license_file:
            license_file.write("MIT License\n\nCopyright (c) [year] [fullname]\n\nPermission is hereby granted...")

        # Add remote origin
        subprocess.run(["git", "remote", "add", "origin", clone_url], cwd=directory_path, check=True)

        # Add all files
        subprocess.run(["git", "add", "."], cwd=directory_path, check=True)

        # Commit the files
        subprocess.run(["git", "commit", "-m", "Initial commit with .gitignore, LICENSE, and main.py"], cwd=directory_path, check=True)

        # Push to GitHub
        subprocess.run(["git", "push", "-u", "origin", "master"], cwd=directory_path, check=True)
        print("Code pushed to the repository successfully.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to push code: {e}")
    finally:
        # Clean up temporary directory
        shutil.rmtree(directory_path)

# Usage
token = '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'  # Replace with your GitHub token
repo_name = 'MyNewRepo'  # Replace with your desired repository name
description = 'This is a test repository'  # Optional
directory_path = '/path/to/your/code'  # Path to the local directory to upload
main_py_path = 'main.py'

try:
    clone_url = create_github_repo(token, repo_name, description)
    push_code_to_repo(clone_url, directory_path, main_py_path)
except Exception as e:
    print(e)
