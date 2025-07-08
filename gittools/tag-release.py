import os
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.env_utils import load_environment, get_required_env
from utils.git_utils import clone_repository, create_tag, push_tag

# Load environment variables from .env file
if not load_environment():
    sys.exit(1)

# Config
GITHUB_USER = get_required_env("GITHUB_USER")
GITHUB_TOKEN = get_required_env("GITHUB_TOKEN")

# Get repositories from environment or use default list
from utils.env_utils import get_env_list
default_repos = ["AgentWorks", "FlaskHDF", "ASTMApp", "aiserver", "HDFTools"]
REPOS = get_env_list("GITHUB_REPOS", default=default_repos)

print(f"Repositories to tag: {', '.join(REPOS)}")
TAG_NAME = input("Enter tag name: ")
TAG_MESSAGE = f"Tagging release {TAG_NAME}"

for repo in REPOS:
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{repo}.git"
    print(f"\nProcessing repo: {repo}")
    
    # Clone the repo
    if not clone_repository(repo_url, repo, clean=True):
        print(f"Failed to clone {repo}, skipping...")
        continue
    
    # Tag and push
    if not create_tag(TAG_NAME, TAG_MESSAGE, repo):
        print(f"Failed to create tag for {repo}, skipping push...")
        continue
        
    if not push_tag(TAG_NAME, repo):
        print(f"Failed to push tag for {repo}")
        continue
        
    print(f"Successfully tagged and pushed {repo} with {TAG_NAME}")

print("\nAll repositories have been tagged.")
