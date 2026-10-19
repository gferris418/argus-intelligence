import json
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()
CORE = (ROOT / "spec" / "core.md").read_text()
ALIGNMENT = (ROOT / "alignments" / "atlas-os.md").read_text()
RESULT_SCHEMA = json.loads((ROOT / "schemas" / "domain-result.schema.json").read_text())
HANDOFF_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "domain-context-handoff-v1.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "domain-handoff-receipt-v1.schema.json"
APPROVAL_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "approval-v1.schema.json"
SYNC_DESCRIPTOR_PATH = ROOT / "contracts" / "atlas" / "synchronization-compatibility.yaml"
SYNC_RECEIPT_SCHEMA_PATH = ROOT / "schemas" / "atlas-argus-sync-receipt.schema.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "contract-tests.yml"
SYNC_VALIDATION_PATH = ROOT / "docs" / "validation" / "atlas-argus-synchronization-v1.md"


class AtlasDomainHandoffContract(unittest.TestCase):
    def test_sync_validation_records_remote_exact_head_ci(self):
        validation = SYNC_VALIDATION_PATH.read_text(encoding="utf-8")
        self.assertIn("**Status:** REMOTE_CI_PASS", validation)
        self.assertIn("2269c961d2fa1f7df648f6b7f8cc2d223b53cb1f", validation)
        self.assertIn("39157293626", validation)
        self.assertNotIn("remote exact-head CI: **pending push**", validation)

    def test_argus_pins_the_atlas_handoff_contract(self):
        schema = json.loads(HANDOFF_SCHEMA_PATH.read_text())
        self.assertIn("atlas_domain_context_contract_version: 1.1.0", MANIFEST)
        self.assertIn("atlas_domain_context_contract_path: contracts/atlas/domain-context-handoff-v1.schema.json", MANIFEST)
        self.assertEqual("1.1.0", schema["properties"]["contract_version"]["const"])

    def test_sync_descriptor_pins_exact_atlas_baseline(self):
        descriptor = json.loads(SYNC_DESCRIPTOR_PATH.read_text())["atlas_compatibility"]
        self.assertEqual("2.0.0", descriptor["atlas_version"])
        self.assertEqual("a533d092fb35f5c048a96f46c0201d5ce37871c7", descriptor["atlas_commit"])
        self.assertEqual("chatgpt-bootstrap-2026-10-19-r4", descriptor["control_revision"])
        self.assertEqual("1.1.0", descriptor["handoff_contract_version"])
        self.assertEqual(6, len(descriptor["source_contracts"]))
        self.assertEqual(
            "62a5048f0c6d5a672e4321239596563ea169ebf593dbefda46e4c2d1d6368e64",
            descriptor["source_contracts"]["runtime"]["sha256"],
        )

    def test_pinned_local_contract_hashes_match_descriptor(self):
        descriptor = json.loads(SYNC_DESCRIPTOR_PATH.read_text())["atlas_compatibility"]
        paths = {
            "domain_context_handoff": HANDOFF_SCHEMA_PATH,
            "domain_handoff_receipt": RECEIPT_SCHEMA_PATH,
            "approval": APPROVAL_SCHEMA_PATH,
        }
        for name, path in paths.items():
            with self.subTest(name=name):
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(descriptor["source_contracts"][name]["sha256"], actual)

    def test_sync_descriptor_contains_no_placeholder_hashes(self):
        descriptor = json.loads(SYNC_DESCRIPTOR_PATH.read_text())["atlas_compatibility"]
        for name, source in descriptor["source_contracts"].items():
            with self.subTest(name=name):
                self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")
                self.assertNotEqual("0" * 64, source["sha256"])
                self.assertNotIn("<", source["sha256"])

    def test_contextualize_is_first_argus_domain_operation(self):
        self.assertIn("Contextualize → Discover → Extract → Resolve → Reconcile", CORE)
        self.assertIn("ATLAS Domain Context", CORE)
        self.assertIn("must not redefine ATLAS taxonomy or standards conclusions", CORE)

    def test_alignment_requires_validated_handoff_before_argus_execution(self):
        self.assertIn("ATLAS Domain Context → ARGUS Contextualize", ALIGNMENT)
        self.assertIn("schema-valid domain-context handoff", ALIGNMENT)
        self.assertIn("handoff_id", ALIGNMENT)
        self.assertIn("payload_sha256", ALIGNMENT)
        self.assertIn("reject mismatched", ALIGNMENT.lower())

    def test_domain_result_requires_correlation_in_atlas_governed_mode(self):
        self.assertIn("governance_mode", RESULT_SCHEMA["required"])
        self.assertIn("upstream_handoff", RESULT_SCHEMA["properties"])
        conditional = RESULT_SCHEMA["allOf"][0]
        self.assertEqual("ATLAS_GOVERNED", conditional["if"]["properties"]["governance_mode"]["const"])
        self.assertIn("upstream_handoff", conditional["then"]["required"])
        receipt = RESULT_SCHEMA["properties"]["upstream_handoff"]
        self.assertEqual("ARGUS", receipt["properties"]["consumer"]["const"])
        self.assertEqual("ACCEPTED", receipt["properties"]["status"]["const"])

    def test_standalone_mode_remains_declared(self):
        modes = RESULT_SCHEMA["properties"]["governance_mode"]["enum"]
        self.assertIn("STANDALONE", modes)
        self.assertIn("ATLAS_GOVERNED", modes)

    def test_manifest_declares_sync_runtime_without_changing_production_authority(self):
        self.assertIn(
            "atlas_synchronization_compatibility: contracts/atlas/synchronization-compatibility.yaml",
            MANIFEST,
        )
        self.assertIn(
            "atlas_synchronization_receipt_schema: schemas/atlas-argus-sync-receipt.schema.json",
            MANIFEST,
        )
        self.assertIn("synchronization_runtime: tools/atlas_sync.py", MANIFEST)
        self.assertIn("analysis_runtime: tools/argus_runtime.py", MANIFEST)
        self.assertIn("bangladesh_procurement_standard_version: 1.3.0", MANIFEST)
        self.assertIn("atlas_change_required: false", MANIFEST)
        self.assertIn("standalone_argus: false", MANIFEST)
        record_type_block = MANIFEST.split("record_types:", 1)[1].split(
            "logical_canonical_store:", 1
        )[0]
        self.assertEqual(7, sum(line.strip().startswith("- ") for line in record_type_block.splitlines()))
        self.assertTrue(SYNC_RECEIPT_SCHEMA_PATH.is_file())

    def test_ci_uses_immutable_actions_hash_locked_install_and_audit(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertNotIn("actions/checkout@v", workflow)
        self.assertNotIn("actions/setup-python@v", workflow)
        self.assertIn(
            "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0",
            workflow,
        )
        self.assertIn(
            "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6.3.0",
            workflow,
        )
        self.assertIn("pip install --require-hashes", workflow)
        self.assertIn("gh-action-pip-audit@", workflow)
        self.assertIn("cache-dependency-path: requirements-test.lock", workflow)
        self.assertTrue((ROOT / "requirements-test.lock").is_file())


if __name__ == "__main__":
    unittest.main()
