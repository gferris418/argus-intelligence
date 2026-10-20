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


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class DTIFReconciliation(unittest.TestCase):
    def test_reconciliation_receipt_exists_and_pins_verified_legacy_sources(self):
        receipt = _read_json(RECEIPT_PATH)
        self.assertEqual("DTIF-RECONCILIATION", receipt["control_id"])
        self.assertEqual("RECONCILED", receipt["status"])
        self.assertEqual("ARGUS-DTIF-MIGRATION-PILOT-001", receipt["pilot"]["id"])
        self.assertEqual("0.1.0", receipt["pilot"]["version"])
        self.assertEqual(EXPECTED_PILOT_FIXTURE_SHA256, receipt["pilot"]["fixture_sha256"])
        actual_sources = {
            source["logical_id"]: {"file": source["file"], "sha256": source["sha256"]}
            for source in receipt["legacy_sources"]
        }
        self.assertEqual(EXPECTED_SOURCES, actual_sources)
        self.assertTrue(all(source["hash_verified_from_library_bytes"] for source in receipt["legacy_sources"]))

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

    def test_archive_disposition_retains_legacy_sources_and_does_not_claim_bulk_cutover(self):
        receipt = _read_json(RECEIPT_PATH)
        self.assertEqual("RETAIN_READ_ONLY_ARCHIVE_SOURCE", receipt["archive_disposition"]["action"])
        self.assertTrue(receipt["archive_disposition"]["retain_original_source_bytes"])
        self.assertFalse(receipt["archive_disposition"]["delete_after_reconciliation"])
        self.assertFalse(receipt["claims"]["fresh_database_export"])
        self.assertFalse(receipt["claims"]["bulk_dtif_cutover"])
        self.assertTrue(REPORT_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
