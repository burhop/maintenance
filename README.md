# Maintenance Tools

## Overview
This repository contains a collection of utility scripts for maintaining the company's codebase. The tools are designed to automate common maintenance tasks such as tagging releases across multiple repositories, counting lines of code, and other git operations.

## Key Features
- **Cross-platform compatibility**: All scripts work on both Windows and Linux
- **Secure credential management**: Uses `.env` file for sensitive information
- **Modular design**: Common functionality is extracted into reusable utility modules
- **Consistent error handling**: Robust error handling across all scripts

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git

### Installation
1. Clone this repository:
   ```
   git clone https://github.com/burhop/maintenance.git
   cd maintenance
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your credentials:
   ```
   GITHUB_USER=your-github-username-or-org
   GITHUB_TOKEN=your-github-token
   ```

## Available Tools

### Git Tools
- **tag-release.py**: Tags multiple repositories with the same release tag
  ```
  python gittools/tag-release.py
  ```

- **linecount.py**: Analyzes repositories for line count statistics
  ```
  python gittools/linecount.py
  ```

## Development

### Project Structure
```
maintenance/
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore configuration
├── README.md            # This file
├── ai-notes.MD          # Notes for AI assistants
├── requirements.txt     # Python dependencies
├── gittools/            # Git-related scripts
└── utils/               # Shared utility modules
```

### Working with AI Assistants
This project includes an `ai-notes.MD` file that provides important context for AI assistants. When using AI tools to help develop or modify scripts in this repository, point them to this file for better context and guidance.

```
Please review the ai-notes.MD file for important information about this project's structure and best practices.
```

### Adding New Scripts
When adding new scripts:
1. Place them in an appropriate subdirectory
2. Import utilities from the `utils` package
3. Use environment variables for sensitive information
4. Add any new dependencies to `requirements.txt`
5. Follow the cross-platform compatibility guidelines

## License
Internal company use only.
