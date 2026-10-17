import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v2.0.yaml"
ADDENDUM = ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v2.0-validation-addendum.yaml"
SCHEMA = ROOT / "schemas" / "bangladesh-procurement-v2.schema.json"
CURRENT_INDEX = ROOT / "data" / "registry" / "current-index.json"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "bangladesh-v2"
FIXTURE_MAP = FIXTURE_DIR / "current-procurement-fixture-map.json"
REPORT = ROOT / "docs" / "validation" / "bangladesh-procurement-v2-write-contract-dry-run.md"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()
WORLD_BANK_FIXTURE = FIXTURE_DIR / "world-bank-sita-g01.json"


def load_schema():
    return json.loads(SCHEMA.read_text())


def load_v2_candidate(path):
    return json.loads(path.read_text())["v2_candidate"]


class BangladeshProcurementV2WriteContract(unittest.TestCase):
    def test_validation_addendum_is_folded_into_main_candidate(self):
        text = V2.read_text()
        self.assertIn("PROCUREMENT_DOCUMENT_READY", text)
        self.assertIn("EXPECTED_PUBLICATION", text)
        self.assertIn("schemas/bangladesh-procurement-v2.schema.json", text)
        self.assertFalse(ADDENDUM.exists(), "temporary validation addendum must be folded into v2 candidate")

    def test_machine_write_schema_exists_as_draft_2020_12(self):
        self.assertTrue(SCHEMA.exists())
        schema = load_schema()
        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), {"argus_id", "title", "record_state", "record_revision"})

    def test_sparse_minimum_record_is_valid_without_fabricated_fields(self):
        schema = load_schema()
        validator = Draft202012Validator(schema)
        validator.validate({
            "argus_id": "PROC-TEST-SPARSE",
            "title": "Sparse procurement",
            "record_state": "CURRENT",
            "record_revision": 1,
        })

    def test_schema_rejects_unknown_legacy_or_duplicate_fields(self):
        schema = load_schema()
        validator = Draft202012Validator(schema)
        base = {
            "argus_id": "PROC-TEST-STRICT",
            "title": "Strict procurement",
            "record_state": "CURRENT",
            "record_revision": 1,
        }
        for field in ("extension_count", "solicitation", "ministry_name"):
            bad = copy.deepcopy(base)
            bad[field] = 1
            with self.assertRaises(ValidationError, msg=field):
                validator.validate(bad)

    def test_schema_rejects_invalid_role_and_process_vocabularies(self):
        validator = Draft202012Validator(load_schema())
        invalid_role = {
            "argus_id": "PROC-TEST-ROLE",
            "title": "Role test",
            "record_state": "CURRENT",
            "record_revision": 1,
            "party_role_links": [{"party_id": "ENT-X", "role": "MINISTRY_NAME"}],
        }
        with self.assertRaises(ValidationError):
            validator.validate(invalid_role)

        invalid_category = {
            "argus_id": "PROC-TEST-CAT",
            "title": "Category test",
            "record_state": "CURRENT",
            "record_revision": 1,
            "process": {"category": "EQUIPMENT"},
        }
        with self.assertRaises(ValidationError):
            validator.validate(invalid_category)

    def test_planning_milestones_and_arbitrary_observation_values_are_supported(self):
        schema = load_schema()
        milestone_enum = schema["$defs"]["milestone"]["properties"]["type"]["enum"]
        self.assertIn("PROCUREMENT_DOCUMENT_READY", milestone_enum)
        self.assertIn("EXPECTED_PUBLICATION", milestone_enum)
        observation_value = schema["$defs"]["observation"]["properties"]["value"]
        self.assertEqual(observation_value, {})

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

    def test_every_current_dry_run_and_world_bank_fixture_validates_against_schema(self):
        validator = Draft202012Validator(load_schema())
        fixture_map = json.loads(FIXTURE_MAP.read_text())
        fixture_paths = [ROOT / rel_path for rel_path in fixture_map.values()] + [WORLD_BANK_FIXTURE]
        errors = {}
        for path in fixture_paths:
            candidate = load_v2_candidate(path)
            found = sorted(validator.iter_errors(candidate), key=lambda e: list(e.path))
            if found:
                errors[path.name] = [f"{list(e.path)}: {e.message}" for e in found]
        self.assertEqual(errors, {})

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
