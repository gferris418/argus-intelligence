from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "contract-tests.yml"
QUALITY_REQUIREMENTS = ROOT / "requirements-quality.txt"


class QualityRatchetContractTests(unittest.TestCase):
    def test_quality_tools_are_separately_pinned(self) -> None:
        self.assertTrue(QUALITY_REQUIREMENTS.is_file())
        text = QUALITY_REQUIREMENTS.read_text(encoding="utf-8")
        self.assertIn("coverage==", text)
        self.assertIn("mypy==", text)
        self.assertIn("ruff==", text)
        self.assertIn("types-PyYAML==", text)

    def test_contract_workflow_enforces_critical_path_quality(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("requirements-quality.txt", workflow)
        self.assertIn("name: Ruff critical execution paths", workflow)
        self.assertIn("name: Mypy critical execution paths", workflow)
        self.assertIn("name: Critical-path coverage ratchet", workflow)
        self.assertIn("--source=tools", workflow)
        self.assertIn("--fail-under=75", workflow)
        for path in (
            "tools/atlas_contract.py",
            "tools/atlas_v3_provider.py",
            "tools/postgres_search.py",
            "tools/argus_runtime.py",
            "tools/cross_repo_e2e.py",
        ):
            self.assertIn(path, workflow)


if __name__ == "__main__":
    unittest.main()
