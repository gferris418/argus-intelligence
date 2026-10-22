import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()
ARCH = (ROOT / "docs" / "architecture" / "canonical-identity-operational-database-v1.md").read_text()

PROHIBITED_DATA_SUFFIXES = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".msg", ".eml",
    ".zip", ".rar", ".7z", ".tar", ".gz"
}
PROHIBITED_DIR_NAMES = {"raw", "tenders", "tender-documents", "source-documents", "attachments"}


class GitHubStoragePolicy(unittest.TestCase):
    def test_manifest_declares_sharepoint_operational_store_and_github_governance_role(self):
        self.assertIn("physical_canonical_store: sharepoint_sqlite", MANIFEST)
        self.assertIn("sharepoint_operational_store: true", MANIFEST)
        self.assertIn("operational_database_runtime: active_single_writer", MANIFEST)
        self.assertIn("github_registry_role: migration_bootstrap_audit_and_release_snapshots", MANIFEST)
        self.assertIn("raw_tender_documents_in_github: prohibited", MANIFEST)

    def test_data_tree_contains_no_prohibited_raw_document_formats(self):
        offenders = []
        for path in DATA.rglob("*"):
            if path.is_file() and path.suffix.lower() in PROHIBITED_DATA_SUFFIXES:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [], f"raw/source document formats are prohibited under data/: {offenders}")

    def test_data_tree_contains_no_raw_source_directories(self):
        offenders = []
        for path in DATA.rglob("*"):
            if path.is_dir() and path.name.lower() in PROHIBITED_DIR_NAMES:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [], f"raw/source directories are prohibited under data/: {offenders}")

    def test_architecture_preserves_logical_registry_and_explicit_store_boundary(self):
        self.assertIn("GitHub", ARCH)
        self.assertIn("SharePoint SQLite", ARCH)
        self.assertIn("current mutable operational ARGUS structured state", ARCH)
        self.assertIn("Existing GitHub JSON/JSONL registry records remain migration/audit/bootstrap material", ARCH)
        self.assertIn("SharePoint source and working documents remain files", ARCH)


if __name__ == "__main__":
    unittest.main()
