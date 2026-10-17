import json
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = yaml.safe_load((ROOT / "argus-intelligence.yaml").read_text())
CORE = (ROOT / "spec" / "core.md").read_text()
ALIGNMENT = (ROOT / "alignments" / "atlas-os.md").read_text()
RESULT_SCHEMA = json.loads((ROOT / "schemas" / "domain-result.schema.json").read_text())
HANDOFF_SCHEMA_PATH = ROOT / "contracts" / "atlas" / "domain-context-handoff-v1.schema.json"


class AtlasDomainHandoffContract(unittest.TestCase):
    def test_argus_pins_the_atlas_handoff_contract(self):
        schema = json.loads(HANDOFF_SCHEMA_PATH.read_text())
        compat = MANIFEST["atlas_compatibility"]
        self.assertEqual("1.0.0", compat["atlas_domain_context_contract_version"])
        self.assertEqual("contracts/atlas/domain-context-handoff-v1.schema.json", compat["atlas_domain_context_contract_path"])
        self.assertEqual("1.0.0", schema["properties"]["contract_version"]["const"])

    def test_contextualize_is_first_argus_domain_operation(self):
        self.assertIn("Contextualize → Discover → Extract → Resolve → Reconcile", CORE)
        self.assertIn("ATLAS Domain Context", CORE)
        self.assertIn("must not redefine ATLAS taxonomy or standards conclusions", CORE)

    def test_alignment_requires_validated_handoff_before_argus_execution(self):
        self.assertIn("ATLAS Domain Context → ARGUS Contextualize", ALIGNMENT)
        self.assertIn("schema-valid domain-context handoff", ALIGNMENT)
        self.assertIn("handoff_id", ALIGNMENT)
        self.assertIn("payload_sha256", ALIGNMENT)
        self.assertIn("reject mismatched", ALIGNMENT.lower())

    def test_domain_result_requires_correlation_in_atlas_governed_mode(self):
        governed = {
            "governance_mode": "ATLAS_GOVERNED",
            "upstream_handoff": {
                "contract_version": "1.0.0",
                "handoff_id": "HANDOFF-ARGUS-001",
                "payload_sha256": "sha256:" + "a" * 64,
                "consumer": "ARGUS",
                "status": "ACCEPTED",
                "received_at": "2026-10-18T03:00:01+06:00"
            },
            "objective": "Assess a public-sector opportunity",
            "candidate_or_opportunity": {"name": "Example"},
            "decision": "INVESTIGATE",
            "maturity": "I1",
            "evidence": [],
            "unknowns_conflicts": [],
            "next_recommended_action": "Continue governed research"
        }
        jsonschema.validate(governed, RESULT_SCHEMA, format_checker=jsonschema.FormatChecker())
        broken = dict(governed)
        broken.pop("upstream_handoff")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(broken, RESULT_SCHEMA, format_checker=jsonschema.FormatChecker())

    def test_standalone_result_does_not_require_atlas_handoff(self):
        standalone = {
            "governance_mode": "STANDALONE",
            "objective": "Portable test",
            "candidate_or_opportunity": {"name": "Example"},
            "decision": "INVESTIGATE",
            "maturity": "I1",
            "evidence": [],
            "unknowns_conflicts": [],
            "next_recommended_action": "Continue analysis"
        }
        jsonschema.validate(standalone, RESULT_SCHEMA, format_checker=jsonschema.FormatChecker())


if __name__ == "__main__":
    unittest.main()
