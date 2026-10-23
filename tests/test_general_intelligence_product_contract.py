from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class GeneralIntelligenceProductContractTests(unittest.TestCase):
    def test_manifest_declares_collection_candidate(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        product = manifest["product"]
        scope = manifest["scope"]
        compatibility = manifest["atlas_compatibility"]
        self.assertEqual("3.0.0-rc.2", product["version"])
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"**Current candidate:** `{product['version']}`", readme)
        self.assertEqual("candidate", product["release_channel"])
        self.assertEqual("CANDIDATE", product["status"])
        self.assertEqual("ATLAS-governed government commercial opportunity intelligence", scope["primary"])
        self.assertIn("government_public_sector_opportunity_intelligence", scope["specializations"])
        self.assertIn("opportunity_engine", scope)
        self.assertEqual("intelligence_collection", compatibility["activation_capability"])
        self.assertEqual("ARGUS_ACTIVATION", compatibility["approval_key"])
        self.assertTrue(compatibility["explicit_user_approval_required"])
        self.assertEqual("ATLAS", compatibility["provider_return_target"])

    def test_machine_readable_collection_contracts_are_authoritative(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        authority = manifest["authority"]
        core = yaml.safe_load((ROOT / authority["core"]).read_text(encoding="utf-8"))
        method = yaml.safe_load((ROOT / authority["collection_method"]).read_text(encoding="utf-8"))
        opportunity = yaml.safe_load((ROOT / authority["commercial_opportunity_intelligence"]).read_text(encoding="utf-8"))
        plan_schema = json.loads((ROOT / authority["collection_plan_schema"]).read_text(encoding="utf-8"))
        alignment = yaml.safe_load((ROOT / authority["atlas_alignment"]).read_text(encoding="utf-8"))
        activation = json.loads((ROOT / authority["atlas_activation_contract"]).read_text(encoding="utf-8"))
        current = yaml.safe_load((ROOT / authority["atlas_current_integration"]).read_text(encoding="utf-8"))
        self.assertTrue(core["normative"])
        self.assertTrue(method["normative"])
        self.assertTrue(opportunity["normative"])
        self.assertEqual(
            [
                "PIR",
                "EEI",
                "COLLECTION_PLAN",
                "SOURCE_PLAN",
                "COLLECT",
                "SEARCH_LEARNING",
                "RESOLVE",
                "GRADE",
                "COMPETING_HYPOTHESES",
                "GAPS",
                "PACKAGE",
            ],
            method["method"]["stages"],
        )
        self.assertIn("Country", method["target_classes"])
        self.assertIn("Tender", method["target_classes"])
        self.assertIn("Person", method["target_classes"])
        self.assertEqual("material_business_relevance_only", method["person_scope"])
        self.assertIn("priority_intelligence_requirements", plan_schema["required"])
        self.assertIn("essential_elements_of_information", plan_schema["required"])
        self.assertIn("competing_hypotheses", plan_schema["required"])
        self.assertEqual(["ARGUS", "MULTI_CAPABILITY"], core["activation"]["route_mechanisms"])
        self.assertEqual("ATLAS", alignment["atlas_contract"]["activation_authority"])
        self.assertEqual("intelligence_collection", activation["required_capability"])
        self.assertEqual("ARGUS_ACTIVATION", activation["required_approval_key"])
        self.assertTrue(activation["explicit_user_approval_required"])
        self.assertEqual("ATLAS", current["contract"]["next_step_authority"])
        self.assertFalse(alignment["routing"]["policy_analysis_alone_activates_argus"])

    def test_collection_method_stops_before_atlas_final_business_decision(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        method = yaml.safe_load((ROOT / manifest["authority"]["collection_method"]).read_text(encoding="utf-8"))
        self.assertIn("collection_package", method["outputs"])
        self.assertIn("collection_gaps", method["outputs"])
        self.assertIn("unresolved_hypotheses", method["outputs"])
        self.assertIn("research_learning_records", method["outputs"])
        self.assertNotIn("final_business_decision", method["outputs"])
        self.assertEqual("ATLAS_OS", method["handoff_to"]["analysis_owner"])
        self.assertEqual("ATLAS_OS", method["handoff_to"]["decision_owner"])

    def test_manifest_preserves_atlas_governance_ownership(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        compatibility = manifest["atlas_compatibility"]
        self.assertFalse(compatibility["creates_execution_spine"])
        self.assertFalse(compatibility["owns_planning"])
        self.assertFalse(compatibility["owns_approvals"])
        self.assertFalse(compatibility["owns_final_business_decision"])
        self.assertEqual("ATLAS", compatibility["activation_authority"])
        self.assertEqual("ATLAS", compatibility["next_step_authority"])
        self.assertEqual("backward_compatibility_only", compatibility["legacy_signed_transport"]["status"])


if __name__ == "__main__":
    unittest.main()
