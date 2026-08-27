from market_data import get_market_data
from dcf_engine import project_financials, calculate_wacc
from models_dcf import CompanyFinancials, IncomeStatement, BalanceSheet, CashFlowStatement, DynamicScenarios

md = get_market_data('VH2.DE')
wacc = calculate_wacc(md)

# Mocking the 2025 extracted data
# According to the logs, Revenue was 704326.
# Let's see what the other fields were. We can just query the SQLite db!
import sqlite3
conn = sqlite3.connect('valuations.db')
c = conn.cursor()
c.execute("SELECT * FROM valuations_v2")
rows = c.fetchall()
for row in rows:
    print(row)
