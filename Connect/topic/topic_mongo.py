#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, argparse
from typing import Dict, Any
from pymongo import MongoClient, ASCENDING, TEXT

DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DEFAULT_DB_NAME   = os.getenv("MONGO_DB", "data_kl")
COLLECTION_NAME   = "topics"

REQUIRED_HEADERS = ["topic_id", "topic_name"]
OPTIONAL_HEADERS = ["topic_url"]

def ensure_indexes(db):
    col = db[COLLECTION_NAME]
    col.create_index([("topic_id", ASCENDING)], unique=True, name="uniq_topic_id")
    col.create_index([("topic_name", TEXT)], name="txt_topic_name")

def validate_headers(headers):
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise ValueError(f"CSV thiếu cột: {', '.join(missing)}")

def normalize_row(row: Dict[str, str]) -> Dict[str, Any]:
    doc = {
        "topic_id": (row.get("topic_id") or "").strip(),
        "topic_name": (row.get("topic_name") or "").strip()
    }
    if "topic_url" in row and row["topic_url"].strip():
        doc["topic_url"] = row["topic_url"].strip()
    return doc

def upsert_topic(col, item: Dict[str, Any]):
    if not item["topic_id"] or not item["topic_name"]:
        raise ValueError("topic_id và topic_name không được rỗng.")
    res = col.update_one(
        {"topic_id": item["topic_id"]},
        {"$set": item},
        upsert=True
    )
    if res.upserted_id:
        return res.upserted_id
    doc = col.find_one({"topic_id": item["topic_id"]}, {"_id": 1})
    return doc["_id"]

def import_csv(csv_path, mongo_uri, db_name):
    if not os.path.exists(csv_path):
        print(f"[ERROR] Không tìm thấy file: {csv_path}")
        sys.exit(1)
    client = MongoClient(mongo_uri)
    db = client[db_name]
    col = db[COLLECTION_NAME]
    ensure_indexes(db)

    total = ins = upd = err = 0
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        validate_headers(reader.fieldnames or [])
        for i, row in enumerate(reader, 1):
            try:
                item = normalize_row(row)
                existed = col.find_one({"topic_id": item["topic_id"]})
                _id = upsert_topic(col, item)
                total += 1
                if existed: upd += 1
                else: ins += 1
                print(f"[{i}] UPSERT topic_id={item['topic_id']} -> _id={_id}")
            except Exception as e:
                err += 1
                print(f"[{i}] ERROR: {e}")
    print(f"\nTotal={total}, Inserted={ins}, Updated={upd}, Errors={err}")

def parse_args():
    p = argparse.ArgumentParser(description="Import CSV Topic vào MongoDB")
    p.add_argument("--csv", required=True)
    p.add_argument("--mongo_uri", default=DEFAULT_MONGO_URI)
    p.add_argument("--db", default=DEFAULT_DB_NAME)
    return p.parse_args()

if __name__ == "__main__":
    a = parse_args()
    import_csv(a.csv, a.mongo_uri, a.db)
