import os
import time
from batch_dcf import run_batch_pipeline
from analyst_agent import run_agent

TICKERS = [
    ("AAPL", "Apple Inc"),
    ("MSFT", "Microsoft"),
    ("GOOG", "Alphabet"),
    ("AMZN", "Amazon"),
    ("TSLA", "Tesla"),
    ("NVDA", "Nvidia"),
    ("META", "Meta Platforms"),
    ("NFLX", "Netflix"),
    ("AMD", "Advanced Micro Devices"),
    ("INTC", "Intel")
]

def run_backfill():
    print("=======================================================")
    print(" INITIATING FAST-TRACK DATA BACKFILL (YAHOO FALLBACK)  ")
    print("=======================================================")
    
    empty_folder = "company-reports/empty_fallback_test"
    os.makedirs(empty_folder, exist_ok=True)
    
    for ticker, company in TICKERS:
        try:
            print(f"\n>>> Processing {ticker} ({company})")
            # 1. Run DCF pipeline on an empty folder to instantly trigger the yfinance fallback
            run_batch_pipeline(empty_folder, ticker)
            
            # 2. Run the Analyst Consensus Agent to scrape DuckDuckGo/Yahoo and update DB
            run_agent(ticker)
            
            # Sleep briefly to avoid aggressive rate limits
            time.sleep(2)
        except Exception as e:
            print(f"  [Error] Failed processing {ticker}: {e}")
            
    print("\n=======================================================")
    print(" BACKFILL COMPLETE! READY FOR REGRESSION ENGINE!       ")
    print("=======================================================")

if __name__ == "__main__":
    run_backfill()
