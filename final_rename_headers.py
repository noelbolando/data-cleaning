"""
Rename Column Header and Add Commodity and Units Columns
Renames 'metric' column to 'type' and adds empty 'commodity' and 'units' columns
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "world_production_long_format"
output_folder = "world_production_renamed"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Renaming 'metric' to 'type' and adding 'commodity' and 'units' columns in {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Read CSV with headers
    df = pd.read_csv(csv_file)
    
    # Rename column
    df = df.rename(columns={'metric': 'type'})
    
    # Add 'commodity' column (empty for now)
    df['commodity'] = ''
    
    # Add 'units' column (empty for now)
    df['units'] = ''
    
    print(f"  Columns: {list(df.columns)}")
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df.to_csv(output_file, index=False)
    
    print(f"  ✓ Saved\n")

print(f"{'='*60}")
print(f"Done! Processed {len(csv_files)} files")
print(f"Output: {output_folder}/")
print(f"{'='*60}")

# Show preview of first file
if csv_files:
    first_file = Path(output_folder) / csv_files[0].name
    df_preview = pd.read_csv(first_file)
    print("\nPreview of first file:")
    print(df_preview.head())
