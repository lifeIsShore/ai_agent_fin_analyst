import argparse
import os
from pdf_parser import extract_text_from_pdf
from llm_extractor import extract_with_llm
from vision_extractor import extract_with_vision
from calculation_engine import export_to_excel

def process_pdf(filepath: str, output_path: str):
    print(f"\n--- Processing: {filepath} ---")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    print("[1] Attempting deterministic text extraction...")
    text = extract_text_from_pdf(filepath)
    
    invoice_data = None
    
    if text:
        print(f"[2] Text extracted ({len(text)} chars). Routing to small LLM (qwen2.5:8b)...")
        invoice_data = extract_with_llm(text)
    else:
        print("[2] No parsable text found. Routing to Vision Model fallback (llama3.2-vision)...")
        invoice_data = extract_with_vision(filepath)
        
    if not invoice_data:
        print("Failed to extract invoice data.")
        return
        
    print("[3] Data successfully extracted. Validating math & exporting to Excel...")
    
    # Save Excel report
    export_to_excel(invoice_data, output_path)
    
    print("--- Done! ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Financial Analyst Agent")
    parser.add_argument("pdf_path", help="Path to the PDF file to analyze")
    parser.add_argument("--out", default="output.xlsx", help="Path for the output Excel file")
    
    args = parser.parse_args()
    process_pdf(args.pdf_path, args.out)
