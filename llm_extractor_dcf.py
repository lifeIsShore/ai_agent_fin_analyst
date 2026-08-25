import ollama
from models_dcf import CompanyFinancials
import json

def extract_financials_with_llm(text: str) -> CompanyFinancials:
    """
    Uses Qwen2.5 to parse the 3 financial statements into a strict Pydantic JSON schema.
    Applies edge case rules for restatements and scale.
    """
    prompt = f"""
    You are an expert financial data extractor. Extract the historical financial data from the provided text for the most recent year.
    Return ONLY valid JSON matching the exact schema provided. Do not add any conversational text.
    
    CRITICAL RULES:
    1. If multiple values exist for the same metric across different years, ALWAYS extract the value for the most recent year only.
    2. Ensure negative numbers (often in parentheses like (500)) are extracted as negative floats (-500.0).
    3. BEWARE OF EUROPEAN FORMATTING: If a number is written as "1.500,00", it means 1500.00. Periods are thousands separators, commas are decimals. Always return a standard Python float.
    
    TEXT TO PARSE:
    {text}
    """
    
    try:
        print("Sending to LLM for extraction (this may take 20-40 seconds)...")
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            format=CompanyFinancials.model_json_schema(),
            options={'temperature': 0.0} # Deterministic
        )
        
        result_json = response['message']['content']
        return CompanyFinancials.model_validate_json(result_json)
        
    except Exception as e:
        print(f"Error extracting financials with LLM: {e}")
        return None
