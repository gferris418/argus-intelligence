"""Pure synchronization controls for ATLAS-governed ARGUS execution."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCHEMA = json.loads(
    (ROOT / "contracts/atlas/domain-context-handoff-v1.schema.json").read_text(encoding="utf-8")
)
SYNC_SCHEMA = json.loads(
    (ROOT / "schemas/atlas-argus-sync-receipt.schema.json").read_text(encoding="utf-8")
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


def canonical_handoff_sha256(handoff: dict[str, Any]) -> str:
    payload = {key: value for key, value in handoff.items() if key != "payload_sha256"}
    return _sha256_json(payload)


def validate_handoff(handoff: dict[str, Any]) -> None:
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
    if handoff.get("payload_sha256") != canonical_handoff_sha256(handoff):
        raise SyncValidationError(
            "HANDOFF_DIGEST_MISMATCH", "VALIDATION_FAILED", "handoff digest does not match payload"
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
    sync_execution_id: str,
    handoff: dict[str, Any],
    started_at: str,
) -> dict[str, Any]:
    validate_handoff(handoff)
    receipt = {
        "sync_execution_id": sync_execution_id,
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
) -> None:
    validate_handoff(handoff)
    validate_sync_receipt(receipt)
    if result.get("governance_mode") != "ATLAS_GOVERNED" or receipt.get("mode") != "ATLAS_GOVERNED":
        raise SyncValidationError(
            "GOVERNANCE_MODE_MISMATCH", "VALIDATION_FAILED", "result is not ATLAS-governed"
        )
    if receipt["state"] not in {"ACTIVE", "RESULT_READY"}:
        raise SyncValidationError(
            "SYNC_EXECUTION_NOT_CURRENT", "VALIDATION_FAILED", "synchronization execution is not current"
        )
    _require_receipt_handoff(receipt, handoff)
    upstream = result.get("upstream_handoff", {})
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


def _restart_failed_sync(receipt: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    validate_sync_receipt(receipt)
    validate_handoff(handoff)
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


def retry_sync(receipt: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    return _restart_failed_sync(receipt, handoff)


def resume_sync(
    receipt: dict[str, Any],
    handoff: dict[str, Any],
    *,
    active_sync_execution_id: str,
    stored_registry_fingerprint: str,
    actual_registry_fingerprint: str,
) -> dict[str, Any]:
    if active_sync_execution_id != receipt.get("sync_execution_id"):
        raise SyncValidationError(
            "SYNC_EXECUTION_STALE", "VALIDATION_FAILED", "a different synchronization execution is active"
        )
    if stored_registry_fingerprint != actual_registry_fingerprint:
        raise SyncValidationError(
            "REGISTRY_FINGERPRINT_DRIFT",
            "VALIDATION_FAILED",
            "ARGUS canonical state changed and requires reconciliation",
        )
    return _restart_failed_sync(receipt, handoff)


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
