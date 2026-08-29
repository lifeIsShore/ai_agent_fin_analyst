import os
import time
import pandas as pd
import requests
from batch_dcf import run_batch_pipeline
from analyst_agent import run_agent

def get_sp500_tickers():
    """Fetches the current S&P 500 tickers from Wikipedia."""
    print("[Fetching S&P 500 Tickers from Wikipedia...]")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    tables = pd.read_html(response.text)
    df = tables[0]
    tickers = df['Symbol'].tolist()
    
    # Clean up tickers with dots (e.g. BRK.B -> BRK-B for Yahoo Finance compatibility)
    tickers = [t.replace('.', '-') for t in tickers]
    return tickers

def run_massive_backfill():
    print("=======================================================")
    print(" INITIATING S&P 500 AUTONOMOUS DATA BACKFILL (~1 HOUR) ")
    print("=======================================================")
    
    tickers = get_sp500_tickers()
    empty_folder = "company-reports/empty_fallback_test"
    os.makedirs(empty_folder, exist_ok=True)
    
    # We will process all 500 tickers!
    for idx, ticker in enumerate(tickers, start=1):
        try:
            print(f"\n>>> [{idx}/500] Processing {ticker}")
            
            # 1. Run DCF pipeline on an empty folder to instantly trigger the yfinance fallback
            run_batch_pipeline(empty_folder, ticker)
            
            # 2. Run the Analyst Consensus Agent to scrape DuckDuckGo/Yahoo and update DB
            run_agent(ticker)
            
            # Sleep briefly to avoid aggressive rate limits
            time.sleep(2)
        except Exception as e:
            print(f"  [Error] Failed processing {ticker}: {e}")
            
    print("\n=======================================================")
    print(" S&P 500 BACKFILL COMPLETE! READY FOR REGRESSION ENGINE! ")
    print("=======================================================")

if __name__ == "__main__":
    run_massive_backfill()
