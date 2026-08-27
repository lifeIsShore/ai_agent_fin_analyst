from table_extractor import extract_financial_data
import fitz
import json

doc = fitz.open("company-reports/friedrich_vorwerk_group_se_-_annual_report_2025.pdf")
data = extract_financial_data("company-reports/friedrich_vorwerk_group_se_-_annual_report_2025.pdf", {'income_statement': 53, 'balance_sheet': 55, 'cash_flow': 57}, 2025)
print(data.model_dump_json(indent=2))
doc.close()
