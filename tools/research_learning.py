"""Validation helpers for ARGUS per-search learning records."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = json.loads(
    (ROOT / "schemas/research-learning-record.schema.json").read_text(encoding="utf-8")
)
_VALIDATOR = jsonschema.Draft202012Validator(
    _SCHEMA,
    format_checker=jsonschema.FormatChecker(),
)


def validate_learning_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a defensive copy of one research learning record."""

    if not isinstance(record, Mapping):
        raise TypeError("research learning record must be a mapping")

    candidate = deepcopy(dict(record))
    try:
        _VALIDATOR.validate(candidate)
    except jsonschema.ValidationError as error:
        raise ValueError(f"invalid research learning record: {error.message}") from error

    if candidate["useful_result_count"] > candidate["results_examined"]:
        raise ValueError("useful_result_count cannot exceed results_examined")

    return candidate


def heuristic_state(*, observation_count: int, backtested: bool) -> str:
    """Return the guarded promotion state for a learned research pattern."""

    if isinstance(observation_count, bool) or not isinstance(observation_count, int):
        raise TypeError("observation_count must be an integer")
    if observation_count < 1:
        raise ValueError("observation_count must be at least 1")
    if backtested and observation_count < 2:
        raise ValueError("a single observation cannot become a validated heuristic")
    if backtested:
        return "VALIDATED_HEURISTIC"
    if observation_count >= 2:
        return "REPEATED_PATTERN"
    return "OBSERVED"


__all__ = ["heuristic_state", "validate_learning_record"]
