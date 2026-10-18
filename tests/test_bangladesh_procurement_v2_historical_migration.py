import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data" / "registry" / "records.jsonl"
BASELINE = json.loads((ROOT / "data" / "registry" / "baseline.json").read_text())
SCHEMA = json.loads((ROOT / "schemas" / "bangladesh-procurement-v2.schema.json").read_text())
CONTRACT = ROOT / "profiles" / "bangladesh-procurement-v2-registry-legacy-migration.json"
TRANSFORMER = ROOT / "tools" / "bangladesh_procurement_v2_migrate.py"
REHEARSAL = ROOT / "tests" / "fixtures" / "bangladesh-v2" / "historical-baseline-rehearsal.json"
REPORT = ROOT / "docs" / "validation" / "bangladesh-procurement-v2-historical-migration-rehearsal.md"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()

EXPECTED_BASELINE_SHA = "a43cb9555f3c82a827d16508d4e3af9764f4445e99df44853895eb2d505bbc31"


def baseline_records():
    return [json.loads(line) for line in RECORDS.read_text().splitlines() if line.strip()]


def baseline_procurements():
    return [record for record in baseline_records() if record["record_type"] == "PROCUREMENT"]


def load_transformer():
    if not TRANSFORMER.exists():
        raise AssertionError("historical migration transformer does not exist")
    spec = importlib.util.spec_from_file_location("bd_v2_migrate", TRANSFORMER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BangladeshProcurementV2HistoricalMigration(unittest.TestCase):
    def test_historical_population_is_pinned_to_immutable_baseline(self):
        raw = RECORDS.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_BASELINE_SHA)
        self.assertEqual(BASELINE["records_jsonl_sha256"], EXPECTED_BASELINE_SHA)
        procurements = baseline_procurements()
        self.assertEqual(len(procurements), 1)
        self.assertEqual(procurements[0]["argus_id"], "PROC-BCG-LT001")

    def test_machine_migration_contract_accounts_for_every_baseline_field(self):
        self.assertTrue(CONTRACT.exists())
        contract = json.loads(CONTRACT.read_text())
        self.assertEqual(contract["status"], "REHEARSAL_ONLY")
        self.assertEqual(contract["target_standard"], "2.0.0-candidate")
        self.assertFalse(contract["live_registry_mutation"])
        rules = contract["field_rules"]
        record = baseline_procurements()[0]
        expected_paths = {key for key in record if key != "attributes"}
        expected_paths.update(f"attributes.{key}" for key in record["attributes"])
        self.assertEqual(set(rules), expected_paths)
        for path, rule in rules.items():
            self.assertIn(rule["action"], {"KEEP", "MAP", "PRESERVE_ONLY", "DROP_REDUNDANT"}, path)
            self.assertIn("rationale", rule, path)

    def test_contract_prohibits_unsafe_legacy_inferences(self):
        contract = json.loads(CONTRACT.read_text())
        rules = contract["field_rules"]
        for path in (
            "attributes.official_reference",
            "attributes.package_reference",
            "attributes.procurement_type",
            "attributes.currency",
            "status",
        ):
            self.assertEqual(rules[path]["action"], "PRESERVE_ONLY", path)
        prohibited = set(contract["prohibited_inferences"])
        for token in (
            "legacy_reference_to_typed_identifier",
            "standalone_currency_to_process_currency",
            "legacy_procurement_type_to_process_category",
            "stale_evidence_to_current_fact",
            "current_overlay_backfill_into_baseline_rehearsal",
        ):
            self.assertIn(token, prohibited)

    def test_transformer_is_pure_deterministic_and_schema_valid(self):
        module = load_transformer()
        source = baseline_procurements()[0]
        before = copy.deepcopy(source)
        first = module.transform_legacy_procurement(source)
        second = module.transform_legacy_procurement(source)
        self.assertEqual(source, before)
        self.assertEqual(first, second)
        Draft202012Validator(SCHEMA).validate(first)
        self.assertEqual(first["argus_id"], source["argus_id"])
        self.assertEqual(first["title"], source["canonical_name_or_title"])
        self.assertEqual(first["record_revision"], source["revision"])
        self.assertEqual(first["record_state"], "BASELINE_PROVENANCE")

    def test_transformer_preserves_safe_semantics_without_retyping_wd2(self):
        module = load_transformer()
        source = baseline_procurements()[0]
        result = module.transform_legacy_procurement(source)
        identifiers = result.get("identifiers", [])
        self.assertFalse(any(identifier["value"] == "WD-2" for identifier in identifiers))
        roles = {(x["party_id"], x["role"]) for x in result["party_role_links"]}
        self.assertIn(("ENT-BD-COAST-GUARD", "BUYER"), roles)
        self.assertIn(("ENT-BD-COAST-GUARD", "PROCURING_ENTITY"), roles)
        refs = {x["argus_id"] for x in result["related_record_refs"]}
        self.assertIn("ENT-BD-COAST-GUARD", refs)
        self.assertIn("PRJ-BCG-CPV-WD2", refs)
        self.assertEqual(result["items"][0]["quantity"], 4)
        self.assertEqual(result["items"][0]["unit"], "vessels")
        self.assertEqual(result["process"]["method_source_code"], "OSTETM")
        self.assertEqual(result["process"]["status_raw"], "Published_snapshot_unverified_current")
        self.assertNotIn("category", result["process"])
        self.assertNotIn("competition_scope", result["process"])
        self.assertNotIn("currency", result["process"])
        self.assertEqual(result["intelligence"]["material_unknowns"], source["attributes"]["material_unknowns"])

    def test_transformer_preserves_ambiguous_and_stale_evidence_as_observations(self):
        module = load_transformer()
        source = baseline_procurements()[0]
        result = module.transform_legacy_procurement(source)
        observations = result["observations"]
        by_path = {x["field_path"]: x for x in observations}
        for path in (
            "legacy.attributes.official_reference",
            "legacy.attributes.package_reference",
            "legacy.attributes.procurement_type",
            "legacy.attributes.currency",
            "legacy.attributes.funding_source_raw",
            "legacy.status",
            "legacy.aliases",
            "legacy.external_refs",
        ):
            self.assertIn(path, by_path)
        evidence_obs = [x for x in observations if x["field_path"].startswith("legacy.evidence_refs[")]
        self.assertEqual(len(evidence_obs), len(source["evidence_refs"]))
        self.assertTrue(all(x["condition"] == "STALE" for x in evidence_obs))
        self.assertTrue(all(x["claim_type"] == "UNKNOWN" for x in evidence_obs))

    def test_transformer_cannot_consult_current_overlay(self):
        self.assertTrue(TRANSFORMER.exists())
        source = TRANSFORMER.read_text()
        self.assertNotIn("current-index.json", source)
        self.assertNotIn("data/registry/current", source)
        self.assertNotIn("PROC-BCG-LT001.json", source)

    def test_historical_rehearsal_artifact_reconciles_every_baseline_procurement(self):
        self.assertTrue(REHEARSAL.exists())
        rehearsal = json.loads(REHEARSAL.read_text())
        self.assertEqual(rehearsal["baseline_sha256"], EXPECTED_BASELINE_SHA)
        self.assertEqual(rehearsal["source_procurement_count"], 1)
        self.assertEqual(rehearsal["output_procurement_count"], 1)
        self.assertEqual(rehearsal["source_argus_ids"], ["PROC-BCG-LT001"])
        self.assertEqual(rehearsal["output_argus_ids"], ["PROC-BCG-LT001"])
        self.assertFalse(rehearsal["live_registry_mutation"])
        self.assertEqual(rehearsal["preservation_assessment"]["material_information_loss"], 0)
        self.assertEqual(rehearsal["preservation_assessment"]["schema_validation"], "PASS")
        for payload in rehearsal["transformed_payloads"]:
            Draft202012Validator(SCHEMA).validate(payload)

    def test_report_defines_reversible_activation_gate_without_activating_v2(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text()
        for token in (
            "Historical baseline PROCUREMENT records: 1/1",
            EXPECTED_BASELINE_SHA,
            "Staging namespace",
            "Pre-activation snapshot",
            "Atomic activation boundary",
            "Rollback order",
            "Post-activation readback",
            "Material information loss: 0",
            "v1.3 remains active",
            "NO-GO for live activation",
            "data/registry/records.jsonl remains immutable",
        ):
            self.assertIn(token, text)

    def test_active_write_authority_is_unchanged(self):
        self.assertIn(
            "bangladesh_procurement_standard: profiles/bangladesh-canonical-procurement-standard-v1.3.yaml",
            MANIFEST,
        )


if __name__ == "__main__":
    unittest.main()
