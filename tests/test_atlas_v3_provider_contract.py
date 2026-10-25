from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ATLAS_CANONICAL_COMMIT = "2972f272026d2cf41e5dd847eb939d3579d8520a"
ATLAS_LAST_VALIDATED_BASE_COMMIT = "95e78eb4f386c7434193014811ef8d2ce5254c30"


class AtlasV3ProviderContractTests(unittest.TestCase):
    def test_manifest_declares_current_atlas_v3_compatibility(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        self.assertEqual("3.0.0-rc.2", manifest["product"]["version"])
        self.assertEqual("3.0.0-rc.1", manifest["product"]["previous_version"])
        self.assertFalse(manifest["production_runtime"]["access_asia"]["atlas_change_required"])
        compatibility = manifest["atlas_compatibility"]
        self.assertEqual("3.0.2", compatibility["last_validated_base"])
        self.assertEqual(ATLAS_LAST_VALIDATED_BASE_COMMIT, compatibility["last_validated_base_commit"])
        self.assertEqual("chatgpt-plugin-bootstrap-v1.0.1", compatibility["last_validated_control_revision"])
        self.assertEqual("atlas_governed_360_business_intelligence_playbook", compatibility["relationship"])
        self.assertEqual("compatibility_execution_handle_not_underlying_tool_provider", compatibility["provider_field_semantics"])
        self.assertEqual("ATLAS", compatibility["activation_authority"])
        self.assertEqual("ATLAS", compatibility["next_step_authority"])
        self.assertTrue(compatibility["explicit_user_approval_required"])
        self.assertTrue(compatibility["mission_control_first_required"])
        self.assertEqual("contracts/atlas/current-integration.yaml", manifest["authority"]["atlas_current_integration"])

    def test_current_integration_descriptor_pins_immutable_atlas_release(self) -> None:
        descriptor = yaml.safe_load(
            (ROOT / "contracts" / "atlas" / "current-integration.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual("2.0.0", descriptor["version"])
        self.assertEqual("derived_snapshot", descriptor["contract_role"])
        self.assertEqual("ATLAS", descriptor["canonical_source"]["authority"])
        self.assertEqual("gferris418/atlas-os", descriptor["atlas"]["repository"])
        self.assertEqual("3.0.2", descriptor["atlas"]["version"])
        self.assertEqual(ATLAS_CANONICAL_COMMIT, descriptor["atlas"]["commit"])
        contract = descriptor["contract"]
        self.assertEqual("MISSION_CONTROL_FIRST", contract["prompt_entry"])
        self.assertEqual("every_user_prompt_while_atlas_active", contract["prompt_entry_scope"])
        self.assertEqual("intelligence_collection", contract["capability"])
        self.assertEqual("argus", contract["provider"])
        self.assertEqual("ARGUS_ACTIVATION", contract["approval_key"])
        self.assertEqual("ATLAS", contract["activation_authority"])
        self.assertEqual("ATLAS", contract["next_step_authority"])
        self.assertEqual("ATLAS", contract["provider_return_target"])
        self.assertTrue(contract["explicit_user_approval_required"])
        self.assertEqual("local_in_process_only", contract["plain_approval_scope"])
        self.assertEqual("backward_compatibility_only", descriptor["legacy_transport"]["status"])

    def test_provider_adapter_accepts_only_approved_atlas_argus_routes(self) -> None:
        module = importlib.import_module("tools.atlas_v3_provider")
        provider = module.ArgusProvider(lambda context: {"evidence": [], "collection_status": "COMPLETE"})
        atlas_result = {
            "task_id": "ATLAS-TEST-001",
            "state": "READY",
            "normalized_objective": "Build a supplier landscape for public infrastructure equipment",
            "domain_framing": {"jurisdiction": None, "risk_flags": []},
            "pre_execution_flow": ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
            "route": {
                "mechanism": "ARGUS",
                "capability": "intelligence_collection",
                "provider": "argus",
                "approval_required": True,
                "approval_status": "APPROVED",
                "reason": "test",
            },
            "next_step_authority": "ATLAS",
            "provider_return_target": "ATLAS",
        }
        outcome = provider.execute(module.ProviderEnvelope(atlas_result=atlas_result))
        self.assertEqual("ARGUS", outcome.provider)
        self.assertEqual("intelligence_collection", outcome.capability)
        self.assertEqual("ATLAS", outcome.return_target)
        self.assertEqual("ATLAS", outcome.next_step_authority)
        self.assertEqual("ATLAS-TEST-001", outcome.result["source_task_id"])
        self.assertEqual("COMPLETE", outcome.result["collection_status"])

        pending = {**atlas_result, "route": {**atlas_result["route"], "approval_status": "PENDING"}}
        with self.assertRaises(ValueError):
            provider.execute(module.ProviderEnvelope(atlas_result=pending))

    def test_provider_adapter_rejects_substring_route_spoofing(self) -> None:
        module = importlib.import_module("tools.atlas_v3_provider")
        provider = module.ArgusProvider(lambda context: {"evidence": [], "collection_status": "COMPLETE"})
        atlas_result = {
            "task_id": "ATLAS-TEST-002",
            "state": "READY",
            "normalized_objective": "Build a supplier landscape",
            "domain_framing": {},
            "pre_execution_flow": ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
            "route": {
                "mechanism": "ARGUS",
                "capability": "not_intelligence_collection",
                "provider": "untrusted-argus-proxy",
                "approval_required": True,
                "approval_status": "APPROVED",
            },
            "next_step_authority": "ATLAS",
            "provider_return_target": "ATLAS",
        }

        with self.assertRaises(ValueError):
            provider.execute(module.ProviderEnvelope(atlas_result=atlas_result))

    def test_active_alignment_and_cross_repo_ci_target_canonical_atlas_contract(self) -> None:
        alignment = yaml.safe_load((ROOT / "alignments" / "atlas-os-triage-v2.yaml").read_text(encoding="utf-8"))
        current = alignment["compatibility"]["current_validated_atlas"]
        self.assertEqual("3.0.2", current["version"])
        self.assertEqual(ATLAS_CANONICAL_COMMIT, current["commit"])
        self.assertEqual("2.0.0", current["execution_contract_version"])
        self.assertEqual("MISSION_CONTROL_FIRST", alignment["routing"]["prompt_entry"])
        self.assertEqual("every_user_prompt_while_atlas_active", alignment["routing"]["prompt_entry_scope"])
        self.assertEqual("atlas_governed_360_business_intelligence_playbook", alignment["relationship"])
        self.assertEqual(
            "compatibility_execution_handle_not_underlying_tool_provider",
            alignment["atlas_contract"]["provider_field_semantics"],
        )
        self.assertFalse(alignment["compatibility"]["current_change_requires_coordinated_atlas_candidate"])
        workflow = (ROOT / ".github" / "workflows" / "cross-repo-e2e.yml").read_text(encoding="utf-8")
        self.assertIn(f"ref: {ATLAS_CANONICAL_COMMIT}", workflow)


if __name__ == "__main__":
    unittest.main()
