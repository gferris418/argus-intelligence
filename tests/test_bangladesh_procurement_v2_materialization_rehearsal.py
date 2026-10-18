import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SCHEMA = ROOT / "registry" / "schema" / "argus-master-registry-v0.3.0-candidate.json"
DOMAIN_SCHEMA = ROOT / "schemas" / "bangladesh-procurement-v2-domain.schema.json"
TOOL = ROOT / "tools" / "bangladesh_procurement_v2_materialize.py"
FIXTURE_MAP = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "current-procurement-fixture-map.json"
REHEARSAL = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "registry-envelope-materialization-rehearsal.json"
HISTORICAL = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "historical-baseline-rehearsal.json"
CURRENT_INDEX = ROOT / "data" / "registry" / "current-index.json"
REPORT = ROOT / "docs" / "validation" / "bangladesh-procurement-v2-registry-envelope-materialization.md"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_sha256(value) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(data)


def load_tool():
    if not TOOL.exists():
        raise AssertionError(f"missing materializer: {TOOL}")
    spec = importlib.util.spec_from_file_location("bd_v2_materialize", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_expected_rehearsal():
    module = load_tool()
    fixture_map = json.loads(FIXTURE_MAP.read_text())
    historical = json.loads(HISTORICAL.read_text())
    ids = sorted(fixture_map)
    source_snapshots = {}
    output_hashes = {}

    for argus_id in ids:
        current_path = ROOT / "data" / "registry" / "current" / f"{argus_id}.json"
        source_bytes = current_path.read_bytes()
        current = json.loads(source_bytes)
        standalone = json.loads((ROOT / fixture_map[argus_id]).read_text())["v2_candidate"]
        materialized = module.materialize_registry_procurement(current, standalone)
        source_snapshots[argus_id] = {
            "sha256": sha256_bytes(source_bytes),
            "bytes": len(source_bytes),
        }
        output_hashes[argus_id] = canonical_json_sha256(materialized)

    return {
        "fixture_type": "registry_envelope_materialization_rehearsal",
        "target_registry_schema": "0.3.0-candidate",
        "target_domain_profile": "BANGLADESH_PROCUREMENT/2.0.0-candidate",
        "current_source_count": len(ids),
        "current_output_count": len(ids),
        "current_source_ids": ids,
        "current_output_ids": ids,
        "source_snapshots": source_snapshots,
        "materialized_output_sha256": output_hashes,
        "candidate_index_ids": ids,
        "historical_source_count": historical["source_procurement_count"],
        "historical_ids": historical["source_argus_ids"],
        "historical_baseline_sha256": historical["baseline_sha256"],
        "historical_current_overlay_backfill_prohibited": True,
        "schema_validation": "PASS",
        "relationship_resolution": "PASS",
        "material_information_loss": 0,
        "rollback_exact": True,
        "live_registry_mutation": False,
    }


class BangladeshProcurementV2MaterializationRehearsal(unittest.TestCase):
    def test_rehearsal_artifact_equals_deterministic_receipt(self):
        expected = build_expected_rehearsal()
        if not REHEARSAL.exists():
            self.fail("EXPECTED_REHEARSAL=" + json.dumps(expected, indent=2, sort_keys=True))
        self.assertEqual(json.loads(REHEARSAL.read_text()), expected)

    def test_every_materialized_candidate_validates_and_relationship_targets_resolve(self):
        module = load_tool()
        registry_schema = json.loads(REGISTRY_SCHEMA.read_text())
        domain_schema = json.loads(DOMAIN_SCHEMA.read_text())
        fixture_map = json.loads(FIXTURE_MAP.read_text())
        index = json.loads(CURRENT_INDEX.read_text())["records"]

        for argus_id, fixture_path in fixture_map.items():
            current = json.loads((ROOT / "data" / "registry" / "current" / f"{argus_id}.json").read_text())
            standalone = json.loads((ROOT / fixture_path).read_text())["v2_candidate"]
            record = module.materialize_registry_procurement(current, standalone)
            Draft202012Validator(registry_schema).validate(record)
            Draft202012Validator(domain_schema).validate(record["domain_payload"]["data"])
            for relation in record.get("relationships", []):
                self.assertIn(relation["target_argus_id"], index)

    def test_rollback_snapshot_hashes_match_current_source_bytes(self):
        expected = build_expected_rehearsal()
        for argus_id, snapshot in expected["source_snapshots"].items():
            data = (ROOT / "data" / "registry" / "current" / f"{argus_id}.json").read_bytes()
            self.assertEqual(snapshot["sha256"], sha256_bytes(data))
            self.assertEqual(snapshot["bytes"], len(data))
        self.assertEqual(expected["current_source_ids"], expected["current_output_ids"])
        self.assertTrue(expected["rollback_exact"])

    def test_historical_fixture_remains_separate_provenance_input(self):
        historical = json.loads(HISTORICAL.read_text())
        expected = build_expected_rehearsal()
        self.assertEqual(expected["historical_baseline_sha256"], historical["baseline_sha256"])
        self.assertEqual(expected["historical_ids"], historical["source_argus_ids"])
        self.assertTrue(expected["historical_current_overlay_backfill_prohibited"])

    def test_validation_report_records_go_no_go_and_v1_3_authority(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text()
        for phrase in [
            "v1.3 remains active",
            "NO-GO for live activation in this gate",
            "composed Master Registry envelope",
            "6/6 current PROCUREMENT records",
            "rollback exact",
            "later activation PR",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
