#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, argparse
from typing import Dict, Any
from pymongo import MongoClient, ASCENDING, TEXT

# connect mongoDB
DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DEFAULT_DB_NAME   = os.getenv("MONGO_DB", "data_kl")
COLLECTION_NAME   = "classes"


REQUIRED_HEADERS = ["class_id", "class_name"]
OPTIONAL_HEADERS = ["class_url"]

#Tạo index trong MongoDB
def ensure_indexes(db):
    col = db[COLLECTION_NAME]
    col.create_index([("class_id", ASCENDING)], unique=True, name="uniq_class_id")
    col.create_index([("class_name", TEXT)], name="txt_class_name")

#  check các cột bắt buộc trong CSV
def validate_headers(headers):
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise ValueError(f"CSV thiếu cột: {', '.join(missing)}")

# Chuẩn hóa dữ liệu từ CSV thành định dạng document MongoDB
def normalize_row(row: Dict[str, str]) -> Dict[str, Any]:
    doc = {
        "class_id": (row.get("class_id") or "").strip(),
        "class_name": (row.get("class_name") or "").strip()
    }
    if "class_url" in row and row["class_url"].strip():
        doc["class_url"] = row["class_url"].strip()
    return doc

def upsert_class(col, item: Dict[str, Any]):
    if not item["class_id"] or not item["class_name"]:
        raise ValueError("class_id và class_name không được rỗng.")
    res = col.update_one(
        {"class_id": item["class_id"]},
        {"$set": item},
        upsert=True
    )
    if res.upserted_id:
        return res.upserted_id
    doc = col.find_one({"class_id": item["class_id"]}, {"_id": 1})
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
                existed = col.find_one({"class_id": item["class_id"]})
                _id = upsert_class(col, item)
                total += 1
                if existed: upd += 1
                else: ins += 1
                print(f"[{i}] UPSERT class_id={item['class_id']} -> _id={_id}")
            except Exception as e:
                err += 1
                print(f"[{i}] ERROR: {e}")
    print(f"\nTotal={total}, Inserted={ins}, Updated={upd}, Errors={err}")

def parse_args():
    p = argparse.ArgumentParser(description="Import CSV Class vào MongoDB")
    p.add_argument("--csv", required=True)
    p.add_argument("--mongo_uri", default=DEFAULT_MONGO_URI)
    p.add_argument("--db", default=DEFAULT_DB_NAME)
    return p.parse_args()

if __name__ == "__main__":
    a = parse_args()
    import_csv(a.csv, a.mongo_uri, a.db)
