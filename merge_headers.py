"""
Merge Rows 1 and 2
Combines first two rows by appending row 2 values to row 1 values with underscore
Example: "Fused aluminum oxidee" + "2022" → "Fused aluminum oxidee_2022"
First position stays empty
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "world_production_forward_filled"
output_folder = "world_production_merged_headers"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Merging header rows in {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Read CSV without headers
    df = pd.read_csv(csv_file, header=None)
    
    if len(df) < 2:
        print(f"  ⚠ File has less than 2 rows, skipping")
        continue
    
    # Get first two rows
    row1 = df.iloc[0]
    row2 = df.iloc[1]
    
    print(f"  Row 1: {row1.tolist()}")
    print(f"  Row 2: {row2.tolist()}")
    
    # Merge rows
    merged_row = []
    
    for i in range(len(row1)):
        # Keep first position empty
        if i == 0:
            merged_row.append(row1.iloc[i])
        else:
            # Get values from both rows
            val1 = row1.iloc[i] if pd.notna(row1.iloc[i]) else ''
            val2 = row2.iloc[i] if i < len(row2) and pd.notna(row2.iloc[i]) else ''
            
            # Convert to strings and strip whitespace
            val1 = str(val1).strip()
            val2 = str(val2).strip()
            
            # Combine with underscore
            if val1 and val2:
                merged_row.append(f"{val1}_{val2}")
            elif val1:
                merged_row.append(val1)
            elif val2:
                merged_row.append(val2)
            else:
                merged_row.append('')
    
    print(f"  Merged: {merged_row}")
    
    # Replace row 1 with merged row and drop row 2
    df.iloc[0] = merged_row
    df = df.drop(1).reset_index(drop=True)
    
    print(f"  New shape: {df.shape}")
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df.to_csv(output_file, index=False, header=False)
    
    print(f"  ✓ Saved\n")

print(f"{'='*60}")
print(f"Done! Processed {len(csv_files)} files")
print(f"Output: {output_folder}/")
print(f"{'='*60}")
