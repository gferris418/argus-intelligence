"""Read-only end-to-end exercise using real ATLAS and ARGUS checkouts."""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter_ns
from collections.abc import Callable
from typing import Any, Sequence, TextIO

import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.argus_runtime import AnalysisEnvelope, AnalysisOutcome, Argus


ROOT = Path(__file__).resolve().parents[1]
COMPATIBILITY_PATH = ROOT / "contracts" / "atlas" / "synchronization-compatibility.yaml"
ARGUS_MANIFEST_PATH = ROOT / "argus-intelligence.yaml"
_KEY_ID = "atlas-cross-repo-e2e"
_OBJECTIVE = "Assess coastal surveillance radar for Bangladesh Navy"


@dataclass(frozen=True)
class CrossRepositoryOutcome:
    """Verified state returned after crossing both repository boundaries."""

    atlas_version: str
    atlas_commit: str
    argus_version: str
    route: dict[str, Any]
    handoff: dict[str, Any]
    analysis: AnalysisOutcome
    duration_ms: int

    @property
    def compact_status(self) -> str:
        result = self.analysis.result
        receipt = self.analysis.receipt
        return "\n".join((
            f"ATLAS→ARGUS VERIFIED | {self.duration_ms} ms | Route {self.route['status']} | "
            f"Receipt {receipt['state']}",
            f"Goal {_OBJECTIVE} | Handoff {self.handoff['handoff_id']} | "
            f"Context {self.handoff['state']}",
            f"Decision {result['decision']} | Maturity {result['maturity']} | "
            f"Unknowns {len(result['unknowns_conflicts'])}",
            f"Mode TEST_ONLY | ATLAS {self.atlas_version}@{self.atlas_commit[:12]} | "
            f"ARGUS {self.argus_version} | External collection none | Registry writes none",
        ))


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"structured file must contain an object: {path}")
    return value


def _load_compatibility() -> dict[str, Any]:
    value = json.loads(COMPATIBILITY_PATH.read_text(encoding="utf-8"))
    return value["atlas_compatibility"]


def _prepare_atlas_import(atlas_repo: Path) -> tuple[Any, dict[str, Any]]:
    if not atlas_repo.is_dir():
        raise ValueError(f"ATLAS checkout not found: {atlas_repo}")
    for required in ("atlas-os.yaml", "atlas_runtime", "registries/domain-methods.yaml"):
        if not (atlas_repo / required).exists():
            raise ValueError(f"invalid ATLAS checkout; missing {required}")

    compatibility = _load_compatibility()
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=atlas_repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError("ATLAS checkout has no readable Git HEAD")
    actual_commit = completed.stdout.strip()
    expected_commit = compatibility["atlas_commit"]
    if actual_commit != expected_commit:
        raise ValueError(
            f"ATLAS checkout commit mismatch: expected {expected_commit}, got {actual_commit}"
        )
    worktree = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=atlas_repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if worktree.returncode != 0:
        raise ValueError("ATLAS checkout status is unreadable")
    if worktree.stdout.strip():
        raise ValueError("ATLAS checkout tracked files differ from its verified HEAD")
    manifest = _load_yaml(atlas_repo / "atlas-os.yaml")
    actual_version = manifest.get("product", {}).get("version")
    expected_version = compatibility["atlas_version"]
    if actual_version != expected_version:
        raise ValueError(
            f"ATLAS checkout version mismatch: expected {expected_version}, got {actual_version}"
        )

    for contract in compatibility.get("source_contracts", {}).values():
        source = atlas_repo / contract["source_path"]
        if not source.is_file():
            raise ValueError(f"ATLAS source contract missing: {source}")
        import hashlib
        actual_sha = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual_sha != contract["sha256"]:
            raise ValueError(f"ATLAS source contract hash mismatch: {contract['source_path']}")

    sys.path.insert(0, str(atlas_repo))
    import atlas_runtime  # imported only after the exact checkout is verified

    module_path = Path(atlas_runtime.__file__).resolve()
    if not module_path.is_relative_to(atlas_repo.resolve()):
        raise ValueError(f"ATLAS runtime resolved outside the verified checkout: {module_path}")

    return atlas_runtime, compatibility


def _handoff_alignment(atlas_alignment: dict[str, Any]) -> dict[str, Any]:
    return {
        "domains": [atlas_alignment["domain"]],
        "status": atlas_alignment["status"],
        "frameworks": atlas_alignment["frameworks"],
        "applicability": atlas_alignment.get("applicability", {}),
        "deviations": atlas_alignment["deviations"],
        "compliance": atlas_alignment["compliance"],
        "evidence": [],
    }


def _analysis_method(handoff: dict[str, Any]) -> dict[str, Any]:
    return {
        "objective": _OBJECTIVE,
        "candidate_or_opportunity": {
            "name": "Bangladesh Navy coastal surveillance radar",
            "record_type": "INTELLIGENCE",
        },
        "decision": "INVESTIGATE",
        "maturity": "I1",
        "evidence": [],
        "unknowns_conflicts": [
            *handoff["unresolved_material"],
            "No external evidence collection was performed by this test.",
        ],
        "next_recommended_action": "Collect current authoritative requirement and procurement evidence.",
    }


def run(
    atlas_repo: Path,
    *,
    event_writer: Callable[[dict[str, Any]], None] | None = None,
) -> CrossRepositoryOutcome:
    """Cross ATLAS→ARGUS→ATLAS using the public runtime functions in each checkout."""

    started = perf_counter_ns()
    atlas, compatibility = _prepare_atlas_import(atlas_repo.resolve())
    now = datetime.now(timezone.utc).replace(microsecond=0)
    timestamp = now.isoformat().replace("+00:00", "Z")

    execution = atlas.execute(atlas.ExecutionEnvelope(
        objective=_OBJECTIVE,
        plan_id="plan-argus-e2e-001",
        work_units=(
            {"id": "classify", "status": "COMPLETED", "dependencies": []},
            {"id": "argus-analysis", "status": "PENDING", "dependencies": ["classify"]},
        ),
        timestamp=timestamp,
        timezone_name="UTC",
    ))
    if execution.active_unit != "argus-analysis":
        raise RuntimeError("ATLAS did not select the ARGUS analysis work unit")

    execution_context = atlas.ExecutionContext(
        task_id="TASK-ARGUS-E2E-001",
        plan_id="plan-argus-e2e-001",
        work_unit_id=execution.active_unit,
        task_class="ANALYSIS",
        available_capabilities=frozenset({
            "capability.domain-alignment",
            "capability.evidence-tracking",
        }),
    )
    classifications = _load_yaml(atlas_repo / "registries" / "classifications.yaml")
    frameworks = _load_yaml(atlas_repo / "registries" / "frameworks.yaml")
    classification = atlas.classify_domain_context(
        _OBJECTIVE,
        classifications["items"],
        required_facets=("jurisdiction", "operator-industry", "capability", "lifecycle-stage"),
    )
    alignment = _handoff_alignment(
        atlas.align_domain_practices("risk-management", frameworks["items"])
    )
    handoff = atlas.prepare_domain_context_handoff(
        {
            "id": execution_context.task_id,
            "domain_classification": classification,
            "domain_alignment": alignment,
        },
        execution_context=execution_context,
        consumer="ARGUS",
        handoff_id="HANDOFF-ARGUS-E2E-001",
        created_at=timestamp,
    )
    domain_methods = _load_yaml(atlas_repo / "registries" / "domain-methods.yaml")
    route = atlas.route_domain_method(
        "government_public_sector_opportunity_intelligence",
        domain_methods,
        execution_context=execution_context,
        handoff=handoff,
    )
    if route["status"] != "ACTIVATE":
        raise RuntimeError(f"ATLAS did not activate ARGUS: {route}")
    if event_writer is not None:
        event_writer({
            "event": "atlas_handoff",
            "handoff_id": handoff["handoff_id"],
            "handoff_state": handoff["state"],
            "route": route["status"],
        })

    private_key = Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    handoff_attestation = atlas.attest_control_record(
        handoff,
        key_id=_KEY_ID,
        private_key=private_bytes,
    )
    lease = atlas.prepare_execution_lease(
        handoff,
        execution_lease_id="LEASE-ARGUS-E2E-001",
        issued_at=timestamp,
        lease_expires_at=(now + timedelta(hours=4)).isoformat().replace("+00:00", "Z"),
    )
    lease_attestation = atlas.attest_control_record(
        lease,
        key_id=_KEY_ID,
        private_key=private_bytes,
    )
    registry = {
        "registry_version": "1.0.0",
        "issuer": "ATLAS_OS",
        "keys": [{
            "key_id": _KEY_ID,
            "algorithm": "Ed25519",
            "public_key_base64": base64.b64encode(public_bytes).decode("ascii"),
            "activated_at": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
            "expires_at": (now + timedelta(hours=8)).isoformat().replace("+00:00", "Z"),
            "status": "ACTIVE",
            "issuer": "ATLAS_OS",
            "allowed_record_classes": ["DOMAIN_CONTEXT_HANDOFF", "EXECUTION_LEASE"],
            "supersedes": None,
        }],
    }
    analysis = Argus(
        _analysis_method,
        trusted_key_registry=registry,
    ).analyze(AnalysisEnvelope(
        handoff=handoff,
        atlas_attestation=handoff_attestation,
        execution_lease=lease,
        execution_lease_attestation=lease_attestation,
        started_at=timestamp,
    ))
    if event_writer is not None:
        event_writer({
            "event": "argus_result",
            "execution_lease_id": analysis.receipt["atlas"]["execution_lease_id"],
            "result_sha256": analysis.result["result_sha256"],
            "state": analysis.receipt["state"],
        })

    atlas.verify_domain_handoff_receipt(handoff, analysis.result["upstream_handoff"])
    if event_writer is not None:
        event_writer({
            "event": "atlas_verified",
            "handoff_id": handoff["handoff_id"],
            "status": "VERIFIED",
        })

    argus_manifest = _load_yaml(ARGUS_MANIFEST_PATH)
    return CrossRepositoryOutcome(
        atlas_version=compatibility["atlas_version"],
        atlas_commit=compatibility["atlas_commit"],
        argus_version=argus_manifest["product"]["version"],
        route=route,
        handoff=handoff,
        analysis=analysis,
        duration_ms=max(0, round((perf_counter_ns() - started) / 1_000_000)),
    )


def _write_event(stdout: TextIO, event: dict[str, Any]) -> None:
    print(json.dumps(event, sort_keys=True, separators=(",", ":")), file=stdout, flush=True)


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.cross_repo_e2e",
        description="Run a real, read-only ATLAS-to-ARGUS-to-ATLAS integration test.",
    )
    parser.add_argument("--atlas-repo", required=True, type=Path)
    parser.add_argument("--format", choices=("text", "ndjson"), default="text")
    arguments = parser.parse_args(argv)
    try:
        writer = (
            (lambda event: _write_event(stdout, event))
            if arguments.format == "ndjson"
            else None
        )
        outcome = run(arguments.atlas_repo, event_writer=writer)
        if arguments.format == "text":
            print(outcome.compact_status, file=stdout)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"cross-repository test failed: {error}", file=stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
