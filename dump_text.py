import pdfplumber
import os
import sys
from pre_processor import locate_statement_pages

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = os.path.join("company-reports", "friedrich_vorwerk_group_se_-_annual_report_2020.pdf")
page_map = locate_statement_pages(pdf_path)

with open("dump_2020.txt", "w", encoding="utf-8") as f:
    with pdfplumber.open(pdf_path) as pdf:
        for stmt, p in page_map.items():
            f.write(f"\n--- {stmt.upper()} (Page {p}) ---\n")
            pages_to_read = [p]
            if p + 1 < len(pdf.pages):
                pages_to_read.append(p + 1)
            for p_num in pages_to_read:
                text = pdf.pages[p_num].extract_text()
                if text:
                    f.write(text + "\n")
