import fitz
import re
import ollama
import json

def get_large_text(page):
    """Extracts text blocks that are likely section headers based on font size."""
    headers = []
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    # Typical body text is 9-12pt. Headers are usually > 13pt.
                    if s["size"] >= 13.0 and len(s["text"].strip()) > 5:
                        headers.append(s["text"].strip())
    return headers

def locate_statement_pages(filepath: str) -> dict:
    """
    Returns a dictionary of page numbers:
    {'income_statement': X, 'balance_sheet': Y, 'cash_flow': Z}
    Uses Regex fast-path, falls back to LLM title-search.
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        print(f"Error opening PDF {filepath}: {e}")
        return {}

    found_pages = {}
    
    # Regex Fast Path
    print("  -> [Pre-Processor] Attempting Regex Fast Path...")
    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text").lower()
        
        if "statement of profit or loss" in text or "gewinn- und verlustrechnung" in text:
            if "income_statement" not in found_pages:
                found_pages["income_statement"] = page_num
                
        if "statement of financial position" in text or "balance sheet" in text or "bilanz" in text:
            if "balance_sheet" not in found_pages:
                found_pages["balance_sheet"] = page_num
                
        if "statement of cash flows" in text or "kapitalflussrechnung" in text:
            if "cash_flow" not in found_pages:
                found_pages["cash_flow"] = page_num

        if len(found_pages) == 3:
            print("  -> [Pre-Processor] Regex Fast Path SUCCESS!")
            doc.close()
            return found_pages

    # Fallback Path: Extract Semantic Titles
    print("  -> [Pre-Processor] Regex failed to find all 3. Falling back to Semantic Title Extraction...")
    toc_lines = []
    for page_num in range(min(100, len(doc))): # Search first 100 pages to save time
        headers = get_large_text(doc[page_num])
        if headers:
            combined_header = " | ".join(headers)
            # Filter out numbers/noise
            if len(re.sub(r'\d', '', combined_header)) > 10:
                toc_lines.append(f"Page {page_num}: {combined_header}")

    doc.close()
    
    if not toc_lines:
        print("  -> [Pre-Processor] Fallback failed (no titles found).")
        return found_pages

    toc_text = "\n".join(toc_lines)
    
    prompt = f"""
    You are an expert financial analyst. Below is a list of section headers and their page numbers extracted from an annual report.
    Identify the page numbers for the Income Statement (Profit or Loss), the Balance Sheet (Financial Position), and the Cash Flow Statement.
    
    TITLES:
    {toc_text}
    
    Return a valid JSON object with the exact keys: "income_statement", "balance_sheet", "cash_flow". The values must be integers (the page number).
    If you cannot find one, set its value to -1.
    """
    
    schema = {
        "type": "object",
        "properties": {
            "income_statement": {"type": "integer"},
            "balance_sheet": {"type": "integer"},
            "cash_flow": {"type": "integer"}
        },
        "required": ["income_statement", "balance_sheet", "cash_flow"]
    }
    
    try:
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            format=schema,
            options={'temperature': 0.0}
        )
        result = json.loads(response['message']['content'])
        print(f"  -> [Pre-Processor] LLM Fallback SUCCESS: {result}")
        return result
    except Exception as e:
        print(f"  -> [Pre-Processor] LLM Fallback failed: {e}")
        return found_pages
