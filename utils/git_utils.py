"""
Git utilities for maintenance scripts.
Provides common git operations for repository management.
"""
import os
import subprocess
from pathlib import Path

def clone_repository(repo_url, target_dir=None, clean=False):
    """
    Clone a git repository.
    
    Args:
        repo_url (str): URL of the repository to clone
        target_dir (str, optional): Target directory name. If None, uses the repo name
        clean (bool): If True, removes the directory if it exists
        
    Returns:
        bool: True if successful, False otherwise
    """
    if target_dir is None:
        # Extract repo name from URL
        target_dir = repo_url.split('/')[-1]
        if target_dir.endswith('.git'):
            target_dir = target_dir[:-4]
    
    # Clean if requested
    if clean and os.path.exists(target_dir):
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["rmdir", "/S", "/Q", target_dir], check=True)
            else:  # Unix-like
                subprocess.run(["rm", "-rf", target_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error removing directory {target_dir}: {e}")
            return False
    
    # Clone the repository
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_url}: {e}")
        return False

def create_tag(tag_name, tag_message, repo_dir='.'):
    """
    Create a git tag in the specified repository.
    
    Args:
        tag_name (str): Name of the tag
        tag_message (str): Message for the tag
        repo_dir (str): Directory of the repository
        
    Returns:
        bool: True if successful, False otherwise
    """
    original_dir = os.getcwd()
    try:
        os.chdir(repo_dir)
        subprocess.run(["git", "tag", "-a", tag_name, "-m", tag_message], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating tag {tag_name} in {repo_dir}: {e}")
        return False
    finally:
        os.chdir(original_dir)

def push_tag(tag_name, repo_dir='.', remote='origin'):
    """
    Push a git tag to the remote repository.
    
    Args:
        tag_name (str): Name of the tag to push
        repo_dir (str): Directory of the repository
        remote (str): Name of the remote repository
        
    Returns:
        bool: True if successful, False otherwise
    """
    original_dir = os.getcwd()
    try:
        os.chdir(repo_dir)
        subprocess.run(["git", "push", remote, tag_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pushing tag {tag_name} to {remote} in {repo_dir}: {e}")
        return False
    finally:
        os.chdir(original_dir)

def get_current_branch(repo_dir='.'):
    """
    Get the current branch name of the repository.
    
    Args:
        repo_dir (str): Directory of the repository
        
    Returns:
        str: Name of the current branch or None if error
    """
    original_dir = os.getcwd()
    try:
        os.chdir(repo_dir)
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting current branch in {repo_dir}: {e}")
        return None
    finally:
        os.chdir(original_dir)
