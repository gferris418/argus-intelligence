from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "postgres-scale-benchmark.yml"
HARNESS = ROOT / "benchmarks" / "postgres" / "scale_benchmark.py"
CONTRACT = ROOT / "benchmarks" / "postgres" / "tender-search-contract.yaml"


class PostgresScaleBenchmarkContractTests(unittest.TestCase):
    def test_workflow_is_isolated_postgres18_and_artifacts_results(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        required = (
            "workflow_dispatch:",
            "pull_request:",
            "postgres:18",
            "timeout-minutes: 60",
            "migrations/postgres/0001_argus_operational_projection.sql",
            "migrations/postgres/0002_argus_fuzzy_knn.sql",
            "benchmarks/postgres/scale_benchmark.py",
            "psycopg[binary]",
            "PyYAML",
            "actions/upload-artifact@",
            "postgres-scale-benchmark",
        )
        for token in required:
            self.assertIn(token, workflow)
        self.assertNotIn("rapid-field-91311881", workflow)
        self.assertNotIn("NEON_DATABASE_URL", workflow)

    def test_harness_honors_committed_scale_and_concurrency_contract(self) -> None:
        harness = HARNESS.read_text(encoding="utf-8")
        contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual([10_000, 100_000, 1_000_000], contract["dataset_scales"])
        self.assertEqual([1, 8, 32], contract["concurrency"]["reader_levels"])
        self.assertEqual([0, 1, 4], contract["concurrency"]["writer_levels"])
        self.assertEqual(60, contract["concurrency"]["duration_seconds"])
        for token in (
            "dataset_scales",
            "reader_levels",
            "writer_levels",
            "duration_seconds",
            "exact_reference",
            "exact_project_code",
            "fts",
            "fuzzy",
            "ThreadPoolExecutor",
            "p50",
            "p95",
            "p99",
            "zero_query_errors",
            "overall_pass",
        ):
            self.assertIn(token, harness)

    def test_harness_is_disposable_and_never_targets_neon_production(self) -> None:
        harness = HARNESS.read_text(encoding="utf-8")
        self.assertNotIn("rapid-field-91311881", harness)
        self.assertNotIn("br-spring-feather-a1cjndbm", harness)
        self.assertIn("ARGUS_BENCH_DSN", harness)
        self.assertIn("ARGUS_BENCH_ADMIN_DSN", harness)


if __name__ == "__main__":
    unittest.main()
