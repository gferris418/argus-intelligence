from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LiveSmokeTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "tools.live_smoke", *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_default_text_smoke_runs_the_real_argus_facade(self) -> None:
        completed = self._run()

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("ARGUS RETURNED", completed.stdout)
        self.assertIn("TEST_ONLY", completed.stdout)
        self.assertIn("ATLAS 2.0.1-rc.1", completed.stdout)
        self.assertIn("ARGUS 2.0.1-rc.1", completed.stdout)
        self.assertEqual("", completed.stderr)

    def test_ndjson_smoke_emits_parseable_start_and_result_events(self) -> None:
        completed = self._run("--format", "ndjson")

        self.assertEqual(0, completed.returncode, completed.stderr)
        events = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(["started", "result"], [event["event"] for event in events])
        self.assertEqual("TEST_ONLY", events[0]["mode"])
        self.assertEqual("RETURNED", events[1]["state"])
        self.assertEqual("2.0.1-rc.1", events[1]["atlas_version"])
        self.assertEqual("2.0.1-rc.1", events[1]["argus_version"])
        self.assertTrue(events[1]["result_sha256"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
