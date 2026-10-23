"""Read-only end-to-end exercise using current ATLAS v3 and ARGUS provider runtimes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns, time
from typing import Any, Sequence, TextIO

import yaml

from tools.atlas_v3_provider import ArgusProvider, ProviderEnvelope, ProviderOutcome


ROOT = Path(__file__).resolve().parents[1]
CURRENT_INTEGRATION_PATH = ROOT / "contracts" / "atlas" / "current-integration.yaml"
ARGUS_MANIFEST_PATH = ROOT / "argus-intelligence.yaml"
_OBJECTIVE = "Build a supplier landscape for coastal surveillance radar for Bangladesh Navy"
_E2E_SECRET = b"atlas-argus-e2e-secret-32-bytes!!"
_E2E_KEY_ID = "atlas-argus-e2e-key"


@dataclass(frozen=True)
class CrossRepositoryOutcome:
    atlas_version: str
    atlas_commit: str
    argus_version: str
    initial_state: str
    route: dict[str, Any]
    provider: ProviderOutcome
    atlas_return_state: str
    duration_ms: int

    @property
    def compact_status(self) -> str:
        return "\n".join((
            f"ATLAS→ARGUS VERIFIED | {self.duration_ms} ms | Route {self.route['mechanism']} | "
            f"Receipt {self.provider.result['status']}",
            f"Goal {_OBJECTIVE} | Source task {self.provider.result['source_task_id']} | "
            f"Return {self.provider.return_target}",
            f"Collection {self.provider.result['collection_status']} | "
            f"Evidence {len(self.provider.result['evidence'])}",
            f"Mode TEST_ONLY_REMOTE_CAPABILITY_V2 | ATLAS {self.atlas_version}@{self.atlas_commit[:12]} | "
            f"ARGUS {self.argus_version} | External collection none | Registry writes none",
        ))


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"structured file must contain an object: {path}")
    return value


def _load_compatibility() -> dict[str, Any]:
    return _load_yaml(CURRENT_INTEGRATION_PATH)


def _prepare_atlas_import(atlas_repo: Path) -> tuple[Any, dict[str, Any]]:
    if not atlas_repo.is_dir():
        raise ValueError(f"ATLAS checkout not found: {atlas_repo}")

    compatibility = _load_compatibility()
    atlas_contract = compatibility["atlas"]
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
    expected_commit = atlas_contract["commit"]
    if actual_commit != expected_commit:
        raise ValueError(f"ATLAS checkout commit mismatch: expected {expected_commit}, got {actual_commit}")
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

    for required in (
        "atlas-os.yaml",
        "atlas_runtime",
        "integrations/argus.yaml",
        "integrations/chatgpt-bootstrap.yaml",
        "contracts/atlas-argus-execution-v2.json",
    ):
        if not (atlas_repo / required).exists():
            raise ValueError(f"invalid ATLAS checkout; missing {required}")

    manifest = _load_yaml(atlas_repo / "atlas-os.yaml")
    actual_version = manifest.get("product", {}).get("version")
    expected_version = atlas_contract["version"]
    if actual_version != expected_version:
        raise ValueError(f"ATLAS checkout version mismatch: expected {expected_version}, got {actual_version}")

    canonical = atlas_contract["canonical_execution_contract"]
    canonical_path = atlas_repo / canonical["path"]
    canonical_bytes = canonical_path.read_bytes()
    actual_digest = hashlib.sha256(canonical_bytes).hexdigest()
    if actual_digest != canonical["sha256"]:
        raise ValueError("ATLAS canonical execution contract digest mismatch")
    canonical_payload = json.loads(canonical_bytes.decode("utf-8"))
    if canonical_payload.get("version") != canonical["version"]:
        raise ValueError("ATLAS canonical execution contract version mismatch")

    integration = _load_yaml(atlas_repo / atlas_contract["integration_path"])
    current = compatibility["contract"]
    if integration.get("capability") != current["capability"]:
        raise ValueError("ATLAS ARGUS capability differs from the pinned current contract")
    if integration.get("activation_authority") != current["activation_authority"]:
        raise ValueError("ATLAS ARGUS activation authority differs from the pinned current contract")
    if integration.get("next_step_authority") != current["next_step_authority"]:
        raise ValueError("ATLAS ARGUS next-step authority differs from the pinned current contract")
    if integration.get("explicit_user_approval_required") is not True:
        raise ValueError("ATLAS ARGUS approval gate is not enabled")

    sys.path.insert(0, str(atlas_repo))
    import atlas_runtime  # imported only after the exact checkout is verified

    module_path = Path(atlas_runtime.__file__).resolve()
    if not module_path.is_relative_to(atlas_repo.resolve()):
        raise ValueError(f"ATLAS runtime resolved outside the verified checkout: {module_path}")
    return atlas_runtime, compatibility


def _collection_method(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "objective": context["objective"],
        "collection_status": "COMPLETE",
        "evidence": [],
        "collection_gaps": ["No external evidence collection was performed by this test."],
    }


def run(
    atlas_repo: Path,
    *,
    event_writer: Callable[[dict[str, Any]], None] | None = None,
) -> CrossRepositoryOutcome:
    """Cross ATLAS→ARGUS→ATLAS using each repository's current public runtime."""

    started = perf_counter_ns()
    atlas, compatibility = _prepare_atlas_import(atlas_repo.resolve())

    pending = atlas.execute(
        atlas.ExecutionEnvelope(
            objective=_OBJECTIVE,
            task_id="ATLAS-ARGUS-E2E-001",
            host="chatgpt",
        )
    )
    if pending.state != "AWAITING_APPROVAL":
        raise RuntimeError("ATLAS did not enforce the ARGUS approval gate")

    approved = atlas.execute(
        atlas.ExecutionEnvelope(
            objective=_OBJECTIVE,
            task_id=pending.task_id,
            host="chatgpt",
            approvals=(atlas.ARGUS_APPROVAL,),
        )
    )
    approved_dict = approved.to_dict()
    if approved.state != "READY" or approved.route.mechanism not in {"ARGUS", "MULTI_CAPABILITY"}:
        raise RuntimeError(f"ATLAS did not activate the bounded ARGUS route: {approved_dict['route']}")
    if event_writer is not None:
        event_writer(
            {
                "event": "atlas_route",
                "task_id": approved.task_id,
                "route": approved.route.mechanism,
                "approval": approved.route.approval_status,
            }
        )

    remote_now = int(time())
    token = atlas.issue_remote_capability(
        _E2E_SECRET,
        task_id=approved.task_id,
        intent=approved.normalized_objective,
        key_id=_E2E_KEY_ID,
        now=remote_now,
        ttl_seconds=120,
        nonce="ATLAS-ARGUS-E2E-CAPABILITY-001",
    )
    provider_runtime = ArgusProvider(
        _collection_method,
        remote_secret_resolver=lambda key_id: _E2E_SECRET if key_id == _E2E_KEY_ID else None,
    )
    provider = provider_runtime.execute(
        ProviderEnvelope(
            atlas_result=approved_dict,
            transport="remote",
            remote_capability=token,
            remote_now=remote_now,
        )
    )
    if event_writer is not None:
        event_writer(
            {
                "event": "argus_result",
                "source_task_id": provider.result["source_task_id"],
                "status": provider.result["status"],
                "return_target": provider.return_target,
                "transport": "remote_capability_v2",
            }
        )

    returned = atlas.execute(
        atlas.ExecutionEnvelope(
            objective=_OBJECTIVE,
            task_id=approved.task_id,
            host="chatgpt",
            approvals=(atlas.ARGUS_APPROVAL,),
            provider_result=provider.result,
        )
    )
    if "PROVIDER_RETURN_RECONCILIATION" not in returned.execution_trace:
        raise RuntimeError("ATLAS did not reconcile the ARGUS provider return")
    if returned.next_step_authority != "ATLAS" or returned.provider_return_target != "ATLAS":
        raise RuntimeError("ATLAS did not retain next-step authority after provider return")
    if event_writer is not None:
        event_writer(
            {
                "event": "atlas_verified",
                "task_id": returned.task_id,
                "status": "VERIFIED",
                "next_step_authority": returned.next_step_authority,
            }
        )

    argus_manifest = _load_yaml(ARGUS_MANIFEST_PATH)
    atlas_contract = compatibility["atlas"]
    return CrossRepositoryOutcome(
        atlas_version=atlas_contract["version"],
        atlas_commit=atlas_contract["commit"],
        argus_version=argus_manifest["product"]["version"],
        initial_state=pending.state,
        route=approved.route.to_dict(),
        provider=provider,
        atlas_return_state=returned.state,
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
        description="Run the current read-only ATLAS-to-ARGUS-to-ATLAS provider integration test.",
    )
    parser.add_argument("--atlas-repo", required=True, type=Path)
    parser.add_argument("--format", choices=("text", "ndjson"), default="text")
    arguments = parser.parse_args(argv)
    try:
        writer = (lambda event: _write_event(stdout, event)) if arguments.format == "ndjson" else None
        outcome = run(arguments.atlas_repo, event_writer=writer)
        if arguments.format == "text":
            print(outcome.compact_status, file=stdout)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"cross-repository test failed: {error}", file=stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
