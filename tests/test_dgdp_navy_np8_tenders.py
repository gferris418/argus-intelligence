import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "data" / "registry" / "current"
INDEX_PATH = ROOT / "data" / "registry" / "current-index.json"


class DGDPNavyNP8Tenders(unittest.TestCase):
    def load_current(self, argus_id):
        index = json.loads(INDEX_PATH.read_text())
        rel = index["records"][argus_id]
        return json.loads((ROOT / rel).read_text())

    def test_institution_chain_is_normalized(self):
        mod = self.load_current("ENT-BD-MOD")
        dgdp = self.load_current("ENT-BD-DGDP")
        navy = self.load_current("ENT-BD-NAVY")
        self.assertEqual(mod["attributes"]["entity_type"], "MINISTRY")
        self.assertEqual(dgdp["attributes"]["entity_type"], "DEFENCE_PROCUREMENT_ORGANIZATION")
        self.assertEqual(navy["attributes"]["entity_type"], "MILITARY_END_USER_SERVICE")
        self.assertIn("ENT-BD-DGDP", mod["related_argus_ids"])
        self.assertIn("ENT-BD-NAVY", dgdp["related_argus_ids"])

    def test_three_separate_tender_records_exist(self):
        expected = {
            "PROC-DGDP-248-07-075-26": ("248.07.075.26", "Inflatable Boat (IB) Without Engines", 3, "Nos", 1000),
            "PROC-DGDP-248-07-076-26": ("248.07.076.26", "Rigid Hull Inflatable Boat (RHIB) with Twin Engine", 3, "Nos", 5000),
            "PROC-DGDP-248-07-078-26": ("248.07.078.26", "Twin Cylinder Open Circuit (SCUBA) Diving Set Complete", 50, "Set", 5000),
        }
        for argus_id, (ref, title, qty, unit, price) in expected.items():
            rec = self.load_current(argus_id)
            attrs = rec["attributes"]
            self.assertEqual(rec["record_type"], "PROCUREMENT")
            self.assertEqual(rec["canonical_name_or_title"], title)
            self.assertEqual(attrs["solicitation_reference_no"], ref)
            self.assertEqual(attrs["quantity"]["value"], qty)
            self.assertEqual(attrs["quantity"]["unit"], unit)
            self.assertEqual(attrs["tender_schedule_price_bdt"], price)

    def test_live_dgdp_route_and_dates_are_preserved(self):
        for argus_id in [
            "PROC-DGDP-248-07-075-26",
            "PROC-DGDP-248-07-076-26",
            "PROC-DGDP-248-07-078-26",
        ]:
            attrs = self.load_current(argus_id)["attributes"]
            self.assertEqual(attrs["bangladesh_route"], "BD-DEF-DGDP")
            self.assertEqual(attrs["procurement_state"], "OPEN")
            self.assertEqual(attrs["maturity"], "I9")
            self.assertEqual(attrs["wing"], "Navy Wing")
            self.assertEqual(attrs["section"], "NP-8")
            self.assertEqual(attrs["selling_from"], "2026-10-15")
            self.assertEqual(attrs["selling_to"], "2026-11-25")
            self.assertEqual(attrs["submission_deadline_at"], "2026-11-26T12:00:00+06:00")
            self.assertEqual(attrs["opening_at"], "2026-11-26T12:05:00+06:00")
            self.assertEqual(attrs["tender_currency_basis"], "FOREIGN_CURRENCY")

    def test_no_unsupported_project_or_system_identifiers_are_invented(self):
        for argus_id in [
            "PROC-DGDP-248-07-075-26",
            "PROC-DGDP-248-07-076-26",
            "PROC-DGDP-248-07-078-26",
        ]:
            attrs = self.load_current(argus_id)["attributes"]
            self.assertNotIn("solicitation_system_id", attrs)
            self.assertNotIn("app_id", attrs)
            self.assertNotIn("project_code", attrs)
            self.assertNotIn("package_no", attrs)
            self.assertNotIn("lot_no", attrs)
            self.assertEqual(attrs["supplier_discovery_state"], "PENDING_TECHNICAL_SCHEDULE")

    def test_notice_is_not_flattened_into_one_multi_lot_procurement(self):
        refs = {
            self.load_current(x)["attributes"]["solicitation_reference_no"]
            for x in [
                "PROC-DGDP-248-07-075-26",
                "PROC-DGDP-248-07-076-26",
                "PROC-DGDP-248-07-078-26",
            ]
        }
        self.assertEqual(refs, {"248.07.075.26", "248.07.076.26", "248.07.078.26"})


if __name__ == "__main__":
    unittest.main()
