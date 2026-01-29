"""
Unpivot Tables (Wide to Long)
Transforms tables from wide format to long format
Keeps 'source' and 'country' columns, unpivots everything else
"""

import pandas as pd
from pathlib import Path

# Configuration
input_folder = "world_production_with_source"
output_folder = "world_production_long_format"

# Create output folder
Path(output_folder).mkdir(exist_ok=True)

print(f"Unpivoting tables in {input_folder}/...\n")

# Process each CSV file
csv_files = list(Path(input_folder).glob("*.csv"))

for csv_file in csv_files:
    print(f"Processing: {csv_file.name}")
    
    # Read CSV - first row is headers
    df = pd.read_csv(csv_file, header=0)
    
    print(f"  Original shape: {df.shape}")
    print(f"  Columns: {list(df.columns)[:5]}...")
    
    # Get the column names
    # First two columns are 'source' and 'country' (id_vars)
    # Everything else gets unpivoted (value_vars)
    id_columns = ['source', 'country']
    value_columns = [col for col in df.columns if col not in id_columns]
    
    # Melt/unpivot the dataframe
    df_long = pd.melt(
        df,
        id_vars=id_columns,
        value_vars=value_columns,
        var_name='metric',
        value_name='value'
    )
    
    print(f"  New shape: {df_long.shape}")
    
    # Save
    output_file = Path(output_folder) / csv_file.name
    df_long.to_csv(output_file, index=False)
    
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
    print(df_preview.head(10))
