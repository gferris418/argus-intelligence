#!/usr/bin/env python3
"""Pure rehearsal transformer from legacy ARGUS registry PROCUREMENT to Bangladesh v2.

This module intentionally does not read current overlays and does not write canonical files.
Its CLI accepts a JSONL input path and prints transformed PROCUREMENT payloads to stdout.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

CLAIM_TYPES = {"FACT", "DERIVED", "INFERENCE", "ASSUMPTION", "UNKNOWN"}
CONDITIONS = {"CURRENT", "STALE", "CONFLICT", "UNKNOWN"}


def _observed_at(record: dict[str, Any]) -> str:
    return str(record.get("updated_at") or record.get("created_at") or "UNKNOWN")


def _preserved_observation(
    record: dict[str, Any],
    *,
    observation_id: str,
    field_path: str,
    value: Any,
    raw_label: str,
) -> dict[str, Any]:
    return {
        "observation_id": observation_id,
        "field_path": field_path,
        "value": copy.deepcopy(value),
        "raw_label": raw_label,
        "raw_value": copy.deepcopy(value),
        "source_id": record["argus_id"],
        "source_system": "ARGUS_LEGACY_REGISTRY",
        "source_locator": "data/registry/records.jsonl",
        "observed_at": _observed_at(record),
        "claim_type": "UNKNOWN",
        "condition": "STALE",
        "assurance": "LEGACY_PRESERVED",
    }


def _evidence_observation(
    record: dict[str, Any], evidence: dict[str, Any], index: int
) -> dict[str, Any]:
    label = str(evidence.get("analytical_label") or "UNKNOWN").upper()
    claim_type = label if label in CLAIM_TYPES else "UNKNOWN"
    condition = label if label in CONDITIONS else "UNKNOWN"
    return {
        "observation_id": f"LEGACY-{record['argus_id']}-EVIDENCE-{index + 1}",
        "field_path": f"legacy.evidence_refs[{index}]",
        "value": copy.deepcopy(evidence),
        "raw_label": "evidence_refs",
        "raw_value": copy.deepcopy(evidence),
        "source_id": evidence.get("source_id"),
        "source_system": str(evidence.get("source_system") or "ARGUS_LEGACY_REGISTRY"),
        "source_locator": evidence.get("source_locator"),
        "observed_at": _observed_at(record),
        "claim_type": claim_type,
        "condition": condition,
        "assurance": f"LEGACY_ANALYTICAL_LABEL_{label}",
    }


def _related_record_refs(record: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    seen_targets: set[str] = set()

    for relationship in record.get("relationships", []):
        target = relationship.get("target_argus_id")
        if not target:
            continue
        refs.append(
            {
                "argus_id": str(target),
                "relation_type": str(relationship.get("relation_type") or "LEGACY_RELATED_TO"),
            }
        )
        seen_targets.add(str(target))

    for target in record.get("related_argus_ids", []):
        target = str(target)
        if target not in seen_targets:
            refs.append({"argus_id": target, "relation_type": "LEGACY_RELATED_TO"})
            seen_targets.add(target)

    project_id = record.get("attributes", {}).get("project_id")
    if project_id and str(project_id) not in seen_targets:
        refs.append({"argus_id": str(project_id), "relation_type": "PART_OF_PROJECT"})

    return refs


def _party_role_links(record: dict[str, Any]) -> list[dict[str, Any]]:
    attrs = record.get("attributes", {})
    links: list[dict[str, Any]] = []
    buyer = attrs.get("buyer_entity_id")
    pe = attrs.get("procuring_entity_id")
    if buyer:
        links.append(
            {
                "party_id": str(buyer),
                "role": "BUYER",
                "source_role_label": "buyer_entity_id",
                "unit_label": None,
                "effective_from": None,
                "effective_to": None,
            }
        )
    if pe:
        links.append(
            {
                "party_id": str(pe),
                "role": "PROCURING_ENTITY",
                "source_role_label": "procuring_entity_id",
                "unit_label": None,
                "effective_from": None,
                "effective_to": None,
            }
        )
    return links


def transform_legacy_procurement(record: dict[str, Any]) -> dict[str, Any]:
    """Return a v2 candidate payload without mutating *record* or external state."""

    if record.get("record_type") != "PROCUREMENT":
        raise ValueError("transform_legacy_procurement accepts PROCUREMENT records only")

    attrs = record.get("attributes", {})
    result: dict[str, Any] = {
        "argus_id": str(record["argus_id"]),
        "title": str(record["canonical_name_or_title"]),
        "record_state": "BASELINE_PROVENANCE",
        "record_revision": int(record.get("revision") or 1),
    }

    related = _related_record_refs(record)
    if related:
        result["related_record_refs"] = related

    party_links = _party_role_links(record)
    if party_links:
        result["party_role_links"] = party_links

    process: dict[str, Any] = {}
    if attrs.get("procurement_method"):
        process["method_source_code"] = str(attrs["procurement_method"])
    if attrs.get("procurement_state"):
        process["status_raw"] = str(attrs["procurement_state"])
    if process:
        result["process"] = process

    quantity = attrs.get("quantity")
    if isinstance(quantity, dict) and quantity.get("value") is not None:
        item: dict[str, Any] = {
            "item_id": "LEGACY-ITEM-1",
            "description": str(record["canonical_name_or_title"]),
            "quantity": quantity.get("value"),
            "unit": quantity.get("unit"),
            "lot_ref": None,
            "classifications": [],
        }
        result["items"] = [item]

    material_unknowns = attrs.get("material_unknowns")
    if isinstance(material_unknowns, list):
        result["intelligence"] = {
            "material_unknowns": [str(value) for value in material_unknowns]
        }

    observations: list[dict[str, Any]] = []
    preserved_top_level = (
        "aliases",
        "created_at",
        "external_refs",
        "information_classification",
        "schema_version",
        "status",
        "updated_at",
    )
    for index, field in enumerate(preserved_top_level, start=1):
        if field in record:
            observations.append(
                _preserved_observation(
                    record,
                    observation_id=f"LEGACY-{record['argus_id']}-TOP-{index}",
                    field_path=f"legacy.{field}",
                    value=record[field],
                    raw_label=field,
                )
            )

    preserved_attributes = (
        "currency",
        "funding_source_raw",
        "official_reference",
        "package_reference",
        "procurement_type",
    )
    for index, field in enumerate(preserved_attributes, start=1):
        if field in attrs:
            observations.append(
                _preserved_observation(
                    record,
                    observation_id=f"LEGACY-{record['argus_id']}-ATTR-{index}",
                    field_path=f"legacy.attributes.{field}",
                    value=attrs[field],
                    raw_label=field,
                )
            )

    for index, evidence in enumerate(record.get("evidence_refs", [])):
        if isinstance(evidence, dict):
            observations.append(_evidence_observation(record, evidence, index))

    if observations:
        result["observations"] = observations

    return result


def transform_jsonl(path: Path) -> list[dict[str, Any]]:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return [
        transform_legacy_procurement(record)
        for record in records
        if record.get("record_type") == "PROCUREMENT"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print rehearsal-only Bangladesh procurement v2 transformations to stdout."
    )
    parser.add_argument("input", type=Path, help="Legacy ARGUS registry JSONL input")
    args = parser.parse_args()
    print(json.dumps(transform_jsonl(args.input), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
