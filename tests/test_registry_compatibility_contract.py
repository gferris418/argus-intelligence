import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "tests" / "fixtures" / "registry-v0.2.0-compatibility-slice.json").read_text())
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()

ROUTES = {
    "BD-GEN-EGP",
    "BD-DEV-GOB",
    "BD-DEV-DP",
    "BD-DEF-DGDP",
    "BD-PPP",
}

RC2_ATTRIBUTE_FIELDS = {
    "country_profile",
    "bangladesh_route",
    "route_confidence",
    "project_state",
    "funding_state",
    "procurement_planning_state",
    "collection_coverage",
    "collection_gaps",
    "source_convergence",
}


class RegistryCompatibilityContract(unittest.TestCase):
    def test_fixture_is_bound_to_registry_v020(self):
        self.assertEqual(FIXTURE["source"]["document_id"], "ARGUS-SCHEMA-REG-001")
        self.assertEqual(FIXTURE["source"]["version"], "0.2.0")
        self.assertEqual(
            FIXTURE["source"]["sha256"],
            "2dad9c73dc0236395fe0418f6694ee53b478ccc51c86996d8bc00abff5f2f808",
        )

    def test_route_and_360_fields_are_additive_inside_attributes(self):
        self.assertTrue(FIXTURE["record"]["attributes_additional_properties"])
        self.assertIn("maturity", FIXTURE["record"]["intelligence_required_attributes"])
        self.assertEqual(len(ROUTES), 5)
        self.assertEqual(len(RC2_ATTRIBUTE_FIELDS), 9)

    def test_evidence_split_is_not_representable_at_evidence_ref_level(self):
        evidence = FIXTURE["evidence_ref"]
        self.assertFalse(evidence["additional_properties"])
        self.assertNotIn("claim_type", evidence["properties"])
        self.assertNotIn("claim_condition", evidence["properties"])
        self.assertIn("CONFLICT", evidence["analytical_label_enum"])
        self.assertIn("STALE", evidence["analytical_label_enum"])

    def test_manifest_tracks_candidate_fix_and_database_deferral_separately(self):
        self.assertIn("claim type and claim condition candidate schema contract: PASS", MANIFEST)
        self.assertIn("operational database deployment for current phase: DEFERRED_NOT_REQUIRED", MANIFEST)
        self.assertIn("evidence_claim_type_condition_split: CANDIDATE_CONTRACT_PASS", MANIFEST)
        self.assertIn("database_materialization_work: deferred_until_runtime_need", MANIFEST)


if __name__ == "__main__":
    unittest.main()
