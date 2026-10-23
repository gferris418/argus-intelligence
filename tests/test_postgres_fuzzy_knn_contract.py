from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "postgres" / "0002_argus_fuzzy_knn.sql"
BENCHMARK = ROOT / "benchmarks" / "postgres" / "tender-search-contract.yaml"


class PostgresFuzzyKnnContractTests(unittest.TestCase):
    def test_additive_migration_uses_gist_knn_for_fuzzy_top_n(self) -> None:
        sql = MIGRATION.read_text(encoding="utf-8")
        required = (
            "CREATE INDEX IF NOT EXISTS idx_tender_title_trgm_gist",
            "USING gist",
            "public.gist_trgm_ops",
            "CREATE OR REPLACE FUNCTION argus.search_tenders",
            "p_mode = 'fuzzy'",
            "OPERATOR(public.<->)",
            "ORDER BY t.title OPERATOR(public.<->) btrim(p_query)",
            "LIMIT argus.enforce_result_limit(p_limit)",
        )
        for token in required:
            self.assertIn(token, sql)
        self.assertNotIn("DROP TABLE", sql.upper())
        self.assertNotIn("TRUNCATE", sql.upper())

    def test_benchmark_contract_requires_gist_knn_index_for_fuzzy(self) -> None:
        benchmark = yaml.safe_load(BENCHMARK.read_text(encoding="utf-8"))
        fuzzy = benchmark["queries"]["fuzzy"]
        self.assertEqual(
            "idx_tender_title_trgm_gist",
            fuzzy["expected_plan"]["required_index_family"],
        )
        self.assertEqual("GIST_TRGM_KNN", fuzzy["expected_plan"]["index_type"])
        self.assertEqual("nearest_neighbor", fuzzy["expected_plan"]["strategy"])
        self.assertTrue(fuzzy["expected_plan"]["disallow_sequential_scan_at_scale"] <= 100000)


if __name__ == "__main__":
    unittest.main()
