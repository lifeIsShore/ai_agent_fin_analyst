import fitz
import re
from typing import List

def isolate_financial_pages(filepath: str) -> str:
    """
    Scans a massive PDF (like a 120-page 10-K) to find the exact pages
    containing the core financial statements (Income, Balance, Cash Flow).
    Returns only the concatenated text of those high-density pages to save LLM context window.
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        print(f"Error opening PDF {filepath}: {e}")
        return ""

    relevant_text = []
    
    # Common headers for financial statements in 10-K/Annual reports
    keywords = [
        "consolidated statement of income",
        "consolidated statements of operations",
        "consolidated balance sheet",
        "consolidated statements of cash flow"
    ]
    
    # We use a scoring system for each page
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").lower()
        
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
                
        # If the page contains numbers (like a table) and hits our keywords, it's a goldmine.
        # Check if it has a high density of numbers/digits
        digits = len(re.findall(r'\d', text))
        
        if score > 0 and digits > 100:
            print(f"Isolated high-value financial data on page {page_num + 1}")
            relevant_text.append(page.get_text("text"))
            
    doc.close()
    
    if not relevant_text:
        print("Warning: Could not confidently isolate financial statement pages. Returning first 10 pages as fallback.")
        # Fallback to just reading the beginning if it's a short document
        doc = fitz.open(filepath)
        for i in range(min(10, len(doc))):
            relevant_text.append(doc[i].get_text("text"))
        doc.close()

    return "\n\n--- NEXT PAGE ---\n\n".join(relevant_text)
