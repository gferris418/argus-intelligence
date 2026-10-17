import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()
ARCH = (ROOT / "docs" / "architecture" / "github-first-canonical-store.md").read_text()

PROHIBITED_DATA_SUFFIXES = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".msg", ".eml",
    ".zip", ".rar", ".7z", ".tar", ".gz"
}
PROHIBITED_DIR_NAMES = {"raw", "tenders", "tender-documents", "source-documents", "attachments"}


class GitHubStoragePolicy(unittest.TestCase):
    def test_manifest_declares_github_interim_canonical_store(self):
        self.assertIn("physical_canonical_store: github", MANIFEST)
        self.assertIn("canonical_structured_path: data/registry", MANIFEST)
        self.assertIn("raw_tender_documents_in_github: prohibited", MANIFEST)
        self.assertIn("operational_database_runtime: deferred", MANIFEST)

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

    def test_architecture_keeps_logical_registry_platform_neutral(self):
        self.assertIn("logical ARGUS Master Registry contract remains platform-neutral", ARCH)
        self.assertIn("JSON or JSONL", ARCH)
        self.assertIn("Raw tender/source documents", ARCH)


if __name__ == "__main__":
    unittest.main()
