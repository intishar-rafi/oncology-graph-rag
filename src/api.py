"""FastAPI backend for the Oncology GraphRAG system."""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import get_connection
from graphrag import ask

app = FastAPI(
    title="Oncology GraphRAG API",
    description="Ask questions about cancer drugs, genes, diseases and trials via a Neo4j knowledge graph + GPT-4o.",
    version="1.0.0",
)

# Comma-separated list of allowed origins, e.g. "https://your-app.lovable.app,http://localhost:5173"
# Defaults to "*" for easy local/demo use; lock this down to your actual Lovable domain in production.
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = ["*"] if _allowed_origins == "*" else [o.strip() for o in _allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    top_k: int = 3
    hops: int = 2


@app.post("/ask")
def ask_question(req: AskRequest):
    try:
        return ask(req.question, top_k=req.top_k, hops=req.hops)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
def vector_search_endpoint(q: str, label: str = "Disease", top_k: int = 5):
    from embeddings import embed_texts

    valid_labels = {"Drug", "Disease", "Gene", "Symptom", "Trial"}
    if label not in valid_labels:
        raise HTTPException(status_code=400, detail=f"label must be one of {valid_labels}")

    conn = get_connection()
    try:
        [vector] = embed_texts([q])
        index_name = f"{label.lower()}_embedding_index"
        rows = conn.query(
            """
            CALL db.index.vector.queryNodes($index_name, $top_k, $vector)
            YIELD node, score
            RETURN node, score
            """,
            {"index_name": index_name, "top_k": top_k, "vector": vector},
        )
        return [{"node": dict(r["node"]), "score": r["score"]} for r in rows]
    finally:
        conn.close()


@app.get("/graph/{entity}")
def entity_neighbourhood(entity: str, label: str = "Disease", hops: int = 2):
    id_prop = {"Drug": "name", "Disease": "name", "Gene": "symbol",
               "Symptom": "name", "Trial": "trial_id"}.get(label)
    if not id_prop:
        raise HTTPException(status_code=400, detail="Invalid label")

    conn = get_connection()
    try:
        rows = conn.query(
            f"""
            MATCH (start:{label} {{{id_prop}: $entity}})
            MATCH path = (start)-[*1..{hops}]-(other)
            WITH relationships(path) AS rels, nodes(path) AS ns
            UNWIND range(0, size(rels)-1) AS i
            WITH ns[i] AS a, rels[i] AS r, ns[i+1] AS b
            RETURN DISTINCT
                coalesce(a.name, a.symbol, a.trial_id) AS source,
                labels(a)[0] AS source_label,
                type(r) AS relationship,
                coalesce(b.name, b.symbol, b.trial_id) AS target,
                labels(b)[0] AS target_label
            LIMIT 100
            """,
            {"entity": entity},
        )
        if not rows:
            raise HTTPException(status_code=404, detail=f"No entity '{entity}' found with label {label}")
        return rows
    finally:
        conn.close()


@app.get("/drug/{name}/profile")
def drug_profile(name: str):
    conn = get_connection()
    try:
        rows = conn.query(
            """
            MATCH (d:Drug {name: $name})
            OPTIONAL MATCH (d)-[:TREATS]->(disease:Disease)
            OPTIONAL MATCH (d)-[:TARGETS]->(gene:Gene)
            OPTIONAL MATCH (d)-[:TESTED_IN]->(trial:Trial)
            RETURN d.name AS drug, d.category AS category, d.mechanism_of_action AS mechanism,
                   collect(DISTINCT disease.name) AS treats,
                   collect(DISTINCT gene.symbol) AS targets,
                   collect(DISTINCT trial.trial_id) AS trials
            """,
            {"name": name},
        )
        if not rows or rows[0]["drug"] is None:
            raise HTTPException(status_code=404, detail=f"Drug '{name}' not found")
        return rows[0]
    finally:
        conn.close()


@app.get("/disease/{name}/profile")
def disease_profile(name: str):
    conn = get_connection()
    try:
        rows = conn.query(
            """
            MATCH (di:Disease {name: $name})
            OPTIONAL MATCH (dr:Drug)-[:TREATS]->(di)
            OPTIONAL MATCH (g:Gene)-[:ASSOCIATED_WITH]->(di)
            OPTIONAL MATCH (di)-[:HAS_SYMPTOM]->(s:Symptom)
            OPTIONAL MATCH (t:Trial)-[:STUDIES]->(di)
            RETURN di.name AS disease, di.category AS category, di.description AS description,
                   collect(DISTINCT dr.name) AS treated_by,
                   collect(DISTINCT g.symbol) AS associated_genes,
                   collect(DISTINCT s.name) AS symptoms,
                   collect(DISTINCT t.trial_id) AS trials
            """,
            {"name": name},
        )
        if not rows or rows[0]["disease"] is None:
            raise HTTPException(status_code=404, detail=f"Disease '{name}' not found")
        return rows[0]
    finally:
        conn.close()


@app.get("/stats")
def graph_stats():
    conn = get_connection()
    try:
        counts = conn.query(
            """
            RETURN
                count { (n:Drug) } AS drugs,
                count { (n:Disease) } AS diseases,
                count { (n:Gene) } AS genes,
                count { (n:Symptom) } AS symptoms,
                count { (n:Trial) } AS trials
            """
        )
        rel_counts = conn.query(
            """
            MATCH ()-[r]->()
            RETURN type(r) AS relationship, count(r) AS count
            ORDER BY count DESC
            """
        )
        return {"nodes": counts[0], "relationships": rel_counts}
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}
