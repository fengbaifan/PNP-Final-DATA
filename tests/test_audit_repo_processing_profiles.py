import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import audit_repo, validate_processing_package as validator
from scripts._source_fingerprint import FINGERPRINT_MODE, aggregate_input_fingerprint, source_sha256


class CompactProcessingProfileTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "02-sources" / "example-source").mkdir(parents=True)
        processing = root / "03-processing" / "example-source"
        processing.mkdir(parents=True)
        return tmp, root, processing

    def test_compact_profile_satisfies_dataflow_and_quality_checks(self):
        tmp, root, processing = self.make_root()
        self.addCleanup(tmp.cleanup)
        source = root / "02-sources" / "example-source" / "original.md"
        source.write_text("source\n", encoding="utf-8")
        (processing / "source-map.jsonl").write_text(
            json.dumps({
                "block_id": "b001",
                "source_file": "02-sources/example-source/original.md",
                "line_start": 1,
                "line_end": 1,
                "read_status": "read",
                "semantic_unit_refs": ["su001"],
                "candidate_refs": [],
                "no_candidate_reason": "scope contains no durable candidate",
            }) + "\n",
            encoding="utf-8",
        )
        (processing / "semantic-units.jsonl").write_text(
            json.dumps({"semantic_unit_id": "su001", "source_block_refs": ["b001"]}) + "\n",
            encoding="utf-8",
        )
        (processing / "candidate-ledger.jsonl").write_text("", encoding="utf-8")
        (processing / "summary.md").write_text("# Summary\n", encoding="utf-8")
        assets = [{"path": "02-sources/example-source/original.md", "sha256": source_sha256(source)}]
        fingerprint = aggregate_input_fingerprint(assets)
        (processing / "manifest.json").write_text(
            json.dumps({
                "processing_profile": "compact-v4",
                "status": "completed",
                "fingerprint_mode": FINGERPRINT_MODE,
                "source_assets": assets,
                "processing_scope": {
                    "mode": "full_asset",
                    "assets": ["02-sources/example-source/original.md"],
                },
                "input_fingerprint": fingerprint,
                "semantic_acceptance": {
                    "reread_status": "accepted",
                    "reviewer_kind": "agent",
                    "reviewer_id": "test-agent",
                    "reviewed_at": "2026-08-02T00:00:00Z",
                    "source_version": fingerprint,
                    "omission_count": 0,
                    "acceptance_boundary": "test semantic boundary",
                },
                "coverage": {
                    "source_blocks_total": 1,
                    "source_blocks_reviewed": 1,
                    "unread_blocks": 0,
                    "blocks_without_candidate_review": 0,
                    "scope_assets_total": 1,
                    "scope_assets_reviewed": 1,
                    "scope_lines_total": 1,
                    "scope_lines_reviewed": 1,
                },
                "output_hashes": {
                    name: f"sha256:{validator.sha256(processing / name)}"
                    for name in validator.LOGICAL_FILES
                },
            }),
            encoding="utf-8",
        )

        self.assertEqual(audit_repo.dataflow_issues(root), [])
        recall = audit_repo.recall_quality_check(root)
        reading = audit_repo.semantic_artifact_integrity_check(root)
        acceptance = audit_repo.semantic_acceptance_check(root)
        self.assertEqual(recall["chapters_without_candidate"], [])
        self.assertEqual(recall["chapters_without_decision"], [])
        self.assertEqual(recall["chapters_without_recall"], [])
        self.assertEqual(reading["chapters_without_reading_ledger"], [])
        self.assertEqual(reading["chapters_without_extraction_coverage_matrix"], [])
        self.assertEqual(acceptance["accepted"], 1)
        self.assertEqual(acceptance["reopened_source_drift"], 0)
        self.assertEqual(acceptance["legacy_packages_without_acceptance"], 0)

    def test_compact_profile_reports_missing_artifact(self):
        tmp, root, processing = self.make_root()
        self.addCleanup(tmp.cleanup)
        (processing / "manifest.json").write_text(
            json.dumps({"processing_profile": "compact-v4"}), encoding="utf-8"
        )

        self.assertIn(
            "example-source: compact-v4 missing candidate-ledger.jsonl",
            audit_repo.dataflow_issues(root),
        )


if __name__ == "__main__":
    unittest.main()
