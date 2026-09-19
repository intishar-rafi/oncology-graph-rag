"""
Computes OpenAI embeddings for each node in the oncology graph and
stores them back on the node so Neo4j can serve vector similarity
search (via a vector index) for the GraphRAG pipeline.

Run once after loader.py. Re-running is safe: it overwrites existing
embeddings.
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

from db import get_connection

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

# (label, text-representation cypher fragment, id property)
NODE_TEXT_QUERIES = {
    "Drug": (
        "MATCH (n:Drug) RETURN n.name AS id, "
        "n.name + ' is a ' + coalesce(n.category, '') + '. Mechanism: ' + "
        "coalesce(n.mechanism_of_action, '') AS text",
        "name",
    ),
    "Disease": (
        "MATCH (n:Disease) RETURN n.name AS id, "
        "n.name + ' (' + coalesce(n.category, '') + '): ' + coalesce(n.description, '') AS text",
        "name",
    ),
    "Gene": (
        "MATCH (n:Gene) RETURN n.symbol AS id, "
        "n.symbol + ' (' + coalesce(n.name, '') + '), located on chromosome ' + "
        "coalesce(n.chromosome, 'unknown') AS text",
        "symbol",
    ),
    "Symptom": (
        "MATCH (n:Symptom) RETURN n.name AS id, "
        "n.name + ': ' + coalesce(n.description, '') AS text",
        "name",
    ),
    "Trial": (
        "MATCH (n:Trial) RETURN n.trial_id AS id, "
        "coalesce(n.title, '') + ' (' + coalesce(n.phase, '') + ', ' + "
        "coalesce(n.status, '') + ', ' + toString(coalesce(n.year, '')) + ')' AS text",
        "trial_id",
    ),
}


def embed_texts(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def create_vector_indexes(conn):
    for label, (_, id_prop) in NODE_TEXT_QUERIES.items():
        index_name = f"{label.lower()}_embedding_index"
        conn.write(
            f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (n:{label}) ON (n.embedding)
            OPTIONS {{indexConfig: {{
                `vector.dimensions`: {EMBEDDING_DIM},
                `vector.similarity_function`: 'cosine'
            }}}}
            """
        )
    print("  ✓ Vector indexes created")


def embed_label(conn, label: str, query: str, id_prop: str, batch_size: int = 50):
    rows = conn.query(query)
    print(f"[{label}] embedding {len(rows)} nodes...")
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        vectors = embed_texts([r["text"] for r in batch])
        for row, vector in zip(batch, vectors):
            conn.write(
                f"MATCH (n:{label} {{{id_prop}: $id}}) SET n.embedding = $embedding",
                {"id": row["id"], "embedding": vector},
            )
    print(f"  ✓ {label} embeddings stored")


def embed_all():
    conn = get_connection()
    try:
        create_vector_indexes(conn)
        for label, (query, id_prop) in NODE_TEXT_QUERIES.items():
            embed_label(conn, label, query, id_prop)
        print("\nAll node embeddings computed and stored.")
    finally:
        conn.close()


if __name__ == "__main__":
    embed_all()
