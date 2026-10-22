"""One deep public interface for ATLAS-governed ARGUS analysis and collection."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Any

import jsonschema

from tools.atlas_sync import (
    SyncValidationError,
    canonical_result_sha256,
    new_sync_receipt,
    transition_sync,
    validate_result_correlation,
    validate_sync_receipt,
)
from tools.collection_sync import validate_collection_result_correlation

ROOT = Path(__file__).resolve().parents[1]
_COLLECTION_MISSION_SCHEMA = json.loads(
    (ROOT / "schemas/collection-mission.schema.json").read_text(encoding="utf-8")
)
_COLLECTION_MISSION_VALIDATOR = jsonschema.Draft202012Validator(
    _COLLECTION_MISSION_SCHEMA,
    format_checker=jsonschema.FormatChecker(),
)

_RESERVED_RESULT_FIELDS = {
    "governance_mode",
    "sync_execution_id",
    "sync_attempt",
    "result_sha256",
    "upstream_handoff",
}

AnalysisMethod = Callable[[dict[str, Any]], Mapping[str, Any]]


class AnalysisExecutionError(RuntimeError):
    """Carries retryable synchronization state after domain-method failure."""

    def __init__(self, receipt: dict[str, Any]) -> None:
        super().__init__("ARGUS domain method failed")
        self.receipt = deepcopy(receipt)


@dataclass(frozen=True)
class AnalysisEnvelope:
    """Authenticated ATLAS context, lease, and optional collection mission for one ARGUS execution."""

    handoff: Mapping[str, Any]
    atlas_attestation: Mapping[str, Any]
    execution_lease: Mapping[str, Any]
    execution_lease_attestation: Mapping[str, Any]
    started_at: str
    collection_mission: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.started_at.strip():
            raise ValueError("analysis started_at is required")
        for field_name in (
            "handoff",
            "atlas_attestation",
            "execution_lease",
            "execution_lease_attestation",
        ):
            value = dict(getattr(self, field_name))
            if not value:
                raise ValueError(f"analysis {field_name} is required")
            object.__setattr__(self, field_name, deepcopy(value))

        if self.collection_mission is not None:
            mission = deepcopy(dict(self.collection_mission))
            try:
                _COLLECTION_MISSION_VALIDATOR.validate(mission)
            except jsonschema.ValidationError as error:
                raise ValueError(f"invalid collection mission: {error.message}") from error
            handoff = dict(self.handoff)
            if mission["source_task_id"] != handoff.get("source_task_id"):
                raise ValueError("collection mission source_task_id does not match authenticated handoff")
            if mission["source_plan_id"] != handoff.get("source_plan_id"):
                raise ValueError("collection mission source_plan_id does not match authenticated handoff")
            object.__setattr__(self, "collection_mission", mission)


@dataclass(frozen=True)
class AnalysisOutcome:
    """Correlated ARGUS result and final synchronization receipt."""

    result: dict[str, Any]
    receipt: dict[str, Any]
    duration_ms: int

    @property
    def compact_status(self) -> str:
        result = self.result
        receipt = self.receipt
        if "collection_status" in result:
            return "\n".join((
                f"ARGUS {receipt['state']} | {self.duration_ms} ms | {receipt['sync_execution_id']}",
                f"Objective {result['objective']} | Collection {result['collection_status']} | Targets {len(result['resolved_targets'])}",
                f"Evidence {len(result['evidence'])} | Gaps {len(result['collection_gaps'])} | Unknowns {len(result['unknowns_conflicts'])}",
            ))
        return "\n".join((
            f"ARGUS {receipt['state']} | {self.duration_ms} ms | {receipt['sync_execution_id']}",
            f"Objective {result['objective']} | Decision {result['decision']} | Maturity {result['maturity']}",
            f"Evidence {len(result['evidence'])} | Unknowns {len(result['unknowns_conflicts'])} | "
            f"Next {result['next_recommended_action']}",
        ))


class Argus:
    """Run one domain method behind the governed synchronization seam."""

    def __init__(
        self,
        method: AnalysisMethod,
        *,
        trusted_key_registry: Mapping[str, Any],
    ) -> None:
        if not callable(method):
            raise TypeError("ARGUS analysis method must be callable")
        registry = deepcopy(dict(trusted_key_registry))
        if not registry or not registry.get("keys"):
            raise ValueError("ARGUS requires a lifecycle-governed ATLAS signing-key registry")
        self._method = method
        self._trusted_key_registry = registry

    def analyze(self, envelope: AnalysisEnvelope) -> AnalysisOutcome:
        """Validate, execute, correlate, and return one governed domain result or collection package."""

        started = perf_counter_ns()
        handoff = deepcopy(dict(envelope.handoff))
        receipt = new_sync_receipt(
            handoff,
            envelope.started_at,
            atlas_attestation=envelope.atlas_attestation,
            execution_lease=deepcopy(dict(envelope.execution_lease)),
            execution_lease_attestation=envelope.execution_lease_attestation,
            trusted_key_registry=self._trusted_key_registry,
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            receipt = transition_sync(receipt, state)

        method_input = deepcopy(handoff)
        if envelope.collection_mission is not None:
            mission = deepcopy(dict(envelope.collection_mission))
            execution_policy = deepcopy(dict(mission["execution_policy"]))
            method_input = {
                "handoff": deepcopy(handoff),
                "collection_mission": mission,
                "mission_context_policy": {
                    "storage": execution_policy["mission_context"],
                    "startup_sequence": deepcopy(execution_policy["startup_sequence"]),
                    "follow_evidence_leads_without_callback": execution_policy["follow_evidence_leads_without_callback"],
                    "parallel_safe_reads": execution_policy["parallel_safe_reads"],
                },
            }

        try:
            payload = self._method(method_input)
        except Exception as error:
            failed = transition_sync(receipt, "FAILED")
            failed["failure_state"] = "DEPENDENCY_FAILED"
            validate_sync_receipt(failed)
            raise AnalysisExecutionError(failed) from error
        if not isinstance(payload, Mapping):
            raise SyncValidationError(
                "DOMAIN_RESULT_INVALID",
                "VALIDATION_FAILED",
                "ARGUS analysis method must return a mapping",
            )
        reserved = sorted(_RESERVED_RESULT_FIELDS & set(payload))
        if reserved:
            raise SyncValidationError(
                "DOMAIN_RESULT_RESERVED_FIELD",
                "VALIDATION_FAILED",
                f"ARGUS analysis method returned governed fields: {', '.join(reserved)}",
            )

        result = deepcopy(dict(payload))
        result.update({
            "governance_mode": "ATLAS_GOVERNED",
            "sync_execution_id": receipt["sync_execution_id"],
            "sync_attempt": receipt["attempt"],
            "upstream_handoff": {
                "contract_version": handoff["contract_version"],
                "handoff_id": handoff["handoff_id"],
                "payload_sha256": handoff["payload_sha256"],
                "consumer": "ARGUS",
                "status": "ACCEPTED",
                "received_at": envelope.started_at,
            },
        })
        result["result_sha256"] = canonical_result_sha256(result)

        if "collection_status" in result:
            if envelope.collection_mission is None:
                raise SyncValidationError(
                    "COLLECTION_MISSION_REQUIRED",
                    "VALIDATION_FAILED",
                    "generic collection packages require a validated collection mission",
                )
            receipt = validate_collection_result_correlation(
                result,
                handoff,
                receipt,
                trusted_key_registry=self._trusted_key_registry,
            )
        else:
            receipt = validate_result_correlation(
                result,
                handoff,
                receipt,
                trusted_key_registry=self._trusted_key_registry,
            )
        receipt = transition_sync(receipt, "RETURNED")
        duration_ms = max(0, round((perf_counter_ns() - started) / 1_000_000))
        return AnalysisOutcome(result=result, receipt=receipt, duration_ms=duration_ms)


__all__ = [
    "AnalysisEnvelope",
    "AnalysisExecutionError",
    "AnalysisOutcome",
    "Argus",
    "SyncValidationError",
]
