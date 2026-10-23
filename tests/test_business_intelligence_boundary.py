from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class BusinessIntelligenceBoundaryTests(unittest.TestCase):
    def _load(self, relative_path: str) -> dict:
        return yaml.safe_load((ROOT / relative_path).read_text(encoding="utf-8"))

    def test_argus_is_360_business_intelligence_playbook_under_atlas(self) -> None:
        boundary = self._load("spec/business-intelligence-boundary.yaml")
        self.assertEqual("ARGUS_360_BUSINESS_INTELLIGENCE_PLAYBOOK", boundary["identity"])
        self.assertEqual("FRAMEWORK", boundary["roles"]["ATLAS_OS"])
        self.assertEqual("BUSINESS_INTELLIGENCE_PLAYBOOK", boundary["roles"]["ARGUS"])
        self.assertEqual("ATLAS_ONLY", boundary["provider_model"]["provider_selection"])

    def test_argus_does_not_gain_transactional_business_execution_authority(self) -> None:
        boundary = self._load("spec/business-intelligence-boundary.yaml")
        exclusions = set(boundary["operational_exclusions"])
        self.assertTrue(
            {
                "BID_SUBMISSION_EXECUTION",
                "PROJECT_MILESTONE_ACCEPTANCE_AUTHORITY",
                "INVOICE_ISSUANCE_AUTHORITY",
                "PAYMENT_EXECUTION_AUTHORITY",
                "ACCOUNTING_LEDGER_AUTHORITY",
            }.issubset(exclusions)
        )
        self.assertFalse(boundary["fact_store_semantics"]["transactional_execution_authority"])

    def test_px_workspace_lineage_preserves_pre_award_opportunity_folder(self) -> None:
        registry = self._load("profiles/access-asia-system-registry.yaml")
        lifecycle = registry["lifecycle"]
        self.assertEqual("General/REV/OPP Opportunities", lifecycle["promote_to_px"]["sharepoint_home"])
        self.assertFalse(lifecycle["submission_active"]["move_existing_lineage"])
        self.assertFalse(lifecycle["awarded_or_contract_activated"]["move_existing_lineage"])
        self.assertTrue(lifecycle["awarded_or_contract_activated"]["preserve_source_workspace"])
        self.assertTrue(lifecycle["awarded_or_contract_activated"]["create_linked_project_workspace"])

        opportunity_lifecycle = self._load("profiles/access-asia-opportunity-lifecycle.yaml")
        self.assertEqual("General/REV/OPP Opportunities", opportunity_lifecycle["tracked_opportunity"]["destination_home"])
        self.assertFalse(opportunity_lifecycle["submission"]["move_entire_folder_if_present"])
        self.assertFalse(opportunity_lifecycle["project"]["move_entire_folder"])
        self.assertTrue(opportunity_lifecycle["project"]["preserve_source_workspace"])
        self.assertTrue(opportunity_lifecycle["project"]["create_linked_project_workspace"])

    def test_financial_records_are_bi_facts_not_an_accounting_ledger(self) -> None:
        standard = self._load("profiles/access-asia-commercial-data-standard-v1.0.yaml")
        rules = standard["financial_fact_rules"]
        self.assertTrue(rules["business_intelligence_fact_only"])
        self.assertFalse(rules["transactional_ledger_authority"])
        exclusions = set(standard["system_ownership"]["ARGUS_SHAREPOINT_SQLITE"]["excludes"])
        self.assertIn("invoice_issuance_authority", exclusions)
        self.assertIn("payment_execution_authority", exclusions)
        self.assertIn("accounting_ledger_authority", exclusions)


if __name__ == "__main__":
    unittest.main()
