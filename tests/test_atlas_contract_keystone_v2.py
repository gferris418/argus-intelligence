from __future__ import annotations

import base64
import hashlib
import hmac
import json
import unittest
from pathlib import Path

import yaml

from tools.atlas_v3_provider import ArgusProvider, ProviderEnvelope


ROOT = Path(__file__).resolve().parents[1]
ATLAS_COMMIT = "27e57c3a80c0910e7fb2fca320d8fad22f4031af"
ATLAS_CONTRACT_SHA256 = "f90fb8cc9a5456ccf700c9af237c5bb02fe25e4960fb675fb1566bbdce9efdf6"
SECRET = b"0123456789abcdef0123456789abcdef"


def _atlas_result() -> dict:
    return {
        "task_id": "ATLAS-REMOTE-001",
        "state": "READY",
        "normalized_objective": "Build a supplier landscape",
        "domain_framing": {},
        "pre_execution_flow": ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
        "route": {
            "mechanism": "ARGUS",
            "capability": "intelligence_collection",
            "provider": "argus",
            "approval_required": True,
            "approval_status": "APPROVED",
        },
        "next_step_authority": "ATLAS",
        "provider_return_target": "ATLAS",
    }


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _remote_token(*, now: int, nonce: str = "remote-nonce") -> str:
    header = {"alg": "HMAC-SHA256", "kid": "test-key", "typ": "ATLAS-CAP"}
    claims = {
        "v": 2,
        "iss": "ATLAS",
        "sub": "argus",
        "aud": "ARGUS",
        "capability": "intelligence_collection",
        "scope": "intelligence_collection:execute",
        "task_id": "ATLAS-REMOTE-001",
        "intent_hash": hashlib.sha256(b"Build a supplier landscape").hexdigest(),
        "iat": now,
        "exp": now + 120,
        "jti": nonce,
    }
    encoded_header = _b64url(json.dumps(header, sort_keys=True, separators=(",", ":")).encode())
    encoded_claims = _b64url(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode())
    signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
    signature = _b64url(hmac.new(SECRET, signing_input, hashlib.sha256).digest())
    return f"{encoded_header}.{encoded_claims}.{signature}"


class AtlasContractKeystoneV2Tests(unittest.TestCase):
    def test_current_integration_is_projection_of_immutable_atlas_contract(self) -> None:
        descriptor = yaml.safe_load(
            (ROOT / "contracts" / "atlas" / "current-integration.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual("2.0.0", descriptor["version"])
        self.assertEqual(ATLAS_COMMIT, descriptor["atlas"]["commit"])
        canonical = descriptor["atlas"]["canonical_execution_contract"]
        self.assertEqual("contracts/atlas-argus-execution-v2.json", canonical["path"])
        self.assertEqual("2.0.0", canonical["version"])
        self.assertEqual(ATLAS_CONTRACT_SHA256, canonical["sha256"])
        remote = descriptor["contract"]["remote_capability"]
        self.assertEqual(2, remote["version"])
        self.assertEqual("argus", remote["subject"])
        self.assertEqual("intelligence_collection", remote["capability"])
        self.assertTrue(remote["one_time"])

    def test_remote_provider_requires_and_consumes_capability_v2(self) -> None:
        provider = ArgusProvider(
            lambda _context: {"evidence": [], "collection_status": "COMPLETE"},
            remote_secret_resolver=lambda key_id: SECRET if key_id == "test-key" else None,
        )
        token = _remote_token(now=1_800_000_000)
        outcome = provider.execute(
            ProviderEnvelope(
                atlas_result=_atlas_result(),
                transport="remote",
                remote_capability=token,
                remote_now=1_800_000_030,
            )
        )
        self.assertEqual("ATLAS-REMOTE-001", outcome.result["source_task_id"])
        with self.assertRaises(ValueError):
            provider.execute(
                ProviderEnvelope(
                    atlas_result=_atlas_result(),
                    transport="remote",
                    remote_capability=token,
                    remote_now=1_800_000_031,
                )
            )

    def test_local_provider_remains_backward_compatible(self) -> None:
        provider = ArgusProvider(lambda _context: {"evidence": [], "collection_status": "COMPLETE"})
        outcome = provider.execute(ProviderEnvelope(atlas_result=_atlas_result()))
        self.assertEqual("ATLAS-REMOTE-001", outcome.result["source_task_id"])


if __name__ == "__main__":
    unittest.main()
