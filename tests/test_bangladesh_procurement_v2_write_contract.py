import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v2.0.yaml"
ADDENDUM = ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v2.0-validation-addendum.yaml"
SCHEMA = ROOT / "schemas" / "bangladesh-procurement-v2.schema.json"
CURRENT_INDEX = ROOT / "data" / "registry" / "current-index.json"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "bangladesh-v2"
FIXTURE_MAP = FIXTURE_DIR / "current-procurement-fixture-map.json"
REPORT = ROOT / "docs" / "validation" / "bangladesh-procurement-v2-write-contract-dry-run.md"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()


class BangladeshProcurementV2WriteContract(unittest.TestCase):
    def test_validation_addendum_is_folded_into_main_candidate(self):
        text = V2.read_text()
        self.assertIn("PROCUREMENT_DOCUMENT_READY", text)
        self.assertIn("EXPECTED_PUBLICATION", text)
        self.assertIn("schemas/bangladesh-procurement-v2.schema.json", text)
        self.assertFalse(ADDENDUM.exists(), "temporary validation addendum must be folded into v2 candidate")

    def test_machine_write_schema_exists_as_draft_2020_12(self):
        self.assertTrue(SCHEMA.exists())
        schema = json.loads(SCHEMA.read_text())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), {"argus_id", "title", "record_state", "record_revision"})

    def test_all_current_procurements_have_non_mutating_v2_dry_run_fixtures(self):
        self.assertTrue(FIXTURE_MAP.exists())
        index = json.loads(CURRENT_INDEX.read_text())
        current_procurement_ids = {argus_id for argus_id in index["records"] if argus_id.startswith("PROC-")}
        fixture_map = json.loads(FIXTURE_MAP.read_text())
        self.assertEqual(set(fixture_map), current_procurement_ids)
        for argus_id, rel_path in fixture_map.items():
            fixture_path = ROOT / rel_path
            self.assertTrue(fixture_path.exists(), argus_id)
            fixture = json.loads(fixture_path.read_text())
            self.assertFalse(fixture["live_registry_mutation"])
            self.assertEqual(fixture["v2_candidate"]["argus_id"], argus_id)

    def test_remaining_current_record_fixture_files_exist(self):
        for name in (
            "dae-low-lift-pump-successor.json",
            "dgdp-inflatable-boat.json",
            "dgdp-scuba.json",
        ):
            self.assertTrue((FIXTURE_DIR / name).exists(), name)

    def test_active_write_authority_remains_v1_3(self):
        self.assertIn(
            "bangladesh_procurement_standard: profiles/bangladesh-canonical-procurement-standard-v1.3.yaml",
            MANIFEST,
        )

    def test_dry_run_report_records_activation_gate(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text()
        for token in (
            "Current PROCUREMENT records covered: 6/6",
            "Schema validation: PASS",
            "Live registry mutation: false",
            "Material information loss: 0",
            "v1.3 remains active",
            "GO / NO-GO",
            "NO-GO for live migration",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
