import fitz  # PyMuPDF

def extract_text_from_pdf(filepath: str) -> str:
    """
    Deterministically extracts text from a PDF.
    Returns the text if found. If the PDF has very little text (likely an image/scan),
    returns an empty string to trigger the vision fallback.
    """
    text = ""
    try:
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
        return ""
        
    # If the text is very short, it's probably a scanned image wrapper
    if len(text.strip()) < 50:
        return ""
        
    return text.strip()
