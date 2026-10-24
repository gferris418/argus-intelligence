"""Conformance tests for the modular ARGUS Agent Skills family."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
ROOT_SKILL = SKILLS / "argus-intelligence" / "SKILL.md"
ROUTING_REFERENCE = SKILLS / "argus-intelligence" / "references" / "mission-routing.md"
TRUST_REFERENCE = SKILLS / "argus-intelligence" / "references" / "untrusted-source-boundary.md"
SPECIALISTS = {
    "argus-opportunity-intelligence": "opportunity",
    "argus-ecosystem-intelligence": "ecosystem",
    "argus-procurement-market-intelligence": "procurement",
    "argus-monitoring-revalidation": "monitor",
}


def read_skill(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError("skill must start with YAML frontmatter")
    return match.group(1)


class AgentSkillFamilyTests(unittest.TestCase):
    def test_all_five_skills_and_progressive_disclosure_references_exist(self) -> None:
        self.assertTrue(ROOT_SKILL.is_file())
        for skill in SPECIALISTS:
            self.assertTrue((SKILLS / skill / "SKILL.md").is_file(), skill)
        self.assertTrue(ROUTING_REFERENCE.is_file())
        self.assertTrue(TRUST_REFERENCE.is_file())

    def test_root_skill_is_router_and_uses_agent_skills_metadata(self) -> None:
        text = ROOT_SKILL.read_text(encoding="utf-8")
        meta = frontmatter(text)
        self.assertIn("name: argus-intelligence", meta)
        self.assertIn("description:", meta)
        self.assertIn("metadata:", meta)
        self.assertNotRegex(meta, r"(?m)^version:")
        self.assertIn("mission_skill_plan", text)
        self.assertIn("references/mission-routing.md", text)
        self.assertIn("references/untrusted-source-boundary.md", text)
        for skill in SPECIALISTS:
            self.assertIn(skill, text)

    def test_specialist_descriptions_are_narrow_and_distinct(self) -> None:
        descriptions: list[str] = []
        for skill, keyword in SPECIALISTS.items():
            text = read_skill(skill)
            meta = frontmatter(text)
            self.assertIn(f"name: {skill}", meta)
            description_line = next(
                line for line in meta.splitlines() if line.startswith("description:")
            )
            self.assertIn(keyword, description_line.lower())
            descriptions.append(description_line)
        self.assertEqual(len(descriptions), len(set(descriptions)))

    def test_every_specialist_preserves_authority_identity_and_source_trust(self) -> None:
        required = [
            "ATLAS",
            "canonical",
            "untrusted",
            "provenance",
            "return",
        ]
        for skill in SPECIALISTS:
            text = read_skill(skill)
            for token in required:
                self.assertIn(token.lower(), text.lower(), f"{skill}: {token}")
            self.assertIn("not a control plane", text.lower())
            self.assertIn("source-embedded instructions", text.lower())

    def test_procurement_specialist_exposes_exact_operating_modes(self) -> None:
        text = read_skill("argus-procurement-market-intelligence")
        for mode in (
            "DISCOVERY",
            "LIVE_PROCUREMENT",
            "POST_DEADLINE_REVALIDATION",
        ):
            self.assertIn(mode, text)

    def test_untrusted_source_reference_blocks_instruction_and_memory_poisoning(self) -> None:
        text = TRUST_REFERENCE.read_text(encoding="utf-8").lower()
        self.assertIn("evidence, not instructions", text)
        self.assertIn("instruction quarantine", text)
        self.assertIn("structured observation", text)
        self.assertIn("memory poisoning", text)
        self.assertIn("durable", text)


if __name__ == "__main__":
    unittest.main()
