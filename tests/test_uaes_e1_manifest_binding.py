from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class UaesE13ManifestBindingTests(unittest.TestCase):
    def test_argus_manifest_declares_e1_3_contracts_as_authority(self) -> None:
        manifest = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text(encoding="utf-8"))
        authority = manifest["authority"]
        self.assertEqual(
            "profiles/access-asia-operational-state-machines-v1.0.yaml",
            authority["access_asia_operational_state_machines"],
        )
        self.assertEqual(
            "profiles/access-asia-security-boundary-v1.0.yaml",
            authority["access_asia_security_boundary"],
        )
        self.assertEqual(
            "profiles/access-asia-threat-register-v1.0.yaml",
            authority["access_asia_threat_register"],
        )
        self.assertEqual(
            "profiles/access-asia-containment-plan-v1.0.yaml",
            authority["access_asia_containment_plan"],
        )


if __name__ == "__main__":
    unittest.main()
