import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARD_TEXT = (ROOT / "profiles" / "bangladesh-data-standard.yaml").read_text()
MAPPINGS_TEXT = (ROOT / "profiles" / "bangladesh-source-mappings.yaml").read_text()
OBS_SCHEMA = json.loads((ROOT / "schemas" / "bangladesh-observation.schema.json").read_text())
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()

FIELD_RE = re.compile(r"^  ([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+):\s*$", re.MULTILINE)
MAPPING_RE = re.compile(r"canonical_field:\s*([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)")


class BangladeshDataStandardTests(unittest.TestCase):
    def test_policy_to_installed_base_layers_are_standardized(self):
        for layer in (
            "POLICY_STRATEGY", "INSTITUTION", "PROGRAMME_PROJECT", "FUNDING",
            "PROCUREMENT_PLAN", "PROCUREMENT_PACKAGE", "SOLICITATION",
            "AMENDMENT_PREBID", "AWARD_CONTRACT", "CONTRACT_EXECUTION",
            "INSTALLED_BASE", "SUPPLIER_MARKET", "INTERNAL_INTELLIGENCE",
        ):
            self.assertIn(f"  - {layer}", STANDARD_TEXT)

    def test_core_identifiers_and_procurement_fields_exist_once(self):
        fields = set(FIELD_RE.findall(STANDARD_TEXT))
        required = {
            "institution.ministry_name",
            "institution.division_name",
            "institution.organization_name",
            "institution.pe_name",
            "institution.pe_code",
            "project.code",
            "project.name",
            "project.total_cost",
            "funding.budget_type",
            "funding.source",
            "funding.development_partner",
            "procurement.app_id",
            "procurement.financial_year",
            "procurement.package_no",
            "procurement.nature",
            "procurement.method",
            "solicitation.id",
            "solicitation.reference_no",
            "solicitation.publication_at",
            "solicitation.closing_at",
            "award.noa_date",
            "award.supplier_name",
            "award.value",
            "contract.start_date",
            "contract.end_date",
            "installed_base.asset_name",
        }
        self.assertTrue(required.issubset(fields), sorted(required - fields))
        self.assertIn("country_code: BD", STANDARD_TEXT)

    def test_route_funding_budget_and_procurement_method_are_separate_concepts(self):
        fields = set(FIELD_RE.findall(STANDARD_TEXT))
        for field_id in (
            "bangladesh.route",
            "funding.budget_type",
            "funding.source",
            "procurement.method",
            "procurement.type",
        ):
            self.assertIn(field_id, fields)
        self.assertIn("Bangladesh route, budget type, source of funds, procurement nature, procurement type and procurement method are independent concepts.", STANDARD_TEXT)

    def test_required_source_families_are_mapped_to_only_known_fields(self):
        required_sources = {
            "BPPA_EGP_APP", "BPPA_EGP_SOLICITATION", "BPPA_EGP_AWARD",
            "BPPA_ECMS", "IMED_ADP", "PLANNING_DPP_TAPP", "ERD_AIMS",
            "PPP_AUTHORITY", "DGDP_EDP", "AGENCY_WEBSITE", "INTERNAL_EMAIL",
            "INTERNAL_DOCUMENT", "MEETING_NOTE",
        }
        for source_id in required_sources:
            self.assertIn(f"  {source_id}:", MAPPINGS_TEXT)
        known = set(FIELD_RE.findall(STANDARD_TEXT))
        mapped = set(MAPPING_RE.findall(MAPPINGS_TEXT))
        self.assertTrue(mapped.issubset(known), sorted(mapped - known))

    def test_observation_schema_is_sparse_and_does_not_require_every_canonical_field(self):
        required = set(OBS_SCHEMA["required"])
        self.assertEqual({"observation_id", "source_family", "canonical_layers", "source", "data_points"}, required)
        point = OBS_SCHEMA["properties"]["data_points"]["items"]
        self.assertEqual({"field_id", "raw_label", "claim_type", "claim_condition"}, set(point["required"]))
        self.assertIn("BPPA_EGP_SOLICITATION", OBS_SCHEMA["properties"]["source_family"]["enum"])
        self.assertNotIn("project.code", required)

    def test_manifest_wires_the_bangladesh_standard_and_source_mappings(self):
        self.assertIn("bangladesh_data_standard: profiles/bangladesh-data-standard.yaml", MANIFEST)
        self.assertIn("bangladesh_source_mappings: profiles/bangladesh-source-mappings.yaml", MANIFEST)
        self.assertIn("bangladesh_observation_schema: schemas/bangladesh-observation.schema.json", MANIFEST)

    def test_standard_declares_multiple_identification_approaches(self):
        for approach in (
            "SOURCE_TEMPLATE", "IDENTIFIER_FIRST", "HIERARCHY_FIRST",
            "ATLAS_DOMAIN_CONTEXT", "TEMPORAL_EVENT", "SEMANTIC_ALIAS",
            "CROSS_SOURCE_CONVERGENCE", "POLICY_DOWNSTREAM",
            "PROCUREMENT_BACKWARD", "INTERNAL_FIRST",
        ):
            self.assertIn(f"  - {approach}", STANDARD_TEXT)


if __name__ == "__main__":
    unittest.main()
