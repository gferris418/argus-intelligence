from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STANDARD = ROOT / "profiles" / "access-asia-commercial-data-standard-v1.0.yaml"
IDENTITY = ROOT / "profiles" / "canonical-object-identity-standard-v1.0.yaml"
SUPPLIER_SCHEMA = ROOT / "schemas" / "supplier-intelligence.schema.json"
SYSTEM_REGISTRY = ROOT / "profiles" / "access-asia-system-registry.yaml"
LIFECYCLE = ROOT / "profiles" / "access-asia-opportunity-lifecycle.yaml"


class CanonicalCommercialGraphTests(unittest.TestCase):
    def test_company_wide_commercial_graph_standard_exists(self) -> None:
        standard = yaml.safe_load(STANDARD.read_text(encoding="utf-8"))

        self.assertEqual("ACTIVE", standard["status"])
        self.assertEqual("ARGUS", standard["canonical_graph_owner"])
        self.assertEqual(
            "enter_once_identify_once_relate_once_derive_views",
            standard["core_principle"],
        )
        self.assertTrue(standard["rules"]["department_views_are_derived"])
        self.assertFalse(standard["rules"]["department_databases_allowed"])
        self.assertTrue(standard["rules"]["material_facts_require_provenance"])
        self.assertTrue(standard["rules"]["history_is_append_only"])

    def test_px_is_permanent_cross_department_lineage(self) -> None:
        standard = yaml.safe_load(STANDARD.read_text(encoding="utf-8"))
        px = standard["commercial_lineage"]["px"]

        self.assertEqual("ATLAS_OS", px["authority"])
        self.assertTrue(px["immutable_after_assignment"])
        self.assertTrue(px["preserve_through_bid_award_project"])
        self.assertEqual(
            ["OPPORTUNITY", "BID", "AWARD", "ACCESS_ASIA_PROJECT"],
            standard["commercial_lineage"]["objects"],
        )

    def test_reporting_dimensions_and_value_semantics_are_not_collapsed(self) -> None:
        standard = yaml.safe_load(STANDARD.read_text(encoding="utf-8"))

        self.assertEqual(
            {"MARKETING", "SALES", "BUSINESS_DEVELOPMENT", "OPERATIONS", "FINANCE", "MANAGEMENT"},
            set(standard["department_views"]),
        )
        values = set(standard["value_semantics"])
        self.assertTrue({
            "government_project_value",
            "procurement_estimated_value",
            "bid_value",
            "award_value",
            "contract_value",
            "access_asia_revenue_value",
            "commission_value",
            "expected_margin",
            "actual_margin",
        }.issubset(values))

    def test_identity_standard_has_bid_and_access_asia_project_without_reclassifying_government_project(self) -> None:
        identity = yaml.safe_load(IDENTITY.read_text(encoding="utf-8"))
        object_types = identity["canonical_object_types"]

        self.assertEqual("Project or implementation initiative", object_types["PROJECT"]["description"])
        self.assertIn("BID", object_types)
        self.assertIn("ACCESS_ASIA_PROJECT", object_types)

    def test_supplier_identity_is_argus_canonical_and_hubspot_link_is_optional(self) -> None:
        schema = json.loads(SUPPLIER_SCHEMA.read_text(encoding="utf-8"))

        self.assertIn("supplier_id", schema["required"])
        self.assertNotIn("crm_ref", schema["required"])
        self.assertIn("crm_ref", schema["properties"])
        self.assertIn("ARGUS", schema["description"])

    def test_system_routing_separates_graph_crm_documents_and_code(self) -> None:
        registry = yaml.safe_load(SYSTEM_REGISTRY.read_text(encoding="utf-8"))

        sqlite = registry["systems"]["argus_sharepoint_sqlite"]
        hubspot = registry["systems"]["hubspot"]
        routing = registry["persistence_routing"]

        self.assertIn("canonical_commercial_graph", sqlite["owns"])
        self.assertNotIn("company_identity_and_profile", hubspot["owns"])
        self.assertIn("access_asia_relationship_state", hubspot["owns"])
        self.assertEqual("ARGUS_SHAREPOINT_SQLITE", routing["CANONICAL_ORGANIZATION"])
        self.assertEqual("ARGUS_SHAREPOINT_SQLITE", routing["CANONICAL_PRODUCT"])
        self.assertEqual("HUBSPOT", routing["CRM_INTERACTION"])
        self.assertEqual("SHAREPOINT", routing["SOURCE_DOCUMENT"])
        self.assertEqual("ARGUS_GITHUB", routing["ARGUS_SCHEMA"])

    def test_lifecycle_preserves_px_and_distinguishes_bid_from_project(self) -> None:
        lifecycle = yaml.safe_load(LIFECYCLE.read_text(encoding="utf-8"))

        self.assertTrue(lifecycle["commercial_identity"]["preserve_across_stage_moves"])
        self.assertEqual("BID", lifecycle["submission"]["canonical_object_type"])
        self.assertEqual("ACCESS_ASIA_PROJECT", lifecycle["project"]["canonical_object_type"])
        self.assertTrue(lifecycle["project"]["preserve_commercial_id"])


if __name__ == "__main__":
    unittest.main()
