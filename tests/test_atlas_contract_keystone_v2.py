from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ATLAS_CANONICAL_COMMIT = "2972f272026d2cf41e5dd847eb939d3579d8520a"
ATLAS_CANONICAL_PATH = "contracts/atlas-argus-execution-v2.json"


class AtlasContractKeystoneV2Tests(unittest.TestCase):
    def test_argus_descriptor_is_a_derived_snapshot_of_atlas_canonical_contract(self) -> None:
        descriptor = yaml.safe_load(
            (ROOT / "contracts" / "atlas" / "current-integration.yaml").read_text(encoding="utf-8")
        )
        canonical = descriptor["canonical_source"]
        self.assertEqual("ATLAS", canonical["authority"])
        self.assertEqual("gferris418/atlas-os", canonical["repository"])
        self.assertEqual(ATLAS_CANONICAL_COMMIT, canonical["commit"])
        self.assertEqual(ATLAS_CANONICAL_PATH, canonical["path"])
        self.assertEqual("2.0.0", canonical["contract_version"])
        self.assertEqual("derived_snapshot", descriptor["contract_role"])

    def test_provider_contract_constants_are_loaded_from_descriptor(self) -> None:
        contract_module = importlib.import_module("tools.atlas_contract")
        provider_module = importlib.import_module("tools.atlas_v3_provider")
        contract = contract_module.ATLAS_EXECUTION_CONTRACT
        self.assertEqual(tuple(contract["pre_execution_flow"]), provider_module.PRE_EXECUTION_FLOW)
        self.assertEqual(
            ("intelligence_collection", "argus"),
            provider_module.ROUTE_CONTRACTS["ARGUS"],
        )
        self.assertEqual(
            ("intelligence_collection+analysis", "argus+atlas"),
            provider_module.ROUTE_CONTRACTS["MULTI_CAPABILITY"],
        )


if __name__ == "__main__":
    unittest.main()
