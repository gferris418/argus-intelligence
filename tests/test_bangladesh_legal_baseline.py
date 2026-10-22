from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "profiles/bangladesh-legal-baseline.yaml"


class BangladeshLegalBaselineTests(unittest.TestCase):
    def test_baseline_is_dated_and_revalidated_when_material(self):
        text = BASELINE.read_text(encoding="utf-8")
        self.assertIn("effective_as_of: 2026-10-22", text)
        self.assertIn("revalidate_if_material: true", text)
        self.assertIn("never_treat_cached_text_as_current_law: true", text)

    def test_known_current_framework_is_recorded_without_overclaim(self):
        text = BASELINE.read_text(encoding="utf-8")
        self.assertIn("Public Procurement Act 2006", text)
        self.assertIn("Public Procurement (Amendment) Act 2026", text)
        self.assertIn("Public Procurement Rules 2025", text)
        self.assertIn("status: CURRENT_BASELINE", text)

    def test_recent_unresolved_change_is_flagged_for_revalidation(self):
        text = BASELINE.read_text(encoding="utf-8")
        self.assertIn("2026-09-22", text)
        self.assertIn("status: REVALIDATE_BEFORE_RELIANCE", text)

    def test_each_material_rule_uses_w_question_contract(self):
        text = BASELINE.read_text(encoding="utf-8")
        for field in (
            "who", "what", "when", "where", "why", "which", "how",
            "how_much_or_many", "source",
        ):
            self.assertIn(f"    {field}:", text)


if __name__ == "__main__":
    unittest.main()
