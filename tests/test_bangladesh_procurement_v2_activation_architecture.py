import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "validation" / "bangladesh-procurement-v2-historical-migration-rehearsal.md"
MANIFEST = (ROOT / "argus-intelligence.yaml").read_text()


class BangladeshProcurementV2ActivationArchitecture(unittest.TestCase):
    def test_report_blocks_activation_until_registry_envelope_is_defined(self):
        self.assertTrue(REPORT.exists())
        text = REPORT.read_text()
        for token in (
            "Registry envelope/materialization contract: BLOCKER",
            "Do not mix direct v2 payloads with registry-envelope records",
            "Next gate: registry envelope/materialization contract",
            "GO to envelope-design gate",
            "NO-GO for live activation",
        ):
            self.assertIn(token, text)

    def test_manifest_still_points_to_v1_3(self):
        self.assertIn(
            "bangladesh_procurement_standard: profiles/bangladesh-canonical-procurement-standard-v1.3.yaml",
            MANIFEST,
        )


if __name__ == "__main__":
    unittest.main()
