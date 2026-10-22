#!/usr/bin/env python3
"""ARGUS operational SQLite database utility.

The database is a mutable operational store. GitHub remains authoritative for
schema and identity governance. SharePoint may store the working SQLite file and
provide file version history.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "argus-operational-database-v1.sql"
PREFIX_BY_TYPE = {
    "POLICY": "POL",
    "STRATEGY_MASTER_PLAN": "STR",
    "PROGRAMME": "PRG",
    "PROJECT": "PRJ",
    "REQUIREMENT": "REQ",
    "PROCUREMENT_PLAN": "PLN",
    "PROCUREMENT_PACKAGE": "PKG",
    "PROCUREMENT_PROCESS": "PROC",
    "TENDER_SOLICITATION": "TND",
    "LOT": "LOT",
    "PROCUREMENT_ITEM": "ITM",
    "ENTITY": "ENT",
    "PERSON": "PER",
    "AWARD": "AWD",
    "CONTRACT": "CTR",
    "EVENT": "EVT",
    "DOCUMENT": "DOC",
    "SOURCE_RECORD": "SRC",
    "OBSERVATION": "OBS",
    "PRODUCT_SOLUTION": "PRD",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def create_db(path: Path, schema: Path = DEFAULT_SCHEMA) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = connect(path)
    db.executescript(schema.read_text())
    ts = now_iso()
    db.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('schema_version','1.0.0')")
    db.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('identity_standard','canonical-identity-standard-v1.0')")
    db.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('created_at',COALESCE((SELECT value FROM metadata WHERE key='created_at'),?))", (ts,))
    db.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('last_updated_at',?)", (ts,))
    count = db.execute("SELECT COUNT(*) FROM database_versions").fetchone()[0]
    if count == 0:
        db.execute("INSERT INTO database_versions(schema_version,created_at,note) VALUES(?,?,?)", ("1.0.0", ts, "Initial operational database"))
    db.commit()
    db.close()


def allocate_canonical_id(db: sqlite3.Connection, object_type: str, jurisdiction: str) -> str:
    prefix = PREFIX_BY_TYPE[object_type]
    jurisdiction = jurisdiction.upper()
    db.execute(
        "INSERT OR IGNORE INTO id_counters(object_prefix,jurisdiction,next_value) VALUES(?,?,1)",
        (prefix, jurisdiction),
    )
    next_value = db.execute(
        "SELECT next_value FROM id_counters WHERE object_prefix=? AND jurisdiction=?",
        (prefix, jurisdiction),
    ).fetchone()[0]
    db.execute(
        "UPDATE id_counters SET next_value=? WHERE object_prefix=? AND jurisdiction=?",
        (next_value + 1, prefix, jurisdiction),
    )
    return f"{prefix}-{jurisdiction}-{next_value:06d}"


def record_change(db: sqlite3.Connection, actor: str, operation: str, table: str, target_id: str, summary: str) -> None:
    db.execute(
        "INSERT INTO change_log(change_id,changed_at,actor,operation,target_table,target_id,summary) VALUES(?,?,?,?,?,?,?)",
        (str(uuid.uuid4()), now_iso(), actor, operation, table, target_id, summary),
    )
    db.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('last_updated_at',?)", (now_iso(),))


def create_object(path: Path, object_type: str, title: str, jurisdiction: str, description: str | None, state: str, actor: str) -> dict:
    if object_type not in PREFIX_BY_TYPE:
        raise SystemExit(f"Unsupported object type: {object_type}")
    db = connect(path)
    with db:
        canonical_id = allocate_canonical_id(db, object_type, jurisdiction)
        internal_uuid = str(uuid.uuid4())
        ts = now_iso()
        db.execute(
            "INSERT INTO canonical_objects(internal_uuid,canonical_id,object_type,jurisdiction,title,description,record_state,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (internal_uuid, canonical_id, object_type, jurisdiction.upper(), title, description, state, ts, ts),
        )
        record_change(db, actor, "CREATE", "canonical_objects", canonical_id, f"Created {object_type}: {title}")
    db.close()
    return {"internal_uuid": internal_uuid, "canonical_id": canonical_id}


def resolve_object_uuid(db: sqlite3.Connection, canonical_id: str) -> str:
    row = db.execute("SELECT internal_uuid FROM canonical_objects WHERE canonical_id=?", (canonical_id,)).fetchone()
    if not row:
        raise SystemExit(f"Unknown canonical_id: {canonical_id}")
    return row[0]


def add_external_id(path: Path, canonical_id: str, source_system: str, scheme: str, value: str, scope: str | None, source_label: str | None, actor: str) -> str:
    db = connect(path)
    with db:
        object_uuid = resolve_object_uuid(db, canonical_id)
        eid = str(uuid.uuid4())
        ts = now_iso()
        db.execute(
            "INSERT INTO external_identifiers(external_identifier_id,object_uuid,source_system,scheme,value,scope,source_label,first_seen_at,last_seen_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (eid, object_uuid, source_system, scheme, value, scope, source_label, ts, ts),
        )
        record_change(db, actor, "CREATE", "external_identifiers", eid, f"Attached {source_system}:{scheme}={value} to {canonical_id}")
    db.close()
    return eid


def add_relationship(path: Path, subject_id: str, predicate: str, object_id: str, actor: str) -> str:
    db = connect(path)
    with db:
        subject_uuid = resolve_object_uuid(db, subject_id)
        object_uuid = resolve_object_uuid(db, object_id)
        rid = str(uuid.uuid4())
        ts = now_iso()
        db.execute(
            "INSERT INTO relationships(relationship_id,subject_uuid,predicate,object_uuid,created_at) VALUES(?,?,?,?,?)",
            (rid, subject_uuid, predicate, object_uuid, ts),
        )
        record_change(db, actor, "CREATE", "relationships", rid, f"{subject_id} {predicate} {object_id}")
    db.close()
    return rid


def integrity_check(path: Path) -> dict:
    db = connect(path)
    integrity = db.execute("PRAGMA integrity_check").fetchall()
    fk = db.execute("PRAGMA foreign_key_check").fetchall()
    duplicate_ids = db.execute(
        "SELECT canonical_id, COUNT(*) FROM canonical_objects GROUP BY canonical_id HAVING COUNT(*) > 1"
    ).fetchall()
    counts = {
        "canonical_objects": db.execute("SELECT COUNT(*) FROM canonical_objects").fetchone()[0],
        "source_records": db.execute("SELECT COUNT(*) FROM source_records").fetchone()[0],
        "events": db.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "observations": db.execute("SELECT COUNT(*) FROM observations").fetchone()[0],
    }
    db.close()
    return {
        "ok": integrity == [("ok",)] and not fk and not duplicate_ids,
        "integrity_check": integrity,
        "foreign_key_violations": fk,
        "duplicate_canonical_ids": duplicate_ids,
        "counts": counts,
    }


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create-db")
    c.add_argument("database")

    c = sub.add_parser("integrity-check")
    c.add_argument("database")

    c = sub.add_parser("create-object")
    c.add_argument("database")
    c.add_argument("--type", required=True, choices=sorted(PREFIX_BY_TYPE))
    c.add_argument("--title", required=True)
    c.add_argument("--jurisdiction", default="BD")
    c.add_argument("--description")
    c.add_argument("--state", default="CURRENT", choices=["CANDIDATE", "CURRENT", "SUPERSEDED", "ARCHIVED"])
    c.add_argument("--actor", default="ARGUS")

    c = sub.add_parser("add-external-id")
    c.add_argument("database")
    c.add_argument("--canonical-id", required=True)
    c.add_argument("--source-system", required=True)
    c.add_argument("--scheme", required=True)
    c.add_argument("--value", required=True)
    c.add_argument("--scope")
    c.add_argument("--source-label")
    c.add_argument("--actor", default="ARGUS")

    c = sub.add_parser("add-relationship")
    c.add_argument("database")
    c.add_argument("--subject", required=True)
    c.add_argument("--predicate", required=True)
    c.add_argument("--object", required=True)
    c.add_argument("--actor", default="ARGUS")

    args = p.parse_args()
    path = Path(args.database)
    if args.command == "create-db":
        create_db(path)
        print(json.dumps({"database": str(path), "sha256": file_sha256(path), **integrity_check(path)}, indent=2))
    elif args.command == "integrity-check":
        result = integrity_check(path)
        result["sha256"] = file_sha256(path)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["ok"] else 1)
    elif args.command == "create-object":
        print(json.dumps(create_object(path, args.type, args.title, args.jurisdiction, args.description, args.state, args.actor), indent=2))
    elif args.command == "add-external-id":
        print(add_external_id(path, args.canonical_id, args.source_system, args.scheme, args.value, args.scope, args.source_label, args.actor))
    elif args.command == "add-relationship":
        print(add_relationship(path, args.subject, args.predicate, args.object, args.actor))


if __name__ == "__main__":
    main()
