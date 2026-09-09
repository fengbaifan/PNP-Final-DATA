import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import build_runtime_index


class RuntimeIndexTests(unittest.TestCase):
    def test_missing_runtime_directory_is_an_empty_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["files"], 0)
        self.assertEqual(inventory["retention_tiers"]["R1"]["files"], 0)

    def test_retention_report_mode_is_read_only_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            batch = automation / "2026-06-01-example-batch-1"
            batch.mkdir(parents=True)
            (batch / "summary.md").write_text("# Summary\n", encoding="utf-8")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = build_runtime_index.main(["--retention-report"], root=root)

            report = json.loads(output.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(report["files"], 1)
        self.assertFalse((automation / "index.md").exists())

    def test_retention_inventory_reports_duplicates_without_mutating_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            first = automation / "2026-06-01-example-batch-1"
            second = automation / "2026-06-02-example-batch-2"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / "evidence.jsonl").write_text('{"id":"same"}\n', encoding="utf-8")
            (second / "evidence.jsonl").write_text('{"id":"same"}\n', encoding="utf-8")
            (second / "summary.md").write_text("# Unique\n", encoding="utf-8")

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["files"], 3)
        self.assertEqual(inventory["exact_duplicate_groups"], 1)
        self.assertEqual(inventory["exact_duplicate_files"], 1)
        self.assertEqual(inventory["potential_duplicate_bytes"], 14)

    def test_retention_inventory_normalizes_text_newlines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            first = automation / "2026-06-01-example-batch-1"
            second = automation / "2026-06-02-example-batch-2"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / "evidence.jsonl").write_bytes(b'{"id":"same"}\n')
            (second / "evidence.jsonl").write_bytes(b'{"id":"same"}\r\n')

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["total_bytes"], 28)
        self.assertEqual(inventory["exact_duplicate_groups"], 1)
        self.assertEqual(inventory["potential_duplicate_bytes"], 14)
        self.assertEqual(inventory["ephemeral_residue"], [])

    def test_retention_inventory_normalizes_unified_diff_newlines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            first = automation / "2026-06-01-example-batch-1"
            second = automation / "2026-06-02-example-batch-2"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / "membership.diff").write_bytes(b"@@ -1 +1 @@\n-old\n+new\n")
            (second / "membership.diff").write_bytes(b"@@ -1 +1 @@\r\n-old\r\n+new\r\n")

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["total_bytes"], 44)
        self.assertEqual(inventory["exact_duplicate_groups"], 1)
        self.assertEqual(inventory["potential_duplicate_bytes"], 22)

    def test_retention_inventory_classifies_r_tiers_conservatively(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = root / "06-runtime" / "automation" / "2026-06-01-example"
            batch.mkdir(parents=True)
            (batch / "evidence.jsonl").write_text("{}\n", encoding="utf-8")
            (batch / "queue-summary.json").write_text("{}\n", encoding="utf-8")
            (batch / "metrics.json").write_text("{}\n", encoding="utf-8")
            (batch / "cache.tmp").write_text("x", encoding="utf-8")

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["retention_tiers"]["R1"]["files"], 3)
        self.assertEqual(inventory["retention_tiers"]["R2"]["files"], 0)
        self.assertEqual(inventory["retention_tiers"]["R3"]["files"], 1)
        self.assertEqual(inventory["r2_provenance"]["review_required"], 1)

    def test_r2_manifest_is_detected_without_reclassifying_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = root / "06-runtime" / "automation" / "2026-06-01-example"
            batch.mkdir(parents=True)
            output_path = batch / "metrics.json"
            output_path.write_text("{}\n", encoding="utf-8")
            digest = build_runtime_index.hashlib.sha256(
                build_runtime_index.canonical_artifact_bytes(output_path)
            ).hexdigest()
            (batch / "generation-manifest.json").write_text(
                json.dumps(
                    {
                        "generator": {
                            "path": "scripts/example.py",
                            "sha256": "1" * 64,
                        },
                        "inputs": {"ku_state": {"sha256": "2" * 64}},
                        "invocation": {"rebuild_command": ["python", "scripts/example.py"]},
                        "outputs": [
                            {
                                "path": "06-runtime/automation/2026-06-01-example/metrics.json",
                                "sha256": f"sha256:{digest}",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["r2_provenance"]["with_manifest"], 1)
        self.assertEqual(inventory["r2_provenance"]["review_required"], 0)

    def test_manifest_with_wrong_hash_does_not_promote_r2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = root / "06-runtime" / "automation" / "2026-06-01-example"
            batch.mkdir(parents=True)
            (batch / "metrics.json").write_text("{}\n", encoding="utf-8")
            (batch / "generation-manifest.json").write_text(
                json.dumps(
                    {
                        "generator": {
                            "path": "scripts/example.py",
                            "sha256": "1" * 64,
                        },
                        "inputs": {"ku_state": {"sha256": "2" * 64}},
                        "parameters": {},
                        "output_hashes": {"metrics.json": "sha256:wrong"},
                    }
                ),
                encoding="utf-8",
            )

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["retention_tiers"]["R2"]["files"], 0)
        self.assertEqual(inventory["r2_provenance"]["review_required"], 1)

    def test_manifest_missing_required_provenance_does_not_promote_r2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = root / "06-runtime" / "automation" / "2026-06-01-example"
            batch.mkdir(parents=True)
            output_path = batch / "metrics.json"
            output_path.write_text("{}\n", encoding="utf-8")
            digest = build_runtime_index.hashlib.sha256(
                build_runtime_index.canonical_artifact_bytes(output_path)
            ).hexdigest()
            (batch / "generation-manifest.json").write_text(
                json.dumps(
                    {
                        "generator": {
                            "path": "scripts/example.py",
                            "sha256": "1" * 64,
                        },
                        "outputs": [{"path": "metrics.json", "sha256": digest}],
                    }
                ),
                encoding="utf-8",
            )

            inventory = build_runtime_index.build_retention_inventory(root)

        self.assertEqual(inventory["retention_tiers"]["R2"]["files"], 0)
        self.assertEqual(inventory["r2_provenance"]["review_required"], 1)

    def test_index_groups_batches_and_limits_recent_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            automation.mkdir(parents=True)
            for number in range(1, 18):
                batch = automation / f"2026-06-01-relation-example-batch-{number:02d}"
                batch.mkdir()
                (batch / "summary.md").write_text(f"# Batch {number}\n", encoding="utf-8")
            claim = automation / "2026-06-01-claim-example-batch-18"
            claim.mkdir()
            (claim / "summary.md").write_text("# Claim\n", encoding="utf-8")

            index = build_runtime_index.build_runtime_index(root, recent_limit=15)

        self.assertIn("| `relation` | 17 |", index)
        self.assertIn("| `claim` | 1 |", index)
        self.assertIn("](2026-06-01-claim-example-batch-18/summary.md)", index)
        self.assertIn("](2026-06-01-relation-example-batch-17/summary.md)", index)
        self.assertNotIn("](06-runtime/automation/", index)
        self.assertNotIn("2026-06-01-relation-example-batch-02/summary.md", index)

    def test_index_snapshot_excludes_generated_index_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            batch = automation / "2026-06-01-relation-example-batch-01"
            batch.mkdir(parents=True)
            (batch / "summary.md").write_text("# Batch\n", encoding="utf-8")
            generated = automation / "index.md"
            generated.write_text("old generated content\n", encoding="utf-8")

            index = build_runtime_index.build_runtime_index(root)

        self.assertIn("- Files: `1`", index)

    def test_index_exposes_retention_signals_without_recommending_deletion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            first = automation / "2026-06-01-example-batch-1"
            second = automation / "2026-06-02-example-batch-2"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / "queue.jsonl").write_text("same\n", encoding="utf-8")
            (second / "queue.jsonl").write_text("same\n", encoding="utf-8")

            index = build_runtime_index.build_runtime_index(root)

        self.assertIn("## Retention Signals", index)
        self.assertIn("- Exact duplicate groups: `1`", index)
        self.assertIn("- Ephemeral residue: `0`", index)
        self.assertIn(
            "[Runtime artifact retention policy](../../.agents/skills/00-coordination/system-upgrade/references/runtime-artifact-retention.md)",
            index,
        )
        self.assertNotIn("safe to delete", index.lower())

    def test_index_sorts_unpadded_batch_numbers_numerically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "06-runtime" / "automation"
            automation.mkdir(parents=True)
            for number in (9, 10, 89, 90):
                batch = automation / f"2026-06-01-relation-example-batch-{number}"
                batch.mkdir()
                (batch / "summary.md").write_text(f"# Batch {number}\n", encoding="utf-8")

            index = build_runtime_index.build_runtime_index(root)

        recent = index.split("## Recent Batches (15)", 1)[1]
        names = [
            line.split("]", 1)[0].removeprefix("- [")
            for line in recent.splitlines()
            if line.startswith("- [2026-")
        ]
        self.assertEqual(
            names,
            [
                "2026-06-01-relation-example-batch-90",
                "2026-06-01-relation-example-batch-89",
                "2026-06-01-relation-example-batch-10",
                "2026-06-01-relation-example-batch-9",
            ],
        )


if __name__ == "__main__":
    unittest.main()
