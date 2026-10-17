import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v2.0.yaml"
MIGRATION = ROOT / "profiles" / "bangladesh-procurement-v1-to-v2-migration.yaml"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()

OLD_FILES = [
    ROOT / "profiles" / "bangladesh-data-standard.yaml",
    ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v1.1.yaml",
    ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v1.2.yaml",
    ROOT / "profiles" / "bangladesh-canonical-procurement-standard-v1.3.yaml",
]
FIELD_RE = re.compile(r"^  ([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+):\s*$", re.MULTILINE)
MAPPING_KEY_RE = re.compile(r"^  ([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+):\s*$", re.MULTILINE)
ACTION_RE = re.compile(r"^    action:\s*(KEEP|RENAME|MERGE|DERIVE|DEPRECATE)\s*$", re.MULTILINE)
FIELD_ENTRY_RE = re.compile(r"^    ([a-z][a-z0-9_]*):\s*$", re.MULTILINE)


class BangladeshCanonicalProcurementV2(unittest.TestCase):
    def setUp(self):
        self.assertTrue(V2.exists(), "v2 standard must exist")
        self.assertTrue(MIGRATION.exists(), "v1-to-v2 migration map must exist")
        self.v2 = V2.read_text()
        self.migration = MIGRATION.read_text()

    def test_v2_is_candidate_and_not_live_migration(self):
        self.assertIn("version: 2.0.0", self.v2)
        self.assertIn("status: CANDIDATE", self.v2)
        self.assertIn("bangladesh_procurement_candidate_v2:", MANIFEST)
        self.assertIn("live_record_migration: DEFERRED", MANIFEST)
        self.assertIn("bangladesh_procurement_standard: profiles/bangladesh-canonical-procurement-standard-v1.3.yaml", MANIFEST)

    def test_semantic_objects_are_explicit(self):
        for obj in (
            "party_role_link", "budget", "financing", "process", "lot", "item",
            "notice", "milestone", "event", "requirement", "fee", "security",
            "contact_point", "award", "contract", "implementation", "observation",
            "intelligence",
        ):
            self.assertIn(f"  {obj}:", self.v2, obj)

    def test_one_concept_one_home_and_derived_counters(self):
        lower = self.v2.lower()
        self.assertIn("one real-world concept has one canonical home", lower)
        self.assertIn("derived", lower)
        self.assertIn("extension_count", self.v2)
        self.assertIn("do_not_store", self.v2)
        for deprecated_scalar in (
            "institution.ministry_name:", "institution.division_name:",
            "solicitation.id:", "award.contract_no:",
        ):
            self.assertNotIn(deprecated_scalar, self.v2)

    def test_field_dictionary_entries_are_explained(self):
        self.assertIn("field_dictionary:", self.v2)
        for token in (
            "definition:", "cardinality:", "when_populated:",
            "not_to_confuse_with:", "international_alignment:",
        ):
            self.assertIn(token, self.v2)
        # The candidate must explain a substantial set of atomic fields, not only object names.
        entries = FIELD_ENTRY_RE.findall(self.v2.split("field_dictionary:", 1)[1])
        self.assertGreaterEqual(len(set(entries)), 55)

    def test_v1_field_migration_map_is_exhaustive(self):
        old_fields = set()
        for path in OLD_FILES:
            old_fields.update(FIELD_RE.findall(path.read_text()))
        mapped = set(MAPPING_KEY_RE.findall(self.migration))
        missing = sorted(old_fields - mapped)
        self.assertFalse(missing, f"unmapped v1 fields: {missing}")
        self.assertIn("allowed_actions: [KEEP, RENAME, MERGE, DERIVE, DEPRECATE]", self.migration)
        self.assertGreaterEqual(len(ACTION_RE.findall(self.migration)), len(old_fields))

    def test_high_risk_semantic_mappings_are_explicit(self):
        expected = {
            "solicitation.system_id": ("RENAME", "identifiers"),
            "solicitation.reference_no": ("RENAME", "identifiers"),
            "procurement.type": ("RENAME", "process.competition_scope"),
            "procurement.method": ("RENAME", "process.method"),
            "procurement.process": ("RENAME", "process.configuration"),
            "procurement.events": ("RENAME", "events"),
            "solicitation.extension_count": ("DERIVE", "events"),
            "award.contract_no": ("RENAME", "contract.contract_number"),
        }
        for source, (action, target) in expected.items():
            pattern = rf"(?ms)^  {re.escape(source)}:\s*$.*?^    action:\s*{action}\s*$.*?^    target:\s*.*{re.escape(target)}.*$"
            self.assertRegex(self.migration, pattern, source)


if __name__ == "__main__":
    unittest.main()
