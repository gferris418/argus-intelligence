from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


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

    def test_text_flow_uses_current_runtimes_and_returns_to_atlas(self) -> None:
        completed = self._run()

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("ATLAS→ARGUS VERIFIED", completed.stdout)
        self.assertIn("Route ARGUS", completed.stdout)
        self.assertIn("Receipt RETURNED", completed.stdout)
        self.assertIn("ATLAS 3.0.1", completed.stdout)
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
