import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "canonical-object-identity-standard-v1.0.yaml"
SCHEMA = ROOT / "schemas" / "argus-operational-store-v1.sql"
TOOL = ROOT / "tools" / "argus_operational_db.py"
MANIFEST = ROOT / "argus-intelligence.yaml"


class CanonicalIdentityOperationalStore(unittest.TestCase):
    def test_identity_profile_exists_and_defines_three_layer_identity(self):
        self.assertTrue(PROFILE.exists())
        text = PROFILE.read_text()
        for token in (
            "CANONICAL_OBJECT",
            "SOURCE_RECORD",
            "EVENT_OBSERVATION",
            "REQUIREMENT",
            "PROCUREMENT_PROCESS",
            "SOLICITATION",
            "ORGANIZATION",
            "PRODUCT",
            "immutable_internal_id",
            "human_readable_canonical_id",
        ):
            self.assertIn(token, text)

    def test_operational_sqlite_schema_builds_and_has_core_tables(self):
        self.assertTrue(SCHEMA.exists())
        sql = SCHEMA.read_text()
        conn = sqlite3.connect(":memory:")
        conn.executescript(sql)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        expected = {
            "schema_meta",
            "id_sequence",
            "canonical_object",
            "external_identifier",
            "relationship",
            "source_record",
            "source_object_link",
            "event",
            "observation",
            "object_attribute",
        }
        self.assertTrue(expected.issubset(tables))

    def test_canonical_and_source_ids_have_uniqueness_guards(self):
        conn = sqlite3.connect(":memory:")
        conn.executescript(SCHEMA.read_text())
        conn.execute(
            "INSERT INTO canonical_object(internal_id, canonical_id, object_type, title, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            ("uuid-1", "REQ-BD-000001", "REQUIREMENT", "Need", "CURRENT", "2026-10-22T00:00:00Z", "2026-10-22T00:00:00Z"),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO canonical_object(internal_id, canonical_id, object_type, title, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
                ("uuid-2", "REQ-BD-000001", "REQUIREMENT", "Duplicate", "CURRENT", "2026-10-22T00:00:00Z", "2026-10-22T00:00:00Z"),
            )

        conn.execute(
            "INSERT INTO source_record(source_record_id, source_system, native_id, record_type, observed_at) VALUES (?,?,?,?,?)",
            ("src-1", "BPPA", "98162", "TENDER_NOTICE", "2026-10-22T00:00:00Z"),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO source_record(source_record_id, source_system, native_id, record_type, observed_at) VALUES (?,?,?,?,?)",
                ("src-2", "BPPA", "98162", "TENDER_NOTICE", "2026-10-22T00:00:00Z"),
            )

    def test_operational_tool_exists_and_supports_init_and_id_generation(self):
        self.assertTrue(TOOL.exists())
        text = TOOL.read_text()
        for token in ("def initialize_database", "def next_canonical_id", "def upsert_canonical_object"):
            self.assertIn(token, text)

    def test_manifest_registers_identity_and_operational_store_contract(self):
        text = MANIFEST.read_text()
        self.assertIn("canonical_identity_standard: profiles/canonical-object-identity-standard-v1.0.yaml", text)
        self.assertIn("operational_database_schema: schemas/argus-operational-store-v1.sql", text)
        self.assertIn("sharepoint_operational_store", text)


if __name__ == "__main__":
    unittest.main()
