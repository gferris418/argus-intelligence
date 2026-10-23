from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class MachineContractSyntaxTests(unittest.TestCase):
    def test_all_tracked_yaml_and_json_documents_parse(self) -> None:
        paths = sorted(
            path
            for suffix in ("*.yaml", "*.yml", "*.json")
            for path in ROOT.rglob(suffix)
            if ".git" not in path.parts and "dist" not in path.parts
        )
        self.assertTrue(paths)

        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                if path.suffix == ".json":
                    json.loads(text)
                else:
                    yaml.safe_load(text)
