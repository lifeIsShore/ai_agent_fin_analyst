import os
import time
from batch_dcf import run_batch_pipeline
from analyst_agent import run_agent

# 150 MORE S&P 500 Companies to push our data size to 200 total observations
TICKERS = [
    "A", "AAL", "AAP", "ABT", "ACN", "ADSK", "AEE", "AEP", "AFL", "AIG", 
    "ALL", "ALXN", "AMAT", "AME", "AMP", "AON", "APA", "APD", "APH", "APTV", 
    "ARE", "AZO", "BAX", "BBY", "BDX", "BEN", "BIIB", "BK", "BKNG", "BKR", 
    "BLL", "BMY", "BR", "BSX", "BWA", "BXP", "C", "CAG", "CAH", "CARR", 
    "CB", "CBOE", "CBRE", "CCI", "CCL", "CDNS", "CDW", "CE", "CF", "CFG", 
    "CHD", "CHRW", "CHTR", "CI", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME", 
    "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "CPRT", "CSX", 
    "CTAS", "CTL", "CTSH", "CTVA", "CVS", "D", "DAL", "DD", "DFS", "DG", 
    "DGX", "DHI", "DHR", "DLR", "DLTR", "DOV", "DOW", "DPZ", "DRE", "DRI", 
    "DTE", "DUK", "DVA", "DVN", "DXC", "EA", "EBAY", "ECL", "ED", "EFX", 
    "EIX", "EL", "EMN", "EMR", "EOG", "EQIX", "EQR", "ES", "ESS", "ETN", 
    "ETR", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", 
    "FBHS", "FCX", "FDX", "FE", "FFIV", "FIS", "FISV", "FITB", "FLIR", "FLS", 
    "FMC", "FOX", "FRC", "FRT", "FTI", "FTNT", "FTV", "GD", "GE", "GL", 
    "GLW", "GM", "GPC", "GPN", "GPS", "GRMN", "GWW", "HAL", "HAS", "HBAN", 
    "HBI", "HCA", "HES", "HFC", "HIG", "HII", "HLT", "HOG"
]

def run_backfill():
    print("=======================================================")
    print(f" INITIATING MASSIVE DATA BACKFILL: {len(TICKERS)} COMPANIES ")
    print("=======================================================")
    
    empty_folder = "company-reports/empty_fallback_test"
    os.makedirs(empty_folder, exist_ok=True)
    
    for ticker in TICKERS:
        try:
            print(f"\n>>> Processing {ticker}")
            # 1. Run DCF pipeline on an empty folder to instantly trigger the yfinance fallback
            run_batch_pipeline(empty_folder, ticker)
            
            # 2. Run the Analyst Consensus Agent to scrape DuckDuckGo/Yahoo and update DB
            run_agent(ticker)
            
            # Sleep briefly to avoid aggressive rate limits
            time.sleep(2)
        except Exception as e:
            print(f"  [Error] Failed processing {ticker}: {e}")
            
    print("\n=======================================================")
    print(" MASSIVE BACKFILL COMPLETE! READY FOR REGRESSION ENGINE! ")
    print("=======================================================")

if __name__ == "__main__":
    run_backfill()
