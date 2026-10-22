from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "argus-intelligence.yaml"
COLLECTION_METHOD = ROOT / "spec/collection-method.yaml"
LEARNING_SPEC = ROOT / "spec/continuous-learning.yaml"
LEARNING_SCHEMA = ROOT / "schemas/research-learning-record.schema.json"
ARCHITECTURE = ROOT / "docs/architecture/bangladesh-opportunity-intelligence-v3.md"


class ContinuousSearchLearningTests(unittest.TestCase):
    def test_learning_contract_is_registered_as_authority(self):
        text = MANIFEST.read_text(encoding="utf-8")
        self.assertIn("continuous_learning: spec/continuous-learning.yaml", text)
        self.assertIn("research_learning_record_schema: schemas/research-learning-record.schema.json", text)
        self.assertIn("continuous_search_learning:", text)
        self.assertIn("every_search_produces_learning_record: true", text)
        self.assertIn("no_result_searches_are_learning_events: true", text)

    def test_every_search_attempt_emits_learning_before_collection_moves_on(self):
        text = COLLECTION_METHOD.read_text(encoding="utf-8")
        self.assertIn("per_search_learning_record: required", text)
        self.assertIn("including_zero_result_searches: true", text)
        self.assertIn("SEARCH_LEARNING", text)

    def test_learning_spec_separates_memory_types_and_evidence(self):
        text = LEARNING_SPEC.read_text(encoding="utf-8")
        for memory_type in (
            "EPISODIC_MEMORY",
            "SEMANTIC_MEMORY",
            "STRATEGY_MEMORY",
            "CALIBRATION_MEMORY",
            "SOURCE_MEMORY",
            "VOCABULARY_MEMORY",
        ):
            self.assertIn(memory_type, text)
        self.assertIn("learned_patterns_are_not_current_facts: true", text)
        self.assertIn("learned_heuristics_may_guide_search_but_never_replace_current_evidence: true", text)
        self.assertIn("contradictions_are_preserved: true", text)
        self.assertIn("atlas_persistence_authority_is_unchanged: true", text)

    def test_heuristic_promotion_requires_repetition_and_backtest(self):
        text = LEARNING_SPEC.read_text(encoding="utf-8")
        self.assertIn("OBSERVED", text)
        self.assertIn("REPEATED_PATTERN", text)
        self.assertIn("VALIDATED_HEURISTIC", text)
        self.assertIn("backtest_required_for_validated_heuristic: true", text)
        self.assertIn("single_observation_cannot_become_validated_heuristic: true", text)
        self.assertIn("outcome_calibration_required: true", text)

    def test_learning_record_schema_captures_search_and_meta_learning(self):
        schema = json.loads(LEARNING_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        required = set(schema["required"])
        for field in (
            "search_id",
            "timestamp",
            "research_question",
            "query",
            "search_method",
            "source_family",
            "results_examined",
            "useful_result_count",
            "information_gain",
            "source_assessment",
            "discoveries",
            "unknowns",
            "hypothesis_change",
            "learning",
            "recommended_next_search",
        ):
            self.assertIn(field, required)

        properties = schema["properties"]
        self.assertIn("what_worked", properties["learning"]["properties"])
        self.assertIn("what_failed", properties["learning"]["properties"])
        self.assertIn("lesson_learned", properties["learning"]["properties"])
        self.assertIn("successful_terms", properties["learning"]["properties"])
        self.assertIn("unsuccessful_terms", properties["learning"]["properties"])

    def test_architecture_states_unknown_means_research_not_stop(self):
        text = ARCHITECTURE.read_text(encoding="utf-8")
        self.assertIn("UNKNOWN means a research task, not a stop condition", text)
        self.assertIn("Every search must leave ARGUS better informed", text)
        self.assertIn("Patterns guide investigation; evidence determines conclusions", text)


if __name__ == "__main__":
    unittest.main()
