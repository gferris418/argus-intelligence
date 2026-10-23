from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "benchmarks" / "postgres" / "role-hardening-2026-10-23.yaml"
MANIFEST = ROOT / "argus-intelligence.yaml"


class PostgresRoleHardeningReceiptTests(unittest.TestCase):
    def test_receipt_closes_only_the_orphan_role_blocker(self) -> None:
        self.assertTrue(RECEIPT.is_file(), "missing immutable PostgreSQL role-hardening receipt")
        receipt = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(
            "benchmarks/postgres/role-hardening-2026-10-23.yaml",
            manifest["authority"]["postgres_role_hardening_receipt"],
        )
        self.assertEqual("PASS", receipt["least_privilege_role_gate"]["status"])
        self.assertEqual(
            ["argus_ingest", "argus_search"],
            receipt["least_privilege_role_gate"]["deleted_roles"],
        )
        self.assertEqual(
            ["argus_reader", "argus_runtime", "argus_writer"],
            sorted(receipt["least_privilege_role_gate"]["verified_bounded_roles"]),
        )
        self.assertFalse(receipt["production_gate"]["production_cutover_approved"])
        self.assertEqual("BLOCKED", receipt["production_gate"]["overall"])
        self.assertNotIn(
            "overprivileged_orphan_role_retirement",
            receipt["production_gate"]["open_blockers"],
        )


if __name__ == "__main__":
    unittest.main()
