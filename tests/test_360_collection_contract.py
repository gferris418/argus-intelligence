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


if __name__ == "__main__":
    unittest.main()
