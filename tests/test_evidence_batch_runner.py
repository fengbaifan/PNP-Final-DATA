import json
import tempfile
import unittest
from pathlib import Path

from scripts import evidence_batch_runner as runner


class AutomationRunnerSupportTests(unittest.TestCase):
    def test_runner_has_no_git_closeout_executor(self):
        self.assertFalse(hasattr(runner, "run_git_closeout"))

    def test_reason_summary_counts_defer_and_no_delta_reasons(self):
        classified = [
            {
                "risk_level": "L3",
                "automation_action": "defer",
                "automation_reasons": ["proposed_new_ku", "blocking_reason: external"],
            },
            {
                "risk_level": "L1",
                "automation_action": "no_delta_existing_ku",
                "automation_reasons": ["existing_ku", "current_frontmatter_already_matches_recommended_changes"],
            },
            {
                "risk_level": "L3",
                "automation_action": "defer",
                "automation_reasons": ["proposed_new_ku"],
            },
        ]

        summary = runner.summarize_automation_reasons(classified)

        self.assertEqual(summary["by_action"]["defer"], 2)
        self.assertEqual(summary["by_action"]["no_delta_existing_ku"], 1)
        self.assertEqual(summary["by_reason"]["proposed_new_ku"], 2)
        self.assertEqual(summary["by_reason"]["current_frontmatter_already_matches_recommended_changes"], 1)

    def test_empty_queue_is_not_materialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            result = runner.write_nonempty_queue(out_dir, "empty.jsonl", [])
            self.assertIsNone(result)
            self.assertFalse((out_dir / "empty.jsonl").exists())

    def test_batch_manifest_accepts_utf8_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text('{"batch_id":"bom-ok"}', encoding="utf-8-sig")

            data = runner.read_batch_manifest(manifest)

        self.assertEqual(data["batch_id"], "bom-ok")

    def test_nonempty_queue_is_materialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            result = runner.write_nonempty_queue(out_dir, "one.jsonl", [{"id": "a"}])
            self.assertEqual(Path(result).name, "one.jsonl")
            self.assertEqual(json.loads((out_dir / "one.jsonl").read_text(encoding="utf-8")), {"id": "a"})

    def test_proposed_new_ku_is_always_deferred(self):
        risk, action, reasons = runner.classify({"proposed_ku_path": "04-knowledge/units/events/new.md"})
        self.assertEqual((risk, action), ("L3", "defer"))
        self.assertIn("proposed_new_event_ku", reasons)


if __name__ == "__main__":
    unittest.main()
