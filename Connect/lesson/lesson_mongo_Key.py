#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, argparse
from datetime import datetime
from typing import Dict, Any, List
from pymongo import MongoClient, ASCENDING, TEXT

# --- ENV / defaults ---
DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DEFAULT_DB_NAME   = os.getenv("MONGO_DB", "data_kl")
COLLECTION_NAME   = "lessons"

REQUIRED_HEADERS: List[str] = ["lesson_id", "lesson_name"]
OPTIONAL_HEADERS: List[str] = ["lesson_url", "keyword"]

def ensure_indexes(db):
    col = db[COLLECTION_NAME]
    col.create_index([("lesson_id", ASCENDING)], unique=True, name="uniq_lesson_id")
    col.create_index([("lesson_name", TEXT)], name="txt_lesson_name")

def validate_headers(headers: List[str]) -> None:
    if not headers:
        raise ValueError("CSV rỗng hoặc không đọc được header.")
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise ValueError(f"CSV thiếu cột bắt buộc: {', '.join(missing)}")

def normalize_row(row: Dict[str, str]) -> Dict[str, Any]:
    doc = {
        "lesson_id": (row.get("lesson_id") or "").strip(),
        "lesson_name": (row.get("lesson_name") or "").strip(),
    }

    url = (row.get("lesson_url") or "").strip()
    if url:
        doc["lesson_url"] = url

    kw = (row.get("keyword") or "").strip()
    if kw:
        doc["keyword"] = [k.strip() for k in kw.split(";") if k.strip()]

    return doc

def upsert_lesson(col, item: Dict[str, Any], dry_run: bool = False):
    if not item["lesson_id"] or not item["lesson_name"]:
        raise ValueError("lesson_id và lesson_name không được rỗng.")

    now = datetime.utcnow()

    # build update data safely
    update_data = {
        "lesson_name": item["lesson_name"],
        "updatedAt": now
    }

    if "lesson_url" in item:
        update_data["lesson_url"] = item["lesson_url"]

    if "keyword" in item:
        update_data["keyword"] = item["keyword"]

    if dry_run:
        existed = col.find_one({"lesson_id": item["lesson_id"]}, {"_id": 1})
        return ("UPDATE" if existed else "INSERT", None)

    res = col.update_one(
        {"lesson_id": item["lesson_id"]},
        {
            "$set": update_data,
            "$setOnInsert": {"createdAt": now},
        },
        upsert=True
    )

    if res.upserted_id:
        return ("INSERT", res.upserted_id)

    doc = col.find_one({"lesson_id": item["lesson_id"]}, {"_id": 1})
    return ("UPDATE", doc["_id"] if doc else None)

def import_csv(csv_path: str, mongo_uri: str, db_name: str, dry_run: bool = False):
    if not os.path.exists(csv_path):
        print(f"[ERROR] Không tìm thấy file: {csv_path}")
        sys.exit(1)

    client = MongoClient(mongo_uri)
    db = client[db_name]
    col = db[COLLECTION_NAME]
    ensure_indexes(db)

    total = ins = upd = err = 0

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        validate_headers(reader.fieldnames or [])

        for i, row in enumerate(reader, 1):
            try:
                item = normalize_row(row)
                action, oid = upsert_lesson(col, item, dry_run=dry_run)

                total += 1
                if action == "INSERT": ins += 1
                if action == "UPDATE": upd += 1

                print(f"[{i}] {action} lesson_id='{item['lesson_id']}'")
            except Exception as e:
                err += 1
                print(f"[{i}] ERROR lesson_id={row.get('lesson_id')} : {e}")

    print("\n=== SUMMARY ===")
    print(f"Total rows : {total}")
    print(f"Inserted   : {ins}")
    print(f"Updated    : {upd}")
    print(f"Errors     : {err}")
    print(f"DB         : {db_name}")
    print(f"Collection : {COLLECTION_NAME}")
    if dry_run:
        print("[NOTE] Chạy dry-run: không ghi dữ liệu vào DB]")

def parse_args():
    p = argparse.ArgumentParser(description="Import CSV 'lessons' vào MongoDB (upsert theo lesson_id)")
    p.add_argument("--csv", required=True)
    p.add_argument("--mongo_uri", default=DEFAULT_MONGO_URI)
    p.add_argument("--db", default=DEFAULT_DB_NAME)
    p.add_argument("--dry_run", action="store_true")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    import_csv(args.csv, args.mongo_uri, args.db, args.dry_run)
