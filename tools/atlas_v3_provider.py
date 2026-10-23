"""Bounded ARGUS provider adapter for the current ATLAS-OS v3 runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .atlas_contract import ATLAS_EXECUTION_CONTRACT, ROUTE_CONTRACTS

PRE_EXECUTION_FLOW = tuple(ATLAS_EXECUTION_CONTRACT["pre_execution_flow"])
_ALLOWED_MECHANISMS = frozenset(ROUTE_CONTRACTS)
_PRIMARY_CAPABILITY = ROUTE_CONTRACTS["ARGUS"][0]
_RETURN_TARGET = str(ATLAS_EXECUTION_CONTRACT["provider_return_target"])
_NEXT_STEP_AUTHORITY = str(ATLAS_EXECUTION_CONTRACT["next_step_authority"])
_RESERVED_RESULT_FIELDS = frozenset(
    {"source_task_id", "provider", "capability", "status", "return_target", "next_step_authority"}
)

CollectionMethod = Callable[[dict[str, Any]], Mapping[str, Any]]


@dataclass(frozen=True)
class ProviderEnvelope:
    """One already-approved ATLAS route handed to the bounded ARGUS provider."""

    atlas_result: Mapping[str, Any]

    def __post_init__(self) -> None:
        value = deepcopy(dict(self.atlas_result))
        if not value:
            raise ValueError("atlas_result is required")
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

    def __init__(self, method: CollectionMethod) -> None:
        if not callable(method):
            raise TypeError("ARGUS provider method must be callable")
        self._method = method

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
        expected_capability, expected_provider = ROUTE_CONTRACTS[mechanism]
        if (
            route.get("capability") != expected_capability
            or route.get("provider") != expected_provider
        ):
            raise ValueError("ATLAS route does not grant ARGUS intelligence collection")
        if route.get("approval_required") is not True or route.get("approval_status") != "APPROVED":
            raise ValueError("explicit ATLAS ARGUS activation approval is required")
        if atlas_result.get("next_step_authority") != _NEXT_STEP_AUTHORITY:
            raise ValueError("ATLAS must remain next-step authority")
        if atlas_result.get("provider_return_target") != _RETURN_TARGET:
            raise ValueError("ARGUS provider result must return to ATLAS")
        if not str(atlas_result.get("task_id", "")).strip():
            raise ValueError("ATLAS task_id is required")

    def execute(self, envelope: ProviderEnvelope) -> ProviderOutcome:
        atlas_result = deepcopy(dict(envelope.atlas_result))
        self._validate_atlas_result(atlas_result)
        context = {
            "source_task_id": atlas_result["task_id"],
            "objective": atlas_result.get("normalized_objective"),
            "domain_framing": deepcopy(dict(atlas_result.get("domain_framing", {}))),
            "route": deepcopy(dict(atlas_result["route"])),
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
                "capability": _PRIMARY_CAPABILITY,
                "status": "RETURNED",
                "return_target": _RETURN_TARGET,
                "next_step_authority": _NEXT_STEP_AUTHORITY,
            }
        )
        return ProviderOutcome(
            provider="ARGUS",
            capability=_PRIMARY_CAPABILITY,
            result=result,
        )


__all__ = [
    "ArgusProvider",
    "PRE_EXECUTION_FLOW",
    "ProviderEnvelope",
    "ProviderOutcome",
    "ROUTE_CONTRACTS",
]
