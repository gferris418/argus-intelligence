from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from tools.atlas_sync import (
    SyncValidationError,
    canonical_handoff_sha256,
    mark_upstream_context_change,
    new_sync_receipt,
    transition_sync,
    validate_handoff,
    validate_sync_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "atlas-sync"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AtlasArgusSynchronizationTests(unittest.TestCase):
    def test_ready_handoff_starts_correlated_receipt(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        validate_handoff(handoff)
        receipt = new_sync_receipt(
            "ARGUS-SYNC-READY-001", handoff, "2026-10-18T07:00:00Z"
        )
        self.assertEqual("RECEIVED", receipt["state"])
        self.assertEqual(handoff["handoff_id"], receipt["atlas"]["handoff_id"])
        self.assertEqual(handoff["source_task_id"], receipt["atlas"]["source_task_id"])
        self.assertEqual(1, receipt["attempt"])

    def test_tampered_handoff_digest_is_rejected(self) -> None:
        handoff = load_fixture("ready-handoff.json")
        handoff["domain_alignment"]["domains"] = ["changed-domain"]
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(handoff)
        self.assertEqual("HANDOFF_DIGEST_MISMATCH", caught.exception.code)
        self.assertEqual("VALIDATION_FAILED", caught.exception.atlas_failure_state)

    def test_wrong_consumer_and_unsupported_version_are_rejected(self) -> None:
        for field, value, code in (
            ("consumer", "OTHER", "HANDOFF_CONSUMER_MISMATCH"),
            ("contract_version", "9.9.9", "HANDOFF_SCHEMA_INVALID"),
        ):
            handoff = load_fixture("ready-handoff.json")
            handoff[field] = value
            handoff["payload_sha256"] = canonical_handoff_sha256(handoff)
            with self.subTest(field=field), self.assertRaises(SyncValidationError) as caught:
                validate_handoff(handoff)
            self.assertEqual(code, caught.exception.code)

    def test_blocked_handoff_cannot_start(self) -> None:
        with self.assertRaises(SyncValidationError) as caught:
            validate_handoff(load_fixture("blocked-handoff.json"))
        self.assertEqual("HANDOFF_BLOCKED", caught.exception.code)
        self.assertEqual("BLOCKED", caught.exception.atlas_failure_state)

    def test_partial_handoff_preserves_unresolved_and_risk_snapshots(self) -> None:
        handoff = load_fixture("partial-handoff.json")
        receipt = new_sync_receipt(
            "ARGUS-SYNC-PARTIAL-001", handoff, "2026-10-18T07:00:00Z"
        )
        self.assertEqual(handoff["unresolved_material"], receipt["unresolved_material"])
        self.assertEqual(handoff["risk_flags"], receipt["risk_flags"])
        self.assertEqual("PARTIAL", receipt["failure_state"])
        validate_sync_receipt(receipt)

    def test_lifecycle_allows_only_explicit_transitions(self) -> None:
        receipt = new_sync_receipt(
            "ARGUS-SYNC-LIFECYCLE-001",
            load_fixture("ready-handoff.json"),
            "2026-10-18T07:00:00Z",
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE", "RESULT_READY", "RETURNED"):
            receipt = transition_sync(receipt, state)
            self.assertEqual(state, receipt["state"])
            validate_sync_receipt(receipt)
        self.assertIsNotNone(receipt["completed_at"])

        with self.assertRaises(SyncValidationError) as caught:
            transition_sync(receipt, "ACTIVE")
        self.assertEqual("ILLEGAL_SYNC_TRANSITION", caught.exception.code)

    def test_material_context_change_supersedes_dependent_work(self) -> None:
        receipt = new_sync_receipt(
            "ARGUS-SYNC-CONTEXT-001",
            load_fixture("ready-handoff.json"),
            "2026-10-18T07:00:00Z",
        )
        for state in ("VALIDATED", "ACCEPTED", "ACTIVE"):
            receipt = transition_sync(receipt, state)
        changed = mark_upstream_context_change(
            receipt,
            ["jurisdiction"],
            ["EVIDENCE-001"],
            "New primary-source evidence changes jurisdiction.",
        )
        self.assertEqual("SUPERSEDED_PENDING_ATLAS", changed["state"])
        self.assertTrue(changed["context_change_detected"])
        self.assertTrue(changed["upstream_refresh_required"])
        self.assertEqual(["jurisdiction"], changed["upstream_context_change"]["affected_facets"])
        validate_sync_receipt(changed)


if __name__ == "__main__":
    unittest.main()
