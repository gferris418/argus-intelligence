from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECONCILIATION = ROOT / "profiles" / "access-asia-canonical-reconciliation-v1.0.yaml"
COMMERCIAL_STANDARD = ROOT / "profiles" / "access-asia-commercial-data-standard-v1.0.yaml"
MANIFEST = ROOT / "argus-intelligence.yaml"


class CanonicalReconciliationFoundationTests(unittest.TestCase):
    def test_reconciliation_contract_is_active_and_schema_is_frozen(self) -> None:
        contract = yaml.safe_load(RECONCILIATION.read_text(encoding="utf-8"))

        self.assertEqual("ACTIVE", contract["status"])
        self.assertEqual("ARGUS", contract["owner"])
        self.assertTrue(contract["production_baseline"]["schema_frozen"])
        self.assertEqual("1.1.0", contract["production_baseline"]["sqlite_schema_version"])
        self.assertEqual(2, contract["production_baseline"]["sqlite_user_version"])
        self.assertEqual(
            "genuine_structural_defect_or_missing_real_world_concept",
            contract["production_baseline"]["schema_change_gate"],
        )

    def test_reconciliation_never_fabricates_history_or_lineage(self) -> None:
        contract = yaml.safe_load(RECONCILIATION.read_text(encoding="utf-8"))

        self.assertEqual(
            {"MATCHED", "PROVISIONAL", "NEEDS_REVIEW", "CONFLICT", "UNRESOLVED"},
            set(contract["reconciliation"]["statuses"]),
        )
        rules = contract["reconciliation"]["rules"]
        self.assertTrue(rules["material_facts_require_evidence"])
        self.assertTrue(rules["lineage_links_require_evidence"])
        self.assertTrue(rules["ambiguous_records_are_quarantined"])
        self.assertTrue(rules["automatic_historical_reclassification_prohibited"])
        self.assertTrue(rules["fabricated_px_bid_award_project_links_prohibited"])

    def test_population_dependency_order_is_explicit(self) -> None:
        contract = yaml.safe_load(RECONCILIATION.read_text(encoding="utf-8"))

        self.assertEqual(
            [
                "ORGANIZATION",
                "PRODUCT_AND_PRODUCT_CATEGORY",
                "SECTOR",
                "GEOGRAPHY",
                "PROGRAMME_AND_GOVERNMENT_PROJECT",
                "REQUIREMENT",
                "FINANCING",
                "PROCUREMENT_AND_TENDER",
                "OPPORTUNITY_AND_PX",
                "ORGANIZATION_ROLES",
                "BID",
                "AWARD",
                "ACCESS_ASIA_PROJECT",
                "FINANCIAL_FACT",
            ],
            contract["population"]["dependency_order"],
        )

    def test_every_population_batch_has_validation_and_rollback_controls(self) -> None:
        contract = yaml.safe_load(RECONCILIATION.read_text(encoding="utf-8"))

        required = set(contract["batch_control"]["required_record"])
        self.assertTrue(
            {
                "batch_id",
                "input_sources",
                "records_examined",
                "canonical_objects_created",
                "canonical_objects_updated",
                "relationships_created",
                "unresolved_records",
                "conflicts",
                "mutation_log_entries",
                "foreign_key_validation",
                "integrity_check",
                "before_sha256",
                "after_sha256",
                "rollback_reference",
            }.issubset(required)
        )
        self.assertEqual("PASS", contract["batch_control"]["promotion_gate"]["integrity_check"])
        self.assertEqual(0, contract["batch_control"]["promotion_gate"]["foreign_key_violations"])
        self.assertTrue(contract["batch_control"]["promotion_gate"]["rollback_required"])

    def test_reporting_is_derived_and_predictions_do_not_become_canonical_truth(self) -> None:
        contract = yaml.safe_load(RECONCILIATION.read_text(encoding="utf-8"))

        reporting = contract["reporting"]
        self.assertTrue(reporting["canonical_views_only"])
        self.assertFalse(reporting["department_specific_master_data_allowed"])
        self.assertEqual(
            {"MARKETING", "SALES", "BUSINESS_DEVELOPMENT", "OPERATIONS", "FINANCE", "MANAGEMENT"},
            set(reporting["department_surfaces"]),
        )
        analytics = contract["analytical_assertions"]
        self.assertTrue(analytics["kept_separate_from_canonical_facts"])
        self.assertTrue(analytics["provenance_required"])
        self.assertTrue(analytics["confidence_required"])
        self.assertTrue(analytics["timestamp_required"])

    def test_commercial_standard_records_activated_migration_and_new_next_step(self) -> None:
        standard = yaml.safe_load(COMMERCIAL_STANDARD.read_text(encoding="utf-8"))
        migration = standard["migration_policy"]

        self.assertTrue(migration["live_database_mutation_activated"])
        self.assertEqual("1.1.0", migration["sqlite_schema_version"])
        self.assertEqual(2, migration["sqlite_user_version"])
        self.assertEqual(
            "controlled_evidence_backed_reconciliation_and_reporting",
            migration["next_step"],
        )

    def test_manifest_registers_reconciliation_authority(self) -> None:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(
            "profiles/access-asia-canonical-reconciliation-v1.0.yaml",
            manifest["authority"]["access_asia_canonical_reconciliation"],
        )


if __name__ == "__main__":
    unittest.main()
