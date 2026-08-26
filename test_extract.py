import pdfplumber
import os

pdf_path = os.path.join("company-reports", "friedrich_vorwerk_group_se_-_annual_report_2023.pdf")
pages = [45, 47, 49]

with pdfplumber.open(pdf_path) as pdf:
    for page_num in pages:
        print(f"\n--- PAGE {page_num} ---")
        page = pdf.pages[page_num]
        
        # Test table extraction
        tables = page.extract_tables()
        if not tables:
            print("pdfplumber.extract_tables() found NO tables.")
        else:
            print(f"pdfplumber found {len(tables)} tables.")
            for i, table in enumerate(tables):
                print(f"  Table {i}:")
                for row in table:
                    print(f"    {row}")
                    
        # Test raw text extraction
        print("\nRaw Text Snippet (First 500 chars):")
        text = page.extract_text()
        print(text[:500] if text else "None")
