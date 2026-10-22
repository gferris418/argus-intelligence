from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDICATORS = ROOT / "profiles/bangladesh-indicators-signposts.yaml"
SOURCES = ROOT / "profiles/bangladesh-upstream-source-families.yaml"


class BangladeshIndicatorsSignpostsTests(unittest.TestCase):
    def test_upstream_events_are_defined(self):
        text = INDICATORS.read_text(encoding="utf-8")
        for event in (
            "POLICY_ADOPTED", "POLICY_REVISED", "REQUIREMENT_IDENTIFIED", "PROJECT_CONCEPT_IDENTIFIED",
            "PROJECT_SUBMITTED", "PROJECT_APPRAISAL", "PROJECT_APPROVED", "PROJECT_REVISED",
            "ADP_INCLUDED", "RADP_CHANGED", "ALLOCATION_INCREASED", "ALLOCATION_REDUCED",
            "FINANCING_PROPOSED", "FINANCING_SIGNED", "CONSULTANT_APPOINTED",
            "PROCUREMENT_STRATEGY_SIGNAL", "APP_CREATED", "PACKAGE_CREATED",
        ):
            self.assertIn(f"  {event}:", text)

    def test_events_do_not_force_state_progression(self):
        text = INDICATORS.read_text(encoding="utf-8")
        self.assertIn("event_detection_forces_progression: false", text)
        self.assertIn("reassessment_required_when_material: true", text)

    def test_competing_hypotheses_and_research_frontier_are_machine_readable(self):
        text = INDICATORS.read_text(encoding="utf-8")
        for field in (
            "preferred_hypothesis", "material_alternatives", "disconfirming_evidence", "key_assumptions",
            "question", "who_or_what_is_unresolved", "decision_affected", "information_value",
            "urgency", "stopping_condition", "priority",
        ):
            self.assertIn(field, text)

    def test_missing_upstream_source_families_are_added_without_bulk_import(self):
        text = SOURCES.read_text(encoding="utf-8")
        for family in (
            "CABINET_ALLOCATION_OF_BUSINESS", "NATIONAL_GOVERNMENT_DIRECTORY", "MINISTRY_POLICY_STRATEGY",
            "PROJECT_PROCESSING", "BUDGET_FINANCE_DOCUMENT", "PUBLIC_INVESTMENT_PROGRAMMING",
            "AGENCY_ANNUAL_REPORT", "GOVERNMENT_GAZETTE",
        ):
            self.assertIn(f"  {family}:", text)
        self.assertIn("bulk_import_government_entities: false", text)
        self.assertIn("opportunity_driven_lazy_enrichment: true", text)


if __name__ == "__main__":
    unittest.main()
