"""
Populate Commodity Column
Matches page number from filename to commodity_names.csv and fills commodity column
"""

import pandas as pd
import re
from pathlib import Path

# Configuration
input_folder = "world_production_renamed"
output_folder = "world_production_with_commodities"
commodity_lookup_file = "commodity_names.csv"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Populating commodity column in {input_folder}/...\n")

# Load commodity lookup table
commodity_df = pd.read_csv(commodity_lookup_file)
print(f"Loaded {len(commodity_df)} commodities from {commodity_lookup_file}\n")

# Create a dictionary for quick lookup: page_number -> commodity_name
commodity_map = dict(zip(commodity_df['page_number'], commodity_df['commodity_name']))

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Extract page number from filename (e.g., page_35_world_production.csv -> 35)
    match = re.search(r'page_(\d+)', csv_file.name)
    
    if not match:
        print(f"  ⚠ Could not extract page number from filename, skipping")
        continue
    
    page_num = int(match.group(1))
    
    # Look up commodity name
    commodity_name = commodity_map.get(page_num)
    
    if commodity_name is None:
        print(f"  ⚠ No commodity found for page {page_num}")
        commodity_name = ''
    else:
        print(f"  Page {page_num} → {commodity_name}")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    
    # Fill commodity column with the commodity name
    df['commodity'] = commodity_name
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df.to_csv(output_file, index=False)
    
    print(f"  ✓ Saved with commodity: {commodity_name}\n")

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
