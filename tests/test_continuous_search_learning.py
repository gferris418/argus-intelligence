from pathlib import Path
import json
import unittest

from tools.research_learning import heuristic_state, validate_learning_record

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "argus-intelligence.yaml"
COLLECTION_METHOD = ROOT / "spec/collection-method.yaml"
LEARNING_SPEC = ROOT / "spec/continuous-learning.yaml"
LEARNING_SCHEMA = ROOT / "schemas/research-learning-record.schema.json"
ARCHITECTURE = ROOT / "docs/architecture/bangladesh-opportunity-intelligence-v3.md"


def zero_result_record():
    return {
        "search_id": "SE-000001",
        "timestamp": "2026-10-22T08:30:00Z",
        "opportunity_ref": "ARGUS-OPP-2026-000001",
        "requirement_ref": "REQ-BD-000001",
        "research_question": "Is there an upstream project signal?",
        "query": "site:example.gov.bd patrol vessel",
        "query_language": "en",
        "query_variants": [],
        "search_method": "WEB_SEARCH",
        "source_family": "GOVERNMENT_WEB",
        "domain": "example.gov.bd",
        "results_examined": 0,
        "documents_examined": 0,
        "useful_result_count": 0,
        "information_gain": {
            "level": "LOW",
            "factual_gain": "",
            "strategic_gain": "Exact equipment wording was not productive.",
            "negative_result_learning": "Try capability and project terminology next.",
        },
        "source_assessment": {
            "authority": "HIGH",
            "freshness": "UNKNOWN",
            "relevance": "MEDIUM",
            "access_status": "SEARCHABLE",
            "notes": "No matching result found.",
        },
        "discoveries": {
            "new_entities": [],
            "new_relationships": [],
            "new_events": [],
            "new_facts": [],
            "new_claims": [],
            "contradictions": [],
        },
        "unknowns": {
            "resolved": [],
            "created": ["Which terminology does the agency use?"],
            "remaining": ["Whether an upstream project exists."],
        },
        "hypothesis_change": {
            "before": "A project may exist under the equipment term.",
            "after": "A project may exist under different terminology.",
            "confidence_before": 0.4,
            "confidence_after": 0.4,
            "decision_impact": "Change the next query, not the opportunity stage.",
        },
        "learning": {
            "what_worked": [],
            "what_failed": ["Exact equipment wording"],
            "lesson_learned": ["Search capability and project terminology."],
            "successful_terms": [],
            "unsuccessful_terms": ["patrol vessel"],
            "synonyms_discovered": [],
            "acronyms_discovered": [],
            "source_lessons": [],
            "strategy_lessons": ["Broaden terminology before changing source family."],
        },
        "recommended_next_search": {
            "question": "Does the agency describe this as capability enhancement?",
            "strategy": "Search capability terms plus project/budget language.",
            "source_family": "GOVERNMENT_WEB",
            "priority": "HIGH",
            "stopping_condition": "Find an authoritative project signal or exhaust material terminology variants.",
        },
    }


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

        self.assertEqual(heuristic_state(observation_count=1, backtested=False), "OBSERVED")
        self.assertEqual(heuristic_state(observation_count=2, backtested=False), "REPEATED_PATTERN")
        self.assertEqual(heuristic_state(observation_count=8, backtested=False), "REPEATED_PATTERN")
        self.assertEqual(heuristic_state(observation_count=2, backtested=True), "VALIDATED_HEURISTIC")
        with self.assertRaises(ValueError):
            heuristic_state(observation_count=1, backtested=True)

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

    def test_zero_result_search_is_a_valid_learning_event(self):
        validated = validate_learning_record(zero_result_record())
        self.assertEqual(validated["results_examined"], 0)
        self.assertEqual(validated["useful_result_count"], 0)
        self.assertEqual(validated["information_gain"]["level"], "LOW")
        self.assertTrue(validated["recommended_next_search"]["strategy"])

    def test_useful_results_cannot_exceed_results_examined(self):
        record = zero_result_record()
        record["useful_result_count"] = 1
        with self.assertRaises(ValueError):
            validate_learning_record(record)

    def test_architecture_states_unknown_means_research_not_stop(self):
        text = ARCHITECTURE.read_text(encoding="utf-8")
        self.assertIn("UNKNOWN means a research task, not a stop condition", text)
        self.assertIn("Every search must leave ARGUS better informed", text)
        self.assertIn("Patterns guide investigation; evidence determines conclusions", text)


if __name__ == "__main__":
    unittest.main()
