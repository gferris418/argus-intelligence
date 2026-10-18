"""Pure candidate materialization helpers for Bangladesh Procurement v2.

This module writes no canonical files and does not change production authority. It
composes an existing ARGUS Master Registry PROCUREMENT envelope with a validated
standalone Bangladesh Procurement v2 candidate for disposable validation/rehearsal.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

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


def _schema_registry() -> Registry:
    registry = Registry()
    for path in (STANDALONE_SCHEMA_PATH, DOMAIN_SCHEMA_PATH, REGISTRY_SCHEMA_PATH):
        schema = _load_schema(path)
        resource_id = schema.get("$id")
        if resource_id:
            registry = registry.with_resource(resource_id, Resource.from_contents(schema))
    return registry


def _validator(path: Path) -> Draft202012Validator:
    return Draft202012Validator(_load_schema(path), registry=_schema_registry())


def _validate_standalone(payload: dict[str, Any]) -> None:
    _validator(STANDALONE_SCHEMA_PATH).validate(payload)


def validate_domain_candidate(payload: dict[str, Any]) -> None:
    _validator(DOMAIN_SCHEMA_PATH).validate(payload)


def validate_registry_candidate(record: dict[str, Any]) -> None:
    _validator(REGISTRY_SCHEMA_PATH).validate(record)
    if record.get("schema_version") == "0.3.0":
        if record.get("record_type") != "PROCUREMENT":
            raise ValueError("v0.3.0 candidate is currently restricted to PROCUREMENT")
        relationship_targets = sorted({
            rel["target_argus_id"] for rel in record.get("relationships", [])
        })
        cache_ids = sorted(record.get("related_argus_ids", []))
        if cache_ids != relationship_targets:
            raise ValueError(
                "related_argus_ids must exactly equal relationship targets for v0.3.0"
            )


def _domain_projection(standalone_v2: dict[str, Any]) -> dict[str, Any]:
    projected = {
        key: copy.deepcopy(value)
        for key, value in standalone_v2.items()
        if key not in ENVELOPE_OWNED_STANDALONE_FIELDS
    }
    validate_domain_candidate(projected)
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
    """Preserve current typed graph and lift additional typed v2 relations."""
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


def _legacy_status_observation(current_record: dict[str, Any]) -> dict[str, Any] | None:
    status = current_record.get("status")
    if status is None:
        return None
    return {
        "field_path": "legacy_registry.status",
        "value": copy.deepcopy(status),
        "raw_label": "status",
        "raw_value": copy.deepcopy(status),
        "source_system": "ARGUS_LEGACY_REGISTRY",
        "claim_type": "UNKNOWN",
        "condition": "CURRENT",
        "assurance": "LEGACY_COMPATIBILITY_PROVENANCE",
    }


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
    related_ids = sorted({relation["target_argus_id"] for relation in relationships})

    observations = copy.deepcopy(standalone.get("observations", []))
    legacy_status = _legacy_status_observation(current)
    if legacy_status is not None:
        observations.append(legacy_status)

    result: dict[str, Any] = {
        "schema_version": "0.3.0",
        "argus_id": current["argus_id"],
        "record_type": "PROCUREMENT",
        "canonical_name_or_title": current["canonical_name_or_title"],
        "record_state": standalone["record_state"],
        "aliases": copy.deepcopy(current.get("aliases", [])),
        "related_argus_ids": related_ids,
        "relationships": relationships,
        "evidence_refs": copy.deepcopy(current.get("evidence_refs", [])),
        "external_refs": copy.deepcopy(current.get("external_refs", [])),
        "revision": current["revision"],
        "created_at": current["created_at"],
        "updated_at": current["updated_at"],
        "observations": observations,
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

    validate_registry_candidate(result)
    return result


def read_procurement_semantics(record: dict[str, Any]) -> dict[str, Any]:
    """Read legacy v0.2.x or composed v0.3.0 PROCUREMENT without persisting projection."""
    if record.get("record_type") != "PROCUREMENT":
        raise ValueError("record must be PROCUREMENT")

    version = record.get("schema_version")
    if version in {"0.2.0", "0.2.1"}:
        return {
            "shape": "LEGACY_REGISTRY_V0_2",
            "argus_id": record["argus_id"],
            "title": record["canonical_name_or_title"],
            "record_revision": record["revision"],
            "record_state": None,
            "legacy_status": record.get("status"),
            "data": copy.deepcopy(record.get("attributes", {})),
            "observations": [],
        }
    if version == "0.3.0":
        validate_registry_candidate(record)
        payload = record.get("domain_payload")
        if not payload or payload.get("profile") != "BANGLADESH_PROCUREMENT":
            raise ValueError("v0.3.0 PROCUREMENT is missing Bangladesh procurement domain_payload")
        return {
            "shape": "COMPOSED_REGISTRY_V0_3",
            "argus_id": record["argus_id"],
            "title": record["canonical_name_or_title"],
            "record_revision": record["revision"],
            "record_state": record["record_state"],
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


def _diff_values(expected: Any, actual: Any, path: str) -> list[str]:
    findings: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected object, got {type(actual).__name__}"]
        for key, value in expected.items():
            child = f"{path}.{key}" if path else key
            if key not in actual:
                findings.append(f"{child}: missing")
            else:
                findings.extend(_diff_values(value, actual[key], child))
        for key in actual:
            if key not in expected:
                child = f"{path}.{key}" if path else key
                findings.append(f"{child}: unexpected")
        return findings
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return [f"{path}: expected list, got {type(actual).__name__}"]
        if expected != actual:
            findings.append(f"{path}: list differs")
        return findings
    if expected != actual:
        findings.append(f"{path}: expected {expected!r}, got {actual!r}")
    return findings


def semantic_loss_findings(
    standalone_v2: dict[str, Any], materialized: dict[str, Any]
) -> list[str]:
    """Compute standalone-v2 semantic loss after composition; returns one finding per loss."""
    findings: list[str] = []
    identity_pairs = {
        "argus_id": materialized.get("argus_id"),
        "title": materialized.get("canonical_name_or_title"),
        "record_state": materialized.get("record_state"),
        "record_revision": materialized.get("revision"),
    }
    for field, actual in identity_pairs.items():
        if standalone_v2.get(field) != actual:
            findings.append(
                f"{field}: expected {standalone_v2.get(field)!r}, got {actual!r}"
            )

    expected_domain = {
        key: copy.deepcopy(value)
        for key, value in standalone_v2.items()
        if key not in ENVELOPE_OWNED_STANDALONE_FIELDS
    }
    actual_domain = materialized.get("domain_payload", {}).get("data", {})
    findings.extend(_diff_values(expected_domain, actual_domain, "domain_payload.data"))

    relationships = {
        (item.get("target_argus_id"), item.get("relation_type"))
        for item in materialized.get("relationships", [])
    }
    for ref in standalone_v2.get("related_record_refs", []):
        pair = (ref.get("argus_id"), ref.get("relation_type"))
        if pair not in relationships:
            findings.append(f"related_record_refs: missing lifted relationship {pair!r}")

    materialized_observations = materialized.get("observations", [])
    for observation in standalone_v2.get("observations", []):
        if observation not in materialized_observations:
            findings.append("observations: standalone observation missing after materialization")
    return findings


def materialization_loss_findings(
    current_record: dict[str, Any],
    standalone_v2: dict[str, Any],
    materialized: dict[str, Any],
) -> list[str]:
    """Compute loss across both the generic envelope and the standalone v2 semantics."""
    findings = semantic_loss_findings(standalone_v2, materialized)

    for field in (
        "aliases",
        "evidence_refs",
        "external_refs",
        "created_at",
        "updated_at",
        "information_classification",
        "domain_classification_refs",
        "standard_refs",
    ):
        if field in current_record and current_record.get(field) != materialized.get(field):
            findings.append(f"envelope.{field}: changed or missing")

    current_pairs = {
        (item.get("target_argus_id"), item.get("relation_type"))
        for item in current_record.get("relationships", [])
    }
    materialized_pairs = {
        (item.get("target_argus_id"), item.get("relation_type"))
        for item in materialized.get("relationships", [])
    }
    for pair in sorted(current_pairs - materialized_pairs):
        findings.append(f"relationships: legacy typed relationship lost {pair!r}")

    represented_ids = {item["target_argus_id"] for item in materialized.get("relationships", [])}
    represented_ids.update(
        item.get("party_id") for item in standalone_v2.get("party_role_links", []) if item.get("party_id")
    )
    represented_ids.update(
        item.get("argus_id") for item in standalone_v2.get("related_record_refs", []) if item.get("argus_id")
    )
    for argus_id in current_record.get("related_argus_ids", []):
        if argus_id not in represented_ids:
            findings.append(f"related_argus_ids: context link {argus_id!r} is not represented")

    legacy_status = current_record.get("status")
    if legacy_status is not None:
        preserved = any(
            obs.get("field_path") == "legacy_registry.status"
            and obs.get("raw_value") == legacy_status
            for obs in materialized.get("observations", [])
            if isinstance(obs, dict)
        )
        if not preserved:
            findings.append("legacy status provenance was not preserved")
    return findings


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        .encode("utf-8")
    )


def disposable_activation_revert_rehearsal(
    *,
    source_bytes: dict[str, bytes],
    candidate_records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Physically activate and revert only disposable copies, then prove exact restoration."""
    if set(source_bytes) != set(candidate_records):
        raise ValueError("source and candidate ID sets must match")

    with tempfile.TemporaryDirectory(prefix="argus-v2-revert-") as temp_dir:
        root = Path(temp_dir)
        paths: dict[str, Path] = {}
        for argus_id, data in source_bytes.items():
            path = root / f"{argus_id}.json"
            path.write_bytes(data)
            paths[argus_id] = path

        pre_bytes = {argus_id: len(path.read_bytes()) for argus_id, path in paths.items()}
        pre_sha = {argus_id: _sha256(path.read_bytes()) for argus_id, path in paths.items()}

        for argus_id, record in candidate_records.items():
            paths[argus_id].write_bytes(_canonical_json_bytes(record))
        activation_sha = {argus_id: _sha256(path.read_bytes()) for argus_id, path in paths.items()}
        activation_changed = any(activation_sha[argus_id] != pre_sha[argus_id] for argus_id in paths)

        for argus_id, data in source_bytes.items():
            paths[argus_id].write_bytes(data)
        post_bytes = {argus_id: len(path.read_bytes()) for argus_id, path in paths.items()}
        post_sha = {argus_id: _sha256(path.read_bytes()) for argus_id, path in paths.items()}

        return {
            "activation_changed_bytes": activation_changed,
            "rollback_exact": pre_sha == post_sha and pre_bytes == post_bytes,
            "pre_sha256": pre_sha,
            "post_rollback_sha256": post_sha,
            "pre_bytes": pre_bytes,
            "post_rollback_bytes": post_bytes,
        }
