import ollama
import fitz  # PyMuPDF
from models import InvoiceModel

def extract_with_vision(filepath: str) -> InvoiceModel:
    """
    Fallback for scanned PDFs. Converts the first page to an image using PyMuPDF 
    (no poppler required) and uses a Vision Model to extract the structured JSON data.
    """
    try:
        # Open the PDF with PyMuPDF
        doc = fitz.open(filepath)
        if len(doc) == 0:
            return None
            
        page = doc[0]
        # Render page to an image pixmap
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x zoom for better OCR quality
        
        # Convert pixmap to PNG byte array
        img_bytes = pix.tobytes("png")
        doc.close()
        
        prompt = "You are an expert data extractor. Extract the invoice details from this image. Return ONLY valid JSON matching the schema. Pay close attention to numerical values."
        
        response = ollama.chat(
            model='llama3.2-vision',
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [img_bytes]
            }],
            format=InvoiceModel.model_json_schema()
        )
        
        result_json = response['message']['content']
        return InvoiceModel.model_validate_json(result_json)
        
    except Exception as e:
        print(f"Error extracting with Vision Model: {e}")
        return None
