from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from tools.postgres_benchmark import percentile, summarize_samples


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "postgres_benchmark.py"
MANIFEST = ROOT / "argus-intelligence.yaml"


class PostgresBenchmarkRunnerTests(unittest.TestCase):
    def test_manifest_registers_the_reproducible_runner(self) -> None:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            "tools/postgres_benchmark.py",
            manifest["authority"]["postgres_benchmark_runner"],
        )
        self.assertTrue(RUNNER.is_file())

    def test_percentiles_use_nearest_rank(self) -> None:
        values = [10.0, 1.0, 5.0, 2.0, 20.0]
        self.assertEqual(5.0, percentile(values, 0.50))
        self.assertEqual(20.0, percentile(values, 0.95))
        self.assertIsNone(percentile([], 0.50))

    def test_summary_counts_errors_without_treating_them_as_latency(self) -> None:
        summary = summarize_samples(
            [
                ("fts", 10.0, 20, None),
                ("fts", 30.0, 20, None),
                ("fts", 2_000.0, 0, "QueryCanceled"),
            ]
        )["fts"]

        self.assertEqual(3, summary["samples"])
        self.assertEqual(2, summary["successful"])
        self.assertEqual(1, summary["errors"])
        self.assertEqual(10.0, summary["p50_ms"])
        self.assertEqual(30.0, summary["p95_ms"])
        self.assertEqual(["QueryCanceled"], summary["error_classes"])

    def test_runner_uses_fixed_projected_sql_and_rollback_only_writes(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("SELECT *", text.upper())
        self.assertIn("SET TRANSACTION READ ONLY", text)
        self.assertIn("connection.rollback()", text)
        self.assertIn("ARGUS_BENCHMARK_DSN", text)
        self.assertNotIn("--dsn", text)


if __name__ == "__main__":
    unittest.main()
