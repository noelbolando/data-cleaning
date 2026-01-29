"""
Add 'source' Column
Adds 'source' column at the very beginning (position 0) of each file
Header row gets 'source', all other rows get 'mcs2024'
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "world_production_final_headers"
output_folder = "world_production_with_source"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Adding 'source' column to files in {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Read CSV without headers
    df = pd.read_csv(csv_file, header=None)
    
    print(f"  Original shape: {df.shape}")
    
    # Create source column
    # First row gets 'source', all other rows get 'mcs2024'
    source_column = ['source'] + ['mcs2024'] * (len(df) - 1)
    
    # Insert at position 0 (very beginning)
    df.insert(0, 'source_col', source_column)
    
    print(f"  New shape: {df.shape}")
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df.to_csv(output_file, index=False, header=False)
    
    print(f"  ✓ Saved\n")

print(f"{'='*60}")
print(f"Done! Processed {len(csv_files)} files")
print(f"Output: {output_folder}/")
print(f"{'='*60}")

# Show preview of first file
if csv_files:
    first_file = Path(output_folder) / csv_files[0].name
    df_preview = pd.read_csv(first_file, header=None)
    print("\nPreview of first file:")
    print(df_preview.head())
    