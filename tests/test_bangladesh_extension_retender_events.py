import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STD = (ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v1.3.yaml").read_text()
MAP = (ROOT / "profiles" / "bangladesh-source-mappings-v1.3.yaml").read_text()
PURSUIT = (ROOT / "profiles" / "bangladesh-pursuit-activation.yaml").read_text()
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()


class BangladeshExtensionRetenderEvents(unittest.TestCase):
    def test_deadline_and_validity_extensions_are_distinct(self):
        self.assertIn("SUBMISSION_DEADLINE_EXTENSION", STD)
        self.assertIn("TENDER_VALIDITY_EXTENSION", STD)
        self.assertIn("solicitation.original_closing_at:", STD)
        self.assertIn("solicitation.closing_at", STD)
        self.assertIn("solicitation.extension_count:", STD)
        self.assertIn("procurement.events:", STD)

    def test_event_history_is_append_only_and_current_dates_are_derived(self):
        self.assertIn("append_only", STD)
        self.assertIn("never overwrite event history", STD.lower())
        self.assertIn("current effective", STD.lower())
        self.assertIn("previous_value", STD)
        self.assertIn("new_value", STD)
        self.assertIn("source_ref", STD)

    def test_retender_is_new_solicitation_cycle_same_opportunity_by_default(self):
        self.assertIn("RETENDER_ISSUED", STD)
        self.assertIn("procurement.reissue_sequence:", STD)
        self.assertIn("procurement.predecessor_argus_id:", STD)
        self.assertIn("replaces", STD)
        self.assertIn("same underlying opportunity lineage", STD.lower())
        self.assertIn("must not overwrite", STD.lower())

    def test_retender_reason_is_not_inferred(self):
        self.assertIn("procurement.reissue_reason_raw:", STD)
        self.assertIn("do not infer", STD.lower())
        self.assertIn("UNKNOWN", STD)

    def test_bppa_and_dgdp_extension_retender_source_patterns_are_mapped(self):
        for token in (
            "Date Of Corrigendum",
            "Tender Closing Date",
            "Tender Opening Date",
            "Invitation for Re-Tender",
            "Request for Extention of Submission Deadline",
        ):
            self.assertIn(token, MAP)
        self.assertIn("SUBMISSION_DEADLINE_EXTENSION", MAP)
        self.assertIn("RETENDER_ISSUED", MAP)

    def test_pursuit_reacts_to_extension_and_retender_without_duplicate_opportunity(self):
        self.assertIn("submission_deadline_extension", PURSUIT.lower())
        self.assertIn("retender", PURSUIT.lower())
        self.assertIn("re-engage", PURSUIT.lower())
        self.assertIn("same underlying opportunity lineage", PURSUIT.lower())

    def test_manifest_activates_v130(self):
        self.assertIn("bangladesh_procurement_standard_version: 1.3.0", MANIFEST)
        self.assertIn("tender_extension_and_retender_events: PASS", MANIFEST)


if __name__ == "__main__":
    unittest.main()
