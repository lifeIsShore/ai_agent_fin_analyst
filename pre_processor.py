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
    
    # Header-Based Deterministic Path (Ignores TOC and Summary body text)
    print("  -> [Pre-Processor] Attempting Header-Based Fast Path...")
    for page_num in range(min(100, len(doc))):
        headers = get_large_text(doc[page_num])
        if not headers: continue
        
        combined_header = " ".join(headers).lower()
        
        if "statement of profit or loss" in combined_header or "gewinn- und verlustrechnung" in combined_header or "income statement" in combined_header:
            if "income_statement" not in found_pages:
                found_pages["income_statement"] = page_num
                
        if "statement of financial position" in combined_header or "balance sheet" in combined_header or "bilanz" in combined_header:
            if "balance_sheet" not in found_pages:
                found_pages["balance_sheet"] = page_num
                
        if "statement of cash flows" in combined_header or "kapitalflussrechnung" in combined_header:
            if "cash_flow" not in found_pages:
                found_pages["cash_flow"] = page_num

        if len(found_pages) == 3:
            print("  -> [Pre-Processor] Header-Based Fast Path SUCCESS!")
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

def locate_qualitative_pages(filepath: str) -> dict:
    """
    Returns a dictionary of page numbers for qualitative sections:
    {'mda': X, 'risk_factors': Y}
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        print(f"Error opening PDF {filepath}: {e}")
        return {}

    found_pages = {}
    print("  -> [Pre-Processor] Attempting to locate qualitative pages via Regex...")
    
    # We scan the first 150 pages assuming MD&A/Risk are early on
    for page_num in range(min(150, len(doc))):
        headers = get_large_text(doc[page_num])
        if not headers: continue
        
        combined_header = " ".join(headers).lower()
        
        # Item 7. Management's Discussion and Analysis
        if "management's discussion" in combined_header or "item 7" in combined_header:
            if "mda" not in found_pages:
                found_pages["mda"] = page_num
                
        # Item 1A. Risk Factors
        if "risk factors" in combined_header or "item 1a" in combined_header:
            if "risk_factors" not in found_pages:
                found_pages["risk_factors"] = page_num
                
        if len(found_pages) == 2:
            break
            
    print(f"  -> [Pre-Processor] Qualitative pages found: {found_pages}")
    doc.close()
    return found_pages

def extract_qualitative_text(filepath: str, pages_dict: dict, max_pages: int = 3) -> dict:
    """
    Extracts up to `max_pages` of text for each identified section.
    Returns: {'mda': "...", 'risk_factors': "..."}
    """
    results = {"mda": "", "risk_factors": ""}
    
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        print(f"Error opening PDF for text extraction: {e}")
        return results

    for key, start_page in pages_dict.items():
        extracted_text = []
        for i in range(start_page, min(start_page + max_pages, len(doc))):
            text = doc[i].get_text("text")
            extracted_text.append(text)
        results[key] = "\n".join(extracted_text)

    doc.close()
    return results
