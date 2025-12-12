#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "data_kl"
COLLECTION = "sections"

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

# Mongo
mongo = MongoClient(MONGO_URI)[DB_NAME][COLLECTION]

# Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


def create_or_update_section(tx, doc):
    tx.run("""
        MERGE (s:Section {mongo_id: $mongo_id})
        SET s.section_id   = $section_id,
            s.section_name = $section_name,
            s.section_url  = $section_url
    """,
    mongo_id=str(doc["_id"]),
    section_id=doc.get("section_id"),
    section_name=doc.get("section_name"),
    section_url=doc.get("section_url")
    )


if __name__ == "__main__":
    data = list(mongo.find({}))
    total = len(data)

    with driver.session() as session:
        for i, doc in enumerate(data, 1):
            session.execute_write(create_or_update_section, doc)
            print(f"[{i}/{total}] Updated Section: {doc.get('section_id')}")

    print("\nDone: Imported all sections into Neo4j.")
