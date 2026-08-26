import argparse
import os
import glob
from pre_processor import isolate_financial_pages
from llm_extractor_dcf import extract_financials_with_llm, generate_dynamic_scenarios
from market_data import get_market_data
from dcf_engine import calculate_wacc, project_financials

def run_batch_pipeline(folder_path: str, ticker: str):
    print(f"\n--- Starting BATCH DCF Pipeline for {ticker} ---")
    print(f"Folder: {folder_path}")
    
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    if not pdf_files:
        print("No PDF files found in the specified folder.")
        return
        
    print(f"Found {len(pdf_files)} PDF reports.")
    historical_data_list = []
    
    for pdf_path in pdf_files:
        print(f"\n[Processing {os.path.basename(pdf_path)}]")
        financial_text = isolate_financial_pages(pdf_path)
        if not financial_text:
            print("  -> Failed to isolate text.")
            continue
            
        print("  -> Running LLM Extraction...")
        data = extract_financials_with_llm(financial_text)
        if data:
            historical_data_list.append(data)
            print(f"  -> Extracted Year {data.year} (Revenue: {data.income_statement.revenue})")
        else:
            print("  -> LLM Extraction failed for this file.")
            
    if not historical_data_list:
        print("No historical data could be extracted.")
        return
        
    # Sort chronologically
    historical_data_list.sort(key=lambda x: x.year)
    
    # 2. Dynamic Insight Generation
    print("\n[Generating Dynamic Scenarios based on History & MD&A]")
    dynamic_scenarios = generate_dynamic_scenarios(historical_data_list)
    print(f"Dynamic Scenarios Insight:\n{dynamic_scenarios.insight_summary}\n")
    print(f"  Bear: {dynamic_scenarios.bear.revenue_growth:.1%}")
    print(f"  Base: {dynamic_scenarios.base.revenue_growth:.1%}")
    print(f"  Bull: {dynamic_scenarios.bull.revenue_growth:.1%}")
    
    # 3. Use most recent year for DCF Base
    most_recent_data = historical_data_list[-1]
    
    # 4. Pull Market Data
    print("\n[Pulling live market data...]")
    market_data = get_market_data(ticker)
    
    # 5. DCF Engine
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch DCF Agent Pipeline")
    parser.add_argument("folder_path", help="Path to the folder containing Annual Report PDFs")
    parser.add_argument("ticker", help="Yahoo Finance Ticker (e.g. AAPL, VH2.DE)")
    
    args = parser.parse_args()
    run_batch_pipeline(args.folder_path, args.ticker)
