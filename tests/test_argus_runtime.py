from __future__ import annotations

import base64
import hashlib
import json
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.argus_runtime import (
    AnalysisEnvelope,
    AnalysisExecutionError,
    Argus,
    SyncValidationError,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "atlas-sync"


class ArgusRuntimeTests(unittest.TestCase):
    KEY_ID = "atlas-test-2026"

    def setUp(self) -> None:
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        clock = patch(
            "tools.atlas_sync._utc_now",
            return_value=datetime(2026, 10, 18, 8, 0, tzinfo=timezone.utc),
        )
        clock.start()
        self.addCleanup(clock.stop)

    def _handoff(self) -> dict:
        return json.loads((FIXTURES / "ready-handoff.json").read_text(encoding="utf-8"))

    def _attestation(self, record: dict) -> dict[str, str]:
        payload = json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        signature = self.private_key.sign(payload)
        return {
            "version": "1",
            "issuer": "ATLAS_OS",
            "algorithm": "Ed25519",
            "key_id": self.KEY_ID,
            "record_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "signature": base64.b64encode(signature).decode("ascii"),
        }

    def _trusted_key_registry(self) -> dict:
        return {
            "registry_version": "1.0.0",
            "issuer": "ATLAS_OS",
            "keys": [{
                "key_id": self.KEY_ID,
                "algorithm": "Ed25519",
                "public_key_base64": base64.b64encode(self.public_key).decode("ascii"),
                "activated_at": "2026-10-01T00:00:00Z",
                "expires_at": "2026-12-31T23:59:59Z",
                "status": "ACTIVE",
                "issuer": "ATLAS_OS",
                "allowed_record_classes": ["DOMAIN_CONTEXT_HANDOFF", "EXECUTION_LEASE", "APPROVAL"],
                "supersedes": None,
            }],
        }

    def _lease(self, handoff: dict) -> dict:
        return {
            "contract_version": "1.0.0",
            "execution_lease_id": "LEASE-ARGUS-RUNTIME-001",
            "handoff_id": handoff["handoff_id"],
            "handoff_payload_sha256": handoff["payload_sha256"],
            "source_task_id": handoff["source_task_id"],
            "source_plan_id": handoff["source_plan_id"],
            "source_work_unit_id": handoff["source_work_unit_id"],
            "producer": "ATLAS_OS",
            "consumer": "ARGUS",
            "issued_at": "2026-10-18T07:05:00Z",
            "lease_expires_at": "2026-10-22T07:05:00Z",
            "supersedes_lease_id": None,
        }

    def _mission(self, handoff: dict) -> dict:
        return {
            "mission_id": "COLLECTION-RUNTIME-001",
            "source_task_id": handoff["source_task_id"],
            "source_plan_id": handoff["source_plan_id"],
            "objective": "Collect evidence about the target.",
            "collection_mode": "ARGUS_COLLECTION",
            "collection_types": ["TARGET_PROFILE"],
            "targets": [{"name": "ST Engineering", "target_type": "organization", "aliases": []}],
            "collection_questions": ["What is the target profile?"],
            "jurisdictions": ["Singapore"],
            "time_horizon": "current",
            "freshness_requirement": "CURRENT",
            "collection_depth": "C2_DOSSIER",
            "source_priorities": ["official"],
            "source_exclusions": [],
            "risk_flags": [],
            "stopping_rule": "Stop when the target identity and material evidence are sufficiently corroborated.",
        }

    def _envelope(self, handoff: dict, *, mission: dict | None = None) -> AnalysisEnvelope:
        lease = self._lease(handoff)
        return AnalysisEnvelope(
            handoff=handoff,
            atlas_attestation=self._attestation(handoff),
            execution_lease=lease,
            execution_lease_attestation=self._attestation(lease),
            started_at="2026-10-18T07:00:00Z",
            collection_mission=mission,
        )

    @staticmethod
    def _method(handoff: dict) -> dict:
        return {
            "objective": "Assess the governed opportunity.",
            "candidate_or_opportunity": {"name": "Coastal radar"},
            "decision": "INVESTIGATE",
            "maturity": "I1",
            "evidence": [],
            "unknowns_conflicts": list(handoff["unresolved_material"]),
            "next_recommended_action": "Continue governed collection.",
        }

    @staticmethod
    def _collection_method(runtime_input: dict) -> dict:
        mission = runtime_input["collection_mission"]
        return {
            "objective": mission["objective"],
            "collection_status": "SUFFICIENT",
            "resolved_targets": [{"name": mission["targets"][0]["name"]}],
            "findings": [{"claim": "Target resolved.", "claim_type": "FACT", "claim_condition": "CURRENT", "evidence_refs": []}],
            "evidence": [],
            "unknowns_conflicts": [],
            "collection_gaps": [],
            "next_collection_questions": [],
        }

    def test_analyze_owns_the_complete_governed_synchronization_path(self) -> None:
        handoff = self._handoff()
        original = deepcopy(handoff)
        runtime = Argus(self._method, trusted_key_registry=self._trusted_key_registry())

        outcome = runtime.analyze(self._envelope(handoff))

        self.assertEqual(original, handoff)
        self.assertEqual("ATLAS_GOVERNED", outcome.result["governance_mode"])
        self.assertEqual(outcome.receipt["sync_execution_id"], outcome.result["sync_execution_id"])
        self.assertEqual("RETURNED", outcome.receipt["state"])
        self.assertEqual("2.0.1", outcome.receipt["argus"]["version"])
        self.assertEqual("LEASE-ARGUS-RUNTIME-001", outcome.receipt["atlas"]["execution_lease_id"])
        self.assertEqual(outcome.result["result_sha256"], outcome.receipt["argus"]["result_sha256"])
        self.assertEqual(handoff["handoff_id"], outcome.result["upstream_handoff"]["handoff_id"])
        self.assertLessEqual(len(outcome.compact_status.splitlines()), 3)

    def test_collection_mission_is_validated_correlated_and_delivered_to_method(self) -> None:
        handoff = self._handoff()
        mission = self._mission(handoff)
        original_handoff = deepcopy(handoff)
        original_mission = deepcopy(mission)
        captured: dict = {}

        def method(runtime_input: dict) -> dict:
            captured.update(deepcopy(runtime_input))
            return self._collection_method(runtime_input)

        runtime = Argus(method, trusted_key_registry=self._trusted_key_registry())
        outcome = runtime.analyze(self._envelope(handoff, mission=mission))

        self.assertEqual(original_handoff, handoff)
        self.assertEqual(original_mission, mission)
        self.assertEqual(original_handoff, captured["handoff"])
        self.assertEqual(original_mission, captured["collection_mission"])
        self.assertEqual("SUFFICIENT", outcome.result["collection_status"])
        self.assertEqual(outcome.result["result_sha256"], outcome.receipt["argus"]["result_sha256"])
        self.assertEqual("RETURNED", outcome.receipt["state"])
        self.assertIn("Collection SUFFICIENT", outcome.compact_status)

    def test_collection_mission_must_match_authenticated_handoff(self) -> None:
        handoff = self._handoff()
        mission = self._mission(handoff)
        mission["source_task_id"] = "TASK-DIFFERENT-001"
        with self.assertRaisesRegex(ValueError, "source_task_id"):
            self._envelope(handoff, mission=mission)

    def test_collection_package_requires_a_bound_mission(self) -> None:
        handoff = self._handoff()
        runtime = Argus(self._collection_method, trusted_key_registry=self._trusted_key_registry())
        with self.assertRaises(AnalysisExecutionError):
            runtime.analyze(self._envelope(handoff))

    def test_analyze_rejects_domain_methods_that_spoof_governance_fields(self) -> None:
        handoff = self._handoff()

        def spoofing_method(_: dict) -> dict:
            payload = self._method(handoff)
            payload["governance_mode"] = "STANDALONE"
            return payload

        runtime = Argus(spoofing_method, trusted_key_registry=self._trusted_key_registry())

        with self.assertRaises(SyncValidationError) as caught:
            runtime.analyze(self._envelope(handoff))

        self.assertEqual("DOMAIN_RESULT_RESERVED_FIELD", caught.exception.code)

    def test_analyze_returns_retryable_failed_state_when_domain_method_crashes(self) -> None:
        handoff = self._handoff()

        def failing_method(_: dict) -> dict:
            raise RuntimeError("collector unavailable")

        runtime = Argus(failing_method, trusted_key_registry=self._trusted_key_registry())

        with self.assertRaises(AnalysisExecutionError) as caught:
            runtime.analyze(self._envelope(handoff))

        self.assertEqual("FAILED", caught.exception.receipt["state"])
        self.assertEqual("DEPENDENCY_FAILED", caught.exception.receipt["failure_state"])
        self.assertIsInstance(caught.exception.__cause__, RuntimeError)

    def test_public_runtime_rejects_missing_governed_trust_or_lease(self) -> None:
        with self.assertRaises(ValueError):
            Argus(self._method, trusted_key_registry={})
        handoff = self._handoff()
        with self.assertRaises(ValueError):
            AnalysisEnvelope(
                handoff=handoff,
                atlas_attestation=self._attestation(handoff),
                execution_lease={},
                execution_lease_attestation={},
                started_at="2026-10-18T07:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
