"""One deep public interface for ATLAS-governed ARGUS analysis."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from time import perf_counter_ns
from typing import Any

from tools.atlas_sync import (
    SyncValidationError,
    canonical_result_sha256,
    new_sync_receipt,
    transition_sync,
    validate_result_correlation,
    validate_sync_receipt,
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
    """Authenticated ATLAS context and lease required for one ARGUS analysis."""

    handoff: Mapping[str, Any]
    atlas_attestation: Mapping[str, Any]
    execution_lease: Mapping[str, Any]
    execution_lease_attestation: Mapping[str, Any]
    started_at: str

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
        """Validate, execute, correlate, and return one governed domain result."""

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

        try:
            payload = self._method(deepcopy(handoff))
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
