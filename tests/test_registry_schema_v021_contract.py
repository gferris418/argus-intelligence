import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "registry" / "schema" / "argus-master-registry-v0.2.1.json"
MIGRATION_PATH = ROOT / "registry" / "migrations" / "0.2.0-to-0.2.1-evidence.sql"


class RegistrySchemaV021Contract(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text())
        self.migration = MIGRATION_PATH.read_text()

    def test_schema_version_accepts_legacy_and_new_records(self):
        versions = self.schema["properties"]["schema_version"]["enum"]
        self.assertEqual(versions, ["0.2.0", "0.2.1"])
        self.assertEqual(self.schema["version"], "0.2.1")

    def test_evidence_supports_legacy_or_split_semantics(self):
        defs = self.schema["$defs"]
        self.assertEqual(defs["claimType"]["enum"], ["FACT", "DERIVED", "INFERENCE", "ASSUMPTION", "UNKNOWN"])
        self.assertEqual(defs["claimCondition"]["enum"], ["CURRENT", "STALE", "CONFLICT"])
        evidence = defs["evidenceRef"]
        self.assertEqual(evidence["required"], ["source_system"])
        self.assertIn("analytical_label", evidence["properties"])
        self.assertIn("claim_type", evidence["properties"])
        self.assertIn("claim_condition", evidence["properties"])
        semantic_gate = evidence["allOf"][1]["anyOf"]
        self.assertIn({"required": ["analytical_label"]}, semantic_gate)
        self.assertIn({"required": ["claim_type", "claim_condition"]}, semantic_gate)

    def test_physical_migration_is_backward_compatible(self):
        sql = self.migration
        self.assertIn("ADD COLUMN IF NOT EXISTS claim_type", sql)
        self.assertIn("ADD COLUMN IF NOT EXISTS claim_condition", sql)
        self.assertIn("ALTER COLUMN analytical_label DROP NOT NULL", sql)
        self.assertIn("analytical_label IS NOT NULL", sql)
        self.assertIn("claim_type IS NOT NULL AND claim_condition IS NOT NULL", sql)
        self.assertNotIn("UPDATE argus.record_evidence SET", sql)

    def test_migration_does_not_delete_or_rewrite_legacy_evidence(self):
        upper = self.migration.upper()
        self.assertNotIn("DELETE FROM ARGUS.RECORD_EVIDENCE", upper)
        self.assertNotIn("TRUNCATE", upper)
        self.assertNotIn("DROP TABLE ARGUS.RECORD_EVIDENCE", upper)


if __name__ == "__main__":
    unittest.main()
