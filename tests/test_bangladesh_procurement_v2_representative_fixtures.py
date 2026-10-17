import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "bangladesh-v2"
REPORT = ROOT / "docs" / "validation" / "bangladesh-procurement-v2-representative-fixtures.md"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()
V2 = (ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v2.0.yaml").read_text()

FIXTURES = {
    "bcg_cpv": FIXTURE_DIR / "bcg-cpv.json",
    "dae_llp": FIXTURE_DIR / "dae-low-lift-pump.json",
    "dgdp_rhib": FIXTURE_DIR / "dgdp-rhib.json",
    "world_bank_sita_g01": FIXTURE_DIR / "world-bank-sita-g01.json",
}


def load_fixture(name):
    return json.loads(FIXTURES[name].read_text())


def identifiers(record):
    return {(x["scheme"], x["value"]) for x in record["identifiers"]}


def roles(record):
    return {(x["party_id"], x["role"]) for x in record["party_role_links"]}


def milestones(record):
    return {x["type"]: x for x in record.get("milestones", [])}


class BangladeshProcurementV2RepresentativeFixtures(unittest.TestCase):
    def test_four_representative_fixtures_exist_without_live_migration(self):
        for name, path in FIXTURES.items():
            self.assertTrue(path.exists(), name)
            fixture = load_fixture(name)
            self.assertEqual(fixture["fixture_type"], "v1_to_v2_semantic_validation")
            self.assertFalse(fixture["live_registry_mutation"])
            self.assertEqual(fixture["target_standard"], "2.0.0-candidate")
            self.assertIn("source_basis", fixture)
            self.assertIn("v2_candidate", fixture)
        self.assertIn("bangladesh_procurement_standard: profiles/bangladesh-canonical-procurement-standard-v1.3.yaml", MANIFEST)

    def test_bcg_cpv_preserves_roles_lot_commercials_and_extension_history_without_duplicate_counter(self):
        f = load_fixture("bcg_cpv")
        r = f["v2_candidate"]
        self.assertIn(("TENDER_REFERENCE_NO", "44.08.2680.033.02.106.26.160"), identifiers(r))
        self.assertIn(("ENT-BD-MOHA", "SPONSORING_MINISTRY"), roles(r))
        self.assertIn(("ENT-BD-BCG-PD-224392800", "PROCURING_ENTITY"), roles(r))
        self.assertIn(("ENT-BD-COAST-GUARD", "END_USER"), roles(r))
        self.assertEqual(r["process"]["category"], "WORKS")
        self.assertEqual(r["process"]["competition_scope"], "INTERNATIONAL")
        self.assertEqual(r["process"]["configuration"], "ONE_STAGE_TWO_ENVELOPE")
        self.assertEqual(r["lots"][0]["lot_id"], "1")
        self.assertEqual(r["lots"][0]["lot_reference"], "WD-2")
        self.assertEqual(r["fees"][0]["amount"], 100000)
        self.assertEqual(r["securities"][0]["amount"], 230000000)
        ms = milestones(r)
        self.assertEqual(ms["SUBMISSION_DEADLINE"]["original_due_at"], "2026-09-29T12:00:00+06:00")
        self.assertEqual(ms["SUBMISSION_DEADLINE"]["due_at"], "2026-10-25T12:00:00+06:00")
        extensions = [e for e in r["events"] if e["type"] == "DEADLINE_EXTENSION"]
        self.assertEqual(len(extensions), 2)
        self.assertNotIn("extension_count", r)
        self.assertNotIn("extension_count", r.get("process", {}))

    def test_dae_egp_preserves_typed_ids_and_separates_method_scope_and_dates(self):
        f = load_fixture("dae_llp")
        r = f["v2_candidate"]
        ids = identifiers(r)
        for expected in {
            ("SYSTEM_TENDER_ID", "1318662"),
            ("TENDER_REFERENCE_NO", "12.01.0000.981.07.005.26-143"),
            ("EGP_APP_ID", "229930"),
            ("PACKAGE_NO", "GD/DAE/CHAR-28"),
        }:
            self.assertIn(expected, ids)
        self.assertEqual(r["requirement_ref"], "REQ-DAE-224385000-CHAR28-LLP")
        self.assertEqual(r["process"]["category"], "GOODS")
        self.assertEqual(r["process"]["method_normalized"], "OPEN")
        self.assertEqual(r["process"]["method_source_code"], "OTM")
        self.assertEqual(r["process"]["competition_scope"], "NATIONAL")
        self.assertNotIn("configuration", r["process"], "do not infer envelope structure when source does not state it")
        self.assertEqual(r["fees"][0]["amount"], 5000)
        self.assertEqual(r["securities"][0]["amount"], 3900000)
        ms = milestones(r)
        self.assertEqual(ms["SUBMISSION_DEADLINE"]["due_at"], "2026-09-13T15:30:00+06:00")
        self.assertEqual(ms["VALIDITY_END"]["due_at"], "2027-01-11")
        self.assertEqual(ms["SECURITY_VALIDITY_END"]["due_at"], "2027-02-08")

    def test_dgdp_fixture_preserves_defence_route_unit_enlistment_and_sparse_unknowns(self):
        f = load_fixture("dgdp_rhib")
        r = f["v2_candidate"]
        self.assertIn(("DGDP_TENDER_NUMBER", "248.07.076.26"), identifiers(r))
        self.assertEqual(r["process"]["route"], "BD-DEF-DGDP")
        self.assertEqual(r["process"]["category"], "GOODS")
        self.assertEqual(r["process"]["method_normalized"], "OPEN")
        self.assertNotIn("competition_scope", r["process"], "foreign-currency tender basis does not prove international competition scope")
        self.assertIn(("ENT-BD-DGDP", "PROCURING_ENTITY"), roles(r))
        self.assertIn(("ENT-BD-NAVY", "END_USER"), roles(r))
        dgdp_link = next(x for x in r["party_role_links"] if x["party_id"] == "ENT-BD-DGDP")
        self.assertEqual(dgdp_link["unit_label"], "Navy Wing / NP-8")
        enlistment = next(x for x in r["requirements"] if x["type"] == "ENLISTMENT")
        self.assertTrue(enlistment["mandatory"])
        self.assertIn("DGDP", enlistment["text"])
        self.assertEqual(r["fees"][0]["type"], "SCHEDULE_PURCHASE")
        self.assertFalse(r["fees"][0]["refundable"])
        self.assertEqual(r["items"][0]["quantity"], 3)
        self.assertEqual(r["intelligence"]["supplier_discovery_state"], "PENDING_TECHNICAL_SCHEDULE")
        self.assertNotIn("project_ref", r)

    def test_world_bank_fixture_exercises_review_market_configuration_financing_and_planned_milestones(self):
        f = load_fixture("world_bank_sita_g01")
        r = f["v2_candidate"]
        self.assertIn(("PROCUREMENT_ACTIVITY_ID", "PMIPSD/G-01"), identifiers(r))
        self.assertEqual(f["linked_context"]["project"]["identifiers"][0]["value"], "P506691")
        self.assertNotIn(("PROJECT_ID", "P506691"), identifiers(r), "project identity belongs to linked PROJECT context, not duplicated on PROCUREMENT")
        self.assertEqual(r["process"]["category"], "GOODS")
        self.assertEqual(r["process"]["method_normalized"], "OPEN")
        self.assertEqual(r["process"]["method_source_label"], "Request for Bids")
        self.assertEqual(r["process"]["competition_scope"], "INTERNATIONAL")
        self.assertEqual(r["process"]["configuration"], "ONE_STAGE_TWO_ENVELOPE")
        self.assertEqual(r["process"]["review_type"], "PRIOR")
        self.assertEqual(r["process"]["estimated_value"], 3333333.00)
        self.assertEqual(r["process"]["currency"], "USD")
        self.assertEqual(r["financing_entries"][0]["instrument"], "CREDIT")
        self.assertEqual(r["financing_entries"][0]["reference"], "IDA / 78280")
        self.assertEqual(r["process"]["status_raw"], "Pending Implementation")
        self.assertIn("EXPECTED_PUBLICATION", V2)
        ms = milestones(r)
        for milestone_type in ("EXPECTED_PUBLICATION", "SUBMISSION_DEADLINE", "EXPECTED_AWARD", "CONTRACT_SIGNING", "COMPLETION"):
            self.assertIn(milestone_type, ms)
            self.assertEqual(ms[milestone_type]["status"], "PLANNED")

    def test_validation_report_requires_zero_material_loss_and_records_non_lossy_semantic_changes(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text()
        for token in (
            "BCG CPV", "DAE Low Lift Pump", "DGDP RHIB", "World Bank SITA PMIPSD/G-01",
            "Material information loss: 0", "Live registry mutation: false",
            "Semantic equivalence: PASS", "Information preservation: PASS",
            "v1.3 remains active", "GO / NO-GO",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
