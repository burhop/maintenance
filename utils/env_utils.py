"""
Environment utilities for maintenance scripts.
Handles loading environment variables from .env file.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """
    Load environment variables from .env file in the project root.
    Returns True if successful, False otherwise.
    """
    # Find the project root (where .env should be located)
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    project_root = current_dir.parent
    
    # Load environment variables from .env file
    env_path = project_root / '.env'
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        print("Please create a .env file with required environment variables.")
        return False
    
    load_dotenv(dotenv_path=env_path)
    return True

def get_required_env(var_name):
    """
    Get a required environment variable or exit with an error message.
    
    Args:
        var_name (str): Name of the environment variable
        
    Returns:
        str: Value of the environment variable
    """
    value = os.environ.get(var_name)
    if not value:
        print(f"Error: Required environment variable '{var_name}' not set.")
        print(f"Please add {var_name} to your .env file.")
        sys.exit(1)
    return value

def get_env_list(var_name, default=None, separator=','):
    """
    Get a list from a comma-separated environment variable.
    
    Args:
        var_name (str): Name of the environment variable
        default (list, optional): Default value if the variable is not set
        separator (str, optional): Separator character, default is comma
        
    Returns:
        list: List parsed from the environment variable or default
    """
    value = os.environ.get(var_name)
    if not value:
        return default if default is not None else []
    
    # Split by separator and strip whitespace from each item
    return [item.strip() for item in value.split(separator) if item.strip()]
