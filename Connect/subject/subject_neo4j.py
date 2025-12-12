#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase

# ============================
# CONFIG
# ============================
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "data_kl"
COLLECTION = "subjects"

NEO4J_URI  = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

# ============================
# CONNECT
# ============================
mongo = MongoClient(MONGO_URI)[DB_NAME][COLLECTION]
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# ============================
# FUNCTION: IMPORT SUBJECT
# ============================
def create_or_update_subject(tx, doc):
    tx.run(
        """
        MERGE (s:Subject {mongo_id: $mongo_id})

        // Cập nhật dữ liệu
        SET s.subject_id   = $subject_id,
            s.subject_name = $subject_name,
            s.subject_url  = $subject_url
        """,
        mongo_id=str(doc["_id"]),
        subject_id=doc.get("subject_id"),
        subject_name=doc.get("subject_name"),
        subject_url=doc.get("subject_url")
    )


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    data = list(mongo.find({}))
    total = len(data)

    with driver.session() as session:
        for i, doc in enumerate(data, start=1):
            session.execute_write(create_or_update_subject, doc)
            print(f"[{i}/{total}] Imported Subject: {doc.get('subject_name')}")

    print("\nDone: All Subjects imported to Neo4j.")
