import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "argus-intelligence" / "SKILL.md"
CONTRACT = ROOT / "spec" / "persistence.yaml"


class SharePointPersistenceContractTests(unittest.TestCase):
    def test_canonical_business_intelligence_root_and_taxonomy(self):
        self.assertTrue(CONTRACT.is_file(), "missing ARGUS persistence contract")
        contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))

        self.assertEqual("1.0.0", contract["version"])
        self.assertEqual("argus-intelligence", contract["authority"]["provider"])
        self.assertEqual("atlas-os", contract["authority"]["governor"])
        self.assertEqual("accessasiaccl.sharepoint.com", contract["sharepoint"]["hostname"])
        self.assertEqual("/sites/accessasia", contract["sharepoint"]["site_path"])
        self.assertEqual("General/Business Intelligence", contract["root"]["path"])
        self.assertEqual("50_OPPORTUNITIES", contract["routing"]["opportunity_intelligence"])
        self.assertEqual("99_INBOX", contract["routing"]["unresolved_or_unclassified"])
        self.assertTrue(contract["rules"]["preserve_source_files"])
        self.assertTrue(contract["rules"]["durable_write_receipt_required"])
        self.assertTrue(contract["rules"]["single_canonical_copy"])

    def test_skill_requires_canonical_persistence_and_fail_closed_receipts(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("spec/persistence.yaml", text)
        self.assertIn("General/Business Intelligence", text)
        self.assertIn("50_OPPORTUNITIES", text)
        self.assertIn("PERSISTENCE_PENDING", text)
        self.assertIn("ATLAS authorization", text)


if __name__ == "__main__":
    unittest.main()
