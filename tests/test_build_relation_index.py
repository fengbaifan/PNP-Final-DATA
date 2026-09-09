import contextlib
import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load_module():
    original_argv = sys.argv[:]
    try:
        sys.argv = ["build_relation_index.py", "--dry-run"]
        with contextlib.redirect_stdout(io.StringIO()):
            if "scripts.build_relation_index" in sys.modules:
                return importlib.reload(sys.modules["scripts.build_relation_index"])
            return importlib.import_module("scripts.build_relation_index")
    finally:
        sys.argv = original_argv


class BuildRelationIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_inverse_of_evidence_backed_relation_is_auto_validated(self):
        inverse = self.module._build_inverse_relation(
            {
                "source": "events/example-event.md",
                "source_type": "event",
                "target": "works/example-work.md",
                "target_type": "work",
                "relation_type": "subject_of",
                "evidence": "Event body directly identifies the work as depicting the event.",
                "evidence_ref": {"source_file": "02-sources/example/original.md"},
                "confidence": "medium",
                "review_status": "auto_validated",
            }
        )

        self.assertEqual(inverse["relation_type"], "has_subject")
        self.assertEqual(inverse["inverse_relation_type"], "subject_of")
        self.assertEqual(inverse["review_status"], "auto_validated")
        self.assertEqual(inverse["relation_source"], "inferred_by_rule")
        self.assertEqual(
            inverse["evidence_ref"]["source_file"],
            "02-sources/example/original.md",
        )

    def test_inverse_of_weak_inference_stays_weak(self):
        inverse = self.module._build_inverse_relation(
            {
                "source": "terms/source.md",
                "source_type": "term",
                "target": "works/target.md",
                "target_type": "work",
                "relation_type": "exemplified_by",
                "review_status": "weak_inference",
            }
        )

        self.assertEqual(inverse["review_status"], "weak_inference")

    def test_inverse_of_needs_evidence_preserves_needs_evidence(self):
        inverse = self.module._build_inverse_relation(
            {
                "source": "persons/source.md",
                "source_type": "person",
                "target": "archives/target.md",
                "target_type": "archive",
                "relation_type": "author_of",
                "review_status": "needs_evidence",
            }
        )

        self.assertEqual(inverse["review_status"], "needs_evidence")

    def test_explicitly_one_way_relation_does_not_build_inverse(self):
        self.assertFalse(self.module._should_build_inverse({
            "relation_type": "member_of",
            "bidirectional_required": False,
            "review_status": "auto_validated",
        }))

    def test_commission_relation_has_controlled_inverse(self):
        self.assertIn("commissioned_by", self.module.RELATION_TYPES)
        self.assertIn("commissioner_of", self.module.RELATION_TYPES)

        inverse = self.module._build_inverse_relation(
            {
                "source": "archives/example-atlas.md",
                "source_type": "archive",
                "target": "persons/example-patron.md",
                "target_type": "person",
                "relation_type": "commissioned_by",
                "evidence": "The source explicitly says the atlas was commissioned by the patron.",
                "evidence_ref": {"source_file": "02-sources/example/original.md"},
                "confidence": "medium",
                "review_status": "evidence_backed_relation",
            }
        )

        self.assertEqual(inverse["relation_type"], "commissioner_of")
        self.assertEqual(inverse["inverse_relation_type"], "commissioned_by")
        self.assertEqual(inverse["review_status"], "auto_validated")

    def test_weak_association_targets_block_legacy_relation_fallbacks(self):
        targets = self.module._weak_association_targets(
            {
                "weak_associations": [
                    {"target": "../terms/context.md", "reason": "context only"},
                    {"target": "../persons/example.md"},
                ]
            },
            "works/source.md",
        )

        self.assertEqual(
            targets,
            {"terms/context.md", "persons/example.md"},
        )

    def test_theme_code_is_not_treated_as_an_explicit_structure_path(self):
        self.assertEqual(self.module._materialized_structure_target("B.2"), "")

    def test_theme_code_resolves_through_materialized_theme_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            themes = Path(tmp) / "04-knowledge" / "structure" / "themes"
            themes.mkdir(parents=True)
            (themes / "b2-artist-training-and-guilds.md").write_text(
                "---\ntheme_code: B.2\n---\n", encoding="utf-8"
            )
            with mock.patch.object(self.module, "STRUCTURE", Path(tmp) / "04-knowledge" / "structure"):
                self.assertEqual(
                    self.module._materialized_theme_target("B.2"),
                    "themes/b2-artist-training-and-guilds.md",
                )

    def test_existing_structure_path_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            topics = Path(tmp) / "04-knowledge" / "structure" / "topics"
            topics.mkdir(parents=True)
            (topics / "patronage-and-social-display.md").write_text(
                "---\nnode_type: topic\n---\n", encoding="utf-8"
            )
            with mock.patch.object(self.module, "STRUCTURE", Path(tmp) / "04-knowledge" / "structure"):
                self.assertEqual(
                    self.module._materialized_structure_target("topics/patronage-and-social-display.md"),
                    "topics/patronage-and-social-display.md",
                )

    def test_hierarchy_relations_use_structure_root_targets(self):
        original = self.module.relations[:]
        try:
            self.module.relations[:] = [{
                "source": "works/x.md",
                "target": "structure/themes/b2-artist-training-and-guilds.md",
                "evidence": "hierarchy.b2",
            }]
            hierarchy_relations = [
                relation
                for relation in self.module.relations
                if str(relation.get("evidence") or "").startswith("hierarchy.")
            ]
            self.assertTrue(hierarchy_relations)
            self.assertTrue(all(relation["target"].startswith("structure/") for relation in hierarchy_relations))
        finally:
            self.module.relations[:] = original

    def test_stable_generated_date_preserves_date_for_unchanged_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "relation-index.yml"
            candidate = self.module.render_relation_index(self.module.TODAY)
            output.write_text(
                candidate.replace(
                    f"# generated: {self.module.TODAY}",
                    "# generated: 2026-06-02",
                    1,
                ),
                encoding="utf-8",
            )

            generated = self.module.stable_generated_date(candidate, output)

        self.assertEqual(generated, "2026-06-02")

    def test_stable_generated_date_advances_for_changed_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "relation-index.yml"
            output.write_text(
                self.module.render_relation_index("2026-06-02") + "# changed\n",
                encoding="utf-8",
            )

            generated = self.module.stable_generated_date(
                self.module.render_relation_index(self.module.TODAY), output
            )

        self.assertEqual(generated, self.module.TODAY)


if __name__ == "__main__":
    unittest.main()
