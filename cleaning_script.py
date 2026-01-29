"""
Quick CSV Cleaner
Finds the years row (2022, 2023, etc.) and keeps one row before it plus everything after
"""

import pandas as pd
import re
from pathlib import Path

# Configuration
input_folder = "world_production"      # Folder with your CSV files
output_folder = "world_production_cleaned"  # Where to save cleaned files

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Cleaning CSV files from {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Read CSV
    df = pd.read_csv(csv_file, header=None)
    
    # Find the row with years (e.g., 2019, 2020, 2021, 2022, 2023)
    year_row = None
    for idx, row in df.iterrows():
        # Convert row to string to search for year patterns
        row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
        
        # Look for multiple years (at least 2 years in format 20XX)
        years = re.findall(r'\b20[0-9]{2}e?\b', row_str)
        
        if len(years) >= 2:
            year_row = idx
            break
    
    if year_row is not None:
        # Keep from (year_row - 1) to end
        # If year_row is 0, just start from year_row
        start_row = max(0, year_row - 1)
        
        cleaned_df = df.iloc[start_row:].reset_index(drop=True)
        
        # Remove empty columns
        cleaned_df = cleaned_df.dropna(axis=1, how='all')
        
        # Save
        output_file = Path(output_folder) / csv_file.name
        cleaned_df.to_csv(output_file, index=False, header=False)
        
        print(f"  ✓ Found years at row {year_row}, keeping from row {start_row}")
        print(f"  ✓ {df.shape} → {cleaned_df.shape}")
    else:
        print(f"  ⚠ Could not find years row")
    
print(f"\n{'='*60}")
print(f"Done! Cleaned {len(csv_files)} files")
print(f"Output: {output_folder}/")
print(f"{'='*60}")
