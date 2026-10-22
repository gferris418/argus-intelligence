"""Contract test for ARGUS 360-degree intelligence collection.

Uses only the Python standard library so it can run in any basic Python 3
checkout and as the repository's initial CI contract gate.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "argus-intelligence.yaml"
SCHEMA = ROOT / "schemas" / "domain-result.schema.json"
MISSION_SCHEMA = ROOT / "schemas" / "collection-mission.schema.json"
CORE = ROOT / "spec" / "core.md"
PROFILE = ROOT / "profiles" / "bangladesh.md"

LENSES = {
    "need_mission",
    "policy_strategy",
    "institution_stakeholders",
    "programme_project",
    "budget_funding",
    "procurement_acquisition",
    "technical_installed_base",
    "supplier_competitor",
    "ecosystem_influence",
    "commercial_participation",
    "timing_triggers",
    "internal_intelligence",
}

COVERAGE_STATES = [
    "NOT_APPLICABLE",
    "UNASSESSED",
    "INSUFFICIENT",
    "PARTIAL",
    "ADEQUATE",
]

STARTUP_SEQUENCE = [
    "RESOLVE_INSTITUTIONAL_HIERARCHY",
    "CHECK_INTERNAL_CANONICAL_REGISTRY",
    "RECONCILE_OPPORTUNITY_IDENTITY",
    "CHECK_OFFICIAL_PROCUREMENT_SOURCES",
    "CHECK_INTERNAL_CUSTOMER_INTELLIGENCE",
    "BUILD_RESEARCH_FRONTIER",
    "EXECUTE_ADAPTIVE_360_COLLECTION",
]


class Collection360ContractTests(unittest.TestCase):
    def test_manifest_declares_360_collection_doctrine(self) -> None:
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("360_intelligence_collection:", text)
        self.assertIn("breadth: all_materially_relevant_lenses", text)
        self.assertIn("depth: decision_driven_by_research_frontier", text)

    def test_core_defines_all_collection_lenses(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        self.assertIn("360° Intelligence Collection Doctrine", text)
        for lens in LENSES:
            self.assertIn(f"`{lens}`", text)

    def test_domain_result_schema_exposes_coverage_and_gaps(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertIn("collection_coverage", props)
        self.assertIn("collection_gaps", props)
        coverage = props["collection_coverage"]
        self.assertEqual(set(coverage["properties"].keys()), LENSES)
        self.assertFalse(coverage["additionalProperties"])

    def test_bangladesh_profile_maps_core_lenses_to_country_collection(self) -> None:
        text = PROFILE.read_text(encoding="utf-8")
        self.assertIn("Bangladesh 360° Collection Map", text)
        for lens in LENSES:
            self.assertIn(f"`{lens}`", text)

    def test_coverage_states_are_governed(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        coverage_props = schema["properties"]["collection_coverage"]["properties"]
        for lens in LENSES:
            self.assertEqual(coverage_props[lens]["enum"], COVERAGE_STATES)

    def test_collection_does_not_add_eighth_record_type(self) -> None:
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("new_record_type_for_collection: false", text)
        self.assertNotIn("- COLLECTION\n", text)

    def test_collection_mission_governs_one_autonomous_startup_sequence(self) -> None:
        schema = json.loads(MISSION_SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("execution_policy", schema["required"])
        policy = schema["properties"]["execution_policy"]
        self.assertFalse(policy["additionalProperties"])
        self.assertEqual(STARTUP_SEQUENCE, policy["properties"]["startup_sequence"]["prefixItems"])

    def test_core_requires_ambiguity_only_user_escalation_after_identity_resolution(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        self.assertIn("Institution-first autonomous startup", text)
        self.assertIn("`EXACT` and `HIGH_CONFIDENCE_MATCH` continue without user confirmation", text)
        self.assertIn("`DISTINCT` continues as a new candidate without user confirmation", text)
        self.assertIn("`PROBABLE_MATCH` and `UNRESOLVED` are the identity-confirmation escalation seam", text)
        self.assertIn("official procurement sources before internal customer intelligence", text)
        self.assertIn("transient mission context", text)


if __name__ == "__main__":
    unittest.main()
