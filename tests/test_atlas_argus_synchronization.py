from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from tools.atlas_sync import (
    SyncValidationError,
    canonical_handoff_sha256,
    mark_upstream_context_change,
    map_atlas_failure,
    new_sync_receipt,
    resume_sync,
    retry_sync,
    transition_sync,
    validate_handoff,
    validate_result_correlation,
    validate_sync_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "atlas-sync"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AtlasArgusSynchronizationTests(unittest.TestCase):
    def _active_receipt(self, handoff: dict | None = None) -> dict:
        handoff = handoff or load_fixture("ready-handoff.json")
        receipt = new_sync_receipt(
            "ARGUS-SYNC-ACTIVE-001", handoff, "2026-10-18T07:00:00Z"
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            receipt = transition_sync(receipt, state)
        return receipt

    def _result(self, handoff: dict) -> dict:
        return {
            "governance_mode": "ATLAS_GOVERNED",
            "upstream_handoff": {
                "contract_version": handoff["contract_version"],
                "handoff_id": handoff["handoff_id"],
                "payload_sha256": handoff["payload_sha256"],
                "consumer": "ARGUS",
                "status": "ACCEPTED",
                "received_at": "2026-10-18T07:00:01Z",
            },
        }

    def test_ready_handoff_starts_correlated_receipt(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        validate_handoff(handoff)
        receipt = new_sync_receipt(
            "ARGUS-SYNC-READY-001", handoff, "2026-10-18T07:00:00Z"
        )
        self.assertEqual("RECEIVED", receipt["state"])
        self.assertEqual(handoff["handoff_id"], receipt["atlas"]["handoff_id"])
        self.assertEqual(handoff["source_task_id"], receipt["atlas"]["source_task_id"])
        self.assertEqual(1, receipt["attempt"])

    def test_tampered_handoff_digest_is_rejected(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        handoff["domain_alignment"]["domains"] = ["changed-domain"]
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(handoff)
        self.assertEqual("HANDOFF_DIGEST_MISMATCH", caught.exception.code)
        self.assertEqual("VALIDATION_FAILED", caught.exception.atlas_failure_state)

    def test_wrong_consumer_and_unsupported_version_are_rejected(self) -> None:
        for field, value, code in (
            ("consumer", "OTHER", "HANDOFF_CONSUMER_MISMATCH"),
            ("contract_version", "9.9.9", "HANDOFF_SCHEMA_INVALID"),
        ):
            handoff = load_fixture("ready-handoff.json")
            handoff[field] = value
            handoff["payload_sha256"] = canonical_handoff_sha256(handoff)
            with self.subTest(field=field), self.assertRaises(SyncValidationError) as caught:
                validate_handoff(handoff)
            self.assertEqual(code, caught.exception.code)

    def test_blocked_handoff_cannot_start(self) -> None:
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(load_fixture("blocked-handoff.json"))
        self.assertEqual("HANDOFF_BLOCKED", caught.exception.code)
        self.assertEqual("BLOCKED", caught.exception.atlas_failure_state)

    def test_partial_handoff_preserves_unresolved_and_risk_snapshots(self) -> None:
        handoff = load_fixture("partial-handoff.json")
        receipt = new_sync_receipt(
            "ARGUS-SYNC-PARTIAL-001", handoff, "2026-10-18T07:00:00Z"
        )
        self.assertEqual(handoff["unresolved_material"], receipt["unresolved_material"])
        self.assertEqual(handoff["risk_flags"], receipt["risk_flags"])
        self.assertEqual("PARTIAL", receipt["failure_state"])
        validate_sync_receipt(receipt)

    def test_lifecycle_allows_only_explicit_transitions(self) -> None:
        receipt = new_sync_receipt(
            "ARGUS-SYNC-LIFECYCLE-001",
            load_fixture("ready-handoff.json"),
            "2026-10-18T07:00:00Z",
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE", "RESULT_READY", "RETURNED"):
            receipt = transition_sync(receipt, state)
            self.assertEqual(state, receipt["state"])
            validate_sync_receipt(receipt)
        self.assertIsNotNone(receipt["completed_at"])

        with self.assertRaises(SyncValidationError) as caught:
            transition_sync(receipt, "ACTIVE")
        self.assertEqual("ILLEGAL_SYNC_TRANSITION", caught.exception.code)

    def test_material_context_change_supersedes_dependent_work(self) -> None:
        receipt = new_sync_receipt(
            "ARGUS-SYNC-CONTEXT-001",
            load_fixture("ready-handoff.json"),
            "2026-10-18T07:00:00Z",
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            receipt = transition_sync(receipt, state)
        changed = mark_upstream_context_change(
            receipt,
            ["jurisdiction"],
            ["EVIDENCE-001"],
            "New primary-source evidence changes jurisdiction.",
        )
        self.assertEqual("SUPERSEDED_PENDING_ATLAS", changed["state"])
        self.assertTrue(changed["context_change_detected"])
        self.assertTrue(changed["upstream_refresh_required"])
        self.assertEqual(["jurisdiction"], changed["upstream_context_change"]["affected_facets"])
        validate_sync_receipt(changed)

    def test_result_requires_exact_current_handoff_correlation(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        receipt = self._active_receipt(handoff)
        validate_result_correlation(self._result(handoff), handoff, receipt)

        for field, value in (
            ("contract_version", "9.9.9"),
            ("handoff_id", "HANDOFF-ARGUS-STALE-999"),
            ("payload_sha256", "sha256:" + "f" * 64),
            ("consumer", "OTHER"),
            ("status", "REJECTED"),
        ):
            result = self._result(handoff)
            result["upstream_handoff"][field] = value
            with self.subTest(field=field), self.assertRaises(SyncValidationError) as caught:
                validate_result_correlation(result, handoff, receipt)
            self.assertEqual("RESULT_CORRELATION_MISMATCH", caught.exception.code)

    def test_stale_result_and_superseded_receipt_are_rejected(self) -> None:
        current = load_fixture("partial-handoff.json")
        old = load_fixture("ready-handoff.json")
        old_receipt = self._active_receipt(old)
        with self.assertRaises(SyncValidationError) as caught:
            validate_result_correlation(self._result(old), current, old_receipt)
        self.assertEqual("SYNC_HANDOFF_STALE", caught.exception.code)

        superseded = mark_upstream_context_change(
            old_receipt, ["jurisdiction"], ["EVIDENCE-001"], "Context changed."
        )
        with self.assertRaises(SyncValidationError) as caught:
            validate_result_correlation(self._result(old), old, superseded)
        self.assertEqual("SYNC_EXECUTION_NOT_CURRENT", caught.exception.code)

    def test_retry_increments_attempt_for_same_current_handoff(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        failed = transition_sync(self._active_receipt(handoff), "FAILED")
        retried = retry_sync(failed, handoff)
        self.assertEqual(failed["sync_execution_id"], retried["sync_execution_id"])
        self.assertEqual(2, retried["attempt"])
        self.assertEqual("ACTIVE", retried["state"])
        self.assertEqual("FAILED", retried["resume_from"])

        returned = self._active_receipt(handoff)
        returned = transition_sync(transition_sync(returned, "RESULT_READY"), "RETURNED")
        with self.assertRaises(SyncValidationError):
            retry_sync(returned, handoff)

    def test_resume_requires_active_identity_and_registry_reconciliation(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        failed = transition_sync(self._active_receipt(handoff), "FAILED")
        common = {
            "stored_registry_fingerprint": "sha256:" + "a" * 64,
            "actual_registry_fingerprint": "sha256:" + "a" * 64,
        }
        with self.assertRaises(SyncValidationError) as caught:
            resume_sync(
                failed, handoff, active_sync_execution_id="ARGUS-SYNC-OTHER-001", **common
            )
        self.assertEqual("SYNC_EXECUTION_STALE", caught.exception.code)

        with self.assertRaises(SyncValidationError) as caught:
            resume_sync(
                failed,
                handoff,
                active_sync_execution_id=failed["sync_execution_id"],
                stored_registry_fingerprint="sha256:" + "a" * 64,
                actual_registry_fingerprint="sha256:" + "b" * 64,
            )
        self.assertEqual("REGISTRY_FINGERPRINT_DRIFT", caught.exception.code)

        resumed = resume_sync(
            failed,
            handoff,
            active_sync_execution_id=failed["sync_execution_id"],
            **common,
        )
        self.assertEqual(2, resumed["attempt"])
        self.assertEqual("ACTIVE", resumed["state"])

    def test_failure_conditions_map_only_to_atlas_vocabulary(self) -> None:
        expected = {
            "invalid": "VALIDATION_FAILED",
            "blocked": "BLOCKED",
            "dependency": "DEPENDENCY_FAILED",
            "capability": "CAPABILITY_UNAVAILABLE",
            "evidence": "EVIDENCE_INSUFFICIENT",
            "authorization": "AUTHORIZATION_REQUIRED",
            "unverified": "UNVERIFIED",
            "partial": "PARTIAL",
        }
        for condition, failure in expected.items():
            with self.subTest(condition=condition):
                self.assertEqual(failure, map_atlas_failure(condition))
        with self.assertRaises(SyncValidationError):
            map_atlas_failure("invented-state")


if __name__ == "__main__":
    unittest.main()
