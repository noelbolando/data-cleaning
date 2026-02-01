"""
Extract Commodity Names and Units
Extracts commodity names from odd pages and units from even pages
Creates a mapping file with page_number, commodity_name, and units
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path

# Configuration
pdf_path = "raw_data/mcs2024.pdf"
start_page = 30  # First commodity page (ABRASIVES)
end_page = 205   # Last commodity page
output_file = "commodity_names_with_units.csv"

print(f"Extracting commodity names and units from pages {start_page} to {end_page}...\n")

# Store results
commodity_data = []

with pdfplumber.open(pdf_path) as pdf:
    # First pass: collect all units from even pages
    units_by_page = {}
    
    for page_num in range(start_page, end_page + 1):
        if page_num % 2 == 0:  # Even page
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            
            if not text:
                continue
            
            lines = text.split('\n')
            units = None
            
            # Look for pattern: "(Data in ... )" - try multiple patterns
            for line in lines[:15]:
                units = None
                
                # Try different patterns
                # Pattern 1: (Data in ...)
                match = re.search(r'\(Data in ([^)]+)\)', line, re.IGNORECASE)
                if match:
                    units = match.group(1).strip()
                
                # Pattern 2: Sometimes it's split across lines or has extra text
                # Try: "Data in" without parentheses
                if not units:
                    match = re.search(r'Data in (.+?)(?:\.|$)', line, re.IGNORECASE)
                    if match:
                        units = match.group(1).strip()
                
                if units:
                    # Clean up: remove anything after "unless" or comma
                    units = re.split(r'\bunless\b', units, flags=re.IGNORECASE)[0].strip()
                    units = units.split(',')[0].strip()
                    units = units.rstrip('.')
                    break
            
            if units:
                units_by_page[page_num] = units
                print(f"Page {page_num} (even): Units = '{units}'")
            else:
                print(f"Page {page_num} (even): ⚠ No units pattern found")
                print(f"  First 5 lines:")
                for i, line in enumerate(lines[:5]):
                    print(f"    {i}: {line[:80]}")
    
    # Second pass: collect commodity names from odd pages and match with units
    for page_num in range(start_page, end_page + 1):
        if page_num % 2 == 1:  # Odd page
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            
            if not text:
                print(f"Page {page_num}: Could not extract text")
                continue
            
            lines = text.split('\n')
            commodity_name = None
            
            # Look for a line that's mostly uppercase (commodity names)
            for line in lines[:10]:
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                
                # Check if line is mostly uppercase
                upper_count = sum(1 for c in line if c.isupper())
                letter_count = sum(1 for c in line if c.isalpha())
                
                if letter_count > 0 and upper_count / letter_count > 0.7:
                    # Skip common headers
                    if not any(skip in line for skip in ['U.S. Geological Survey', 'MINERAL COMMODITY', 'SUMMARIES']):
                        commodity_name = line
                        break
            
            if commodity_name:
                # Get units from previous even page OR next even page
                units = units_by_page.get(page_num - 1, '') or units_by_page.get(page_num + 1, '')
                
                print(f"Page {page_num} (odd): Commodity = {commodity_name}, Units = '{units}'")
                
                commodity_data.append({
                    'page_number': page_num,
                    'commodity_name': commodity_name,
                    'units': units
                })
            else:
                print(f"Page {page_num} (odd): Could not identify commodity name")

# Create DataFrame with all columns
df = pd.DataFrame(commodity_data)

# Keep all columns: page_number, commodity_name, units
df = df[['page_number', 'commodity_name', 'units']]

# Save to CSV
df.to_csv(output_file, index=False)

print(f"\n{'='*60}")
print(f"Extracted {len(commodity_data)} commodities with units")
print(f"Saved to: {output_file}")
print(f"{'='*60}")

# Show preview
if len(df) > 0:
    print("\nPreview:")
    print(df.head(20).to_string(index=False))
    
    # Show summary
    print(f"\nTotal commodities: {len(df)}")
    print(f"Commodities with units: {df['units'].astype(bool).sum()}")
    print(f"Commodities without units: {(~df['units'].astype(bool)).sum()}")
