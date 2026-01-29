"""
Main Pipeline - USGS World Production Data Extraction and Cleaning
Runs all scripts in the correct order to process PDF to final cleaned CSV
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print("\n" + "="*80)
    print(f"STEP: {description}")
    print("="*80)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("WARNINGS:", result.stderr)
        print(f"✓ Completed: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ ERROR in {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run the complete pipeline"""
    
    print("="*80)
    print("USGS WORLD PRODUCTION DATA PIPELINE")
    print("="*80)
    print("\nThis pipeline will:")
    print("1. Extract tables from PDF")
    print("2. Clean and standardize the data")
    print("3. Extract commodity names")
    print("4. Combine all files")
    print("5. Pivot into final format")
    print("\nStarting pipeline...\n")
    
    # Define pipeline steps
    steps = [
        # Step 1: Extract world production tables from PDF
        ("extract_world_prod.py", "Extract world production tables from PDF"),
        
        # Step 2: Clean tables - remove text before data
        ("cleaning_script.py", "Clean tables - remove paragraphs before data"),
        
        # Step 3: Further clean odd-numbered pages
        ("cleaning_odd_pages.py", "Clean odd-numbered pages - remove extra rows"),
        
        # Step 4: Forward-fill/backward-fill headers
        ("forward_filling_script.py", "Fill empty cells in headers"),
        
        # Step 5: Merge header rows
        ("merge_headers.py", "Merge header rows 1 and 2"),
        
        # Step 6: Add 'country' to position 0
        ("add_country_header.py", "Add 'country' header"),
        
        # Step 7: Add source column with mcs2024
        ("add_source_column.py", "Add 'source' column with mcs2024"),
        
        # Step 8: Unpivot to long format
        ("unpivot_tables.py", "Unpivot tables to long format"),
        
        # Step 9: Rename metric to type and add commodity column
        ("final_rename_headers.py", "Rename 'metric' to 'type' and add 'commodity' column"),
        
        # Step 10: Extract commodity names from PDF
        ("extract_commodity_names.py", "Extract commodity names from PDF pages"),
        
        # Step 11: Populate commodity column
        ("add_commodities.py", "Populate commodity column using lookup"),
        
        # Step 12: Combine all files
        ("append_append_append_all.py", "Combine all CSV files into one"),
        
        # Step 13: Pivot years into columns
        ("parsing_yearly_prod_data.py", "Pivot year data into separate columns"),
    ]
    
    # Run each step
    failed_steps = []
    
    for script, description in steps:
        success = run_script(script, description)
        if not success:
            failed_steps.append((script, description))
            print(f"\n⚠ WARNING: {script} failed. Continuing with remaining steps...")
    
    # Final summary
    print("\n" + "="*80)
    print("PIPELINE COMPLETE")
    print("="*80)
    
    if not failed_steps:
        print("\n✓ All steps completed successfully!")
        print("\nFinal output file: combined_world_production_pivoted.csv")
    else:
        print(f"\n⚠ {len(failed_steps)} step(s) failed:")
        for script, description in failed_steps:
            print(f"  - {description} ({script})")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
