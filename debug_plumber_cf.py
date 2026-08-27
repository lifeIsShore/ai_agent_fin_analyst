import pdfplumber
with pdfplumber.open("company-reports/friedrich_vorwerk_group_se_-_annual_report_2025.pdf") as pdf:
    print(pdf.pages[57].extract_text())
