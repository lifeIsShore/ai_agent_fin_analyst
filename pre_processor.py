import fitz
import re

def isolate_financial_pages(filepath: str, top_n: int = 5) -> str:
    """
    Scans a massive PDF and isolates the pages with the highest density of numbers.
    Financial statements (Income, Balance Sheet, Cash Flow) mathematically have the highest
    concentration of digits in any Annual Report, bypassing the need for language-specific keywords.
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        print(f"Error opening PDF {filepath}: {e}")
        return ""

    page_scores = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        
        # Count all numeric digits on the page
        digit_count = len(re.findall(r'\d', text))
        
        # Optional: Boost score slightly if standard English/German keywords are found
        boost = 0
        text_lower = text.lower()
        
        # English terms
        if "assets" in text_lower and "liabilities" in text_lower: boost += 100
        if "revenue" in text_lower and "profit" in text_lower: boost += 100
        if "cash flows" in text_lower: boost += 100
        
        # German/European terms
        if "bilanz" in text_lower or "aktiva" in text_lower or "passiva" in text_lower: boost += 100
        if "gewinn- und verlustrechnung" in text_lower or "umsatzerlöse" in text_lower: boost += 100
        if "kapitalflussrechnung" in text_lower: boost += 100
            
        final_score = digit_count + boost
        
        page_scores.append({
            "page_num": page_num,
            "score": final_score,
            "text": text
        })
            
    doc.close()
    
    # Sort pages by our density score in descending order
    page_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Dynamic threshold: Grab all pages that score significantly above average,
    # or just have a high absolute number of digits (>150), capped at 15 pages to protect context window.
    top_pages = [p for p in page_scores if p["score"] > 150][:15]
    
    # Fallback if no pages meet the threshold
    if not top_pages:
        top_pages = page_scores[:top_n]
        
    # Sort them back in chronological order just in case the LLM cares about flow
    top_pages.sort(key=lambda x: x["page_num"])
    
    relevant_text = []
    print(f"Isolated the {top_n} most data-dense pages:")
    for p in top_pages:
        print(f"  -> Page {p['page_num'] + 1} (Score: {p['score']})")
        relevant_text.append(p['text'])

    return "\n\n--- NEXT DATA PAGE ---\n\n".join(relevant_text)
