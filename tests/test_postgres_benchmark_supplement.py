from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "benchmarks" / "postgres" / "benchmark-100k-supplement-2026-10-23.yaml"
CONTRACT = ROOT / "benchmarks" / "postgres" / "tender-search-contract.yaml"


class PostgresBenchmarkSupplementTests(unittest.TestCase):
    def test_cold_compute_probe_uses_every_required_index_and_records_buffers(self) -> None:
        evidence = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))
        contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
        probe = evidence["cold_compute_probe"]

        self.assertEqual("PARTIAL_PASS", probe["status"])
        for query_name, query_contract in contract["queries"].items():
            result = probe["queries"][query_name]
            self.assertEqual(
                query_contract["expected_plan"]["required_index_family"],
                result["index"],
            )
            self.assertGreaterEqual(result["shared_read_blocks"], 1)
            self.assertLessEqual(
                result["execution_time_ms"],
                query_contract["acceptance"]["p95_ms_at_1000000"],
            )

    def test_inconclusive_connector_batch_cannot_close_concurrency_gate(self) -> None:
        evidence = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))

        self.assertEqual(
            "NOT_ACCEPTED_AS_CONCURRENCY_EVIDENCE",
            evidence["connector_parallel_probe"]["status"],
        )
        self.assertEqual("BLOCKED", evidence["production_gate"]["overall"])
        self.assertFalse(evidence["production_gate"]["production_cutover_approved"])
        self.assertIn("independent_client_concurrency", evidence["production_gate"]["open_blockers"])
        self.assertIn("one_million_rows", evidence["production_gate"]["open_blockers"])


if __name__ == "__main__":
    unittest.main()
