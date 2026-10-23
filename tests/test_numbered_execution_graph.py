from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "contracts/atlas/argus-360-bi-execution-graph-v1.yaml"
COLLECTION_PATH = ROOT / "spec/collection-method.yaml"


class NumberedExecutionGraphTests(unittest.TestCase):
    def test_graph_preserves_normative_startup_and_collection_order(self) -> None:
        graph = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
        collection = yaml.safe_load(COLLECTION_PATH.read_text(encoding="utf-8"))

        nodes = graph["nodes"]
        by_id = {node["stable_id"]: node for node in nodes}

        startup_children = [
            node for node in nodes if node.get("parent_id") == "ARGUS-STARTUP"
        ]
        startup_children.sort(key=lambda node: node["serial"])
        self.assertEqual(
            collection["execution"]["startup_sequence"],
            [node["stage"] for node in startup_children],
        )

        method_children = [
            node for node in nodes if node.get("parent_id") == "ARGUS-COLLECTION-METHOD"
        ]
        method_children.sort(key=lambda node: node["serial"])
        self.assertEqual(
            collection["method"]["stages"],
            [node["stage"] for node in method_children],
        )
        self.assertEqual("ATLAS_OS", by_id["ARGUS-RETURN-TO-ATLAS"]["owner"])

    def test_every_node_has_unique_stable_id_and_unique_hierarchical_serial(self) -> None:
        graph = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
        nodes = graph["nodes"]
        stable_ids = [node["stable_id"] for node in nodes]
        serials = [node["serial"] for node in nodes]

        self.assertEqual(len(stable_ids), len(set(stable_ids)))
        self.assertEqual(len(serials), len(set(serials)))
        for node in nodes:
            self.assertRegex(node["serial"], r"^\d{2}(?:\.\d{2})*$")
            parent_id = node.get("parent_id")
            if parent_id is not None:
                parent = next(item for item in nodes if item["stable_id"] == parent_id)
                self.assertTrue(node["serial"].startswith(parent["serial"] + "."))

    def test_sibling_serials_are_contiguous_and_dependencies_are_declared_nodes(self) -> None:
        graph = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
        nodes = graph["nodes"]
        stable_ids = {node["stable_id"] for node in nodes}
        groups: dict[str | None, list[int]] = {}

        for node in nodes:
            parent_id = node.get("parent_id")
            groups.setdefault(parent_id, []).append(int(node["serial"].split(".")[-1]))
            for dependency in node.get("dependencies", []):
                self.assertIn(dependency, stable_ids)

        for positions in groups.values():
            self.assertEqual(list(range(1, len(positions) + 1)), sorted(positions))

    def test_every_node_declares_governance_metadata(self) -> None:
        graph = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
        allowed_criticality = {"CRITICAL", "MAJOR", "MINOR", "INFORMATIONAL"}
        allowed_statuses = {
            "PENDING",
            "ACTIVE",
            "COMPLETE",
            "BLOCKED",
            "FAILED",
            "NOT_APPLICABLE",
            "SKIPPED_WITH_AUTHORITY",
            "SUPERSEDED",
        }

        for node in graph["nodes"]:
            self.assertTrue(node.get("owner"), node["stable_id"])
            self.assertIn(node.get("criticality"), allowed_criticality, node["stable_id"])
            statuses = node.get("allowed_statuses")
            self.assertIsInstance(statuses, list, node["stable_id"])
            self.assertIn("PENDING", statuses, node["stable_id"])
            self.assertTrue(set(statuses).issubset(allowed_statuses), node["stable_id"])
            if node["kind"] == "REQUIRED":
                self.assertNotIn("NOT_APPLICABLE", statuses, node["stable_id"])

    def test_research_nodes_declare_evidence_or_output_contracts(self) -> None:
        graph = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
        by_id = {node["stable_id"]: node for node in graph["nodes"]}

        for stable_id in (
            "ARGUS-COLLECTION-COLLECT",
            "ARGUS-COLLECTION-RESOLVE",
            "ARGUS-COLLECTION-GRADE",
            "ARGUS-COLLECTION-COMPETING-HYPOTHESES",
            "ARGUS-COLLECTION-GAPS",
            "ARGUS-COLLECTION-PACKAGE",
        ):
            node = by_id[stable_id]
            self.assertTrue(
                node.get("evidence_requirement") or node.get("output_schema_ref"),
                stable_id,
            )

    def test_graph_targets_current_atlas_aceg_contract(self) -> None:
        graph = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
        self.assertEqual("atlas.canonical-execution-graph/1.1.0", graph["atlas_contract"])

    def test_runtime_cannot_invent_canonical_nodes(self) -> None:
        graph = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PROHIBITED", graph["runtime_policy"]["invent_canonical_nodes"])
        self.assertEqual("ATLAS_GOVERNED_VERSION_CHANGE", graph["runtime_policy"]["extension_route"])


if __name__ == "__main__":
    unittest.main()
