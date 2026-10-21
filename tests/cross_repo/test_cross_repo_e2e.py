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

    def test_text_flow_uses_both_real_runtimes_and_returns_to_atlas(self) -> None:
        completed = self._run()

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("ATLAS→ARGUS VERIFIED", completed.stdout)
        self.assertIn("Route ACTIVATE", completed.stdout)
        self.assertIn("Receipt RETURNED", completed.stdout)
        self.assertIn("ATLAS 2.0.1", completed.stdout)
        self.assertIn("ARGUS 2.2.0-rc.1", completed.stdout)
        self.assertIn("External collection none", completed.stdout)
        self.assertIn("Registry writes none", completed.stdout)
        self.assertEqual("", completed.stderr)

    def test_ndjson_flow_exposes_each_real_boundary_as_one_event(self) -> None:
        completed = self._run("--format", "ndjson")

        self.assertEqual(0, completed.returncode, completed.stderr)
        events = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(
            ["atlas_handoff", "argus_result", "atlas_verified"],
            [event["event"] for event in events],
        )
        self.assertEqual("ACTIVATE", events[0]["route"])
        self.assertEqual("RETURNED", events[1]["state"])
        self.assertEqual("VERIFIED", events[2]["status"])
        self.assertEqual(events[0]["handoff_id"], events[2]["handoff_id"])
        self.assertTrue(events[1]["result_sha256"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
