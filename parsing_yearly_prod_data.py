"""
Pivot Year Columns
Creates separate PROD_2022, PROD_2023, etc. columns based on year suffix in type
"""

import pandas as pd
import re

# Configuration
input_file = "mcs1997_all_world_production_usgs.csv"
output_file = "mcs1997_all_world_production_usgs_cleaned.csv"

print(f"Pivoting year data from {input_file}...\n")

# Read the combined file
df = pd.read_csv(input_file)

print(f"Original shape: {df.shape}")
print(f"Columns: {list(df.columns)}\n")

# Extract year from type column
# Pattern: anything ending with _1990, _1995, _2022, _2023, _2022e, _2023e, etc.
df['year'] = df['type'].str.extract(r'_((?:19|20)\d{2}e?)$')

# Remove year suffix from type to get the base metric name
df['type_base'] = df['type'].str.replace(r'_(?:19|20)\d{2}e?$', '', regex=True)

print("Sample data with extracted year:")
print(df[['source', 'country', 'type', 'type_base', 'year', 'value', 'commodity', 'units']].head(10))
print()

# Create column name from year (e.g., 2022 -> PROD_2022, 2023e -> PROD_2023e)
df['year_column'] = 'PROD_' + df['year'].astype(str)

# Remove rows where year extraction failed (no year in type)
df = df[df['year'].notna()]

print(f"Sample year_column values:")
print(df[['type', 'year', 'units', 'year_column']].head(10))
print()

# Pivot the data
# Group by: source, country, commodity, type_base, units
# Pivot on: year_column
# Values: value
df_pivoted = df.pivot_table(
    index=['source', 'country', 'commodity', 'type_base', 'units'],
    columns='year_column',
    values='value',
    aggfunc='first'  # In case of duplicates, take first value
).reset_index()

# Rename type_base back to type
df_pivoted = df_pivoted.rename(columns={'type_base': 'type'})

# Flatten column names (remove multi-index from pivot)
df_pivoted.columns.name = None

print(f"Pivoted shape: {df_pivoted.shape}")
print(f"Columns: {list(df_pivoted.columns)[:10]}...")
print()

# Save
df_pivoted.to_csv(output_file, index=False)

print(f"✓ Saved pivoted file: {output_file}")
print(f"{'='*60}")

# Show preview
print("\nPreview of pivoted data:")
print(df_pivoted.head(10))

# Show column info
print("\nAll columns:")
for col in df_pivoted.columns:
    print(f"  {col}")
print(f"Pivoting year data from {input_file}...\n")
