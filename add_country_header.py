"""
Add 'country' to Position 0
Sets the first cell of the first row to 'country' in all files
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "world_production_merged_headers"
output_folder = "world_production_final_headers"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Adding 'country' header to files in {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Read CSV without headers
    df = pd.read_csv(csv_file, header=None)
    
    # Set position 0 of first row to 'country'
    df.iloc[0, 0] = 'country'
    
    print(f"  ✓ Set position 0 to 'country'")
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df.to_csv(output_file, index=False, header=False)
    
    print(f"  ✓ Saved to: {output_file}\n")

print(f"{'='*60}")
print(f"Done! Processed {len(csv_files)} files")
print(f"Output: {output_folder}/")
print(f"{'='*60}")

# Show preview of first file
if csv_files:
    first_file = Path(output_folder) / csv_files[0].name
    df_preview = pd.read_csv(first_file, header=None)
    print("\nPreview of first file (first row):")
    print(df_preview.iloc[0].tolist())
