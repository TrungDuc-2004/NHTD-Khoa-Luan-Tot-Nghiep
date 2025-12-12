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
COLLECTION_NAME   = "tasks"

REQUIRED_HEADERS: List[str] = ["task_id", "task_name"]
OPTIONAL_HEADERS: List[str] = ["task_url"]


# ==============================
# INDEX
# ==============================
def ensure_indexes(db):
    col = db[COLLECTION_NAME]
    col.create_index([("task_id", ASCENDING)], unique=True, name="uniq_task_id")
    col.create_index([("task_name", TEXT)], name="txt_task_name")


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
        "task_id": (row.get("task_id") or "").strip(),
        "task_name": (row.get("task_name") or "").strip(),
    }

    url = (row.get("task_url") or "").strip()
    doc["task_url"] = url if url else "null"

    return doc


# ==============================
# UPSERT TASK
# ==============================
def upsert_task(col, item: Dict[str, Any], dry_run: bool = False):
    if not item["task_id"] or not item["task_name"]:
        raise ValueError("task_id và task_name không được rỗng.")

    now = datetime.utcnow()

    if dry_run:
        existed = col.find_one({"task_id": item["task_id"]}, {"_id": 1})
        return ("UPDATE" if existed else "INSERT", None)

    res = col.update_one(
        {"task_id": item["task_id"]},
        {
            "$set": {
                "task_name": item["task_name"],
                "task_url": item["task_url"],
                "updatedAt": now,
            },
            "$setOnInsert": { "createdAt": now },
        },
        upsert=True
    )

    if res.upserted_id:
        return ("INSERT", res.upserted_id)

    doc = col.find_one({"task_id": item["task_id"]}, {"_id": 1})
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
                action, oid = upsert_task(col, item, dry_run=dry_run)

                total += 1
                if action == "INSERT": ins += 1
                if action == "UPDATE": upd += 1

                print(f"[{i}] {action} task_id='{item['task_id']}'"
                      + ("" if dry_run else f" -> _id={oid}"))

            except Exception as e:
                err += 1
                print(f"[{i}] ERROR task_id={row.get('task_id')} : {e}")

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
    p = argparse.ArgumentParser(description="Import CSV 'tasks' vào MongoDB (upsert theo task_id)")
    p.add_argument("--csv", required=True, help="Đường dẫn CSV, ví dụ: csv/task.csv")
    p.add_argument("--mongo_uri", default=DEFAULT_MONGO_URI)
    p.add_argument("--db", default=DEFAULT_DB_NAME)
    p.add_argument("--dry_run", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    import_csv(args.csv, args.mongo_uri, args.db, args.dry_run)
