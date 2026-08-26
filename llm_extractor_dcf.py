import ollama
from models_dcf import CompanyFinancials, DynamicScenarios
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

def generate_dynamic_scenarios(historical_data: list[CompanyFinancials]) -> DynamicScenarios:
    """
    Takes a sorted list of historical financials and prompts the LLM to generate 
    forward-looking growth rates based on historical CAGR and management commentary.
    """
    from models_dcf import DynamicScenarios
    
    if not historical_data:
        raise ValueError("No historical data provided.")
        
    # Build historical context
    context = "Historical Revenue Trend:\n"
    for data in historical_data:
        context += f"Year {data.year}: {data.income_statement.revenue}\n"
        
    # Aggregate MD&A
    mda_context = "Management Assumptions (MD&A):\n"
    for data in historical_data[-2:]: # Use last 2 years for most relevant commentary
        mda_context += f"Year {data.year}: {data.management_assumptions}\n"
        
    prompt = f"""
    You are an expert financial analyst. Based on the historical revenue data and management's forward-looking assumptions provided below, project the annual revenue growth rate for the next 5 years in three scenarios: Bear, Base, and Bull.
    
    {context}
    
    {mda_context}
    
    Provide your growth rate projections as floats (e.g., 0.05 for 5% growth).
    Also provide a brief insight_summary explaining your reasoning.
    Return ONLY valid JSON matching the exact schema provided. Do not add conversational text.
    """
    
    try:
        print("\nSending historical trends & MD&A to LLM for Dynamic Scenarios generation...")
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            format=DynamicScenarios.model_json_schema(),
            options={'temperature': 0.2} # Slight variance allowed for qualitative insight
        )
        
        result_json = response['message']['content']
        return DynamicScenarios.model_validate_json(result_json)
        
    except Exception as e:
        print(f"Error generating dynamic scenarios: {e}")
        # Fallback
        return DynamicScenarios(
            bear={"revenue_growth": 0.02},
            base={"revenue_growth": 0.05},
            bull={"revenue_growth": 0.08},
            insight_summary="Fallback to static rates due to error."
        )
