"""Neo4j connection wrapper."""

import os

from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "oncology2024!")


class Neo4jConnection:
    """Thin wrapper around the Neo4j driver with a query() convenience method."""

    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, cypher: str, params: dict | None = None) -> list[dict]:
        with self._driver.session() as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]

    def write(self, cypher: str, params: dict | None = None) -> None:
        with self._driver.session() as session:
            session.run(cypher, params or {})

    def verify_connectivity(self):
        self._driver.verify_connectivity()


def get_connection() -> Neo4jConnection:
    return Neo4jConnection()
