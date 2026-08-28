from pydantic import BaseModel, Field
from typing import List, Optional

class IncomeStatement(BaseModel):
    revenue: float = Field(description="Total revenue or sales.")
    cogs: float = Field(description="Cost of goods sold or cost of revenue.")
    sga: float = Field(description="Selling, general, and administrative expenses.")
    da: float = Field(description="Depreciation and amortization.")
    ebit: float = Field(description="Operating income or EBIT.")
    interest_expense: float = Field(description="Interest expense.")
    taxes: float = Field(description="Income tax expense.")
    net_income: float = Field(description="Net income.")

class BalanceSheet(BaseModel):
    cash: float = Field(description="Cash and cash equivalents.")
    current_assets: float = Field(description="Total current assets.")
    total_assets: float = Field(description="Total assets.")
    current_liabilities: float = Field(description="Total current liabilities.")
    total_debt: float = Field(description="Total short-term and long-term debt.")
    total_liabilities: float = Field(description="Total liabilities.")
    shareholders_equity: float = Field(description="Total shareholders' equity.")

class CashFlowStatement(BaseModel):
    operating_cash_flow: float = Field(description="Net cash provided by operating activities.")
    capex: float = Field(description="Capital expenditures (purchases of property, plant, and equipment). Usually a negative number, convert to positive.")

class QualitativeScores(BaseModel):
    confidence_score: int = Field(description="Management confidence score (0-100). Higher is more optimistic.")
    risk_score: int = Field(description="Risk and transparency score (0-100). Higher means safer and more transparent.")
    governance_score: int = Field(description="Governance and ESG score (0-100). Higher means better governance.")
    rationale: str = Field(description="A short summary explaining why these scores were given based on MD&A and Risk Factors.")

class CompanyFinancials(BaseModel):
    company_name: str = Field(description="Name of the company.")
    ticker: str = Field(description="Stock ticker symbol if available, else 'PRIVATE'.")
    year: int = Field(description="The fiscal year of this report.")
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow: CashFlowStatement
    management_assumptions: str = Field(description="Any forward-looking commentary on expected growth, margins, or capex.")
    qualitative_scores: Optional[QualitativeScores] = Field(default=None, description="Qualitative macro scores extracted from MD&A and Risk Factors.")

class ScenarioBase(BaseModel):
    revenue_growth: float = Field(description="Projected annual revenue growth rate (e.g., 0.05 for 5%). Must be between -1.0 and 5.0.", ge=-1.0, le=5.0)

class DynamicScenarios(BaseModel):
    bear: ScenarioBase = Field(description="Bear case scenario assumptions")
    base: ScenarioBase = Field(description="Base case scenario assumptions")
    bull: ScenarioBase = Field(description="Bull case scenario assumptions")
    insight_summary: str = Field(description="A brief paragraph explaining the rationale behind the selected growth rates based on historical data and management commentary.")
    management_confidence_score: int = Field(description="A score from 1 to 10 evaluating the overall optimism and confidence of management based on the MD&A text. 1 is extremely pessimistic/struggling, 10 is extremely optimistic/booming.")
    confidence_rationale: str = Field(description="A short 1-sentence explanation of why that specific management confidence score was given.")
