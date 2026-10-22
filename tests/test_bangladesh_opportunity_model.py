from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "profiles/bangladesh-opportunity-model.yaml"


class BangladeshOpportunityModelTests(unittest.TestCase):
    def test_s0_s9_is_primary_and_i0_i9_is_compatibility_only(self):
        text = MODEL.read_text(encoding="utf-8")
        self.assertIn("primary_lifecycle: S0_S9", text)
        self.assertIn("legacy_maturity: I0_I9_COMPATIBILITY_ONLY", text)
        self.assertIn("compatibility_maturity_must_not_drive_lifecycle: true", text)

    def test_parallel_state_axes_exist(self):
        text = MODEL.read_text(encoding="utf-8")
        for axis in (
            "need_state", "institution_state", "project_state", "funding_state",
            "procurement_state", "commercial_state",
        ):
            self.assertIn(f"  {axis}:", text)

    def test_requirement_lineage_preserves_identity_across_procurement_events(self):
        text = MODEL.read_text(encoding="utf-8")
        self.assertIn("stable_key: requirement_ref", text)
        self.assertIn("tender_amendment_creates_new_opportunity: false", text)
        self.assertIn("retender_creates_new_requirement_automatically: false", text)
        self.assertIn("project_revision_creates_new_requirement_automatically: false", text)
        self.assertIn("same_equipment_family_proves_same_requirement: false", text)
        self.assertIn("successor_requires_distinct_lifecycle_evidence: true", text)

    def test_event_observation_does_not_force_progression(self):
        text = MODEL.read_text(encoding="utf-8")
        self.assertIn("event_detection_forces_state_progression: false", text)
        self.assertIn("evidence_required_for_progression: true", text)


if __name__ == "__main__":
    unittest.main()
