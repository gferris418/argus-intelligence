"""Bounded ARGUS provider adapter for the current ATLAS-OS v3 runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tools.atlas_capability import InMemoryReplayGuard, ReplayGuard, verify_remote_capability


ROOT = Path(__file__).resolve().parents[1]
CURRENT_INTEGRATION_PATH = ROOT / "contracts" / "atlas" / "current-integration.yaml"


def _load_execution_projection(path: Path = CURRENT_INTEGRATION_PATH) -> dict[str, Any]:
    descriptor = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(descriptor, dict) or descriptor.get("status") != "CURRENT":
        raise ValueError("ATLAS integration projection must be CURRENT")
    contract = descriptor.get("contract")
    if not isinstance(contract, dict):
        raise ValueError("ATLAS integration projection lacks contract")
    routes = contract.get("route_contracts")
    if not isinstance(routes, dict) or not routes:
        raise ValueError("ATLAS integration projection lacks route contracts")
    return contract


_EXECUTION_PROJECTION = _load_execution_projection()
PRE_EXECUTION_FLOW = tuple(_EXECUTION_PROJECTION["pre_execution_flow"])
_ROUTE_CONTRACTS = {
    mechanism: (str(details["capability"]), str(details["provider"]))
    for mechanism, details in _EXECUTION_PROJECTION["route_contracts"].items()
}
_ALLOWED_MECHANISMS = frozenset(_ROUTE_CONTRACTS)
_RETURN_TARGET = str(_EXECUTION_PROJECTION["provider_return_target"])
_NEXT_STEP_AUTHORITY = str(_EXECUTION_PROJECTION["next_step_authority"])
_RESERVED_RESULT_FIELDS = frozenset(
    {"source_task_id", "provider", "capability", "status", "return_target", "next_step_authority"}
)

CollectionMethod = Callable[[dict[str, Any]], Mapping[str, Any]]
SecretResolver = Callable[[str], bytes | None]


@dataclass(frozen=True)
class ProviderEnvelope:
    """One already-approved ATLAS route handed to the bounded ARGUS provider."""

    atlas_result: Mapping[str, Any]
    transport: str = "local"
    remote_capability: str | None = None
    remote_now: int | None = None

    def __post_init__(self) -> None:
        value = deepcopy(dict(self.atlas_result))
        if not value:
            raise ValueError("atlas_result is required")
        if self.transport not in {"local", "remote"}:
            raise ValueError("transport must be local or remote")
        if self.transport == "remote":
            if not isinstance(self.remote_capability, str) or not self.remote_capability:
                raise ValueError("remote transport requires an ATLAS capability")
            if isinstance(self.remote_now, bool) or not isinstance(self.remote_now, int) or self.remote_now < 0:
                raise ValueError("remote transport requires a non-negative integer timestamp")
        elif self.remote_capability is not None or self.remote_now is not None:
            raise ValueError("remote capability fields are valid only for remote transport")
        object.__setattr__(self, "atlas_result", value)


@dataclass(frozen=True)
class ProviderOutcome:
    """ARGUS collection result returned to ATLAS for reconciliation."""

    provider: str
    capability: str
    result: dict[str, Any]
    return_target: str = _RETURN_TARGET
    next_step_authority: str = _NEXT_STEP_AUTHORITY


class ArgusProvider:
    """Execute one bounded intelligence-collection mission selected by ATLAS."""

    def __init__(
        self,
        method: CollectionMethod,
        *,
        remote_secret_resolver: SecretResolver | None = None,
        replay_guard: ReplayGuard | None = None,
    ) -> None:
        if not callable(method):
            raise TypeError("ARGUS provider method must be callable")
        if remote_secret_resolver is not None and not callable(remote_secret_resolver):
            raise TypeError("remote_secret_resolver must be callable")
        if replay_guard is not None and not callable(getattr(replay_guard, "consume", None)):
            raise TypeError("replay_guard must provide consume(jti, exp, now)")
        self._method = method
        self._remote_secret_resolver = remote_secret_resolver
        self._replay_guard = replay_guard or InMemoryReplayGuard()

    @staticmethod
    def _validate_atlas_result(atlas_result: Mapping[str, Any]) -> None:
        route = atlas_result.get("route")
        if not isinstance(route, Mapping):
            raise ValueError("ATLAS route is required")
        if atlas_result.get("state") != "READY":
            raise ValueError("ARGUS requires an ATLAS route in READY state")
        if tuple(atlas_result.get("pre_execution_flow", ())) != PRE_EXECUTION_FLOW:
            raise ValueError("ATLAS pre-execution flow does not match the current contract")
        mechanism = route.get("mechanism")
        if mechanism not in _ALLOWED_MECHANISMS:
            raise ValueError("ATLAS did not route this mission to ARGUS")
        expected_capability, expected_provider = _ROUTE_CONTRACTS[str(mechanism)]
        if route.get("capability") != expected_capability or route.get("provider") != expected_provider:
            raise ValueError("ATLAS route does not grant ARGUS intelligence collection")
        if route.get("approval_required") is not True or route.get("approval_status") != "APPROVED":
            raise ValueError("explicit ATLAS ARGUS activation approval is required")
        if atlas_result.get("next_step_authority") != _NEXT_STEP_AUTHORITY:
            raise ValueError("ATLAS must remain next-step authority")
        if atlas_result.get("provider_return_target") != _RETURN_TARGET:
            raise ValueError("ARGUS provider result must return to ATLAS")
        if not str(atlas_result.get("task_id", "")).strip():
            raise ValueError("ATLAS task_id is required")
        if not str(atlas_result.get("normalized_objective", "")).strip():
            raise ValueError("ATLAS normalized objective is required")

    def _verify_remote_transport(self, envelope: ProviderEnvelope, atlas_result: Mapping[str, Any]) -> None:
        if envelope.transport != "remote":
            return
        if self._remote_secret_resolver is None:
            raise ValueError("remote ARGUS transport requires an ATLAS capability secret resolver")
        try:
            verify_remote_capability(
                envelope.remote_capability or "",
                self._remote_secret_resolver,
                task_id=str(atlas_result["task_id"]),
                intent=str(atlas_result["normalized_objective"]),
                replay_guard=self._replay_guard,
                now=int(envelope.remote_now),
            )
        except ValueError as exc:
            raise ValueError(f"remote ATLAS capability rejected: {exc}") from exc

    def execute(self, envelope: ProviderEnvelope) -> ProviderOutcome:
        atlas_result = deepcopy(dict(envelope.atlas_result))
        self._validate_atlas_result(atlas_result)
        self._verify_remote_transport(envelope, atlas_result)
        context = {
            "source_task_id": atlas_result["task_id"],
            "objective": atlas_result.get("normalized_objective"),
            "domain_framing": deepcopy(dict(atlas_result.get("domain_framing", {}))),
            "route": deepcopy(dict(atlas_result["route"])),
            "transport": envelope.transport,
        }
        payload = self._method(context)
        if not isinstance(payload, Mapping):
            raise ValueError("ARGUS provider method must return a mapping")
        reserved = sorted(_RESERVED_RESULT_FIELDS & set(payload))
        if reserved:
            raise ValueError(f"ARGUS provider method returned governed fields: {', '.join(reserved)}")
        result = deepcopy(dict(payload))
        result.update(
            {
                "source_task_id": atlas_result["task_id"],
                "provider": "ARGUS",
                "capability": "intelligence_collection",
                "status": "RETURNED",
                "return_target": _RETURN_TARGET,
                "next_step_authority": _NEXT_STEP_AUTHORITY,
            }
        )
        return ProviderOutcome(
            provider="ARGUS",
            capability="intelligence_collection",
            result=result,
        )


__all__ = ["ArgusProvider", "ProviderEnvelope", "ProviderOutcome"]
