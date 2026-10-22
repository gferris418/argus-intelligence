import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "atlas" / "argus-activation-v1.json"


class ArgusActivationContractTests(unittest.TestCase):
    def _contract(self) -> dict:
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_atlas_owns_governance_analysis_and_final_delivery(self) -> None:
        contract = self._contract()
        ownership = contract["ownership"]
        self.assertEqual("ATLAS_OS", contract["activation_authority"])
        for field in (
            "mission_control",
            "control_plane",
            "collection_need_gate",
            "planning",
            "permissions",
            "approvals",
            "canonical_taxonomy_authority",
            "strategic_analysis",
            "forecasting_and_scenarios",
            "opportunity_qualification",
            "access_asia_pursuit_decisions",
            "assurance_and_verification",
            "persistence_authorization",
            "observability",
            "dashboard_projection",
            "final_delivery",
        ):
            with self.subTest(field=field):
                self.assertEqual("ATLAS_OS", ownership[field])

    def test_activation_uses_collection_need_gate_and_collection_capability(self) -> None:
        contract = self._contract()
        self.assertEqual("3.1.0", contract["contract_version"])
        self.assertEqual("atlas_collection_need_gate", contract["activation_mechanism"])
        self.assertEqual("intelligence_collection", contract["required_capability"])
        self.assertEqual(["ARGUS_COLLECTION", "HYBRID"], contract["required_collection_modes"])
        self.assertTrue(contract["task_route_independent"])
        self.assertEqual(["READY", "PARTIAL"], contract["accepted_handoff_states"])
        self.assertEqual("REJECT_DEPENDENT_EXECUTION", contract["blocked_handoff_behavior"])
        self.assertTrue(contract["requires_atlas_domain_context_handoff"])

    def test_contract_declares_collection_types_and_depths(self) -> None:
        contract = self._contract()
        self.assertIn("TARGET_PROFILE", contract["supported_collection_types"])
        self.assertIn("PROCUREMENT_PLAN", contract["supported_collection_types"])
        self.assertIn("OPPORTUNITY_DISCOVERY", contract["supported_collection_types"])
        self.assertIn("MONITORING", contract["supported_collection_types"])
        self.assertEqual(
            ["C0_IDENTITY", "C1_PROFILE", "C2_DOSSIER", "C3_OPPORTUNITY", "C4_MONITOR"],
            contract["collection_depths"],
        )

    def test_argus_owns_collection_functions_not_final_analysis(self) -> None:
        contract = self._contract()
        ownership = contract["ownership"]
        for field in (
            "institutional_hierarchy_resolution",
            "internal_registry_reconciliation",
            "opportunity_identity_resolution",
            "official_procurement_collection",
            "authorized_internal_customer_intelligence_collection",
            "research_frontier_ordering",
            "adaptive_360_collection",
            "source_discovery",
            "acquisition",
            "extraction",
            "normalization",
            "entity_resolution",
            "deduplication",
            "collection_classification_suggestions",
            "corroboration",
            "gap_and_conflict_detection",
            "collection_packaging",
        ):
            with self.subTest(field=field):
                self.assertEqual("ARGUS", ownership[field])

    def test_contract_governs_one_bounded_autonomous_mission(self) -> None:
        contract = self._contract()
        self.assertEqual("ONE_HANDOFF_ONE_RETURN", contract["mission_handoff_pattern"])
        self.assertEqual("BOUNDED_AUTONOMOUS", contract["autonomy_mode"])
        self.assertEqual(
            [
                "RESOLVE_INSTITUTIONAL_HIERARCHY",
                "CHECK_INTERNAL_CANONICAL_REGISTRY",
                "RECONCILE_OPPORTUNITY_IDENTITY",
                "CHECK_OFFICIAL_PROCUREMENT_SOURCES",
                "CHECK_INTERNAL_CUSTOMER_INTELLIGENCE",
                "BUILD_RESEARCH_FRONTIER",
                "EXECUTE_ADAPTIVE_360_COLLECTION",
            ],
            contract["startup_sequence"],
        )
        self.assertEqual(["EXACT", "HIGH_CONFIDENCE_MATCH"], contract["identity_resolution"]["auto_reuse"])
        self.assertEqual(["DISTINCT"], contract["identity_resolution"]["auto_new_candidate"])
        self.assertEqual(["PROBABLE_MATCH", "UNRESOLVED"], contract["identity_resolution"]["user_confirmation"])
        self.assertEqual(
            ["MATERIAL_SCOPE_CHANGE", "AUTHORIZATION_REQUIRED", "POLICY_OR_SECURITY_CONFLICT", "MATERIAL_AMBIGUITY"],
            contract["escalation_conditions"],
        )
        self.assertTrue(contract["follow_evidence_leads_without_callback"])
        self.assertTrue(contract["parallel_safe_reads"])
        self.assertEqual("TRANSIENT_ONLY", contract["mission_context"])
        self.assertEqual("PROPOSE_BATCH_THEN_ATLAS_COMMIT", contract["persistence_mode"])

    def test_required_examples_encode_boundary(self) -> None:
        examples = self._contract()["representative_routing_examples"]
        self.assertEqual("ATLAS_DIRECT", examples["Bangladesh Bank foreign exchange policy"])
        self.assertEqual("ARGUS_COLLECTION", examples["ST Engineering"])
        self.assertEqual("ARGUS_COLLECTION", examples["coastal patrol vessel for Bangladesh Coast Guard"])
        self.assertEqual("ARGUS_COLLECTION", examples["seed cum cleaner for BADC"])
        self.assertEqual("ARGUS_COLLECTION", examples["share the annual procurement plan of Bangladesh Navy"])
        self.assertEqual("HYBRID", examples["compare ST Engineering and L3Harris for Bangladesh opportunities"])

    def test_argus_has_no_keyword_or_background_auto_activation(self) -> None:
        contract = self._contract()
        self.assertFalse(contract["keyword_activation"])
        self.assertFalse(contract["background_activation"])
        self.assertIn("generic factual explanation", contract["non_triggers"])
        self.assertIn("policy or regulation explanation without a collection mission", contract["non_triggers"])


if __name__ == "__main__":
    unittest.main()
