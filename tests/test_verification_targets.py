import json
import tempfile
import unittest
from pathlib import Path

from scripts import _verification_targets as targets


class VerificationTargetTests(unittest.TestCase):
    def test_load_result_targets_filters_checkpoint_and_preserves_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            units = root / "04-knowledge/units"
            first = units / "terms/first.md"
            second = units / "works/second.md"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text("---\ntitle: First\n---\n", encoding="utf-8")
            second.write_text("---\ntitle: Second\n---\n", encoding="utf-8")
            plan = root / "plan.json"
            plan.write_text(
                json.dumps(
                    {
                        "targets": [
                            {"unit": "04-knowledge/units/terms/first.md", "checkpoint": 1},
                            {"unit": "04-knowledge/units/works/second.md", "checkpoint": 2},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = targets.load_result_targets(plan, root, units, checkpoint=2)

        self.assertEqual(result, [second])

    def test_write_jsonl_replaces_output_without_leaving_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence.jsonl"
            targets.write_jsonl([{"evidence": 1}], output)

            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"evidence": 1})
            self.assertFalse(output.with_suffix(".jsonl.tmp").exists())

    def test_load_evidence_targets_filters_failures_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            units = root / "04-knowledge/units"
            first = units / "terms/first.md"
            second = units / "works/second.md"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text("---\ntitle: First\n---\n", encoding="utf-8")
            second.write_text("---\ntitle: Second\n---\n", encoding="utf-8")
            evidence_one = root / "evidence-one.jsonl"
            evidence_two = root / "evidence-two.jsonl"
            evidence_one.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "ku_path": "04-knowledge/units/terms/first.md",
                                "blocking_reason": "api_error",
                            }
                        ),
                        json.dumps(
                            {
                                "ku_path": "04-knowledge/units/works/second.md",
                                "blocking_reason": "weak_match",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            evidence_two.write_text(
                json.dumps(
                    {
                        "ku_path": "04-knowledge/units/terms/first.md",
                        "blocking_reason": "api_error",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = targets.load_evidence_targets(
                [evidence_one, evidence_two],
                root,
                units,
                {"api_error"},
            )

        self.assertEqual(result, [first])


if __name__ == "__main__":
    unittest.main()
