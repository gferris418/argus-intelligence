"""Pure synchronization controls for ATLAS-governed ARGUS execution."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCHEMA = json.loads(
    (ROOT / "contracts/atlas/domain-context-handoff-v1.schema.json").read_text(encoding="utf-8")
)
SYNC_SCHEMA = json.loads(
    (ROOT / "schemas/atlas-argus-sync-receipt.schema.json").read_text(encoding="utf-8")
)
APPROVAL_SCHEMA = json.loads(
    (ROOT / "contracts/atlas/approval-v1.schema.json").read_text(encoding="utf-8")
)
HANDOFF_RECEIPT_SCHEMA = json.loads(
    (ROOT / "contracts/atlas/domain-handoff-receipt-v1.schema.json").read_text(encoding="utf-8")
)
RESULT_SCHEMA = json.loads(
    (ROOT / "schemas/domain-result.schema.json").read_text(encoding="utf-8")
)
COMPATIBILITY = json.loads(
    (ROOT / "contracts/atlas/synchronization-compatibility.yaml").read_text(encoding="utf-8")
)["atlas_compatibility"]

_TRANSITIONS = {
    "RECEIVED": {"VALIDATED", "INVALID", "REJECTED", "BLOCKED"},
    "VALIDATED": {"ACCEPTED", "REJECTED", "INVALID"},
    "ACCEPTED": {"ACTIVE", "SUPERSEDED_PENDING_ATLAS", "FAILED"},
    "ACTIVE": {"RESULT_READY", "SUPERSEDED_PENDING_ATLAS", "STALE", "FAILED"},
    "RESULT_READY": {"RETURNED", "SUPERSEDED_PENDING_ATLAS", "STALE", "FAILED"},
}


class SyncValidationError(ValueError):
    def __init__(self, code: str, atlas_failure_state: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.atlas_failure_state = atlas_failure_state


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value)).hexdigest()


def _verify_atlas_attestation(
    record: Mapping[str, Any],
    attestation: Mapping[str, Any],
    trusted_public_keys: Mapping[str, bytes],
) -> None:
    expected_fields = {
        "version", "issuer", "algorithm", "key_id", "record_sha256", "signature"
    }
    if set(attestation) != expected_fields or (
        attestation.get("version") != "1"
        or attestation.get("issuer") != "ATLAS_OS"
        or attestation.get("algorithm") != "Ed25519"
    ):
        raise SyncValidationError(
            "ATLAS_ATTESTATION_INVALID", "VALIDATION_FAILED", "unsupported ATLAS attestation"
        )
    public_key_bytes = trusted_public_keys.get(str(attestation.get("key_id", "")))
    if public_key_bytes is None:
        raise SyncValidationError(
            "ATLAS_ATTESTATION_UNTRUSTED", "VALIDATION_FAILED", "ATLAS signing key is not trusted"
        )
    payload = _canonical_json(record)
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    if attestation.get("record_sha256") != digest:
        raise SyncValidationError(
            "ATLAS_ATTESTATION_DIGEST_MISMATCH", "VALIDATION_FAILED", "ATLAS attestation does not match record"
        )
    try:
        signature = base64.b64decode(str(attestation["signature"]), validate=True)
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(signature, payload)
    except (KeyError, ValueError, InvalidSignature) as error:
        raise SyncValidationError(
            "ATLAS_ATTESTATION_SIGNATURE_INVALID", "VALIDATION_FAILED", "ATLAS signature is invalid"
        ) from error


def canonical_handoff_sha256(handoff: dict[str, Any]) -> str:
    payload = {key: value for key, value in handoff.items() if key != "payload_sha256"}
    return _sha256_json(payload)


def canonical_result_sha256(result: dict[str, Any]) -> str:
    payload = {key: value for key, value in result.items() if key != "result_sha256"}
    return _sha256_json(payload)


def canonical_sync_execution_id(handoff: Mapping[str, Any]) -> str:
    digest = str(handoff.get("payload_sha256", ""))
    if not digest.startswith("sha256:") or len(digest) != 71:
        raise SyncValidationError(
            "HANDOFF_DIGEST_INVALID", "VALIDATION_FAILED", "handoff cannot derive a synchronization identity"
        )
    return "ARGUS-SYNC-" + digest.removeprefix("sha256:")[:24].upper()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _derived_handoff_state(handoff: dict[str, Any]) -> str:
    classification = handoff["domain_classification"]
    alignment = handoff["domain_alignment"]
    if classification.get("status") == "RESEARCH_REQUIRED" or alignment.get("status") == "RESEARCH_REQUIRED":
        return "BLOCKED"
    if classification.get("status") == "CLASSIFIED" and alignment.get("status") in {"ALIGNED", "NOT_APPLICABLE"}:
        return "READY"
    return "PARTIAL"


def validate_handoff(
    handoff: dict[str, Any],
    *,
    atlas_attestation: Mapping[str, Any],
    trusted_public_keys: Mapping[str, bytes],
) -> None:
    try:
        jsonschema.validate(
            handoff,
            HANDOFF_SCHEMA,
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        raise SyncValidationError(
            "HANDOFF_SCHEMA_INVALID", "VALIDATION_FAILED", error.message
        ) from error
    if handoff.get("producer") != "ATLAS_OS":
        raise SyncValidationError(
            "HANDOFF_PRODUCER_MISMATCH", "VALIDATION_FAILED", "handoff producer is not ATLAS_OS"
        )
    if handoff.get("consumer") != "ARGUS":
        raise SyncValidationError(
            "HANDOFF_CONSUMER_MISMATCH", "VALIDATION_FAILED", "handoff consumer is not ARGUS"
        )
    if handoff.get("contract_version") != COMPATIBILITY["handoff_contract_version"]:
        raise SyncValidationError(
            "HANDOFF_VERSION_UNSUPPORTED", "VALIDATION_FAILED", "unsupported handoff contract version"
        )
    _verify_atlas_attestation(handoff, atlas_attestation, trusted_public_keys)
    if handoff.get("payload_sha256") != canonical_handoff_sha256(handoff):
        raise SyncValidationError(
            "HANDOFF_DIGEST_MISMATCH", "VALIDATION_FAILED", "handoff digest does not match payload"
        )
    classification = handoff["domain_classification"]
    if handoff["unresolved_material"] != classification.get("unresolved_facets", []):
        raise SyncValidationError(
            "HANDOFF_UNRESOLVED_INCONSISTENT", "VALIDATION_FAILED", "unresolved material differs from classification"
        )
    if handoff["risk_flags"] != classification.get("risk_flags", []):
        raise SyncValidationError(
            "HANDOFF_RISK_INCONSISTENT", "VALIDATION_FAILED", "risk flags differ from classification"
        )
    if handoff["state"] != _derived_handoff_state(handoff):
        raise SyncValidationError(
            "HANDOFF_STATE_INCONSISTENT", "VALIDATION_FAILED", "handoff state differs from its ATLAS context"
        )
    created_at = datetime.fromisoformat(handoff["created_at"].replace("Z", "+00:00"))
    current = _utc_now()
    if created_at > current + timedelta(minutes=5) or current - created_at > timedelta(hours=24):
        raise SyncValidationError(
            "HANDOFF_EXPIRED", "VALIDATION_FAILED", "handoff is outside the 24-hour activation window"
        )
    if handoff.get("state") == "BLOCKED":
        raise SyncValidationError(
            "HANDOFF_BLOCKED", "BLOCKED", "BLOCKED handoff cannot start dependent ARGUS execution"
        )


def validate_sync_receipt(receipt: dict[str, Any]) -> None:
    try:
        jsonschema.validate(
            receipt,
            SYNC_SCHEMA,
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        raise SyncValidationError(
            "SYNC_RECEIPT_INVALID", "VALIDATION_FAILED", error.message
        ) from error


def new_sync_receipt(
    handoff: dict[str, Any],
    started_at: str,
    *,
    atlas_attestation: Mapping[str, Any],
    trusted_public_keys: Mapping[str, bytes],
) -> dict[str, Any]:
    validate_handoff(
        handoff,
        atlas_attestation=atlas_attestation,
        trusted_public_keys=trusted_public_keys,
    )
    receipt = {
        "sync_execution_id": canonical_sync_execution_id(handoff),
        "attempt": 1,
        "mode": "ATLAS_GOVERNED",
        "atlas": {
            "version": COMPATIBILITY["atlas_version"],
            "commit": COMPATIBILITY["atlas_commit"],
            "handoff_contract_version": handoff["contract_version"],
            "handoff_id": handoff["handoff_id"],
            "payload_sha256": handoff["payload_sha256"],
            "source_task_id": handoff["source_task_id"],
            "source_plan_id": handoff["source_plan_id"],
            "source_work_unit_id": handoff["source_work_unit_id"],
            "handoff_attestation": deepcopy(atlas_attestation),
        },
        "argus": {"version": "2.0.0-rc.2", "result_sha256": None},
        "state": "RECEIVED",
        "started_at": started_at,
        "completed_at": None,
        "unresolved_material": deepcopy(handoff["unresolved_material"]),
        "risk_flags": deepcopy(handoff["risk_flags"]),
        "context_change_detected": False,
        "upstream_refresh_required": False,
        "upstream_context_change": None,
        "proposed_actions": [],
        "approval_refs": [],
        "authorized_actions": [],
        "failure_state": "PARTIAL" if handoff["state"] == "PARTIAL" else None,
        "resume_from": None,
    }
    validate_sync_receipt(receipt)
    return receipt


def transition_sync(receipt: dict[str, Any], target_state: str) -> dict[str, Any]:
    validate_sync_receipt(receipt)
    current_state = receipt["state"]
    if target_state not in _TRANSITIONS.get(current_state, set()):
        raise SyncValidationError(
            "ILLEGAL_SYNC_TRANSITION",
            "VALIDATION_FAILED",
            f"synchronization cannot transition from {current_state} to {target_state}",
        )
    result = deepcopy(receipt)
    result["state"] = target_state
    if target_state == "RETURNED":
        result["completed_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    validate_sync_receipt(result)
    return result


def mark_upstream_context_change(
    receipt: dict[str, Any],
    affected_facets: list[str],
    evidence_refs: list[str],
    reason: str,
) -> dict[str, Any]:
    if not affected_facets or not evidence_refs or not reason.strip():
        raise SyncValidationError(
            "CONTEXT_CHANGE_INCOMPLETE", "VALIDATION_FAILED", "context change requires facets, evidence, and reason"
        )
    changed = transition_sync(receipt, "SUPERSEDED_PENDING_ATLAS")
    changed["context_change_detected"] = True
    changed["upstream_refresh_required"] = True
    changed["upstream_context_change"] = {
        "affected_facets": list(dict.fromkeys(affected_facets)),
        "evidence_refs": list(dict.fromkeys(evidence_refs)),
        "reason": reason,
    }
    changed["failure_state"] = "PARTIAL"
    validate_sync_receipt(changed)
    return changed


def _require_receipt_handoff(receipt: dict[str, Any], handoff: dict[str, Any]) -> None:
    expected = {
        "handoff_contract_version": handoff.get("contract_version"),
        "handoff_id": handoff.get("handoff_id"),
        "payload_sha256": handoff.get("payload_sha256"),
        "source_task_id": handoff.get("source_task_id"),
        "source_plan_id": handoff.get("source_plan_id"),
        "source_work_unit_id": handoff.get("source_work_unit_id"),
    }
    if any(receipt.get("atlas", {}).get(field) != value for field, value in expected.items()):
        raise SyncValidationError(
            "SYNC_HANDOFF_STALE", "VALIDATION_FAILED", "receipt does not belong to the active handoff"
        )


def validate_result_correlation(
    result: dict[str, Any],
    handoff: dict[str, Any],
    receipt: dict[str, Any],
    *,
    trusted_public_keys: Mapping[str, bytes],
) -> dict[str, Any]:
    validate_sync_receipt(receipt)
    _require_receipt_handoff(receipt, handoff)
    validate_handoff(
        handoff,
        atlas_attestation=receipt["atlas"]["handoff_attestation"],
        trusted_public_keys=trusted_public_keys,
    )
    try:
        jsonschema.validate(result, RESULT_SCHEMA, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        raise SyncValidationError(
            "RESULT_SCHEMA_INVALID", "VALIDATION_FAILED", error.message
        ) from error
    if result.get("governance_mode") != "ATLAS_GOVERNED" or receipt.get("mode") != "ATLAS_GOVERNED":
        raise SyncValidationError(
            "GOVERNANCE_MODE_MISMATCH", "VALIDATION_FAILED", "result is not ATLAS-governed"
        )
    if receipt["state"] not in {"ACTIVE", "RESULT_READY"}:
        raise SyncValidationError(
            "SYNC_EXECUTION_NOT_CURRENT", "VALIDATION_FAILED", "synchronization execution is not current"
        )
    if result.get("sync_execution_id") != receipt["sync_execution_id"] or result.get("sync_attempt") != receipt["attempt"]:
        raise SyncValidationError(
            "RESULT_EXECUTION_MISMATCH", "VALIDATION_FAILED", "result does not belong to this synchronization attempt"
        )
    if result.get("result_sha256") != canonical_result_sha256(result):
        raise SyncValidationError(
            "RESULT_DIGEST_MISMATCH", "VALIDATION_FAILED", "result digest does not match its payload"
        )
    upstream = result.get("upstream_handoff", {})
    try:
        jsonschema.validate(upstream, HANDOFF_RECEIPT_SCHEMA, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        raise SyncValidationError(
            "RESULT_RECEIPT_INVALID", "VALIDATION_FAILED", error.message
        ) from error
    expected = {
        "contract_version": handoff["contract_version"],
        "handoff_id": handoff["handoff_id"],
        "payload_sha256": handoff["payload_sha256"],
        "consumer": "ARGUS",
        "status": "ACCEPTED",
    }
    if any(upstream.get(field) != value for field, value in expected.items()):
        raise SyncValidationError(
            "RESULT_CORRELATION_MISMATCH", "VALIDATION_FAILED", "result does not match the active handoff"
        )
    if receipt["state"] == "RESULT_READY":
        if receipt["argus"]["result_sha256"] != result["result_sha256"]:
            raise SyncValidationError(
                "RESULT_REPLAY_MISMATCH", "VALIDATION_FAILED", "a different result is already bound to this execution"
            )
        return deepcopy(receipt)
    bound = deepcopy(receipt)
    bound["argus"]["result_sha256"] = result["result_sha256"]
    bound["state"] = "RESULT_READY"
    validate_sync_receipt(bound)
    return bound


def _restart_failed_sync(
    receipt: dict[str, Any], handoff: dict[str, Any], *, trusted_public_keys: Mapping[str, bytes]
) -> dict[str, Any]:
    validate_sync_receipt(receipt)
    validate_handoff(
        handoff,
        atlas_attestation=receipt.get("atlas", {}).get("handoff_attestation", {}),
        trusted_public_keys=trusted_public_keys,
    )
    _require_receipt_handoff(receipt, handoff)
    if receipt["state"] != "FAILED":
        raise SyncValidationError(
            "SYNC_NOT_RETRYABLE", "VALIDATION_FAILED", "only a failed current execution may restart"
        )
    restarted = deepcopy(receipt)
    restarted["attempt"] += 1
    restarted["resume_from"] = receipt["state"]
    restarted["state"] = "ACTIVE"
    restarted["completed_at"] = None
    restarted["failure_state"] = "PARTIAL" if handoff["state"] == "PARTIAL" else None
    validate_sync_receipt(restarted)
    return restarted


def retry_sync(
    receipt: dict[str, Any], handoff: dict[str, Any], *, trusted_public_keys: Mapping[str, bytes]
) -> dict[str, Any]:
    return _restart_failed_sync(receipt, handoff, trusted_public_keys=trusted_public_keys)


def resume_sync(
    receipt: dict[str, Any],
    handoff: dict[str, Any],
    *,
    active_sync_execution_id: str,
    stored_registry_fingerprint: str,
    actual_registry_fingerprint: str,
    trusted_public_keys: Mapping[str, bytes],
) -> dict[str, Any]:
    if active_sync_execution_id != receipt.get("sync_execution_id"):
        raise SyncValidationError(
            "SYNC_EXECUTION_STALE", "VALIDATION_FAILED", "a different synchronization execution is active"
        )
    digest_pattern = re.compile(r"sha256:[0-9a-f]{64}")
    if not digest_pattern.fullmatch(stored_registry_fingerprint) or not digest_pattern.fullmatch(actual_registry_fingerprint):
        raise SyncValidationError(
            "REGISTRY_FINGERPRINT_INVALID", "VALIDATION_FAILED", "registry fingerprints must be SHA-256 values"
        )
    if stored_registry_fingerprint != actual_registry_fingerprint:
        raise SyncValidationError(
            "REGISTRY_FINGERPRINT_DRIFT",
            "VALIDATION_FAILED",
            "ARGUS canonical state changed and requires reconciliation",
        )
    return _restart_failed_sync(receipt, handoff, trusted_public_keys=trusted_public_keys)


def map_atlas_failure(condition: str) -> str:
    mapping = {
        "invalid": "VALIDATION_FAILED",
        "blocked": "BLOCKED",
        "dependency": "DEPENDENCY_FAILED",
        "capability": "CAPABILITY_UNAVAILABLE",
        "evidence": "EVIDENCE_INSUFFICIENT",
        "authorization": "AUTHORIZATION_REQUIRED",
        "unverified": "UNVERIFIED",
        "partial": "PARTIAL",
    }
    try:
        return mapping[condition]
    except KeyError as error:
        raise SyncValidationError(
            "UNKNOWN_SYNC_FAILURE", "VALIDATION_FAILED", f"unknown synchronization condition: {condition}"
        ) from error


def validate_action_authorization(
    action: dict[str, Any],
    approval: dict[str, Any],
    expected_scope: list[str],
    receipt: dict[str, Any],
    *,
    approval_attestation: Mapping[str, Any],
    trusted_public_keys: Mapping[str, bytes],
) -> None:
    try:
        jsonschema.validate(
            approval,
            APPROVAL_SCHEMA,
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        raise SyncValidationError(
            "APPROVAL_SCHEMA_INVALID", "AUTHORIZATION_REQUIRED", error.message
        ) from error

    if not expected_scope:
        raise SyncValidationError(
            "APPROVAL_SCOPE_EMPTY", "AUTHORIZATION_REQUIRED", "canonical mutation requires explicit scope"
        )
    try:
        _verify_atlas_attestation(approval, approval_attestation, trusted_public_keys)
    except SyncValidationError as error:
        raise SyncValidationError(
            "APPROVAL_NOT_TRUSTED", "AUTHORIZATION_REQUIRED", str(error)
        ) from error
    if approval["required"] is not True or approval["status"] != "APPROVED":
        raise SyncValidationError(
            "APPROVAL_STATUS_INVALID",
            "AUTHORIZATION_REQUIRED",
            "approval required/status combination does not authorize mutation",
        )
    if not set(expected_scope).issubset(set(approval["scope"])):
        raise SyncValidationError(
            "APPROVAL_SCOPE_MISMATCH", "AUTHORIZATION_REQUIRED", "approval scope is insufficient"
        )

    target_id = action.get("target_argus_id")
    expected = {
        "action_type": action.get("action"),
        "target_id": target_id,
        "input_sha256": _sha256_json(action),
        "precondition_revision": action.get("precondition_revision"),
        "policy_revision": action.get("policy_revision"),
        "source_task_id": receipt.get("atlas", {}).get("source_task_id"),
        "source_plan_id": receipt.get("atlas", {}).get("source_plan_id"),
        "source_work_unit_id": receipt.get("atlas", {}).get("source_work_unit_id"),
        "handoff_id": receipt.get("atlas", {}).get("handoff_id"),
    }
    if any(not value or approval.get(field) != value for field, value in expected.items()):
        raise SyncValidationError(
            "APPROVAL_ACTION_MISMATCH",
            "AUTHORIZATION_REQUIRED",
            "approval is not bound to the exact proposed action",
        )
    issued_at = datetime.fromisoformat(approval["issued_at"].replace("Z", "+00:00"))
    expires_at = datetime.fromisoformat(approval["expires_at"].replace("Z", "+00:00"))
    approved_at = datetime.fromisoformat(approval["approved_at"].replace("Z", "+00:00"))
    current = _utc_now()
    if not issued_at <= approved_at <= current < expires_at:
        raise SyncValidationError(
            "APPROVAL_EXPIRED", "AUTHORIZATION_REQUIRED", "approval is outside its validity interval"
        )


def action_idempotency_key(action: dict[str, Any]) -> str:
    return _sha256_json(action)


def authorize_action(
    receipt: dict[str, Any],
    action: dict[str, Any],
    approval: dict[str, Any],
    expected_scope: list[str],
    *,
    approval_attestation: Mapping[str, Any],
    trusted_public_keys: Mapping[str, bytes],
) -> dict[str, Any]:
    validate_sync_receipt(receipt)
    if receipt["state"] not in {"ACTIVE", "RESULT_READY"}:
        raise SyncValidationError(
            "SYNC_EXECUTION_NOT_CURRENT",
            "AUTHORIZATION_REQUIRED",
            "a non-current synchronization cannot authorize canonical mutation",
        )
    validate_action_authorization(
        action,
        approval,
        expected_scope,
        receipt,
        approval_attestation=approval_attestation,
        trusted_public_keys=trusted_public_keys,
    )
    key = action_idempotency_key(action)
    if any(entry["idempotency_key"] == key for entry in receipt["authorized_actions"]):
        return deepcopy(receipt)
    result = deepcopy(receipt)
    if action not in result["proposed_actions"]:
        result["proposed_actions"].append(deepcopy(action))
    if approval["id"] not in result["approval_refs"]:
        result["approval_refs"].append(approval["id"])
    result["authorized_actions"].append({
        "idempotency_key": key,
        "action_sha256": _sha256_json(action),
        "approval_id": approval["id"],
    })
    validate_sync_receipt(result)
    return result
