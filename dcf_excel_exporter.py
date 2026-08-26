import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from typing import List
from models_dcf import CompanyFinancials, DynamicScenarios

def export_dcf_to_excel(
    historical_data: List[CompanyFinancials], 
    dynamic_scenarios: DynamicScenarios,
    market_data: dict,
    wacc: float,
    scale: float,
    results: dict,
    output_filepath: str = "dcf_output.xlsx"
):
    """
    Exports the DCF historical data and AI-generated valuations into a neat Excel file.
    """
    wb = openpyxl.Workbook()
    
    # --- Sheet 1: Valuation Results ---
    ws_val = wb.active
    ws_val.title = "Valuation Summary"
    
    ws_val.cell(row=1, column=1, value="DCF Valuation Summary").font = Font(bold=True, size=14)
    
    ws_val.cell(row=3, column=1, value="Ticker:").font = Font(bold=True)
    ws_val.cell(row=3, column=2, value=market_data.get('ticker', 'N/A'))
    
    ws_val.cell(row=4, column=1, value="WACC:").font = Font(bold=True)
    ws_val.cell(row=4, column=2, value=f"{wacc:.2%}")
    
    ws_val.cell(row=5, column=1, value="Assumed Scale Factor:").font = Font(bold=True)
    ws_val.cell(row=5, column=2, value=scale)
    
    row_idx = 7
    for scenario_name, data in results.items():
        ws_val.cell(row=row_idx, column=1, value=f"{scenario_name} Scenario").font = Font(bold=True, color="FFFFFF")
        ws_val.cell(row=row_idx, column=1).fill = PatternFill(start_color="4F81BD", fill_type="solid")
        
        ws_val.cell(row=row_idx+1, column=1, value="Assumed Revenue Growth")
        ws_val.cell(row=row_idx+1, column=2, value=f"{data['rev_growth']:.2%}")
        
        ws_val.cell(row=row_idx+2, column=1, value="Target Price (Perp. Growth)")
        ws_val.cell(row=row_idx+2, column=2, value=data['implied_price_pg']).number_format = '#,##0.00'
        
        ws_val.cell(row=row_idx+3, column=1, value="Target Price (Exit Multiple)")
        ws_val.cell(row=row_idx+3, column=2, value=data['implied_price_mult']).number_format = '#,##0.00'
        
        row_idx += 5
        
    ws_val.cell(row=row_idx, column=1, value="AI Insights Summary").font = Font(bold=True)
    ws_val.cell(row=row_idx+1, column=1, value=dynamic_scenarios.insight_summary)
    ws_val.column_dimensions['A'].width = 35
    ws_val.column_dimensions['B'].width = 20
    
    # --- Sheet 2: Historical Financials ---
    ws_hist = wb.create_sheet("Historical Financials")
    
    headers = ["Metric"] + [f"Year {d.year}" for d in historical_data]
    for col_num, header in enumerate(headers, 1):
        cell = ws_hist.cell(row=1, column=col_num, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F81BD", fill_type="solid")
        
    metrics = [
        ("Revenue", lambda d: d.income_statement.revenue),
        ("EBIT", lambda d: d.income_statement.ebit),
        ("D&A", lambda d: d.income_statement.da),
        ("Net Income", lambda d: d.income_statement.net_income),
        ("Total Assets", lambda d: d.balance_sheet.total_assets),
        ("Total Debt", lambda d: d.balance_sheet.total_debt),
        ("Cash", lambda d: d.balance_sheet.cash),
        ("Operating Cash Flow", lambda d: d.cash_flow.operating_cash_flow),
        ("CapEx", lambda d: d.cash_flow.capex)
    ]
    
    for row_num, (metric_name, getter) in enumerate(metrics, 2):
        ws_hist.cell(row=row_num, column=1, value=metric_name).font = Font(bold=True)
        for col_num, data in enumerate(historical_data, 2):
            val = getter(data)
            ws_hist.cell(row=row_num, column=col_num, value=val).number_format = '#,##0'
            
    ws_hist.column_dimensions['A'].width = 25
    for i in range(2, len(headers) + 1):
        ws_hist.column_dimensions[openpyxl.utils.get_column_letter(i)].width = 15

    wb.save(output_filepath)
    print(f"Valuation results exported to {output_filepath}")
