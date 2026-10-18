"""Pure candidate materialization helpers for Bangladesh Procurement v2.

This module writes no files and does not change production authority. It composes
an existing ARGUS Master Registry PROCUREMENT envelope with a validated standalone
Bangladesh Procurement v2 candidate for disposable validation/rehearsal only.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
STANDALONE_SCHEMA_PATH = ROOT / "schemas" / "bangladesh-procurement-v2.schema.json"
DOMAIN_SCHEMA_PATH = ROOT / "schemas" / "bangladesh-procurement-v2-domain.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "registry" / "schema" / "argus-master-registry-v0.3.0-candidate.json"

ENVELOPE_OWNED_STANDALONE_FIELDS = {
    "argus_id",
    "title",
    "record_state",
    "record_revision",
    "related_record_refs",
    "observations",
}


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _validate_standalone(payload: dict[str, Any]) -> None:
    Draft202012Validator(_load_schema(STANDALONE_SCHEMA_PATH)).validate(payload)


def _validate_domain(payload: dict[str, Any]) -> None:
    Draft202012Validator(_load_schema(DOMAIN_SCHEMA_PATH)).validate(payload)


def _validate_registry(record: dict[str, Any]) -> None:
    Draft202012Validator(_load_schema(REGISTRY_SCHEMA_PATH)).validate(record)


def _domain_projection(standalone_v2: dict[str, Any]) -> dict[str, Any]:
    projected = {
        key: copy.deepcopy(value)
        for key, value in standalone_v2.items()
        if key not in ENVELOPE_OWNED_STANDALONE_FIELDS
    }
    _validate_domain(projected)
    return projected


def _require_same_identity(current_record: dict[str, Any], standalone_v2: dict[str, Any]) -> None:
    if current_record.get("record_type") != "PROCUREMENT":
        raise ValueError("current record must be PROCUREMENT")
    if current_record.get("argus_id") != standalone_v2.get("argus_id"):
        raise ValueError("argus_id mismatch between registry envelope and standalone v2 payload")
    if current_record.get("canonical_name_or_title") != standalone_v2.get("title"):
        raise ValueError("title mismatch between registry envelope and standalone v2 payload")
    if current_record.get("revision") != standalone_v2.get("record_revision"):
        raise ValueError("revision mismatch between registry envelope and standalone v2 payload")


def _compose_relationships(
    current_relationships: list[dict[str, Any]],
    related_record_refs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Preserve current graph and lift any additional typed v2 relation without loss."""
    result = copy.deepcopy(current_relationships)
    existing = {
        (item.get("target_argus_id"), item.get("relation_type"))
        for item in result
    }
    for ref in related_record_refs:
        pair = (ref.get("argus_id"), ref.get("relation_type"))
        if pair not in existing:
            result.append(
                {
                    "target_argus_id": ref["argus_id"],
                    "relation_type": ref["relation_type"],
                    "evidence_refs": [],
                }
            )
            existing.add(pair)
    return result


def materialize_registry_procurement(
    current_record: dict[str, Any], standalone_v2: dict[str, Any]
) -> dict[str, Any]:
    """Return a deterministic v0.3.0 candidate record without mutating inputs."""
    current = copy.deepcopy(current_record)
    standalone = copy.deepcopy(standalone_v2)

    _validate_standalone(standalone)
    _require_same_identity(current, standalone)

    relationships = _compose_relationships(
        current.get("relationships", []), standalone.get("related_record_refs", [])
    )
    related_ids = list(current.get("related_argus_ids", []))
    for relation in relationships:
        target = relation["target_argus_id"]
        if target not in related_ids:
            related_ids.append(target)

    result: dict[str, Any] = {
        "schema_version": "0.3.0",
        "argus_id": current["argus_id"],
        "record_type": "PROCUREMENT",
        "canonical_name_or_title": current["canonical_name_or_title"],
        "status": current["status"],
        "aliases": copy.deepcopy(current.get("aliases", [])),
        "related_argus_ids": related_ids,
        "relationships": relationships,
        "evidence_refs": copy.deepcopy(current.get("evidence_refs", [])),
        "external_refs": copy.deepcopy(current.get("external_refs", [])),
        "revision": current["revision"],
        "created_at": current["created_at"],
        "updated_at": current["updated_at"],
        "observations": copy.deepcopy(standalone.get("observations", [])),
        "domain_payload": {
            "profile": "BANGLADESH_PROCUREMENT",
            "version": "2.0.0-candidate",
            "data": _domain_projection(standalone),
        },
    }

    for optional in (
        "information_classification",
        "domain_classification_refs",
        "standard_refs",
    ):
        if optional in current:
            result[optional] = copy.deepcopy(current[optional])

    _validate_registry(result)
    return result


def read_procurement_semantics(record: dict[str, Any]) -> dict[str, Any]:
    """Read legacy v0.2.x or composed v0.3.0 PROCUREMENT without persisting a projection."""
    if record.get("record_type") != "PROCUREMENT":
        raise ValueError("record must be PROCUREMENT")

    version = record.get("schema_version")
    if version in {"0.2.0", "0.2.1"}:
        return {
            "shape": "LEGACY_REGISTRY_V0_2",
            "argus_id": record["argus_id"],
            "title": record["canonical_name_or_title"],
            "record_revision": record["revision"],
            "status": record["status"],
            "data": copy.deepcopy(record.get("attributes", {})),
            "observations": [],
        }
    if version == "0.3.0":
        payload = record.get("domain_payload")
        if not payload or payload.get("profile") != "BANGLADESH_PROCUREMENT":
            raise ValueError("v0.3.0 PROCUREMENT is missing Bangladesh procurement domain_payload")
        return {
            "shape": "COMPOSED_REGISTRY_V0_3",
            "argus_id": record["argus_id"],
            "title": record["canonical_name_or_title"],
            "record_revision": record["revision"],
            "status": record["status"],
            "data": copy.deepcopy(payload["data"]),
            "observations": copy.deepcopy(record.get("observations", [])),
        }
    raise ValueError(f"unsupported registry schema_version: {version}")


def project_legacy_procurement_view(record: dict[str, Any]) -> dict[str, Any]:
    """Return a non-persisted compatibility view for consumers expecting legacy-style data."""
    semantic = read_procurement_semantics(record)
    if semantic["shape"] == "LEGACY_REGISTRY_V0_2":
        return copy.deepcopy(semantic["data"])

    data = semantic["data"]
    process = data.get("process", {})
    view: dict[str, Any] = {}
    if process.get("status_normalized") is not None:
        view["procurement_state"] = process["status_normalized"]
    if process.get("method_source_code") is not None:
        view["procurement_method"] = process["method_source_code"]
    elif process.get("method_normalized") is not None:
        view["procurement_method"] = process["method_normalized"]
    if data.get("requirement_ref") is not None:
        view["underlying_requirement_id"] = data["requirement_ref"]
    if len(data.get("items", [])) == 1:
        item = data["items"][0]
        if item.get("quantity") is not None or item.get("unit") is not None:
            view["quantity"] = {"value": item.get("quantity"), "unit": item.get("unit")}
    return view
