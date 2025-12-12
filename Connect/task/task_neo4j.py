#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase

# ======================
# CONFIG
# ======================
MONGO_URI   = "mongodb://localhost:27017"
DB_NAME     = "data_kl"
COLLECTION  = "tasks"

NEO4J_URI   = "bolt://127.0.0.1:7687"
NEO4J_USER  = "neo4j"
NEO4J_PASS  = "12345678"


# ======================
# CONNECT
# ======================
mongo  = MongoClient(MONGO_URI)[DB_NAME][COLLECTION]
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# ======================
# CREATE / UPDATE TASK
# ======================
def create_or_update_task(tx, doc):
    tx.run("""
        MERGE (t:Task {mongo_id: $mongo_id})
        SET t.task_id   = $task_id,
            t.task_name = $task_name,
            t.task_url  = $task_url
    """,
    mongo_id=str(doc["_id"]),
    task_id=doc.get("task_id"),
    task_name=doc.get("task_name"),
    task_url=doc.get("task_url")
    )


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    data  = list(mongo.find({}))
    total = len(data)

    with driver.session() as session:
        for i, doc in enumerate(data, start=1):
            session.execute_write(create_or_update_task, doc)
            print(f"[{i}/{total}] Imported Task: {doc.get('task_id')}")

    print("\nDone: All Tasks imported into Neo4j!")
