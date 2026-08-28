# Progress Tracker

Update this as you go. This is what you (or an agent picking up this project) should read first to know where things stand.

## Current phase
**Phase 1 — First project**

## Phase checklist

### Phase 0 — Setup
- [x] Read `ROADMAP.md` fully
- [x] Pick Project 1 from `PROJECTS.md`
- [x] Set up dev environment (Python, Git, editor)

### Phase 1 — First project (Layer 1 + 2 focus)
- [x] Scoped the problem in one paragraph
- [x] Built v1
- [x] Filled in `ARCHITECTURE.md` entry for it
- [ ] Showed it to one real person
- [ ] Wrote the one-page business case

### Phase 2 — Second project (add Layer 3: enterprise systems)
- [x] Chosen project: **Advanced Multi-Year DCF Insight Engine**
- [x] Built v1 with hybrid LLM-Regex architecture, SQLite Database, and deterministic Table Extractors
- [x] Excel generation via OpenPyXL for DCF projection tracking
- [x] Squashed OCR hallucination bugs, achieving high parity with manual €80/share calculations

### Phase 3 — Third project (Layer 4: full AI application)
- [x] Feature: Qualitative Macro-Scoring. Use LLM to grade MD&A and Risk Factors for Confidence, Risk, and Governance.
- [x] Feature: Orchestration Script. Fully automate PDF fetching for a target list of tickers from company IR sites/Edgar to feed the DCF Engine.
- [x] Feature: Analyst Consensus Agent. A standalone agent (`analyst_agent.py`) that scours the internet for Wall Street target prices to act as an external feature for ML training.
- [x] Feature: Fallback Logic. If PDF parsing fails entirely, automatically fallback to pulling historical data from Yahoo Finance API.
- [x] Feature: Statistical Regression Engine (OLS). Build an explainable statistical model to predict Market-Premium-to-DCF based on `valuations_v2.db` features (margins, management confidence, risk).
- [x] Externalize Regex Config: Move string matchers (like "Liabilities to banks", "EBIT") into a `config.json` dictionary so non-technical users can add labels without editing python code.
- [ ] Deployed somewhere real (not just localhost)
- [ ] Monitoring/evaluation in place
- [ ] Architecture entry

### Phase 4 — Portfolio & positioning
- [ ] 3 projects documented with architecture diagrams + business cases
- [ ] One-pager written: "I am a business technologist who..." (your positioning statement)
- [ ] Target roles list finalized (see `ROADMAP.md` §4)
- [ ] Applied / pitched to at least 3 real opportunities

## Notes / log
(freeform space — date-stamp entries as you go)

- 2026-08-25: Project initialized.
- 2026-08-26: Completed v1 of Project 1 (Invoice Extractor). Transitioning to Project 2 (DCF Agent with API integration).
