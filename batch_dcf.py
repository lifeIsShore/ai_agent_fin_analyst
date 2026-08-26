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

def extract_year_from_filename(filename: str) -> int:
    match = re.search(r'(20\d{2})', filename)
    if match:
        return int(match.group(1))
    return 2025 # Fallback

def run_batch_pipeline(folder_path: str, ticker: str):
    print(f"\n--- Starting DETERMINISTIC BATCH DCF Pipeline for {ticker} ---")
    print(f"Folder: {folder_path}")
    
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    if not pdf_files:
        print("No PDF files found in the specified folder.")
        return
        
    print(f"Found {len(pdf_files)} PDF reports.")
    historical_data_list = []
    
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
        print("No historical data could be extracted.")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deterministic Batch DCF Agent Pipeline")
    parser.add_argument("folder_path", help="Path to the folder containing Annual Report PDFs")
    parser.add_argument("ticker", help="Yahoo Finance Ticker (e.g. AAPL, VH2.DE)")
    
    args = parser.parse_args()
    run_batch_pipeline(args.folder_path, args.ticker)
