#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "data_kl"
COLLECTION = "practices"

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

mongo = MongoClient(MONGO_URI)[DB_NAME][COLLECTION]
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


def create_or_update_practice(tx, doc):
    tx.run("""
        MERGE (p:Practice {mongo_id: $mongo_id})
        SET p.practice_id   = $practice_id,
            p.practice_name = $practice_name,
            p.practice_url  = $practice_url,
            p.keyword       = $keyword
    """,
    mongo_id=str(doc["_id"]),
    practice_id=doc.get("practice_id"),
    practice_name=doc.get("practice_name"),
    practice_url=doc.get("practice_url"),
    keyword=doc.get("keyword", [])
    )


if __name__ == "__main__":
    data = list(mongo.find({}))
    total = len(data)

    with driver.session() as session:
        for i, doc in enumerate(data, 1):
            session.execute_write(create_or_update_practice, doc)
            print(f"[{i}/{total}] Imported Practice: {doc.get('practice_id')}")

    print("\nDone: Imported all practices into Neo4j.")
