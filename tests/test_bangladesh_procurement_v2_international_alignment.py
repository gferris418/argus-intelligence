import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "bangladesh-procurement-v2.1.schema.json"
PROFILE = ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v2.1.yaml"
ALIGNMENT = ROOT / "profiles" / "bangladesh-procurement-international-alignment-v1.0.yaml"


class BangladeshProcurementV21InternationalAlignment(unittest.TestCase):
    def test_schema_is_valid_and_uses_one_stage_aligned_contract(self):
        self.assertTrue(SCHEMA.exists())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["jurisdiction"]["const"], "BD")

    def test_schema_exposes_ocds_lifecycle_components(self):
        schema = json.loads(SCHEMA.read_text())
        props = schema["properties"]
        for field in (
            "parties",
            "planning",
            "tender",
            "awards",
            "contracts",
            "related_processes",
            "source_releases",
            "ocds_alignment",
        ):
            self.assertIn(field, props)

    def test_schema_supports_world_bank_and_adb_planning_and_award_fields(self):
        schema = json.loads(SCHEMA.read_text())
        plan = schema["$defs"]["procurement_plan"]["properties"]
        for field in (
            "plan_id",
            "plan_type",
            "plan_version",
            "expected_advertisement_at",
            "bidding_document_type",
            "review_type",
            "estimated_cost",
        ):
            self.assertIn(field, plan)

        submission = schema["$defs"]["submission"]["properties"]
        for field in (
            "bidder_party_ids",
            "opening_value",
            "evaluated_value",
            "status",
            "rejection_reason",
        ):
            self.assertIn(field, submission)

        award = schema["$defs"]["award"]["properties"]
        for field in (
            "scope_summary",
            "contract_duration",
            "notification_of_intention_at",
            "standstill_end_at",
            "beneficial_ownership_disclosed",
            "beneficial_ownership_source_ref",
        ):
            self.assertIn(field, award)

    def test_source_change_history_uses_immutable_release_semantics(self):
        schema = json.loads(SCHEMA.read_text())
        release = schema["$defs"]["source_release"]
        self.assertEqual(
            set(release["required"]),
            {"release_id", "source_system", "recorded_at", "release_type", "immutable"},
        )
        self.assertEqual(release["properties"]["immutable"]["const"], True)
        self.assertIn("content_hash", release["properties"])
        self.assertIn("supersedes_release_id", release["properties"])

    def test_contract_implementation_transactions_and_modifications_are_typed(self):
        schema = json.loads(SCHEMA.read_text())
        implementation = schema["$defs"]["implementation"]["properties"]
        self.assertEqual(implementation["transactions"]["items"]["$ref"], "#/$defs/transaction")
        self.assertEqual(implementation["modifications"]["items"]["$ref"], "#/$defs/modification")

    def test_alignment_profile_registers_ocds_world_bank_adb_and_bangladesh_extensions(self):
        self.assertTrue(ALIGNMENT.exists())
        self.assertTrue(PROFILE.exists())
        text = ALIGNMENT.read_text()
        for token in (
            "OCDS_1_1_5",
            "WORLD_BANK_IPF_PROCUREMENT_REGULATIONS_7TH_EDITION_2025",
            "WORLD_BANK_STEP",
            "ADB_PROCUREMENT_REGULATIONS",
            "ADB_PROCUREMENT_PLAN",
            "Bangladesh",
            "DGDP",
            "BPPA",
            "e-GP",
        ):
            self.assertIn(token, text)
        profile_text = PROFILE.read_text()
        self.assertIn("bangladesh-procurement-v2.1.schema.json", profile_text)
        self.assertIn("bangladesh-procurement-international-alignment-v1.0.yaml", profile_text)
        self.assertIn("v1.3 remains the active production authority", profile_text)


if __name__ == "__main__":
    unittest.main()
