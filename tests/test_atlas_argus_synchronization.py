from __future__ import annotations

import hashlib
import json
import base64
import unittest
from copy import deepcopy
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.atlas_sync import (
    SyncValidationError,
    action_idempotency_key,
    authorize_action,
    canonical_handoff_sha256,
    canonical_result_sha256,
    canonical_sync_execution_id,
    mark_upstream_context_change,
    map_atlas_failure,
    new_sync_receipt,
    resume_sync,
    retry_sync,
    transition_sync,
    validate_handoff,
    validate_action_authorization,
    validate_result_correlation,
    validate_sync_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "atlas-sync"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AtlasArgusSynchronizationTests(unittest.TestCase):
    PRIVATE_KEY = bytes(range(1, 33))
    KEY_ID = "atlas-test-2026"

    def _trusted_public_keys(self) -> dict[str, bytes]:
        public_key = Ed25519PrivateKey.from_private_bytes(self.PRIVATE_KEY).public_key()
        return {self.KEY_ID: public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )}

    def _attestation(self, record: dict) -> dict[str, str]:
        payload = json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        signature = Ed25519PrivateKey.from_private_bytes(self.PRIVATE_KEY).sign(payload)
        return {
            "version": "1", "issuer": "ATLAS_OS", "algorithm": "Ed25519",
            "key_id": self.KEY_ID,
            "record_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "signature": base64.b64encode(signature).decode("ascii"),
        }

    def _action(self) -> dict:
        return {
            "action": "CREATE_PX_OPPORTUNITY",
            "target_argus_id": "NEW:PX:COASTAL-RADAR",
            "rationale": "Promote the governed candidate after verification.",
            "reversible": False,
            "precondition_revision": "registry-rev-11",
            "policy_revision": "approvals-v2",
        }

    def _action_sha256(self, action: dict) -> str:
        encoded = json.dumps(
            action, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    def _approval(self, name: str = "approval-approved.json") -> dict:
        approval = load_fixture(name)
        approval["input_sha256"] = self._action_sha256(self._action())
        return approval

    def _active_receipt(self, handoff: dict | None = None) -> dict:
        handoff = handoff or load_fixture("ready-handoff.json")
        receipt = new_sync_receipt(
            handoff, "2026-10-18T07:00:00Z",
            atlas_attestation=self._attestation(handoff),
            trusted_public_keys=self._trusted_public_keys(),
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            receipt = transition_sync(receipt, state)
        return receipt

    def _result(self, handoff: dict, receipt: dict) -> dict:
        result = {
            "governance_mode": "ATLAS_GOVERNED",
            "sync_execution_id": receipt["sync_execution_id"],
            "sync_attempt": receipt["attempt"],
            "upstream_handoff": {
                "contract_version": handoff["contract_version"],
                "handoff_id": handoff["handoff_id"],
                "payload_sha256": handoff["payload_sha256"],
                "consumer": "ARGUS",
                "status": "ACCEPTED",
                "received_at": "2026-10-18T07:00:01Z",
            },
            "objective": "Assess the governed opportunity.",
            "candidate_or_opportunity": {"name": "Coastal radar"},
            "decision": "INVESTIGATE",
            "maturity": "I1",
            "evidence": [],
            "unknowns_conflicts": [],
            "next_recommended_action": "Continue governed collection.",
        }
        result["result_sha256"] = canonical_result_sha256(result)
        return result

    def test_ready_handoff_starts_correlated_receipt(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        validate_handoff(
            handoff, atlas_attestation=self._attestation(handoff),
            trusted_public_keys=self._trusted_public_keys(),
        )
        receipt = new_sync_receipt(
            handoff, "2026-10-18T07:00:00Z",
            atlas_attestation=self._attestation(handoff),
            trusted_public_keys=self._trusted_public_keys(),
        )
        self.assertEqual("RECEIVED", receipt["state"])
        self.assertEqual(handoff["handoff_id"], receipt["atlas"]["handoff_id"])
        self.assertEqual(handoff["source_task_id"], receipt["atlas"]["source_task_id"])
        self.assertEqual(canonical_sync_execution_id(handoff), receipt["sync_execution_id"])
        self.assertEqual(1, receipt["attempt"])

        repeated = new_sync_receipt(
            handoff, "2026-10-18T07:00:01Z",
            atlas_attestation=self._attestation(handoff),
            trusted_public_keys=self._trusted_public_keys(),
        )
        self.assertEqual(receipt["sync_execution_id"], repeated["sync_execution_id"])

    def test_tampered_handoff_digest_is_rejected(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        handoff["domain_alignment"]["domains"] = ["changed-domain"]
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(
                handoff, atlas_attestation=self._attestation(load_fixture("ready-handoff.json")),
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertEqual("ATLAS_ATTESTATION_DIGEST_MISMATCH", caught.exception.code)
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
                validate_handoff(
                    handoff, atlas_attestation=self._attestation(handoff),
                    trusted_public_keys=self._trusted_public_keys(),
                )
            self.assertEqual(code, caught.exception.code)

    def test_blocked_handoff_cannot_start(self) -> None:
        with self.assertRaises(SyncValidationError) as caught:
            handoff = load_fixture("blocked-handoff.json")
            validate_handoff(
                handoff, atlas_attestation=self._attestation(handoff),
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertEqual("HANDOFF_BLOCKED", caught.exception.code)
        self.assertEqual("BLOCKED", caught.exception.atlas_failure_state)

    def test_partial_handoff_preserves_unresolved_and_risk_snapshots(self) -> None:
        handoff = load_fixture("partial-handoff.json")
        receipt = new_sync_receipt(
            handoff, "2026-10-18T07:00:00Z",
            atlas_attestation=self._attestation(handoff),
            trusted_public_keys=self._trusted_public_keys(),
        )
        self.assertEqual(handoff["unresolved_material"], receipt["unresolved_material"])
        self.assertEqual(handoff["risk_flags"], receipt["risk_flags"])
        self.assertEqual("PARTIAL", receipt["failure_state"])
        validate_sync_receipt(receipt)

    def test_lifecycle_allows_only_explicit_transitions(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        receipt = new_sync_receipt(
            handoff,
            "2026-10-18T07:00:00Z",
            atlas_attestation=self._attestation(handoff),
            trusted_public_keys=self._trusted_public_keys(),
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            receipt = transition_sync(receipt, state)
            self.assertEqual(state, receipt["state"])
            validate_sync_receipt(receipt)
        receipt = validate_result_correlation(
            self._result(handoff, receipt), handoff, receipt,
            trusted_public_keys=self._trusted_public_keys(),
        )
        self.assertEqual("RESULT_READY", receipt["state"])
        receipt = transition_sync(receipt, "RETURNED")
        self.assertIsNotNone(receipt["completed_at"])

        with self.assertRaises(SyncValidationError) as caught:
            transition_sync(receipt, "ACTIVE")
        self.assertEqual("ILLEGAL_SYNC_TRANSITION", caught.exception.code)

    def test_material_context_change_supersedes_dependent_work(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        receipt = new_sync_receipt(
            handoff,
            "2026-10-18T07:00:00Z",
            atlas_attestation=self._attestation(handoff),
            trusted_public_keys=self._trusted_public_keys(),
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
        bound = validate_result_correlation(
            self._result(handoff, receipt), handoff, receipt,
            trusted_public_keys=self._trusted_public_keys(),
        )
        self.assertEqual("RESULT_READY", bound["state"])
        self.assertEqual(self._result(handoff, receipt)["result_sha256"], bound["argus"]["result_sha256"])

        for field, value in (
            ("contract_version", "9.9.9"),
            ("handoff_id", "HANDOFF-ARGUS-STALE-999"),
            ("payload_sha256", "sha256:" + "f" * 64),
            ("consumer", "OTHER"),
            ("status", "REJECTED"),
        ):
            result = self._result(handoff, receipt)
            result["upstream_handoff"][field] = value
            result["result_sha256"] = canonical_result_sha256(result)
            with self.subTest(field=field), self.assertRaises(SyncValidationError) as caught:
                validate_result_correlation(
                    result, handoff, receipt,
                    trusted_public_keys=self._trusted_public_keys(),
                )
            self.assertIn(
                caught.exception.code,
                {"RESULT_CORRELATION_MISMATCH", "RESULT_SCHEMA_INVALID", "RESULT_RECEIPT_INVALID"},
            )

    def test_stale_result_and_superseded_receipt_are_rejected(self) -> None:
        current = load_fixture("partial-handoff.json")
        old = load_fixture("ready-handoff.json")
        old_receipt = self._active_receipt(old)
        with self.assertRaises(SyncValidationError) as caught:
            validate_result_correlation(
                self._result(old, old_receipt), current, old_receipt,
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertEqual("SYNC_HANDOFF_STALE", caught.exception.code)

        superseded = mark_upstream_context_change(
            old_receipt, ["jurisdiction"], ["EVIDENCE-001"], "Context changed."
        )
        with self.assertRaises(SyncValidationError) as caught:
            validate_result_correlation(
                self._result(old, old_receipt), old, superseded,
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertEqual("SYNC_EXECUTION_NOT_CURRENT", caught.exception.code)

    def test_retry_increments_attempt_for_same_current_handoff(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        failed = transition_sync(self._active_receipt(handoff), "FAILED")
        retried = retry_sync(failed, handoff, trusted_public_keys=self._trusted_public_keys())
        self.assertEqual(failed["sync_execution_id"], retried["sync_execution_id"])
        self.assertEqual(2, retried["attempt"])
        self.assertEqual("ACTIVE", retried["state"])
        self.assertEqual("FAILED", retried["resume_from"])

        returned = self._active_receipt(handoff)
        returned = validate_result_correlation(
            self._result(handoff, returned), handoff, returned,
            trusted_public_keys=self._trusted_public_keys(),
        )
        returned = transition_sync(returned, "RETURNED")
        with self.assertRaises(SyncValidationError):
            retry_sync(returned, handoff, trusted_public_keys=self._trusted_public_keys())

    def test_resume_requires_active_identity_and_registry_reconciliation(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        failed = transition_sync(self._active_receipt(handoff), "FAILED")
        common = {
            "stored_registry_fingerprint": "sha256:" + "a" * 64,
            "actual_registry_fingerprint": "sha256:" + "a" * 64,
            "trusted_public_keys": self._trusted_public_keys(),
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
                trusted_public_keys=self._trusted_public_keys(),
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

    def test_required_and_not_required_approval_states_are_conservative(self) -> None:
        action = self._action()
        receipt = self._active_receipt()
        approval = self._approval()
        validate_action_authorization(
            action, approval, ["CREATE_PX_OPPORTUNITY", "ARGUS:CANONICAL_WRITE"], receipt,
            approval_attestation=self._attestation(approval),
            trusted_public_keys=self._trusted_public_keys(),
        )
        not_required = self._approval("approval-not-required.json")
        with self.assertRaises(SyncValidationError):
            validate_action_authorization(
                action, not_required, ["CREATE_PX_OPPORTUNITY"], receipt,
                approval_attestation=self._attestation(not_required),
                trusted_public_keys=self._trusted_public_keys(),
            )

        for status in ("PENDING", "DENIED", "EXPIRED"):
            approval = self._approval()
            approval["status"] = status
            if status != "PENDING":
                approval["approved_at"] = "2026-10-18T07:01:00Z"
            with self.subTest(status=status), self.assertRaises(SyncValidationError):
                validate_action_authorization(
                    action, approval, ["CREATE_PX_OPPORTUNITY"], receipt,
                    approval_attestation=self._attestation(approval),
                    trusted_public_keys=self._trusted_public_keys(),
                )

        inconsistent = self._approval("approval-not-required.json")
        inconsistent["status"] = "APPROVED"
        inconsistent["approved_at"] = "2026-10-18T07:01:00Z"
        with self.assertRaises(SyncValidationError):
            validate_action_authorization(
                action, inconsistent, ["CREATE_PX_OPPORTUNITY"], receipt,
                approval_attestation=self._attestation(inconsistent),
                trusted_public_keys=self._trusted_public_keys(),
            )

    def test_approval_scope_and_action_binding_are_exact(self) -> None:
        action = self._action()
        approval = self._approval()
        receipt = self._active_receipt()
        for expected_scope in (
            ["CREATE-PX-OPPORTUNITY"],
            ["CREATE_PX"],
            ["CREATE_PX_OPPORTUNITY", "MISSING_SCOPE"],
        ):
            with self.subTest(expected_scope=expected_scope), self.assertRaises(SyncValidationError):
                validate_action_authorization(
                    action, approval, expected_scope, receipt,
                    approval_attestation=self._attestation(approval),
                    trusted_public_keys=self._trusted_public_keys(),
                )

        changed = deepcopy(action)
        changed["target_argus_id"] = "NEW:PX:OTHER"
        with self.assertRaises(SyncValidationError) as caught:
            validate_action_authorization(
                changed, approval, ["CREATE_PX_OPPORTUNITY"], receipt,
                approval_attestation=self._attestation(approval),
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertEqual("APPROVAL_ACTION_MISMATCH", caught.exception.code)

    def test_action_authorization_is_idempotent_and_rejects_superseded_sync(self) -> None:
        action = self._action()
        approval = self._approval()
        receipt = self._active_receipt()
        key = action_idempotency_key(action)
        self.assertEqual(key, action_idempotency_key(action))

        authorized = authorize_action(
            receipt, action, approval, ["CREATE_PX_OPPORTUNITY"],
            approval_attestation=self._attestation(approval),
            trusted_public_keys=self._trusted_public_keys(),
        )
        repeated = authorize_action(
            authorized, action, approval, ["CREATE_PX_OPPORTUNITY"],
            approval_attestation=self._attestation(approval),
            trusted_public_keys=self._trusted_public_keys(),
        )
        self.assertEqual(authorized, repeated)
        self.assertEqual(1, len(repeated["authorized_actions"]))
        self.assertEqual(key, repeated["authorized_actions"][0]["idempotency_key"])

        superseded = mark_upstream_context_change(
            receipt, ["jurisdiction"], ["EVIDENCE-001"], "Context changed."
        )
        with self.assertRaises(SyncValidationError):
            authorize_action(
                superseded, action, approval, ["CREATE_PX_OPPORTUNITY"],
                approval_attestation=self._attestation(approval),
                trusted_public_keys=self._trusted_public_keys(),
            )

    def test_standalone_result_cannot_masquerade_as_governed(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        receipt = self._active_receipt(handoff)
        result = self._result(handoff, receipt)
        result["governance_mode"] = "STANDALONE"
        with self.assertRaises(SyncValidationError) as caught:
            validate_result_correlation(
                result, handoff, receipt, trusted_public_keys=self._trusted_public_keys()
            )
        self.assertEqual("GOVERNANCE_MODE_MISMATCH", caught.exception.code)

    def test_relabelled_blocked_handoff_is_rejected(self) -> None:
        handoff = load_fixture("blocked-handoff.json")
        handoff["state"] = "READY"
        handoff["payload_sha256"] = canonical_handoff_sha256(handoff)
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(
                handoff, atlas_attestation=self._attestation(load_fixture("blocked-handoff.json")),
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertIn(caught.exception.code, {"ATLAS_ATTESTATION_DIGEST_MISMATCH", "HANDOFF_STATE_INCONSISTENT"})

    def test_result_is_bound_to_execution_attempt_and_digest(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        first = self._active_receipt(handoff)
        second = dict(first)
        second["sync_execution_id"] = "ARGUS-SYNC-SECOND-001"
        result = self._result(handoff, first)
        with self.assertRaises(SyncValidationError) as caught:
            validate_result_correlation(
                result, handoff, second, trusted_public_keys=self._trusted_public_keys()
            )
        self.assertEqual("RESULT_EXECUTION_MISMATCH", caught.exception.code)

        changed = deepcopy(result)
        changed["decision"] = "PROMOTE_TO_PX"
        with self.assertRaises(SyncValidationError) as caught:
            validate_result_correlation(
                changed, handoff, first, trusted_public_keys=self._trusted_public_keys()
            )
        self.assertEqual("RESULT_DIGEST_MISMATCH", caught.exception.code)

    def test_fabricated_approval_is_not_a_trust_anchor(self) -> None:
        receipt = self._active_receipt()
        fabricated = self._approval()
        fabricated["id"] = "APR-FABRICATED"
        with self.assertRaises(SyncValidationError) as caught:
            authorize_action(
                receipt, self._action(), fabricated, ["CREATE_PX_OPPORTUNITY"],
                approval_attestation=self._attestation(self._approval()),
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertEqual("APPROVAL_NOT_TRUSTED", caught.exception.code)

    def test_stale_handoff_is_rejected_even_with_matching_digest(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        handoff["created_at"] = "2000-01-01T00:00:00Z"
        handoff["payload_sha256"] = canonical_handoff_sha256(handoff)
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(
                handoff, atlas_attestation=self._attestation(handoff),
                trusted_public_keys=self._trusted_public_keys(),
            )
        self.assertEqual("HANDOFF_EXPIRED", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
