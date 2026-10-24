"""Release-blocking regression tests for the three modular ARGUS pilot missions."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "tests" / "scenarios" / "modular-skill-pilots.json"
ROUTING = ROOT / "spec" / "mission-skill-routing.yaml"


class ModularSkillPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        cls.routing = yaml.safe_load(ROUTING.read_text(encoding="utf-8"))

    def _profile(self, key: str) -> dict:
        return self.routing["pilot_profiles"][key]

    def test_cpv_is_full_chain_live_procurement_and_reuses_lineage(self) -> None:
        expected = self.scenarios["COASTAL_PATROL_VESSEL_BCG"]
        actual = self._profile("COASTAL_PATROL_VESSEL_BCG")
        self.assertEqual(expected["mission_state"], actual["mission_state"])
        self.assertEqual(expected["procurement_mode"], actual["procurement_mode"])
        self.assertEqual(expected["specialists"], actual["specialist_plan"])
        self.assertTrue(actual["reuse_existing_lineage"])
        self.assertTrue(actual["latest_authoritative_event_controls_current_dates"])

    def test_radar_stays_seed_and_cannot_promote_from_supplier_coverage(self) -> None:
        expected = self.scenarios["COASTAL_SURVEILLANCE_RADAR_BN"]
        actual = self._profile("COASTAL_SURVEILLANCE_RADAR_BN")
        self.assertEqual(expected["mission_state"], actual["mission_state"])
        self.assertEqual(expected["procurement_mode"], actual["procurement_mode"])
        self.assertEqual(expected["specialists"], actual["specialist_plan"])
        self.assertTrue(actual["live_procurement_requires_authoritative_evidence"])
        self.assertTrue(actual["supplier_coverage_cannot_promote_opportunity"])

    def test_badc_requires_revalidation_and_secondary_source_cannot_promote_lifecycle(self) -> None:
        expected = self.scenarios["SEED_CLEANER_CUM_GRADER_BADC"]
        actual = self._profile("SEED_CLEANER_CUM_GRADER_BADC")
        self.assertEqual(expected["mission_state"], actual["mission_state"])
        self.assertEqual(expected["procurement_mode"], actual["procurement_mode"])
        self.assertEqual(expected["specialists"], actual["specialist_plan"])
        self.assertTrue(actual["stale_revalidation_required"])
        self.assertTrue(actual["historical_need_not_current_lifecycle"])
        self.assertTrue(actual["secondary_source_cannot_promote_canonical_lifecycle"])


if __name__ == "__main__":
    unittest.main()
