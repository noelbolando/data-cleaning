"""
Clean Data - Country, Type, and PROD Columns
1. Cleans 'country' column by:
   - Removing comma and everything after it
   - Removing trailing numbers
   - Removing text in parentheses
2. Cleans 'type' column by:
   - Removing comma and everything after it
   - Removing trailing numbers
   - Removing trailing 'e'
   - Removing trailing ')'
3. Converts all PROD_ columns from strings to numeric (int/float)
Handles common issues like commas, spaces, 'e' suffix, and non-numeric values
"""

import pandas as pd
import re

# Configuration
input_file = "mcs1997_all_world_production_usgs_cleaned.csv"
output_file = "combined_world_production_cleaned.csv"

print(f"Cleaning PROD_ columns in {input_file}...\n")

# Read the pivoted file
df = pd.read_csv(input_file)

print(f"Original shape: {df.shape}")
print(f"Columns: {list(df.columns)}\n")

# Step 1: Clean the 'country' column - remove comma and everything after it, remove trailing numbers, remove parentheses
print("Step 1: Cleaning 'country' column...")
print(f"  Original sample values:")
print(f"  {df['country'].head(10).tolist()}\n")

# Remove comma and everything after it
df['country'] = df['country'].astype(str).str.split(',').str[0].str.strip()

# Remove trailing numbers (e.g., "United States5" -> "United States")
df['country'] = df['country'].str.replace(r'\d+$', '', regex=True).str.strip()

# Remove anything in parentheses including the parentheses (handles both complete and orphaned parentheses)
# First remove complete parentheses: "World total (rounded)" -> "World total"
df['country'] = df['country'].str.replace(r'\s*\([^)]*\)', '', regex=True).str.strip()

# Remove orphaned opening parentheses and everything after: "World total (rounded" -> "World total"
df['country'] = df['country'].str.replace(r'\s*\(.*$', '', regex=True).str.strip()

# Remove orphaned closing parentheses: "World total)" -> "World total"
df['country'] = df['country'].str.replace(r'\s*\).*$', '', regex=True).str.strip()

print(f"  Cleaned sample values:")
print(f"  {df['country'].head(10).tolist()}\n")

# Step 2: Clean the 'type' column - remove comma and everything after it, remove trailing numbers, 'e', and ')'
print("Step 2: Cleaning 'type' column...")
print(f"  Original sample values:")
print(f"  {df['type'].head(10).tolist()}\n")

# Remove comma and everything after it
df['type'] = df['type'].astype(str).str.split(',').str[0].str.strip()

# Remove trailing numbers (e.g., "Mine production6" -> "Mine production")
df['type'] = df['type'].str.replace(r'\d+$', '', regex=True).str.strip()

# Remove trailing 'e' (e.g., "Mine productione" -> "Mine production")
df['type'] = df['type'].str.replace(r'e$', '', regex=True).str.strip()

# Remove trailing ')' (e.g., "gross weight)" -> "gross weight")
df['type'] = df['type'].str.replace(r'\)$', '', regex=True).str.strip()

print(f"  Cleaned sample values:")
print(f"  {df['type'].head(10).tolist()}\n")

# Step 3: Clean PROD_ columns
print("Step 3: Cleaning PROD_ columns...")

# Find all PROD_ columns
prod_columns = [col for col in df.columns if col.startswith('PROD_')]

print(f"Found {len(prod_columns)} PROD_ columns to clean")
print(f"PROD columns: {prod_columns[:5]}...\n")

# Clean and convert each PROD column
for col in prod_columns:
    print(f"Cleaning: {col}")
    
    # Show original data type
    print(f"  Original dtype: {df[col].dtype}")
    
    # Convert to string first to handle any mixed types
    df[col] = df[col].astype(str)
    
    # Clean the values:
    # - Remove 'e' or 'E' anywhere (estimated values like "e1000", "1000e", "1e000" -> "1000")
    # - Remove commas (e.g., "1,000" -> "1000")
    # - Remove spaces
    # - Replace common text values with NaN
    df[col] = df[col].str.replace('e', '', regex=False, case=False)  # Remove all 'e' or 'E'
    df[col] = df[col].str.replace('E', '', regex=False)  # Make sure capital E is also removed
    df[col] = df[col].str.replace(',', '', regex=False)
    df[col] = df[col].str.replace(' ', '', regex=False)
    df[col] = df[col].str.strip()
    
    # Replace common non-numeric values with empty string
    df[col] = df[col].replace({
        'nan': '',
        'NaN': '',
        'NA': '',
        'N/A': '',
        '--': '',
        'W': '',  # Withheld
        'XX': '',
        '': ''
    })
    
    # Convert to numeric (coerce errors to NaN)
    df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Show new data type and sample values
    print(f"  New dtype: {df[col].dtype}")
    print(f"  Non-null count: {df[col].notna().sum()} / {len(df)}")
    print(f"  Sample values: {df[col].dropna().head(3).tolist()}")
    print()

# Save cleaned file
df.to_csv(output_file, index=False)

print(f"{'='*60}")
print(f"✓ Saved cleaned file: {output_file}")
print(f"{'='*60}")

# Show summary
print("\nSummary:")
print(f"Total rows: {len(df):,}")
print(f"PROD columns cleaned: {len(prod_columns)}")

# Show preview
print("\nPreview of cleaned data:")
print(df.head(10))

# Show data types
print("\nData types of PROD columns:")
for col in prod_columns[:5]:
    print(f"  {col}: {df[col].dtype}")
