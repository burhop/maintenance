#!/usr/bin/env python3
"""
Code Growth Analysis Script

This script analyzes code growth across multiple repositories by examining
commit history and counting lines of code for each programming language.
It produces a CSV file with detailed statistics for each commit.

Requires:
- cloc (either in PATH or as cloc.exe in the current directory)
- git

Configuration is read from .env file.
"""

# GitPython package provides the git module
import git
import os
import sys
import csv
import json
import subprocess
import tempfile
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent))
from utils.env_utils import load_environment, get_required_env, get_env_list
from utils.git_utils import clone_repository

# Load environment variables from .env file
if not load_environment():
    sys.exit(1)

# Get configuration from environment variables
GITHUB_USER = get_required_env("GITHUB_USER")
GITHUB_TOKEN = get_required_env("GITHUB_TOKEN")

# Get repositories from environment or use default list
default_repos = [f"{GITHUB_USER}/AgentWorks", f"{GITHUB_USER}/aiserver", 
                f"{GITHUB_USER}/ASTMApp", f"{GITHUB_USER}/HDFTools", 
                f"{GITHUB_USER}/FlaskHDF"]
REPOS = get_env_list("GITHUB_REPOS", default=default_repos)

# Output file format
OUTPUT_CSV_FORMAT = "code_growth-{}.csv"
COMBINED_CSV = "code_growth.csv"

# Initial date for all projects (zero lines of code)
INITIAL_DATE = "2024-11-01 00:00:00"

def process_repository(repo_name, temp_dir):
    """Process a single repository to collect code growth data."""
    print(f"\nProcessing repository: {repo_name}")
    
    # Prepare repo URL with token for authentication
    repo_url = f"https://{GITHUB_TOKEN}@github.com/{repo_name}.git"
    
    # Clone the repository
    repo_dir = os.path.join(temp_dir, repo_name.split('/')[-1])
    if not clone_repository(repo_url, repo_dir):
        print(f"Failed to clone {repo_name}, skipping...")
        return None, None
    
    # Open the repository
    try:
        repo = git.Repo(repo_dir)
        
        # Determine default branch (main or master)
        default_branch = "main"
        if "master" in repo.refs and "main" not in repo.refs:
            default_branch = "master"
            
        repo.git.checkout(default_branch)
        print(f"Using {default_branch} branch for {repo_name}")
        
        # Get commits from oldest to newest
        commits = list(repo.iter_commits(default_branch))[::-1]
        print(f"Found {len(commits)} commits in {repo_name}")
        
        # First pass to collect all languages
        language_set = set()
        for i, commit in enumerate(commits):
            if i % 10 == 0:  # Progress indicator every 10 commits
                print(f"Analyzing commit {i+1}/{len(commits)} in {repo_name}")
                
            repo.git.checkout(commit.hexsha)
            try:
                # Find cloc.exe in the current directory or use 'cloc' command
                cloc_path = "cloc.exe" if os.path.exists("cloc.exe") else "cloc"
                
                cloc_output = subprocess.check_output(
                    [cloc_path, "--json", "--quiet", repo_dir], 
                    stderr=subprocess.DEVNULL
                ).decode()
                
                cloc_data = json.loads(cloc_output)
                for lang in cloc_data:
                    if lang not in ["header", "SUM"]:
                        language_set.add(lang)
            except Exception as e:
                print(f"Error analyzing commit {commit.hexsha[:7]}: {e}")
                continue
        
        return commits, sorted(language_set)
    except Exception as e:
        print(f"Error processing repository {repo_name}: {e}")
        return None, None

def main():
    """Main function to process all repositories."""
    print(f"Processing repositories: {', '.join(REPOS)}")
    
    # Create a temporary directory for all repositories
    temp_dir = tempfile.mkdtemp()
    try:
        all_repo_data = {}
        all_languages = set()
        
        # Process each repository
        for repo_name in REPOS:
            commits, languages = process_repository(repo_name, temp_dir)
            
            if commits and languages:
                all_repo_data[repo_name] = {
                    "commits": commits,
                    "languages": languages
                }
                all_languages.update(languages)
        
        # Sort languages for consistent column order
        language_columns = sorted(all_languages)
        
        # Generate CSV with code growth data
        generate_csv(all_repo_data, language_columns)
        
        print(f"\nAnalysis complete! Results saved to {OUTPUT_CSV}")
    finally:
        # Clean up temp directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not clean up temporary directory: {e}")


def generate_csv(all_repo_data, language_columns):
    """Generate CSV file with code growth data for all repositories."""
    base_columns = ["repo_name", "commit_hash", "datetime", "author", "lines_of_code", "delta"]
    header = base_columns + language_columns
    
    # Create a combined CSV file for all repositories
    print(f"\nGenerating combined CSV file: {COMBINED_CSV}")
    combined_file = open(COMBINED_CSV, "w", newline="")
    combined_writer = csv.writer(combined_file)
    combined_writer.writerow(header)
    
    # Process each repository
    for repo_name, repo_data in all_repo_data.items():
        repo_short_name = repo_name.split("/")[-1]
        repo_csv = OUTPUT_CSV_FORMAT.format(repo_short_name)
        
        print(f"Generating CSV file for {repo_short_name}: {repo_csv}")
        with open(repo_csv, "w", newline="") as repo_file:
            repo_writer = csv.writer(repo_file)
            repo_writer.writerow(header)
            
            # Add initial data point with zero lines of code
            initial_row = [
                repo_short_name,
                "initial",
                INITIAL_DATE,
                "N/A",
                0,  # zero lines of code
                0   # zero delta
            ]
            
            # Add zero values for all languages
            for _ in language_columns:
                initial_row.append(0)
                
            # Write to both repo-specific and combined CSV
            repo_writer.writerow(initial_row)
            combined_writer.writerow(initial_row)
            commits = repo_data["commits"]
            
            # Create a temporary directory for this repository
            repo_temp_dir = tempfile.mkdtemp()
            try:
                # Clone the repository again for final analysis
                repo_url = f"https://{GITHUB_TOKEN}@github.com/{repo_name}.git"
                repo_dir = os.path.join(repo_temp_dir, repo_short_name)
                
                if not clone_repository(repo_url, repo_dir):
                    print(f"Failed to clone {repo_name} for final analysis, skipping...")
                    continue
                
                repo = git.Repo(repo_dir)
                
                # Determine default branch
                default_branch = "main"
                if "master" in repo.refs and "main" not in repo.refs:
                    default_branch = "master"
                
                # Track previous commit's line count for delta calculation
                prev_total_lines = 0
                
                # Process each commit
                for i, commit in enumerate(commits):
                    if i % 10 == 0:  # Progress indicator
                        print(f"Processing commit {i+1}/{len(commits)} in {repo_name}")
                    
                    try:
                        # Checkout the commit
                        repo.git.checkout(commit.hexsha)
                        
                        # Get commit metadata
                        commit_hash = commit.hexsha[:7]
                        commit_date = datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M:%S")
                        author = commit.author.name
                        
                        # Run cloc on this commit
                        cloc_path = "cloc.exe" if os.path.exists("cloc.exe") else "cloc"
                        cloc_output = subprocess.check_output(
                            [cloc_path, "--json", "--quiet", repo_dir],
                            stderr=subprocess.DEVNULL
                        ).decode()
                        
                        cloc_data = json.loads(cloc_output)
                        
                        # Extract language-specific line counts
                        lang_lines = {lang: 0 for lang in language_columns}
                        total_lines = 0
                        
                        for lang in cloc_data:
                            if lang not in ["header", "SUM"]:
                                if lang in lang_lines:
                                    lang_lines[lang] = cloc_data[lang]["code"]
                                    total_lines += cloc_data[lang]["code"]
                        
                        # Calculate delta from previous commit
                        delta = total_lines - prev_total_lines if i > 0 else total_lines
                        prev_total_lines = total_lines
                        
                        # Prepare row data
                        row_data = [
                            repo_short_name,
                            commit_hash,
                            commit_date,
                            author,
                            total_lines,
                            delta
                        ]
                        
                        # Add language-specific line counts
                        for lang in language_columns:
                            row_data.append(lang_lines[lang])
                        
                        # Write to both repo-specific and combined CSV files
                        with open(OUTPUT_CSV_FORMAT.format(repo_short_name), "a", newline="") as repo_file:
                            repo_writer = csv.writer(repo_file)
                            repo_writer.writerow(row_data)
                            
                        combined_writer.writerow(row_data)
                        
                    except Exception as e:
                        print(f"Error processing commit {commit.hexsha[:7]}: {e}")
                        continue
            finally:
                # Clean up repo temp directory
                try:
                    import shutil
                    shutil.rmtree(repo_temp_dir, ignore_errors=True)
                except Exception as e:
                    print(f"Warning: Could not clean up repository temporary directory: {e}")
    
    # Close the combined CSV file
    combined_file.close()
    
    print(f"\nCSV files generated successfully:")
    print(f"- Combined file: {COMBINED_CSV}")
    for repo_name in all_repo_data:
        repo_short_name = repo_name.split("/")[-1]
        print(f"- {repo_short_name}: {OUTPUT_CSV_FORMAT.format(repo_short_name)}")

if __name__ == "__main__":
    main()
