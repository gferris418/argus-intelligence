from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CollectionArchitectureTests(unittest.TestCase):
    def test_activation_examples_encode_required_boundary(self) -> None:
        contract = json.loads((ROOT / "contracts/atlas/argus-activation-v1.json").read_text(encoding="utf-8"))
        examples = contract["representative_routing_examples"]
        self.assertEqual("DIRECT_SEARCH_OR_DEEP_RESEARCH", examples["Bangladesh Bank foreign exchange policy"])
        self.assertEqual("ARGUS", examples["ST Engineering"])
        self.assertEqual("ARGUS", examples["build a coastal patrol vessel opportunity footprint for Bangladesh Coast Guard"])
        self.assertEqual("ARGUS", examples["build a supplier landscape for seed cum cleaner opportunities for BADC"])
        self.assertEqual("DIRECT_SEARCH", examples["share the annual procurement plan of Bangladesh Navy"])
        self.assertEqual("MULTI_CAPABILITY", examples["compare ST Engineering and L3Harris for Bangladesh opportunities"])

    def test_argus_does_not_own_analysis_or_governance(self) -> None:
        contract = json.loads((ROOT / "contracts/atlas/argus-activation-v1.json").read_text(encoding="utf-8"))
        ownership = contract["ownership"]
        for field in ("mission_control", "control_plane", "planning", "approvals", "strategic_analysis", "forecasting_and_scenarios", "opportunity_qualification", "assurance_and_verification", "observability", "dashboard_projection", "final_delivery"):
            self.assertEqual("ATLAS", ownership[field])
        self.assertEqual("ARGUS", ownership["source_discovery"])
        self.assertEqual("ARGUS", ownership["collection_packaging"])

    def test_generic_collection_contracts_exist(self) -> None:
        mission = json.loads((ROOT / "schemas/collection-mission.schema.json").read_text(encoding="utf-8"))
        package = json.loads((ROOT / "schemas/intelligence-collection-package.schema.json").read_text(encoding="utf-8"))
        self.assertIn("collection_depth", mission["properties"])
        self.assertIn("collection_status", package["properties"])
        self.assertNotIn("decision", package["required"])
        self.assertNotIn("maturity", package["required"])


if __name__ == "__main__":
    unittest.main()
