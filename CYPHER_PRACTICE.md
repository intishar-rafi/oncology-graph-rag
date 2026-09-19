# Interesting Cypher queries to try in the Neo4j Browser

```cypher
-- All drugs that target EGFR
MATCH (d:Drug)-[:TARGETS]->(g:Gene {symbol: 'EGFR'})
RETURN d.name, d.mechanism_of_action

-- Genes associated with more than one cancer type
MATCH (g:Gene)-[:ASSOCIATED_WITH]->(di:Disease)
WITH g, count(di) AS disease_count, collect(di.name) AS diseases
WHERE disease_count > 1
RETURN g.symbol, diseases

-- Drugs tested in Phase 3 trials for melanoma
MATCH (d:Drug)-[:TESTED_IN]->(t:Trial)-[:STUDIES]->(di:Disease {name: 'Melanoma'})
WHERE t.phase = 'Phase 3'
RETURN d.name, t.title, t.status

-- Shortest path between two drugs through shared gene targets
MATCH path = shortestPath(
    (a:Drug {name: 'Trastuzumab'})-[*]-(b:Drug {name: 'Olaparib'})
)
RETURN [n IN nodes(path) | coalesce(n.name, n.symbol, n.trial_id)] AS path, length(path) AS hops

-- Diseases sharing a symptom
MATCH (d1:Disease)-[:HAS_SYMPTOM]->(s:Symptom)<-[:HAS_SYMPTOM]-(d2:Disease)
WHERE d1.name < d2.name
RETURN s.name, d1.name, d2.name

-- Full drug-gene-disease chain for immunotherapies
MATCH (d:Drug {category: 'Immunotherapy'})-[:TARGETS]->(g:Gene)
OPTIONAL MATCH (d)-[:TREATS]->(di:Disease)
RETURN d.name, g.symbol, collect(di.name) AS treats
```
