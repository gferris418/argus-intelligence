"""Governed synchronization validation for generic ARGUS collection packages."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from tools.atlas_sync import (
    SyncValidationError,
    canonical_result_sha256,
    validate_execution_lease,
    validate_handoff_integrity,
    validate_sync_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_RESULT_SCHEMA = json.loads(
    (ROOT / "schemas/intelligence-collection-package.schema.json").read_text(encoding="utf-8")
)
_COLLECTION_RESULT_VALIDATOR = jsonschema.Draft202012Validator(
    COLLECTION_RESULT_SCHEMA,
    format_checker=jsonschema.FormatChecker(),
)


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
            "SYNC_HANDOFF_STALE",
            "VALIDATION_FAILED",
            "receipt does not belong to the active handoff",
        )


def _validate_receipt_lease(
    receipt: dict[str, Any],
    handoff: dict[str, Any],
    *,
    trusted_key_registry: Mapping[str, Any],
) -> None:
    atlas = receipt.get("atlas", {})
    execution_lease = atlas.get("execution_lease")
    lease_attestation = atlas.get("execution_lease_attestation")
    lease_id = atlas.get("execution_lease_id")
    if execution_lease is None or lease_attestation is None or not lease_id:
        raise SyncValidationError(
            "EXECUTION_LEASE_REQUIRED",
            "VALIDATION_FAILED",
            "ATLAS-governed collection requires a current execution lease",
        )
    validate_execution_lease(
        execution_lease,
        handoff,
        lease_attestation=lease_attestation,
        trusted_key_registry=trusted_key_registry,
        expected_lease_id=lease_id,
    )


def validate_collection_result_correlation(
    result: dict[str, Any],
    handoff: dict[str, Any],
    receipt: dict[str, Any],
    *,
    trusted_key_registry: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and bind a generic intelligence collection package to one ATLAS execution."""

    validate_sync_receipt(receipt)
    _require_receipt_handoff(receipt, handoff)
    validate_handoff_integrity(
        handoff,
        atlas_attestation=receipt["atlas"]["handoff_attestation"],
        trusted_key_registry=trusted_key_registry,
    )
    _validate_receipt_lease(
        receipt,
        handoff,
        trusted_key_registry=trusted_key_registry,
    )

    try:
        _COLLECTION_RESULT_VALIDATOR.validate(result)
    except jsonschema.ValidationError as error:
        raise SyncValidationError(
            "COLLECTION_RESULT_SCHEMA_INVALID",
            "VALIDATION_FAILED",
            error.message,
        ) from error

    if result.get("governance_mode") != "ATLAS_GOVERNED" or receipt.get("mode") != "ATLAS_GOVERNED":
        raise SyncValidationError(
            "GOVERNANCE_MODE_MISMATCH",
            "VALIDATION_FAILED",
            "collection result is not ATLAS-governed",
        )
    if receipt["state"] not in {"ACTIVE", "RESULT_READY"}:
        raise SyncValidationError(
            "SYNC_EXECUTION_NOT_CURRENT",
            "VALIDATION_FAILED",
            "synchronization execution is not current",
        )
    if result.get("sync_execution_id") != receipt["sync_execution_id"] or result.get("sync_attempt") != receipt["attempt"]:
        raise SyncValidationError(
            "RESULT_EXECUTION_MISMATCH",
            "VALIDATION_FAILED",
            "collection result does not belong to this synchronization attempt",
        )
    if result.get("result_sha256") != canonical_result_sha256(result):
        raise SyncValidationError(
            "RESULT_DIGEST_MISMATCH",
            "VALIDATION_FAILED",
            "collection result digest does not match its payload",
        )

    upstream = result.get("upstream_handoff") or {}
    expected_upstream = {
        "contract_version": handoff["contract_version"],
        "handoff_id": handoff["handoff_id"],
        "payload_sha256": handoff["payload_sha256"],
        "consumer": "ARGUS",
        "status": "ACCEPTED",
    }
    if any(upstream.get(field) != value for field, value in expected_upstream.items()) or not upstream.get("received_at"):
        raise SyncValidationError(
            "RESULT_CORRELATION_MISMATCH",
            "VALIDATION_FAILED",
            "collection result does not match the active handoff",
        )

    if receipt["state"] == "RESULT_READY":
        if receipt["argus"]["result_sha256"] != result["result_sha256"]:
            raise SyncValidationError(
                "RESULT_REPLAY_MISMATCH",
                "VALIDATION_FAILED",
                "a different result is already bound to this execution",
            )
        return deepcopy(receipt)

    bound = deepcopy(receipt)
    bound["argus"]["result_sha256"] = result["result_sha256"]
    bound["state"] = "RESULT_READY"
    validate_sync_receipt(bound)
    return bound


__all__ = ["validate_collection_result_correlation"]
