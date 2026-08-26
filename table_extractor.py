import pdfplumber
import re
from models_dcf import CompanyFinancials, IncomeStatement, BalanceSheet, CashFlowStatement

def clean_number(num_str: str) -> float:
    if not num_str:
        return 0.0
    # Remove parentheses for negatives
    is_neg = False
    if '(' in num_str and ')' in num_str:
        is_neg = True
    # Remove everything except digits, comma, period, minus
    cleaned = re.sub(r'[^\d,\.-]', '', num_str)
    if not cleaned:
        return 0.0
        
    # Handle European format: 1.500,00 vs US format: 1,500.00
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rfind(',') > cleaned.rfind('.'):
            # European: 1.500,00 -> 1500.00
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # US: 1,500.00 -> 1500.00
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Check if it's acting as a decimal (e.g. 15,5) or thousand separator (e.g. 1,500)
        parts = cleaned.split(',')
        if len(parts[-1]) != 3:
            cleaned = cleaned.replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
            
    try:
        val = float(cleaned)
        return -val if is_neg else val
    except:
        return 0.0

def find_unit_multiplier(text: str) -> float:
    if not text: return 1.0
    text_lower = text.lower()
    if 'keur' in text_lower or 'teur' in text_lower or 'in thousands' in text_lower or 'in 000s' in text_lower:
        return 1000.0
    if 'millions' in text_lower or 'in mio' in text_lower or 'in m' in text_lower:
        return 1000000.0
    return 1.0

def extract_financial_data(filepath: str, page_map: dict, year: int) -> CompanyFinancials:
    inc = IncomeStatement(revenue=0, cogs=0, sga=0, da=0, ebit=0, interest_expense=0, taxes=0, net_income=0)
    bal = BalanceSheet(cash=0, current_assets=0, total_assets=0, current_liabilities=0, total_debt=0, total_liabilities=0, shareholders_equity=0)
    cf = CashFlowStatement(operating_cash_flow=0, capex=0)
    
    with pdfplumber.open(filepath) as pdf:
        for stmt_type, page_num in page_map.items():
            if page_num < 0 or page_num >= len(pdf.pages):
                continue
                
            page = pdf.pages[page_num]
            text = page.extract_text()
            multiplier = find_unit_multiplier(text)
            
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or not row[0]: continue
                    label = str(row[0]).lower().strip()
                    
                    val = 0.0
                    for cell in row[1:]:
                        if cell and any(c.isdigit() for c in str(cell)):
                            val = clean_number(str(cell)) * multiplier
                            break # Most recent year is usually the first data column
                    
                    if val == 0: continue
                    
                    if stmt_type == 'income_statement':
                        if 'revenue' in label or 'umsatzerlöse' in label:
                            if inc.revenue == 0: inc.revenue = val
                        elif 'ebit' in label or 'operating result' in label or 'betriebsergebnis' in label:
                            if inc.ebit == 0: inc.ebit = val
                        elif 'net income' in label or 'konzernergebnis' in label:
                            if inc.net_income == 0: inc.net_income = val
                            
                    elif stmt_type == 'balance_sheet':
                        if 'cash and' in label or 'zahlungsmittel' in label:
                            if bal.cash == 0: bal.cash = val
                        elif 'total assets' in label or 'summe aktiva' in label:
                            if bal.total_assets == 0: bal.total_assets = val
                        elif 'financial liabilities' in label or 'finanzverbindlichkeiten' in label:
                            bal.total_debt += val # Short + long term
                            
                    elif stmt_type == 'cash_flow':
                        if 'operating activities' in label or 'laufende geschäftstätigkeit' in label:
                            if cf.operating_cash_flow == 0: cf.operating_cash_flow = val
                        elif 'property, plant and equipment' in label or 'sachanlagen' in label:
                            if cf.capex == 0: cf.capex = abs(val)

    return CompanyFinancials(
        company_name="Extracted Company",
        ticker="UNKNOWN",
        year=year,
        income_statement=inc,
        balance_sheet=bal,
        cash_flow=cf,
        management_assumptions="" # Extracted separately
    )
