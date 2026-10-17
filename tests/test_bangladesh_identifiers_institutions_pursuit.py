import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = (ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v1.2.yaml").read_text()
MAP = (ROOT / "profiles" / "bangladesh-source-mappings-v1.2.yaml").read_text()
INST = (ROOT / "profiles" / "bangladesh-institution-standard.yaml").read_text()
PURSUIT = (ROOT / "profiles" / "bangladesh-pursuit-activation.yaml").read_text()
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()


class BangladeshIdentifierInstitutionPursuit(unittest.TestCase):
    def test_egp_system_id_and_reference_number_are_distinct(self):
        proc_lower = PROC.lower()
        self.assertIn("solicitation.system_id:", PROC)
        self.assertIn("solicitation.reference_no:", PROC)
        self.assertIn("portal-generated tender/proposal id", proc_lower)
        self.assertIn("procuring-entity invitation/tender/proposal reference", proc_lower)
        self.assertIn("Tender/Proposal ID", MAP)
        self.assertIn("canonical_field: solicitation.system_id", MAP)
        self.assertIn("Invitation Reference No.", MAP)
        self.assertIn("canonical_field: solicitation.reference_no", MAP)
        self.assertIn("DGDP Tender No", MAP)

    def test_legacy_generic_solicitation_id_is_deprecated(self):
        self.assertIn("solicitation.id:", PROC)
        self.assertIn("deprecated", PROC.lower())
        self.assertIn("do_not_write_new_records: true", PROC)

    def test_institution_graph_separates_stable_entity_from_officeholder(self):
        for token in (
            "MINISTRY", "DIVISION", "DIRECTORATE", "AUTHORITY", "BOARD",
            "CORPORATION", "COMMISSION", "FORCE", "PROJECT_OFFICE", "PROCURING_ENTITY_OFFICE",
        ):
            self.assertIn(f"  - {token}", INST)
        for field in (
            "institution_id", "official_name_bn", "official_name_en", "parent_institution_id",
            "organization_type", "official_domain", "aliases", "valid_from", "valid_to",
        ):
            self.assertIn(field, INST)
        self.assertIn("officeholders are time-bounded role assignments", INST)
        self.assertIn("Bangladesh National Portal", INST)
        self.assertIn("BPPA/e-GP", INST)
        self.assertIn("DGDP/e-DP", INST)

    def test_procurement_entity_hierarchy_is_not_flattened(self):
        for token in (
            "ministry", "division", "organization", "procuring_entity_office", "project_office", "end_user",
        ):
            self.assertIn(token, INST)
        self.assertIn("same text value does not make two typed institutions identical", INST)

    def test_three_activation_modes_are_explicit(self):
        for mode in (
            "EARLY_REQUIREMENT_DEVELOPMENT",
            "PLANNED_PROCUREMENT_CAPTURE",
            "LIVE_TENDER_RESPONSE",
        ):
            self.assertIn(mode, PURSUIT)
        self.assertIn("one underlying opportunity lineage", PURSUIT)
        self.assertIn("supplier discovery", PURSUIT.lower())
        self.assertIn("customer engagement", PURSUIT.lower())
        self.assertIn("compliance matrix", PURSUIT.lower())

    def test_specification_influence_has_competition_safeguards(self):
        pursuit_lower = PURSUIT.lower()
        self.assertIn("performance-based", pursuit_lower)
        self.assertIn("widest possible competition", pursuit_lower)
        self.assertIn("improperly exclude competitors", pursuit_lower)
        self.assertIn("ppr 2025", pursuit_lower)

    def test_manifest_preserves_v120_contracts_under_active_v130(self):
        self.assertIn("bangladesh_data_standard_version: 1.3.0", MANIFEST)
        self.assertIn("bangladesh_institution_standard: profiles/bangladesh-institution-standard.yaml", MANIFEST)
        self.assertIn("bangladesh_pursuit_activation: profiles/bangladesh-pursuit-activation.yaml", MANIFEST)
        self.assertIn("egp_system_id_reference_no_separation: PASS", MANIFEST)


if __name__ == "__main__":
    unittest.main()
