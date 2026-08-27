# AI Financial Analyst - Phase 3 Roadmap

With the DCF Engine now functioning with high accuracy (via Hybrid Regex/LLM processing) and outputting reliable enterprise valuations to both SQLite and Excel, the core foundation of the project is complete. 

The next overarching goal is **Scale and Prediction**. We need to take this engine, run it across hundreds of tickers automatically, and use the generated data to train a Machine Learning model.

## Step 1: Fully Automated Orchestration (The Ticker Pipeline)
Currently, the DCF pipeline is run manually by pointing `batch_dcf.py` to a local folder of PDFs. 
**Goal:** Build a master python orchestrator (`run_universe.py`) that:
1. Takes a list of tickers (e.g., `tickers.txt`).
2. Automatically calls an API (like Yahoo Finance or Edgar) to fetch the last 5 years of annual reports for each ticker.
3. Downloads the PDFs into dynamically created folders.
4. Spawns `batch_dcf.py` for each ticker sequentially.
5. Logs successes and failures to a master CSV.

## Step 2: Yahoo Finance Fallback Layer
Not all PDFs are perfectly parsable. Sometimes, companies publish scanned images instead of text PDFs, or format their tables in completely anomalous ways.
**Goal:** Implement a fallback in `table_extractor.py`:
1. If both Regex and the Sniper LLM fail to extract Revenue/Assets (or if the PDF is purely image-based), catch the error.
2. Automatically trigger a `yfinance` API call for that specific ticker and year.
3. Pull Revenue, EBIT, D&A, CapEx, and Net Debt directly from Yahoo Finance's historical data to ensure the DCF engine never crashes and always completes its valuation.

## Step 3: Config-Driven Regex Mappings
The `table_extractor.py` currently has hardcoded German/English strings (e.g., `'liabilities to banks'`, `'betriebsergebnis'`). 
**Goal:** Externalize this logic.
1. Create a `regex_config.json` file containing arrays of matching strings for every financial metric.
2. Update `table_extractor.py` to iterate over this JSON.
3. This allows non-technical users to easily add new edge-case labels (e.g., "Short-term borrowings") without editing Python code, making the pipeline vastly more robust against diverse accounting standards.

## Step 4: Machine Learning Price Prediction Layer
We now have a rich SQLite database (`valuations_v2.db`) containing multi-dimensional features (Historical CAGRs, EBIT Margins, Management Sentiment Scores, Reinvestment Rates).
**Goal:** Build an ML model to predict stock prices.
1. Create `ml_predictor.py` using `xgboost` or `scikit-learn`.
2. Extract all historical KPIs from `valuations_v2.db` as input features (X).
3. Use historical stock price data (from Yahoo Finance) as the target variable (Y).
4. Train a Random Forest or XGBoost Regressor to predict the "Fair Value" of the stock based on these features.
5. Output these ML predictions to the "Projections & ML" tab in the Excel exports, allowing users to compare the DCF Calculated Value vs. the ML Predicted Value.

## Step 5: Self-Correcting LLM Loop (Hallucination Prevention)
Even with strict decimal prompts, the LLM in `llm_extractor_dcf.py` can occasionally hallucinate JSON formats, causing Pydantic to crash.
**Goal:** Add a programmatic retry loop.
1. If Pydantic throws a `ValidationError` when parsing the LLM's growth rate projections, catch the error.
2. Send the exact Error Message back to the LLM in a new prompt: *"You output invalid JSON. Fix this specific error: [Error Message]"*.
3. Allow up to 3 retries before defaulting to static conservative growth rates, ensuring 100% pipeline uptime.

## Step 6: Analyst Consensus Agent (Multi-Agent Architecture)
To further enrich the ML prediction model, we will build a completely separate agent script.
**Goal:** Create `analyst_agent.py` to scour the web/APIs for analyst targets.
1. Build a standalone script that runs parallel to the DCF engine.
2. For each ticker, it uses a financial API (like Yahoo Finance) or web search to scrape current Wall Street Analyst Targets (Mean, Median, High, Low) and Buy/Hold/Sell ratings.
3. It saves these consensus metrics into a new table in `valuations_v2.db`.
4. The ML Model (Step 4) will then use both the internal DCF calculations AND the external Analyst Consensus as combined features to predict the true future stock price. Keeping this as a separate agent prevents bloating the core DCF engine!
