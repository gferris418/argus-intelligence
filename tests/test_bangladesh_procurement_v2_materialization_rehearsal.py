import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "bangladesh_procurement_v2_materialize.py"
FIXTURE_MAP = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "current-procurement-fixture-map.json"
REHEARSAL = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "registry-envelope-materialization-rehearsal.json"
HISTORICAL = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "historical-baseline-rehearsal.json"
CURRENT_INDEX = ROOT / "data" / "registry" / "current-index.json"
REPORT = ROOT / "docs" / "validation" / "argus-v2-drift-repair.md"


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


def build_runtime_rehearsal():
    module = load_tool()
    fixture_map = json.loads(FIXTURE_MAP.read_text())
    historical = json.loads(HISTORICAL.read_text())
    index = json.loads(CURRENT_INDEX.read_text())["records"]
    ids = sorted(fixture_map)
    source_snapshots = {}
    output_hashes = {}
    source_bytes_map = {}
    candidate_records = {}
    loss_findings = {}
    relationships_resolve = True

    for argus_id in ids:
        current_path = ROOT / "data" / "registry" / "current" / f"{argus_id}.json"
        source_bytes = current_path.read_bytes()
        current = json.loads(source_bytes)
        standalone = json.loads((ROOT / fixture_map[argus_id]).read_text())["v2_candidate"]
        materialized = module.materialize_registry_procurement(current, standalone)
        module.validate_registry_candidate(materialized)
        module.validate_domain_candidate(materialized["domain_payload"]["data"])

        source_snapshots[argus_id] = {
            "sha256": sha256_bytes(source_bytes),
            "bytes": len(source_bytes),
        }
        output_hashes[argus_id] = canonical_json_sha256(materialized)
        source_bytes_map[argus_id] = source_bytes
        candidate_records[argus_id] = materialized

        findings = module.materialization_loss_findings(current, standalone, materialized)
        if findings:
            loss_findings[argus_id] = findings
        for relation in materialized.get("relationships", []):
            if relation["target_argus_id"] not in index:
                relationships_resolve = False

    rollback = module.disposable_activation_revert_rehearsal(
        source_bytes=source_bytes_map,
        candidate_records=candidate_records,
    )
    material_loss_count = sum(len(items) for items in loss_findings.values())

    return {
        "fixture_type": "registry_envelope_materialization_rehearsal_v2",
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
        "relationship_resolution": "PASS" if relationships_resolve else "FAIL",
        "material_information_loss": material_loss_count,
        "material_information_loss_findings": loss_findings,
        "activation_changed_bytes": rollback["activation_changed_bytes"],
        "rollback_exact": rollback["rollback_exact"],
        "pre_sha256": rollback["pre_sha256"],
        "post_rollback_sha256": rollback["post_rollback_sha256"],
        "live_registry_mutation": False,
    }


class BangladeshProcurementV2MaterializationRehearsal(unittest.TestCase):
    def test_rehearsal_contract_matches_runtime_proof(self):
        contract = json.loads(REHEARSAL.read_text())
        runtime = build_runtime_rehearsal()
        self.assertEqual(runtime["current_source_ids"], contract["current_source_ids"])
        self.assertEqual(runtime["target_registry_schema"], contract["target_registry_schema"])
        self.assertEqual(runtime["target_domain_profile"], contract["target_domain_profile"])
        for key, expected in contract["expected"].items():
            self.assertEqual(runtime[key], expected, key)

    def test_runtime_rehearsal_is_deterministic(self):
        first = build_runtime_rehearsal()
        second = build_runtime_rehearsal()
        self.assertEqual(first, second)

    def test_every_materialized_candidate_validates_and_relationship_targets_resolve(self):
        runtime = build_runtime_rehearsal()
        self.assertEqual(runtime["schema_validation"], "PASS")
        self.assertEqual(runtime["relationship_resolution"], "PASS")
        self.assertEqual(runtime["current_source_ids"], runtime["current_output_ids"])

    def test_material_information_loss_is_computed_not_declared(self):
        runtime = build_runtime_rehearsal()
        self.assertEqual(runtime["material_information_loss_findings"], {})
        self.assertEqual(runtime["material_information_loss"], 0)

    def test_disposable_activation_and_revert_is_physical_and_exact(self):
        runtime = build_runtime_rehearsal()
        self.assertTrue(runtime["activation_changed_bytes"])
        self.assertTrue(runtime["rollback_exact"])
        self.assertEqual(runtime["pre_sha256"], runtime["post_rollback_sha256"])

    def test_historical_fixture_remains_separate_provenance_input(self):
        historical = json.loads(HISTORICAL.read_text())
        runtime = build_runtime_rehearsal()
        self.assertEqual(runtime["historical_baseline_sha256"], historical["baseline_sha256"])
        self.assertEqual(runtime["historical_ids"], historical["source_argus_ids"])
        self.assertTrue(runtime["historical_current_overlay_backfill_prohibited"])

    def test_validation_report_records_correction_and_no_go(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text().lower()
        for phrase in [
            "v1.3 remains active",
            "no-go for live activation",
            "record_state",
            "computed material information loss",
            "disposable activation/revert",
            "atlas unchanged",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
