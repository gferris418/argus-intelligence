from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ATLAS_ROOT = ROOT.parent / "atlas-os"


class CrossRepositoryEndToEndTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.cross_repo_e2e",
                "--atlas-repo",
                str(ATLAS_ROOT),
                *arguments,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_argus_snapshot_matches_atlas_canonical_execution_contract(self) -> None:
        descriptor = yaml.safe_load(
            (ROOT / "contracts" / "atlas" / "current-integration.yaml").read_text(encoding="utf-8")
        )
        source = descriptor["canonical_source"]
        canonical = json.loads((ATLAS_ROOT / source["path"]).read_text(encoding="utf-8"))
        snapshot = descriptor["contract"]

        self.assertEqual(source["contract_version"], canonical["version"])
        self.assertEqual(canonical["prompt_entry"]["value"], snapshot["prompt_entry"])
        self.assertEqual(canonical["prompt_entry"]["scope"], snapshot["prompt_entry_scope"])
        self.assertEqual(canonical["pre_execution_flow"], snapshot["pre_execution_flow"])
        self.assertEqual(canonical["route_mechanisms"], snapshot["route_mechanisms"])
        self.assertEqual(canonical["approval"]["key"], snapshot["approval_key"])
        self.assertEqual(
            canonical["approval"]["explicit_user_approval_required"],
            snapshot["explicit_user_approval_required"],
        )
        self.assertEqual(canonical["approval"]["plain_approval_scope"], snapshot["plain_approval_scope"])
        self.assertEqual(canonical["activation_authority"], snapshot["activation_authority"])
        self.assertEqual(canonical["next_step_authority"], snapshot["next_step_authority"])
        self.assertEqual(canonical["provider_return_target"], snapshot["provider_return_target"])

    def test_text_flow_uses_current_runtimes_and_returns_to_atlas(self) -> None:
        completed = self._run()

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("ATLAS→ARGUS VERIFIED", completed.stdout)
        self.assertIn("Route ARGUS", completed.stdout)
        self.assertIn("Receipt RETURNED", completed.stdout)
        self.assertIn("ATLAS 3.0.2", completed.stdout)
        self.assertIn("ARGUS 3.0.0-rc.2", completed.stdout)
        self.assertIn("External collection none", completed.stdout)
        self.assertIn("Registry writes none", completed.stdout)
        self.assertEqual("", completed.stderr)

    def test_ndjson_flow_exposes_route_provider_and_return_boundaries(self) -> None:
        completed = self._run("--format", "ndjson")

        self.assertEqual(0, completed.returncode, completed.stderr)
        events = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(
            ["atlas_route", "argus_result", "atlas_verified"],
            [event["event"] for event in events],
        )
        self.assertEqual("ARGUS", events[0]["route"])
        self.assertEqual("APPROVED", events[0]["approval"])
        self.assertEqual("RETURNED", events[1]["status"])
        self.assertEqual("ATLAS", events[1]["return_target"])
        self.assertEqual("VERIFIED", events[2]["status"])
        self.assertEqual("ATLAS", events[2]["next_step_authority"])
        self.assertEqual(events[0]["task_id"], events[2]["task_id"])


if __name__ == "__main__":
    unittest.main()
