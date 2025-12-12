#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
from pymongo import MongoClient

# ================================
# CONFIG
# ================================
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB  = "data_kl"

PG_HOST = "localhost"
PG_DB   = "data"
PG_USER = "postgres"
PG_PASS = "12345678"

# ================================
# CONNECT
# ================================
mongo = MongoClient(MONGO_URI)[MONGO_DB]

pg = psycopg2.connect(
    host=PG_HOST,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASS
)
cur = pg.cursor()

# ================================
# TABLE DEFINITIONS
# ================================
TABLE_MAP = {
    "classes": ("class", ["class_id", "class_name", "mongo_id"]),
    "subjects": ("subject", ["subject_id", "subject_name", "mongo_id", "class_id"]),
    "topics": ("topic", ["topic_id", "topic_name", "mongo_id", "subject_id"]),
    "lessons": ("lesson", ["lesson_id", "lesson_name", "mongo_id", "topic_id"]),
    "sections": ("section", ["section_id", "section_name", "mongo_id", "lesson_id"]),
    "practices": ("practice", ["practice_id", "practice_name", "practice_url", "keyword", "mongo_id", "topic_id"]),
    "tasks": ("task", ["task_id", "task_name", "task_url", "mongo_id", "practice_id"])
}

# ================================
# UPSERT GENERIC
# ================================
def upsert(table, fields, record):
    placeholders = ",".join(["%s"] * len(fields))
    update_list = ",".join([f"{f}=EXCLUDED.{f}" for f in fields[1:]])

    sql = f"""
        INSERT INTO {table} ({",".join(fields)})
        VALUES ({placeholders})
        ON CONFLICT ({fields[0]})
        DO UPDATE SET {update_list};
    """

    cur.execute(sql, record)


# ================================
# AUTO MAP FK THEO PREFIX
# ================================
def resolve_fk(table, record):
    """Tự động tìm FK theo prefix ID."""

    # Subject cần class_id
    if table == "subject":
        if not record["class_id"]:
            prefix = record["subject_id"]   # VD: TH
            cur.execute("SELECT class_id FROM class WHERE class_id LIKE %s LIMIT 1", (prefix + "%",))
            r = cur.fetchone()
            if r: record["class_id"] = r[0]

    # Topic cần subject_id
    if table == "topic":
        if not record["subject_id"]:
            prefix = record["topic_id"]      # VD: TH10_CD2 → TH
            prefix = prefix.split("_")[0]    # lấy TH10
            cur.execute("SELECT subject_id FROM subject WHERE subject_id LIKE %s LIMIT 1", ("%TH%",))
            r = cur.fetchone()
            if r: record["subject_id"] = r[0]

    # Lesson cần topic_id
    if table == "lesson":
        if not record["topic_id"]:
            prefix = "_".join(record["lesson_id"].split("_")[:2])   # TH10_CD2
            cur.execute("SELECT topic_id FROM topic WHERE topic_id=%s LIMIT 1", (prefix,))
            r = cur.fetchone()
            if r: record["topic_id"] = r[0]

    # Section cần lesson_id
    if table == "section":
        if not record["lesson_id"]:
            prefix = "_".join(record["section_id"].split("_")[:3])  # TH10_CD2_L7
            cur.execute("SELECT lesson_id FROM lesson WHERE lesson_id=%s LIMIT 1", (prefix,))
            r = cur.fetchone()
            if r: record["lesson_id"] = r[0]

    # Practice cần topic_id
    if table == "practice":
        if not record["topic_id"]:
            prefix = "_".join(record["practice_id"].split("_")[:2])  # TH10_CD2
            cur.execute("SELECT topic_id FROM topic WHERE topic_id LIKE %s LIMIT 1", (prefix + "%",))
            r = cur.fetchone()
            if r: record["topic_id"] = r[0]

    # Task cần practice_id
    if table == "task":
        if not record["practice_id"]:
            prefix = "_".join(record["task_id"].split("_")[:3])      # TH10_CD2_P10
            cur.execute("SELECT practice_id FROM practice WHERE practice_id=%s LIMIT 1", (prefix,))
            r = cur.fetchone()
            if r: record["practice_id"] = r[0]

# ================================
# MAIN IMPORT
# ================================
def import_all():

    for col_name, (table, fields) in TABLE_MAP.items():
        data = list(mongo[col_name].find({}))

        print(f"\n=== Importing {col_name} → {table} ===")

        for doc in data:
            record = {}

            # lấy field từ Mongo
            for f in fields:
                if f == "mongo_id":
                    record[f] = str(doc["_id"])
                else:
                    record[f] = doc.get(f)

            # AUTO MAP FK
            resolve_fk(table, record)

            # convert keyword list → string
            if table == "practice" and isinstance(record.get("keyword"), list):
                record["keyword"] = "; ".join(record["keyword"])

            # Insert/update
            values = [record[f] for f in fields]
            upsert(table, fields, values)

            print(" → Imported:", record[fields[0]])

    pg.commit()
    print("\nDONE — All Mongo data imported to PostgreSQL!")


# ================================
# RUN
# ================================
if __name__ == "__main__":
    import_all()
    cur.close()
    pg.close()
