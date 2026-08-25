from pydantic import BaseModel, Field
from typing import List, Optional

class RawLineItem(BaseModel):
    name: str = Field(description="The exact name of the line item as reported by the company.")
    value: float = Field(description="The reported value.")

class IncomeStatement(BaseModel):
    revenue: float = Field(description="Total revenue or sales.")
    cogs: float = Field(description="Cost of goods sold or cost of revenue.")
    sga: float = Field(description="Selling, general, and administrative expenses.")
    da: float = Field(description="Depreciation and amortization.")
    ebit: float = Field(description="Operating income or EBIT.")
    interest_expense: float = Field(description="Interest expense.")
    taxes: float = Field(description="Income tax expense.")
    net_income: float = Field(description="Net income.")
    raw_items: List[RawLineItem] = Field(description="List of all raw line items found in the income statement for transparency.")

class BalanceSheet(BaseModel):
    cash: float = Field(description="Cash and cash equivalents.")
    current_assets: float = Field(description="Total current assets.")
    total_assets: float = Field(description="Total assets.")
    current_liabilities: float = Field(description="Total current liabilities.")
    total_debt: float = Field(description="Total short-term and long-term debt.")
    total_liabilities: float = Field(description="Total liabilities.")
    shareholders_equity: float = Field(description="Total shareholders' equity.")
    raw_items: List[RawLineItem] = Field(description="List of all raw line items found in the balance sheet for transparency.")

class CashFlowStatement(BaseModel):
    operating_cash_flow: float = Field(description="Net cash provided by operating activities.")
    capex: float = Field(description="Capital expenditures (purchases of property, plant, and equipment). Usually a negative number, convert to positive.")
    raw_items: List[RawLineItem] = Field(description="List of all raw line items found in the cash flow statement for transparency.")

class CompanyFinancials(BaseModel):
    company_name: str = Field(description="Name of the company.")
    ticker: str = Field(description="Stock ticker symbol if available, else 'PRIVATE'.")
    year: int = Field(description="The fiscal year of this report.")
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow: CashFlowStatement
    management_assumptions: str = Field(description="Any forward-looking commentary on expected growth, margins, or capex.")
