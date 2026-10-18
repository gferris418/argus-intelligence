import copy
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "bangladesh_procurement_v2_materialize.py"
CURRENT = ROOT / "data" / "registry" / "current" / "PROC-DAE-1318662.json"
FIXTURE = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "dae-low-lift-pump.json"


def load_tool():
    spec = importlib.util.spec_from_file_location("bd_v2_materialize", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_inputs():
    current = json.loads(CURRENT.read_text())
    standalone = json.loads(FIXTURE.read_text())["v2_candidate"]
    return current, standalone


class ArgusV2DriftRepair(unittest.TestCase):
    def test_v03_procurement_uses_record_state_not_legacy_status(self):
        module = load_tool()
        current, standalone = load_inputs()
        materialized = module.materialize_registry_procurement(current, standalone)
        self.assertEqual(materialized["record_state"], standalone["record_state"])
        self.assertNotIn("status", materialized)
        semantic = module.read_procurement_semantics(materialized)
        self.assertEqual(semantic["record_state"], standalone["record_state"])
        self.assertNotEqual(current["status"], standalone["record_state"])

    def test_v03_non_procurement_is_rejected_until_designed(self):
        module = load_tool()
        record = {
            "schema_version": "0.3.0",
            "argus_id": "ENT-TEST",
            "record_type": "ENTITY",
            "canonical_name_or_title": "Test Entity",
            "record_state": "CURRENT",
            "related_argus_ids": [],
            "relationships": [],
            "evidence_refs": [],
            "external_refs": [],
            "revision": 1,
            "created_at": "2026-10-18",
            "updated_at": "2026-10-18",
            "observations": [],
            "domain_payload": {
                "profile": "BANGLADESH_PROCUREMENT",
                "version": "2.0.0-candidate",
                "data": {},
            },
        }
        with self.assertRaises((ValidationError, ValueError)):
            module.validate_registry_candidate(record)

    def test_domain_projection_is_deeply_typed(self):
        module = load_tool()
        current, standalone = load_inputs()
        projected = module.materialize_registry_procurement(current, standalone)["domain_payload"]["data"]
        broken = copy.deepcopy(projected)
        self.assertTrue(broken.get("identifiers"))
        broken["identifiers"][0].pop("scheme", None)
        with self.assertRaises(ValidationError):
            module.validate_domain_candidate(broken)

    def test_registry_schema_binds_domain_payload_deeply(self):
        module = load_tool()
        current, standalone = load_inputs()
        materialized = module.materialize_registry_procurement(current, standalone)
        broken = copy.deepcopy(materialized)
        broken["domain_payload"]["data"]["identifiers"][0].pop("scheme", None)
        with self.assertRaises(ValidationError):
            module.validate_registry_candidate(broken)

    def test_relationship_cache_must_exactly_match_relationship_targets(self):
        module = load_tool()
        current, standalone = load_inputs()
        materialized = module.materialize_registry_procurement(current, standalone)
        expected = sorted({r["target_argus_id"] for r in materialized["relationships"]})
        self.assertEqual(sorted(materialized["related_argus_ids"]), expected)
        broken = copy.deepcopy(materialized)
        broken["related_argus_ids"].append("ENT-UNRELATED")
        with self.assertRaises((ValidationError, ValueError)):
            module.validate_registry_candidate(broken)

    def test_semantic_loss_is_computed_and_detects_removed_domain_field(self):
        module = load_tool()
        current, standalone = load_inputs()
        materialized = module.materialize_registry_procurement(current, standalone)
        self.assertEqual(module.semantic_loss_findings(standalone, materialized), [])
        broken = copy.deepcopy(materialized)
        broken["domain_payload"]["data"].pop("process", None)
        findings = module.semantic_loss_findings(standalone, broken)
        self.assertTrue(findings)
        self.assertTrue(any("process" in finding for finding in findings))

    def test_disposable_activation_revert_physically_restores_exact_bytes(self):
        module = load_tool()
        current, standalone = load_inputs()
        materialized = module.materialize_registry_procurement(current, standalone)
        source_bytes = {current["argus_id"]: CURRENT.read_bytes()}
        result = module.disposable_activation_revert_rehearsal(
            source_bytes=source_bytes,
            candidate_records={current["argus_id"]: materialized},
        )
        self.assertTrue(result["activation_changed_bytes"])
        self.assertTrue(result["rollback_exact"])
        self.assertEqual(result["pre_sha256"], result["post_rollback_sha256"])
        self.assertEqual(result["pre_bytes"], result["post_rollback_bytes"])


if __name__ == "__main__":
    unittest.main()
