import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_STANDARD = (ROOT / "profiles" / "bangladesh-data-standard.yaml").read_text()
STANDARD = (ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v1.1.yaml").read_text()
MAPPINGS = (ROOT / "profiles" / "bangladesh-source-mappings-v1.1.yaml").read_text()
SCHEMA = json.loads((ROOT / "schemas" / "bangladesh-observation-v1.1.schema.json").read_text())
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()

FIELD_RE = re.compile(r"^  ([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+):\s*$", re.MULTILINE)
MAPPING_RE = re.compile(r"canonical_field:\s*([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)")
INLINE_TARGET_RE = re.compile(r"(?:amount|currency|reference|description|date_time|place):\s*([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+)")


class BangladeshExtendedProcurementStandard(unittest.TestCase):
    def test_standard_is_v110_and_adds_preprocurement_layer(self):
        self.assertIn("version: 1.1.0", STANDARD)
        self.assertIn("  - PRE_PROCUREMENT", STANDARD)
        layers = SCHEMA["properties"]["canonical_layers"]["items"]["enum"]
        self.assertIn("PRE_PROCUREMENT", layers)

    def test_extended_common_fields_exist(self):
        fields = set(FIELD_RE.findall(STANDARD))
        required = {
            "project.external_ids", "project.component", "funding.financing_references",
            "funding.procurement_conditions", "procurement.activity_reference_no",
            "procurement.review_type", "procurement.market_approach", "procurement.process",
            "procurement.prequalification_required", "procurement.status_raw",
            "procurement.status_normalized", "procurement.plan_date",
            "procurement.expected_advertisement_date", "procurement.actual_amount",
            "procurement.actual_currency", "procurement.lots", "procurement.milestones",
            "preproc.event_type", "preproc.reference_no", "preproc.title",
            "preproc.wing_or_unit", "preproc.publication_at", "preproc.deadline_at",
            "preproc.status", "solicitation.notice_type", "solicitation.document_price_text",
            "solicitation.prebid_at", "solicitation.prebid_location",
            "solicitation.submission_channel", "solicitation.submission_locator",
            "solicitation.registration_requirement", "solicitation.source_country_eligibility",
            "solicitation.local_participation_requirement", "solicitation.sustainability_requirements",
            "solicitation.contact_name", "solicitation.contact_designation",
            "solicitation.contact_address", "solicitation.contact_phone",
            "solicitation.contact_email", "award.approval_reference", "award.supplier_address",
            "award.financier_financed_amount", "award.financier_financed_currency",
        }
        self.assertTrue(required.issubset(fields), sorted(required - fields))

    def test_multi_lot_and_milestone_rules_prevent_flattening(self):
        self.assertIn("multi-lot", STANDARD.lower())
        self.assertIn("procurement.lots", STANDARD)
        self.assertIn("procurement.milestones", STANDARD)
        self.assertIn("must not be collapsed", STANDARD)

    def test_domestic_and_development_partner_source_families_are_supported(self):
        required_sources = {
            "BPPA_EGP_SOLICITATION", "DGDP_EDP", "DGDP_PREPROCUREMENT",
            "WORLD_BANK_PROCUREMENT_PLAN", "WORLD_BANK_PROCUREMENT_NOTICE",
            "ADB_PROJECT_PROCUREMENT", "AIIB_PROJECT_PROCUREMENT",
            "JICA_ODA_PROCUREMENT", "UNGM_NOTICE", "DEVELOPMENT_PARTNER_OTHER",
        }
        schema_sources = set(SCHEMA["properties"]["source_family"]["enum"])
        self.assertTrue(required_sources.issubset(schema_sources), sorted(required_sources - schema_sources))
        for source in required_sources:
            self.assertIn(f"  {source}:", MAPPINGS)

    def test_all_extended_mappings_target_known_canonical_fields(self):
        known = set(FIELD_RE.findall(BASE_STANDARD)) | set(FIELD_RE.findall(STANDARD))
        mapped = set(MAPPING_RE.findall(MAPPINGS)) | set(INLINE_TARGET_RE.findall(MAPPINGS))
        self.assertTrue(mapped.issubset(known), sorted(mapped - known))

    def test_world_bank_controls_are_mapped(self):
        for token in (
            "Activity Reference No.", "Loan / Credit No.", "Review Type", "Market Approach",
            "Procurement Process", "Prequalification", "Process Status",
            "Specific Procurement Notice / Invitation",
        ):
            self.assertIn(token, MAPPINGS)

    def test_adb_aiib_jica_and_ungm_specifics_are_preserved(self):
        for token in (
            "ADB Review Procedure", "Expected Advertisement Date",
            "Contract Amount Financed by ADB", "CONTRACT SIGNING DATE",
            "Conditions for Procurement", "Eligible Source Countries", "Registration level",
            "Beneficiary countries or territories", "Sustainable opportunity", "UNSPSC",
        ):
            self.assertIn(token, MAPPINGS)

    def test_manifest_preserves_v110_foundation_under_newer_active_standard(self):
        self.assertIn("Bangladesh development-partner and cross-portal procurement normalization v1.1: PASS", MANIFEST)
        self.assertIn("bangladesh_data_standard_version: 1.3.0", MANIFEST)
        self.assertIn("development_partner_procurement_normalization: PASS", MANIFEST)


if __name__ == "__main__":
    unittest.main()
