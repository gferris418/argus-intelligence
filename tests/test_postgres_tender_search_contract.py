from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "registry" / "migrations" / "postgres-1.0.0-argus-tender-search.sql"


class PostgresTenderSearchContractTests(unittest.TestCase):
    def test_manifest_governs_the_postgres_search_migration(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))

        self.assertIn("postgres_tender_search_migration", manifest["authority"])
        self.assertEqual(
            "registry/migrations/postgres-1.0.0-argus-tender-search.sql",
            manifest["authority"]["postgres_tender_search_migration"],
        )
        self.assertTrue(MIGRATION.is_file())

    def test_migration_enforces_bounded_least_privilege_search(self) -> None:
        sql = MIGRATION.read_text(encoding="utf-8")

        self.assertIn("SECURITY DEFINER", sql)
        self.assertIn("SET statement_timeout = '2s'", sql)
        self.assertIn("argus.enforce_result_limit(p_limit)", sql)
        self.assertIn("REVOKE ALL ON ALL TABLES IN SCHEMA argus FROM PUBLIC, argus_reader", sql)
        self.assertIn("GRANT EXECUTE ON FUNCTION argus.search_tenders", sql)
        self.assertNotIn("GRANT SELECT ON argus.tender TO argus_reader", sql)
        self.assertNotIn("SELECT *", sql.upper())

    def test_migration_preserves_fast_paths_and_automatic_update_timestamps(self) -> None:
        sql = MIGRATION.read_text(encoding="utf-8")

        for index_name in (
            "idx_tender_reference_lower",
            "idx_tender_project_code_lower",
            "idx_tender_status_closing",
            "idx_tender_search_vector",
            "idx_tender_title_trgm",
        ):
            self.assertIn(index_name, sql)
        self.assertIn("CREATE OR REPLACE TRIGGER canonical_object_set_updated_at", sql)
        self.assertIn("p_mode = 'fuzzy'", sql)


if __name__ == "__main__":
    unittest.main()
