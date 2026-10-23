from __future__ import annotations

from datetime import datetime
from math import isfinite
from typing import Mapping


OPPORTUNITY_WEIGHTS = {
    "strategic_fit": 0.20,
    "commercial_attractiveness": 0.20,
    "procurement_probability": 0.20,
    "supplier_availability": 0.15,
    "access_advantage": 0.15,
    "competitive_difficulty": 0.10,
}

SUPPLIER_MATCH_WEIGHTS = {
    "technical_fit": 0.25,
    "relevant_references": 0.15,
    "tender_eligibility": 0.10,
    "export_feasibility": 0.10,
    "price_competitiveness": 0.10,
    "bangladesh_fit": 0.10,
    "local_support_capability": 0.05,
    "willingness_to_partner": 0.10,
    "relationship_access": 0.05,
}


def _validate_scores(scores: Mapping[str, float], allowed: set[str]) -> None:
    unknown = set(scores) - allowed
    if unknown:
        raise ValueError(f"unknown score dimensions: {sorted(unknown)}")
    for name, value in scores.items():
        if isinstance(value, bool):
            raise ValueError(f"{name} must be a finite number between 0 and 100")
        numeric = float(value)
        if not isfinite(numeric) or not 0 <= numeric <= 100:
            raise ValueError(f"{name} must be between 0 and 100")


def _validated_weights(weights: Mapping[str, float]) -> dict[str, float]:
    if any(isinstance(value, bool) for value in weights.values()):
        raise ValueError("weights must be finite numbers")
    normalized = {name: float(value) for name, value in weights.items()}
    if any(not isfinite(value) for value in normalized.values()):
        raise ValueError("weights must be finite numbers")
    if any(value < 0 for value in normalized.values()):
        raise ValueError("weights cannot be negative")
    total = sum(normalized.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError("weights must sum to 1.0")
    return normalized


def score_opportunity(
    scores: Mapping[str, float],
    weights: Mapping[str, float] | None = None,
) -> dict[str, float | str]:
    effective_weights = _validated_weights(weights or OPPORTUNITY_WEIGHTS)
    _validate_scores(scores, set(effective_weights))
    missing = set(effective_weights) - set(scores)
    if missing:
        raise ValueError(f"missing score dimensions: {sorted(missing)}")
    weighted_score = round(
        sum(float(scores[name]) * weight for name, weight in effective_weights.items()),
        2,
    )
    if weighted_score >= 80:
        band = "PRIORITY"
    elif weighted_score >= 65:
        band = "ACTIVE"
    elif weighted_score >= 50:
        band = "WATCH"
    else:
        band = "MONITOR"
    return {"score": weighted_score, "recommended_priority_band": band}


def score_supplier_match(
    scores: Mapping[str, float],
    weights: Mapping[str, float] | None = None,
) -> dict[str, float]:
    effective_weights = _validated_weights(weights or SUPPLIER_MATCH_WEIGHTS)
    _validate_scores(scores, set(effective_weights))
    supplied_weight = sum(effective_weights[name] for name in scores)
    if supplied_weight <= 0:
        raise ValueError("at least one weighted supplier-match dimension is required")
    weighted_score = sum(float(scores[name]) * effective_weights[name] for name in scores)
    normalized_score = round(weighted_score / supplied_weight, 2)
    confidence = round(supplied_weight, 4)
    return {"score": normalized_score, "confidence": confidence}


def detection_lag_hours(earliest_observable_at: datetime, detected_at: datetime) -> float:
    if earliest_observable_at.tzinfo is None or detected_at.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    delta = detected_at - earliest_observable_at
    if delta.total_seconds() < 0:
        raise ValueError("detected_at cannot precede earliest_observable_at")
    return round(delta.total_seconds() / 3600.0, 2)
