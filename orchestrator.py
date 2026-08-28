import argparse
import os
import time
import requests
from googlesearch import search
from batch_dcf import run_batch_pipeline

def download_pdf(url: str, save_path: str) -> bool:
    """Downloads a PDF from a given URL and saves it to the specified path."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, stream=True, timeout=15)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"      [!] Download failed: {e}")
    return False

def orchestrate_company(ticker: str, company_name: str, years: list, region: str = "US"):
    print(f"\n=======================================================")
    print(f" ORCHESTRATION SCRIPT STARTED: {company_name} ({ticker})")
    print(f"=======================================================")
    
    # Create target directory
    target_dir = os.path.join("company-reports", ticker)
    os.makedirs(target_dir, exist_ok=True)
    
    # Download Phase
    print(f"\n[Phase 1] Hunting for Annual Reports ({min(years)}-{max(years)}) via Google Search...")
    
    for year in years:
        save_filename = os.path.join(target_dir, f"{ticker}_annual_report_{year}.pdf")
        if os.path.exists(save_filename):
            print(f"  -> Year {year}: Already exists locally. Skipping download.")
            continue
            
        # Customize search query based on region
        if region.upper() == "US":
            query = f'"{company_name}" 10-K {year} filetype:pdf'
        else:
            query = f'"{company_name}" Annual Report {year} filetype:pdf'
            
        print(f"  -> Year {year}: Searching Google... ({query})")
        
        try:
            # We search and check the top 10 results for a valid PDF link
            results = list(search(query, num_results=10))
            download_success = False
            for url in results:
                try:
                    # Quick HEAD request to check Content-Type
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    h = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                    if 'application/pdf' in h.headers.get('Content-Type', '').lower() or url.lower().endswith('.pdf'):
                        print(f"      Found PDF link: {url[:60]}...")
                        if download_pdf(url, save_filename):
                            print(f"      [Success] Downloaded {year} report!")
                            download_success = True
                            break
                except Exception as e:
                    pass
            
            if not download_success:
                print(f"      [Failed] Could not find a valid PDF for {year}.")
                
            # Sleep to prevent Google rate-limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"      [Error] Google search failed: {e}")
            
    # Processing Phase
    print(f"\n[Phase 2] Triggering Batch DCF Pipeline on '{target_dir}'...")
    try:
        run_batch_pipeline(target_dir, ticker)
        print("\n[Orchestrator] Pipeline execution finished successfully!")
    except Exception as e:
        print(f"\n[Orchestrator Error] Pipeline crashed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-End Orchestrator for AI Financial Analyst")
    parser.add_argument("--ticker", required=True, help="Yahoo Finance Ticker (e.g. AAPL, VH2.DE)")
    parser.add_argument("--company", required=True, help="Company Name for searching (e.g. 'Apple Inc')")
    parser.add_argument("--region", default="US", choices=["US", "EU"], help="Region determines search terms (10-K vs Annual Report)")
    parser.add_argument("--years", nargs='+', type=int, default=[2023, 2024], help="List of years to fetch (e.g. 2023 2024)")
    
    args = parser.parse_args()
    orchestrate_company(args.ticker, args.company, args.years, args.region)
