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

    def test_activation_uses_one_generic_intelligence_capability(self) -> None:
        contract = self._contract()
        self.assertEqual("atlas_request_triage", contract["activation_mechanism"])
        self.assertEqual("intelligence_analysis", contract["required_capability"])
        self.assertEqual("INTELLIGENCE", contract["required_request_route"])
        self.assertEqual(["READY", "PARTIAL"], contract["accepted_handoff_states"])
        self.assertEqual("REJECT_DEPENDENT_EXECUTION", contract["blocked_handoff_behavior"])
        self.assertTrue(contract["requires_atlas_domain_context_handoff"])

    def test_contract_declares_broad_intelligence_modes(self) -> None:
        contract = self._contract()
        self.assertEqual(
            {
                "STRATEGIC_INTELLIGENCE",
                "MARKET_INTELLIGENCE",
                "OPPORTUNITY_INTELLIGENCE",
                "COMPETITIVE_INTELLIGENCE",
                "STAKEHOLDER_INTELLIGENCE",
                "POLITICAL_ECONOMIC_INTELLIGENCE",
                "MONITORING_INTELLIGENCE",
                "FORECASTING_INTELLIGENCE",
                "SCENARIO_INTELLIGENCE",
                "DECISION_INTELLIGENCE",
            },
            set(contract["supported_intelligence_types"]),
        )

    def test_domain_context_may_be_partial_at_activation(self) -> None:
        contract = self._contract()
        self.assertEqual("ATLAS_OS", contract["ownership"]["request_triage"])
        self.assertEqual("ARGUS", contract["ownership"]["intelligence_domain_enrichment"])
        self.assertIn("PARTIAL", contract["accepted_handoff_states"])
        self.assertEqual("ARGUS_ENRICHES", contract["partial_handoff_semantics"])

    def test_argus_has_no_keyword_or_background_auto_activation(self) -> None:
        contract = self._contract()
        self.assertFalse(contract["keyword_activation"])
        self.assertFalse(contract["background_activation"])
        self.assertIn("generic factual explanation", contract["non_triggers"])
        self.assertIn("simple current-information search without an intelligence objective", contract["non_triggers"])
        self.assertIn("general writing or translation", contract["non_triggers"])


if __name__ == "__main__":
    unittest.main()
