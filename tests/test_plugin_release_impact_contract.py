import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
IMPACT = ROOT / "contracts" / "atlas" / "plugin-release-impact.yaml"
CURRENT = ROOT / "contracts" / "atlas" / "current-integration.yaml"


class PluginReleaseImpactContractTests(unittest.TestCase):
    def test_argus_exposes_machine_readable_plugin_release_impact(self) -> None:
        self.assertTrue(IMPACT.is_file(), "missing ARGUS plugin release impact contract")
        impact = yaml.safe_load(IMPACT.read_text(encoding="utf-8"))
        self.assertEqual("1.0.0", impact["version"])
        self.assertEqual("CURRENT", impact["status"])
        self.assertEqual("atlas-os", impact["chatgpt_plugin"]["name"])
        self.assertEqual("ATLAS", impact["chatgpt_plugin"]["release_owner"])
        self.assertFalse(impact["default"]["plugin_release_required"])
        self.assertTrue(impact["boundary_changes"]["plugin_review_required"])
        self.assertIn("activation_contract", impact["boundary_changes"]["categories"])
        self.assertIn("provider_return_contract", impact["boundary_changes"]["categories"])
        self.assertIn("approval_contract", impact["boundary_changes"]["categories"])
        self.assertIn("route_mechanisms", impact["boundary_changes"]["categories"])
        self.assertIn("source_collectors", impact["internal_changes"]["categories"])
        self.assertFalse(impact["internal_changes"]["plugin_release_required"])

    def test_current_atlas_integration_references_release_impact_contract(self) -> None:
        current = yaml.safe_load(CURRENT.read_text(encoding="utf-8"))
        self.assertEqual(
            "contracts/atlas/plugin-release-impact.yaml",
            current["contract"]["plugin_release_impact"],
        )


if __name__ == "__main__":
    unittest.main()
