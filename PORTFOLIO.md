# Business Technologist Portfolio

## Positioning Statement
> **"I am a Business Technologist who bridges the gap between enterprise problems and AI-driven software execution."**

My competitive advantage is not just knowing how to write Python code or build AI pipelines. It comes from my ability to look at an entire business ecosystem and say:
*"Here is the business problem → here is the process bottleneck → here is the scattered data → here is where an LLM or Agent can automate the logic → here is how we integrate it via APIs → here is the ROI."*

## Target Roles
- **AI Product Manager**: Leading the strategic vision and technical execution of AI features within enterprise software.
- **Enterprise AI Strategist / Consultant**: Advising and implementing digital transformation for companies looking to automate workflows with LLMs and deterministic code.
- **Digital Transformation Lead**: Identifying legacy bottlenecks and architecting modern, data-driven systems to replace them.

---

# Project 1: Autonomous AI Hedge Fund Analyst
**Status:** Completed | **Tech Stack:** Python, SQLite, Ollama (Local LLM), DuckDuckGo Search, Yahoo Finance API, statsmodels, pdfplumber

### The Business Problem
Financial analysts spend hundreds of hours manually downloading Annual Reports (10-Ks), scrolling through 200-page PDFs to find 4 specific numbers (Revenue, EBIT, Assets, Cash), reading subjective "Management Discussion" sections, and Googling Wall Street consensus estimates just to build a single Discounted Cash Flow (DCF) model. This is slow, error-prone, and unscalable.

### The Solution
An end-to-end, autonomous AI pipeline that completely replaces the junior analyst workflow. Given just a list of stock tickers, the system:
1. **Orchestrates** web scraping to automatically hunt down and download the latest Annual Report PDFs.
2. **Deterministically Extracts** exact financial tables using a robust, externalized regex configuration file.
3. **Qualitatively Analyzes** the complex text of the "Risk Factors" and "Management Discussions" using a local LLM, mathematically grading the CEO's confidence and governance risk.
4. **Calculates** a complete Dynamic DCF model projecting future cash flows based on those LLM insights.
5. **Deploys an AI Agent** to autonomously search the web for Wall Street consensus target prices, falling back to the Yahoo Finance API if blocked by bot-protection.
6. **Statistically Explains** the market premium using an OLS Regression Engine (Explainable AI) based on the combined quantitative and qualitative data.

### System Architecture
```text
User Input (Ticker List)
       ↓
[Orchestrator Agent] ----(Google Search)----> Corporate IR Sites
       ↓
   PDF Documents
       ↓
[Deterministic Regex Extractor] --------(Fails?)-------> [YFinance API Fallback]
       ↓
  Financial KPIs (Revenue, EBIT)
       ↓
[LLM Evaluator (Ollama)] <---(Reads MD&A Text)
       ↓
  Qualitative Scores (Risk, Confidence)
       ↓
[DCF Math Engine] <---(Market Data API)
       ↓
[Web Search Agent] ---> (DuckDuckGo) ---> Wall Street Consensus
       ↓
[SQLite Database: valuations_v2]
       ↓
[Explainable AI: OLS Regression] ---> Output: Market Premium Drivers
```

---

# Project 2: Automated Invoice Data Extractor
**Status:** Completed | **Tech Stack:** Python, OCR, Document Intelligence

### The Business Problem
Accounting departments are bogged down by manual data entry, processing hundreds of unstructured PDF and image-based invoices from various vendors. This creates bottlenecks in accounts payable and increases the risk of human error.

### The Solution
An automated pipeline that ingests raw invoice files, applies Optical Character Recognition (OCR), and uses intelligent parsing to extract structured data (Vendor Name, Total Amount, Tax, Due Date). 
*(Note: Expand this section with architecture details from the previous project).*

---

# Project 3: "H-Budget" Personal Finance Engine
**Status:** In Progress (70%) | **Tech Stack:** React Native, Expo, TypeScript, TailwindCSS, SQLite

### The Business Problem
Most mobile expense trackers are clunky, require too many taps to log a simple transaction, and lack deep categorizational insights (tracking by vendor, category, *and* overarching purpose).

### The Solution
A lightning-fast, mobile-first iOS/Android application built with React Native. It features a frictionless "Quick-Add" interface, a highly responsive swipeable ledger, and a robust local SQLite data layer. 
*(Note: Expand this section upon backend SQLite completion).*
