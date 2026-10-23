from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.cross_repo_e2e import _prepare_atlas_import


ROOT = Path(__file__).resolve().parents[1]
ATLAS_COMMIT = "27e57c3a80c0910e7fb2fca320d8fad22f4031af"


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

    def test_automatic_workflow_pins_public_atlas_boundary_without_secret(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "cross-repo-e2e.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("repository: gferris418/atlas-os", workflow)
        self.assertIn(f"ref: {ATLAS_COMMIT}", workflow)
        self.assertNotIn("ATLAS_SSH_KEY", workflow)
        self.assertNotIn("ATLAS_READ_TOKEN", workflow)
        self.assertEqual(2, workflow.count("persist-credentials: false"))
        self.assertIn("python -m unittest discover -s tests/cross_repo -v", workflow)

    def test_modified_tracked_atlas_runtime_is_rejected_even_when_head_matches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            atlas = Path(directory)
            (atlas / "atlas_runtime").mkdir()
            (atlas / "integrations").mkdir()
            (atlas / "atlas-os.yaml").write_text(
                "product:\n  version: test-version\n", encoding="utf-8"
            )
            runtime = atlas / "atlas_runtime" / "__init__.py"
            runtime.write_text("VALUE = 'committed'\n", encoding="utf-8")
            (atlas / "integrations" / "argus.yaml").write_text(
                "capability: intelligence_collection\nactivation_authority: ATLAS\nnext_step_authority: ATLAS\nexplicit_user_approval_required: true\n",
                encoding="utf-8",
            )
            (atlas / "integrations" / "chatgpt-bootstrap.yaml").write_text(
                "version: 1.0.1\n", encoding="utf-8"
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
                return_value={
                    "atlas": {
                        "commit": head,
                        "version": "test-version",
                        "integration_path": "integrations/argus.yaml",
                        "canonical_execution_contract": {
                            "path": "contracts/atlas-argus-execution-v2.json",
                            "version": "2.0.0",
                            "sha256": "0" * 64,
                        },
                    },
                    "contract": {
                        "capability": "intelligence_collection",
                        "activation_authority": "ATLAS",
                        "next_step_authority": "ATLAS",
                    },
                },
            ), self.assertRaisesRegex(ValueError, "tracked files differ"):
                _prepare_atlas_import(atlas)


if __name__ == "__main__":
    unittest.main()
