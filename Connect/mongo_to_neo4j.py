#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase
from bson import ObjectId

# --- CONFIG ---
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "KLTN"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

# --- CONNECT ---
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def create_node(tx, label, props):
    query = f"""
    MERGE (n:{label} {{mongo_id: $mongo_id}})
    SET n += $props
    """
    tx.run(query, mongo_id=str(props["_id"]), props=props)

def import_collection(collection_name, label):
    col = db[collection_name]
    data = list(col.find({}))
    total = len(data)
    print(f"\n Importing {total} documents from '{collection_name}' to Neo4j node '{label}'")

    with driver.session() as session:
        for i, doc in enumerate(data, 1):
            doc["_id"] = str(doc["_id"])
            session.execute_write(create_node, label, doc)
            print(f"[{i}/{total}] Imported {label} ({doc.get(list(doc.keys())[1])})")

# --- RUN ---
if __name__ == "__main__":
    import_collection("subjects", "Subject")
    import_collection("classes", "Class")
    import_collection("topics", "Topic")
    import_collection("lessons", "Lesson")

    print("\nĐã import toàn bộ dữ liệu từ MongoDB sang Neo4j!")