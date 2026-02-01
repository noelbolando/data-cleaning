"""
Populate Commodity and Units Columns
Matches page number from filename to commodity_names_with_units.csv 
Fills commodity and units columns
"""

import pandas as pd
import re
from pathlib import Path

# Configuration
input_folder = "world_production_renamed"
output_folder = "world_production_with_commodities"
commodity_lookup_file = "commodity_names_with_units.csv"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Populating commodity and units columns in {input_folder}/...\n")

# Load commodity lookup table
commodity_df = pd.read_csv(commodity_lookup_file)
print(f"Loaded {len(commodity_df)} commodities from {commodity_lookup_file}\n")

# Show what columns we have
print(f"Lookup file columns: {list(commodity_df.columns)}\n")

# For backwards compatibility, check if we have page_number column
# If not, we need to create the mapping differently
if 'page_number' in commodity_df.columns:
    # Create dictionaries for quick lookup: page_number -> commodity_name/units
    commodity_map = dict(zip(commodity_df['page_number'], commodity_df['commodity_name']))
    units_map = dict(zip(commodity_df['page_number'], commodity_df['units']))
    use_page_mapping = True
else:
    # No page numbers, will need to match by filename or other method
    # Create mapping by commodity name
    use_page_mapping = False
    print("⚠ No page_number column found in lookup file")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    if use_page_mapping:
        # Extract page number from filename (e.g., page_35_world_production.csv -> 35)
        match = re.search(r'page_(\d+)', csv_file.name)
        
        if not match:
            print(f"  ⚠ Could not extract page number from filename, skipping")
            continue
        
        page_num = int(match.group(1))
        
        # Look up commodity name and units
        commodity_name = commodity_map.get(page_num, '')
        units = units_map.get(page_num, '')
        
        if not commodity_name:
            print(f"  ⚠ No commodity found for page {page_num}")
        
        print(f"  Page {page_num} → {commodity_name} ({units})")
    else:
        commodity_name = ''
        units = ''
        print(f"  ⚠ Skipping - no page mapping available")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    
    # Fill commodity and units columns
    df['commodity'] = commodity_name
    
    # Add units column if it doesn't exist
    if 'units' not in df.columns:
        df['units'] = units
    else:
        df['units'] = units
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df.to_csv(output_file, index=False)
    
    print(f"  ✓ Saved with commodity: {commodity_name}, units: {units}\n")

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
