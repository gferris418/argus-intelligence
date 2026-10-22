from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.argus_operational_migrate import (
    LATEST_SCHEMA_VERSION,
    LATEST_USER_VERSION,
    initialize_latest_database,
    migrate_database,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_SCHEMA = ROOT / "schemas" / "argus-operational-store-v1.sql"

EXPECTED_NEW_TYPES = {
    "PRODUCT_CATEGORY": "PCAT",
    "SECTOR": "SEC",
    "GEOGRAPHY": "GEO",
    "BID": "BID",
    "ACCESS_ASIA_PROJECT": "AAPJ",
}
MIGRATION_RECEIPT_ID = "MIGRATION-ARGUS-STORE-1.1.0"


class CommercialGraphStoreMigrationTests(unittest.TestCase):
    def test_migration_api_exists(self) -> None:
        self.assertTrue(callable(migrate_database))
        self.assertTrue(callable(initialize_latest_database))
        self.assertEqual("1.1.0", LATEST_SCHEMA_VERSION)
        self.assertEqual(2, LATEST_USER_VERSION)

    def test_existing_v1_database_migrates_additively_without_data_loss(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.sqlite"
            conn = sqlite3.connect(path)
            conn.executescript(BASE_SCHEMA.read_text(encoding="utf-8"))
            conn.execute(
                """
                INSERT INTO canonical_object(
                    internal_id, canonical_id, object_type, jurisdiction, title,
                    status, legacy_identity, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?)
                """,
                (
                    "obj-1", "ENT-BD-000001", "ORGANIZATION", "BD", "Existing Entity",
                    "CURRENT", 0, "2026-10-22T00:00:00Z", "2026-10-22T00:00:00Z",
                ),
            )
            conn.commit()
            before = conn.execute("SELECT COUNT(*) FROM canonical_object").fetchone()[0]
            conn.close()

            migrate_database(path)

            conn = sqlite3.connect(path)
            try:
                meta = dict(conn.execute("SELECT key, value FROM schema_meta"))
                self.assertEqual("1.1.0", meta["schema_version"])
                self.assertEqual(
                    "canonical-object-identity-standard-v1.0.yaml@1.1.0",
                    meta["identity_standard"],
                )
                self.assertEqual(
                    "access-asia-commercial-data-standard-v1.0",
                    meta["commercial_data_standard"],
                )
                self.assertEqual(2, conn.execute("PRAGMA user_version").fetchone()[0])
                self.assertEqual(before, conn.execute("SELECT COUNT(*) FROM canonical_object").fetchone()[0])
                self.assertEqual("ok", conn.execute("PRAGMA integrity_check").fetchone()[0])
                self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
                types = dict(conn.execute(
                    "SELECT object_type, prefix FROM object_type_registry WHERE object_type IN (?,?,?,?,?)",
                    tuple(EXPECTED_NEW_TYPES),
                ))
                self.assertEqual(EXPECTED_NEW_TYPES, types)
                receipt = conn.execute(
                    "SELECT actor, operation, note FROM mutation_log WHERE mutation_id = ?",
                    (MIGRATION_RECEIPT_ID,),
                ).fetchone()
                self.assertEqual(
                    (
                        "ATLAS",
                        "SCHEMA_MIGRATION",
                        "ARGUS operational store 1.0.0 -> 1.1.0; additive commercial graph activation",
                    ),
                    receipt,
                )
            finally:
                conn.close()

    def test_migration_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.sqlite"
            conn = sqlite3.connect(path)
            conn.executescript(BASE_SCHEMA.read_text(encoding="utf-8"))
            conn.commit()
            conn.close()

            migrate_database(path)
            migrate_database(path)

            conn = sqlite3.connect(path)
            try:
                self.assertEqual(
                    len(EXPECTED_NEW_TYPES),
                    conn.execute(
                        "SELECT COUNT(*) FROM object_type_registry WHERE object_type IN (?,?,?,?,?)",
                        tuple(EXPECTED_NEW_TYPES),
                    ).fetchone()[0],
                )
                self.assertEqual("1.1.0", dict(conn.execute("SELECT key,value FROM schema_meta"))["schema_version"])
                self.assertEqual(
                    1,
                    conn.execute(
                        "SELECT COUNT(*) FROM mutation_log WHERE mutation_id = ?",
                        (MIGRATION_RECEIPT_ID,),
                    ).fetchone()[0],
                )
                self.assertEqual("ok", conn.execute("PRAGMA integrity_check").fetchone()[0])
                self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            finally:
                conn.close()

    def test_new_database_initialization_finishes_at_latest_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.sqlite"
            initialize_latest_database(path)
            conn = sqlite3.connect(path)
            try:
                meta = dict(conn.execute("SELECT key, value FROM schema_meta"))
                self.assertEqual("1.1.0", meta["schema_version"])
                self.assertEqual(2, conn.execute("PRAGMA user_version").fetchone()[0])
                self.assertEqual("ok", conn.execute("PRAGMA integrity_check").fetchone()[0])
                self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
