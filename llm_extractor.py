import ollama
from models import InvoiceModel
import json

def extract_with_llm(text: str) -> InvoiceModel:
    """
    Uses a small quantized LLM (qwen2.5) to parse text into a structured JSON schema.
    """
    prompt = f"""
    You are an expert financial data extractor. Extract the invoice details from the following text.
    Return ONLY valid JSON matching the schema. Do not add any conversational text.
    
    TEXT:
    {text}
    """
    
    try:
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            format=InvoiceModel.model_json_schema()
        )
        
        # Parse the JSON string back into our Pydantic model
        result_json = response['message']['content']
        return InvoiceModel.model_validate_json(result_json)
        
    except Exception as e:
        print(f"Error extracting with LLM: {e}")
        return None
