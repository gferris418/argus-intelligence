from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from tools.argus_operational_db import SCHEMA_PATH, connect_database, initialize_database

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_1_0_TO_1_1 = ROOT / "schemas" / "migrations" / "argus-operational-store-1.0.0-to-1.1.0.sql"
LATEST_SCHEMA_VERSION = "1.1.0"
LATEST_USER_VERSION = 2


def _schema_version(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT value FROM schema_meta WHERE key = 'schema_version'"
    ).fetchone()
    if row is None:
        raise RuntimeError("Operational database is missing schema_meta.schema_version")
    return str(row[0])


def _verify(conn: sqlite3.Connection) -> None:
    integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity check failed: {integrity}")
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        raise RuntimeError(f"SQLite foreign-key check failed: {len(violations)} violation(s)")


def migrate_database(path: str | Path) -> Path:
    """Upgrade one existing ARGUS operational registry to the latest schema.

    The migration is additive and idempotent. Unsupported versions fail closed.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Operational database does not exist: {path}")

    conn = connect_database(path)
    try:
        _verify(conn)
        version = _schema_version(conn)
        if version == "1.0.0":
            migration = MIGRATION_1_0_TO_1_1.read_text(encoding="utf-8")
            conn.executescript(migration)
            version = _schema_version(conn)
        elif version != LATEST_SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported operational schema version: {version}")

        if version != LATEST_SCHEMA_VERSION:
            raise RuntimeError(
                f"Migration did not reach latest schema: {version} != {LATEST_SCHEMA_VERSION}"
            )
        user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])
        if user_version != LATEST_USER_VERSION:
            raise RuntimeError(
                f"Unexpected SQLite user_version: {user_version} != {LATEST_USER_VERSION}"
            )
        _verify(conn)
    finally:
        conn.close()
    return path


def initialize_latest_database(
    path: str | Path,
    schema_path: str | Path = SCHEMA_PATH,
) -> Path:
    """Create a fresh base registry and immediately upgrade it to the latest schema."""
    initialized = initialize_database(path, schema_path=schema_path)
    return migrate_database(initialized)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="ARGUS operational-store migration utility")
    sub = parser.add_subparsers(dest="command", required=True)

    migrate_parser = sub.add_parser("migrate", help="Migrate an existing registry")
    migrate_parser.add_argument("database")

    init_parser = sub.add_parser("init-latest", help="Initialize a registry at the latest schema")
    init_parser.add_argument("database")

    args = parser.parse_args()
    if args.command == "migrate":
        migrate_database(args.database)
        print(args.database)
        return 0
    if args.command == "init-latest":
        initialize_latest_database(args.database)
        print(args.database)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli())
