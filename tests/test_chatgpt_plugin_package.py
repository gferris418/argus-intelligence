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

    def test_bundles_all_modular_skills_and_required_contracts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        required_paths = [
            "skills/argus-intelligence/SKILL.md",
            "skills/argus-intelligence/references/mission-routing.md",
            "skills/argus-intelligence/references/untrusted-source-boundary.md",
            "skills/argus-opportunity-intelligence/SKILL.md",
            "skills/argus-ecosystem-intelligence/SKILL.md",
            "skills/argus-procurement-market-intelligence/SKILL.md",
            "skills/argus-monitoring-revalidation/SKILL.md",
            "spec/persistence.yaml",
            "spec/mission-skill-routing.yaml",
            "schemas/mission-skill-plan.schema.json",
        ]
        for path in required_paths:
            self.assertIn(path, text, path)

        self.assertIn("mkdir -p dist/plugin-package/argus-intelligence/schemas", text)
        self.assertIn("cp -R skills/argus-intelligence", text)
        self.assertIn("cp -R skills/argus-opportunity-intelligence", text)
        self.assertIn("cp -R skills/argus-ecosystem-intelligence", text)
        self.assertIn("cp -R skills/argus-procurement-market-intelligence", text)
        self.assertIn("cp -R skills/argus-monitoring-revalidation", text)

    def test_modular_contracts_are_release_driving(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for trigger in (
            "skills/argus-opportunity-intelligence/**",
            "skills/argus-ecosystem-intelligence/**",
            "skills/argus-procurement-market-intelligence/**",
            "skills/argus-monitoring-revalidation/**",
            "spec/mission-skill-routing.yaml",
            "schemas/mission-skill-plan.schema.json",
            "tests/test_modular_skill_pilots.py",
            "tests/scenarios/modular-skill-pilots.json",
        ):
            self.assertIn(trigger, text, trigger)


if __name__ == "__main__":
    unittest.main()
