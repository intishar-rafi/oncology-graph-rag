"""
Optional live data fetcher for the oncology knowledge graph.

Pulls real target-disease-drug data from the Open Targets Platform
GraphQL API (https://api.platform.opentargets.org) and trial records
from the ClinicalTrials.gov API v2 (https://clinicaltrials.gov/api/v2),
then writes a cached JSON snapshot that `loader.py` can ingest instead
of (or alongside) the hand-curated `oncology_data.py` seed set.

This script makes outbound HTTPS calls, so run it from a machine with
normal internet access (it will not work inside network-sandboxed
environments). Re-running is safe; it overwrites the cache file.

Usage:
    python fetch_oncology_data.py

Output:
    data/oncology_live_cache.json
"""

import json
import time
from pathlib import Path

import requests

OPEN_TARGETS_URL = "https://api.platform.opentargets.org/api/v4/graphql"
CLINICAL_TRIALS_URL = "https://clinicaltrials.gov/api/v2/studies"
CACHE_PATH = Path(__file__).parent / "oncology_live_cache.json"

# A representative set of cancer types to seed the graph from.
# Extend this list to pull a larger dataset.
SEED_DISEASE_QUERIES = [
    "HER2-positive breast cancer",
    "non-small cell lung cancer",
    "chronic myeloid leukemia",
    "melanoma",
    "colorectal cancer",
    "gastrointestinal stromal tumor",
    "renal cell carcinoma",
    "diffuse large B-cell lymphoma",
    "ovarian cancer",
    "prostate cancer",
    "multiple myeloma",
    "hepatocellular carcinoma",
    "pancreatic ductal adenocarcinoma",
    "bladder cancer",
]

DISEASE_SEARCH_QUERY = """
query DiseaseSearch($q: String!) {
  search(queryString: $q, entityNames: ["disease"], page: {index: 0, size: 1}) {
    hits { id name entity }
  }
}
"""

DISEASE_TARGETS_QUERY = """
query DiseaseTargets($efoId: String!) {
  disease(efoId: $efoId) {
    id
    name
    description
    associatedTargets(page: {index: 0, size: 15}) {
      rows {
        score
        target {
          id
          approvedSymbol
          approvedName
          genomicLocation { chromosome }
        }
      }
    }
  }
}
"""

TARGET_DRUGS_QUERY = """
query TargetDrugs($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    id
    approvedSymbol
    drugAndClinicalCandidates {
      rows {
        drug {
          id
          name
          drugType
          maximumClinicalStage
          mechanismsOfAction {
            rows { mechanismOfAction actionType }
          }
        }
      }
    }
  }
}
"""


def gql(query: str, variables: dict) -> dict:
    resp = requests.post(
        OPEN_TARGETS_URL,
        json={"query": query, "variables": variables},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def fetch_clinical_trials(condition: str, page_size: int = 5) -> list:
    resp = requests.get(
        CLINICAL_TRIALS_URL,
        params={
            "query.cond": condition,
            "pageSize": page_size,
            "fields": "NCTId,BriefTitle,Phase,OverallStatus,StartDate",
        },
        timeout=30,
    )
    resp.raise_for_status()
    studies = resp.json().get("studies", [])
    out = []
    for s in studies:
        protocol = s.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        out.append({
            "trial_id": ident.get("nctId"),
            "title": ident.get("briefTitle"),
            "phase": (design.get("phases") or ["N/A"])[0],
            "status": status.get("overallStatus"),
            "start_date": status.get("startDateStruct", {}).get("date"),
        })
    return out


def main():
    diseases, genes, drugs = {}, {}, {}
    associated_with, targets_rel, treats_placeholder, trials = [], [], [], {}

    for disease_query in SEED_DISEASE_QUERIES:
        print(f"[disease] searching: {disease_query}")
        hits = gql(DISEASE_SEARCH_QUERY, {"q": disease_query})["search"]["hits"]
        if not hits:
            print(f"  no match, skipping")
            continue
        efo_id = hits[0]["id"]

        detail = gql(DISEASE_TARGETS_QUERY, {"efoId": efo_id})["disease"]
        if not detail:
            continue
        diseases[efo_id] = {
            "id": efo_id,
            "name": detail["name"],
            "description": detail.get("description") or "",
            "category": disease_query,
        }

        for row in detail["associatedTargets"]["rows"]:
            t = row["target"]
            genes[t["id"]] = {
                "symbol": t["approvedSymbol"],
                "name": t["approvedName"],
                "chromosome": (t.get("genomicLocation") or {}).get("chromosome", ""),
            }
            associated_with.append({"gene_id": t["id"], "disease_id": efo_id, "score": row["score"]})

        # pull real trials for this condition too
        try:
            trials[disease_query] = fetch_clinical_trials(disease_query)
        except Exception as e:
            print(f"  trial fetch failed: {e}")

        time.sleep(0.3)  # be polite to the API

    # for the top few genes, pull known drugs targeting them
    for gene_id, gene in list(genes.items())[:20]:
        print(f"[target] fetching drugs for {gene['symbol']}")
        try:
            detail = gql(TARGET_DRUGS_QUERY, {"ensemblId": gene_id})["target"]
        except Exception as e:
            print(f"  failed: {e}")
            continue
        if not detail:
            continue
        for row in detail["drugAndClinicalCandidates"]["rows"]:
            d = row["drug"]
            if not d:
                continue
            drugs[d["id"]] = {
                "name": d["name"],
                "drug_type": d["drugType"],
                "clinical_stage": d.get("maximumClinicalStage"),
                "mechanism_of_action": (
                    d["mechanismsOfAction"]["rows"][0]["mechanismOfAction"]
                    if d.get("mechanismsOfAction") and d["mechanismsOfAction"]["rows"]
                    else ""
                ),
            }
            targets_rel.append({"drug_id": d["id"], "gene_id": gene_id})
        time.sleep(0.3)

    cache = {
        "diseases": list(diseases.values()),
        "genes": list(genes.values()),
        "drugs": list(drugs.values()),
        "associated_with": associated_with,
        "targets": targets_rel,
        "trials": trials,
    }
    CACHE_PATH.write_text(json.dumps(cache, indent=2))
    print(f"\nWrote {CACHE_PATH} with {len(diseases)} diseases, {len(genes)} genes, {len(drugs)} drugs.")


if __name__ == "__main__":
    main()
