import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data" / "registry" / "records.jsonl"
BASELINE = json.loads((ROOT / "data" / "registry" / "baseline.json").read_text())


class GitHubCanonicalBaseline(unittest.TestCase):
    def test_baseline_hash_and_count(self):
        raw = RECORDS.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), BASELINE["records_jsonl_sha256"])
        records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
        self.assertEqual(len(records), BASELINE["record_count"])
        self.assertEqual(len(records), 11)

    def test_ids_are_unique_and_relationship_targets_resolve(self):
        records = [json.loads(line) for line in RECORDS.read_text().splitlines() if line.strip()]
        ids = [record["argus_id"] for record in records]
        self.assertEqual(len(ids), len(set(ids)))
        known = set(ids)
        for record in records:
            for target in record.get("related_argus_ids", []):
                self.assertIn(target, known, f"{record['argus_id']} -> {target}")
            for rel in record.get("relationships", []):
                self.assertIn(rel["target_argus_id"], known, f"{record['argus_id']} -> {rel['target_argus_id']}")

    def test_baseline_contains_expected_record_types_and_existing_px(self):
        records = [json.loads(line) for line in RECORDS.read_text().splitlines() if line.strip()]
        types = {record["record_type"] for record in records}
        self.assertEqual(types, {"ENTITY", "PROJECT", "PROCUREMENT", "INTELLIGENCE", "OPPORTUNITY", "SUPPLIER_PRODUCT", "KNOWLEDGE"})
        self.assertTrue(any(record["argus_id"] == "2026_PX0011_APIS" for record in records))

    def test_transition_provenance_does_not_claim_fresh_database_export(self):
        source = BASELINE["import_source"]
        self.assertIn("not a fresh byte-for-byte export", source["source_authority"])
        self.assertFalse(BASELINE["canonical_transition"]["raw_source_documents_imported"])
        self.assertFalse(BASELINE["canonical_transition"]["tender_documents_imported"])


if __name__ == "__main__":
    unittest.main()
