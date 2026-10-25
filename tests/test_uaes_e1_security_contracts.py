from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "profiles" / "access-asia-operational-state-machines-v1.0.yaml"
SECURITY_PATH = ROOT / "profiles" / "access-asia-security-boundary-v1.0.yaml"
THREAT_PATH = ROOT / "profiles" / "access-asia-threat-register-v1.0.yaml"
CONTAINMENT_PATH = ROOT / "profiles" / "access-asia-containment-plan-v1.0.yaml"


class UaesE13SecurityContractTests(unittest.TestCase):
    def _load(self, path: Path) -> dict:
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_operational_state_machines_cover_every_status_bearing_store_object(self) -> None:
        contract = self._load(STATE_PATH)
        self.assertEqual("1.0.0", contract["version"])
        self.assertEqual("ACTIVE", contract["status"])

        machines = contract["stateful_objects"]
        expected = {
            "canonical_object",
            "relationship",
            "organization_role",
            "commercial_lineage",
            "financial_fact",
        }
        self.assertEqual(expected, set(machines))

        for name, machine in machines.items():
            with self.subTest(name=name):
                self.assertTrue(machine["states"])
                self.assertTrue(machine["initial_states"])
                self.assertTrue(machine["terminal_states"])
                self.assertIn("mutation_authority", machine)
                self.assertIn("failure_behavior", machine)
                self.assertIn("transitions", machine)
                for transition in machine["transitions"]:
                    self.assertIn(transition["from"], machine["states"])
                    self.assertIn(transition["to"], machine["states"])
                    self.assertTrue(transition["initiator"])
                    self.assertIn("preconditions", transition)
                    self.assertIn("side_effects", transition)
                    self.assertTrue(transition["failure_behavior"])

        self.assertEqual(
            {"CANDIDATE", "CURRENT", "ACTIVE", "DERIVED", "OBSERVED_LEGACY"},
            set(machines["canonical_object"]["states"]),
        )
        self.assertEqual(
            {"CURRENT", "DERIVED", "LEGACY"},
            set(machines["relationship"]["states"]),
        )

    def test_security_boundary_fails_closed_on_unverified_external_controls(self) -> None:
        security = self._load(SECURITY_PATH)
        self.assertEqual("ACTIVE", security["status"])
        self.assertFalse(security["execution"]["security_sandbox_claim"])
        self.assertEqual(
            "external_provider_evidence_required",
            security["oauth"]["enforcement_status"],
        )
        self.assertEqual(
            "external_provider_evidence_required",
            security["network"]["ssrf_enforcement_status"],
        )

        forbidden = set(security["secrets"]["forbidden_in"])
        self.assertTrue({"prompts", "skills", "source_control", "urls", "ordinary_logs"} <= forbidden)

        redacted = set(security["logging"]["never_log_raw"])
        self.assertTrue(
            {
                "passwords",
                "access_tokens",
                "refresh_tokens",
                "api_keys",
                "private_keys",
                "authentication_cookies",
                "unnecessary_sensitive_prompt_or_document_content",
                "protected_personal_financial_health_information",
            }
            <= redacted
        )

    def test_threat_register_covers_uaes_ap2_minimum_agent_threats(self) -> None:
        register = self._load(THREAT_PATH)
        threats = register["threats"]
        required_fields = {
            "id",
            "type",
            "asset",
            "trust_boundary",
            "actor",
            "entry_point",
            "abuse_case",
            "affected_contracts",
            "likelihood",
            "impact",
            "preventive_controls",
            "detective_controls",
            "containment",
            "owner",
            "verification_method",
            "residual_risk",
        }
        for threat in threats:
            self.assertTrue(required_fields <= set(threat))

        covered = {threat["type"] for threat in threats}
        required_types = {
            "direct_prompt_injection",
            "indirect_prompt_injection",
            "goal_hijacking",
            "tool_misuse",
            "excessive_agency",
            "identity_privilege_abuse",
            "memory_context_poisoning",
            "rag_vector_poisoning_or_leakage",
            "sensitive_information_disclosure",
            "unsafe_output_handling",
            "agent_impersonation_or_untrusted_peer",
            "delegated_authority_escalation",
            "malicious_plugin_skill_or_mcp_server",
            "supply_chain_compromise",
            "model_provider_compromise_or_failure",
            "resource_exhaustion_or_agent_loops",
            "data_exfiltration_through_tools_or_network",
            "approval_spoofing_or_replay",
            "task_artifact_idor_bola",
        }
        self.assertTrue(required_types <= covered)

    def test_containment_plan_has_authoritative_kill_actions_and_receipts(self) -> None:
        plan = self._load(CONTAINMENT_PATH)
        actions = plan["actions"]
        expected = {
            "disable_argus_activation",
            "revoke_connector_authorization",
            "suspend_canonical_persistence",
            "block_external_actions",
            "freeze_repository_writes",
        }
        self.assertTrue(expected <= set(actions))

        for action_id in expected:
            action = actions[action_id]
            self.assertTrue(action["authority"])
            self.assertTrue(action["trigger"])
            self.assertTrue(action["verification"])
            self.assertTrue(action["receipt_required"])
            self.assertTrue(action["restore_rule"])


if __name__ == "__main__":
    unittest.main()
