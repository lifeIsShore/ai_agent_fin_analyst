import sys
from models_dcf import CompanyFinancials, IncomeStatement, BalanceSheet, CashFlowStatement, DynamicScenarios, ScenarioBase
from dcf_excel_exporter import export_dcf_to_excel

def get_dummy_financials(year: int, rev: float) -> CompanyFinancials:
    return CompanyFinancials(
        company_name="Friedrich Vorwerk",
        ticker="VH2.DE",
        year=year,
        income_statement=IncomeStatement(revenue=rev, cogs=0, sga=0, da=0, ebit=rev*0.15, interest_expense=0, taxes=0, net_income=0),
        balance_sheet=BalanceSheet(cash=0, current_assets=0, total_assets=0, current_liabilities=0, total_debt=0, total_liabilities=0, shareholders_equity=0),
        cash_flow=CashFlowStatement(operating_cash_flow=0, capex=rev*0.05),
        management_assumptions="Generated from previous batch run logs."
    )

hist_data = [
    get_dummy_financials(2020, 291791000.0),
    get_dummy_financials(2021, 279071000.0),
    get_dummy_financials(2022, 368161000.0),
    get_dummy_financials(2023, 373355.0),
    get_dummy_financials(2024, 498353.0),
    get_dummy_financials(2025, 1346879.0)
]

scenarios = DynamicScenarios(
    bear=ScenarioBase(revenue_growth=-0.123),
    base=ScenarioBase(revenue_growth=0.123),
    bull=ScenarioBase(revenue_growth=0.247),
    insight_summary="The Bear scenario assumes a significant decline in revenue growth, reflecting potential market challenges or operational issues. The Base scenario projects moderate growth based on the historical trend and management's assumptions of order backlog. The Bull scenario anticipates strong growth driven by the Service & Operations segment, aligning with the high value of the order backlog as of end 2024."
)

results = {
    "Bear": {"rev_growth": -0.123, "implied_price_pg": -257.94, "implied_price_mult": -5.73},
    "Base": {"rev_growth": 0.123, "implied_price_pg": -795.02, "implied_price_mult": 77.31},
    "Bull": {"rev_growth": 0.247, "implied_price_pg": -1295.35, "implied_price_mult": 173.84}
}

market_data = {"ticker": "VH2.DE", "market_cap": 800000000}

export_dcf_to_excel(hist_data, scenarios, market_data, 0.0826, 1000.0, results, "batch_dcf_output.xlsx")
print("Excel generated successfully!")
