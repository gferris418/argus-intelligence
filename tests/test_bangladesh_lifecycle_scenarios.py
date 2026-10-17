import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = json.loads((ROOT / "tests" / "scenarios" / "bangladesh-lifecycle-rc2.json").read_text())
PROFILE = (ROOT / "profiles" / "bangladesh.md").read_text()
CORE = (ROOT / "spec" / "core.md").read_text()
ALIGNMENT = (ROOT / "alignments" / "atlas-os.md").read_text()

SCENARIOS = {x["id"]: x for x in SUITE["scenarios"]}


class BangladeshLifecycleScenarios(unittest.TestCase):
    def test_app_tender_amendment_award_is_one_underlying_opportunity(self):
        s = SCENARIOS["BD-APP-TENDER-AMENDMENT-AWARD"]
        self.assertEqual(s["expected"]["canonical_opportunity_count"], 1)
        self.assertFalse(s["expected"]["new_opportunity_per_event"])
        self.assertEqual([e["type"] for e in s["events"]], ["APP_PACKAGE", "TENDER", "AMENDMENT", "AWARD"])
        self.assertIn("Do not create duplicate opportunities", PROFILE)
        self.assertIn("A new document, tender, amendment or award does not automatically create a new commercial opportunity", CORE)

    def test_defence_evaluation_is_preproc_not_live_tender(self):
        s = SCENARIOS["BD-DEFENCE-PREPROC-EVALUATION"]
        self.assertEqual(s["route"], "BD-DEF-DGDP")
        self.assertEqual(s["expected"]["maturity"], "I7")
        self.assertFalse(s["expected"]["treat_as_live_tender"])
        self.assertFalse(s["expected"]["automatic_px_creation"])
        self.assertIn("evaluation/re-evaluation/standardization", PROFILE)
        self.assertIn("defence/national-security", PROFILE)

    def test_cross_fiscal_project_keeps_one_lineage(self):
        s = SCENARIOS["BD-CROSS-FISCAL-PROJECT-LINEAGE"]
        fiscal_years = {x["fiscal_year"] for x in s["appearances"]}
        self.assertGreater(len(fiscal_years), 1)
        self.assertEqual(s["expected"]["canonical_project_count"], 1)
        self.assertEqual(s["expected"]["canonical_opportunity_count"], 1)
        self.assertFalse(s["expected"]["new_opportunity_per_fiscal_year"])
        self.assertIn("successive ADPs/RADPs", PROFILE)

    def test_promotion_can_precede_tender_but_px_creation_is_separate(self):
        s = SCENARIOS["BD-PROMOTION-BEFORE-LIVE-TENDER"]
        self.assertFalse(s["live_tender"])
        self.assertEqual(s["expected"]["decision"], "PROMOTE_TO_PX")
        self.assertTrue(all(s["promotion_basis"].values()))
        self.assertFalse(s["expected"]["permanent_px_created_by_decision_alone"])
        self.assertEqual(s["expected"]["atlas_approval_gate"], "major_canonical_state_change")
        self.assertIn("PROMOTE_TO_PX", CORE)
        self.assertIn("major canonical", ALIGNMENT.lower())


if __name__ == "__main__":
    unittest.main()
