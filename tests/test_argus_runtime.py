from __future__ import annotations

import base64
import hashlib
import json
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.argus_runtime import (
    AnalysisEnvelope,
    AnalysisExecutionError,
    Argus,
    SyncValidationError,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "atlas-sync"


class ArgusRuntimeTests(unittest.TestCase):
    PRIVATE_KEY = bytes(range(1, 33))
    KEY_ID = "atlas-test-2026"

    def setUp(self) -> None:
        clock = patch(
            "tools.atlas_sync._utc_now",
            return_value=datetime(2026, 10, 18, 8, 0, tzinfo=timezone.utc),
        )
        clock.start()
        self.addCleanup(clock.stop)

    def _handoff(self) -> dict:
        return json.loads((FIXTURES / "ready-handoff.json").read_text(encoding="utf-8"))

    def _attestation(self, record: dict) -> dict[str, str]:
        payload = json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        signature = Ed25519PrivateKey.from_private_bytes(self.PRIVATE_KEY).sign(payload)
        return {
            "version": "1",
            "issuer": "ATLAS_OS",
            "algorithm": "Ed25519",
            "key_id": self.KEY_ID,
            "record_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "signature": base64.b64encode(signature).decode("ascii"),
        }

    def _trusted_public_keys(self) -> dict[str, bytes]:
        public_key = Ed25519PrivateKey.from_private_bytes(self.PRIVATE_KEY).public_key()
        return {
            self.KEY_ID: public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        }

    @staticmethod
    def _method(handoff: dict) -> dict:
        return {
            "objective": "Assess the governed opportunity.",
            "candidate_or_opportunity": {"name": "Coastal radar"},
            "decision": "INVESTIGATE",
            "maturity": "I1",
            "evidence": [],
            "unknowns_conflicts": list(handoff["unresolved_material"]),
            "next_recommended_action": "Continue governed collection.",
        }

    def test_analyze_owns_the_complete_governed_synchronization_path(self) -> None:
        handoff = self._handoff()
        original = deepcopy(handoff)
        runtime = Argus(self._method, trusted_public_keys=self._trusted_public_keys())

        outcome = runtime.analyze(AnalysisEnvelope(
            handoff=handoff,
            atlas_attestation=self._attestation(handoff),
            started_at="2026-10-18T07:00:00Z",
        ))

        self.assertEqual(original, handoff)
        self.assertEqual("ATLAS_GOVERNED", outcome.result["governance_mode"])
        self.assertEqual(outcome.receipt["sync_execution_id"], outcome.result["sync_execution_id"])
        self.assertEqual("RETURNED", outcome.receipt["state"])
        self.assertEqual("2.0.0-rc.3", outcome.receipt["argus"]["version"])
        self.assertEqual(outcome.result["result_sha256"], outcome.receipt["argus"]["result_sha256"])
        self.assertEqual(handoff["handoff_id"], outcome.result["upstream_handoff"]["handoff_id"])
        self.assertLessEqual(len(outcome.compact_status.splitlines()), 3)

    def test_analyze_rejects_domain_methods_that_spoof_governance_fields(self) -> None:
        handoff = self._handoff()

        def spoofing_method(_: dict) -> dict:
            payload = self._method(handoff)
            payload["governance_mode"] = "STANDALONE"
            return payload

        runtime = Argus(spoofing_method, trusted_public_keys=self._trusted_public_keys())

        with self.assertRaises(SyncValidationError) as caught:
            runtime.analyze(AnalysisEnvelope(
                handoff=handoff,
                atlas_attestation=self._attestation(handoff),
                started_at="2026-10-18T07:00:00Z",
            ))

        self.assertEqual("DOMAIN_RESULT_RESERVED_FIELD", caught.exception.code)

    def test_analyze_returns_retryable_failed_state_when_domain_method_crashes(self) -> None:
        handoff = self._handoff()

        def failing_method(_: dict) -> dict:
            raise RuntimeError("collector unavailable")

        runtime = Argus(failing_method, trusted_public_keys=self._trusted_public_keys())

        with self.assertRaises(AnalysisExecutionError) as caught:
            runtime.analyze(AnalysisEnvelope(
                handoff=handoff,
                atlas_attestation=self._attestation(handoff),
                started_at="2026-10-18T07:00:00Z",
            ))

        self.assertEqual("FAILED", caught.exception.receipt["state"])
        self.assertEqual("DEPENDENCY_FAILED", caught.exception.receipt["failure_state"])
        self.assertIsInstance(caught.exception.__cause__, RuntimeError)


if __name__ == "__main__":
    unittest.main()
