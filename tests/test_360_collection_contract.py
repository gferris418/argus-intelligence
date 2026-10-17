"""Contract test for ARGUS 360-degree intelligence collection.

This intentionally uses only the Python standard library so the repository has a
portable executable gate before a larger test stack is introduced.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "argus-intelligence.yaml"
SCHEMA = ROOT / "schemas" / "domain-result.schema.json"
CORE = ROOT / "spec" / "core.md"
PROFILE = ROOT / "profiles" / "bangladesh.md"

LENSES = {
    "need_mission",
    "policy_strategy",
    "institution_stakeholders",
    "programme_project",
    "budget_funding",
    "procurement_acquisition",
    "technical_installed_base",
    "supplier_competitor",
    "ecosystem_influence",
    "commercial_participation",
    "timing_triggers",
    "internal_intelligence",
}


def test_manifest_declares_360_collection_doctrine() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    assert "360_intelligence_collection:" in text
    assert "breadth: all_materially_relevant_lenses" in text
    assert "depth: decision_driven_by_research_frontier" in text


def test_core_defines_all_collection_lenses() -> None:
    text = CORE.read_text(encoding="utf-8")
    assert "360° Intelligence Collection Doctrine" in text
    for lens in LENSES:
        assert f"`{lens}`" in text


def test_domain_result_schema_exposes_coverage_and_gaps() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    props = schema["properties"]
    assert "collection_coverage" in props
    assert "collection_gaps" in props
    coverage = props["collection_coverage"]
    assert set(coverage["properties"].keys()) == LENSES
    states = coverage["additionalProperties"] if isinstance(coverage.get("additionalProperties"), dict) else None
    assert states is None, "coverage must enumerate governed lenses, not arbitrary keys"


def test_bangladesh_profile_maps_core_lenses_to_country_collection() -> None:
    text = PROFILE.read_text(encoding="utf-8")
    assert "Bangladesh 360° Collection Map" in text
    for lens in LENSES:
        assert f"`{lens}`" in text


def test_coverage_states_are_governed() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    lens_schema = next(iter(schema["properties"]["collection_coverage"]["properties"].values()))
    assert lens_schema["enum"] == [
        "NOT_APPLICABLE",
        "UNASSESSED",
        "INSUFFICIENT",
        "PARTIAL",
        "ADEQUATE",
    ]
