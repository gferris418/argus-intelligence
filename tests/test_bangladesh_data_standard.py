import json
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
STANDARD_PATH = ROOT / "profiles" / "bangladesh-data-standard.yaml"
MAPPINGS_PATH = ROOT / "profiles" / "bangladesh-source-mappings.yaml"
OBS_SCHEMA_PATH = ROOT / "schemas" / "bangladesh-observation.schema.json"
PROFILE = (ROOT / "profiles" / "bangladesh.md").read_text()


class BangladeshDataStandardTests(unittest.TestCase):
    def setUp(self):
        self.standard = yaml.safe_load(STANDARD_PATH.read_text())
        self.mappings = yaml.safe_load(MAPPINGS_PATH.read_text())
        self.schema = json.loads(OBS_SCHEMA_PATH.read_text())

    def test_policy_to_installed_base_layers_are_standardized(self):
        layers = set(self.standard["canonical_layers"])
        required = {
            "POLICY_STRATEGY",
            "INSTITUTION",
            "PROGRAMME_PROJECT",
            "FUNDING",
            "PROCUREMENT_PLAN",
            "PROCUREMENT_PACKAGE",
            "SOLICITATION",
            "AMENDMENT_PREBID",
            "AWARD_CONTRACT",
            "CONTRACT_EXECUTION",
            "INSTALLED_BASE",
            "SUPPLIER_MARKET",
            "INTERNAL_INTELLIGENCE",
        }
        self.assertTrue(required.issubset(layers))

    def test_core_identifiers_and_procurement_fields_exist_once(self):
        fields = self.standard["canonical_fields"]
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
        self.assertTrue(required.issubset(fields))
        self.assertEqual("BD", self.standard["defaults"]["country_code"])

    def test_route_funding_budget_and_procurement_method_are_separate_concepts(self):
        fields = self.standard["canonical_fields"]
        for field_id in (
            "bangladesh.route",
            "funding.budget_type",
            "funding.source",
            "procurement.method",
            "procurement.type",
        ):
            self.assertIn(field_id, fields)
        meanings = {fields[field_id]["meaning"] for field_id in (
            "bangladesh.route",
            "funding.budget_type",
            "funding.source",
            "procurement.method",
            "procurement.type",
        )}
        self.assertEqual(5, len(meanings))

    def test_required_source_families_are_mapped_to_only_known_fields(self):
        required_sources = {
            "BPPA_EGP_APP",
            "BPPA_EGP_SOLICITATION",
            "BPPA_EGP_AWARD",
            "BPPA_ECMS",
            "IMED_ADP",
            "PLANNING_DPP_TAPP",
            "ERD_AIMS",
            "PPP_AUTHORITY",
            "DGDP_EDP",
            "AGENCY_WEBSITE",
            "INTERNAL_EMAIL",
            "INTERNAL_DOCUMENT",
            "MEETING_NOTE",
        }
        profiles = self.mappings["source_profiles"]
        self.assertTrue(required_sources.issubset(profiles))
        known = set(self.standard["canonical_fields"])
        for source_id, profile in profiles.items():
            for mapping in profile.get("field_mappings", []):
                self.assertIn(mapping["canonical_field"], known, f"{source_id}: {mapping}")

    def test_observation_schema_accepts_sparse_source_specific_data_without_inventing_nulls(self):
        observation = {
            "observation_id": "BDOBS-EGP-1323636",
            "source_family": "BPPA_EGP_SOLICITATION",
            "canonical_layers": ["SOLICITATION", "PROCUREMENT_PACKAGE", "INSTITUTION", "FUNDING"],
            "source": {
                "source_system": "e-GP",
                "source_id": "1323636",
                "source_locator": "https://www.eprocure.gov.bd/resources/common/ViewTender.jsp?id=1323636",
                "observed_at": "2026-10-18T03:30:00+06:00"
            },
            "data_points": [
                {"field_id": "institution.organization_name", "value": "Directorate General of Drug Administration", "raw_label": "Organization", "claim_type": "FACT", "claim_condition": "CURRENT"},
                {"field_id": "procurement.package_no", "value": "DGDA/APP/2026-2027/GR-09", "raw_label": "Tender/Proposal Package No.", "claim_type": "FACT", "claim_condition": "CURRENT"},
                {"field_id": "solicitation.id", "value": "1323636", "raw_label": "Tender/Proposal ID", "claim_type": "FACT", "claim_condition": "CURRENT"}
            ]
        }
        jsonschema.validate(observation, self.schema, format_checker=jsonschema.FormatChecker())
        self.assertNotIn("project.code", {item["field_id"] for item in observation["data_points"]})

    def test_profile_declares_standardization_before_route_and_research(self):
        self.assertIn("Bangladesh Data Standard", PROFILE)
        self.assertIn("normalize available source data", PROFILE)
        self.assertIn("source-specific labels must map to canonical fields", PROFILE)

    def test_standard_declares_multiple_identification_approaches(self):
        approaches = set(self.standard["identification_and_normalization_approaches"])
        required = {
            "SOURCE_TEMPLATE",
            "IDENTIFIER_FIRST",
            "HIERARCHY_FIRST",
            "ATLAS_DOMAIN_CONTEXT",
            "TEMPORAL_EVENT",
            "SEMANTIC_ALIAS",
            "CROSS_SOURCE_CONVERGENCE",
            "POLICY_DOWNSTREAM",
            "PROCUREMENT_BACKWARD",
            "INTERNAL_FIRST",
        }
        self.assertTrue(required.issubset(approaches))


if __name__ == "__main__":
    unittest.main()
