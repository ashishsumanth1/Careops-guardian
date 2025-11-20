# CareOps Guardian

CareOps Guardian is an AI assistant for domiciliary care managers. It ingests synthetic but realistic care plans, risk assessments, and incident logs, then combines retrieval-augmented generation (RAG) with domain rules to answer questions, flag risks, and produce QA-style reports.

## Why this project exists

UK domiciliary care teams handle hundreds of documents per service user: life history, risk assessments, daily notes, and large CSV-style incident logs. In practice, staff rely on fragmented spreadsheets and long narrative reports, so answering simple questions ("What does SU004 need for transfers?") or auditing incidents is slow. CareOps Guardian simulates a "digital junior guardian" that can:

- Ingest structured + unstructured care evidence
- Retrieve the right fragments with provenance per service user
- Layer deterministic rule checks (frequent fallers, missing risk assessments, severity counts)
- Generate concise narratives a manager can paste into QA returns or safeguarding reports

Even though the corpus is synthetic, the schema mirrors what interviewers ask about: data ETL, RAG safety, and automation of compliance tasks.

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

### End-to-end flow

1. **Synthetic data generator** creates 100 markdown care plans, 300 risk assessments, and ~1,700 incidents with believable metadata (severity, categories, timestamps).
2. **Vector-store builder** chunks the markdown docs, embeds them with `text-embedding-3-small`, and persists the Chroma index filtered by `service_user_id` metadata so we can scope retrieval per person.
3. **RAG pipeline** (`rag_pipeline.py`) loads the persisted Chroma store, applies a LangChain prompt tuned for UK care language, and returns grounded answers.
4. **Rules engine** (`rules.py`) runs deterministic analytics over the incidents CSV—frequent fallers, high severity counts, missing falls assessments—surfacing metrics the LLM might miss.
5. **Guardian orchestrator** (`guardian.py`) stitches the incident narrative + RAG care summary + rule results into a structured, always-three-section QA report.
6. **Interfaces**: CLI for automation and a Streamlit UI for portfolio demos, both calling the same core functions. Streamlit auto-builds the vector store if missing in deployment.

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

## Deep dive by component

### Synthetic data (`src/generate_synthetic_data.py`)
- Mixes curated vocab lists (conditions, routines, risks) with controlled randomness to keep narratives realistic.
- Produces Markdown files so embeddings retain structure (headings, bullet lists) and CSV incidents for tabular analytics.
- Lets interviewers inspect actual files to understand data complexity.

### Vector store + RAG (`src/build_vector_store.py`, `src/rag_pipeline.py`)
- Uses `RecursiveCharacterTextSplitter` (800/150) to balance chunk size vs. recall.
- Metadata: `service_user_id`, `doc_type`, `risk_category` so retriever filters per person before kNN search; avoids cross-contamination between users.
- Prompt explicitly tells GPT-4o-mini to answer only from context and to admit when data is missing.
- Retrieval shim is resilient: if `langchain`'s `RetrievalQA` import fails, the file falls back to a minimal custom implementation so interviews can discuss portability.

### Incident analytics + Guardian orchestrator (`rules.py`, `guardian.py`)
- `rules.py` exposes pure functions (frequent fallers, severity counters, missing assessments). They are deterministic and unit-testable.
- `guardian.py` caches incident loads via `lru_cache`, builds the context dict (incident + rule outputs + RAG summary), then prompts GPT-4o-mini with strict instructions: narrative paragraph, bullet risks, numbered actions.
- This combination shows interviewers how to blend symbolic analytics with generative summaries.

### Interfaces (`src/cli.py`, `streamlit_app.py`)
- CLI proves the core logic is library-ready: `care` command hits the RAG pipeline, `incident` command hits Guardian.
- Streamlit UI mirrors a production "guardian" console with three tabs. It auto-builds the vector store in cloud deployments when `.chroma_db/` is absent (and reuses existing embeddings locally). Side bar surfaces dataset counts + environment warnings so you can discuss observability.

### Data and security considerations
- All data is synthetic yet structured to resemble actual CQC documentation; no PHI/PII risk.
- `.env` / `.streamlit/secrets.toml` keep your API keys local. When hosting, Streamlit Cloud secrets store protects the key; README explains the process interviewers often care about.

## Technical decisions to highlight in interviews

- **Model choice**: GPT-4o-mini provides high-quality answers with sensible latency/cost for demos; embeddings rely on `text-embedding-3-small` because of its 8k context and low price.
- **Vector store**: Chroma was picked because it ships with persistence-by-default and works offline. Filtering on metadata prevents cross-user leakage, which is a common compliance question.
- **Rules + RAG**: Interviewers often ask how you limit hallucinations. Answer: combine deterministic rule outputs with RAG context, never let the LLM invent severity counts.
- **Caching**: `lru_cache` on incident loads avoids repeated CSV parsing while keeping the code simple.
- **Error handling**: Streamlit auto-detects missing vector stores and builds them, falling back with user-facing warnings when API keys are absent.
- **Deployment**: Designed specifically for Streamlit Community Cloud to keep hosting free. README captures the full process so you can walk an interviewer through it from memory.

## What I learned / talking points

1. **Document chunking matters** – testing different chunk sizes showed 800 tokens with 150 overlap was the sweet spot: small chunks missed context, large ones hallucinated. I can talk about evaluation strategy.
2. **Metadata is a compliance control** – filtering the retriever on `service_user_id` guarantees we never mix evidence between residents, which is critical in regulated domains.
3. **Rules + LLMs complement each other** – by keeping risk rules deterministic, we can explain every flag and only use the LLM for narrative glue.
4. **Synthetic-but-realistic corpora** – generating the dataset forced me to think like a care manager: life history, routines, triggers, escalation routes.
5. **Operational readiness** – the Streamlit deployment story covers secrets management, dependency locking, and auto-building the vector store, which mirrors real-world MLOps concerns.

If an interviewer drills deeper, skim `guardian.py` for the full prompt or `rules.py` for analytics—they’re intentionally concise and well-commented.

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
