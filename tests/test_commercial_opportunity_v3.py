from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _load_engine():
    path = ROOT / "tools" / "opportunity_engine.py"
    spec = importlib.util.spec_from_file_location("opportunity_engine", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load opportunity_engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommercialOpportunityV3Tests(unittest.TestCase):
    def test_manifest_declares_v3_government_commercial_opportunity_mission(self) -> None:
        text = (ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8")
        self.assertIn("version: 3.0.0-rc.1", text)
        self.assertIn("government commercial opportunity intelligence", text.lower())
        self.assertIn("demand_intelligence", text)
        self.assertIn("supply_intelligence", text)
        self.assertIn("opportunity_engine", text)
        self.assertIn("matching_and_qualification", text)
        self.assertIn("early_warning", text)

    def test_opportunity_is_first_class_before_px_promotion(self) -> None:
        schema = _load_json("schemas/opportunity.schema.json")
        props = schema["properties"]
        self.assertIn("argus_opportunity_id", schema["required"])
        self.assertIn("commercial_id", props)
        self.assertEqual(["string", "null"], props["commercial_id"]["type"])
        self.assertEqual("^ARGUS-OPP-[0-9]{4}-[0-9]{6}$", props["argus_opportunity_id"]["pattern"])
        self.assertEqual("^[0-9]{4}_PX[0-9]{5}_[A-Z0-9][A-Z0-9-]{1,31}$", props["commercial_id"]["pattern"])

    def test_opportunity_separates_stage_mode_and_probabilities(self) -> None:
        schema = _load_json("schemas/opportunity.schema.json")
        props = schema["properties"]
        self.assertEqual([f"S{i}" for i in range(10)], props["lifecycle_stage"]["enum"])
        self.assertEqual(["SHAPE", "POSITION", "REACT", "EXPAND"], props["opportunity_mode"]["enum"])
        measures = props["measures"]["properties"]
        for name in (
            "evidence_confidence",
            "procurement_realization_probability",
            "access_asia_success_probability",
            "supplier_match_confidence",
        ):
            self.assertIn(name, measures)

    def test_supplier_intelligence_exposes_partnerability_without_crm_relationship_duplication(self) -> None:
        schema = _load_json("schemas/supplier-intelligence.schema.json")
        self.assertIn("crm_ref", schema["properties"])
        partnerability = schema["properties"]["partnerability"]["properties"]
        for field in (
            "existing_bangladesh_partner",
            "exclusivity_status",
            "channel_model",
            "willingness_to_partner",
            "local_support_requirement",
            "conflict_status",
            "commercial_fit",
        ):
            self.assertIn(field, partnerability)
        self.assertNotIn("access_asia_relationship", partnerability)
        self.assertNotIn("contactability", partnerability)

    def test_opportunity_events_cover_early_warning_and_follow_on(self) -> None:
        schema = _load_json("schemas/opportunity-event.schema.json")
        event_types = set(schema["properties"]["event_type"]["enum"])
        required = {
            "POLICY_SIGNAL",
            "CAPABILITY_GAP",
            "FEASIBILITY_STUDY",
            "DPP_TAPP_PREPARATION",
            "BUDGET_ALLOCATION",
            "PROJECT_APPROVAL",
            "APP_INCLUSION",
            "MARKET_CONSULTATION",
            "RFI",
            "EOI",
            "PREQUALIFICATION",
            "TENDER_PUBLICATION",
            "CANCELLATION",
            "REBID",
            "AWARD",
            "DELIVERY",
            "FOLLOW_ON",
            "UPGRADE",
            "REPLACEMENT",
        }
        self.assertTrue(required <= event_types)

    def test_matching_schema_uses_configurable_weight_profile(self) -> None:
        schema = _load_json("schemas/opportunity-supplier-match.schema.json")
        weights = schema["properties"]["weights"]["properties"]
        self.assertEqual(
            {
                "technical_fit",
                "relevant_references",
                "tender_eligibility",
                "export_feasibility",
                "price_competitiveness",
                "bangladesh_fit",
                "local_support_capability",
                "willingness_to_partner",
                "relationship_access",
            },
            set(weights),
        )

    def test_default_opportunity_qualification_scoring(self) -> None:
        engine = _load_engine()
        result = engine.score_opportunity(
            {
                "strategic_fit": 90,
                "commercial_attractiveness": 80,
                "procurement_probability": 70,
                "supplier_availability": 80,
                "access_advantage": 70,
                "competitive_difficulty": 60,
            }
        )
        self.assertEqual(76.5, result["score"])
        self.assertEqual("ACTIVE", result["recommended_priority_band"])

    def test_supplier_match_scoring_defaults_to_recommended_weights(self) -> None:
        engine = _load_engine()
        result = engine.score_supplier_match(
            {
                "technical_fit": 100,
                "relevant_references": 100,
                "tender_eligibility": 100,
                "export_feasibility": 100,
                "price_competitiveness": 100,
                "bangladesh_fit": 100,
                "local_support_capability": 100,
                "willingness_to_partner": 100,
                "relationship_access": 100,
            }
        )
        self.assertEqual(100.0, result["score"])
        self.assertEqual(1.0, result["confidence"])

    def test_detection_lag_is_measured_from_earliest_observable_event(self) -> None:
        engine = _load_engine()
        earliest = datetime(2026, 10, 20, 0, 0, tzinfo=timezone.utc)
        detected = datetime(2026, 10, 21, 6, 0, tzinfo=timezone.utc)
        self.assertEqual(30.0, engine.detection_lag_hours(earliest, detected))
        with self.assertRaises(ValueError):
            engine.detection_lag_hours(detected, earliest)

    def test_rapid_tender_mode_has_minimum_first_pass_fields(self) -> None:
        spec = (ROOT / "spec" / "commercial-opportunity-intelligence.yaml").read_text(encoding="utf-8")
        for field in (
            "closing_date",
            "procurement_method",
            "eligibility",
            "experience_requirements",
            "financial_requirements",
            "technical_requirements",
            "oem_restrictions",
            "country_restrictions",
            "local_agent_requirements",
            "bid_security",
            "performance_guarantee",
            "delivery",
            "incoterms",
            "evaluation_methodology",
            "critical_disqualifiers",
        ):
            self.assertIn(field, spec)

    def test_collection_types_cover_demand_supply_and_commercial_opportunity(self) -> None:
        schema = _load_json("schemas/collection-mission.schema.json")
        values = set(schema["properties"]["collection_types"]["items"]["enum"])
        required = {
            "NEED_GAP",
            "POLICY_DRIVER",
            "PROGRAMME_PROJECT",
            "APPROVAL_STATUS",
            "SUPPLIER_PROFILE",
            "REFERENCE_PROJECT",
            "EXPORT_FEASIBILITY",
            "PARTNERABILITY",
            "OPPORTUNITY_DEVELOPMENT",
            "OPPORTUNITY_MATCHING",
            "EXPANSION_DISCOVERY",
            "RAPID_TENDER",
        }
        self.assertTrue(required <= values)

    def test_access_asia_lifecycle_preserves_argus_identity_before_px(self) -> None:
        text = (ROOT / "profiles" / "access-asia-opportunity-lifecycle.yaml").read_text(encoding="utf-8")
        self.assertIn("argus_opportunity_identity", text)
        self.assertIn("created_before_px: true", text)
        self.assertIn("px_identity_requires_atlas_promotion: true", text)
        self.assertIn("preserve_argus_identity_after_px: true", text)


if __name__ == "__main__":
    unittest.main()
