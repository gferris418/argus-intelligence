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
        self.assertEqual("2.2.0-rc.1", product["version"])
        self.assertEqual("candidate", product["release_channel"])
        self.assertEqual("CANDIDATE", product["status"])
        self.assertEqual("ATLAS-governed structured intelligence collection", scope["primary"])
        self.assertIn("government_public_sector_opportunity_intelligence", scope["specializations"])
        self.assertEqual(["ARGUS_COLLECTION", "HYBRID"], compatibility["activation_collection_modes"])
        self.assertEqual("intelligence_collection", compatibility["activation_capability"])
        self.assertEqual("3.0.0", compatibility["activation_contract_version"])

    def test_machine_readable_collection_contracts_are_authoritative(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        authority = manifest["authority"]
        core = yaml.safe_load((ROOT / authority["core"]).read_text(encoding="utf-8"))
        alignment = yaml.safe_load((ROOT / authority["atlas_alignment"]).read_text(encoding="utf-8"))
        activation = json.loads((ROOT / authority["atlas_activation_contract"]).read_text(encoding="utf-8"))
        self.assertTrue(core["normative"])
        self.assertEqual(["ARGUS_COLLECTION", "HYBRID"], core["activation"]["collection_modes"])
        self.assertEqual("COLLECTION_NEED_GATE", alignment["atlas_contract"]["activation_gate"])
        self.assertEqual("intelligence_collection", activation["required_capability"])
        self.assertFalse(alignment["routing"]["policy_analysis_alone_activates_argus"])

    def test_manifest_preserves_atlas_governance_ownership(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        compatibility = manifest["atlas_compatibility"]
        self.assertFalse(compatibility["creates_execution_spine"])
        self.assertFalse(compatibility["owns_planning"])
        self.assertFalse(compatibility["owns_approvals"])
        self.assertFalse(compatibility["owns_analysis_and_decision"])
        self.assertTrue(compatibility["handoff_required_in_access_asia_production"])


if __name__ == "__main__":
    unittest.main()
