import json
import ollama
from models_dcf import QualitativeScores

def analyze_qualitative_factors(mda_text: str, risk_text: str) -> QualitativeScores:
    """
    Analyzes the MD&A and Risk Factors text to produce macro qualitative scores.
    Implements a missing data penalty if the text is empty or too short.
    """
    # 1. Missing Data Penalty
    if len(mda_text.strip()) < 200 or len(risk_text.strip()) < 200:
        print("  -> [Qualitative Analyzer] Missing data detected! Applying penalty scores.")
        return QualitativeScores(
            confidence_score=30,
            risk_score=30,
            governance_score=30,
            rationale="Automated penalty: The MD&A or Risk Factors sections were missing or too sparse to analyze."
        )

    # 2. Prepare Prompt
    prompt = f"""
    You are an expert financial analyst. Analyze the following excerpts from a company's Annual Report (MD&A and Risk Factors).
    
    Provide scores from 0-100 on three dimensions:
    1. confidence_score: How optimistic and confident is management about future growth and margins? (High = very confident)
    2. risk_score: How safe and transparent is the company based on its risk disclosures? (High = very safe, low risk)
    3. governance_score: Based on the tone and detail, how strong is the corporate governance and ESG focus? (High = strong governance)
    
    EXCERPT - MD&A:
    {mda_text[:6000]} # Limit to ~6k chars to avoid token overflow
    
    EXCERPT - RISK FACTORS:
    {risk_text[:6000]}
    
    Return the result exactly matching the JSON schema provided.
    """

    print("  -> [Qualitative Analyzer] Calling Local LLM (qwen2.5) for scoring...")
    
    try:
        response = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            format=QualitativeScores.model_json_schema(),
            options={'temperature': 0.1}
        )
        
        result_dict = json.loads(response['message']['content'])
        scores = QualitativeScores(**result_dict)
        print(f"  -> [Qualitative Analyzer] SUCCESS! Confidence: {scores.confidence_score}, Risk: {scores.risk_score}")
        return scores
        
    except Exception as e:
        print(f"  -> [Qualitative Analyzer] LLM Scoring failed: {e}")
        # Default fallback if LLM crashes
        return QualitativeScores(
            confidence_score=50,
            risk_score=50,
            governance_score=50,
            rationale=f"LLM processing failed: {e}"
        )
