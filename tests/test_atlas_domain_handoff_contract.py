import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()
CORE = (ROOT / "spec" / "core.md").read_text()
ALIGNMENT = (ROOT / "alignments" / "atlas-os.md").read_text()
RESULT_SCHEMA = json.loads((ROOT / "schemas" / "domain-result.schema.json").read_text())
HANDOFF_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "domain-context-handoff-v1.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "domain-handoff-receipt-v1.schema.json"
LEASE_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "execution-lease-v1.schema.json"
KEY_REGISTRY_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "signing-key-registry-v1.schema.json"
APPROVAL_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "approval-v1.schema.json"
SYNC_DESCRIPTOR_PATH = ROOT / "contracts" / "atlas" / "synchronization-compatibility.yaml"
SYNC_RECEIPT_SCHEMA_PATH = ROOT / "schemas" / "atlas-argus-sync-receipt.schema.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "contract-tests.yml"
CROSS_REPO_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "cross-repo-e2e.yml"


class AtlasDomainHandoffContract(unittest.TestCase):
    def test_argus_pins_the_atlas_handoff_and_lease_contracts(self):
        handoff_schema = json.loads(HANDOFF_SCHEMA_PATH.read_text())
        lease_schema = json.loads(LEASE_SCHEMA_PATH.read_text())
        self.assertIn("version: 2.0.1-rc.1", MANIFEST)
        self.assertIn("release_channel: candidate", MANIFEST)
        self.assertIn("atlas_domain_context_contract_version: 1.2.0", MANIFEST)
        self.assertIn("atlas_execution_lease_contract_version: 1.0.0", MANIFEST)
        self.assertIn("atlas_signing_key_registry_contract_version: 1.0.0", MANIFEST)
        self.assertIn("execution_lease_required_in_access_asia_production: true", MANIFEST)
        self.assertEqual("1.2.0", handoff_schema["properties"]["contract_version"]["const"])
        self.assertEqual("1.0.0", lease_schema["properties"]["contract_version"]["const"])

    def test_sync_descriptor_pins_exact_atlas_candidate(self):
        descriptor = json.loads(SYNC_DESCRIPTOR_PATH.read_text())["atlas_compatibility"]
        self.assertEqual("2.0.1-rc.1", descriptor["atlas_version"])
        self.assertEqual("53ae8723fe2939898015810a821f61a93ed8b9c8", descriptor["atlas_commit"])
        self.assertEqual("chatgpt-bootstrap-2026-10-19-r4", descriptor["control_revision"])
        self.assertEqual("1.2.0", descriptor["handoff_contract_version"])
        self.assertEqual("1.0.0", descriptor["execution_lease_contract_version"])
        self.assertEqual("1.0.0", descriptor["signing_key_registry_version"])
        self.assertEqual(8, len(descriptor["source_contracts"]))
        self.assertEqual(
            "62a5048f0c6d5a672e4321239596563ea169ebf593dbefda46e4c2d1d6368e64",
            descriptor["source_contracts"]["runtime"]["sha256"],
        )

    def test_pinned_local_contract_hashes_match_descriptor(self):
        descriptor = json.loads(SYNC_DESCRIPTOR_PATH.read_text())["atlas_compatibility"]
        paths = {
            "domain_context_handoff": HANDOFF_SCHEMA_PATH,
            "domain_handoff_receipt": RECEIPT_SCHEMA_PATH,
            "execution_lease": LEASE_SCHEMA_PATH,
            "signing_key_registry": KEY_REGISTRY_SCHEMA_PATH,
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
        self.assertEqual("1.2.0", receipt["properties"]["contract_version"]["const"])
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
        self.assertIn("atlas_control_record_authenticity: detached_ed25519_lifecycle_governed_key_registry", MANIFEST)
        record_type_block = MANIFEST.split("record_types:", 1)[1].split(
            "logical_canonical_store:", 1
        )[0]
        self.assertEqual(7, sum(line.strip().startswith("- ") for line in record_type_block.splitlines()))
        self.assertTrue(SYNC_RECEIPT_SCHEMA_PATH.is_file())

    def test_cross_repo_gate_is_automatic_and_pins_exact_atlas_commit(self):
        workflow = CROSS_REPO_WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("repository: gferris418/atlas-os", workflow)
        self.assertIn("ref: 53ae8723fe2939898015810a821f61a93ed8b9c8", workflow)
        self.assertIn("ssh-key: ${{ secrets.ATLAS_SSH_KEY }}", workflow)
        self.assertNotIn("ATLAS_READ_TOKEN", workflow)
        self.assertIn("python -m unittest discover -s tests/cross_repo -v", workflow)

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
