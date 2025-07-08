#!/usr/bin/env python3
"""
Code Growth Total Script

This script combines data from all code_growth CSV files in the directory
to create a summary CSV with total lines of code by date across all projects.

Output format:
- date, total_loc, language1_loc, language2_loc, ...

Initial date of November 1, 2024 is used as the starting point with zero lines of code.
"""

import os
import csv
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent))
from utils.env_utils import load_environment

# Load environment variables from .env file
if not load_environment():
    sys.exit(1)

# Output file
OUTPUT_CSV = "code_growth_total.csv"
INITIAL_DATE = "2024-11-01 00:00:00"

def main():
    """Main function to combine CSV data and generate a total growth CSV."""
    print(f"Generating total code growth CSV: {OUTPUT_CSV}")
    
    # Find all code_growth CSV files in the directory
    csv_files = [f for f in os.listdir() if f.startswith("code_growth-") and f.endswith(".csv")]
    
    if not csv_files:
        print("No code_growth CSV files found in the directory.")
        return
    
    print(f"Found {len(csv_files)} code growth CSV files to process.")
    
    # Dictionary to store combined data by date
    # Format: {date: {total_loc: X, language1: Y, language2: Z, ...}}
    combined_data = defaultdict(lambda: defaultdict(int))
    all_languages = set()
    
    # Process each CSV file
    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        
        with open(csv_file, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            
            # Extract language columns (after the first 6 columns)
            languages = header[6:]
            all_languages.update(languages)
            
            # Process each row in the CSV
            for row in reader:
                if len(row) < 6:
                    continue  # Skip invalid rows
                
                repo_name = row[0]
                commit_hash = row[1]
                date = row[2]
                author = row[3]
                lines_of_code = int(row[4]) if row[4] else 0
                delta = int(row[5]) if row[5] else 0
                
                # Add total lines of code for this date
                combined_data[date]["total_loc"] += lines_of_code
                
                # Add language-specific lines of code
                for i, lang in enumerate(languages):
                    if i + 6 < len(row) and row[i + 6]:
                        lang_loc = int(row[i + 6])
                        combined_data[date][lang] += lang_loc
    
    # Sort languages for consistent column order
    sorted_languages = sorted(all_languages)
    
    # Create the output CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header row
        header = ["date", "total_loc"] + sorted_languages
        writer.writerow(header)
        
        # Add initial row with zero values
        initial_row = [INITIAL_DATE, 0] + [0] * len(sorted_languages)
        writer.writerow(initial_row)
        
        # Sort dates and write data rows (excluding the initial date if it exists in the data)
        sorted_dates = sorted([d for d in combined_data.keys() if d != INITIAL_DATE])
        
        for date in sorted_dates:
            data = combined_data[date]
            row = [date, data["total_loc"]]
            
            # Add language-specific lines of code
            for lang in sorted_languages:
                row.append(data[lang])
            
            writer.writerow(row)
    
    print(f"\nTotal code growth CSV generated successfully: {OUTPUT_CSV}")
    print(f"Summary includes data from {len(csv_files)} repositories and {len(sorted_languages)} languages.")

if __name__ == "__main__":
    main()
