import argparse
import os
import glob
import re
from pre_processor import locate_statement_pages
from table_extractor import extract_financial_data
from llm_extractor_dcf import extract_mda_with_llm, generate_dynamic_scenarios
from market_data import get_market_data
from dcf_engine import calculate_wacc, project_financials
from dcf_excel_exporter import export_dcf_to_excel
from models_dcf import CompanyFinancials, IncomeStatement, BalanceSheet, CashFlowStatement
from llm_extractor_dcf import DynamicScenarios
import yfinance as yf
import pandas as pd
import datetime

def fallback_to_yfinance_historicals(ticker_symbol: str) -> list[CompanyFinancials]:
    """Fallback: Pulls historical financials from Yahoo Finance if PDFs are missing."""
    print(f"\n[Fallback] Pulling historical data from Yahoo Finance for {ticker_symbol}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        inc = ticker.income_stmt
        bal = ticker.balance_sheet
        cf = ticker.cashflow
        
        if inc.empty or bal.empty or cf.empty:
            print("  [Error] Yahoo Finance returned empty tables.")
            return []
            
        historical_data_list = []
        # Get the columns (dates) available across all 3 statements, up to 4 years
        dates = inc.columns[:4]
        
        for date in reversed(dates):  # Process oldest to newest
            year = date.year
            
            # Helper to safely extract values from yfinance dataframe
            def get_val(df, keys):
                for k in keys:
                    if k in df.index:
                        val = df.loc[k, date]
                        if pd.notna(val): return float(val)
                return 0.0
                
            # Income Statement
            revenue = get_val(inc, ["Total Revenue", "Operating Revenue"])
            ebit = get_val(inc, ["EBIT", "Operating Income"])
            da = get_val(inc, ["Depreciation And Amortization", "Reconciled Depreciation"])
            net_income = get_val(inc, ["Net Income", "Net Income Common Stockholders"])
            
            # Balance Sheet
            cash = get_val(bal, ["Cash And Cash Equivalents", "Total Cash And Short Term Investments"])
            total_assets = get_val(bal, ["Total Assets"])
            total_debt = get_val(bal, ["Total Debt"])
            
            # Cash Flow
            operating_cash_flow = get_val(cf, ["Operating Cash Flow"])
            capex = get_val(cf, ["Capital Expenditure"])
            
            income_statement = IncomeStatement(
                revenue=abs(revenue), cogs=0, sga=0, da=abs(da), 
                ebit=ebit, interest_expense=0, taxes=0, net_income=net_income
            )
            balance_sheet = BalanceSheet(
                cash=abs(cash), current_assets=0, total_assets=abs(total_assets), 
                current_liabilities=0, total_debt=abs(total_debt), total_liabilities=0, shareholders_equity=0
            )
            cash_flow = CashFlowStatement(operating_cash_flow=operating_cash_flow, capex=abs(capex))
            
            data = CompanyFinancials(
                company_name=ticker_symbol,
                ticker=ticker_symbol,
                year=year,
                income_statement=income_statement,
                balance_sheet=balance_sheet,
                cash_flow=cash_flow,
                management_assumptions="Historical data retrieved via Yahoo Finance API fallback. No qualitative text available."
            )
            historical_data_list.append(data)
            
        print(f"  [Success] Retrieved {len(historical_data_list)} years of historicals from yfinance.")
        return historical_data_list
    except Exception as e:
        print(f"  [Error] yfinance fallback failed: {e}")
        return []
def extract_year_from_filename(filename: str) -> int:
    match = re.search(r'(20\d{2})', filename)
    if match:
        return int(match.group(1))
    return 2025 # Fallback

def run_batch_pipeline(folder_path: str, ticker: str):
    print(f"\n--- Starting DETERMINISTIC BATCH DCF Pipeline for {ticker} ---")
    print(f"Folder: {folder_path}")
    
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    historical_data_list = []
    
    if not pdf_files:
        print("No PDF files found in the specified folder.")
        historical_data_list = fallback_to_yfinance_historicals(ticker)
        if not historical_data_list:
            return
    else:
        print(f"Found {len(pdf_files)} PDF reports.")
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        year = extract_year_from_filename(filename)
        print(f"\n[Processing {filename} (Year: {year})]")
        
        # 1. Locate Pages (Hybrid Regex/LLM)
        page_map = locate_statement_pages(pdf_path)
        if not page_map:
            print("  -> Failed to locate financial statements.")
            continue
            
        print(f"  -> Found pages: {page_map}")
        
        # 2. Deterministic Extraction (Python)
        print("  -> Running Python Table Extraction...")
        data = extract_financial_data(pdf_path, page_map, year)
        
        # 3. MD&A Extraction (LLM)
        mda = extract_mda_with_llm(pdf_path)
        data.management_assumptions = mda
        
        historical_data_list.append(data)
        print(f"  -> Extracted Year {data.year} (Revenue: {data.income_statement.revenue})")
            
    if not historical_data_list:
        print("No historical data could be extracted from PDFs.")
        historical_data_list = fallback_to_yfinance_historicals(ticker)
        if not historical_data_list:
            return
        
    # Sort chronologically
    historical_data_list.sort(key=lambda x: x.year)
    
    # 4. Dynamic Insight Generation
    print("\n[Generating Dynamic Scenarios based on History & MD&A]")
    dynamic_scenarios = generate_dynamic_scenarios(historical_data_list)
    print(f"Dynamic Scenarios Insight:\n{dynamic_scenarios.insight_summary}\n")
    print(f"  Bear: {dynamic_scenarios.bear.revenue_growth:.1%}")
    print(f"  Base: {dynamic_scenarios.base.revenue_growth:.1%}")
    print(f"  Bull: {dynamic_scenarios.bull.revenue_growth:.1%}")
    
    # 5. DCF Math Engine
    most_recent_data = historical_data_list[-1]
    print("\n[Pulling live market data...]")
    market_data = get_market_data(ticker)
    
    print("\n[Running Dynamic DCF Math Engine...]")
    wacc = calculate_wacc(market_data)
    print(f"Calculated WACC: {wacc:.2%}")
    
    results, final_wacc, scale = project_financials(most_recent_data, wacc, market_data, dynamic_scenarios=dynamic_scenarios)
    
    print("\n--- VALUATION RESULTS ---")
    print(f"Assumed Scale Factor: {scale}")
    for scenario, data in results.items():
        print(f"\n{scenario} Case (Growth: {data['rev_growth']:.1%})")
        print(f"  Target Price (Perpetuity Growth): €{data['implied_price_pg']:,.2f}")
        print(f"  Target Price (Exit Multiple):     €{data['implied_price_mult']:,.2f}")
    print("-------------------------")
    
    # 6. Export to Excel
    export_dcf_to_excel(historical_data_list, dynamic_scenarios, market_data, wacc, scale, results, "batch_dcf_output.xlsx")
    
    # 7. Save to SQLite DB
    print("\n[Saving qualitative insights and target prices to SQLite Database...]")
    import sqlite3
    conn = sqlite3.connect('valuations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS valuations_v2
                 (ticker text, date text, wacc real, 
                  bear_target real, base_target real, bull_target real,
                  confidence_score integer, rationale text,
                  latest_ebit_margin real, latest_net_margin real,
                  latest_capex_to_rev real, latest_roa real,
                  proj_y1_rev real, proj_y1_ufcf real)''')
                  
    import datetime
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Calculate KPIs for most recent year
    rev = most_recent_data.income_statement.revenue
    ebit_margin = most_recent_data.income_statement.ebit / rev if rev else 0
    net_margin = most_recent_data.income_statement.net_income / rev if rev else 0
    capex_rev = most_recent_data.cash_flow.capex / rev if rev else 0
    assets = most_recent_data.balance_sheet.total_assets
    roa = most_recent_data.income_statement.net_income / assets if assets else 0
    
    c.execute("""INSERT INTO valuations_v2 (
                 ticker, date, wacc, bear_target, base_target, bull_target,
                 confidence_score, rationale, latest_ebit_margin, latest_net_margin,
                 latest_capex_to_rev, latest_roa, proj_y1_rev, proj_y1_ufcf
                 ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
              (ticker, today, wacc, 
               results['Bear']['implied_price_pg'], 
               results['Base']['implied_price_pg'], 
               results['Bull']['implied_price_pg'],
               dynamic_scenarios.management_confidence_score, 
               dynamic_scenarios.confidence_rationale,
               ebit_margin, net_margin, capex_rev, roa,
               results['Base']['projected_rev'][0],
               results['Base']['projected_ufcf'][0]))
               
    conn.commit()
    conn.close()
    print("  -> Saved successfully to valuations.db!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deterministic Batch DCF Agent Pipeline")
    parser.add_argument("folder_path", help="Path to the folder containing Annual Report PDFs")
    parser.add_argument("ticker", help="Yahoo Finance Ticker (e.g. AAPL, VH2.DE)")
    
    args = parser.parse_args()
    run_batch_pipeline(args.folder_path, args.ticker)
