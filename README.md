# 🧬 Oncology GraphRAG

A complete GraphRAG (Graph Retrieval-Augmented Generation) system built on an **oncology knowledge graph**. Ask questions about cancer drugs, gene targets, disease associations, and clinical trials in plain English — the system finds the answer by traversing a Neo4j graph of drugs, genes, cancer types, symptoms, and trials, then generates a grounded response via GPT-4o.

> Educational / portfolio project. Not medical advice — always defer to primary clinical sources (FDA labels, NCCN guidelines, ClinicalTrials.gov) for real decisions.

---

## What This Project Demonstrates

| Concept                          | How it appears in this project                    |
| --------------------------------- | -------------------------------------------------- |
| Graph database fundamentals       | Neo4j with an oncology ontology                    |
| Cypher query language             | Loader, traversal, and stat queries                |
| Vector embeddings on graph nodes  | Each node carries an OpenAI embedding              |
| GraphRAG pipeline                 | Vector search → graph traversal → LLM answer       |
| Real-world biomedical data APIs   | Open Targets Platform + ClinicalTrials.gov         |
| FastAPI backend                   | REST endpoints for all pipeline operations         |
| Streamlit frontend                | 3-page chat + explorer + stats interface           |
| Docker Compose                    | One command to start everything                    |

---

## Knowledge Graph Ontology

```
NODES
──────────────────────────────────────────────────────────
Drug     {name, category, mechanism_of_action}
Disease  {name, category, description}
Gene     {symbol, name, chromosome}
Symptom  {name, description}
Trial    {trial_id, phase, status, year, title}

RELATIONSHIPS
──────────────────────────────────────────────────────────
(Drug)    -[:TREATS]->            (Disease)
(Drug)    -[:INTERACTS_WITH]->    (Drug)
(Drug)    -[:TARGETS]->           (Gene)
(Gene)    -[:ASSOCIATED_WITH]->   (Disease)
(Disease) -[:HAS_SYMPTOM]->       (Symptom)
(Drug)    -[:TESTED_IN]->         (Trial)
(Trial)   -[:STUDIES]->           (Disease)
```

## About the data

The default seed dataset (`src/data/oncology_data.py`) is a hand-curated set of ~25 genes, ~20 cancer types, ~35 FDA-approved oncology drugs, and real trial identifiers, reflecting well-documented pharmacology (e.g. trastuzumab → HER2/ERBB2 → HER2-positive breast cancer; imatinib → BCR-ABL1 → chronic myeloid leukemia). It's accurate but not exhaustive.

For a larger, live-refreshed dataset, run `src/data/fetch_oncology_data.py`, which pulls target–disease associations and drug mechanisms from the [Open Targets Platform GraphQL API](https://platform.opentargets.org/) and real trial records from the [ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api/api), caching the result to `oncology_live_cache.json`. Wire that cache into `loader.py` if you want to load it instead of (or in addition to) the curated set.

---

## Setup

### Prerequisites

| Tool           | Version | Notes                            |
| -------------- | ------- | -------------------------------- |
| Docker Desktop | Latest  | Must be running                  |
| Python         | 3.11+   | For running scripts locally      |
| OpenAI API key | —       | Required for embeddings + GPT-4o |

### 1. Clone and configure

```bash
git clone <repo-url>
cd oncology-graph-rag

cp .env.example .env
# Edit .env and add your OpenAI key
```

Your `.env` file:

```
OPENAI_API_KEY=sk-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=oncology2024!
```

### 2. Start Neo4j

```bash
docker compose up neo4j -d
docker compose logs neo4j | grep "Started"
```

Open the Neo4j Browser at http://localhost:7474 (user: `neo4j`, password: `oncology2024!`)

### 3. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Load the knowledge graph

```bash
cd src
python loader.py
```

### 5. Add vector embeddings

```bash
python embeddings.py
```

### 6. Start the FastAPI backend

```bash
uvicorn api:app --reload --port 8000
```

Open http://localhost:8000/docs to confirm it's up.

### 7. Run the Streamlit app

Open a **new terminal**, activate the venv, then:

```bash
cd src
streamlit run app.py
```

Open http://localhost:8501

### 8. (Recommended) Start everything with Docker Compose

```bash
docker compose up --build
```

| Service        | URL                          |
| -------------- | ---------------------------- |
| Neo4j Browser  | http://localhost:7474        |
| FastAPI docs   | http://localhost:8000/docs   |
| Streamlit chat | http://localhost:8501        |

---

## Usage

### Streamlit Chat Interface

Try:

- *"What drugs treat HER2-positive breast cancer and what gene do they target?"*
- *"Which drugs target EGFR and what cancers are they used for?"*
- *"What clinical trials tested pembrolizumab?"*
- *"Which genes are associated with both breast cancer and ovarian cancer?"*
- *"What symptoms are associated with pancreatic ductal adenocarcinoma?"*

### FastAPI Endpoints

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What treats chronic myeloid leukemia?", "top_k": 3, "hops": 2}'

curl "http://localhost:8000/search?q=BRAF+inhibitor&label=Drug"
curl "http://localhost:8000/graph/Melanoma?label=Disease&hops=2"
curl "http://localhost:8000/drug/Trastuzumab/profile"
curl "http://localhost:8000/disease/Melanoma/profile"
curl "http://localhost:8000/stats"
```

---

## Project Structure

```
oncology-graph-rag/
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── Dockerfile.api
├── Dockerfile.streamlit
├── CYPHER_PRACTICE.md
└── src/
    ├── db.py                        ← Neo4j connection wrapper
    ├── loader.py                    ← Load ontology + data into Neo4j
    ├── embeddings.py                ← Compute + store node embeddings
    ├── graphrag.py                  ← The full GraphRAG pipeline
    ├── api.py                       ← FastAPI backend
    ├── app.py                       ← Streamlit frontend
    └── data/
        ├── oncology_data.py         ← Curated seed dataset
        └── fetch_oncology_data.py   ← Live data fetcher (Open Targets + ClinicalTrials.gov)
```

---

## How the GraphRAG Pipeline Works

```
User question (text)
       │
       ▼
┌──────────────────────────────┐
│  1. Vector Search            │  Embed question → find top-k similar nodes
│     (embeddings.py)          │  e.g. "What treats CML?" → [Imatinib, CML]
└──────────────────┬───────────┘
                    │  top-k node identifiers
                    ▼
┌──────────────────────────────┐
│  2. Graph Traversal          │  Walk N hops from each identified node
│     (graphrag.py)            │  Collect all connected facts as triples
└──────────────────┬───────────┘
                    │  subgraph as structured text
                    ▼
┌──────────────────────────────┐
│  3. LLM Answer Generation    │  GPT-4o reasons over graph context
│     (OpenAI GPT-4o)          │  Returns grounded, verifiable answer
└──────────────────────────────┘
```

---

## Deploying: Render (API) + Neo4j Aura (database) + Lovable (frontend)

The Streamlit app above is the quickest way to try things locally, but for a
deployed portfolio piece the recommended split is:

- **Database:** [Neo4j Aura Free](https://neo4j.com/cloud/aura-free/) — Render's
  web services don't have persistent local disks, so Neo4j needs to live
  somewhere else. Aura's free tier is a hosted Neo4j instance made for exactly
  this.
- **Backend:** this FastAPI app, deployed to [Render](https://render.com).
- **Frontend:** a React app built in [Lovable](https://lovable.dev), talking to
  the Render API over plain REST/JSON.

### 1. Stand up Neo4j Aura

1. Create a free instance at [console.neo4j.io](https://console.neo4j.io).
2. Save the generated connection URI (`neo4j+s://xxxx.databases.neo4j.io`),
   username, and password — Aura only shows the password once.
3. Locally, point `.env` at Aura instead of your local Docker Neo4j:
   ```
   NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<your Aura password>
   ```
4. Run `python src/loader.py` then `python src/embeddings.py` once, from your
   machine, to populate the Aura instance. (Aura free tier supports vector
   indexes, so `embeddings.py` works unmodified.)

### 2. Deploy the API to Render

This repo includes `render.yaml`, so you can deploy via a Blueprint:

1. Push this repo to GitHub.
2. In Render, choose **New → Blueprint**, point it at the repo — it will pick
   up `render.yaml` and `Dockerfile.api` automatically.
3. Render will prompt for the env vars marked `sync: false`:
   `OPENAI_API_KEY`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
4. Deploy. Your API will be live at `https://<service-name>.onrender.com`.
   Check `https://<service-name>.onrender.com/health` once it's up.
5. Note: Render's free web service tier spins down after inactivity, so the
   first request after idle time will be slow (cold start, ~30-60s) — normal
   for a free-tier demo.

If you'd rather deploy manually instead of via Blueprint: create a new **Web
Service**, runtime **Docker**, Dockerfile path `Dockerfile.api`, and set the
same four env vars in the dashboard.

### 3. Build the frontend in Lovable

Use the ready-to-paste spec in [`LOVABLE_PROMPT.md`](./LOVABLE_PROMPT.md) — it
describes every endpoint, request/response shape, and page layout so Lovable
can scaffold the whole UI (chat, graph explorer, stats dashboard) in one go.
Swap in your Render URL where the prompt says `<YOUR_RENDER_URL>`.

Once your Lovable app has its own URL, tighten CORS on the backend by setting
`ALLOWED_ORIGINS` in Render to that exact URL (comma-separate multiple origins
if needed) instead of the default `*`.

---

## Extending the Project

### Adding more drugs/diseases/genes

Add entries to the lists in `src/data/oncology_data.py`, then re-run `loader.py` and `embeddings.py`.

### Pulling live data

Run `python src/data/fetch_oncology_data.py` to refresh from Open Targets + ClinicalTrials.gov, then adapt `loader.py` to read from `oncology_live_cache.json`.

### Ideas for further differentiation (great portfolio talking points)

- Add a `Publication` node type linking drugs/genes to PubMed abstracts (evidence-grounded QA)
- Add drug-drug interaction severity scoring
- Add a biomarker-based treatment recommender endpoint
- Swap GPT-4o for a different LLM by editing the `openai` calls in `graphrag.py`

---

*Adapted from the GraphRAG pattern used in the [bollywood-graph-rag](https://github.com/Ramendra611/bollywood-graph-rag) teaching project (Codeverra), retargeted to a real biomedical/oncology use case.*
