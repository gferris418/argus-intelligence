import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "bangladesh-procurement-v2.schema.json"
DICTIONARY = ROOT / "profiles" / "bangladesh-procurement-v2-field-dictionary.json"


def schema_property_paths(schema):
    paths = {f"root.{name}" for name in schema.get("properties", {})}
    for def_name, definition in schema.get("$defs", {}).items():
        for prop_name in definition.get("properties", {}):
            paths.add(f"{def_name}.{prop_name}")
    return paths


class BangladeshProcurementV2FieldDictionary(unittest.TestCase):
    def test_every_machine_field_has_one_complete_human_definition(self):
        self.assertTrue(DICTIONARY.exists())
        schema = json.loads(SCHEMA.read_text())
        dictionary = json.loads(DICTIONARY.read_text())
        schema_paths = schema_property_paths(schema)
        documented_paths = set(dictionary["fields"])
        self.assertEqual(documented_paths, schema_paths)
        for path, metadata in dictionary["fields"].items():
            for key in ("definition", "cardinality", "when_populated", "not_to_confuse_with"):
                self.assertIsInstance(metadata.get(key), str, f"{path}.{key}")
                self.assertTrue(metadata[key].strip(), f"{path}.{key}")

    def test_dictionary_keeps_core_semantic_distinctions_explicit(self):
        fields = json.loads(DICTIONARY.read_text())["fields"]
        self.assertIn("market scope", fields["process.competition_scope"]["definition"].lower())
        self.assertIn("selection", fields["process.method_normalized"]["definition"].lower())
        self.assertIn("planned", fields["milestone.type"]["definition"].lower())
        self.assertIn("actual", fields["notice.published_at"]["definition"].lower())
        self.assertIn("source", fields["observation.raw_value"]["definition"].lower())
        self.assertIn("signed", fields["contract.contract_number"]["definition"].lower())


if __name__ == "__main__":
    unittest.main()
