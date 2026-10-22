from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from tools.argus_operational_db import connect_database

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MIGRATION = ROOT / "registry" / "migrations" / "1.0.0-to-1.1.0-commercial-graph.sql"
SUPPORTED_SOURCE_VERSIONS = {"1.0.0", "1.1.0"}
TARGET_VERSION = "1.1.0"
TARGET_USER_VERSION = 2


def _schema_version(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
    if row is None:
        raise RuntimeError("schema_meta.schema_version is missing")
    return str(row[0])


def _assert_database_health(conn: sqlite3.Connection) -> None:
    integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity check failed: {integrity}")
    fk_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_rows:
        raise RuntimeError(f"SQLite foreign-key check failed: {len(fk_rows)} violation(s)")


def apply_commercial_graph_migration(
    database: str | Path,
    migration_path: str | Path = DEFAULT_MIGRATION,
) -> Path:
    """Apply or re-assert the additive Access Asia commercial-graph migration.

    Existing canonical IDs and business records are preserved. Supported 1.0.0 and
    1.1.0 databases both execute the idempotent migration SQL so schema objects and
    both version markers are brought back to the complete 1.1.0 contract even after
    a legacy initializer has reset ``PRAGMA user_version``.
    """
    database = Path(database)
    if not database.is_file():
        raise FileNotFoundError(f"Operational database does not exist: {database}")

    migration_path = Path(migration_path)
    if not migration_path.is_file():
        raise FileNotFoundError(f"Migration SQL does not exist: {migration_path}")

    conn = connect_database(database)
    try:
        _assert_database_health(conn)
        source_version = _schema_version(conn)
        if source_version not in SUPPORTED_SOURCE_VERSIONS:
            raise RuntimeError(
                f"Unsupported operational schema version {source_version}; expected one of "
                f"{sorted(SUPPORTED_SOURCE_VERSIONS)}"
            )

        sql = migration_path.read_text(encoding="utf-8")
        conn.executescript(sql)
        if _schema_version(conn) != TARGET_VERSION:
            raise RuntimeError("Commercial graph migration did not set schema_version=1.1.0")
        if int(conn.execute("PRAGMA user_version").fetchone()[0]) != TARGET_USER_VERSION:
            raise RuntimeError(
                f"Commercial graph migration did not set PRAGMA user_version={TARGET_USER_VERSION}"
            )
        _assert_database_health(conn)
    finally:
        conn.close()
    return database


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Apply ARGUS commercial graph SQLite migration")
    parser.add_argument("database")
    parser.add_argument("--migration", default=str(DEFAULT_MIGRATION))
    args = parser.parse_args()
    apply_commercial_graph_migration(args.database, args.migration)
    print(args.database)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
