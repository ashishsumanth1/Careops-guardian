# CareOps Guardian

CareOps Guardian is an AI assistant for domiciliary care managers. It ingests synthetic but realistic care plans, risk assessments, and incident logs, then combines retrieval-augmented generation (RAG) with domain rules to answer questions, flag risks, and produce QA-style reports.

## Architecture Overview

```
careops-guardian/
├── data/
│   ├── care_plans/*.md
│   ├── risk_assessments/*.md
│   └── incidents.csv
├── src/
│   ├── config.py                  # Paths and model choices
│   ├── generate_synthetic_data.py # Builds the dataset
│   ├── load_data.py               # Loads markdown docs as LangChain Documents
│   ├── build_vector_store.py      # Chunks docs + stores embeddings in Chroma
│   ├── rag_pipeline.py            # Service-user-specific QA pipeline
│   ├── incidents.py               # Pydantic model + loader for incidents
│   ├── rules.py                   # Incident analytics and risk checks
│   ├── guardian.py                # Orchestrates rules + RAG into QA report
│   └── cli.py                     # CLI for care questions and incident reports
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your OpenAI key (bash/zsh example):
```bash
echo "OPENAI_API_KEY=sk-..." > .env
set -a && source .env && set +a
```

### 2. Generate synthetic data
```bash
python -m src.generate_synthetic_data
```
This creates 100 care plans, 200+ risk assessments, and ~1,700 incident records under `data/`.

### 3. Build the vector store
```bash
python -m src.build_vector_store
```
Chunks the markdown documents, creates embeddings, and persists them to `.chroma_db`.

## Usage

### Ask questions about a service user
```bash
python -m src.cli care SU001 "Describe this person's behaviour risks and support strategies"
```
Provides a RAG-based answer grounded in that user’s care plan and risk assessments.

### Generate an incident QA report
```bash
python -m src.cli incident INC001016
```
Combines the incident narrative, rule-based findings, and a care-plan summary to produce a structured report with narrative, risks/controls, and suggested actions.

### Launch the Streamlit UI prototype
```bash
streamlit run streamlit_app.py
```
Gives you three tabs:
- **Care Q&A** – pick a service user, type a free-text question, and view the RAG response.
- **Incident QA** – browse incidents (with severity/category context) and trigger the Guardian report generator.
- **Risk Rules** – refreshable snapshot of deterministic analytics (frequent fallers, falls-without-assessment, etc.).

> Tip: the app expects `.env` to expose `OPENAI_API_KEY` and a built Chroma vector store under `.chroma_db/` (run `python -m src.build_vector_store` first if empty).

## Example Output

**Service-user query (care):**
```
Service User: SU001
Question: Summarise transfers and falls risk
Answer:
- Medium falls risk with multiple falls, unsteady gait, and dementia
- Control measures: 2-hour repositioning, barrier cream, call bell access, staff supervision...
```

**Incident report (incident):**
```
### 1) Short Narrative Summary
On December 10, 2024 ... pressure area redness observed ...

### 2) Bullet Risks/Controls
- High risk of skin integrity issues ...

### 3) Follow-Up Actions
1. Monitor skin integrity
2. District nurse assessment within 24 hours
...
```

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (done already) and sign in at [share.streamlit.io](https://share.streamlit.io/).
2. Click **New app**, pick `ashishsumanth1/Careops-guardian`, choose `main` and set the entry point to `streamlit_app.py`.
3. In the *Advanced settings → Secrets* panel, add:
	```toml
	OPENAI_API_KEY = "sk-..."
	```
	(For local testing you can copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml`, but never commit the real key.)
4. Deploy. Streamlit builds the app, installs `requirements.txt`, and exposes a public HTTPS link you can share from your portfolio/README.

If the app warns that the vector store is missing you have two options:
- Run `python -m src.build_vector_store` locally and commit the resulting `.chroma_db/` folder (remove it from `.gitignore` temporarily so it ships with the repo).
- Or, modify `streamlit_app.py` to call the builder automatically in Cloud (e.g. run `src.build_vector_store` if the folder is empty) before serving requests.

## Roadmap

1. **UI Prototype:** Build a lightweight Streamlit or console UI to browse service users, run care queries, and display incident QA reports.
2. **Documentation Enhancements:** Add architecture diagrams, screenshots, and evaluation metrics to the README.
3. **Evaluation:** Track answer provenance, rule hits, and potential hallucination checks for RAG outputs.
4. **API Layer:** Expose REST endpoints (FastAPI) so external tools can request service-user summaries or incident QA reports.
5. **Extended Corpora:** Ingest policies or regulator (CQC) reports for additional context and benchmarking.

## Tech Stack
- **Python 3.13**, `langchain`, `langchain-openai`, `langchain-community`
- **Chroma** vector store (persisted locally)
- **Pydantic** + **pandas** for incident parsing
- **OpenAI GPT-4o-mini** + `text-embedding-3-small`

---
Designed for experimentation and portfolio demos. All data is synthetic and anonymised, yet structured to mirror UK social care documentation and incident patterns.
