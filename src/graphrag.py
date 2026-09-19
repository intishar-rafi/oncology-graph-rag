"""
The GraphRAG pipeline for the oncology knowledge graph:

    1. Vector search  — embed the question, find the top-k most similar nodes
       across Drug/Disease/Gene/Symptom/Trial via Neo4j vector indexes.
    2. Graph traversal — walk N hops from each matched node, collecting all
       connected facts as (subject, relationship, object) triples.
    3. LLM answer generation — feed the collected subgraph as grounded
       context to GPT-4o and return a cited, natural-language answer.
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

from db import get_connection
from embeddings import embed_texts, NODE_TEXT_QUERIES

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CHAT_MODEL = "gpt-4o"

LABELS = list(NODE_TEXT_QUERIES.keys())  # Drug, Disease, Gene, Symptom, Trial


def vector_search(conn, question: str, top_k: int = 5) -> list[dict]:
    """Embed the question and search each label's vector index, merge results by score."""
    [q_vector] = embed_texts([question])

    hits = []
    for label in LABELS:
        index_name = f"{label.lower()}_embedding_index"
        rows = conn.query(
            f"""
            CALL db.index.vector.queryNodes($index_name, $top_k, $vector)
            YIELD node, score
            RETURN labels(node) AS labels, node, score
            """,
            {"index_name": index_name, "top_k": top_k, "vector": q_vector},
        )
        for r in rows:
            node = r["node"]
            hits.append({
                "label": label,
                "score": r["score"],
                "identifier": node.get("name") or node.get("symbol") or node.get("trial_id"),
                "properties": dict(node),
            })

    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:top_k]


def graph_traversal(conn, hits: list[dict], hops: int = 2) -> list[str]:
    """Walk N hops from each matched node and return facts as readable triples."""
    triples = set()

    for hit in hits:
        label = hit["label"]
        identifier = hit["identifier"]
        id_prop = {"Drug": "name", "Disease": "name", "Gene": "symbol",
                   "Symptom": "name", "Trial": "trial_id"}[label]

        rows = conn.query(
            f"""
            MATCH (start:{label} {{{id_prop}: $id}})
            MATCH path = (start)-[*1..{hops}]-(other)
            WITH relationships(path) AS rels, nodes(path) AS ns
            UNWIND range(0, size(rels)-1) AS i
            WITH ns[i] AS a, rels[i] AS r, ns[i+1] AS b
            RETURN DISTINCT
                coalesce(a.name, a.symbol, a.trial_id) AS a_id,
                labels(a)[0] AS a_label,
                type(r) AS rel,
                coalesce(b.name, b.symbol, b.trial_id) AS b_id,
                labels(b)[0] AS b_label
            LIMIT 40
            """,
            {"id": identifier},
        )
        for r in rows:
            triples.add(f"({r['a_label']}:{r['a_id']}) -[{r['rel']}]-> ({r['b_label']}:{r['b_id']})")

    return sorted(triples)


def generate_answer(question: str, triples: list[str]) -> str:
    context = "\n".join(triples) if triples else "No relevant graph facts found."
    system_prompt = (
        "You are an oncology knowledge assistant. Answer the user's question using ONLY the "
        "graph facts (triples) provided below as context. Be precise, cite the specific drugs, "
        "genes, diseases or trials involved, and say clearly if the graph does not contain "
        "enough information to answer confidently. This is an educational/demo tool, not a "
        "source of clinical advice."
    )
    user_prompt = f"Graph facts:\n{context}\n\nQuestion: {question}"

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content


def ask(question: str, top_k: int = 3, hops: int = 2) -> dict:
    conn = get_connection()
    try:
        hits = vector_search(conn, question, top_k=top_k)
        triples = graph_traversal(conn, hits, hops=hops)
        answer = generate_answer(question, triples)
        return {
            "question": question,
            "matched_nodes": [{"label": h["label"], "id": h["identifier"], "score": h["score"]} for h in hits],
            "graph_context": triples,
            "answer": answer,
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = ask("What drugs treat HER2-positive breast cancer and what gene do they target?")
    print(result["answer"])
