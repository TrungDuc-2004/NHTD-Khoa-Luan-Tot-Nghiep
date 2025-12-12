#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, argparse
from datetime import datetime
from typing import Dict, Any, List
from pymongo import MongoClient, ASCENDING, TEXT

# ==============================
# CONFIG
# ==============================
DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DEFAULT_DB_NAME   = os.getenv("MONGO_DB", "data_kl")
COLLECTION_NAME   = "practices"

REQUIRED_HEADERS: List[str] = ["practice_id", "practice_name"]
OPTIONAL_HEADERS: List[str] = ["practice_url", "keyword"]


# ==============================
# INDEX
# ==============================
def ensure_indexes(db):
    col = db[COLLECTION_NAME]
    col.create_index([("practice_id", ASCENDING)], unique=True, name="uniq_practice_id")
    col.create_index([("practice_name", TEXT)], name="txt_practice_name")


# ==============================
# VALIDATE CSV
# ==============================
def validate_headers(headers: List[str]) -> None:
    if not headers:
        raise ValueError("CSV rỗng hoặc không đọc được header.")

    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        raise ValueError(f"CSV thiếu cột bắt buộc: {', '.join(missing)}")


# ==============================
# NORMALIZE ROW
# ==============================
def normalize_row(row: Dict[str, str]) -> Dict[str, Any]:
    doc = {
        "practice_id": (row.get("practice_id") or "").strip(),
        "practice_name": (row.get("practice_name") or "").strip(),
    }

    # practice_url
    url = (row.get("practice_url") or "").strip()
    doc["practice_url"] = url if url else "null"

    # keyword xử lý thành list
    raw_kw = (row.get("keyword") or "").strip()
    if raw_kw:
        # dạng: A; B; C → ["A","B","C"]
        kws = [k.strip() for k in raw_kw.split(";") if k.strip()]
        doc["keyword"] = kws
    else:
        doc["keyword"] = []

    return doc


# ==============================
# UPSERT PRACTICE
# ==============================
def upsert_practice(col, item: Dict[str, Any], dry_run: bool = False):
    if not item["practice_id"] or not item["practice_name"]:
        raise ValueError("Các trường practice_id và practice_name không được rỗng.")

    now = datetime.utcnow()

    if dry_run:
        existed = col.find_one({"practice_id": item["practice_id"]}, {"_id": 1})
        return ("UPDATE" if existed else "INSERT", None)

    res = col.update_one(
        {"practice_id": item["practice_id"]},
        {
            "$set": {
                "practice_name": item["practice_name"],
                "practice_url": item["practice_url"],
                "keyword": item["keyword"],
                "updatedAt": now,
            },
            "$setOnInsert": { "createdAt": now },
        },
        upsert=True
    )

    if res.upserted_id:
        return ("INSERT", res.upserted_id)

    doc = col.find_one({"practice_id": item["practice_id"]}, {"_id": 1})
    return ("UPDATE", doc["_id"] if doc else None)


# ==============================
# IMPORT CSV
# ==============================
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
                action, oid = upsert_practice(col, item, dry_run=dry_run)

                total += 1
                if action == "INSERT": ins += 1
                if action == "UPDATE": upd += 1

                print(f"[{i}] {action} practice_id='{item['practice_id']}'" +
                      ("" if dry_run else f" -> _id={oid}"))

            except Exception as e:
                err += 1
                print(f"[{i}] ERROR practice_id={row.get('practice_id')} : {e}")

    print("\n=== SUMMARY ===")
    print(f"Total rows : {total}")
    print(f"Inserted   : {ins}")
    print(f"Updated    : {upd}")
    print(f"Errors     : {err}")
    print(f"DB         : {db_name}")
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Mongo URI  : {mongo_uri}")
    if dry_run:
        print("[NOTE] dry-run: không ghi DB.]")

# ==============================
# MAIN
# ==============================
def parse_args():
    p = argparse.ArgumentParser(description="Import CSV 'practices' vào MongoDB (upsert theo practice_id)")
    p.add_argument("--csv", required=True, help="Đường dẫn CSV, ví dụ: csv/practice.csv")
    p.add_argument("--mongo_uri", default=DEFAULT_MONGO_URI)
    p.add_argument("--db", default=DEFAULT_DB_NAME)
    p.add_argument("--dry_run", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    import_csv(args.csv, args.mongo_uri, args.db, args.dry_run)
