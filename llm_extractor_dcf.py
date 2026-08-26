import ollama
from models_dcf import CompanyFinancials, DynamicScenarios
import json

import fitz

def extract_mda_with_llm(filepath: str) -> str:
    """
    Extracts the Management Discussion & Analysis (MD&A) forward-looking 
    statements using the LLM from the first 20 pages of the report.
    """
    try:
        doc = fitz.open(filepath)
        mda_text = ""
        # Grab first 20 pages (usually contains letter to shareholders and management report)
        for i in range(min(20, len(doc))):
            mda_text += doc[i].get_text("text") + "\n"
        doc.close()
        
        # Truncate to save context window if it's too massive
        mda_text = mda_text[:12000]
        
        prompt = f"""
        You are a financial analyst. Read the following excerpts from the beginning of an Annual Report.
        Extract any forward-looking management assumptions regarding future revenue growth, margins, order backlog, or market conditions.
        Return a single paragraph summarizing their outlook. If none is found, return "No forward-looking assumptions provided."
        
        TEXT:
        {mda_text}
        """
        
        print(f"  -> [LLM] Extracting MD&A insights from {filepath}...")
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1}
        )
        
        return response['message']['content'].strip()
        
    except Exception as e:
        print(f"Error extracting MD&A with LLM: {e}")
        return "Error extracting assumptions."

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
