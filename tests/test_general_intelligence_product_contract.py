from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class GeneralIntelligenceProductContractTests(unittest.TestCase):
    def test_manifest_declares_general_intelligence_candidate(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        product = manifest["product"]
        scope = manifest["scope"]
        compatibility = manifest["atlas_compatibility"]

        self.assertEqual("2.1.0-rc.1", product["version"])
        self.assertEqual("candidate", product["release_channel"])
        self.assertEqual("CANDIDATE", product["status"])
        self.assertEqual("general strategic and decision intelligence", scope["primary"])
        self.assertIn("government_public_sector_opportunity_intelligence", scope["specializations"])
        self.assertEqual("INTELLIGENCE", compatibility["activation_request_route"])
        self.assertEqual("intelligence_analysis", compatibility["activation_capability"])
        self.assertEqual("2.0.0", compatibility["activation_contract_version"])
        self.assertEqual("ARGUS_ENRICHES", compatibility["partial_handoff_semantics"])

    def test_manifest_preserves_atlas_governance_ownership(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        compatibility = manifest["atlas_compatibility"]
        self.assertFalse(compatibility["creates_execution_spine"])
        self.assertFalse(compatibility["owns_planning"])
        self.assertFalse(compatibility["owns_approvals"])
        self.assertTrue(compatibility["handoff_required_in_access_asia_production"])


if __name__ == "__main__":
    unittest.main()
