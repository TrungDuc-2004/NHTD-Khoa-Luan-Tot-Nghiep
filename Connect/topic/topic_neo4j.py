#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "data_kl"
COLLECTION = "topics"

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

mongo = MongoClient(MONGO_URI)[DB_NAME][COLLECTION]
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def create_topic(tx, doc):
    tx.run("""
        MERGE (t:Topic {mongo_id: $mongo_id})
        SET t.topic_id = $topic_id,
            t.topic_name = $topic_name,
            t.topic_url = $topic_url
    """, mongo_id=str(doc["_id"]),
         topic_id=doc.get("topic_id"),
         topic_name=doc.get("topic_name"),
         topic_url=doc.get("topic_url"))

if __name__ == "__main__":
    data = list(mongo.find({}))
    total = len(data)
    with driver.session() as session:
        for i, doc in enumerate(data, 1):
            session.execute_write(create_topic, doc)
            print(f"[{i}/{total}] Imported Topic: {doc.get('topic_name')}")
    print("\n Done: Imported all Topics into Neo4j.")
