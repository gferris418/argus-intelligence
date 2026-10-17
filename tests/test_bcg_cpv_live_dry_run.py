import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = json.loads((ROOT / "tests" / "scenarios" / "bd-bcg-cpv-live-2026.json").read_text())
STANDARD = (ROOT / "profiles" / "bangladesh-data-standard.yaml").read_text()


class BCGCPVLiveDryRun(unittest.TestCase):
    def test_atlas_classification_precedes_argus_contextualization(self):
        stages = SCENARIO["process_flow"]
        self.assertLess(stages.index("ATLAS_DOMAIN_CLASSIFICATION"), stages.index("ATLAS_DOMAIN_HANDOFF"))
        self.assertLess(stages.index("ATLAS_DOMAIN_HANDOFF"), stages.index("ARGUS_CONTEXTUALIZE"))
        self.assertLess(stages.index("ARGUS_CONTEXTUALIZE"), stages.index("ARGUS_NORMALIZE_OBSERVATIONS"))

    def test_domain_context_has_governed_product_industry_taxonomy(self):
        ctx = SCENARIO["atlas_domain_context"]
        self.assertEqual(ctx["jurisdiction"], "Bangladesh")
        self.assertEqual(ctx["supplier_industry"]["isic_code"], "3011")
        self.assertEqual(ctx["product_classification"]["cpc_code"], "49319")
        self.assertIn("890690", ctx["product_classification"]["hs_candidates"])
        self.assertIn("890610", ctx["product_classification"]["hs_candidates"])
        self.assertIn("hs_subheading", ctx["unresolved_material"])

    def test_bangladesh_normalization_preserves_typed_identifiers(self):
        canonical = SCENARIO["normalized_state"]
        self.assertEqual(canonical["project.code"], "224392800")
        self.assertEqual(canonical["institution.pe_code"], "224392800")
        self.assertEqual(canonical["procurement.lot_no"], "1")
        self.assertEqual(canonical["procurement.lot_identification"], "WD-2")
        self.assertEqual(canonical["solicitation.reference_no"], "44.08.2680.033.02.106.26.160")
        self.assertNotIn("procurement.package_no", canonical)
        self.assertNotEqual(canonical["procurement.lot_identification"], canonical["solicitation.reference_no"])

    def test_standard_models_lot_number_and_identification_separately(self):
        self.assertIn("procurement.lot_no:", STANDARD)
        self.assertIn("procurement.lot_identification:", STANDARD)
        obs = SCENARIO["source_observations"]["bppa_solicitation"]
        lot_no = next(x for x in obs["data_points"] if x["field_id"] == "procurement.lot_no")
        lot_id = next(x for x in obs["data_points"] if x["field_id"] == "procurement.lot_identification")
        self.assertEqual(lot_no["raw_label"], "Lot No")
        self.assertEqual(lot_id["raw_label"], "Identification")
        self.assertEqual(lot_no["value"], "1")
        self.assertEqual(lot_id["value"], "WD-2")

    def test_current_official_evidence_updates_stale_registry_state_without_duplicate(self):
        result = SCENARIO["reconciliation_result"]
        self.assertEqual(result["project_match"], "PRJ-BCG-CPV-WD2")
        self.assertEqual(result["procurement_match"], "PROC-BCG-LT001")
        self.assertEqual(result["decision"], "MATCHED_EXISTING")
        self.assertFalse(result["create_new_opportunity"])
        self.assertTrue(result["refresh_stale_procurement_state"])

    def test_live_state_is_time_qualified(self):
        assessment = SCENARIO["assessment"]
        self.assertEqual(assessment["maturity"], "I9")
        self.assertEqual(assessment["procurement_state"], "OPEN")
        self.assertEqual(assessment["as_of"], "2026-10-18")
        self.assertEqual(assessment["closing_at"], "2026-10-25T12:00:00+06:00")

    def test_project_funding_route_and_procurement_method_remain_separate(self):
        state = SCENARIO["normalized_state"]
        self.assertEqual(state["bangladesh.route"], "BD-DEV-GOB")
        self.assertEqual(state["funding.budget_type"], "Development Budget")
        self.assertEqual(state["funding.source"], "GOB")
        self.assertEqual(state["procurement.method"], "ICT One Stage & Two envelope Tendering Method")

    def test_source_documents_are_not_stored(self):
        persistence = SCENARIO["persistence"]
        self.assertFalse(persistence["raw_tender_documents_in_github"])
        self.assertTrue(persistence["structured_observations_only"])
        self.assertTrue(persistence["source_locators_preserved"])

    def test_research_frontier_is_decision_driven(self):
        frontier = SCENARIO["research_frontier"]
        self.assertEqual(frontier["priority"], 1)
        self.assertIn("commercially viable participation path", frontier["question"])
        self.assertIn("2026-10-25", frontier["decision_hinge"])


if __name__ == "__main__":
    unittest.main()
