import pandas as pd
import numpy as np
from models_dcf import CompanyFinancials

def calculate_wacc(market_data: dict) -> float:
    """
    Calculates Weighted Average Cost of Capital (WACC).
    Uses CAPM for Cost of Equity.
    """
    risk_free_rate = market_data.get('risk_free_rate', 0.04)
    beta = market_data.get('beta', 1.0)
    market_risk_premium = 0.055 # Standard ERP
    
    # Cost of Equity via CAPM
    cost_of_equity = risk_free_rate + (beta * market_risk_premium)
    
    # Simplified Cost of Debt (pre-tax) assuming 5%
    cost_of_debt = 0.05
    tax_rate = 0.25 # Assumed average corporate tax rate
    after_tax_cod = cost_of_debt * (1 - tax_rate)
    
    # Simplified capital structure (assumes 80% equity, 20% debt if unknown)
    # In a full model, we'd use market cap / (market cap + total debt)
    weight_equity = 0.80
    weight_debt = 0.20
    
    wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cod)
    return wacc

def project_financials(historical: CompanyFinancials, wacc: float, market_data: dict):
    """
    Projects financials 5 years into the future using Base, Bull, and Bear scenarios.
    Returns a dictionary of projections and valuation metrics.
    """
    # Historical base year metrics (assumed clean from LLM extraction)
    # Applying generic scale fix if values look too small compared to market cap.
    scale = 1.0
    if market_data['market_cap'] > 0 and historical.income_statement.revenue > 0:
        if market_data['market_cap'] / historical.income_statement.revenue > 1000:
            scale = 1000000.0 # Revenue was likely reported in millions
            
    base_rev = historical.income_statement.revenue * scale
    base_ebit = historical.income_statement.ebit * scale
    base_da = historical.income_statement.da * scale
    # Capex is usually reported negative in cash flow, ensure it's positive for formulas
    base_capex = abs(historical.cash_flow.capex) * scale
    
    # Base margins
    ebit_margin = base_ebit / base_rev if base_rev > 0 else 0.15
    da_margin = base_da / base_rev if base_rev > 0 else 0.05
    capex_margin = base_capex / base_rev if base_rev > 0 else 0.05
    tax_rate = 0.25
    
    # Scenarios (Revenue Growth rates)
    scenarios = {
        "Bear": 0.02,
        "Base": 0.05,
        "Bull": 0.08
    }
    
    results = {}
    
    for scenario_name, growth_rate in scenarios.items():
        projected_rev = [base_rev * (1 + growth_rate)**i for i in range(1, 6)]
        projected_ebit = [rev * ebit_margin for rev in projected_rev]
        projected_da = [rev * da_margin for rev in projected_rev]
        projected_capex = [rev * capex_margin for rev in projected_rev]
        
        # Unlevered Free Cash Flow (UFCF) = EBIT*(1-t) + D&A - Capex - Change in NWC
        # Assuming Change in NWC is 0 for simplicity in MVP
        ufcf = []
        for i in range(5):
            nopat = projected_ebit[i] * (1 - tax_rate)
            fcf = nopat + projected_da[i] - projected_capex[i]
            ufcf.append(fcf)
            
        # Terminal Value - Perpetuity Growth
        perpetuity_growth_rate = 0.02
        tv_pg = (ufcf[-1] * (1 + perpetuity_growth_rate)) / (wacc - perpetuity_growth_rate)
        
        # Terminal Value - Exit Multiple (EV/EBITDA of 10x)
        # EBITDA = EBIT + D&A
        ebitda_year5 = projected_ebit[-1] + projected_da[-1]
        tv_mult = ebitda_year5 * 10.0
        
        # Discounting
        discount_factors = [1 / ((1 + wacc)**i) for i in range(1, 6)]
        pv_ufcf = sum(ufcf[i] * discount_factors[i] for i in range(5))
        
        pv_tv_pg = tv_pg * discount_factors[-1]
        pv_tv_mult = tv_mult * discount_factors[-1]
        
        ev_pg = pv_ufcf + pv_tv_pg
        ev_mult = pv_ufcf + pv_tv_mult
        
        # Equity Value = EV + Cash - Debt
        net_debt = (historical.balance_sheet.total_debt - historical.balance_sheet.cash) * scale
        eq_val_pg = ev_pg - net_debt
        eq_val_mult = ev_mult - net_debt
        
        shares = market_data.get('shares_outstanding', 1)
        if shares == 0: shares = 1
        
        price_pg = eq_val_pg / shares
        price_mult = eq_val_mult / shares
        
        results[scenario_name] = {
            "rev_growth": growth_rate,
            "projected_ufcf": ufcf,
            "tv_pg": tv_pg,
            "implied_price_pg": price_pg,
            "tv_mult": tv_mult,
            "implied_price_mult": price_mult
        }
        
    return results, wacc, scale
