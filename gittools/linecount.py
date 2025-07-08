import os
import sys
import csv
from github import Github
from datetime import datetime, timedelta
import subprocess
import tempfile
import io
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.env_utils import load_environment, get_required_env
from utils.git_utils import clone_repository

# Load environment variables from .env file
if not load_environment():
    sys.exit(1)

# Configuration
GITHUB_TOKEN = get_required_env("GITHUB_TOKEN")
GITHUB_USER = get_required_env("GITHUB_USER")
REPOS = [f"{GITHUB_USER}/AgentWorks", f"{GITHUB_USER}/aiserver", f"{GITHUB_USER}/ASTMApp", f"{GITHUB_USER}/HDFTools", f"{GITHUB_USER}/FlaskHDF"]
START_DATE = datetime(2024, 7, 7)  # One year ago from July 7, 2025
END_DATE = datetime(2025, 7, 7)

def get_total_lines_of_code(repo_name):
    """Clone the repo and count total lines of code using cloc."""
    print(f"  Cloning {repo_name}...")
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            # Clone the repository using our utility function
            repo_url = f"https://{GITHUB_TOKEN}@github.com/{repo_name}.git"
            if not clone_repository(repo_url, tmpdirname):
                print(f"  Failed to clone {repo_name}")
                return 0
            print(f"  Successfully cloned {repo_name}")
            
            # Run cloc with explicit languages
            print(f"  Counting lines in {repo_name} with cloc...")
            cloc_output = subprocess.run(
                ["cloc", tmpdirname, "--csv", "--quiet", "--include-lang=Python,JavaScript,Java,C,C++,C#,Go,TypeScript"],
                capture_output=True,
                text=True
            )
            print(f"  Raw cloc output:\n{cloc_output.stdout}")
            
            # Parse cloc CSV output
            total_lines = 0
            csv_reader = csv.reader(io.StringIO(cloc_output.stdout))
            for row in csv_reader:
                if row and row[0] == "SUM":
                    total_lines = int(row[-1])  # Last column is code lines
                    break
            print(f"  Total lines in {repo_name}: {total_lines}")
            
            # Fallback: Count lines manually if cloc returns 0
            if total_lines == 0:
                print(f"  cloc returned 0 lines; using fallback Python counter...")
                total_lines = fallback_line_count(tmpdirname)
                print(f"  Fallback count: {total_lines} lines")
            
            return total_lines
        except Exception as e:
            print(f"  Error processing {repo_name}: {e}")
            return 0

def fallback_line_count(directory):
    """Count non-blank, non-comment lines in all files as a fallback."""
    total_lines = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".py", ".js", ".java", ".c", ".cpp", ".cs", ".go", ".ts")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith(("#", "//", "/*", "*")):
                                total_lines += 1
                except:
                    continue
    return total_lines

def main():
    print("Starting GitHub lines of code analysis...")
    # Initialize GitHub client
    print("Connecting to GitHub API...")
    try:
        g = Github(GITHUB_TOKEN)
        print("Successfully connected to GitHub API")
    except Exception as e:
        print(f"Error connecting to GitHub API: {e}")
        return
    
    # Prepare CSV
    print("Creating github_loc_report.csv...")
    with open("github_loc_report.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Repository", "Date", "Lines Added Since Last Check", "Total Lines in Repository", "Total Lines by burhop"])
        
        # Process each repository
        for repo_name in REPOS:
            print(f"\nProcessing repository: {repo_name}")
            try:
                repo = g.get_repo(repo_name)
                total_lines = get_total_lines_of_code(repo_name)
                total_user_lines = 0
                
                # Fetch commits
                print(f"  Fetching commits for {repo.name}...")
                commits = repo.get_commits(since=START_DATE, until=END_DATE)
                commit_count = 0
                
                for commit in commits:
                    commit_date = commit.commit.author.date.strftime("%Y-%m-%d")
                    lines_added = commit.stats.additions
                    if commit.author and commit.author.login == GITHUB_USER:
                        total_user_lines += lines_added
                        commit_count += 1
                    
                    writer.writerow([
                        repo_name,
                        commit_date,
                        lines_added,
                        total_lines,  # Approximate: uses current repo state
                        total_user_lines
                    ])
                
                print(f"  Found {commit_count} commits by {GITHUB_USER} in {repo.name}")
                print(f"Completed processing {repo_name}")
            except Exception as e:
                print(f"Error processing {repo_name}: {e}")
                writer.writerow([repo_name, "", 0, 0, 0])
    
    print("\nAnalysis complete! Output written to github_loc_report.csv")

if __name__ == "__main__":
    main()