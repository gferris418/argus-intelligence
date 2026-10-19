from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.cross_repo_e2e import _prepare_atlas_import


ROOT = Path(__file__).resolve().parents[1]


class CrossRepositoryCommandTests(unittest.TestCase):
    def test_missing_atlas_checkout_fails_concisely(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.cross_repo_e2e",
                "--atlas-repo",
                str(ROOT / "missing-atlas-checkout"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(2, completed.returncode)
        self.assertIn("ATLAS checkout not found", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertEqual("", completed.stdout)

    def test_manual_workflow_pins_both_private_repository_boundaries(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "cross-repo-e2e.yml").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("pull_request:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("repository: gferris418/atlas-os", workflow)
        self.assertIn("ref: a533d092fb35f5c048a96f46c0201d5ce37871c7", workflow)
        self.assertIn("secrets.ATLAS_READ_TOKEN", workflow)
        self.assertEqual(2, workflow.count("persist-credentials: false"))
        self.assertIn("python -m unittest discover -s tests/cross_repo -v", workflow)

    def test_modified_tracked_atlas_runtime_is_rejected_even_when_head_matches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            atlas = Path(directory)
            (atlas / "atlas_runtime").mkdir()
            (atlas / "registries").mkdir()
            (atlas / "atlas-os.yaml").write_text(
                "product:\n  version: test-version\n", encoding="utf-8"
            )
            runtime = atlas / "atlas_runtime" / "__init__.py"
            runtime.write_text("VALUE = 'committed'\n", encoding="utf-8")
            (atlas / "registries" / "domain-methods.yaml").write_text(
                "registry: {}\n", encoding="utf-8"
            )
            for command in (
                ["git", "init", "-q"],
                ["git", "config", "user.name", "Test"],
                ["git", "config", "user.email", "test@example.invalid"],
                ["git", "add", "."],
                ["git", "commit", "-qm", "fixture"],
            ):
                subprocess.run(command, cwd=atlas, check=True)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=atlas,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            runtime.write_text("VALUE = 'modified'\n", encoding="utf-8")

            with patch(
                "tools.cross_repo_e2e._load_compatibility",
                return_value={"atlas_commit": head, "atlas_version": "test-version"},
            ), self.assertRaisesRegex(ValueError, "tracked files differ"):
                _prepare_atlas_import(atlas)


if __name__ == "__main__":
    unittest.main()
