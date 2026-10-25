import hashlib
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "argus-intelligence.yaml"
MANIFEST = MANIFEST_PATH.read_text()
CORE = (ROOT / "spec" / "core.md").read_text()
ALIGNMENT = (ROOT / "alignments" / "atlas-os.md").read_text()
RESULT_SCHEMA = json.loads((ROOT / "schemas" / "domain-result.schema.json").read_text())
HANDOFF_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "domain-context-handoff-v1.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "domain-handoff-receipt-v1.schema.json"
LEASE_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "execution-lease-v1.schema.json"
KEY_REGISTRY_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "signing-key-registry-v1.schema.json"
APPROVAL_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "approval-v1.schema.json"
SYNC_DESCRIPTOR_PATH = ROOT / "contracts" / "atlas" / "synchronization-compatibility.yaml"
CURRENT_INTEGRATION_PATH = ROOT / "contracts" / "atlas" / "current-integration.yaml"
SYNC_RECEIPT_SCHEMA_PATH = ROOT / "schemas" / "atlas-argus-sync-receipt.schema.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "contract-tests.yml"
CROSS_REPO_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "cross-repo-e2e.yml"
ATLAS_CANONICAL_COMMIT = "2972f272026d2cf41e5dd847eb939d3579d8520a"
ATLAS_LAST_VALIDATED_BASE_COMMIT = "95e78eb4f386c7434193014811ef8d2ce5254c30"


class AtlasDomainHandoffContract(unittest.TestCase):
    def test_current_manifest_uses_atlas_v3_provider_seam(self):
        manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertIn("version: 3.0.0-rc.2", MANIFEST)
        self.assertIn("release_channel: candidate", MANIFEST)
        self.assertEqual("contracts/atlas/current-integration.yaml", manifest["authority"]["atlas_current_integration"])
        self.assertEqual("tools/atlas_v3_provider.py", manifest["authority"]["atlas_v3_provider"])
        compatibility = manifest["atlas_compatibility"]
        self.assertEqual("3.0.2", compatibility["last_validated_base"])
        self.assertEqual(ATLAS_LAST_VALIDATED_BASE_COMMIT, compatibility["last_validated_base_commit"])
        self.assertEqual("chatgpt-plugin-bootstrap-v1.0.1", compatibility["last_validated_control_revision"])
        self.assertEqual("ATLAS", compatibility["activation_authority"])
        self.assertEqual("ATLAS", compatibility["next_step_authority"])
        self.assertEqual("ATLAS", compatibility["provider_return_target"])
        self.assertTrue(compatibility["explicit_user_approval_required"])
        self.assertTrue(compatibility["mission_control_first_required"])
        self.assertFalse(manifest["production_runtime"]["access_asia"]["atlas_change_required"])

    def test_legacy_signed_handoff_and_lease_contracts_remain_available(self):
        handoff_schema = json.loads(HANDOFF_SCHEMA_PATH.read_text())
        lease_schema = json.loads(LEASE_SCHEMA_PATH.read_text())
        manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
        legacy = manifest["atlas_compatibility"]["legacy_signed_transport"]
        self.assertEqual("backward_compatibility_only", legacy["status"])
        self.assertEqual("1.2.0", legacy["handoff_contract_version"])
        self.assertEqual("1.0.0", legacy["execution_lease_contract_version"])
        self.assertEqual("1.2.0", handoff_schema["properties"]["contract_version"]["const"])
        self.assertEqual("1.0.0", lease_schema["properties"]["contract_version"]["const"])

    def test_sync_descriptor_pins_exact_historical_atlas_stable(self):
        descriptor = json.loads(SYNC_DESCRIPTOR_PATH.read_text())["atlas_compatibility"]
        self.assertEqual("2.0.1", descriptor["atlas_version"])
        self.assertEqual("b8b8559c57eef5fbb97d914d924077ba20b1883d", descriptor["atlas_commit"])
        self.assertEqual("chatgpt-bootstrap-2026-10-19-r4", descriptor["control_revision"])
        self.assertEqual("1.2.0", descriptor["handoff_contract_version"])
        self.assertEqual("1.0.0", descriptor["execution_lease_contract_version"])
        self.assertEqual("1.0.0", descriptor["signing_key_registry_version"])
        self.assertEqual(8, len(descriptor["source_contracts"]))
        self.assertEqual(
            "62a5048f0c6d5a672e4321239596563ea169ebf593dbefda46e4c2d1d6368e64",
            descriptor["source_contracts"]["runtime"]["sha256"],
        )

    def test_pinned_legacy_local_contract_hashes_match_descriptor(self):
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

    def test_historical_alignment_remains_available_as_evidence(self):
        self.assertIn("ATLAS Domain Context → ARGUS Contextualize", ALIGNMENT)
        self.assertIn("schema-valid domain-context handoff", ALIGNMENT)
        self.assertIn("handoff_id", ALIGNMENT)
        self.assertIn("payload_sha256", ALIGNMENT)
        self.assertIn("reject mismatched", ALIGNMENT.lower())
        self.assertIn("one handoff and one return", CORE)

    def test_domain_result_remains_specialization_compatibility_contract(self):
        self.assertIn("governance_mode", RESULT_SCHEMA["required"])
        self.assertIn("upstream_handoff", RESULT_SCHEMA["properties"])
        conditional = RESULT_SCHEMA["allOf"][0]
        self.assertEqual("ATLAS_GOVERNED", conditional["if"]["properties"]["governance_mode"]["const"])
        self.assertIn("upstream_handoff", conditional["then"]["required"])
        receipt = RESULT_SCHEMA["properties"]["upstream_handoff"]
        self.assertEqual("1.2.0", receipt["properties"]["contract_version"]["const"])
        self.assertEqual("ARGUS", receipt["properties"]["consumer"]["const"])
        self.assertEqual("ACCEPTED", receipt["properties"]["status"]["const"])

    def test_standalone_mode_remains_declared_for_compatibility(self):
        modes = RESULT_SCHEMA["properties"]["governance_mode"]["enum"]
        self.assertIn("STANDALONE", modes)
        self.assertIn("ATLAS_GOVERNED", modes)

    def test_current_descriptor_and_legacy_transport_are_both_registered(self):
        manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertTrue(CURRENT_INTEGRATION_PATH.is_file())
        current = yaml.safe_load(CURRENT_INTEGRATION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(ATLAS_CANONICAL_COMMIT, current["atlas"]["commit"])
        self.assertEqual("derived_snapshot", current["contract_role"])
        self.assertEqual("2.0.0", current["canonical_source"]["contract_version"])
        self.assertEqual("MISSION_CONTROL_FIRST", current["contract"]["prompt_entry"])
        self.assertEqual("ATLAS", current["contract"]["next_step_authority"])
        self.assertEqual("backward_compatibility_only", current["legacy_transport"]["status"])
        self.assertEqual("contracts/atlas/synchronization-compatibility.yaml", manifest["authority"]["atlas_synchronization_compatibility"])
        self.assertEqual("tools/atlas_sync.py", manifest["authority"]["synchronization_runtime"])
        self.assertTrue(SYNC_RECEIPT_SCHEMA_PATH.is_file())
        self.assertEqual(7, len(manifest["master_registry"]["record_types"]))
        self.assertEqual("OPPORTUNITY", manifest["master_registry"]["primary_commercial_record_type"])

    def test_cross_repo_gate_targets_current_atlas_and_preserves_historical_proof_elsewhere(self):
        workflow = CROSS_REPO_WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("repository: gferris418/atlas-os", workflow)
        self.assertIn(f"ref: {ATLAS_CANONICAL_COMMIT}", workflow)
        self.assertNotIn("ATLAS_SSH_KEY", workflow)
        self.assertNotIn("ATLAS_READ_TOKEN", workflow)
        self.assertIn("python -m unittest discover -s tests/cross_repo -v", workflow)
        descriptor = json.loads(SYNC_DESCRIPTOR_PATH.read_text())["atlas_compatibility"]
        self.assertEqual("b8b8559c57eef5fbb97d914d924077ba20b1883d", descriptor["atlas_commit"])

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
        self.assertIn("cache-dependency-path:", workflow)
        self.assertIn("requirements-test.lock", workflow)
        self.assertIn("requirements-quality.txt", workflow)
        self.assertTrue((ROOT / "requirements-test.lock").is_file())
        self.assertTrue((ROOT / "requirements-quality.txt").is_file())


if __name__ == "__main__":
    unittest.main()
