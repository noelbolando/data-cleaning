"""
Combine All CSV Files
Appends all individual CSV files into one master file
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "world_production_with_commodities"
output_file = "mcs2024_all_world_production_usgs.csv"

print(f"Combining all CSV files from {input_folder}/...\n")

# Get all CSV files
csv_files = sorted(Path(input_folder).glob("*.csv"))

print(f"Found {len(csv_files)} files to combine\n")

# List to hold all dataframes
all_dfs = []

for csv_file in csv_files:
    print(f"Reading: {csv_file.name}")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    
    print(f"  Rows: {len(df)}, Columns: {list(df.columns)}")
    
    # Add to list
    all_dfs.append(df)

# Combine all dataframes
print(f"\n{'='*60}")
print("Combining all files...")
combined_df = pd.concat(all_dfs, ignore_index=True)

print(f"Combined shape: {combined_df.shape}")
print(f"Columns: {list(combined_df.columns)}")

# Save combined file
combined_df.to_csv(output_file, index=False)

print(f"\n✓ Saved combined file: {output_file}")
print(f"{'='*60}")

# Show summary
print("\nSummary:")
print(f"Total rows: {len(combined_df):,}")
print(f"Total files combined: {len(csv_files)}")
print(f"\nUnique commodities: {combined_df['commodity'].nunique()}")
print(f"Unique countries: {combined_df['country'].nunique()}")

# Show preview
print("\nPreview of combined data:")
print(combined_df.head(10))

print("\nTail of combined data:")
print(combined_df.tail(10))
