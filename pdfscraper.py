"""
Camelot PDF Table Extractor
Extract tables from PDFs and convert to pandas DataFrames
"""

# Import libraries
import camelot
import pandas as pd
from pathlib import Path
import re


class CamelotTableExtractor:
    """
    Extract tables from PDFs using Camelot
    
    Camelot has two modes:
    - 'lattice': For tables with clear borders/lines (more accurate)
    - 'stream': For tables without borders (more flexible)
    """
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
    
    def extract_tables_from_page(self, page_num, flavor='lattice', **kwargs):
        """
        Extract tables from a specific page
        
        Args:
            page_num: Page number (1-indexed in Camelot!)
            flavor: 'lattice' or 'stream'
            **kwargs: Additional Camelot settings
            
        Returns:
            List of pandas DataFrames
        """
        try:
            tables = camelot.read_pdf(
                self.pdf_path,
                pages=str(page_num),
                flavor=flavor,
                **kwargs
            )
            
            print(f"\nPage {page_num}: Found {len(tables)} table(s) using {flavor} mode")
            
            dfs = []
            for i, table in enumerate(tables):
                df = table.df
                print(f"  Table {i+1}: {df.shape} (accuracy: {table.accuracy:.1f}%)")
                dfs.append(df)
            
            return dfs
            
        except Exception as e:
            print(f"Error extracting from page {page_num}: {e}")
            return []
    
    def extract_tables_from_pages(self, pages, flavor='lattice', **kwargs):
        """
        Extract tables from multiple pages
        
        Args:
            pages: Page range as string (e.g., '1-10' or '1,3,5-7')
            flavor: 'lattice' or 'stream'
            **kwargs: Additional Camelot settings
            
        Returns:
            Dictionary with page numbers as keys and list of DataFrames as values
        """
        try:
            tables = camelot.read_pdf(
                self.pdf_path,
                pages=pages,
                flavor=flavor,
                **kwargs
            )
            
            print(f"\nExtracted {len(tables)} total table(s) from pages {pages} using {flavor} mode")
            
            # Organize by page
            results = {}
            for table in tables:
                page_num = table.page
                if page_num not in results:
                    results[page_num] = []
                
                df = table.df
                results[page_num].append({
                    'dataframe': df,
                    'accuracy': table.accuracy,
                    'shape': df.shape
                })
                
                print(f"  Page {page_num}, Table {len(results[page_num])}: {df.shape} (accuracy: {table.accuracy:.1f}%)")
            
            return results
            
        except Exception as e:
            print(f"Error extracting tables: {e}")
            return {}
    
    def auto_extract(self, page_num):
        """
        Automatically try both lattice and stream modes, return best result
        
        Args:
            page_num: Page number (1-indexed)
            
        Returns:
            List of DataFrames
        """
        print(f"\n=== Auto-extracting from page {page_num} ===")
        
        # Try lattice first (more accurate for bordered tables)
        print("Trying lattice mode (for tables with borders)...")
        lattice_tables = self.extract_tables_from_page(page_num, flavor='lattice')
        
        # Try stream (better for borderless tables)
        print("\nTrying stream mode (for tables without borders)...")
        stream_tables = self.extract_tables_from_page(page_num, flavor='stream')
        
        # Return whichever found more/better tables
        if len(lattice_tables) >= len(stream_tables):
            print(f"\n→ Using lattice mode results ({len(lattice_tables)} tables)")
            return lattice_tables
        else:
            print(f"\n→ Using stream mode results ({len(stream_tables)} tables)")
            return stream_tables
    
    def extract_usgs_commodity_table(self, page_num, flavor='stream'):
        """
        Specialized extraction for USGS Mineral Commodity Summaries
        These typically work better with stream mode
        
        Args:
            page_num: Page number (1-indexed)
            flavor: 'lattice' or 'stream' (default: stream)
            
        Returns:
            DataFrame or None
        """
        # USGS tables often work better with stream mode and custom settings
        if flavor == 'stream':
            kwargs = {
                'edge_tol': 50,        # Tolerance for edge detection
                'row_tol': 10,          # Tolerance for row separation
                'column_tol': 5,        # Tolerance for column separation
            }
        else:
            kwargs = {}
        
        tables = self.extract_tables_from_page(page_num, flavor=flavor, **kwargs)
        
        if not tables:
            return None
        
        # Return the largest table (usually the Salient Statistics table)
        largest_table = max(tables, key=lambda df: df.shape[0] * df.shape[1])
        return largest_table
    
    def save_tables_to_csv(self, tables_dict, output_dir="camelot_output"):
        """
        Save extracted tables to CSV files
        
        Args:
            tables_dict: Dictionary from extract_tables_from_pages()
            output_dir: Output directory
        """
        Path(output_dir).mkdir(exist_ok=True)
        
        for page_num, table_list in tables_dict.items():
            for i, table_info in enumerate(table_list):
                filename = f"{output_dir}/page_{page_num}_table_{i+1}.csv"
                table_info['dataframe'].to_csv(filename, index=False, header=False)
                print(f"Saved: {filename}")
    
    def save_tables_to_excel(self, tables_dict, output_file="camelot_output.xlsx"):
        """
        Save all tables to Excel with one sheet per table
        
        Args:
            tables_dict: Dictionary from extract_tables_from_pages()
            output_file: Output Excel filename
        """
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for page_num, table_list in tables_dict.items():
                for i, table_info in enumerate(table_list):
                    sheet_name = f"P{page_num}_T{i+1}"[:31]
                    table_info['dataframe'].to_excel(
                        writer, 
                        sheet_name=sheet_name, 
                        index=False,
                        header=False
                    )
                    print(f"Saved sheet: {sheet_name}")
        
        print(f"\n✓ All tables saved to {output_file}")
    
    def extract_all_usgs_commodities(self, start_page=31, end_page=205, flavor='stream'):
        """
        Extract all USGS commodity tables (one per page)
        
        Args:
            start_page: First page (1-indexed, default 31)
            end_page: Last page (1-indexed, default 205)
            flavor: 'lattice' or 'stream'
            
        Returns:
            Dictionary with page numbers and DataFrames
        """
        results = {}
        
        print(f"Extracting USGS tables from pages {start_page} to {end_page}...")
        
        for page_num in range(start_page, end_page + 1):
            try:
                df = self.extract_usgs_commodity_table(page_num, flavor=flavor)
                if df is not None and not df.empty:
                    results[page_num] = df
                    print(f"✓ Page {page_num}: {df.shape}")
                else:
                    print(f"✗ Page {page_num}: No table found")
            except Exception as e:
                print(f"✗ Page {page_num}: Error - {e}")
        
        return results
    
    def get_table_quality_report(self, page_num):
        """
        Get detailed quality report for tables on a page
        
        Args:
            page_num: Page number (1-indexed)
        """
        print(f"\n=== Quality Report for Page {page_num} ===\n")
        
        for flavor in ['lattice', 'stream']:
            print(f"{flavor.upper()} MODE:")
            try:
                tables = camelot.read_pdf(
                    self.pdf_path,
                    pages=str(page_num),
                    flavor=flavor
                )
                
                for i, table in enumerate(tables):
                    print(f"  Table {i+1}:")
                    print(f"    Shape: {table.df.shape}")
                    print(f"    Accuracy: {table.accuracy:.2f}%")
                    print(f"    Whitespace: {table.whitespace:.2f}%")
                    
                    # Show first few cells
                    if not table.df.empty:
                        print(f"    First cell: '{table.df.iloc[0, 0]}'")
                        print(f"    Sample data: {table.df.iloc[0].tolist()[:3]}")
                    print()
            except Exception as e:
                print(f"  Error: {e}\n")


def main():
    """Example usage"""
    
    pdf_path = "data/mcs2024.pdf"
    extractor = CamelotTableExtractor(pdf_path)
    
    # Example 1: Extract from a single page
    print("="*80)
    print("EXAMPLE 1: Single Page Extraction")
    print("="*80)
    
    tables = extractor.auto_extract(32)  # Note: 1-indexed!
    
    if tables:
        print("\n--- EXTRACTED TABLE ---")
        print(tables[0])
        print(f"\nShape: {tables[0].shape}")
    
    # Example 2: Extract from multiple pages
    print("\n" + "="*80)
    print("EXAMPLE 2: Multiple Pages")
    print("="*80)
    
    # Extract pages 32-205
    results = extractor.extract_tables_from_pages('32-205', flavor='stream')
    
    # Example 3: Get quality report
    print("\n" + "="*80)
    print("EXAMPLE 3: Quality Report")
    print("="*80)
    
    extractor.get_table_quality_report(32)
    
    # Example 4: Extract specific USGS commodity
    print("\n" + "="*80)
    print("EXAMPLE 4: USGS Commodity Table")
    print("="*80)
    
    df = extractor.extract_usgs_commodity_table(32, flavor='stream')
    if df is not None:
        print("\nSalient Statistics Table:")
        print(df)
    
    # Example 5: Save to files
    if results:
        print("\n" + "="*80)
        print("EXAMPLE 5: Saving Results")
        print("="*80)
        
        extractor.save_tables_to_csv(results)
        extractor.save_tables_to_excel(results, "usgs_camelot.xlsx")


if __name__ == "__main__":
    main()
