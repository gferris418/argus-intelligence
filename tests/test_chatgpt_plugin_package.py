from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "chatgpt-plugin-package.yml"


class ChatGPTPluginPackageWorkflowTests(unittest.TestCase):
    def test_packages_exact_revision_and_emits_hashed_sync_handoff(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: ${{ github.event.pull_request.head.sha || github.sha }}", text)
        self.assertIn("name: Build synchronization request", text)
        self.assertIn("hashlib.sha256", text)
        self.assertIn("plugin-sync-request.json", text)
        self.assertIn("chatgpt_plugin_sync_required", text)
        self.assertIn("artifact_only_publication_input", text)
        self.assertIn("publication_receipt_required", text)
        self.assertIn("name: Emit repository synchronization event", text)
        self.assertIn("github.event_name == 'push'", text)

    def test_bundles_persistence_contract_required_by_skill(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("'spec/persistence.yaml'", text)
        self.assertIn(
            "mkdir -p dist/plugin-package/argus-intelligence/spec",
            text,
        )
        self.assertIn(
            "cp spec/persistence.yaml dist/plugin-package/argus-intelligence/spec/persistence.yaml",
            text,
        )


if __name__ == "__main__":
    unittest.main()
