import pdfplumber
import re
from models_dcf import CompanyFinancials, IncomeStatement, BalanceSheet, CashFlowStatement
from llm_extractor_dcf import fallback_extract_with_llm

def clean_number(num_str: str) -> float:
    if not num_str: return 0.0
    is_neg = '-' in num_str or ('(' in num_str and ')' in num_str)
    cleaned = re.sub(r'[^\d,\.]', '', num_str)
    if not cleaned: return 0.0
    
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rfind(',') > cleaned.rfind('.'):
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
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
    if 'keur' in text_lower or 'teur' in text_lower or 'in thousands' in text_lower or 'in 000s' in text_lower or "€ '000" in text_lower:
        return 1000.0
    if 'millions' in text_lower or 'in mio' in text_lower or 'in m' in text_lower:
        return 1000000.0
    return 1.0

def extract_numbers_from_line(line: str) -> list[str]:
    line = re.sub(r'\b[IVX]+\.\d+\.?\b', '', line)
    matches = re.findall(r'-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?', line)
    valid_nums = [m for m in matches if m not in ['2020', '2021', '2022', '2023', '2024', '2025']]
    return valid_nums

def extract_financial_data(filepath: str, page_map: dict, year: int) -> CompanyFinancials:
    inc = IncomeStatement(revenue=0, cogs=0, sga=0, da=0, ebit=0, interest_expense=0, taxes=0, net_income=0)
    bal = BalanceSheet(cash=0, current_assets=0, total_assets=0, current_liabilities=0, total_debt=0, total_liabilities=0, shareholders_equity=0)
    cf = CashFlowStatement(operating_cash_flow=0, capex=0)
    
    all_raw_text = ""
    
    with pdfplumber.open(filepath) as pdf:
        # Get sorted list of statement start pages to calculate ranges
        sorted_start_pages = sorted(list(page_map.values()))
        
        for stmt_type, page_num in page_map.items():
            if page_num < 0 or page_num >= len(pdf.pages): continue
            
            # Determine the end page by looking at the start of the next statement
            end_page = page_num + 4 # Fallback maximum of 4 pages for a single statement
            for next_start in sorted_start_pages:
                if next_start > page_num:
                    end_page = min(end_page, next_start)
                    break
                    
            pages_to_read = list(range(page_num, end_page))
                
            for p_num in pages_to_read:
                if p_num >= len(pdf.pages): continue
                page = pdf.pages[p_num]
                text = page.extract_text()
                if not text: continue
                
                all_raw_text += text + "\n\n"
                multiplier = find_unit_multiplier(text)
                lines = text.split('\n')
                
                for line in lines:
                    label_match = re.match(r'^([a-zA-Z\s,\-\(\)\+/&]+)', line)
                    if not label_match: continue
                    label = label_match.group(1).lower().strip()
                    
                    nums = extract_numbers_from_line(line)
                    if not nums: continue
                    
                    val = clean_number(nums[0]) * multiplier
                    if val == 0: continue
                    
                    if stmt_type == 'income_statement':
                        if 'revenue' in label or 'umsatz' in label or 'sales' in label or 'turnover' in label:
                            if inc.revenue == 0: inc.revenue = abs(val)
                        elif ('ebit' in label and 'ebitda' not in label) or 'betriebsergebnis' in label or 'operating result' in label or 'operating profit' in label:
                            if inc.ebit == 0: inc.ebit = val # EBIT can be negative
                        elif ('depreciation' in label or 'amortisation' in label or 'amortization' in label or 'abschreibungen' in label) and 'ebitda' not in label:
                            if inc.da == 0: inc.da = abs(val)
                        elif 'net income' in label or 'konzernergebnis' in label or 'net profit' in label or 'profit for the period' in label:
                            if inc.net_income == 0: inc.net_income = val # Net Income can be negative
                            
                    elif stmt_type == 'balance_sheet':
                        if 'cash and' in label or 'zahlungsmittel' in label or 'bank balances' in label or 'cash in hand' in label:
                            if bal.cash == 0: bal.cash = abs(val)
                        elif 'total assets' in label or 'summe aktiva' in label or 'bilanzsumme' in label:
                            if bal.total_assets == 0: bal.total_assets = abs(val)
                        elif 'financial liabilities' in label or 'liabilities to banks' in label or 'finanzverbindlichkeiten' in label or 'borrowings' in label or 'schulden' in label or 'debt' in label:
                            bal.total_debt += abs(val)
                            
                    elif stmt_type == 'cash_flow':
                        if 'cash flow from operating' in label or 'laufende geschäftstätigkeit' in label or 'net cash from operating' in label:
                            if cf.operating_cash_flow == 0: cf.operating_cash_flow = val
                        elif 'property, plant' in label or 'sachanlagen' in label or 'capital expenditure' in label or 'capex' in label or 'intangible assets' in label:
                            cf.capex += abs(val)

    # SNIPER LLM FALLBACK TRIGGER
    # If the regex completely failed to find Revenue or Total Assets (e.g. they equal 0),
    # we fallback to the LLM sending ONLY the text of these 3 pages.
    if inc.revenue == 0 or bal.total_assets == 0:
        print(f"    -> [Table Extractor] Regex failed to find core metrics for {year}. Triggering Sniper LLM...")
        fallback_data = fallback_extract_with_llm(all_raw_text, year)
        if fallback_data:
            return fallback_data

    return CompanyFinancials(
        company_name="Extracted Company",
        ticker="UNKNOWN",
        year=year,
        income_statement=inc,
        balance_sheet=bal,
        cash_flow=cf,
        management_assumptions=""
    )
