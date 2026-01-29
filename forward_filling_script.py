"""
Backward Fill First Row (except reserves)
Fills empty cells with the next non-empty value (looking ahead)
Exception: Don't backward fill to reserves - use previous value instead
First cell (position 0) always stays empty
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "world_production_final"
output_folder = "world_production_forward_filled"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Filling first rows in {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Read CSV without headers
    df = pd.read_csv(csv_file, header=None)
    
    # Get first row
    first_row = df.iloc[0].copy()
    
    print(f"  Before: {first_row.tolist()}")
    
    # Build new row
    new_row = [first_row.iloc[0]]  # Keep position 0 as-is (empty)
    
    # Track last value for reserves case
    last_value = None
    
    for i in range(1, len(first_row)):
        cell = first_row.iloc[i]
        
        # If this position has a value, use it
        if pd.notna(cell) and str(cell).strip():
            current_value = str(cell).strip()
            new_row.append(current_value)
            last_value = current_value
        else:
            # Empty cell - need to find next non-empty value
            next_value = None
            for j in range(i + 1, len(first_row)):
                if pd.notna(first_row.iloc[j]) and str(first_row.iloc[j]).strip():
                    next_value = str(first_row.iloc[j]).strip()
                    break
            
            # Check if next value contains "reserve"
            if next_value and 'reserve' in next_value.lower():
                # Use previous value instead
                fill_value = last_value if last_value else ''
            elif next_value:
                # Use next value (backward fill)
                fill_value = next_value
            else:
                # No next value, use last value
                fill_value = last_value if last_value else ''
            
            new_row.append(fill_value)
    
    # Update first row
    df.iloc[0] = new_row
    
    print(f"  After:  {new_row}")
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df.to_csv(output_file, index=False, header=False)
    
    print(f"  ✓ Saved\n")

print(f"{'='*60}")
print(f"Done! Processed {len(csv_files)} files")
print(f"Output: {output_folder}/")
print(f"{'='*60}")
