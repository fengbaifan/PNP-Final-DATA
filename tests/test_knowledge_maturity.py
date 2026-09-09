import json
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import audit_repo


def snapshot(root: Path, relative: str, source_count: int, confidence: str, consensus: str) -> audit_repo.UnitSnapshot:
    path = root / relative
    text = (
        "---\n"
        f"source_count: {source_count}\n"
        f"confidence: {confidence}\n"
        f"consensus: {consensus}\n"
        "evidence_status: source_backed\n"
        "---\nbody\n"
    )
    return audit_repo.UnitSnapshot(
        path=path,
        relative_path=relative,
        type_name=path.parent.name,
        text=text,
        frontmatter=audit_repo.extract_frontmatter(text),
        body="body\n",
    )


class KnowledgeMaturityTests(unittest.TestCase):
    def test_runtime_retention_gaps_reduce_engineering_safety(self):
        baseline = audit_repo.build_structural_health_score({})
        degraded = audit_repo.build_structural_health_score({
            "runtime_artifact_retention": {
                "review_required": 2,
                "ephemeral_residue": 2,
            }
        })

        self.assertEqual(baseline["engineering_safety"], 5)
        self.assertEqual(degraded["engineering_safety"], 2)

    def test_maturity_is_unscored_and_separates_research_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relation = root / "04-knowledge" / "quality" / "relation-index.yml"
            relation.parent.mkdir(parents=True)
            relation.write_text(yaml.safe_dump([{"source": "persons/a.md", "target": "terms/b.md"}]), encoding="utf-8")
            discovery = root / "06-runtime" / "state" / "discovery-manifest.json"
            discovery.parent.mkdir(parents=True)
            discovery.write_text(json.dumps({
                "candidate_counts": {
                    "total": 2,
                    "by_state": {"needs_evidence": 2},
                    "by_candidate_type": {"relation": 2},
                },
                "actionable_candidate_counts": {
                    "total": 2,
                    "by_state": {"needs_evidence": 2},
                    "by_candidate_type": {"relation": 2},
                },
            }), encoding="utf-8")
            snapshots = [
                snapshot(root, "04-knowledge/units/persons/a.md", 1, "low", "tentative"),
                snapshot(root, "04-knowledge/units/terms/b.md", 2, "medium", "confirmed"),
                snapshot(root, "04-knowledge/units/works/c.md", 1, "medium", "tentative"),
            ]

            maturity = audit_repo.knowledge_maturity_check(root, snapshots)

        self.assertEqual(maturity["metric_kind"], "unscored_semantic_maturity")
        self.assertEqual(maturity["source_count_distribution"], {"multi_source": 1, "single_source": 2})
        self.assertEqual(maturity["isolated_units"]["count"], 1)
        self.assertEqual(maturity["research_debt"]["candidates_needing_evidence"], 2)
        self.assertNotIn("score", maturity)

    def test_structure_quality_has_truthful_maximum_and_no_fake_source_diversity(self):
        score = audit_repo.build_knowledge_structure_quality_score({
            "disambiguation": {"duplicates_without_disambiguation": 0},
            "type_mismatches": [],
            "invalid_enums": {"invalid_confidence": [], "invalid_consensus": []},
            "unverified_by_type": {},
            "recommended_field_missing": {},
        })

        self.assertEqual(score["total"], 65)
        self.assertEqual(score["max_score"], 65)
        self.assertNotIn("source_diversity", score)

    def test_hierarchy_assignment_is_reported_as_research_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshots = [snapshot(root, "04-knowledge/units/terms/a.md", 1, "medium", "tentative")]

            assignment = audit_repo.hierarchy_assignment_check(snapshots)
            maturity = audit_repo.knowledge_maturity_check(root, snapshots)

        self.assertEqual(assignment["complete_assignments"], 0)
        self.assertEqual(assignment["units_missing_any_assignment"], 1)
        self.assertEqual(maturity["research_debt"]["units_missing_hierarchy_assignment"], 1)

    def test_hierarchy_assignment_requires_a_structured_topic_membership(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "04-knowledge/units/terms/a.md"
            text = (
                "---\nprimary_domain: example\nprimary_dimension: A\nprimary_theme: A.1\n"
                "topic_memberships:\n  - topic: topics/example.md\n    role: term_anchor\n---\nbody\n"
            )
            snapshots = [audit_repo.UnitSnapshot(
                path=path,
                relative_path="04-knowledge/units/terms/a.md",
                type_name="terms",
                text=text,
                frontmatter=audit_repo.extract_frontmatter(text),
                body="body\n",
            )]

            assignment = audit_repo.hierarchy_assignment_check(snapshots)

        self.assertEqual(assignment["complete_assignments"], 1)
        self.assertEqual(assignment["field_coverage"]["topic_memberships"], "1/1")

    def test_structure_inventory_excludes_readme_and_rejects_wrong_node_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            domains = root / "04-knowledge" / "structure" / "domains"
            domains.mkdir(parents=True)
            (domains / "README.md").write_text("# navigation\n", encoding="utf-8")
            (domains / "wrong.md").write_text(
                "---\ntitle: Wrong\nnode_type: dimension\n---\n",
                encoding="utf-8",
            )

            counts = audit_repo.count_structure_nodes(root)
            issues = audit_repo.structure_node_type_issues(root)

        self.assertEqual(counts["domains"], 1)
        self.assertEqual(issues[0]["expected"], "domain")

    def test_hierarchy_structure_rejects_unknown_topic_parent_theme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            topics = root / "04-knowledge" / "structure" / "topics"
            themes = root / "04-knowledge" / "structure" / "themes"
            topics.mkdir(parents=True)
            themes.mkdir(parents=True)
            (topics / "orphan.md").write_text(
                "---\nnode_type: topic\nprimary_dimension: A\nparent_theme: A.9\n---\n",
                encoding="utf-8",
            )

            issues = audit_repo.hierarchy_structure_issues(root)

        self.assertEqual(issues[0]["issue"], "unknown_parent_theme")
