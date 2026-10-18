import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "atlas" / "argus-activation-v1.json"


class ArgusActivationContractTests(unittest.TestCase):
    def _contract(self) -> dict:
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_atlas_owns_activation_and_the_single_execution_spine(self) -> None:
        contract = self._contract()
        self.assertEqual("ATLAS_OS", contract["activation_authority"])
        self.assertEqual("ATLAS_OS", contract["ownership"]["execution_spine"])
        self.assertEqual("ATLAS_OS", contract["ownership"]["planning"])
        self.assertEqual("ATLAS_OS", contract["ownership"]["approvals"])
        self.assertEqual("ARGUS", contract["ownership"]["domain_analysis"])

    def test_activation_requires_explicit_capability_and_valid_handoff(self) -> None:
        contract = self._contract()
        self.assertEqual(
            "government_public_sector_opportunity_intelligence",
            contract["required_capability"],
        )
        self.assertEqual(["READY", "PARTIAL"], contract["accepted_handoff_states"])
        self.assertEqual("REJECT_DEPENDENT_EXECUTION", contract["blocked_handoff_behavior"])
        self.assertTrue(contract["requires_atlas_domain_context_handoff"])

    def test_argus_has_no_keyword_or_background_auto_activation(self) -> None:
        contract = self._contract()
        self.assertFalse(contract["keyword_activation"])
        self.assertFalse(contract["background_activation"])
        self.assertIn("generic factual explanation", contract["non_triggers"])
        self.assertIn("organization mentioned without opportunity-intelligence objective", contract["non_triggers"])


if __name__ == "__main__":
    unittest.main()
