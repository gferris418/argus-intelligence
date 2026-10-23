from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


class ProcurementPackageForecastingTests(unittest.TestCase):
    def test_forecasting_contract_is_wired_into_argus(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        core = yaml.safe_load((ROOT / "spec" / "general-intelligence.yaml").read_text(encoding="utf-8"))

        self.assertEqual(
            "profiles/procurement-package-forecasting-v1.0.yaml",
            manifest["authority"]["procurement_package_forecasting"],
        )
        self.assertEqual(
            "schemas/procurement-package-forecast.schema.json",
            manifest["authority"]["procurement_package_forecast_schema"],
        )
        self.assertIn("procurement_package_forecasting", manifest["scope"]["specializations"])
        self.assertEqual("active", manifest["engines"]["procurement_package_forecasting"]["status"])
        self.assertIn("PROCUREMENT_PACKAGE_FORECAST", core["collection_types"])
        self.assertIn("procurement_package_hypothesis_generation", core["ownership"]["argus"])
        self.assertIn("forecasting_and_scenarios", core["ownership"]["atlas"])

    def test_method_decomposes_project_without_fabricating_procurement(self) -> None:
        method = yaml.safe_load(
            (ROOT / "profiles" / "procurement-package-forecasting-v1.0.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual("PROCUREMENT_PACKAGE_FORECASTING", method["capability"])
        self.assertFalse(method["governance"]["approved_project_proves_package_exists"])
        self.assertFalse(method["governance"]["forecast_is_canonical_procurement_fact"])
        self.assertEqual("ATLAS", method["governance"]["final_forecast_authority"])
        self.assertEqual("ARGUS", method["governance"]["package_hypothesis_authority"])
        self.assertEqual(
            [
                "ESTABLISH_PROJECT_BASELINE",
                "DECOMPOSE_DELIVERY_MODEL",
                "GENERATE_PACKAGE_HYPOTHESES",
                "ESTIMATE_SEQUENCE_AND_TIMING",
                "TEST_PROCUREMENT_ROUTE",
                "CORROBORATE_AND_FALSIFY",
                "SCORE_AND_PRIORITIZE",
                "MONITOR_SIGNPOSTS",
                "RECONCILE_OBSERVED_PACKAGE",
            ],
            method["workflow"],
        )
        self.assertIn("project_scope_outputs", method["decomposition_lenses"])
        self.assertIn("funding_and_cost_structure", method["decomposition_lenses"])
        self.assertIn("historical_analogues", method["decomposition_lenses"])
        self.assertIn("institutional_procurement_pattern", method["decomposition_lenses"])
        self.assertIn("technical_dependencies", method["decomposition_lenses"])
        self.assertIn("local_foreign_delivery_split", method["decomposition_lenses"])
        self.assertIn("works_goods_services_consulting_split", method["decomposition_lenses"])
        self.assertIn("source_lineage_independence", method["verification_rules"])
        self.assertIn("contradiction_search", method["verification_rules"])
        self.assertIn("falsifier_required", method["verification_rules"])
        self.assertEqual(
            "PROCUREMENT_PACKAGE",
            method["promotion"]["observed_target_object_type"],
        )
        self.assertTrue(method["promotion"]["authoritative_package_evidence_required"])

    def test_forecast_schema_accepts_evidence_bounded_package_hypotheses(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "procurement-package-forecast.schema.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator.check_schema(schema)

        payload = {
            "forecast_id": "PPF-BD-2026-000001",
            "project_ref": "PRJ-BD-000123",
            "requirement_refs": ["REQ-BD-000456"],
            "forecast_state": "ACTIVE_HYPOTHESIS",
            "as_of": "2026-10-23T00:00:00Z",
            "basis": {
                "project_state": "APPROVED",
                "project_evidence_refs": ["SRC-001"],
                "approved_project_proves_package_exists": False,
            },
            "package_hypotheses": [
                {
                    "hypothesis_id": "PKGH-BD-2026-000001",
                    "title": "Marine communications and navigation systems package",
                    "package_class": "GOODS_WITH_RELATED_SERVICES",
                    "scope_summary": "Potential supply, integration, commissioning and training package.",
                    "claim_type": "INFERENCE",
                    "status": "HYPOTHESIZED",
                    "realization_probability": 0.68,
                    "evidence_confidence": 0.74,
                    "timing_window": {
                        "earliest": "2027-01-01",
                        "latest": "2027-09-30",
                        "precision": "QUARTER_RANGE",
                    },
                    "procurement_route_hypotheses": [
                        {
                            "route": "OPEN_TENDERING",
                            "probability": 0.55,
                            "basis_refs": ["SRC-002"],
                        }
                    ],
                    "supporting_evidence_refs": ["SRC-001", "SRC-002"],
                    "contradicting_evidence_refs": [],
                    "assumptions": ["Project scope remains materially unchanged."],
                    "falsifiers": ["Approved procurement plan combines the scope into a different package."],
                    "signposts": ["APP publication", "DPP/RDPP procurement annex update"],
                    "supplier_implications": {
                        "international_oem_likely": True,
                        "local_partner_likely": True,
                    },
                }
            ],
            "coverage": {
                "expected_package_count_range": {"minimum": 1, "maximum": 5},
                "unallocated_scope": ["Civil enabling works not yet decomposed."],
            },
            "monitoring": {
                "next_questions": ["Has the project procurement plan been approved?"],
                "next_triggers": ["APP or development-partner procurement plan publication"],
            },
            "governance": {
                "final_forecast_authority": "ATLAS",
                "canonical_procurement_fact": False,
            },
        }

        jsonschema.validate(payload, schema)

    def test_schema_prevents_hypothesis_from_claiming_observed_package(self) -> None:
        schema = json.loads(
            (ROOT / "schemas" / "procurement-package-forecast.schema.json").read_text(encoding="utf-8")
        )
        invalid_payload = {
            "forecast_id": "PPF-BD-2026-000001",
            "project_ref": "PRJ-BD-000123",
            "requirement_refs": [],
            "forecast_state": "ACTIVE_HYPOTHESIS",
            "as_of": "2026-10-23T00:00:00Z",
            "basis": {
                "project_state": "APPROVED",
                "project_evidence_refs": ["SRC-001"],
                "approved_project_proves_package_exists": False,
            },
            "package_hypotheses": [
                {
                    "hypothesis_id": "PKGH-BD-2026-000001",
                    "title": "Unverified package",
                    "package_class": "GOODS",
                    "scope_summary": "Hypothesis only.",
                    "claim_type": "FACT",
                    "status": "OBSERVED",
                    "realization_probability": 1.0,
                    "evidence_confidence": 1.0,
                    "timing_window": {"precision": "UNKNOWN"},
                    "procurement_route_hypotheses": [],
                    "supporting_evidence_refs": ["SRC-001"],
                    "contradicting_evidence_refs": [],
                    "assumptions": [],
                    "falsifiers": ["Any authoritative source contradicts package existence."],
                    "signposts": [],
                    "supplier_implications": {
                        "international_oem_likely": False,
                        "local_partner_likely": False,
                    },
                }
            ],
            "coverage": {
                "expected_package_count_range": {"minimum": 1, "maximum": 1},
                "unallocated_scope": [],
            },
            "monitoring": {"next_questions": [], "next_triggers": []},
            "governance": {"final_forecast_authority": "ATLAS", "canonical_procurement_fact": False},
        }

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid_payload, schema)


if __name__ == "__main__":
    unittest.main()
