#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase

# ============================
# CONFIG
# ============================
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "data_kl"
COLLECTION = "classes"

NEO4J_URI  = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

# ============================
# CONNECT
# ============================
mongo = MongoClient(MONGO_URI)[DB_NAME][COLLECTION]
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# ============================
# CREATE / UPDATE CLASS
# ============================
def create_or_update_class(tx, doc):
    tx.run(
        """
        MERGE (c:Class {mongo_id: $mongo_id})
        SET c.class_id   = $class_id,
            c.class_name = $class_name,
            c.class_url  = $class_url
        """,
        mongo_id=str(doc["_id"]),
        class_id=doc.get("class_id"),
        class_name=doc.get("class_name"),
        class_url=doc.get("class_url")  # nếu không có thì = None
    )


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    data = list(mongo.find({}))
    total = len(data)

    with driver.session() as session:
        for i, doc in enumerate(data, start=1):
            session.execute_write(create_or_update_class, doc)
            print(f"[{i}/{total}] Imported Class: {doc.get('class_name')}")

    print("\nDone: All Classes imported to Neo4j.")
