import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "profiles" / "canonical-identity-standard-v1.0.yaml"
SQL = ROOT / "schemas" / "argus-operational-database-v1.sql"
TOOL = ROOT / "tools" / "argus_operational_db.py"
DOC = ROOT / "docs" / "architecture" / "canonical-identity-operational-database-v1.md"


class CanonicalIdentityOperationalDatabase(unittest.TestCase):
    def test_identity_standard_declares_two_layer_identity_and_required_object_types(self):
        self.assertTrue(IDENTITY.exists())
        text = IDENTITY.read_text()
        for token in (
            "internal_uuid",
            "canonical_id",
            "POL",
            "STR",
            "PRG",
            "PRJ",
            "REQ",
            "PLN",
            "PKG",
            "PROC",
            "TND",
            "LOT",
            "ITM",
            "ENT",
            "PER",
            "OPP",
            "INT",
            "KNO",
            "AWD",
            "CTR",
            "EVT",
            "DOC",
            "SRC",
            "OBS",
            "PRD",
        ):
            self.assertIn(token, text)
        self.assertIn("supplier_is_entity_role", text)
        self.assertIn("title_alone_never_deduplicates", text)
        self.assertIn("single_writer", text)

    def test_sql_schema_builds_with_core_integrity_constraints(self):
        self.assertTrue(SQL.exists())
        sql = SQL.read_text()
        self.assertIn("PRAGMA journal_mode = DELETE", sql)
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
            db = sqlite3.connect(tmp.name)
            db.executescript(sql)
            tables = {row[0] for row in db.execute("select name from sqlite_master where type='table'")}
            for table in (
                "metadata",
                "id_counters",
                "canonical_objects",
                "external_identifiers",
                "relationships",
                "source_records",
                "events",
                "observations",
                "legacy_registry_records",
                "change_log",
            ):
                self.assertIn(table, tables)

            db.execute(
                "insert into canonical_objects(internal_uuid, canonical_id, object_type, title, record_state, created_at, updated_at) values(?,?,?,?,?,?,?)",
                ("u1", "ENT-BD-000001", "ENTITY", "Example", "CURRENT", "2026-10-22T00:00:00Z", "2026-10-22T00:00:00Z"),
            )
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "insert into canonical_objects(internal_uuid, canonical_id, object_type, title, record_state, created_at, updated_at) values(?,?,?,?,?,?,?)",
                    ("u2", "ENT-BD-000001", "ENTITY", "Duplicate", "CURRENT", "2026-10-22T00:00:00Z", "2026-10-22T00:00:00Z"),
                )

    def test_update_utility_and_architecture_document_exist(self):
        self.assertTrue(TOOL.exists())
        self.assertTrue(DOC.exists())
        tool = TOOL.read_text()
        for token in (
            "create-db",
            "integrity-check",
            "create-object",
            "add-external-id",
            "add-relationship",
            "import-legacy-registry",
        ):
            self.assertIn(token, tool)


if __name__ == "__main__":
    unittest.main()
