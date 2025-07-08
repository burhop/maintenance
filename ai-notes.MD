# AI Notes for Maintenance Repository

## Repository Overview
This repository contains utility scripts for maintaining the company's codebase. It includes tools for git operations, environment management, and other maintenance tasks.

## Key Components

### Environment Management
- `.env` file: Contains sensitive information like GitHub tokens and usernames
- `.gitignore`: Configured to exclude the `.env` file from version control
- `utils/env_utils.py`: Utilities for loading and accessing environment variables

### Git Utilities
- `utils/git_utils.py`: Common git operations (clone, tag, push)
- `gittools/tag-release.py`: Script for tagging multiple repositories with the same release tag

## Project Structure
```
maintenance/
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore configuration
├── ai-notes.MD          # This file - context for AI assistants
├── requirements.txt     # Python dependencies
├── gittools/
│   └── tag-release.py   # Script for tagging multiple repositories
└── utils/
    ├── __init__.py      # Package initialization
    ├── env_utils.py     # Environment variable utilities
    └── git_utils.py     # Git operation utilities
```

## Environment Setup
1. Create a `.env` file in the root directory with:
   ```
   GITHUB_USER=your-github-username-or-org
   GITHUB_TOKEN=your-github-token
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Common Tasks

### Tagging Repositories
Run the tag-release script:
```
python gittools/tag-release.py
```
This will:
1. Load environment variables from `.env`
2. Prompt for a tag name
3. Clone each repository in the configured list
4. Create and push a tag with the specified name to each repository

### Adding New Scripts
When adding new scripts:
1. Place them in an appropriate subdirectory
2. Import utilities from the `utils` package
3. Use environment variables for sensitive information
4. Add any new dependencies to `requirements.txt`
5. Update this document with relevant information

## Best Practices
1. Never hardcode sensitive information (tokens, passwords)
2. Use the utility modules for common operations
3. Handle errors gracefully with appropriate messages
4. Document new scripts and utilities
5. Follow consistent coding style

## Important Notes for AI Assistants

### Utility Modules
- **CRITICAL**: The files in the `utils` directory are used by multiple scripts
- Do NOT modify utility files in ways that could break existing scripts
- When making changes to utilities, ensure backward compatibility
- If a breaking change is necessary, update all dependent scripts

### Cross-Platform Compatibility
- **IMPORTANT**: Users work on both Windows and Linux environments
- All scripts MUST be written in Python for cross-platform compatibility
- If a user requests a bash (.sh) or batch (.bat) script for local execution, suggest a Python alternative instead
- Use platform-agnostic paths with `os.path` or `pathlib.Path`
- Handle OS-specific commands appropriately (e.g., use conditional logic based on `os.name`)

### Creating New Scripts
- Always use the utility modules for common operations:
  - `env_utils.py` for environment variables and configuration
  - `git_utils.py` for git operations
- Follow the pattern established in existing scripts
- Add appropriate error handling and logging
- Update requirements.txt if new dependencies are needed
