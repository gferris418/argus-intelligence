import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / "data" / "registry" / "current-index.json").read_text())


def current(argus_id):
    path = INDEX["records"][argus_id]
    return json.loads((ROOT / path).read_text())


class DAEChar28Reconciliation(unittest.TestCase):
    def test_project_and_institution_chain_are_normalized(self):
        project = current("PRJ-BD-DAE-224385000")
        attrs = project["attributes"]
        self.assertEqual(attrs["project_code"], "224385000")
        self.assertEqual(attrs["sponsoring_ministry_entity_id"], "ENT-BD-MOA")
        self.assertEqual(attrs["implementing_agency_entity_id"], "ENT-BD-DAE")
        self.assertEqual(attrs["procuring_entity_id"], "ENT-BD-DAE-CHAR-224385000-PE")

    def test_original_tender_preserves_distinct_typed_identifiers(self):
        proc = current("PROC-DAE-1318662")
        a = proc["attributes"]
        self.assertEqual(a["solicitation_system_id"], "1318662")
        self.assertEqual(a["solicitation_reference_no"], "12.01.0000.981.07.005.26-143")
        self.assertEqual(a["app_id"], "229930")
        self.assertEqual(a["project_code"], "224385000")
        self.assertEqual(a["package_no"], "GD/DAE/CHAR-28")
        self.assertEqual(a["lot_no"], "01")
        self.assertEqual(len({a["solicitation_system_id"], a["solicitation_reference_no"], a["app_id"], a["project_code"], a["package_no"]}), 5)

    def test_original_tender_mechanics_match_uploaded_notice(self):
        a = current("PROC-DAE-1318662")["attributes"]
        self.assertEqual(a["procurement_nature"], "GOODS")
        self.assertEqual(a["procurement_type"], "NCT")
        self.assertEqual(a["procurement_method"], "OTM")
        self.assertEqual(a["document_price_bdt"], 5000)
        self.assertEqual(a["tender_security_bdt"], 3900000)
        self.assertEqual(a["tender_valid_until"], "2027-01-11")
        self.assertEqual(a["tender_security_valid_until"], "2027-02-08")
        self.assertEqual(a["closing_at"], "2026-09-13T15:30:00+06:00")
        self.assertEqual(a["opening_at"], "2026-09-13T15:30:00+06:00")
        self.assertEqual(a["procurement_state"], "CLOSED_OR_SUPERSEDED")

    def test_successor_is_supported_candidate_not_verified_retender(self):
        successor = current("PROC-DAE-CHAR28-R2")
        a = successor["attributes"]
        self.assertEqual(a["solicitation_reference_no"], "12.01.0000.981.07.005.26-367")
        self.assertEqual(a["package_no"], "GD/DAE/CHAR-28")
        self.assertEqual(a["project_code"], "224385000")
        self.assertEqual(a["publication_date"], "2026-10-08")
        self.assertEqual(a["closing_date"], "2026-10-25")
        self.assertEqual(a["cycle_sequence"], 2)
        self.assertEqual(a["predecessor_procurement_id"], "PROC-DAE-1318662")
        self.assertEqual(a["relationship_to_predecessor"], "PROBABLE_REISSUE_OF")
        self.assertEqual(a["retender_assessment"], "SUPPORTED_PENDING_OFFICIAL_VERIFICATION")
        self.assertNotIn("solicitation_system_id", a)
        self.assertNotIn("app_id", a)

    def test_same_underlying_requirement_lineage_is_preserved(self):
        first = current("PROC-DAE-1318662")
        second = current("PROC-DAE-CHAR28-R2")
        self.assertEqual(first["attributes"]["underlying_requirement_id"], second["attributes"]["underlying_requirement_id"])
        self.assertEqual(first["attributes"]["underlying_requirement_id"], "REQ-DAE-224385000-CHAR28-LLP")


if __name__ == "__main__":
    unittest.main()
