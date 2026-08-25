# Architecture Practice Log

Every project gets one entry here. The goal isn't a perfect diagram — it's forcing yourself to explain every box in plain language, the way you'd explain it to a non-technical stakeholder.

## Template (copy this for each project)

### Project: [name]

**Diagram:**
```
Customer
   ↓
Web / CRM
   ↓
API Layer
   ↓
Business Logic
   ↓
Database
   ↓
LLM / RAG
   ↓
Automation / Workflow
   ↓
ERP / CRM / Email
```
(edit boxes to fit what you actually built — remove/add as needed)

**Explain each box in one sentence, no jargon:**
- Box 1:
- Box 2:
- Box 3:
- ...

**Where does data live, and who can see it?**

**What would break first if this had 100x the users?**

**What's the ROI story in one sentence?** (e.g. "saves the finance team ~5 hours/week on manual PDF review")

---

## Entries

### Project 1: PDF Financial Analyst Agent

**Diagram:**
```
PDF Document
   ↓
Python Orchestrator (LangChain / LlamaIndex / Custom)
   ↓
Text Extraction Tool (PyMuPDF / pdfplumber) → Success? 
   ↓ (If Yes)                               ↓ (If No / Image-heavy)
LLM (Qwen 8B - Tool Calls)            VLM (Vision Model Fallback)
   ↓                                        ↓
Data parsing & mapping (JSON extraction)
   ↓
Python Calculation Engine (Pandas / custom scripts for math)
   ↓
Database / Clean Spreadsheet (CSV/Excel)
```

**Explain each box in one sentence, no jargon:**
- **Python Orchestrator:** The brain that takes the file and decides where it needs to go next.
- **Text Extraction Tool:** A fast, non-AI script that rips text directly out of the file if possible.
- **LLM (Qwen 8B):** A small, efficient AI that reads the raw text and structures it into specific fields.
- **VLM (Vision Fallback):** A specialized AI that "looks" at the document as an image if the fast text extractor fails.
- **Python Calculation Engine:** Traditional code that does the math (like summing totals) because AI is bad at math.

**Where does data live, and who can see it?**
Currently processed locally; data exists in memory and outputs to a local CSV file.

**What would break first if this had 100x the users?**
If running locally, inference compute (GPU/RAM) would bottleneck immediately under concurrent requests.

**What's the ROI story in one sentence?** 
Saves the finance team hours of manual data entry per week by instantly converting messy PDFs into clean, calculated spreadsheet rows.

(add new entries below as you complete projects)
