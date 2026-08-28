import sqlite3
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import warnings

# Suppress yfinance warnings for cleaner output
warnings.filterwarnings('ignore')

def load_data_from_db(db_path="valuations.db") -> pd.DataFrame:
    """Loads valuation data and qualitative scores from SQLite."""
    conn = sqlite3.connect(db_path)
    
    # Pragma check for consensus_target to ensure it exists
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(valuations_v2)")
    columns = [col[1] for col in cursor.fetchall()]
    
    consensus_col = ", consensus_target" if "consensus_target" in columns else ", 0 as consensus_target"
    
    query = f"""
    SELECT ticker, date, wacc, base_target, 
           confidence_score, risk_score, governance_score,
           latest_ebit_margin, latest_net_margin, latest_roa
           {consensus_col}
    FROM valuations_v2
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_current_prices(tickers: list) -> dict:
    """Fetches real-time market prices for a list of tickers using Yahoo Finance."""
    print(f"[Market Data] Fetching current prices for {len(tickers)} tickers...")
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            prices[ticker] = info.get("currentPrice", 0.0)
        except Exception as e:
            print(f"  -> Error fetching data for {ticker}: {e}")
            prices[ticker] = 0.0
    return prices

def run_regression_engine():
    print("\n--- STATISTICAL REGRESSION ENGINE (OLS) ---")
    
    # 1. Load Data
    df = load_data_from_db()
    if df.empty:
        print("[Error] No data found in valuations_v2 table.")
        return

    print(f"[Data Load] Successfully loaded {len(df)} records from database.")
    
    # 2. Fetch current prices
    unique_tickers = df['ticker'].unique().tolist()
    current_prices = fetch_current_prices(unique_tickers)
    
    # Map prices back to DataFrame
    df['current_price'] = df['ticker'].map(current_prices)
    
    # Filter out missing data
    df = df[df['current_price'] > 0]
    df = df[df['base_target'] > 0]
    
    if len(df) < 5:
        print("\n[Warning] Not enough data points to run a mathematically valid regression (Need > 5).")
        print("          Run the Orchestration Script on more companies to populate the database.")
        print(f"          Current valid rows: {len(df)}")
        print("\n[Preview of Data]:")
        print(df[['ticker', 'base_target', 'current_price', 'confidence_score']].head())
        return

    # 3. Calculate Target Variable (Market Premium to DCF)
    # A value of 1.20 means the market prices the stock at a 20% premium to our DCF.
    df['market_premium'] = df['current_price'] / df['base_target']
    
    # Calculate Consensus Spread (How far Wall Street is from our DCF)
    # e.g. if consensus is 150 and our DCF is 100, spread is 0.50 (+50%)
    df['consensus_spread'] = (df['consensus_target'] / df['base_target']) - 1
    # Handle cases where consensus_target is 0 (missing)
    df.loc[df['consensus_target'] == 0, 'consensus_spread'] = 0
    
    # 4. Prepare Regression Matrix
    print("\n[Regression] Building OLS Design Matrix...")
    
    # Fill missing qualitative scores with 0
    df['confidence_score'] = df['confidence_score'].fillna(0)
    df['risk_score'] = df['risk_score'].fillna(0)
    df['governance_score'] = df['governance_score'].fillna(0)
    
    df = df.dropna(subset=['latest_ebit_margin', 'latest_roa'])
    
    # Dependent variable (Y)
    y = df['market_premium']
    
    # Independent variables (X)
    X = df[['confidence_score', 'risk_score', 'governance_score', 'latest_ebit_margin', 'consensus_spread']]
    
    # Add constant (intercept) to the model
    X = sm.add_constant(X)
    
    # 5. Fit the Model
    try:
        model = sm.OLS(y, X).fit()
        
        # 6. Output Insights
        print("\n==============================================================================")
        print("                        HEDGE FUND STATISTICAL BRIEFING                       ")
        print("==============================================================================")
        print(f"Model: Multiple Linear Regression (OLS)")
        print(f"Observations: {len(df)}")
        print(f"R-squared: {model.rsquared:.4f} (The model explains {model.rsquared*100:.1f}% of the variance in Market Premium)")
        print(f"Adjusted R-squared: {model.rsquared_adj:.4f}")
        print("------------------------------------------------------------------------------")
        print("Coefficients & P-Values:")
        print(" (P-value < 0.05 indicates statistical significance)")
        
        for index, row in model.params.items():
            p_val = model.pvalues[index]
            significance = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.1 else ""
            print(f"  {index.ljust(20)} : {row:>8.4f}   (p-val: {p_val:.4f}) {significance}")
            
        print("==============================================================================\n")
        
    except Exception as e:
        print(f"\n[Error] Failed to fit OLS model: {e}")

if __name__ == "__main__":
    run_regression_engine()
