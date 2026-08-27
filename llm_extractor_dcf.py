import ollama
from models_dcf import CompanyFinancials, DynamicScenarios
import json

import fitz

def fallback_extract_with_llm(text: str, year: int) -> CompanyFinancials:
    """
    Sniper LLM Fallback: Used when the deterministic Python regex fails.
    Takes ONLY the exact text of the 3 financial statement pages and extracts the data.
    """
    prompt = f"""
    You are an expert financial data extractor. I am providing you with the exact raw text from 3 pages of an annual report containing the Income Statement, Balance Sheet, and Cash Flow Statement.
    Extract the financial data for the most recent year (which is usually the first column of numbers).
    
    CRITICAL RULES:
    1. Revenue and Total Assets MUST ALWAYS be positive numbers. Never return negative revenue. If you see a dash before revenue, it is just formatting.
    2. If a number is negative (e.g. in parentheses like (500) or -500), extract it as -500.0 (except for Revenue and Assets).
    3. LOOK AT THE TABLE HEADERS. If it says 'in kEUR', 'in TEUR', or 'in thousands', you MUST multiply every single number by 1000 before returning it. 
       If it says 'in millions', multiply by 1,000,000.
       If it is in absolute units, do not multiply.
    4. Return ONLY valid JSON matching the schema provided.
    
    TEXT:
    {text}
    """
    
    print(f"    -> [Sniper LLM] Regex failed. Triggering LLM fallback extraction for Year {year}...")
    try:
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            format=CompanyFinancials.model_json_schema(),
            options={'temperature': 0.0}
        )
        
        result_json = response['message']['content']
        data = CompanyFinancials.model_validate_json(result_json)
        data.year = year
        return data
    except Exception as e:
        print(f"    -> [Sniper LLM] Failed: {e}")
        return None

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
    hist_summary = []
    for i, data in enumerate(historical_data):
        context += f"Year {data.year}: {data.income_statement.revenue}\n"
        
        # Only include heavy MD&A text for the last 2 years to save RAM/Context
        mda_snippet = data.management_assumptions if i >= len(historical_data) - 2 else "Archived."
        
        hist_summary.append({
            "year": data.year,
            "revenue": data.income_statement.revenue,
            "management_assumptions": mda_snippet
        })
        
    prompt = f"""
    You are an expert financial analyst. Analyze the following historical revenue data and management MD&A text.
    Your task is to generate realistic revenue growth rates for a Bear, Base, and Bull scenario for the next 5 years.
    MUST FORMAT AS DECIMALS: 5% must be written as 0.05. -10% must be written as -0.10. Do not use whole numbers.
    
    Additionally, analyze the tone of the management's text and provide a 'management_confidence_score' from 1 to 10 (1 = extremely pessimistic/distressed, 10 = extremely confident/booming) and a short 1-sentence 'confidence_rationale'.
    
    Return ONLY a valid JSON object matching the requested schema.
    
    HISTORICAL DATA & MANAGEMENT TEXT:
    {json.dumps(hist_summary, indent=2)}
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
            insight_summary="Fallback to static rates due to error.",
            management_confidence_score=5,
            confidence_rationale="Failed to parse LLM insight."
        )
