# Analyst Consensus Agent (Design & Implementation Plan)

## 1. Goal & Responsibilities
The **Analyst Consensus Agent** is a standalone, lightweight data-fetching agent. Its primary purpose is to autonomously gather external Wall Street sentiment and price targets for a given stock ticker, and inject this data into the master database (`valuations_v2.db`). 

By separating this from the core DCF Engine, we achieve a robust Multi-Agent Architecture where the DCF Engine calculates intrinsic mathematical value, and the Analyst Agent captures extrinsic market sentiment. Later, our Machine Learning script will combine both datasets as predictive features.

## 2. Technology Stack
- **Python 3.10+** (Standalone script `analyst_agent.py`)
- **`yfinance`**: The fastest and most reliable API for fetching Yahoo Finance analyst data (requires zero authentication).
- **`sqlite3`**: To interface with our existing `valuations_v2.db`.
- **`pydantic`** (Optional): For strictly structuring the scraped data before saving it to the database, preventing schema corruption.

## 3. Database Schema Updates
We need a new table in `valuations_v2.db` to house this data. 

**Table Name:** `analyst_consensus`

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `ticker` | TEXT | The stock ticker (e.g., `VH2.DE`) |
| `date_fetched` | TEXT | Timestamp of when the data was scraped (ISO 8601) |
| `target_mean` | REAL | The average analyst price target |
| `target_median` | REAL | The median analyst price target |
| `target_high` | REAL | The highest analyst price target |
| `target_low` | REAL | The lowest analyst price target |
| `num_analysts` | INTEGER | The total number of analysts covering the stock |
| `recommendation` | TEXT | Consensus rating (e.g., "Buy", "Hold", "Strong Buy") |

## 4. Step-by-Step Workflow

### Step 4a: Initialization
The script is called via the terminal: `python analyst_agent.py VH2.DE`.
It connects to `valuations_v2.db` and ensures the `analyst_consensus` table exists, creating it if it doesn't.

### Step 4b: Data Fetching (The API Layer)
The script uses the `yfinance` library to query the ticker.
```python
import yfinance as yf

ticker = yf.Ticker("VH2.DE")
analyst_targets = ticker.info # Contains 'targetMeanPrice', 'targetHighPrice', etc.
recommendations = ticker.recommendations # Contains historical buy/sell ratings
```

### Step 4c: Fallback Web Scraping (Optional)
If Yahoo Finance fails or returns `None` (which occasionally happens for obscure EU stocks), the agent falls back to scraping MarketWatch or TradingView using `requests` and `BeautifulSoup4`.

### Step 4d: Database Injection
The agent packages the fetched variables into a SQL `INSERT` statement and commits the row to `valuations_v2.db`.

## 5. Directory Structure
When you create the new directory for this agent, you can organize it like this:

```text
ai_agent_fin_analyst/
│
├── core_dcf/                 <-- (Move the current DCF files here eventually)
│   ├── batch_dcf.py
│   ├── table_extractor.py
│   └── ...
│
├── analyst_agent/            <-- (The new directory you will create)
│   ├── analyst_agent.py      <-- (The main agent script)
│   ├── requirements.txt      <-- (yfinance, requests, bs4)
│   └── test_agent.py         <-- (A small script to test the API)
│
└── databases/
    └── valuations_v2.db      <-- (Shared database both agents talk to)
```

## 6. Open Questions for You

> [!IMPORTANT]
> 1. **Data Sources:** Are you okay with using Yahoo Finance as the primary data source via `yfinance`, or do you have a paid API key (like AlphaVantage, Finnhub, or Bloomberg) you'd prefer the agent to use?
> 2. **Execution Frequency:** Should this agent run automatically every time the DCF engine runs, or should it run on a weekly/monthly cron-job schedule to update the database?

Let me know if this architectural plan aligns with your vision!
