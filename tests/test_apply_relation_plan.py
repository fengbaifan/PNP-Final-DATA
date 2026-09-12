import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import apply_relation_plan


class ApplyRelationPlanTests(unittest.TestCase):
    def test_replacement_preserves_evidence_and_adds_qualifiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "04-knowledge" / "units" / "persons" / "teacher.md"
            target.parent.mkdir(parents=True)
            target.write_text("---\ntitle: Teacher\n---\n", encoding="utf-8")
            original = {
                "relation_type": "associated_person",
                "target": "persons/teacher.md",
                "evidence_ref": {"doc_id": "source-1"},
            }

            with patch.object(apply_relation_plan, "BASE", root):
                result = apply_relation_plan._validated_replacement(
                    original,
                    {"relation_type": "trained_by", "role": "student", "time": "1640"},
                    1,
                )

        self.assertEqual(result["relation_type"], "trained_by")
        self.assertEqual(result["role"], "student")
        self.assertEqual(result["time"], "1640")
        self.assertEqual(result["evidence_ref"], {"doc_id": "source-1"})

    def test_render_requires_exact_selector_and_can_split_one_relation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units = root / "04-knowledge" / "units" / "persons"
            units.mkdir(parents=True)
            source = units / "artist.md"
            (units / "teacher.md").write_text("---\ntitle: Teacher\n---\n", encoding="utf-8")
            relation = {
                "relation_type": "associated_person",
                "target": "persons/teacher.md",
                "note": "training and work",
                "evidence_ref": {"doc_id": "source-1"},
            }
            source.write_text(
                "---\ntitle: Artist\nrelations:\n  - "
                + json.dumps(relation, separators=(",", ":"))
                + "\n---\n\n## 内容\n",
                encoding="utf-8",
            )
            decision = {
                "_line": 1,
                "relation_type": "associated_person",
                "target": "persons/teacher.md",
                "replacements": [
                    {"relation_type": "trained_by", "role": "student"},
                    {"relation_type": "collaborated_with", "role": "collaborator"},
                ],
            }

            with patch.object(apply_relation_plan, "BASE", root):
                rendered, changes = apply_relation_plan._render_file(source, [decision])

        self.assertEqual(rendered.count('"relation_type":"trained_by"'), 1)
        self.assertEqual(rendered.count('"relation_type":"collaborated_with"'), 1)
        self.assertEqual(rendered.count('"evidence_ref":{"doc_id":"source-1"}'), 2)
        self.assertEqual(changes, ["associated_person->trained_by,collaborated_with persons/teacher.md"])

    def test_render_recognizes_an_already_applied_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units = root / "04-knowledge" / "units" / "persons"
            units.mkdir(parents=True)
            source = units / "artist.md"
            (units / "teacher.md").write_text("---\ntitle: Teacher\n---\n", encoding="utf-8")
            relation = {
                "relation_type": "trained_by",
                "target": "persons/teacher.md",
                "role": "student",
                "evidence_ref": {"doc_id": "source-1"},
            }
            original_text = (
                "---\ntitle: Artist\nrelations:\n  - "
                + json.dumps(relation, separators=(",", ":"))
                + "\n---\n\n## 内容\n"
            )
            source.write_text(original_text, encoding="utf-8")
            decision = {
                "_line": 1,
                "relation_type": "associated_person",
                "target": "persons/teacher.md",
                "replacements": [{"relation_type": "trained_by", "role": "student"}],
            }

            with patch.object(apply_relation_plan, "BASE", root):
                rendered, changes = apply_relation_plan._render_file(source, [decision])

        self.assertEqual(rendered, original_text)
        self.assertEqual(changes, ["already-applied associated_person->trained_by persons/teacher.md"])


if __name__ == "__main__":
    unittest.main()
