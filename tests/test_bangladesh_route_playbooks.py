from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOKS = ROOT / "profiles/bangladesh-route-playbooks.yaml"


class BangladeshRoutePlaybookTests(unittest.TestCase):
    def test_all_existing_routes_are_preserved(self):
        text = PLAYBOOKS.read_text(encoding="utf-8")
        for route in (
            "BD-GEN-EGP", "BD-DEV-GOB", "BD-DEV-DP", "BD-DEF-DGDP",
            "BD-SOE-AUT", "BD-PPP", "BD-G2G-STRAT", "BD-LOCAL", "BD-UNKNOWN",
        ):
            self.assertIn(f"  {route}:", text)

    def test_every_route_has_w_question_dimensions(self):
        text = PLAYBOOKS.read_text(encoding="utf-8")
        for dimension in (
            "who", "what", "when", "where", "why", "which", "how",
            "how_much_or_many", "evidence", "decision_impact",
        ):
            self.assertGreaterEqual(text.count(f"    {dimension}:"), 9)

    def test_route_is_hypothesis_until_evidenced(self):
        text = PLAYBOOKS.read_text(encoding="utf-8")
        self.assertIn("route_is_hypothesis_until_evidenced: true", text)
        self.assertIn("different_packages_may_use_different_routes: true", text)
        self.assertIn("better_evidence_may_supersede_route: true", text)


if __name__ == "__main__":
    unittest.main()
