import yfinance as yf

def get_market_data(ticker_symbol: str) -> dict:
    """
    Pulls live market data for WACC and Target Price calculations.
    Returns Beta, Current Price, Shares Outstanding, and a proxy Risk-Free Rate.
    """
    print(f"Pulling live market data for {ticker_symbol} via Yahoo Finance...")
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    
    # 10-Year Treasury Yield proxy for Risk-Free Rate (^TNX)
    try:
        tnx = yf.Ticker("^TNX")
        risk_free_rate = tnx.info.get('previousClose', 4.0) / 100.0
    except:
        risk_free_rate = 0.04  # Fallback to 4%
        
    data = {
        "ticker": ticker_symbol,
        "current_price": info.get("currentPrice", 0.0),
        "beta": info.get("beta", 1.0),
        "shares_outstanding": info.get("sharesOutstanding", 0),
        "risk_free_rate": risk_free_rate,
        "market_cap": info.get("marketCap", 0)
    }
    
    return data

if __name__ == "__main__":
    # Quick test
    print(get_market_data("AAPL"))
