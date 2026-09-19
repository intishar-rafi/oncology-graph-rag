"""
Loads the oncology ontology and data into Neo4j.

Ontology:
    NODES:      Drug, Disease, Gene, Symptom, Trial
    RELATIONSHIPS:
        (Drug)-[:TREATS]->(Disease)
        (Drug)-[:INTERACTS_WITH]->(Drug)
        (Drug)-[:TARGETS]->(Gene)
        (Gene)-[:ASSOCIATED_WITH]->(Disease)
        (Disease)-[:HAS_SYMPTOM]->(Symptom)
        (Drug)-[:TESTED_IN]->(Trial)
        (Trial)-[:STUDIES]->(Disease)

Two data sources feed this loader:
    1. data/oncology_data.py    — hand-curated seed set (always loaded)
    2. data/extracted_data.json — optional, produced by entity_extraction.py
                                   from unstructured drug monographs via GPT-4o.
                                   Loaded automatically if present.
"""

import json
from pathlib import Path

from db import get_connection
from data.oncology_data import (
    GENES,
    DISEASES,
    SYMPTOMS,
    DRUGS,
    TRIALS,
    TREATS,
    TARGETS,
    ASSOCIATED_WITH,
    HAS_SYMPTOM,
    TESTED_IN,
    STUDIES,
    INTERACTS_WITH,
)

EXTRACTED_DATA_PATH = Path(__file__).parent / "data" / "extracted_data.json"


def create_constraints(conn):
    constraints = [
        "CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE",
        "CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
        "CREATE CONSTRAINT gene_symbol IF NOT EXISTS FOR (g:Gene) REQUIRE g.symbol IS UNIQUE",
        "CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT trial_id IF NOT EXISTS FOR (t:Trial) REQUIRE t.trial_id IS UNIQUE",
    ]
    for c in constraints:
        conn.write(c)
    print("  ✓ Constraints active")


def load_nodes(conn):
    print("[1/2] Loading nodes...")
    create_constraints(conn)

    for g in GENES:
        conn.write(
            "MERGE (n:Gene {symbol: $symbol}) SET n.name = $name, n.chromosome = $chromosome",
            g,
        )
    print(f"  ✓ {len(GENES)} Gene nodes")

    for d in DISEASES:
        conn.write(
            "MERGE (n:Disease {name: $name}) SET n.category = $category, n.description = $description",
            d,
        )
    print(f"  ✓ {len(DISEASES)} Disease nodes")

    for s in SYMPTOMS:
        conn.write(
            "MERGE (n:Symptom {name: $name}) SET n.description = $description",
            s,
        )
    print(f"  ✓ {len(SYMPTOMS)} Symptom nodes")

    for d in DRUGS:
        conn.write(
            "MERGE (n:Drug {name: $name}) SET n.category = $category, n.mechanism_of_action = $mechanism_of_action",
            d,
        )
    print(f"  ✓ {len(DRUGS)} Drug nodes")

    for t in TRIALS:
        conn.write(
            """MERGE (n:Trial {trial_id: $trial_id})
               SET n.phase = $phase, n.status = $status, n.year = $year, n.title = $title""",
            t,
        )
    print(f"  ✓ {len(TRIALS)} Trial nodes")


def load_relationships(conn):
    print("[2/2] Loading relationships...")

    for drug, disease in TREATS:
        conn.write(
            """MATCH (dr:Drug {name: $drug}), (di:Disease {name: $disease})
               MERGE (dr)-[:TREATS]->(di)""",
            {"drug": drug, "disease": disease},
        )
    print(f"  ✓ {len(TREATS)} TREATS relationships")

    for drug, gene in TARGETS:
        conn.write(
            """MATCH (dr:Drug {name: $drug}), (g:Gene {symbol: $gene})
               MERGE (dr)-[:TARGETS]->(g)""",
            {"drug": drug, "gene": gene},
        )
    print(f"  ✓ {len(TARGETS)} TARGETS relationships")

    for gene, disease in ASSOCIATED_WITH:
        conn.write(
            """MATCH (g:Gene {symbol: $gene}), (di:Disease {name: $disease})
               MERGE (g)-[:ASSOCIATED_WITH]->(di)""",
            {"gene": gene, "disease": disease},
        )
    print(f"  ✓ {len(ASSOCIATED_WITH)} ASSOCIATED_WITH relationships")

    for disease, symptom in HAS_SYMPTOM:
        conn.write(
            """MATCH (di:Disease {name: $disease}), (s:Symptom {name: $symptom})
               MERGE (di)-[:HAS_SYMPTOM]->(s)""",
            {"disease": disease, "symptom": symptom},
        )
    print(f"  ✓ {len(HAS_SYMPTOM)} HAS_SYMPTOM relationships")

    for drug, trial_id in TESTED_IN:
        conn.write(
            """MATCH (dr:Drug {name: $drug}), (t:Trial {trial_id: $trial_id})
               MERGE (dr)-[:TESTED_IN]->(t)""",
            {"drug": drug, "trial_id": trial_id},
        )
    print(f"  ✓ {len(TESTED_IN)} TESTED_IN relationships")

    for trial_id, disease in STUDIES:
        conn.write(
            """MATCH (t:Trial {trial_id: $trial_id}), (di:Disease {name: $disease})
               MERGE (t)-[:STUDIES]->(di)""",
            {"trial_id": trial_id, "disease": disease},
        )
    print(f"  ✓ {len(STUDIES)} STUDIES relationships")

    for drug_a, drug_b in INTERACTS_WITH:
        conn.write(
            """MATCH (a:Drug {name: $drug_a}), (b:Drug {name: $drug_b})
               MERGE (a)-[:INTERACTS_WITH]->(b)""",
            {"drug_a": drug_a, "drug_b": drug_b},
        )
    print(f"  ✓ {len(INTERACTS_WITH)} INTERACTS_WITH relationships")


def load_extracted(conn):
    """Load LLM-extracted entities/relationships from entity_extraction.py, if present.

    Nodes are tagged with source='llm_extracted' so you can distinguish
    provenance in the graph (vs. the hand-curated seed set, untagged).
    Uses the same MERGE pattern, so it's safe to run alongside or after
    load_nodes()/load_relationships() without creating duplicates.
    """
    if not EXTRACTED_DATA_PATH.exists():
        print(f"[extracted] no {EXTRACTED_DATA_PATH.name} found, skipping (run entity_extraction.py first)")
        return

    data = json.loads(EXTRACTED_DATA_PATH.read_text())
    print(f"[extracted] loading LLM-extracted entities from {EXTRACTED_DATA_PATH.name}...")

    for d in data.get("drugs", []):
        conn.write(
            """MERGE (n:Drug {name: $name})
               ON CREATE SET n.category = $category, n.mechanism_of_action = $mechanism_of_action, n.source = 'llm_extracted'""",
            d,
        )
    for d in data.get("diseases", []):
        conn.write(
            """MERGE (n:Disease {name: $name})
               ON CREATE SET n.category = $category, n.description = $description, n.source = 'llm_extracted'""",
            d,
        )
    for g in data.get("genes", []):
        conn.write(
            """MERGE (n:Gene {symbol: $symbol})
               ON CREATE SET n.name = $name, n.source = 'llm_extracted'""",
            g,
        )
    print(
        f"  ✓ {len(data.get('drugs', []))} Drug, {len(data.get('diseases', []))} Disease, "
        f"{len(data.get('genes', []))} Gene nodes merged"
    )

    for r in data.get("treats", []):
        conn.write(
            """MATCH (dr:Drug {name: $drug}), (di:Disease {name: $disease})
               MERGE (dr)-[:TREATS]->(di)""",
            r,
        )
    for r in data.get("targets", []):
        conn.write(
            """MATCH (dr:Drug {name: $drug}), (g:Gene {symbol: $gene})
               MERGE (dr)-[:TARGETS]->(g)""",
            r,
        )
    for r in data.get("associated_with", []):
        conn.write(
            """MATCH (g:Gene {symbol: $gene}), (di:Disease {name: $disease})
               MERGE (g)-[:ASSOCIATED_WITH]->(di)""",
            r,
        )
    print(
        f"  ✓ {len(data.get('treats', []))} TREATS, {len(data.get('targets', []))} TARGETS, "
        f"{len(data.get('associated_with', []))} ASSOCIATED_WITH relationships merged"
    )


def load_all():
    conn = get_connection()
    try:
        load_nodes(conn)
        load_relationships(conn)
        load_extracted(conn)
        print("\nOncology knowledge graph loaded successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    load_all()
