"""Load the ATLAS-owned execution contract snapshot used by ARGUS.

ATLAS remains the canonical authority. This module reads ARGUS's derived integration
snapshot so provider code does not duplicate contract literals.
"""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml


_ROOT = Path(__file__).resolve().parents[1]
_DESCRIPTOR_PATH = _ROOT / "contracts" / "atlas" / "current-integration.yaml"


def _load_descriptor(path: Path = _DESCRIPTOR_PATH) -> dict[str, Any]:
    descriptor = yaml.safe_load(path.read_text(encoding="utf-8"))
    if descriptor.get("status") != "CURRENT":
        raise ValueError("ATLAS integration descriptor must be CURRENT")
    if descriptor.get("contract_role") != "derived_snapshot":
        raise ValueError("ARGUS ATLAS contract must be marked derived_snapshot")
    source = descriptor.get("canonical_source", {})
    if source.get("authority") != "ATLAS":
        raise ValueError("ATLAS must remain canonical execution-contract authority")
    if source.get("repository") != "gferris418/atlas-os":
        raise ValueError("unexpected canonical ATLAS repository")
    commit = source.get("commit")
    if not isinstance(commit, str) or len(commit) != 40:
        raise ValueError("canonical ATLAS contract must pin an immutable commit")
    contract = descriptor.get("contract")
    if not isinstance(contract, dict):
        raise ValueError("ATLAS contract snapshot is required")
    if contract.get("pre_execution_flow") != [
        "UNDERSTAND_AND_NORMALIZE",
        "MINIMAL_DOMAIN_FRAMING",
        "ROUTE",
    ]:
        raise ValueError("ATLAS pre-execution flow invariant mismatch")
    if contract.get("approval_key") != "ARGUS_ACTIVATION":
        raise ValueError("ATLAS ARGUS activation approval invariant mismatch")
    if contract.get("activation_authority") != "ATLAS":
        raise ValueError("ATLAS must retain activation authority")
    if contract.get("next_step_authority") != "ATLAS":
        raise ValueError("ATLAS must retain next-step authority")
    if contract.get("provider_return_target") != "ATLAS":
        raise ValueError("ARGUS results must return to ATLAS")
    return descriptor


ATLAS_INTEGRATION_DESCRIPTOR = _load_descriptor()
ATLAS_EXECUTION_CONTRACT = MappingProxyType(dict(ATLAS_INTEGRATION_DESCRIPTOR["contract"]))


def route_contracts() -> MappingProxyType[str, tuple[str, str]]:
    mechanisms = ATLAS_EXECUTION_CONTRACT.get("route_mechanisms")
    if not isinstance(mechanisms, dict):
        raise ValueError("ATLAS route mechanisms are required")
    return MappingProxyType(
        {
            mechanism: (str(details["capability"]), str(details["provider"]))
            for mechanism, details in mechanisms.items()
        }
    )


ROUTE_CONTRACTS = route_contracts()


__all__ = [
    "ATLAS_EXECUTION_CONTRACT",
    "ATLAS_INTEGRATION_DESCRIPTOR",
    "ROUTE_CONTRACTS",
    "route_contracts",
]
