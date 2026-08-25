# Projects: The Training Loop

**Philosophy:** don't study skills, do projects that force skills on you. One real project trains more of the stack than weeks of isolated tutorials.

The loop, every time:
```
Find a real problem → talk to people who have it → build a tiny solution →
show it → ask for feedback (or money) → learn → improve
```

---

## How to pick a project

A good project for this roadmap:
- Solves a real (even small) problem for a real person or business — not a toy dataset.
- Touches at least 3 of the 4 technical layers.
- Forces at least one non-technical skill (a conversation with a real user, a small business case, a demo).
- Can produce a v1 in days, not months.

---

## Starter project ideas (roughly increasing in complexity)

### 1. Document/PDF intelligence tool
You discover that small Mittelstand companies spend hours extracting information from PDFs. You build a highly-efficient, tiny document-analysis tool using quantized local models (Qwen 8B / DeepSeek 14B) and a "deterministic-first" architecture. It attempts text extraction and Python calculations first, falling back to a Vision model only if the PDF is an image.
- **Trains:** Python → APIs → LLMs (tool calls/structured output) → VLM fallbacks → databases → authentication → UI → deployment → pricing → customer discovery → sales. 
*One project can therefore train 60% of your desired skill set.*

### 2. Internal knowledge-base RAG assistant
Take a company's (or your own) scattered docs — policies, wikis, PDFs — and build a Q&A assistant over them.
- **Trains:** embeddings, vector DB, RAG, evaluation (does it actually answer correctly?), auth (who can query what), deployment.

### 3. Workflow automation agent
Pick one annoying recurring business process (e.g. triaging inbound leads, summarizing meeting notes into CRM entries) and automate it end-to-end with an agent that calls real APIs.
- **Trains:** agents, tool use, webhooks, CRM/ERP integration patterns, monitoring — plus you'll need a business case for why it's worth automating.

### 4. Fraud/anomaly detection dashboard (plays to your background)
Take a financial or transactional dataset, build simple anomaly detection, and wrap it in a dashboard a non-technical finance person could use.
- **Trains:** ML fundamentals, data pipelines, SQL, dashboarding, and — critically — explaining a technical result to a business audience.

### 5. End-to-end AI copilot for a niche vertical
Combine everything: a small AI product for one specific industry process (e.g. real estate due-diligence document review), with auth, a real UI, deployed somewhere real people can use it, and at least one real conversation about whether they'd pay for it.
- **Trains:** the entire stack + pricing + go-to-market + a genuine business case.

---

## For each project, produce these artifacts

1. One paragraph: what problem, for whom.
2. The architecture diagram (see `ARCHITECTURE.md`).
3. The working thing (however minimal).
4. A one-page business case: cost saved / time saved / revenue potential.
5. Evidence you showed it to a real person and what they said.

This turns "I built a RAG demo" into "I identified a problem, designed a solution, built it, and validated it with a real user" — which is the actual profile you're building.
