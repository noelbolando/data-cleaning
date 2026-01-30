"""
Commodity Name Extractor
Extracts commodity names from the top of each USGS page and saves to CSV
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path

# Configuration
pdf_path = "raw_data/mcs1997.pdf"
start_page = 20  # First commodity page to extract
end_page = 195    # Last commodity page to extract
output_file = "commodity_names.csv"

print(f"Extracting commodity names from pages {start_page} to {end_page}...\n")

# Store results
commodity_data = []

with pdfplumber.open(pdf_path) as pdf:
    for page_num in range(start_page, end_page + 1):
        # Get page (pdfplumber is 0-indexed, so subtract 1)
        page = pdf.pages[page_num - 1]
        
        # Extract text
        text = page.extract_text()
        
        if text:
            # Split into lines
            lines = text.split('\n')
            
            # Look for a line that's all caps or mostly caps (commodity names)
            commodity_name = None
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is mostly uppercase and not too long
                # Commodity names are usually short and in ALL CAPS
                if len(line) > 3 and len(line) < 100:
                    # Count uppercase letters
                    upper_count = sum(1 for c in line if c.isupper())
                    letter_count = sum(1 for c in line if c.isalpha())
                    
                    # If mostly uppercase (and not just a single word header)
                    if letter_count > 0 and upper_count / letter_count > 0.7:
                        # Skip common headers that aren't commodity names
                        if not any(skip in line for skip in ['U.S. Geological Survey', 'MINERAL COMMODITY', 'SUMMARIES']):
                            commodity_name = line
                            break
            
            if commodity_name:
                commodity_data.append({
                    'page_number': page_num,
                    'commodity_name': commodity_name
                })
                
                print(f"Page {page_num}: {commodity_name}")
            else:
                print(f"Page {page_num}: Could not identify commodity name")
                # Debug: show first few lines
                print(f"  First lines: {lines[:3]}")
        else:
            print(f"Page {page_num}: Could not extract text")

# Create DataFrame
df = pd.DataFrame(commodity_data)

# Save to CSV
df.to_csv(output_file, index=False)

print(f"\n{'='*60}")
print(f"Extracted {len(commodity_data)} commodity names")
print(f"Saved to: {output_file}")
print(f"{'='*60}")

# Show preview
if len(df) > 0:
    print("\nPreview:")
    print(df.head(20))
