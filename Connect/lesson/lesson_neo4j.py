#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from neo4j import GraphDatabase

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "data_kl"
COLLECTION = "lessons"

NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

# Mongo
mongo = MongoClient(MONGO_URI)[DB_NAME][COLLECTION]

# Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


def create_or_update_lesson(tx, doc):
    tx.run("""
        MERGE (l:Lesson {mongo_id: $mongo_id})
        SET l.lesson_id   = $lesson_id,
            l.lesson_name = $lesson_name,
            l.lesson_url  = $lesson_url,
            l.keyword     = $keyword
    """,
    mongo_id=str(doc["_id"]),
    lesson_id=doc.get("lesson_id"),
    lesson_name=doc.get("lesson_name"),
    lesson_url=doc.get("lesson_url"),
    keyword=doc.get("keyword", [])
    )


if __name__ == "__main__":
    data = list(mongo.find({}))
    total = len(data)

    with driver.session() as session:
        for i, doc in enumerate(data, 1):
            session.execute_write(create_or_update_lesson, doc)
            print(f"[{i}/{total}] Updated Lesson: {doc.get('lesson_name')}")

    print("\nDone: Updated all lessons into Neo4j with keyword.")
