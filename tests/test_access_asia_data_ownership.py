from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AccessAsiaDataOwnershipTests(unittest.TestCase):
    def test_px_promotion_stays_in_business_intelligence_until_submission_active(self) -> None:
        text = (ROOT / "profiles" / "access-asia-opportunity-lifecycle.yaml").read_text(encoding="utf-8")
        tracked = text.split("tracked_opportunity:", 1)[1].split("\nsubmission:", 1)[0]
        submission = text.split("submission:", 1)[1].split("\nproject:", 1)[0]

        self.assertIn("destination_home: General/Business Intelligence/50_OPPORTUNITIES", tracked)
        self.assertIn("move_entire_folder_if_present: false", tracked)
        self.assertIn("source_home: General/Business Intelligence/50_OPPORTUNITIES", submission)
        self.assertIn("working_home: General/REV/OPP Opportunities", submission)

    def test_supplier_intelligence_links_to_hubspot_instead_of_owning_crm_master_data(self) -> None:
        schema = json.loads((ROOT / "schemas" / "supplier-intelligence.schema.json").read_text(encoding="utf-8"))
        self.assertIn("crm_ref", schema["required"])
        self.assertNotIn("legal_name", schema["required"])
        self.assertNotIn("country", schema["required"])

        crm_ref = schema["properties"]["crm_ref"]
        self.assertEqual("HUBSPOT", crm_ref["properties"]["system"]["const"])
        self.assertEqual("COMPANY", crm_ref["properties"]["object_type"]["const"])
        self.assertIn("integration_key", crm_ref["required"])
        self.assertIn("company_id", crm_ref["properties"])

        partnerability = schema["properties"]["partnerability"]["properties"]
        self.assertNotIn("access_asia_relationship", partnerability)
        self.assertNotIn("contactability", partnerability)

    def test_storage_policy_names_hubspot_sharepoint_and_pointer_only_cross_system_links(self) -> None:
        text = (ROOT / "docs" / "architecture" / "canonical-identity-operational-database-v1.md").read_text(encoding="utf-8")
        registry = (ROOT / "profiles" / "access-asia-system-registry.yaml").read_text(encoding="utf-8")
        self.assertIn("HubSpot", text)
        self.assertIn("SharePoint SQLite", text)
        self.assertIn("stable_integration_key_plus_runtime_resolution", registry)
        self.assertIn("reference", text.lower())
        self.assertIn("public", text.lower())
        self.assertIn("must never be committed", text.lower())


if __name__ == "__main__":
    unittest.main()
