from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AccessAsiaDataOwnershipTests(unittest.TestCase):
    def test_px_promotion_establishes_single_rev_opp_pre_award_workspace(self) -> None:
        text = (ROOT / "profiles" / "access-asia-opportunity-lifecycle.yaml").read_text(encoding="utf-8")
        tracked = text.split("tracked_opportunity:", 1)[1].split("\nsubmission:", 1)[0]
        submission = text.split("submission:", 1)[1].split("\naward:", 1)[0]
        project = text.split("project:", 1)[1].split("\nnon_submission_outcomes:", 1)[0]

        self.assertIn("destination_home: General/REV/OPP Opportunities", tracked)
        self.assertIn("move_entire_folder_if_present: true", tracked)
        self.assertIn("source_home: General/REV/OPP Opportunities", submission)
        self.assertIn("working_home: General/REV/OPP Opportunities", submission)
        self.assertIn("move_entire_folder_if_present: false", submission)
        self.assertIn("destination_home: General/OPS/PRJ Projects", project)
        self.assertIn("move_entire_folder: false", project)
        self.assertIn("preserve_source_workspace: true", project)
        self.assertIn("create_linked_project_workspace: true", project)

    def test_supplier_intelligence_uses_argus_identity_and_optional_hubspot_mirror(self) -> None:
        schema = json.loads((ROOT / "schemas" / "supplier-intelligence.schema.json").read_text(encoding="utf-8"))
        self.assertIn("supplier_id", schema["required"])
        self.assertNotIn("crm_ref", schema["required"])
        self.assertNotIn("legal_name", schema["required"])
        self.assertNotIn("country", schema["required"])

        crm_ref = schema["properties"]["crm_ref"]
        self.assertEqual(["object", "null"], crm_ref["type"])
        self.assertEqual("HUBSPOT", crm_ref["properties"]["system"]["const"])
        self.assertEqual("COMPANY", crm_ref["properties"]["object_type"]["const"])
        self.assertIn("integration_key", crm_ref["required"])
        self.assertIn("company_id", crm_ref["properties"])

        partnerability = schema["properties"]["partnerability"]["properties"]
        self.assertNotIn("access_asia_relationship", partnerability)
        self.assertNotIn("contactability", partnerability)

    def test_storage_policy_names_argus_hubspot_sharepoint_and_pointer_only_cross_system_links(self) -> None:
        text = (ROOT / "docs" / "architecture" / "canonical-identity-operational-database-v1.md").read_text(encoding="utf-8")
        registry = (ROOT / "profiles" / "access-asia-system-registry.yaml").read_text(encoding="utf-8")
        self.assertIn("HubSpot", text)
        self.assertIn("SharePoint SQLite", text)
        self.assertIn("stable_integration_key_plus_runtime_resolution", registry)
        self.assertIn("reference", text.lower())
        self.assertIn("public", text.lower())
        self.assertIn("must never be committed", text.lower())
        self.assertIn("canonical_commercial_graph", registry)
        self.assertIn("derived_views_over_canonical_graph", registry)


if __name__ == "__main__":
    unittest.main()
