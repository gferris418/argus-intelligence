from __future__ import annotations

import base64
import hashlib
import json
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.atlas_sync import (
    SyncValidationError,
    canonical_handoff_sha256,
    new_sync_receipt,
    renew_execution_lease,
    retry_sync,
    validate_execution_lease,
    validate_handoff,
    validate_handoff_integrity,
    validate_result_correlation,
)


class AtlasControlPlaneHardeningTests(unittest.TestCase):
    KEY_ID = "atlas-test-2026"

    def setUp(self) -> None:
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        clock = patch(
            "tools.atlas_sync._utc_now",
            return_value=datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc),
        )
        clock.start()
        self.addCleanup(clock.stop)

    def _attestation(self, record: dict) -> dict[str, str]:
        payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return {
            "version": "1",
            "issuer": "ATLAS_OS",
            "algorithm": "Ed25519",
            "key_id": self.KEY_ID,
            "record_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "signature": base64.b64encode(self.private_key.sign(payload)).decode("ascii"),
        }

    def _registry(self, *, status: str = "ACTIVE", allowed: list[str] | None = None) -> dict:
        return {
            "registry_version": "1.0.0",
            "issuer": "ATLAS_OS",
            "keys": [{
                "key_id": self.KEY_ID,
                "algorithm": "Ed25519",
                "public_key_base64": base64.b64encode(self.public_key).decode("ascii"),
                "activated_at": "2026-10-01T00:00:00Z",
                "expires_at": "2026-12-31T23:59:59Z",
                "status": status,
                "issuer": "ATLAS_OS",
                "allowed_record_classes": allowed or ["DOMAIN_CONTEXT_HANDOFF", "EXECUTION_LEASE", "APPROVAL"],
                "supersedes": None,
            }],
        }

    def _handoff(self) -> dict:
        handoff = {
            "contract_version": "1.2.0",
            "handoff_id": "HANDOFF-ARGUS-001",
            "source_task_id": "TASK-SAMPLE-001",
            "source_plan_id": "plan-domain-handoff",
            "source_work_unit_id": "unit-domain-analysis",
            "producer": "ATLAS_OS",
            "consumer": "ARGUS",
            "created_at": "2026-10-18T00:00:00Z",
            "activation_expires_at": "2026-10-19T00:00:00Z",
            "state": "READY",
            "domain_classification": {
                "status": "CLASSIFIED",
                "facets": {},
                "taxonomy_references": [],
                "risk_flags": [],
                "unresolved_facets": [],
                "conditional_candidates": [],
                "evidence": [],
                "next_action": None,
            },
            "domain_alignment": {
                "domains": ["planning"],
                "status": "ALIGNED",
                "frameworks": [],
                "applicability": {},
                "deviations": [],
                "compliance": "NOT_CLAIMED",
                "evidence": [],
            },
            "unresolved_material": [],
            "risk_flags": [],
        }
        handoff["payload_sha256"] = canonical_handoff_sha256(handoff)
        return handoff

    def _lease(self, handoff: dict, *, lease_id: str = "LEASE-ARGUS-001", expires_at: str = "2026-10-22T00:05:00Z", supersedes: str | None = None) -> dict:
        return {
            "contract_version": "1.0.0",
            "execution_lease_id": lease_id,
            "handoff_id": handoff["handoff_id"],
            "handoff_payload_sha256": handoff["payload_sha256"],
            "source_task_id": handoff["source_task_id"],
            "source_plan_id": handoff["source_plan_id"],
            "source_work_unit_id": handoff["source_work_unit_id"],
            "producer": "ATLAS_OS",
            "consumer": "ARGUS",
            "issued_at": "2026-10-18T00:05:00Z" if supersedes is None else "2026-10-21T11:00:00Z",
            "lease_expires_at": expires_at,
            "supersedes_lease_id": supersedes,
        }

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
                "received_at": "2026-10-18T00:06:00Z",
            },
            "objective": "Assess the governed opportunity.",
            "candidate_or_opportunity": {"name": "Coastal radar"},
            "decision": "INVESTIGATE",
            "maturity": "I1",
            "evidence": [],
            "unknowns_conflicts": [],
            "next_recommended_action": "Continue governed collection.",
        }
        payload = {key: value for key, value in result.items() if key != "result_sha256"}
        result["result_sha256"] = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        return result

    def test_activation_window_applies_only_to_initial_activation(self) -> None:
        handoff = self._handoff()
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(
                handoff,
                atlas_attestation=self._attestation(handoff),
                trusted_key_registry=self._registry(),
            )
        self.assertEqual("HANDOFF_EXPIRED", caught.exception.code)
        self.assertIsNone(validate_handoff_integrity(
            handoff,
            atlas_attestation=self._attestation(handoff),
            trusted_key_registry=self._registry(),
        ))

    def test_active_execution_lease_allows_result_after_activation_window(self) -> None:
        handoff = self._handoff()
        lease = self._lease(handoff)
        receipt = new_sync_receipt(
            handoff,
            "2026-10-18T00:06:00Z",
            atlas_attestation=self._attestation(handoff),
            execution_lease=lease,
            execution_lease_attestation=self._attestation(lease),
            trusted_key_registry=self._registry(),
            activated_at="2026-10-18T00:06:00Z",
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            from tools.atlas_sync import transition_sync
            receipt = transition_sync(receipt, state)
        correlated = validate_result_correlation(
            self._result(handoff, receipt),
            handoff,
            receipt,
            trusted_key_registry=self._registry(),
        )
        self.assertEqual("RESULT_READY", correlated["state"])
        self.assertEqual("LEASE-ARGUS-001", correlated["atlas"]["execution_lease_id"])

    def test_expired_or_revoked_lease_fails_closed(self) -> None:
        handoff = self._handoff()
        expired = self._lease(handoff, expires_at="2026-10-20T00:05:00Z")
        with self.assertRaises(SyncValidationError) as caught:
            validate_execution_lease(
                expired,
                handoff,
                lease_attestation=self._attestation(expired),
                trusted_key_registry=self._registry(),
            )
        self.assertEqual("EXECUTION_LEASE_EXPIRED", caught.exception.code)
        active = self._lease(handoff)
        with self.assertRaises(SyncValidationError) as caught:
            validate_execution_lease(
                active,
                handoff,
                lease_attestation=self._attestation(active),
                trusted_key_registry=self._registry(status="REVOKED"),
            )
        self.assertEqual("ATLAS_ATTESTATION_UNTRUSTED", caught.exception.code)

    def test_lease_renewal_supersedes_old_lease_and_retry_uses_current_lease(self) -> None:
        handoff = self._handoff()
        first = self._lease(handoff)
        receipt = new_sync_receipt(
            handoff,
            "2026-10-18T00:06:00Z",
            atlas_attestation=self._attestation(handoff),
            execution_lease=first,
            execution_lease_attestation=self._attestation(first),
            trusted_key_registry=self._registry(),
            activated_at="2026-10-18T00:06:00Z",
        )
        from tools.atlas_sync import transition_sync
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            receipt = transition_sync(receipt, state)
        failed = transition_sync(receipt, "FAILED")
        renewed = self._lease(
            handoff,
            lease_id="LEASE-ARGUS-002",
            expires_at="2026-10-24T12:00:00Z",
            supersedes="LEASE-ARGUS-001",
        )
        failed = renew_execution_lease(
            failed,
            handoff,
            renewed,
            execution_lease_attestation=self._attestation(renewed),
            trusted_key_registry=self._registry(),
        )
        retried = retry_sync(failed, handoff, trusted_key_registry=self._registry())
        self.assertEqual("LEASE-ARGUS-002", retried["atlas"]["execution_lease_id"])
        self.assertEqual(2, retried["attempt"])
        with self.assertRaises(SyncValidationError) as caught:
            validate_execution_lease(
                first,
                handoff,
                lease_attestation=self._attestation(first),
                trusted_key_registry=self._registry(),
                expected_lease_id="LEASE-ARGUS-002",
            )
        self.assertEqual("EXECUTION_LEASE_STALE", caught.exception.code)

    def test_signing_key_scope_is_enforced(self) -> None:
        handoff = self._handoff()
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff_integrity(
                handoff,
                atlas_attestation=self._attestation(handoff),
                trusted_key_registry=self._registry(allowed=["EXECUTION_LEASE"]),
            )
        self.assertEqual("ATLAS_ATTESTATION_UNTRUSTED", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
