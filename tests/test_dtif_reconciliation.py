import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "data" / "registry" / "baseline.json"
BASELINE_RECORDS_PATH = ROOT / "data" / "registry" / "records.jsonl"
CURRENT_INDEX_PATH = ROOT / "data" / "registry" / "current-index.json"
RECEIPT_PATH = ROOT / "data" / "registry" / "dtif-reconciliation-receipt.json"
REPORT_PATH = ROOT / "docs" / "validation" / "dtif-reconciliation-2026-10-20.md"

EXPECTED_SOURCES = {
    "DB-001": {
        "file": "20261014_01_Opportunities_Master_v2.0.0.xlsx",
        "sha256": "1bd99cc3bf4f8b669c901fe198df2d6f6eeeb0c6f13f27272cfec296f2c60a77",
    },
    "DB-002": {
        "file": "20261014_02_Suppliers_Products_Master_v2.0.0.xlsx",
        "sha256": "a3ef7ae0efed440d6ed27dea2721c1f31207bd44300ea2cb8cfd17531e60daf7",
    },
    "DB-003": {
        "file": "20261010_03_Pursuits_Bids_Projects_v1.1.0.xlsx",
        "sha256": "26b204e536c3d2151df0e3b4da6cfaaac198c3e66d9b4585159542ba4b5803c2",
    },
}
EXPECTED_PILOT_FIXTURE_SHA256 = "2cfb99c9045eb8bf2739f39db3591b618307bda4b3cc1b301461bb259e50f2b9"
EXPECTED_SNAPSHOT = {
    "registry_record": {"rows": 131, "ordered_md5": "1b4e02ca56f4d02ca9b4af0e44348ddb"},
    "record_alias": {"rows": 13, "ordered_md5": "feb5130b3fad796e090e46809febd293"},
    "record_domain_classification": {"rows": 1, "ordered_md5": "15238b724278d3bd2a8a0220295b1d3f"},
    "record_evidence": {"rows": 136, "ordered_md5": "d5ee2f484e0099024a6a5d2405eeb75b"},
    "record_external_ref": {"rows": 135, "ordered_md5": "9e79ca7430bf06959fa98fcf593949a2"},
    "record_related": {"rows": 130, "ordered_md5": "01a1719f6d3b59fd88146847dda4a554"},
    "record_relationship": {"rows": 130, "ordered_md5": "16045bc0ece0c8f8594f760938d960e6"},
    "record_standard_ref": {"rows": 0, "ordered_md5": "d41d8cd98f00b204e9800998ecf8427e"},
}
EXPECTED_DISPOSITIONS = {
    "DB-001_CURRENT_PUBLISHED_WAVE1": {
        "count": 119,
        "action": "HISTORICAL_LINEAGE_REVERIFY_ON_TRIGGER",
    },
    "DB-001_PLANNED_PURCHASE": {
        "count": 702,
        "action": "RETAIN_READ_ONLY_REVERIFY_ON_TRIGGER",
    },
    "DB-002_SUPPLIER_PRODUCT_RELATIONSHIPS": {
        "count": None,
        "action": "RETAIN_READ_ONLY_REVERIFY_BEFORE_REUSE",
    },
    "DB-003_PURSUIT_BUDGET": {
        "count": None,
        "action": "RETAIN_READ_ONLY_REEVALUATE_BEFORE_ACTIVE_USE",
    },
}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class DTIFReconciliation(unittest.TestCase):
    def test_reconciliation_receipt_pins_verified_legacy_sources(self):
        receipt = _read_json(RECEIPT_PATH)
        self.assertEqual("DTIF-RECONCILIATION", receipt["control_id"])
        self.assertEqual("RECONCILED_ARCHIVE_ONLY", receipt["status"])
        self.assertEqual("ARGUS-DTIF-MIGRATION-PILOT-001", receipt["pilot"]["id"])
        self.assertEqual("0.1.0", receipt["pilot"]["version"])
        self.assertEqual(EXPECTED_PILOT_FIXTURE_SHA256, receipt["pilot"]["fixture_sha256"])
        actual_sources = {
            source["logical_id"]: {"file": source["file"], "sha256": source["sha256"]}
            for source in receipt["legacy_sources"]
        }
        self.assertEqual(EXPECTED_SOURCES, actual_sources)
        self.assertTrue(all(source["hash_verified_from_library_bytes"] for source in receipt["legacy_sources"]))

    def test_wave1_historical_snapshot_is_fingerprinted_not_repromoted(self):
        receipt = _read_json(RECEIPT_PATH)
        snapshot = receipt["wave1_historical_snapshot"]
        self.assertEqual(131, snapshot["registry_records"])
        self.assertEqual(119, snapshot["wave1_procurement_records"])
        self.assertEqual(1, snapshot["wave1_supporting_entities"])
        self.assertEqual(0, snapshot["broken_relationship_targets"])
        self.assertEqual("published_or_active_source_current_status_unverified", snapshot["wave1_status"])
        self.assertEqual(EXPECTED_SNAPSHOT, snapshot["table_fingerprints"])
        self.assertFalse(snapshot["promoted_to_current_github_canonical"])
        self.assertEqual(
            "HISTORICAL_LINEAGE_REVERIFY_ON_TRIGGER",
            snapshot["current_truth_treatment"],
        )

    def test_all_remaining_legacy_classes_have_explicit_non_bulk_disposition(self):
        receipt = _read_json(RECEIPT_PATH)
        actual = {
            item["class"]: {"count": item["count"], "action": item["action"]}
            for item in receipt["legacy_class_dispositions"]
        }
        self.assertEqual(EXPECTED_DISPOSITIONS, actual)
        self.assertTrue(all(item["bulk_import_prohibited"] for item in receipt["legacy_class_dispositions"]))

    def test_canonical_baseline_is_bound_to_the_same_pilot_fixture(self):
        baseline = _read_json(BASELINE_PATH)
        raw = BASELINE_RECORDS_PATH.read_bytes()
        self.assertEqual("ARGUS-DTIF-MIGRATION-PILOT-001", baseline["import_source"]["pilot_id"])
        self.assertEqual("0.1.0", baseline["import_source"]["pilot_version"])
        self.assertEqual(EXPECTED_PILOT_FIXTURE_SHA256, baseline["import_source"]["library_fixture_sha256"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), baseline["records_jsonl_sha256"])
        self.assertEqual(len(_read_jsonl(BASELINE_RECORDS_PATH)), baseline["record_count"])
        self.assertIn("not a fresh byte-for-byte export", baseline["import_source"]["source_authority"])

    def test_current_canonical_overlay_and_relationship_targets_resolve(self):
        baseline_records = {record["argus_id"]: record for record in _read_jsonl(BASELINE_RECORDS_PATH)}
        current_index = _read_json(CURRENT_INDEX_PATH)["records"]
        canonical = dict(baseline_records)
        for argus_id, relative_path in current_index.items():
            current_path = ROOT / relative_path
            self.assertTrue(current_path.is_file(), relative_path)
            current = _read_json(current_path)
            self.assertEqual(argus_id, current["argus_id"])
            if argus_id in baseline_records:
                self.assertGreaterEqual(current["revision"], baseline_records[argus_id]["revision"])
            canonical[argus_id] = current

        known = set(canonical)
        for record in canonical.values():
            for target in record.get("related_argus_ids", []):
                self.assertIn(target, known, f"{record['argus_id']} -> {target}")
            for relationship in record.get("relationships", []):
                self.assertIn(
                    relationship["target_argus_id"],
                    known,
                    f"{record['argus_id']} -> {relationship['target_argus_id']}",
                )

    def test_archive_disposition_retains_sources_and_does_not_claim_bulk_cutover(self):
        receipt = _read_json(RECEIPT_PATH)
        archive = receipt["archive_disposition"]
        self.assertEqual("RETAIN_READ_ONLY_ARCHIVE_SOURCE", archive["action"])
        self.assertTrue(archive["archive_only_ready"])
        self.assertTrue(archive["retain_original_source_bytes"])
        self.assertFalse(archive["delete_after_reconciliation"])
        self.assertFalse(receipt["claims"]["fresh_database_export"])
        self.assertFalse(receipt["claims"]["bulk_dtif_cutover"])
        self.assertFalse(receipt["claims"]["legacy_current_status_treated_as_current_truth"])
        self.assertTrue(REPORT_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
