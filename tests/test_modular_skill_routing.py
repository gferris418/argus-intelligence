"""Contract tests for maturity-aware ARGUS specialist routing."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "spec" / "mission-skill-routing.yaml"
SCHEMA = ROOT / "schemas" / "mission-skill-plan.schema.json"
MANIFEST = ROOT / "argus-intelligence.yaml"

MISSION_STATES = {
    "SEED",
    "NEED_OBSERVED",
    "PROJECT_IDENTIFIED",
    "PROCUREMENT_EXPECTED",
    "PROCUREMENT_LIVE",
    "PROCUREMENT_CLOSED",
    "AWARD_OBSERVED",
    "POST_AWARD",
}
PROCUREMENT_MODES = {
    "DISCOVERY",
    "LIVE_PROCUREMENT",
    "POST_DEADLINE_REVALIDATION",
}
SPECIALISTS = {
    "argus-opportunity-intelligence",
    "argus-ecosystem-intelligence",
    "argus-procurement-market-intelligence",
    "argus-monitoring-revalidation",
}


class ModularSkillRoutingTests(unittest.TestCase):
    def test_routing_contract_and_schema_exist(self) -> None:
        self.assertTrue(ROUTING.is_file())
        self.assertTrue(SCHEMA.is_file())

    def test_schema_governs_mission_states_procurement_modes_and_specialists(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        plan = schema["properties"]["mission_skill_plan"]
        props = plan["properties"]
        self.assertEqual(MISSION_STATES, set(props["mission_state"]["enum"]))
        self.assertEqual(
            PROCUREMENT_MODES,
            set(props["procurement_mode"]["enum"]),
        )
        specialist_enum = props["specialists"]["items"]["properties"]["skill"]["enum"]
        self.assertEqual(SPECIALISTS, set(specialist_enum))
        self.assertEqual(
            {"REQUIRED", "CONDITIONAL", "SKIP"},
            set(props["specialists"]["items"]["properties"]["activation"]["enum"]),
        )

    def test_routing_contract_keeps_stale_revalidation_orthogonal(self) -> None:
        text = ROUTING.read_text(encoding="utf-8")
        self.assertIn("stale_revalidation_required", text)
        self.assertIn("orthogonal_to_mission_state: true", text)
        self.assertIn("secondary_source_cannot_promote_canonical_lifecycle: true", text)

    def test_contract_preserves_atlas_authority_and_canonical_identity(self) -> None:
        text = ROUTING.read_text(encoding="utf-8")
        self.assertIn("next_step_authority: ATLAS", text)
        self.assertIn("specialists_are_not_control_planes: true", text)
        self.assertIn("preserve_canonical_ids_across_specialists: true", text)
        self.assertIn("specialist_may_create_competing_canonical_identity: false", text)

    def test_three_pilot_profiles_encode_distinct_maturity_paths(self) -> None:
        text = ROUTING.read_text(encoding="utf-8")
        self.assertIn("COASTAL_PATROL_VESSEL_BCG", text)
        self.assertIn("mission_state: PROCUREMENT_LIVE", text)
        self.assertIn("procurement_mode: LIVE_PROCUREMENT", text)

        self.assertIn("COASTAL_SURVEILLANCE_RADAR_BN", text)
        self.assertIn("mission_state: SEED", text)
        self.assertIn("live_procurement_requires_authoritative_evidence: true", text)

        self.assertIn("SEED_CLEANER_CUM_GRADER_BADC", text)
        self.assertIn("stale_revalidation_required: true", text)
        self.assertIn("secondary_source_cannot_promote_canonical_lifecycle: true", text)

    def test_manifest_points_to_modular_routing_authority(self) -> None:
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("mission_skill_routing: spec/mission-skill-routing.yaml", text)
        self.assertIn("mission_skill_plan_schema: schemas/mission-skill-plan.schema.json", text)


if __name__ == "__main__":
    unittest.main()
