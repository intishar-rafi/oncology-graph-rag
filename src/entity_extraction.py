"""
Entity extraction pipeline: unstructured documents -> structured entities & relationships.

Reads the plain-text drug monographs in data/documents/, sends each one to
GPT-4o with a strict JSON schema (OpenAI structured outputs), and asks the
model to extract:
    - Drug entities (name, category, mechanism of action)
    - Disease entities (name, category, description)
    - Gene entities (symbol, name)
    - Relationships: TREATS (drug->disease), TARGETS (drug->gene),
      ASSOCIATED_WITH (gene->disease)

Results from every document are merged and deduplicated, then written to
data/extracted_data.json. Run this before loader.py if you want the graph
built from LLM-extracted facts instead of (or alongside) the hand-curated
oncology_data.py seed set.

Usage:
    python entity_extraction.py
"""

import json
import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"

DOCUMENTS_DIR = Path(__file__).parent / "data" / "documents"
OUTPUT_PATH = Path(__file__).parent / "data" / "extracted_data.json"

EXTRACTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "oncology_entity_extraction",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "drugs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "mechanism_of_action": {"type": "string"},
                        },
                        "required": ["name", "category", "mechanism_of_action"],
                        "additionalProperties": False,
                    },
                },
                "diseases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "description": {"type": "string"},
                        },
                        "required": ["name", "category", "description"],
                        "additionalProperties": False,
                    },
                },
                "genes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string"},
                            "name": {"type": "string"},
                        },
                        "required": ["symbol", "name"],
                        "additionalProperties": False,
                    },
                },
                "treats": {
                    "type": "array",
                    "description": "Drug-treats-Disease relationships, referencing drug/disease names above",
                    "items": {
                        "type": "object",
                        "properties": {
                            "drug": {"type": "string"},
                            "disease": {"type": "string"},
                        },
                        "required": ["drug", "disease"],
                        "additionalProperties": False,
                    },
                },
                "targets": {
                    "type": "array",
                    "description": "Drug-targets-Gene relationships, referencing drug/gene names above",
                    "items": {
                        "type": "object",
                        "properties": {
                            "drug": {"type": "string"},
                            "gene": {"type": "string"},
                        },
                        "required": ["drug", "gene"],
                        "additionalProperties": False,
                    },
                },
                "associated_with": {
                    "type": "array",
                    "description": "Gene-associated_with-Disease relationships, referencing gene/disease names above",
                    "items": {
                        "type": "object",
                        "properties": {
                            "gene": {"type": "string"},
                            "disease": {"type": "string"},
                        },
                        "required": ["gene", "disease"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["drugs", "diseases", "genes", "treats", "targets", "associated_with"],
            "additionalProperties": False,
        },
    },
}

SYSTEM_PROMPT = """\
You are a biomedical entity extraction system. Given a passage of text about \
an oncology drug, extract every Drug, Disease, and Gene entity mentioned, \
along with the relationships between them, and return them in the exact JSON \
schema provided.

Rules:
- Use the gene SYMBOL (e.g. "ERBB2", "EGFR", "BRAF"), not the full protein name, for gene.symbol.
- Disease names should be specific (e.g. "HER2-positive breast cancer", not just "cancer").
- Only extract relationships that are explicitly stated or clearly implied in the text.
- Do not invent facts that are not present in the passage.
- mechanism_of_action and description should be concise (1 sentence), derived from the text.
"""


def extract_from_document(text: str) -> dict:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format=EXTRACTION_SCHEMA,
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)


def merge_extractions(all_results: list[dict]) -> dict:
    """Merge + dedupe entities and relationships across all extracted documents."""
    drugs, diseases, genes = {}, {}, {}
    treats, targets, associated_with = set(), set(), set()

    for result in all_results:
        for d in result["drugs"]:
            drugs[d["name"]] = d
        for d in result["diseases"]:
            diseases[d["name"]] = d
        for g in result["genes"]:
            genes[g["symbol"]] = g
        for r in result["treats"]:
            treats.add((r["drug"], r["disease"]))
        for r in result["targets"]:
            targets.add((r["drug"], r["gene"]))
        for r in result["associated_with"]:
            associated_with.add((r["gene"], r["disease"]))

    return {
        "drugs": list(drugs.values()),
        "diseases": list(diseases.values()),
        "genes": list(genes.values()),
        "treats": [{"drug": d, "disease": di} for d, di in sorted(treats)],
        "targets": [{"drug": d, "gene": g} for d, g in sorted(targets)],
        "associated_with": [{"gene": g, "disease": di} for g, di in sorted(associated_with)],
    }


def run_extraction():
    doc_paths = sorted(DOCUMENTS_DIR.glob("*.txt"))
    if not doc_paths:
        raise FileNotFoundError(f"No documents found in {DOCUMENTS_DIR}")

    all_results = []
    for path in doc_paths:
        print(f"[extract] {path.name}...")
        text = path.read_text()
        try:
            result = extract_from_document(text)
            all_results.append(result)
            print(
                f"  ✓ {len(result['drugs'])} drugs, {len(result['diseases'])} diseases, "
                f"{len(result['genes'])} genes, {len(result['treats'])} TREATS, "
                f"{len(result['targets'])} TARGETS, {len(result['associated_with'])} ASSOCIATED_WITH"
            )
        except Exception as e:
            print(f"  ✗ failed: {e}")

    merged = merge_extractions(all_results)
    OUTPUT_PATH.write_text(json.dumps(merged, indent=2))
    print(
        f"\nWrote {OUTPUT_PATH}\n"
        f"Totals: {len(merged['drugs'])} drugs, {len(merged['diseases'])} diseases, "
        f"{len(merged['genes'])} genes, {len(merged['treats'])} TREATS, "
        f"{len(merged['targets'])} TARGETS, {len(merged['associated_with'])} ASSOCIATED_WITH"
    )


if __name__ == "__main__":
    run_extraction()
