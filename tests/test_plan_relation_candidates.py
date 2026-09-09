import contextlib
import copy
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
        sys.argv = ["plan_relation_candidates.py", "--dry-run"]
        with contextlib.redirect_stdout(io.StringIO()):
            if "scripts.plan_relation_candidates" in sys.modules:
                return importlib.reload(sys.modules["scripts.plan_relation_candidates"])
            return importlib.import_module("scripts.plan_relation_candidates")
    finally:
        sys.argv = original_argv


class PlanRelationCandidatesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def candidate(self, *, note="unchanged", created_at="2026-08-02", updated_at="2026-08-02"):
        return {
            "candidate_id": "relation-example",
            "origin_type": "relation_graph",
            "origin_ref": "scripts/plan_relation_candidates.py#s2_legacy_related",
            "candidate_type": "relation",
            "target_ref": "terms/target.md",
            "payload": {
                "source": "terms/source.md",
                "source_type": "term",
                "target": "terms/target.md",
                "target_type": "term",
                "signal": "s2_legacy_related",
                "note": note,
                "signal_confidence": "low",
            },
            "evidence_refs": [],
            "state": "needs_evidence",
            "decision": {
                "status": "pending",
                "reason": None,
                "decided_by": None,
                "decided_at": None,
            },
            "created_at": created_at,
            "updated_at": updated_at,
        }

    def test_unchanged_candidates_preserve_all_snapshot_dates_and_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "relation-candidates.yml"
            previous = self.candidate(created_at="2026-08-01", updated_at="2026-08-01")
            previous_text = self.module.render_relation_candidates([previous], "2026-08-01")
            output.write_text(previous_text, encoding="utf-8")

            stabilized = self.module.stabilize_candidate_timestamps(
                [self.candidate()],
                output,
                today="2026-08-02",
            )
            candidate_text = self.module.render_relation_candidates(stabilized, "2026-08-02")
            generated = self.module.stable_generated_date(
                candidate_text,
                output,
                today="2026-08-02",
            )
            rendered = self.module.render_relation_candidates(stabilized, generated)

        self.assertEqual(stabilized[0]["created_at"], "2026-08-01")
        self.assertEqual(stabilized[0]["updated_at"], "2026-08-01")
        self.assertEqual(generated, "2026-08-01")
        self.assertEqual(rendered, previous_text)

    def test_semantic_change_preserves_created_at_and_advances_updated_at(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "relation-candidates.yml"
            previous = self.candidate(
                note="before",
                created_at="2026-08-01",
                updated_at="2026-08-01",
            )
            output.write_text(
                self.module.render_relation_candidates([previous], "2026-08-01"),
                encoding="utf-8",
            )

            changed = copy.deepcopy(previous)
            changed["payload"]["note"] = "after"
            stabilized = self.module.stabilize_candidate_timestamps(
                [changed],
                output,
                today="2026-08-02",
            )
            candidate_text = self.module.render_relation_candidates(stabilized, "2026-08-02")
            generated = self.module.stable_generated_date(
                candidate_text,
                output,
                today="2026-08-02",
            )

        self.assertEqual(stabilized[0]["created_at"], "2026-08-01")
        self.assertEqual(stabilized[0]["updated_at"], "2026-08-02")
        self.assertEqual(generated, "2026-08-02")

    def test_new_candidate_uses_current_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "missing.yml"
            stabilized = self.module.stabilize_candidate_timestamps(
                [self.candidate()],
                output,
                today="2026-08-02",
            )

        self.assertEqual(stabilized[0]["created_at"], "2026-08-02")
        self.assertEqual(stabilized[0]["updated_at"], "2026-08-02")

    def test_theme_code_is_not_promoted_to_a_fabricated_structure_path(self):
        self.assertEqual(self.module._materialized_structure_target("C.6"), "")

    def test_theme_code_resolves_through_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            themes = Path(tmp) / "04-knowledge" / "structure" / "themes"
            themes.mkdir(parents=True)
            (themes / "c6-seventeenth-century-venice.md").write_text(
                "---\ntheme_code: C.6\n---\n", encoding="utf-8"
            )
            (themes / "b2-artist-training-and-guilds.md").write_text(
                "---\ntheme_code: B.2\n---\n", encoding="utf-8"
            )
            with mock.patch.object(self.module, "BASE", Path(tmp)):
                self.assertEqual(
                    self.module._materialized_theme_target("C.6"),
                    "themes/c6-seventeenth-century-venice.md",
                )

    def test_existing_topic_path_is_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            topics = Path(tmp) / "04-knowledge" / "structure" / "topics"
            topics.mkdir(parents=True)
            (topics / "art-and-institutional-power.md").write_text(
                "---\nnode_type: topic\n---\n", encoding="utf-8"
            )
            with mock.patch.object(self.module, "BASE", Path(tmp)):
                self.assertEqual(
                    self.module._materialized_structure_target("topics/art-and-institutional-power.md"),
                    "topics/art-and-institutional-power.md",
                )

    def test_weak_association_pair_is_not_recalled_as_candidate(self):
        source = "terms/source.md"
        target = "terms/target.md"
        pair = tuple(sorted((source, target)))
        original_candidates = self.module.candidates
        original_seen_pairs = self.module.seen_pairs
        original_formal_pairs = self.module.formal_pairs
        original_weak_pairs = self.module.weak_pairs
        original_all_units = self.module.all_units
        try:
            self.module.candidates = []
            self.module.seen_pairs = set()
            self.module.formal_pairs = set()
            self.module.weak_pairs = {pair}
            self.module.all_units = {
                source: {"type": "term"},
                target: {"type": "term"},
            }

            self.module.add_candidate(
                source,
                target,
                "s2_legacy_related",
                "legacy related",
                "low",
            )

            self.assertEqual(self.module.candidates, [])
            self.assertNotIn(pair, self.module.seen_pairs)
        finally:
            self.module.candidates = original_candidates
            self.module.seen_pairs = original_seen_pairs
            self.module.formal_pairs = original_formal_pairs
            self.module.weak_pairs = original_weak_pairs
            self.module.all_units = original_all_units

    def test_same_structure_membership_is_not_an_active_relation_signal(self):
        signals = {candidate["payload"]["signal"] for candidate in self.module.candidates}
        self.assertNotIn("s8_same_structure", signals)


if __name__ == "__main__":
    unittest.main()
