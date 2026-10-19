"""Ephemeral, non-production smoke exercise for the governed ARGUS runtime."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Sequence, TextIO

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.argus_runtime import AnalysisEnvelope, Argus
from tools.atlas_sync import canonical_handoff_sha256


_KEY_ID = "atlas-ephemeral-smoke"


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _fresh_handoff(timestamp: str) -> dict[str, Any]:
    created_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    handoff: dict[str, Any] = {
        "contract_version": "1.2.0",
        "handoff_id": "HANDOFF-ARGUS-SMOKE-001",
        "source_task_id": "TASK-ARGUS-SMOKE-001",
        "source_plan_id": "plan-argus-smoke-001",
        "source_work_unit_id": "unit-runtime-smoke",
        "producer": "ATLAS_OS",
        "consumer": "ARGUS",
        "created_at": timestamp,
        "activation_expires_at": (created_at + timedelta(hours=24)).isoformat().replace("+00:00", "Z"),
        "state": "READY",
        "domain_classification": {
            "status": "CLASSIFIED",
            "facets": {},
            "taxonomy_references": [],
            "risk_flags": [],
            "unresolved_facets": [],
            "conditional_candidates": [],
            "evidence": [],
            "next_action": None,
        },
        "domain_alignment": {
            "domains": ["government-opportunity-intelligence"],
            "status": "ALIGNED",
            "frameworks": [],
            "applicability": {},
            "deviations": [],
            "compliance": "NOT_CLAIMED",
            "evidence": [],
        },
        "unresolved_material": [],
        "risk_flags": [],
    }
    handoff["payload_sha256"] = canonical_handoff_sha256(handoff)
    return handoff


def _execution_lease(handoff: dict[str, Any], timestamp: str) -> dict[str, Any]:
    issued_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return {
        "contract_version": "1.0.0",
        "execution_lease_id": "LEASE-ARGUS-SMOKE-001",
        "handoff_id": handoff["handoff_id"],
        "handoff_payload_sha256": handoff["payload_sha256"],
        "source_task_id": handoff["source_task_id"],
        "source_plan_id": handoff["source_plan_id"],
        "source_work_unit_id": handoff["source_work_unit_id"],
        "producer": "ATLAS_OS",
        "consumer": "ARGUS",
        "issued_at": timestamp,
        "lease_expires_at": (issued_at + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
        "supersedes_lease_id": None,
    }


def _attest(record: dict[str, Any], private_key: Ed25519PrivateKey) -> dict[str, str]:
    payload = _canonical_json(record)
    return {
        "version": "1",
        "issuer": "ATLAS_OS",
        "algorithm": "Ed25519",
        "key_id": _KEY_ID,
        "record_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "signature": base64.b64encode(private_key.sign(payload)).decode("ascii"),
    }


def _smoke_method(_: dict[str, Any]) -> dict[str, Any]:
    return {
        "objective": "Verify the governed ARGUS runtime seam.",
        "candidate_or_opportunity": {"name": "Runtime smoke opportunity"},
        "decision": "INVESTIGATE",
        "maturity": "I1",
        "evidence": [],
        "unknowns_conflicts": ["No external collection was performed."],
        "next_recommended_action": "Configure a real domain method and governed ATLAS trust registry.",
    }


def _write_event(stdout: TextIO, event: dict[str, Any]) -> None:
    print(json.dumps(event, sort_keys=True, separators=(",", ":")), file=stdout, flush=True)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.live_smoke",
        description="Run an ephemeral test-only ATLAS-to-ARGUS synchronization exercise.",
    )
    parser.add_argument(
        "--format", choices=("text", "ndjson"), default="text",
        help="Output format; compact text is the default.",
    )
    arguments = parser.parse_args(argv)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    timestamp = now.isoformat().replace("+00:00", "Z")
    handoff = _fresh_handoff(timestamp)
    lease = _execution_lease(handoff, timestamp)
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    registry = {
        "registry_version": "1.0.0",
        "issuer": "ATLAS_OS",
        "keys": [{
            "key_id": _KEY_ID,
            "algorithm": "Ed25519",
            "public_key_base64": base64.b64encode(public_key).decode("ascii"),
            "activated_at": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
            "expires_at": (now + timedelta(hours=2)).isoformat().replace("+00:00", "Z"),
            "status": "ACTIVE",
            "issuer": "ATLAS_OS",
            "allowed_record_classes": ["DOMAIN_CONTEXT_HANDOFF", "EXECUTION_LEASE"],
            "supersedes": None,
        }],
    }
    handoff_attestation = _attest(handoff, private_key)
    lease_attestation = _attest(lease, private_key)
    if arguments.format == "ndjson":
        _write_event(stdout, {"event": "started", "mode": "TEST_ONLY"})

    outcome = Argus(
        _smoke_method,
        trusted_key_registry=registry,
    ).analyze(AnalysisEnvelope(
        handoff=handoff,
        atlas_attestation=handoff_attestation,
        execution_lease=lease,
        execution_lease_attestation=lease_attestation,
        started_at=timestamp,
    ))

    if arguments.format == "text":
        print(outcome.compact_status, file=stdout)
        print(
            f"Mode TEST_ONLY | ATLAS {outcome.receipt['atlas']['version']} | "
            f"ARGUS {outcome.receipt['argus']['version']} | External collection none | Registry writes none",
            file=stdout,
        )
    else:
        _write_event(stdout, {
            "argus_version": outcome.receipt["argus"]["version"],
            "atlas_version": outcome.receipt["atlas"]["version"],
            "event": "result",
            "result_sha256": outcome.result["result_sha256"],
            "state": outcome.receipt["state"],
            "sync_execution_id": outcome.receipt["sync_execution_id"],
        })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
