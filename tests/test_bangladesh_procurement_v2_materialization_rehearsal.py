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


def load_tool():
    if not TOOL.exists():
        raise AssertionError(f"missing materializer: {TOOL}")
    spec = importlib.util.spec_from_file_location("bd_v2_materialize", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BangladeshProcurementV2MaterializationRehearsal(unittest.TestCase):
    def test_rehearsal_artifact_covers_all_current_procurements_and_historical_baseline(self):
        self.assertTrue(REHEARSAL.exists())
        fixture_map = json.loads(FIXTURE_MAP.read_text())
        rehearsal = json.loads(REHEARSAL.read_text())
        self.assertEqual(set(rehearsal["current_source_ids"]), set(fixture_map))
        self.assertEqual(set(rehearsal["current_output_ids"]), set(fixture_map))
        self.assertEqual(rehearsal["current_source_count"], 6)
        self.assertEqual(rehearsal["current_output_count"], 6)
        self.assertEqual(rehearsal["historical_source_count"], 1)
        self.assertEqual(rehearsal["historical_ids"], ["PROC-BCG-LT001"])
        self.assertEqual(rehearsal["material_information_loss"], 0)
        self.assertTrue(rehearsal["rollback_exact"])
        self.assertFalse(rehearsal["live_registry_mutation"])

    def test_committed_current_materializations_equal_fresh_adapter_output(self):
        self.assertTrue(REHEARSAL.exists())
        module = load_tool()
        rehearsal = json.loads(REHEARSAL.read_text())
        fixture_map = json.loads(FIXTURE_MAP.read_text())
        committed = {r["argus_id"]: r for r in rehearsal["materialized_current_records"]}

        for argus_id, fixture_path in fixture_map.items():
            current = json.loads((ROOT / "data" / "registry" / "current" / f"{argus_id}.json").read_text())
            standalone = json.loads((ROOT / fixture_path).read_text())["v2_candidate"]
            fresh = module.materialize_registry_procurement(current, standalone)
            self.assertEqual(committed[argus_id], fresh)

    def test_every_materialized_candidate_validates_and_relationship_targets_resolve(self):
        self.assertTrue(REHEARSAL.exists())
        registry_schema = json.loads(REGISTRY_SCHEMA.read_text())
        domain_schema = json.loads(DOMAIN_SCHEMA.read_text())
        rehearsal = json.loads(REHEARSAL.read_text())
        index = json.loads(CURRENT_INDEX.read_text())["records"]

        for record in rehearsal["materialized_current_records"]:
            Draft202012Validator(registry_schema).validate(record)
            Draft202012Validator(domain_schema).validate(record["domain_payload"]["data"])
            for relation in record.get("relationships", []):
                self.assertIn(relation["target_argus_id"], index)

    def test_rollback_snapshot_hashes_match_current_source_bytes(self):
        self.assertTrue(REHEARSAL.exists())
        rehearsal = json.loads(REHEARSAL.read_text())
        fixture_map = json.loads(FIXTURE_MAP.read_text())
        snapshots = rehearsal["source_snapshots"]
        self.assertEqual(set(snapshots), set(fixture_map))
        for argus_id in fixture_map:
            data = (ROOT / "data" / "registry" / "current" / f"{argus_id}.json").read_bytes()
            self.assertEqual(snapshots[argus_id]["sha256"], sha256_bytes(data))
            self.assertEqual(snapshots[argus_id]["bytes"], len(data))

    def test_historical_fixture_remains_separate_provenance_input(self):
        self.assertTrue(HISTORICAL.exists())
        self.assertTrue(REHEARSAL.exists())
        historical = json.loads(HISTORICAL.read_text())
        rehearsal = json.loads(REHEARSAL.read_text())
        self.assertEqual(rehearsal["historical_baseline_sha256"], historical["baseline_sha256"])
        self.assertEqual(rehearsal["historical_ids"], historical["source_procurement_ids"])
        self.assertTrue(rehearsal["historical_current_overlay_backfill_prohibited"])

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
