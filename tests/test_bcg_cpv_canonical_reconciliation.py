import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = {
    r["argus_id"]: r
    for r in (
        json.loads(line)
        for line in (ROOT / "data" / "registry" / "records.jsonl").read_text().splitlines()
        if line.strip()
    )
}


class BCGCPVCanonicalReconciliation(unittest.TestCase):
    def test_project_is_linked_to_current_official_project_identity(self):
        project = RECORDS["PRJ-BCG-CPV-WD2"]
        attrs = project["attributes"]
        self.assertEqual(attrs["project_code"], "224392800")
        self.assertEqual(attrs["project_status"], "APPROVED")
        self.assertEqual(attrs["funding_source"], "GOB")
        self.assertEqual(attrs["implementing_agency"], "Bangladesh Coast Guard")

    def test_procurement_uses_reference_and_lot_identification_correctly(self):
        proc = RECORDS["PROC-BCG-LT001"]
        attrs = proc["attributes"]
        self.assertEqual(attrs["solicitation_reference_no"], "44.08.2680.033.02.106.26.160")
        self.assertIsNone(attrs["solicitation_system_id"])
        self.assertIsNone(attrs["package_reference"])
        self.assertEqual(attrs["lot_no"], "1")
        self.assertEqual(attrs["lot_identification"], "WD-2")
        self.assertNotEqual(attrs["solicitation_reference_no"], attrs["lot_identification"])

    def test_procurement_is_current_i9_with_two_append_only_extensions(self):
        proc = RECORDS["PROC-BCG-LT001"]
        attrs = proc["attributes"]
        self.assertEqual(attrs["maturity"], "I9")
        self.assertEqual(attrs["maturity_condition"], "CURRENT")
        self.assertEqual(attrs["procurement_state"], "LIVE")
        self.assertEqual(attrs["solicitation_status"], "ACTIVE_CORRIGENDUM")
        self.assertEqual(attrs["original_closing_at"], "2026-09-29T12:00:00+06:00")
        self.assertEqual(attrs["closing_at"], "2026-10-25T12:00:00+06:00")
        self.assertEqual(attrs["opening_at"], "2026-10-25T12:30:00+06:00")
        self.assertEqual(attrs["extension_count"], 2)
        events = attrs["procurement_events"]
        self.assertEqual(len(events), 2)
        self.assertEqual([e["event_type"] for e in events], ["SUBMISSION_DEADLINE_EXTENSION", "SUBMISSION_DEADLINE_EXTENSION"])

    def test_verified_commercial_mechanics_are_preserved(self):
        attrs = RECORDS["PROC-BCG-LT001"]["attributes"]
        self.assertEqual(attrs["tender_document_price_bdt"], 100000)
        self.assertEqual(attrs["tender_security_bdt"], 230000000)
        self.assertEqual(attrs["completion_period"], "36 months after signing the contract")
        self.assertEqual(attrs["procurement_method"], "ICT_ONE_STAGE_TWO_ENVELOPE")

    def test_competitor_signal_remains_qualified_not_confirmed_bidder(self):
        attrs = RECORDS["PROC-BCG-LT001"]["attributes"]
        signals = attrs["ecosystem_signals"]
        dew = next(x for x in signals if x["entity"] == "Dockyard and Engineering Works Limited")
        self.assertEqual(dew["signal_type"], "COMPETITOR_OR_BIDDER_SIGNAL")
        self.assertEqual(dew["exact_role"], "UNKNOWN")
        self.assertNotEqual(dew["exact_role"], "CONFIRMED_BIDDER")


if __name__ == "__main__":
    unittest.main()
