import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import generate_relation_evidence_candidates as generator


class RelationEvidenceCandidateGeneratorTests(unittest.TestCase):
    def test_collects_only_migrated_rows_without_selecting_relation_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.write_unit(root, "persons/source.md", "Source", ["../works/target.md"])
            target = self.write_unit(root, "works/target.md", "Target", ["../persons/source.md"])
            rows = [
                {
                    "source": "persons/source.md",
                    "source_type": "person",
                    "target": "works/target.md",
                    "target_type": "work",
                    "relation_type": "relates_to_work",
                    "relation_source": "migrated_from_related",
                },
                {
                    "source": "persons/source.md",
                    "source_type": "person",
                    "target": "works/target.md",
                    "target_type": "work",
                    "relation_type": "creator_of",
                    "relation_source": "explicit",
                },
            ]

            candidates, blockers = generator.build_candidates(rows, [], root)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(blockers, [])
        self.assertTrue(candidates[0]["signals"]["source_body_links_target"])
        self.assertTrue(candidates[0]["signals"]["target_body_links_source"])
        self.assertNotIn("proposed_relation_type", candidates[0])
        self.assertTrue(source.name)
        self.assertTrue(target.name)

    def test_routes_missing_endpoint_to_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(root, "persons/source.md", "Source", [])
            rows = [
                {
                    "source": "persons/source.md",
                    "source_type": "person",
                    "target": "works/missing.md",
                    "target_type": "work",
                    "relation_type": "relates_to_work",
                    "relation_source": "migrated_from_related",
                }
            ]

            candidates, blockers = generator.build_candidates(rows, [], root)

        self.assertEqual(candidates, [])
        self.assertEqual(len(blockers), 1)
        self.assertIn("target_endpoint_missing", blockers[0]["blocker_reasons"])

    def test_records_resolvable_frontmatter_evidence_ref_as_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(
                root,
                "persons/source.md",
                "Source",
                ["../works/target.md"],
                source_file="02-sources/doc/ch01/original.md",
            )
            self.write_unit(root, "works/target.md", "Target", [])
            (root / "02-sources/doc/ch01").mkdir(parents=True)
            (root / "02-sources/doc/ch01/original.md").write_text("source\n", encoding="utf-8")
            rows = [
                {
                    "source": "persons/source.md",
                    "source_type": "person",
                    "target": "works/target.md",
                    "target_type": "work",
                    "relation_type": "relates_to_work",
                    "relation_source": "migrated_from_related",
                }
            ]

            candidates, blockers = generator.build_candidates(rows, [], root)

        self.assertEqual(blockers, [])
        self.assertTrue(candidates[0]["signals"]["source_evidence_ref_resolvable"])
        self.assertEqual(
            candidates[0]["signals"]["source_evidence_ref"]["source_file"],
            "02-sources/doc/ch01/original.md",
        )

    def test_canonical_routes_self_link_to_blocker(self):
        candidate = self.candidate("terms/self.md", "terms/self.md")

        queues = generator.build_canonical_queues([], [candidate])

        self.assertEqual(queues["canonical_strong"], [])
        self.assertEqual(queues["blockers"][0]["blocker_reasons"], ["self_link"])

    def test_canonical_excludes_pair_when_reverse_explicit_relation_exists(self):
        candidate = self.candidate("terms/source.md", "terms/target.md")
        rows = [
            {
                "source": "terms/target.md",
                "target": "terms/source.md",
                "relation_source": "explicit",
                "relation_type": "variant_of",
            }
        ]

        queues = generator.build_canonical_queues(rows, [candidate])

        self.assertEqual(queues["canonical_strong"], [])
        self.assertEqual(queues["excluded_existing_pair"][0]["candidate_id"], "candidate-1")

    def test_canonical_collapses_mirror_candidates_deterministically(self):
        reverse = self.candidate("terms/target.md", "terms/source.md", candidate_id="candidate-2")
        forward = self.candidate("terms/source.md", "terms/target.md", candidate_id="candidate-1")

        queues = generator.build_canonical_queues([], [reverse, forward])

        self.assertEqual([row["candidate_id"] for row in queues["canonical_strong"]], ["candidate-1"])
        self.assertEqual([row["candidate_id"] for row in queues["excluded_mirror"]], ["candidate-2"])

    def test_canonical_requires_strong_window_without_adding_semantic_fields(self):
        weak = self.candidate("terms/weak.md", "terms/target.md", candidate_id="candidate-weak")
        weak["signals"]["target_body_links_source"] = False
        strong = self.candidate("terms/strong.md", "terms/target.md", candidate_id="candidate-strong")

        queues = generator.build_canonical_queues([], [weak, strong])

        self.assertEqual([row["candidate_id"] for row in queues["canonical_strong"]], ["candidate-strong"])
        self.assertEqual([row["candidate_id"] for row in queues["defer_signal"]], ["candidate-weak"])
        self.assertNotIn("proposed_relation_type", queues["canonical_strong"][0])
        self.assertNotIn("inverse_relation_type", queues["canonical_strong"][0])
        self.assertNotIn("approved", queues["canonical_strong"][0])

    def test_canonical_splits_fresh_and_historical_defer_windows(self):
        fresh = self.candidate("terms/fresh.md", "terms/target.md", candidate_id="candidate-fresh")
        historical = self.candidate("terms/historical.md", "terms/other.md", candidate_id="candidate-historical")
        historical["historical_defer"] = [{"reason": "controlled_relation_type_not_semantically_justified"}]

        queues = generator.build_canonical_queues([], [fresh, historical])

        self.assertEqual(
            [row["candidate_id"] for row in queues["canonical_strong"]],
            ["candidate-fresh", "candidate-historical"],
        )
        self.assertEqual([row["candidate_id"] for row in queues["canonical_fresh"]], ["candidate-fresh"])
        self.assertEqual(
            [row["candidate_id"] for row in queues["canonical_historical_defer"]],
            ["candidate-historical"],
        )

    @staticmethod
    def candidate(source: str, target: str, candidate_id: str = "candidate-1") -> dict:
        return {
            "candidate_id": candidate_id,
            "source": source,
            "target": target,
            "signals": {
                "source_body_links_target": True,
                "target_body_links_source": True,
                "source_evidence_ref_resolvable": True,
            },
        }

    @staticmethod
    def write_unit(
        root: Path,
        relative_path: str,
        title: str,
        body_links: list[str],
        source_file: str | None = None,
    ) -> Path:
        path = root / "04-knowledge/units" / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        frontmatter = {"title": title}
        if source_file:
            frontmatter["sources"] = [{"evidence_ref": {"source_file": source_file}}]
        links = "\n".join(f"[link]({link})" for link in body_links)
        path.write_text(f"---\n{yaml.safe_dump(frontmatter, allow_unicode=True)}---\n{links}\n", encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
