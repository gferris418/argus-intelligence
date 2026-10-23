"""Bounded ARGUS provider adapter for the current ATLAS-OS v3 runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

PRE_EXECUTION_FLOW = (
    "UNDERSTAND_AND_NORMALIZE",
    "MINIMAL_DOMAIN_FRAMING",
    "ROUTE",
)
_ALLOWED_MECHANISMS = frozenset({"ARGUS", "MULTI_CAPABILITY"})
_RESERVED_RESULT_FIELDS = frozenset(
    {"source_task_id", "provider", "capability", "status", "return_target", "next_step_authority"}
)

CollectionMethod = Callable[[dict[str, Any]], Mapping[str, Any]]

_COLLECTION_PACKAGE_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "intelligence-collection-package.schema.json").read_text(
        encoding="utf-8"
    )
)


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, Mapping)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return False


def _validate_schema(value: Any, schema: Mapping[str, Any], path: str) -> None:
    expected = schema.get("type")
    if expected is not None:
        choices = [expected] if isinstance(expected, str) else list(expected)
        if not any(_matches_type(value, choice) for choice in choices):
            label = "an array" if choices == ["array"] else " or ".join(choices)
            raise ValueError(f"ARGUS collection package {path} must be {label}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"ARGUS collection package has an invalid {path}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValueError(f"ARGUS collection package {path} is too short")
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            raise ValueError(f"ARGUS collection package {path} has an invalid format")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError(f"ARGUS collection package {path} is below its minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError(f"ARGUS collection package {path} exceeds its maximum")

    if isinstance(value, Mapping):
        missing = sorted(set(schema.get("required", [])) - set(value))
        if missing:
            raise ValueError(
                f"ARGUS collection package {path} missing required fields: " + ", ".join(missing)
            )
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unsupported = sorted(set(value) - set(properties))
            if unsupported:
                raise ValueError(
                    f"ARGUS collection package {path} contains unsupported fields: "
                    + ", ".join(unsupported)
                )
        for key, item in value.items():
            if key in properties:
                child = key if path == "root" else f"{path}.{key}"
                _validate_schema(item, properties[key], child)

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            _validate_schema(item, schema["items"], f"{path}[{index}]")


def _validate_collection_package(payload: Mapping[str, Any]) -> None:
    _validate_schema(payload, _COLLECTION_PACKAGE_SCHEMA, "root")


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
    return_target: str = "ATLAS"
    next_step_authority: str = "ATLAS"


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
        if route.get("mechanism") not in _ALLOWED_MECHANISMS:
            raise ValueError("ATLAS did not route this mission to ARGUS")
        capability = str(route.get("capability", ""))
        provider = str(route.get("provider", ""))
        if "intelligence_collection" not in capability or "argus" not in provider:
            raise ValueError("ATLAS route does not grant ARGUS intelligence collection")
        if route.get("approval_required") is not True or route.get("approval_status") != "APPROVED":
            raise ValueError("explicit ATLAS ARGUS activation approval is required")
        if atlas_result.get("next_step_authority") != "ATLAS":
            raise ValueError("ATLAS must remain next-step authority")
        if atlas_result.get("provider_return_target") != "ATLAS":
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
        _validate_collection_package(payload)
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
                "return_target": "ATLAS",
                "next_step_authority": "ATLAS",
            }
        )
        return ProviderOutcome(
            provider="ARGUS",
            capability="intelligence_collection",
            result=result,
        )


__all__ = ["ArgusProvider", "ProviderEnvelope", "ProviderOutcome"]
