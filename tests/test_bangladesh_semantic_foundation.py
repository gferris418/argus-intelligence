from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "argus-intelligence.yaml"
ARCHITECTURE = ROOT / "docs/architecture/bangladesh-opportunity-intelligence-v3.md"


class BangladeshSemanticFoundationTests(unittest.TestCase):
    def test_primary_lifecycle_remains_s0_s9(self):
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("lifecycle_stages: [S0, S1, S2, S3, S4, S5, S6, S7, S8, S9]", text)
        self.assertIn("status: compatibility_only", text)
        self.assertIn("replaced_primary_model_by: S0_S9_lifecycle_plus_opportunity_mode", text)

    def test_manifest_registers_bangladesh_semantic_authority(self):
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("bangladesh_opportunity_architecture: docs/architecture/bangladesh-opportunity-intelligence-v3.md", text)
        self.assertIn("bangladesh_w_question_contract:", text)
        for dimension in (
            "who", "what", "when", "where", "why", "which", "how",
            "how_much_or_many", "evidence", "decision_impact",
        ):
            self.assertIn(f"    {dimension}:", text)

    def test_architecture_separates_graphs_traversal_and_analysis(self):
        text = ARCHITECTURE.read_text(encoding="utf-8")
        for graph in ("INSTITUTION_GRAPH", "OPPORTUNITY_GRAPH", "MARKET_GRAPH"):
            self.assertIn(graph, text)
        for traversal in (
            "TOP_DOWN", "BOTTOM_UP", "UPSTREAM", "DOWNSTREAM",
            "LATERAL_GOVERNMENT", "LATERAL_MARKET", "HISTORICAL",
            "SUCCESSOR", "ADJACENT",
        ):
            self.assertIn(traversal, text)
        for capability in (
            "EVENT_RECONCILIATION", "HYPOTHESIS_TESTING",
            "INDICATORS_SIGNPOSTS", "RESEARCH_FRONTIER",
        ):
            self.assertIn(capability, text)
        self.assertIn("not lifecycle stages", text.lower())

    def test_w_question_contract_is_completeness_lens_not_state_machine(self):
        text = ARCHITECTURE.read_text(encoding="utf-8")
        self.assertIn("documentation completeness lens", text.lower())
        self.assertIn("NOT_APPLICABLE", text)
        self.assertIn("S0–S9 remains primary", text)
        self.assertIn("I0–I9 remains compatibility-only", text)


if __name__ == "__main__":
    unittest.main()
