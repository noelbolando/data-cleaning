"""
Odd Pages Cleaner
Cleans only odd-numbered pages (35, 37, 39, etc.) from world_production_cleaned folder
Finds rows with pattern: ,2022,2023e, (comma before years)
Keeps one row before that pattern through "World total" row
"""

import pandas as pd
import re
from pathlib import Path

# Configuration
input_folder = "world_production_cleaned"      # Already cleaned files
output_folder = "world_production_final"       # Final cleaned files

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Cleaning odd-numbered pages from {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    # Extract page number from filename (e.g., page_35_world_production.csv)
    match = re.search(r'page_(\d+)', csv_file.name)
    
    if not match:
        print(f"Skipping {csv_file.name} - couldn't extract page number")
        continue
    
    page_num = int(match.group(1))
    
    # Only process odd-numbered pages
    if page_num % 2 == 0:
        print(f"Skipping {csv_file.name} - page {page_num} is even")
        continue
    
    print(f"Processing: {csv_file.name} (page {page_num})")
    
    # Read CSV
    df = pd.read_csv(csv_file, header=None)
    
    # Step 1: Find the row with pattern: ,2022,2023e, (comma before years)
    years_row = None
    for idx, row in df.iterrows():
        # Check if first cell is empty/NA and second cell looks like a year
        if len(row) >= 2:
            first_cell = row.iloc[0]
            second_cell = row.iloc[1]
            
            # Check if first cell is empty and second looks like a year
            if (pd.isna(first_cell) or str(first_cell).strip() == ''):
                if pd.notna(second_cell):
                    # Check if it's a year pattern (20XX with optional 'e')
                    if re.match(r'^20[0-9]{2}e?$', str(second_cell).strip()):
                        years_row = idx
                        break
    
    if years_row is None:
        print(f"  ⚠ Could not find years row with comma pattern")
        continue
    
    # Step 2: Find "World total" row (case insensitive)
    world_total_row = None
    for idx, row in df.iterrows():
        if idx < years_row:  # Only look after the years row
            continue
        
        # Check each cell for "world total"
        for cell in row:
            if pd.notna(cell) and isinstance(cell, str):
                if 'world total' in cell.lower():
                    world_total_row = idx
                    break
        if world_total_row is not None:
            break
    
    if world_total_row is None:
        print(f"  ⚠ Could not find 'World total' row")
        continue
    
    # Step 3: Keep from (years_row - 1) to world_total_row (inclusive)
    start_row = max(0, years_row - 1)
    end_row = world_total_row + 1  # +1 because iloc is exclusive at end
    
    cleaned_df = df.iloc[start_row:end_row].reset_index(drop=True)
    
    # Remove empty columns
    cleaned_df = cleaned_df.dropna(axis=1, how='all')
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    cleaned_df.to_csv(output_file, index=False, header=False)
    
    print(f"  ✓ Years row: {years_row}, World total row: {world_total_row}")
    print(f"  ✓ Keeping rows {start_row} to {world_total_row}")
    print(f"  ✓ {df.shape} → {cleaned_df.shape}")

print(f"\n{'='*60}")
print(f"Done! Processed odd-numbered pages")
print(f"Output: {output_folder}/")
print(f"{'='*60}")
