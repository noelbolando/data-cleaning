"""
Diagnostic: Check Forward Fill Results
Shows which files still have empty cells in first row after forward-filling
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "data-cleaning/processed_data/world_production_forward_filled"

print(f"Checking files in {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

files_with_issues = []

for csv_file in csv_files:
    # Read CSV
    df = pd.read_csv(csv_file, header=None)
    
    # Get first row
    first_row = df.iloc[0]
    
    # Check for empty cells (skip first cell which should be empty)
    empty_cells = []
    for i in range(1, len(first_row)):
        cell = first_row.iloc[i]
        if pd.isna(cell) or str(cell).strip() == '':
            empty_cells.append(i)
    
    if empty_cells:
        files_with_issues.append(csv_file.name)
        print(f"❌ {csv_file.name}")
        print(f"   First row: {first_row.tolist()}")
        print(f"   Empty cells at positions: {empty_cells}")
        print()
    else:
        print(f"✓ {csv_file.name}")

print(f"\n{'='*60}")
print(f"Files checked: {len(csv_files)}")
print(f"Files with issues: {len(files_with_issues)}")
print(f"{'='*60}")

if files_with_issues:
    print("\nFiles with remaining empty cells:")
    for f in files_with_issues:
        print(f"  - {f}")
