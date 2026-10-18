import copy
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SCHEMA = ROOT / "registry" / "schema" / "argus-master-registry-v0.3.0-candidate.json"
DOMAIN_SCHEMA = ROOT / "schemas" / "bangladesh-procurement-v2-domain.schema.json"
STANDALONE_SCHEMA = ROOT / "schemas" / "bangladesh-procurement-v2.schema.json"
TOOL = ROOT / "tools" / "bangladesh_procurement_v2_materialize.py"
CURRENT = ROOT / "data" / "registry" / "current" / "PROC-DAE-1318662.json"
FIXTURE = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "dae-low-lift-pump.json"
MANIFEST = ROOT / "argus-intelligence.yaml"

FORBIDDEN_DOMAIN_FIELDS = {
    "argus_id",
    "title",
    "record_state",
    "record_revision",
    "related_record_refs",
    "observations",
}


def load_tool():
    if not TOOL.exists():
        raise AssertionError(f"missing materializer: {TOOL}")
    spec = importlib.util.spec_from_file_location("bd_v2_materialize", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BangladeshProcurementV2RegistryEnvelope(unittest.TestCase):
    def test_candidate_schemas_exist_and_are_draft_2020_12(self):
        self.assertTrue(REGISTRY_SCHEMA.exists())
        self.assertTrue(DOMAIN_SCHEMA.exists())
        registry = json.loads(REGISTRY_SCHEMA.read_text())
        domain = json.loads(DOMAIN_SCHEMA.read_text())
        self.assertEqual(registry["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(domain["$schema"], "https://json-schema.org/draft/2020-12/schema")
        Draft202012Validator.check_schema(registry)
        Draft202012Validator.check_schema(domain)

    def test_domain_projection_has_no_envelope_owned_fields(self):
        self.assertTrue(DOMAIN_SCHEMA.exists())
        domain = json.loads(DOMAIN_SCHEMA.read_text())
        props = set(domain["properties"])
        self.assertTrue(FORBIDDEN_DOMAIN_FIELDS.isdisjoint(props))
        self.assertFalse(domain.get("additionalProperties", True))
        for required in FORBIDDEN_DOMAIN_FIELDS:
            self.assertNotIn(required, domain.get("required", []))

    def test_registry_candidate_is_backward_compatible_and_composed(self):
        self.assertTrue(REGISTRY_SCHEMA.exists())
        schema = json.loads(REGISTRY_SCHEMA.read_text())
        self.assertEqual(schema["document_id"], "ARGUS-SCHEMA-REG-001")
        self.assertEqual(schema["version"], "0.3.0-candidate")
        self.assertEqual(schema["properties"]["schema_version"]["enum"], ["0.2.0", "0.2.1", "0.3.0"])
        self.assertIn("domain_payload", schema["properties"])
        self.assertIn("observations", schema["properties"])

        legacy = json.loads(CURRENT.read_text())
        Draft202012Validator(schema).validate(legacy)

    def test_materializer_is_pure_deterministic_and_enforces_identity(self):
        module = load_tool()
        current = json.loads(CURRENT.read_text())
        standalone = json.loads(FIXTURE.read_text())["v2_candidate"]
        before_current = copy.deepcopy(current)
        before_standalone = copy.deepcopy(standalone)

        first = module.materialize_registry_procurement(current, standalone)
        second = module.materialize_registry_procurement(current, standalone)
        self.assertEqual(first, second)
        self.assertEqual(current, before_current)
        self.assertEqual(standalone, before_standalone)

        self.assertEqual(first["schema_version"], "0.3.0")
        self.assertEqual(first["argus_id"], current["argus_id"])
        self.assertEqual(first["canonical_name_or_title"], current["canonical_name_or_title"])
        self.assertEqual(first["revision"], current["revision"])
        self.assertNotIn("attributes", first)
        self.assertEqual(first["domain_payload"]["profile"], "BANGLADESH_PROCUREMENT")
        self.assertEqual(first["domain_payload"]["version"], "2.0.0-candidate")
        self.assertTrue(FORBIDDEN_DOMAIN_FIELDS.isdisjoint(first["domain_payload"]["data"]))
        self.assertEqual(first["observations"], standalone.get("observations", []))
        self.assertEqual(first["evidence_refs"], current["evidence_refs"])
        self.assertEqual(first["external_refs"], current["external_refs"])

        materialized_pairs = {(r["target_argus_id"], r["relation_type"]) for r in first["relationships"]}
        current_pairs = {(r["target_argus_id"], r["relation_type"]) for r in current["relationships"]}
        v2_pairs = {(r["argus_id"], r["relation_type"]) for r in standalone.get("related_record_refs", [])}
        self.assertTrue(current_pairs.issubset(materialized_pairs))
        self.assertTrue(v2_pairs.issubset(materialized_pairs))
        relationship_targets = {r["target_argus_id"] for r in first["relationships"]}
        self.assertTrue(relationship_targets.issubset(set(first["related_argus_ids"])))

        bad_id = copy.deepcopy(standalone)
        bad_id["argus_id"] = "PROC-WRONG"
        with self.assertRaises(ValueError):
            module.materialize_registry_procurement(current, bad_id)

        bad_title = copy.deepcopy(standalone)
        bad_title["title"] = "Different title"
        with self.assertRaises(ValueError):
            module.materialize_registry_procurement(current, bad_title)

        bad_revision = copy.deepcopy(standalone)
        bad_revision["record_revision"] = current["revision"] + 1
        with self.assertRaises(ValueError):
            module.materialize_registry_procurement(current, bad_revision)

    def test_materialized_record_validates_and_reader_supports_both_shapes(self):
        module = load_tool()
        registry_schema = json.loads(REGISTRY_SCHEMA.read_text())
        domain_schema = json.loads(DOMAIN_SCHEMA.read_text())
        current = json.loads(CURRENT.read_text())
        standalone = json.loads(FIXTURE.read_text())["v2_candidate"]
        materialized = module.materialize_registry_procurement(current, standalone)

        Draft202012Validator(registry_schema).validate(materialized)
        Draft202012Validator(domain_schema).validate(materialized["domain_payload"]["data"])

        legacy_view = module.read_procurement_semantics(current)
        self.assertEqual(legacy_view["shape"], "LEGACY_REGISTRY_V0_2")
        self.assertEqual(legacy_view["argus_id"], current["argus_id"])
        self.assertEqual(legacy_view["data"], current["attributes"])

        v2_view = module.read_procurement_semantics(materialized)
        self.assertEqual(v2_view["shape"], "COMPOSED_REGISTRY_V0_3")
        self.assertEqual(v2_view["argus_id"], materialized["argus_id"])
        self.assertEqual(v2_view["data"], materialized["domain_payload"]["data"])
        self.assertEqual(v2_view["observations"], materialized["observations"])

    def test_v1_3_production_authority_remains_unchanged(self):
        text = MANIFEST.read_text()
        self.assertIn("bangladesh-canonical-procurement-standard-v1.3.yaml", text)
        self.assertNotIn("active_bangladesh_procurement_standard: 2.0.0", text)


if __name__ == "__main__":
    unittest.main()
