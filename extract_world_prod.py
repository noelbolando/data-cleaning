"""
Simple World Production Extractor
Quick script to extract ONLY world production tables (no text) from USGS PDF
"""

import camelot
import pandas as pd
from pathlib import Path

# Configuration
pdf_path = "data/mcs2024.pdf"
start_page = 34  # First commodity page to extract
end_page = 209    # Last commodity page to extract
output_dir = "world_production"

# Create output directory
Path(output_dir).mkdir(exist_ok=True)

print(f"Extracting world production tables from pages {start_page} to {end_page}...\n")

# Extract tables
all_results = []

for page_num in range(start_page, end_page + 1):
    print(f"Processing page {page_num}...")
    
    try:
        # Extract all tables from page using stream mode (best for USGS)
        # Camelot only extracts tables, not paragraphs!
        tables = camelot.read_pdf(pdf_path, pages=str(page_num), flavor='stream')
        
        if tables:
            # Get the largest table (typically the world production table)
            largest_table = max(tables, key=lambda t: t.df.shape[0] * t.df.shape[1])
            df = largest_table.df
            
            # Clean the dataframe - remove completely empty rows
            df = df.replace('', pd.NA)  # Replace empty strings with NA
            df = df.dropna(how='all')   # Drop rows that are all NA
            df = df.reset_index(drop=True)
            
            # Also remove rows where all cells are just whitespace
            df = df[~df.apply(lambda row: all(str(cell).strip() == '' for cell in row), axis=1)]
            df = df.reset_index(drop=True)
            
            print(f"  ✓ Found table: {df.shape} (accuracy: {largest_table.accuracy:.1f}%)")
            
            # Save to CSV
            filename = f"{output_dir}/page_{page_num}_world_production.csv"
            df.to_csv(filename, index=False, header=False)
            
            all_results.append({
                'page': page_num,
                'filename': filename,
                'shape': df.shape,
                'dataframe': df
            })
        else:
            print(f"  ✗ No tables found")
    
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n{'='*80}")
print(f"Extracted {len(all_results)} world production tables")
print(f"Saved to: {output_dir}/")
print(f"{'='*80}")

# Also save all to one Excel file
if all_results:
    print(f"\nCreating combined Excel file...")
    
    with pd.ExcelWriter(f"{output_dir}/all_world_production.xlsx", engine='openpyxl') as writer:
        for i, result in enumerate(all_results):
            sheet_name = f"Page_{result['page']}"
            result['dataframe'].to_excel(writer, sheet_name=sheet_name, index=False, header=False)
    
    print(f"✓ Saved combined file: {output_dir}/all_world_production.xlsx")

# Show preview of first table
if all_results:
    print(f"\n{'='*80}")
    print(f"Preview of first table (Page {all_results[0]['page']}):")
    print(f"{'='*80}")
    print(all_results[0]['dataframe'].head(10))

