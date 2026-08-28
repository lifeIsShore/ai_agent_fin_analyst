import os
import re
import json
import sqlite3
import argparse
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from ollama import Client

OLLAMA_MODEL = "qwen2.5"  # Match the model used in qualitative_analyzer.py

def search_web(query: str, max_results=3) -> list:
    """Searches DuckDuckGo and returns URLs."""
    print(f"    [Agent] Searching web: '{query}'")
    urls = []
    try:
        results = DDGS().text(query, max_results=max_results)
        for r in results:
            urls.append(r.get('href'))
    except Exception as e:
        print(f"      [!] DuckDuckGo Search failed: {e}")
    return urls

def read_website_snippets(url: str) -> str:
    """Reads a website and extracts snippets that look like they contain target prices."""
    print(f"    [Agent] Reading: {url[:50]}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            
            # Resilient Regex to find snippets mentioning target prices
            # Looks for: target, consensus, average, price, $
            pattern = re.compile(r'(.{0,100}(?:target|consensus|average).{0,50}price.{0,50}\$[\d\.]+.{0,100})', re.IGNORECASE)
            matches = pattern.findall(text)
            
            if matches:
                return " ".join(matches)
            else:
                # Fallback: grab first 2000 characters if regex fails, maybe LLM can find it
                return text[:2000]
    except Exception:
        pass
    return ""

def extract_target_price_with_llm(snippets: str, ticker: str) -> float:
    """Uses the local LLM to extract the exact consensus target price from text snippets."""
    if not snippets.strip():
        return 0.0
        
    client = Client(host='http://localhost:11434')
    
    prompt = f"""
    You are an expert financial analyst. I will give you text snippets from financial websites about the stock {ticker}.
    Your task is to find the "Consensus Target Price" or "Average Target Price" for {ticker}.
    
    Return ONLY a valid JSON object in this exact format:
    {{"consensus_target": 150.50}}
    
    If you cannot find a clear consensus or average target price, return 0.0.
    
    Snippets:
    {snippets[:4000]}
    """
    
    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        
        result_text = response['message']['content']
        data = json.loads(result_text)
        return float(data.get("consensus_target", 0.0))
    except Exception as e:
        print(f"      [!] LLM Extraction failed: {e}")
        return 0.0

def update_database(ticker: str, target_price: float):
    """Updates the valuations_v2 database with the new consensus target."""
    conn = sqlite3.connect("valuations.db")
    cursor = conn.cursor()
    
    # Check if column exists, if not, create it
    cursor.execute("PRAGMA table_info(valuations_v2)")
    columns = [col[1] for col in cursor.fetchall()]
    if "consensus_target" not in columns:
        print("    [Database] Adding 'consensus_target' column to valuations_v2 table.")
        cursor.execute("ALTER TABLE valuations_v2 ADD COLUMN consensus_target REAL DEFAULT 0.0")
        
    # Update the row for this ticker
    cursor.execute("UPDATE valuations_v2 SET consensus_target = ? WHERE ticker = ?", (target_price, ticker))
    conn.commit()
    conn.close()

def log_not_found(ticker: str):
    """Logs failed tickers so the user can manually input them later."""
    with open("not_found_targets.txt", "a") as f:
        f.write(f"{ticker}\n")

def fetch_fallback_target(ticker: str) -> float:
    """Fallback to Yahoo Finance if web search is blocked."""
    import yfinance as yf
    try:
        info = yf.Ticker(ticker).info
        return info.get("targetMeanPrice", 0.0)
    except:
        return 0.0

def run_agent(ticker: str):
    print(f"\n=======================================================")
    print(f" ANALYST CONSENSUS AGENT INITIATED: {ticker}")
    print(f"=======================================================")
    
    # Step 1: Search
    query = f"{ticker} wall street consensus average target price"
    urls = search_web(query, max_results=3)
    
    if not urls:
        print(f"  [Warning] Web search blocked or no results. Attempting fallback via yfinance...")
        target_price = fetch_fallback_target(ticker)
        if target_price > 0:
            print(f"  [Success] Found Consensus Target Price via Fallback for {ticker}: ${target_price}")
            update_database(ticker, target_price)
            print("    [Database] Updated valuations_v2 successfully.")
            return
            
        print(f"  [Error] Fallback failed. Logging {ticker} to not_found_targets.txt.")
        log_not_found(ticker)
        return
        
    # Step 2: Read and Extract Snippets
    combined_snippets = ""
    for url in urls:
        combined_snippets += read_website_snippets(url) + "\n"
        
    # Step 3: LLM Reasoning
    print("    [Agent] Snippets gathered. Asking LLM to extract target price...")
    target_price = extract_target_price_with_llm(combined_snippets, ticker)
    
    if target_price > 0:
        print(f"  [Success] Found Consensus Target Price for {ticker}: ${target_price}")
        update_database(ticker, target_price)
        print("    [Database] Updated valuations_v2 successfully.")
    else:
        print(f"  [Failed] Could not confidently determine target price from web data.")
        print(f"           Logging {ticker} to not_found_targets.txt")
        log_not_found(ticker)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Analyst Consensus Agent")
    parser.add_argument("--ticker", required=True, help="Stock ticker to research (e.g., MSFT)")
    args = parser.parse_args()
    
    run_agent(args.ticker)
