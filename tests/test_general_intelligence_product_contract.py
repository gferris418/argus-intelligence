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

    def test_machine_readable_general_intelligence_contracts_are_authoritative(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        authority = manifest["authority"]
        self.assertEqual("spec/general-intelligence.yaml", authority["core"])
        self.assertEqual("alignments/atlas-os-triage-v2.yaml", authority["atlas_alignment"])
        self.assertEqual("spec/core.md", authority["public_sector_opportunity_doctrine"])
        core = yaml.safe_load((ROOT / authority["core"]).read_text(encoding="utf-8"))
        alignment = yaml.safe_load((ROOT / authority["atlas_alignment"]).read_text(encoding="utf-8"))
        self.assertTrue(core["normative"])
        self.assertEqual("INTELLIGENCE", core["activation"]["request_route"])
        self.assertEqual(["GENERAL_SEARCH", "GENERAL_TASK"], alignment["routing"]["direct_routes"])
        self.assertFalse(alignment["routing"]["government_mention_alone_activates_argus"])

    def test_manifest_preserves_atlas_governance_ownership(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        compatibility = manifest["atlas_compatibility"]
        self.assertFalse(compatibility["creates_execution_spine"])
        self.assertFalse(compatibility["owns_planning"])
        self.assertFalse(compatibility["owns_approvals"])
        self.assertTrue(compatibility["handoff_required_in_access_asia_production"])


if __name__ == "__main__":
    unittest.main()
