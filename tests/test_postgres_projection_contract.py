from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from tools.postgres_search import TenderSearchAdapter, TenderSearchConfig, build_tender_search_steps

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "postgres" / "0001_argus_operational_projection.sql"
RECOVERY = ROOT / "docs" / "architecture" / "postgresql-production-hardening.md"
BENCHMARK = ROOT / "benchmarks" / "postgres" / "tender-search-contract.yaml"
MANIFEST = ROOT / "argus-intelligence.yaml"


class _FakeCursor:
    def __init__(self, scripted_rows: list[list[tuple]]) -> None:
        self.scripted_rows = scripted_rows
        self.executed: list[tuple[str, tuple | None]] = []
        self._rows: list[tuple] = []
        self.description = [
            ("canonical_tender_id",),
            ("tender_reference",),
            ("project_code",),
            ("title",),
            ("buyer_name",),
            ("status",),
            ("closing_at",),
            ("source_url",),
            ("score",),
        ]

    def execute(self, sql: str, params: tuple | None = None) -> None:
        self.executed.append((sql, params))
        if "argus.search_tenders" in sql:
            self._rows = self.scripted_rows.pop(0) if self.scripted_rows else []
        else:
            self._rows = []

    def fetchall(self) -> list[tuple]:
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FakeConnection:
    def __init__(self, scripted_rows: list[list[tuple]]) -> None:
        self.cursor_instance = _FakeCursor(scripted_rows)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self) -> _FakeCursor:
        return self.cursor_instance

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class PostgresProjectionContractTests(unittest.TestCase):
    def test_manifest_admits_postgres_as_governed_runtime_projection_without_replacing_sqlite(self) -> None:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        authority = manifest["authority"]
        projections = manifest["operational_projections"]
        self.assertEqual(
            "migrations/postgres/0001_argus_operational_projection.sql",
            authority["postgres_operational_projection_migration"],
        )
        self.assertEqual("tools/postgres_search.py", authority["postgres_query_adapter"])
        self.assertEqual("ACTIVE", projections["sqlite_sharepoint"]["status"])
        self.assertEqual("ADMITTED_NOT_PRODUCTION", projections["postgresql"]["status"])
        self.assertFalse(projections["postgresql"]["production_cutover_approved"])

    def test_migration_is_idempotent_additive_and_preserves_canonical_lineage(self) -> None:
        sql = MIGRATION.read_text(encoding="utf-8")
        required = (
            "CREATE SCHEMA IF NOT EXISTS argus",
            "CREATE EXTENSION IF NOT EXISTS pg_trgm",
            "CREATE TABLE IF NOT EXISTS argus.schema_migration",
            "CREATE TABLE IF NOT EXISTS argus.object_type_registry",
            "CREATE TABLE IF NOT EXISTS argus.status_registry",
            "CREATE TABLE IF NOT EXISTS argus.source_record",
            "CREATE TABLE IF NOT EXISTS argus.canonical_object",
            "CREATE TABLE IF NOT EXISTS argus.tender",
            "REFERENCES argus.canonical_object",
            "REFERENCES argus.source_record",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_tender_reference_scope",
            "CREATE TRIGGER canonical_object_set_updated_at",
            "CREATE OR REPLACE FUNCTION argus.search_tenders",
            "CREATE OR REPLACE FUNCTION argus.list_tenders",
            "REVOKE ALL ON SCHEMA argus FROM PUBLIC",
            "GRANT USAGE ON SCHEMA argus TO argus_reader",
        )
        for token in required:
            self.assertIn(token, sql)
        self.assertNotIn("DROP TABLE", sql.upper())
        self.assertNotIn("TRUNCATE", sql.upper())

    def test_recovery_and_benchmark_contracts_are_versioned(self) -> None:
        recovery = RECOVERY.read_text(encoding="utf-8")
        benchmark = yaml.safe_load(BENCHMARK.read_text(encoding="utf-8"))
        for token in (
            "pre-migration snapshot",
            "dedicated migration role",
            "post-migration smoke",
            "rollback",
            "restore rehearsal",
            "production branch protection",
        ):
            self.assertIn(token, recovery.lower())
        self.assertEqual([10_000, 100_000, 1_000_000], benchmark["dataset_scales"])
        self.assertEqual(["p50", "p95", "p99"], benchmark["latency_percentiles"])
        self.assertIn("cold_cache", benchmark["workloads"])
        self.assertIn("concurrent_readers", benchmark["workloads"])
        self.assertIn("concurrent_ingestion", benchmark["workloads"])
        self.assertIn("expected_plan", benchmark["queries"]["exact_reference"])


class PostgresSearchAdapterTests(unittest.TestCase):
    def test_search_steps_are_parameterized_projected_and_ordered_exact_fts_fuzzy(self) -> None:
        steps = build_tender_search_steps("CPV-2026", 20)
        self.assertEqual(
            ["exact_reference", "exact_project_code", "fts", "fuzzy"],
            [step.mode for step in steps],
        )
        for step in steps:
            upper = step.sql.upper()
            self.assertNotIn("SELECT *", upper)
            self.assertIn("%S", upper)
            self.assertEqual((step.mode, "CPV-2026", 20), step.params)

    def test_limit_is_hard_bounded(self) -> None:
        for invalid in (0, -1, 101, 1000):
            with self.assertRaises(ValueError):
                build_tender_search_steps("query", invalid)
        self.assertEqual(4, len(build_tender_search_steps("query", 100)))

    def test_adapter_enforces_read_only_timeout_and_exact_to_fuzzy_fallback(self) -> None:
        final_row = (
            "TND-BD-000001",
            "REF-1",
            "PRJ-1",
            "Coastal Patrol Vessel",
            "Buyer",
            "active",
            None,
            "https://example.test/tender/1",
            0.87,
        )
        conn = _FakeConnection([[], [], [], [final_row]])
        adapter = TenderSearchAdapter(TenderSearchConfig(statement_timeout_ms=1500))
        result = adapter.search(conn, "Costal Patrol Vesel", limit=20)

        self.assertEqual("fuzzy", result.route)
        self.assertEqual(1, len(result.rows))
        self.assertEqual(4, result.query_count)
        self.assertGreaterEqual(result.latency_ms, 0)

        executed = conn.cursor_instance.executed
        self.assertTrue(any("SET TRANSACTION READ ONLY" in sql for sql, _ in executed))
        self.assertTrue(any("SET LOCAL statement_timeout" in sql for sql, _ in executed))
        search_calls = [(sql, params) for sql, params in executed if "argus.search_tenders" in sql]
        self.assertEqual(4, len(search_calls))
        self.assertTrue(all(params is not None for _, params in search_calls))
        self.assertEqual(0, conn.commits)
        self.assertEqual(1, conn.rollbacks)

    def test_empty_query_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_tender_search_steps("   ", 20)


if __name__ == "__main__":
    unittest.main()
