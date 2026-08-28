import argparse
import os
import json
from pre_processor import isolate_financial_pages, locate_qualitative_pages, extract_qualitative_text
from qualitative_analyzer import analyze_qualitative_factors
from llm_extractor_dcf import extract_financials_with_llm
from market_data import get_market_data
from dcf_engine import calculate_wacc, project_financials

def run_dcf_pipeline(pdf_path: str, ticker: str):
    print(f"\n--- Starting DCF Pipeline for {ticker} ---")
    print(f"Document: {pdf_path}")
    
    # 1. Isolate pages
    print("[1] Running Pre-Processor to isolate financial pages...")
    financial_text = isolate_financial_pages(pdf_path)
    
    if not financial_text:
        print("Failed to extract text from PDF.")
        return
        
    print(f"Isolated {len(financial_text)} characters of high-density financial text.")
    
    # 2. Extract with LLM
    print("[2] Running LLM Extraction Engine...")
    historical_data = extract_financials_with_llm(financial_text)
    
    if not historical_data:
        print("Failed to extract structured financials via LLM.")
        return
        
    print(f"Successfully extracted financials for: {historical_data.company_name} ({historical_data.year})")
    print(f"Base Revenue: {historical_data.income_statement.revenue}")
    print(f"Base EBIT: {historical_data.income_statement.ebit}")
    
    # 2.5 Qualitative Macro-Scoring
    print("\n[2.5] Extracting Qualitative Factors (MD&A & Risks)...")
    qual_pages = locate_qualitative_pages(pdf_path)
    qual_text = extract_qualitative_text(pdf_path, qual_pages)
    
    qual_scores = analyze_qualitative_factors(
        mda_text=qual_text.get('mda', ''), 
        risk_text=qual_text.get('risk_factors', '')
    )
    historical_data.qualitative_scores = qual_scores
    
    # 3. Pull Market Data
    print("[3] Pulling live market data...")
    market_data = get_market_data(ticker)
    
    # 4. DCF Engine
    print("[4] Running DCF Math Engine...")
    wacc = calculate_wacc(market_data)
    print(f"Calculated WACC: {wacc:.2%}")
    
    results, final_wacc, scale = project_financials(historical_data, wacc, market_data)
    
    print("\n--- VALUATION RESULTS ---")
    print(f"Assumed Scale Factor: {scale}")
    for scenario, data in results.items():
        print(f"\n{scenario} Case (Growth: {data['rev_growth']:.1%})")
        print(f"  Target Price (Perpetuity Growth): €{data['implied_price_pg']:,.2f}")
        print(f"  Target Price (Exit Multiple):     €{data['implied_price_mult']:,.2f}")
        
    if historical_data.qualitative_scores:
        qs = historical_data.qualitative_scores
        print("\n--- QUALITATIVE SCORES ---")
        print(f"Confidence: {qs.confidence_score}/100")
        print(f"Risk & Transparency: {qs.risk_score}/100")
        print(f"Governance & ESG: {qs.governance_score}/100")
        print(f"Rationale: {qs.rationale}")
        
    print("-------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full DCF Agent Pipeline")
    parser.add_argument("pdf_path", help="Path to the Annual Report PDF")
    parser.add_argument("ticker", help="Yahoo Finance Ticker (e.g. AAPL, VH2.DE)")
    
    args = parser.parse_args()
    run_dcf_pipeline(args.pdf_path, args.ticker)
