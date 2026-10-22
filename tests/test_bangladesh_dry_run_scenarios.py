from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "profiles/bangladesh-dry-run-scenarios.yaml"


class BangladeshDryRunScenarioTests(unittest.TestCase):
    def test_required_scenarios_exist(self):
        text = SCENARIOS.read_text(encoding="utf-8")
        for scenario in (
            "POLICY_SIGNAL_ONLY", "PROJECT_UNDER_APPRAISAL", "APPROVED_ADP_PROJECT",
            "APP_PACKAGE_APPEARS", "DGDP_STANDARDIZATION", "LIVE_EGP_TENDER",
            "DEVELOPMENT_PARTNER_PLAN", "AWARD_FOUND_FIRST", "ALLOCATION_REDUCED",
            "TENDER_CANCELLED_REISSUED", "SIMILAR_ITEM_SAME_END_USER", "OLD_INSTALLED_BASE",
            "CONFLICTING_SOURCES", "MULTIPLE_POSSIBLE_ROUTES", "OEM_DISCOVERED_FIRST",
        ):
            self.assertIn(f"  {scenario}:", text)

    def test_s0_s9_remains_primary_in_dry_runs(self):
        text = SCENARIOS.read_text(encoding="utf-8")
        self.assertIn("primary_lifecycle: S0_S9", text)
        self.assertIn("legacy_maturity: I0_I9_COMPATIBILITY_ONLY", text)

    def test_lineage_and_hypothesis_safety_rules_are_explicit(self):
        text = SCENARIOS.read_text(encoding="utf-8")
        self.assertIn("new_opportunity: false", text)
        self.assertIn("successor_hypothesis_only: true", text)
        self.assertIn("preserve_contradiction: true", text)
        self.assertIn("competing_hypotheses_required: true", text)


if __name__ == "__main__":
    unittest.main()
