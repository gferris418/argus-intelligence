from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.argus_operational_db import initialize_database
from tools.commercial_graph_migration import apply_commercial_graph_migration

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "registry" / "migrations" / "1.0.0-to-1.1.0-commercial-graph.sql"


class CommercialGraphSQLiteMigrationTests(unittest.TestCase):
    def test_migration_is_additive_and_registers_new_object_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "registry.sqlite"
            initialize_database(db)
            before = sqlite3.connect(db)
            before_count = before.execute("SELECT COUNT(*) FROM canonical_object").fetchone()[0]
            before.close()

            apply_commercial_graph_migration(db)

            conn = sqlite3.connect(db)
            types = {
                row[0]
                for row in conn.execute(
                    "SELECT object_type FROM object_type_registry WHERE active = 1"
                )
            }
            for object_type in (
                "PRODUCT_CATEGORY",
                "SECTOR",
                "GEOGRAPHY",
                "BID",
                "ACCESS_ASIA_PROJECT",
            ):
                self.assertIn(object_type, types)
            self.assertEqual(
                before_count,
                conn.execute("SELECT COUNT(*) FROM canonical_object").fetchone()[0],
            )
            self.assertEqual(
                "1.1.0",
                conn.execute(
                    "SELECT value FROM schema_meta WHERE key='schema_version'"
                ).fetchone()[0],
            )
            self.assertEqual(2, conn.execute("PRAGMA user_version").fetchone()[0])
            conn.close()

    def test_migration_creates_role_lineage_and_financial_fact_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "registry.sqlite"
            initialize_database(db)
            apply_commercial_graph_migration(db)
            conn = sqlite3.connect(db)
            tables = {
                row[0]
                for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            self.assertTrue(
                {
                    "organization_role",
                    "commercial_lineage",
                    "commercial_lineage_member",
                    "financial_fact",
                }.issubset(tables)
            )
            conn.close()

    def test_migration_creates_department_reporting_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "registry.sqlite"
            initialize_database(db)
            apply_commercial_graph_migration(db)
            conn = sqlite3.connect(db)
            views = {
                row[0]
                for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view'")
            }
            self.assertTrue(
                {
                    "reporting_fact_opportunity",
                    "reporting_fact_bid",
                    "reporting_fact_award",
                    "reporting_fact_project",
                    "reporting_financial_fact",
                }.issubset(views)
            )
            conn.close()

    def test_px_lineage_accepts_multiple_bids_without_changing_px(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "registry.sqlite"
            initialize_database(db)
            apply_commercial_graph_migration(db)
            conn = sqlite3.connect(db)
            conn.execute("PRAGMA foreign_keys=ON")
            now = "2026-10-22T00:00:00Z"
            rows = [
                ("opp", "ARGUS-OPP-2026-000001", "OPPORTUNITY", "Opportunity"),
                ("bid1", "BID-BD-000001", "BID", "Bid 1"),
                ("bid2", "BID-BD-000002", "BID", "Bid 2"),
            ]
            for internal_id, canonical_id, object_type, title in rows:
                conn.execute(
                    "INSERT INTO canonical_object(internal_id,canonical_id,object_type,jurisdiction,title,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",
                    (internal_id, canonical_id, object_type, "BD", title, "CURRENT", now, now),
                )
            conn.execute(
                "INSERT INTO commercial_lineage(commercial_px_id,opportunity_internal_id,assigned_at,assigned_by,status) VALUES (?,?,?,?,?)",
                ("2026_PX00012_BCG-CPV", "opp", now, "ATLAS", "ACTIVE"),
            )
            conn.execute(
                "INSERT INTO commercial_lineage_member(member_id,commercial_px_id,object_internal_id,member_type,sequence_no,created_at) VALUES (?,?,?,?,?,?)",
                ("m1", "2026_PX00012_BCG-CPV", "opp", "OPPORTUNITY", 1, now),
            )
            conn.execute(
                "INSERT INTO commercial_lineage_member(member_id,commercial_px_id,object_internal_id,member_type,sequence_no,created_at) VALUES (?,?,?,?,?,?)",
                ("m2", "2026_PX00012_BCG-CPV", "bid1", "BID", 1, now),
            )
            conn.execute(
                "INSERT INTO commercial_lineage_member(member_id,commercial_px_id,object_internal_id,member_type,sequence_no,created_at) VALUES (?,?,?,?,?,?)",
                ("m3", "2026_PX00012_BCG-CPV", "bid2", "BID", 2, now),
            )
            self.assertEqual(
                2,
                conn.execute(
                    "SELECT COUNT(*) FROM commercial_lineage_member WHERE commercial_px_id=? AND member_type='BID'",
                    ("2026_PX00012_BCG-CPV",),
                ).fetchone()[0],
            )
            conn.close()

    def test_migration_is_idempotent_and_integrity_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "registry.sqlite"
            initialize_database(db)
            apply_commercial_graph_migration(db)
            apply_commercial_graph_migration(db)
            conn = sqlite3.connect(db)
            self.assertEqual("ok", conn.execute("PRAGMA integrity_check").fetchone()[0])
            self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            conn.close()


if __name__ == "__main__":
    unittest.main()
