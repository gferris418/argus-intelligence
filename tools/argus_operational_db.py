from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "argus-operational-store-v1.sql"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect_database(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = DELETE")
    conn.execute("PRAGMA synchronous = FULL")
    return conn


def initialize_database(path: str | Path, schema_path: str | Path = SCHEMA_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = Path(schema_path).read_text(encoding="utf-8")
    conn = connect_database(path)
    try:
        conn.executescript(schema)
        conn.execute("PRAGMA user_version = 1")
        conn.commit()
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {result}")
    finally:
        conn.close()
    return path


def next_canonical_id(conn: sqlite3.Connection, object_type: str, jurisdiction: str = "BD") -> str:
    object_type = object_type.upper()
    jurisdiction = jurisdiction.upper()
    prefix_row = conn.execute(
        "SELECT prefix FROM object_type_registry WHERE object_type = ? AND active = 1",
        (object_type,),
    ).fetchone()
    if prefix_row is None:
        raise ValueError(f"Unknown or inactive object type: {object_type}")
    prefix = prefix_row[0]
    row = conn.execute(
        "SELECT next_value FROM id_sequence WHERE object_type = ? AND jurisdiction = ?",
        (object_type, jurisdiction),
    ).fetchone()
    if row is None:
        sequence = 1
        conn.execute(
            "INSERT INTO id_sequence(object_type, jurisdiction, next_value) VALUES (?,?,?)",
            (object_type, jurisdiction, 2),
        )
    else:
        sequence = int(row[0])
        conn.execute(
            "UPDATE id_sequence SET next_value = ? WHERE object_type = ? AND jurisdiction = ?",
            (sequence + 1, object_type, jurisdiction),
        )
    return f"{prefix}-{jurisdiction}-{sequence:06d}"


def upsert_canonical_object(
    conn: sqlite3.Connection,
    *,
    object_type: str,
    title: str,
    jurisdiction: str = "BD",
    canonical_id: str | None = None,
    internal_id: str | None = None,
    description: str | None = None,
    status: str = "CURRENT",
    legacy_identity: bool = False,
) -> dict[str, str]:
    """Create or explicitly update one canonical object.

    No fuzzy/title-based matching occurs here. Callers must reconcile identity before
    supplying an existing canonical_id. If canonical_id is omitted a new identity is issued.
    """
    now = utc_now()
    existing = None
    if canonical_id:
        existing = conn.execute(
            "SELECT internal_id, canonical_id FROM canonical_object WHERE canonical_id = ?",
            (canonical_id,),
        ).fetchone()
    if existing:
        conn.execute(
            "UPDATE canonical_object SET title=?, description=?, status=?, updated_at=? WHERE internal_id=?",
            (title, description, status, now, existing["internal_id"]),
        )
        return {"internal_id": existing["internal_id"], "canonical_id": existing["canonical_id"]}
    if canonical_id is None:
        canonical_id = next_canonical_id(conn, object_type, jurisdiction)
    if internal_id is None:
        internal_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO canonical_object(
            internal_id, canonical_id, object_type, jurisdiction, title, description,
            status, legacy_identity, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            internal_id,
            canonical_id,
            object_type.upper(),
            jurisdiction.upper(),
            title,
            description,
            status,
            1 if legacy_identity else 0,
            now,
            now,
        ),
    )
    return {"internal_id": internal_id, "canonical_id": canonical_id}


def register_source_record(
    conn: sqlite3.Connection,
    *,
    source_system: str,
    record_type: str,
    observed_at: str | None = None,
    native_id: str | None = None,
    source_authority: str | None = None,
    source_url: str | None = None,
    published_at: str | None = None,
    content_hash: str | None = None,
    raw_title: str | None = None,
    access_class: str | None = None,
    source_record_id: str | None = None,
    canonical_source_id: str | None = None,
) -> str:
    if source_record_id is None:
        source_record_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO source_record(
            source_record_id, canonical_source_id, source_system, source_authority,
            native_id, record_type, source_url, published_at, observed_at,
            content_hash, raw_title, access_class
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            source_record_id,
            canonical_source_id,
            source_system,
            source_authority,
            native_id,
            record_type,
            source_url,
            published_at,
            observed_at or utc_now(),
            content_hash,
            raw_title,
            access_class,
        ),
    )
    return source_record_id


def add_external_identifier(
    conn: sqlite3.Connection,
    *,
    object_internal_id: str,
    source_system: str,
    scheme: str,
    value: str,
    scope: str = "OBJECT",
    source_record_id: str | None = None,
) -> str:
    identifier_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO external_identifier(
            identifier_id, object_internal_id, source_system, scheme, value,
            scope, source_record_id, created_at
        ) VALUES (?,?,?,?,?,?,?,?)
        """,
        (identifier_id, object_internal_id, source_system, scheme, value, scope, source_record_id, utc_now()),
    )
    return identifier_id


def add_relationship(
    conn: sqlite3.Connection,
    *,
    from_object_internal_id: str,
    to_object_internal_id: str,
    relation_type: str,
    source_record_id: str | None = None,
    valid_from: str | None = None,
    valid_to: str | None = None,
    status: str = "CURRENT",
) -> str:
    relationship_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO relationship(
            relationship_id, from_object_internal_id, to_object_internal_id,
            relation_type, source_record_id, valid_from, valid_to, status, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            relationship_id,
            from_object_internal_id,
            to_object_internal_id,
            relation_type,
            source_record_id,
            valid_from,
            valid_to,
            status,
            utc_now(),
        ),
    )
    return relationship_id


def record_event(
    conn: sqlite3.Connection,
    *,
    subject_object_internal_id: str,
    event_type: str,
    occurred_at: str | None = None,
    published_at: str | None = None,
    source_record_id: str | None = None,
    payload: dict[str, Any] | None = None,
    canonical_event_id: str | None = None,
) -> str:
    event_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO event(
            event_id, canonical_event_id, subject_object_internal_id, event_type,
            occurred_at, published_at, source_record_id, payload_json, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            event_id,
            canonical_event_id,
            subject_object_internal_id,
            event_type,
            occurred_at,
            published_at,
            source_record_id,
            json.dumps(payload, sort_keys=True) if payload is not None else None,
            utc_now(),
        ),
    )
    return event_id


def record_observation(
    conn: sqlite3.Connection,
    *,
    subject_object_internal_id: str,
    field_path: str,
    source_record_id: str | None = None,
    value: Any = None,
    raw_label: str | None = None,
    raw_value: str | None = None,
    observed_at: str | None = None,
    published_at: str | None = None,
    claim_type: str = "FACT",
    condition: str = "CURRENT",
    confidence: float | None = None,
    canonical_observation_id: str | None = None,
) -> str:
    observation_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO observation(
            observation_id, canonical_observation_id, subject_object_internal_id,
            field_path, value_json, raw_label, raw_value, source_record_id,
            observed_at, published_at, claim_type, condition, confidence, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            observation_id,
            canonical_observation_id,
            subject_object_internal_id,
            field_path,
            json.dumps(value, sort_keys=True) if value is not None else None,
            raw_label,
            raw_value,
            source_record_id,
            observed_at or utc_now(),
            published_at,
            claim_type,
            condition,
            confidence,
            utc_now(),
        ),
    )
    return observation_id


def record_mutation(
    conn: sqlite3.Connection,
    *,
    actor: str,
    operation: str,
    object_internal_id: str | None = None,
    before_hash: str | None = None,
    after_hash: str | None = None,
    note: str | None = None,
) -> str:
    mutation_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO mutation_log(mutation_id, applied_at, actor, operation, object_internal_id, before_hash, after_hash, note) VALUES (?,?,?,?,?,?,?,?)",
        (mutation_id, utc_now(), actor, operation, object_internal_id, before_hash, after_hash, note),
    )
    return mutation_id


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def integrity_check(path: str | Path) -> str:
    conn = connect_database(path)
    try:
        return str(conn.execute("PRAGMA integrity_check").fetchone()[0])
    finally:
        conn.close()


def _cli() -> int:
    parser = argparse.ArgumentParser(description="ARGUS operational SQLite registry utility")
    sub = parser.add_subparsers(dest="command", required=True)
    init_parser = sub.add_parser("init", help="Initialize a database")
    init_parser.add_argument("database")
    check_parser = sub.add_parser("integrity", help="Run PRAGMA integrity_check")
    check_parser.add_argument("database")
    args = parser.parse_args()
    if args.command == "init":
        initialize_database(args.database)
        print(args.database)
        return 0
    if args.command == "integrity":
        result = integrity_check(args.database)
        print(result)
        return 0 if result == "ok" else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli())
