#!/usr/bin/env python
# -*- coding: utf-8 -*-

from neo4j import GraphDatabase

NEO4J_URI  = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "12345678"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ==========================================
# CONSTRAINTS + INDEXES
# ==========================================
CREATE_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Subject) REQUIRE s.mongo_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Class)   REQUIRE c.mongo_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Topic)   REQUIRE t.mongo_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Lesson)  REQUIRE l.mongo_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (sec:Section) REQUIRE sec.mongo_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Practice) REQUIRE p.mongo_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (tk:Task)    REQUIRE tk.mongo_id IS UNIQUE",

    "CREATE INDEX IF NOT EXISTS FOR (s:Subject) ON (s.subject_id)",
    "CREATE INDEX IF NOT EXISTS FOR (c:Class)   ON (c.class_id)",
    "CREATE INDEX IF NOT EXISTS FOR (t:Topic)   ON (t.topic_id)",
    "CREATE INDEX IF NOT EXISTS FOR (l:Lesson)  ON (l.lesson_id)",
    "CREATE INDEX IF NOT EXISTS FOR (sec:Section) ON (sec.section_id)",
    "CREATE INDEX IF NOT EXISTS FOR (p:Practice) ON (p.practice_id)",
    "CREATE INDEX IF NOT EXISTS FOR (tk:Task) ON (tk.task_id)"
]

# ==========================================
# RELATIONS — FINAL STRUCTURE
# ==========================================

# 1. Class → Subject
Q_CLASS_SUBJECT = """
MATCH (c:Class), (s:Subject)
WHERE c.class_id STARTS WITH s.subject_id
MERGE (c)-[r:HAS_SUBJECT]->(s)
RETURN count(r) AS total
"""

# 2. Subject → Topic
Q_SUBJECT_TOPIC = """
MATCH (s:Subject), (t:Topic)
WHERE t.topic_id STARTS WITH s.subject_id
MERGE (s)-[r:HAS_TOPIC]->(t)
RETURN count(r) AS total
"""

# 3. Topic → Lesson
Q_TOPIC_LESSON = """
MATCH (t:Topic), (l:Lesson)
WHERE l.lesson_id STARTS WITH t.topic_id
MERGE (t)-[r:HAS_LESSON]->(l)
RETURN count(r) AS total
"""

# 4. Lesson → Section
Q_LESSON_SECTION = """
MATCH (l:Lesson), (s:Section)
WHERE s.section_id STARTS WITH l.lesson_id
MERGE (l)-[r:HAS_SECTION]->(s)
RETURN count(r) AS total
"""

# 5. Topic → Practice
Q_TOPIC_PRACTICE = """
MATCH (t:Topic), (p:Practice)
WHERE p.practice_id STARTS WITH t.topic_id
MERGE (t)-[r:HAS_PRACTICE]->(p)
RETURN count(r) AS total
"""

# 6. Practice → Task (NEW)
Q_PRACTICE_TASK = """
MATCH (p:Practice), (tk:Task)
WHERE tk.task_id STARTS WITH p.practice_id
MERGE (p)-[r:HAS_TASK]->(tk)
RETURN count(r) AS total
"""

# ==========================================
# MAIN RUNNER
# ==========================================
def run_queries():
    with driver.session() as session:
        # run constraints
        for q in CREATE_CONSTRAINTS:
            session.run(q)

        print("Creating HAS_SUBJECT...")
        print(session.run(Q_CLASS_SUBJECT).single()["total"])

        print("Creating HAS_TOPIC...")
        print(session.run(Q_SUBJECT_TOPIC).single()["total"])

        print("Creating HAS_LESSON...")
        print(session.run(Q_TOPIC_LESSON).single()["total"])

        print("Creating HAS_SECTION...")
        print(session.run(Q_LESSON_SECTION).single()["total"])

        print("Creating HAS_PRACTICE...")
        print(session.run(Q_TOPIC_PRACTICE).single()["total"])

        print("Creating HAS_TASK...")
        print(session.run(Q_PRACTICE_TASK).single()["total"])


if __name__ == "__main__":
    run_queries()
    print("\nDONE — All relationships updated (INCLUDING TASK)!")
