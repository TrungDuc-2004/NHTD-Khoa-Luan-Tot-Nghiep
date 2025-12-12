#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, argparse
from typing import Dict, Any
from pymongo import MongoClient, ASCENDING, TEXT

DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DEFAULT_DB_NAME   = os.getenv("MONGO_DB", "data_kl")
COLLECTION_NAME   = "subjects"

REQUIRED_HEADERS = ["subject_id", "subject_name"]

def ensure_indexes(db):
    col = db[COLLECTION_NAME]
    col.create_index([("subject_id", ASCENDING)], unique=True, name="uniq_subject_id")
    col.create_index([("subject_name", TEXT)], name="txt_subject_name")

def validate_headers(headers):
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise ValueError(f"CSV thiếu cột: {', '.join(missing)}")

def normalize_row(row: Dict[str, str]) -> Dict[str, Any]:
    return {
        "subject_id": (row.get("subject_id") or "").strip(),
        "subject_name": (row.get("subject_name") or "").strip()
    }

def upsert_subject(col, item: Dict[str, Any]):
    if not item["subject_id"] or not item["subject_name"]:
        raise ValueError("subject_id và subject_name không được rỗng.")
    res = col.update_one(
        {"subject_id": item["subject_id"]},
        {"$set": {"subject_name": item["subject_name"]}},
        upsert=True
    )
    if res.upserted_id:
        return res.upserted_id
    doc = col.find_one({"subject_id": item["subject_id"]}, {"_id": 1})
    return doc["_id"]

def import_csv(csv_path: str, mongo_uri: str, db_name: str):
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
                existed = col.find_one({"subject_id": item["subject_id"]})
                _id = upsert_subject(col, item)
                total += 1
                if existed: upd += 1
                else: ins += 1
                print(f"[{i}] UPSERT subject_id={item['subject_id']} -> _id={_id}")
            except Exception as e:
                err += 1
                print(f"[{i}] ERROR: {e}")

    print(f"\nTotal={total}, Inserted={ins}, Updated={upd}, Errors={err}")

def parse_args():
    p = argparse.ArgumentParser(description="Import CSV Subject vào MongoDB")
    p.add_argument("--csv", required=True)
    p.add_argument("--mongo_uri", default=DEFAULT_MONGO_URI)
    p.add_argument("--db", default=DEFAULT_DB_NAME)
    return p.parse_args()

if __name__ == "__main__":
    a = parse_args()
    import_csv(a.csv, a.mongo_uri, a.db)