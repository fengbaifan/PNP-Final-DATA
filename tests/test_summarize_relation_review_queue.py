import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import summarize_relation_review_queue as summarizer


class RelationReviewQueueSummaryTests(unittest.TestCase):
    def test_relation_index_evidence_ref_and_claim_id_are_direct_evidence(self):
        summary = summarizer.relation_index_summary(
            [
                {"confidence": "medium", "relation_type": "created_by", "evidence_ref": {"source_span": "p. 4"}},
                {"confidence": "low", "relation_type": "parent_of", "claim_id": "claim-1"},
                {"confidence": "medium", "relation_type": "held_by"},
            ]
        )

        self.assertEqual(summary["weak_evidence_count"], 1)
        self.assertEqual(summary["weak_evidence_by_relation_type"], {"held_by": 1})

    def test_latest_defer_ledger_uses_numeric_batch_suffix_across_directory_prefixes(self):
        with tempfile.TemporaryDirectory() as tmp:
            automation_dir = Path(tmp)
            self.write_ledger(automation_dir / "2026-05-31-relation-defer-ledger-refresh-batch-77")
            newest = automation_dir / "2026-05-31-claim-support-closeout-refresh-batch-80"
            self.write_ledger(newest)

            with patch.object(summarizer, "AUTOMATION_DIR", automation_dir):
                summary = summarizer.latest_defer_ledger_summary()

        self.assertEqual(summary["path"], str(newest / "defer_ledger.jsonl"))

    def test_latest_isolated_ledger_uses_numeric_batch_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            automation_dir = Path(tmp)
            self.write_isolated_ledger(automation_dir / "2026-06-01-isolated-unit-ledger-refresh-batch-98")
            newest = automation_dir / "2026-06-01-isolated-unit-ledger-refresh-batch-101"
            self.write_isolated_ledger(newest)

            with patch.object(summarizer, "AUTOMATION_DIR", automation_dir):
                summary = summarizer.latest_isolated_unit_ledger_summary()

        self.assertEqual(summary["path"], str(newest / "isolated_unit_ledger.jsonl"))

    def test_latest_isolated_ledger_prefers_newer_date_and_accepts_preflight_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            automation_dir = Path(tmp)
            self.write_isolated_ledger(
                automation_dir / "2026-06-02-isolated-canonical-closeout-refresh-batch-130"
            )
            newest = automation_dir / "2026-07-10-isolated-unit-classification-batch-118-preflight"
            self.write_isolated_ledger(newest)

            with patch.object(summarizer, "AUTOMATION_DIR", automation_dir):
                summary = summarizer.latest_isolated_unit_ledger_summary()

        self.assertEqual(summary["path"], str(newest / "isolated_unit_ledger.jsonl"))

    def test_latest_isolated_ledger_discovers_nested_current_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            automation_dir = Path(tmp)
            self.write_isolated_ledger(
                automation_dir / "2026-07-11-isolated-source-boundary-review-batch-140"
            )
            newest = (
                automation_dir
                / "2026-07-16-pending-control-evidence-closeout-batch-252"
                / "current-isolated-ledger"
            )
            self.write_isolated_ledger(newest)

            with patch.object(summarizer, "AUTOMATION_DIR", automation_dir):
                summary = summarizer.latest_isolated_unit_ledger_summary()

        self.assertEqual(summary["path"], str(newest / "isolated_unit_ledger.jsonl"))

    def test_latest_defer_ledger_prefers_newer_date_over_higher_old_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            automation_dir = Path(tmp)
            self.write_ledger(automation_dir / "2026-06-02-relation-defer-refresh-batch-130")
            newest = automation_dir / "2026-07-10-relation-defer-refresh-batch-118-preflight"
            self.write_ledger(newest)

            with patch.object(summarizer, "AUTOMATION_DIR", automation_dir):
                summary = summarizer.latest_defer_ledger_summary()

        self.assertEqual(summary["path"], str(newest / "defer_ledger.jsonl"))

    def test_latest_isolated_ledger_prefers_current_window_bucket_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            automation_dir = Path(tmp)
            newest = automation_dir / "2026-06-02-isolated-unit-ledger-refresh-batch-120"
            self.write_isolated_ledger(newest)
            (newest / "isolated_unit_ledger_coverage.json").write_text(
                json.dumps(
                    {
                        "current_isolated_audit_window": 1,
                        "covered_current_window": 1,
                        "by_bucket": {"formal_relation_candidate": 16, "needs_minimum_relation_review": 1},
                        "current_window_by_bucket": {"needs_minimum_relation_review": 1},
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(summarizer, "AUTOMATION_DIR", automation_dir):
                summary = summarizer.latest_isolated_unit_ledger_summary()

        self.assertEqual(summary["by_bucket"], {"needs_minimum_relation_review": 1})

    @staticmethod
    def write_ledger(directory: Path) -> None:
        directory.mkdir(parents=True)
        (directory / "defer_ledger.jsonl").write_text(
            json.dumps({"source_type": "term", "target_type": "term"}) + "\n",
            encoding="utf-8",
        )
        (directory / "defer_ledger_aggregate.jsonl").write_text("", encoding="utf-8")

    @staticmethod
    def write_isolated_ledger(directory: Path) -> None:
        directory.mkdir(parents=True)
        (directory / "isolated_unit_ledger.jsonl").write_text(
            json.dumps({"unit": "persons/example.md", "bucket": "valid_standalone"}) + "\n",
            encoding="utf-8",
        )
        (directory / "isolated_unit_ledger_coverage.json").write_text(
            json.dumps({"current_isolated_audit_window": 1, "covered_current_window": 1}),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
