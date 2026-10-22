from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RELATIONSHIPS = ROOT / "profiles/bangladesh-government-relationships.yaml"
INSTITUTIONS = ROOT / "profiles/bangladesh-institution-standard.yaml"


class BangladeshGovernmentGraphTests(unittest.TestCase):
    def test_relationship_classes_are_explicit(self):
        text = RELATIONSHIPS.read_text(encoding="utf-8")
        for relationship in (
            "PARENT_OF", "CHILD_OF", "SUPERVISES", "REPORTS_TO", "ADMINISTERS", "OPERATES_THROUGH",
            "SPONSORS", "OWNS_REQUIREMENT", "IMPLEMENTS", "PROCURES_FOR", "USES", "FUNDS", "APPROVES",
            "EVALUATES", "MONITORS", "REGULATES", "COORDINATES_WITH", "JOINTLY_REVIEWS",
            "JOINTLY_IMPLEMENTS", "ADVISES", "PROVIDES_OVERSIGHT_TO",
        ):
            self.assertIn(f"  {relationship}:", text)

    def test_project_procurement_roles_are_not_collapsed(self):
        text = RELATIONSHIPS.read_text(encoding="utf-8")
        for role in (
            "NEED_OWNER", "SPONSOR", "PROJECT_OWNER", "IMPLEMENTING_AGENCY", "PROJECT_OFFICE",
            "END_USER", "PROCURING_ENTITY", "APPROVING_AUTHORITY", "FUNDER",
            "MONITORING_AUTHORITY", "REGULATOR",
        ):
            self.assertIn(f"  - {role}", text)

    def test_approves_requires_evidence_and_scope(self):
        text = RELATIONSHIPS.read_text(encoding="utf-8")
        self.assertIn("inferred_from_hierarchy_only: false", text)
        self.assertIn("authoritative_source_required: true", text)
        self.assertIn("scope_required: true", text)

    def test_authority_path_preserves_unknowns(self):
        text = RELATIONSHIPS.read_text(encoding="utf-8")
        for field in (
            "need_owner", "sponsor", "project_owner", "implementing_agency", "funding_authority",
            "approving_authority", "procuring_entity", "evaluation_authority", "end_user",
            "monitoring_authority",
        ):
            self.assertIn(f"    {field}:", text)
        self.assertIn("unknown_policy: PRESERVE_AS_UNRESOLVED", text)

    def test_reference_graph_remains_lazy_and_evidence_driven(self):
        text = INSTITUTIONS.read_text(encoding="utf-8")
        self.assertIn("mode: continuously_enriched_reference_graph", text)
        self.assertIn("require_authoritative_evidence_for_restructure: true", text)


if __name__ == "__main__":
    unittest.main()
