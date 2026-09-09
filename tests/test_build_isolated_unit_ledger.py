import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_isolated_unit_ledger as ledger


class IsolatedUnitLedgerTests(unittest.TestCase):
    def test_generation_manifest_captures_every_rebuild_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generator = root / "scripts" / "build_isolated_unit_ledger.py"
            relation_index = root / "04-knowledge" / "quality" / "relation-index.yml"
            triage = root / "automation" / "batch-1" / "reviewed-units.jsonl"
            reviewed = root / "automation" / "batch-0" / "isolated_unit_ledger.jsonl"
            current_window = root / "automation" / "batch-0" / "next_isolated_review_window.jsonl"
            output = root / "out" / "isolated_unit_ledger_coverage.json"
            for path, content in (
                (generator, "generator\n"),
                (relation_index, "relations: []\n"),
                (triage, "{}\n"),
                (reviewed, "{}\n"),
                (current_window, "{}\n"),
                (output, "{}\n"),
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            self.write_unit(root, "works/example.md", body="first state\n")

            manifest = ledger.build_generation_manifest(
                generator_path=generator,
                automation_root=root / "automation",
                relation_index_path=relation_index,
                triage_paths=[triage],
                reviewed_ledger_paths=[reviewed],
                current_window_path=current_window,
                units_dir=root / "04-knowledge" / "units",
                output_paths=[output],
                original_argv=["--triage", "automation/batch-1/reviewed-units.jsonl"],
                audit_window_limit=100,
                current_window_only=True,
                base=root,
            )

        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["generator"]["path"], "scripts/build_isolated_unit_ledger.py")
        self.assertEqual(manifest["inputs"]["relation_index"]["path"], "04-knowledge/quality/relation-index.yml")
        self.assertEqual(
            [row["path"] for row in manifest["inputs"]["triage"]],
            ["automation/batch-1/reviewed-units.jsonl"],
        )
        self.assertEqual(
            [row["path"] for row in manifest["inputs"]["reviewed_ledgers"]],
            ["automation/batch-0/isolated_unit_ledger.jsonl"],
        )
        self.assertEqual(manifest["inputs"]["ku_state"]["file_count"], 1)
        self.assertEqual(manifest["outputs"][0]["path"], "out/isolated_unit_ledger_coverage.json")
        self.assertEqual(manifest["invocation"]["original_argv"], ["--triage", "automation/batch-1/reviewed-units.jsonl"])
        self.assertIn("--reviewed-ledger", manifest["invocation"]["rebuild_command"])
        self.assertIn("{out_dir}", manifest["invocation"]["rebuild_command"])

    def test_complete_ku_state_digest_changes_when_unit_content_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_unit(root, "works/example.md", body="first state\n")
            units_dir = root / "04-knowledge" / "units"
            before = ledger.complete_ku_state_digest(units_dir, base=root)

            self.write_unit(root, "works/example.md", body="second state\n")
            after = ledger.complete_ku_state_digest(units_dir, base=root)

        self.assertEqual(before["file_count"], 1)
        self.assertEqual(after["file_count"], 1)
        self.assertNotEqual(before["sha256"], after["sha256"])

    def test_explicit_triage_reads_only_selected_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected = root / "automation" / "selected-batch-100" / "triage.jsonl"
            unrelated = root / "automation" / "unrelated-batch-99" / "triage.jsonl"
            self.write_triage(selected, "persons/selected.md", "valid_standalone")
            self.write_triage(unrelated, "persons/unrelated.md", "needs_source_review")
            self.write_unit(root, "persons/selected.md")
            self.write_unit(root, "persons/unrelated.md")

            rows = ledger.build_ledger_from_triage([selected], root / "04-knowledge" / "units")

        self.assertEqual([row["unit"] for row in rows], ["persons/selected.md"])

    def test_multiple_triage_inputs_keep_only_latest_decision_per_unit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            older = root / "automation" / "2026-07-10-isolated-batch-132" / "triage.jsonl"
            newer = root / "automation" / "2026-07-11-isolated-batch-134" / "triage.jsonl"
            self.write_triage(older, "persons/example.md", "needs_source_review")
            self.write_triage(newer, "persons/example.md", "valid_standalone")
            self.write_unit(root, "persons/example.md")

            rows = ledger.build_ledger_from_triage([older, newer], root / "04-knowledge" / "units")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["bucket"], "valid_standalone")

    def test_current_frontmatter_exposes_stale_snapshot_and_mechanical_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            triage = root / "automation" / "isolated-batch-47" / "triage.jsonl"
            self.write_triage(
                triage,
                "events/example.md",
                "needs_source_review",
                source_count=0,
                confidence="",
                evidence_status="",
                body_link_count=0,
            )
            self.write_unit(
                root,
                "events/example.md",
                body="[Target](../publications/target.md)\n",
                weak_associations=[{"target": "../publications/target.md", "reason": "needs_review"}],
            )

            rows = ledger.build_ledger_from_triage([triage], root / "04-knowledge" / "units")
            windows = ledger.build_signal_queues(rows)

        row = rows[0]
        self.assertEqual(row["historical_bucket"], "needs_source_review")
        self.assertEqual(row["source_count"], 1)
        self.assertEqual(row["confidence"], "medium")
        self.assertEqual(row["evidence_status"], "source_backed")
        self.assertEqual(row["body_link_count"], 1)
        self.assertEqual(row["weak_association_count"], 1)
        self.assertEqual(row["relation_count"], 0)
        self.assertTrue(row["stale_snapshot"])
        self.assertEqual(len(windows["stale_snapshot_queue"]), 1)
        self.assertEqual(len(windows["weak_association_signal_queue"]), 1)

    def test_current_signals_ignore_triple_dash_inside_frontmatter_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "works" / "example.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "\n".join(
                    [
                        "---",
                        "title: example",
                        "type: work",
                        "sources:",
                        "  - url: https://example.test/object---detail",
                        "source_count: 2",
                        "confidence: medium",
                        "evidence_status: externally_verified",
                        "---",
                        "",
                        "[Target](../publications/target.md)",
                    ]
                ),
                encoding="utf-8",
            )

            signals = ledger.read_current_signals(path)

        self.assertEqual(signals["source_count"], 2)
        self.assertEqual(signals["evidence_status"], "externally_verified")
        self.assertEqual(signals["body_link_count"], 1)

    def test_missing_historical_snapshot_fields_do_not_create_false_stale_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            triage = root / "automation" / "isolated-batch-105" / "triage.jsonl"
            triage.parent.mkdir(parents=True, exist_ok=True)
            triage.write_text(
                json.dumps({"unit": "events/example.md", "bucket": "valid_standalone"}) + "\n",
                encoding="utf-8",
            )
            self.write_unit(root, "events/example.md")

            rows = ledger.build_ledger_from_triage([triage], root / "04-knowledge" / "units")

        self.assertFalse(rows[0]["stale_snapshot"])
        self.assertEqual(rows[0]["unit_type"], "event")

    def test_mechanical_signal_queues_do_not_auto_adjudicate_relation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            triage = root / "automation" / "isolated-batch-100" / "triage.jsonl"
            self.write_triage(triage, "persons/example.md", "valid_standalone", source_count=1)
            self.write_unit(root, "persons/example.md")

            rows = ledger.build_ledger_from_triage([triage], root / "04-knowledge" / "units")
            windows = ledger.build_signal_queues(rows)

        self.assertEqual(len(windows["source_backed_no_relation_signal_queue"]), 1)
        forbidden = {"relation_type", "inverse_relation_type", "approved", "writeback"}
        self.assertTrue(forbidden.isdisjoint(rows[0]))
        self.assertTrue(forbidden.isdisjoint(windows["source_backed_no_relation_signal_queue"][0]))

    def test_latest_reviewed_ledger_decision_wins_by_numeric_batch_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            older = root / "automation" / "isolated-ledger-batch-98" / "isolated_unit_ledger.jsonl"
            newer = root / "automation" / "isolated-triage-batch-103" / "triage.jsonl"
            self.write_triage(older, "persons/example.md", "needs_minimum_relation_review")
            self.write_triage(newer, "persons/example.md", "valid_standalone")

            decisions = ledger.merge_reviewed_decisions([older, newer])

        self.assertEqual(decisions["persons/example.md"]["bucket"], "valid_standalone")
        self.assertEqual(decisions["persons/example.md"]["batch_number"], 103)

    def test_latest_reviewed_ledger_decision_prefers_newer_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            older = root / "automation" / "2026-06-02-isolated-ledger-batch-130" / "triage.jsonl"
            newer = root / "automation" / "2026-07-10-isolated-ledger-batch-118-preflight" / "triage.jsonl"
            self.write_triage(older, "persons/example.md", "needs_minimum_relation_review")
            self.write_triage(newer, "persons/example.md", "valid_standalone")

            decisions = ledger.merge_reviewed_decisions([newer, older])

        self.assertEqual(decisions["persons/example.md"]["bucket"], "valid_standalone")
        self.assertEqual(decisions["persons/example.md"]["batch_number"], 118)

    def test_discovered_reviewed_ledgers_use_outer_batch_order_and_exclude_prior_standalone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            automation = root / "automation"
            older = automation / "2026-07-17-isolated-review-batch-270" / "current-isolated-ledger" / "isolated_unit_ledger.jsonl"
            newer = automation / "2026-07-18-source-review-batch-278" / "reviewed-units.jsonl"
            self.write_triage(older, "persons/example.md", "valid_standalone")
            self.write_triage(newer, "persons/pending.md", "needs_source_review")
            self.write_unit(root, "persons/example.md")
            self.write_unit(root, "persons/pending.md")

            paths = ledger.discover_reviewed_ledger_paths(automation)
            decisions = ledger.merge_reviewed_decisions(paths)
            with patch.object(ledger, "all_units", return_value=["persons/example.md", "persons/pending.md"]):
                window, progress = ledger.next_isolated_review_window(
                    Path("missing.yml"), 10, decisions, root / "04-knowledge" / "units"
                )

        self.assertEqual(paths, [older, newer])
        self.assertEqual(decisions["persons/example.md"]["batch_number"], 270)
        self.assertEqual(window, ["persons/pending.md"])
        self.assertEqual(progress["excluded_valid_standalone"], 1)

    def test_next_window_excludes_only_reviewed_valid_standalone_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            units_dir = root / "04-knowledge" / "units"
            decisions = {
                "persons/standalone.md": {"unit": "persons/standalone.md", "bucket": "valid_standalone"},
                "persons/pending.md": {"unit": "persons/pending.md", "bucket": "needs_minimum_relation_review"},
                "persons/source-review.md": {"unit": "persons/source-review.md", "bucket": "needs_source_review"},
                "persons/formal-candidate.md": {"unit": "persons/formal-candidate.md", "bucket": "formal_relation_candidate"},
                "persons/minimal.md": {"unit": "persons/minimal.md", "bucket": "needs_minimal_relation"},
                "persons/boundary.md": {"unit": "persons/boundary.md", "bucket": "needs_identity_or_boundary_review"},
                "persons/duplicate.md": {"unit": "persons/duplicate.md", "bucket": "candidate_duplicate_or_merge"},
            }
            units = [
                "persons/standalone.md",
                "persons/pending.md",
                "persons/source-review.md",
                "persons/formal-candidate.md",
                "persons/minimal.md",
                "persons/boundary.md",
                "persons/duplicate.md",
                "persons/new-weak.md",
                "persons/new.md",
            ]
            self.write_unit(
                root,
                "persons/pending.md",
                weak_associations=[{"target": "../publications/context.md", "reason": "review"}],
            )
            self.write_unit(
                root,
                "persons/new-weak.md",
                weak_associations=[{"target": "../publications/context.md", "reason": "review"}],
            )

            with patch.object(ledger, "all_units", return_value=units):
                window, progress = ledger.next_isolated_review_window(
                    Path("missing.yml"),
                    7,
                    decisions,
                    units_dir=units_dir,
                )

        self.assertEqual(
            window,
            [
                "persons/pending.md",
                "persons/source-review.md",
                "persons/formal-candidate.md",
                "persons/minimal.md",
                "persons/boundary.md",
                "persons/duplicate.md",
                "persons/new.md",
            ],
        )
        self.assertEqual(progress["excluded_valid_standalone"], 1)
        self.assertEqual(progress["excluded_fresh_weak_associations"], 1)
        self.assertEqual(progress["retained_pending"], 6)
        self.assertEqual(progress["next_isolated_review_window"], 7)

    def test_current_window_filter_excludes_historical_non_isolated_rows(self):
        rows = [
            {"unit": "persons/current.md", "bucket": "valid_standalone"},
            {"unit": "persons/historical.md", "bucket": "valid_standalone"},
        ]

        filtered = ledger.filter_ledger_to_units(rows, ["persons/current.md"])

        self.assertEqual(filtered, [rows[0]])

    def test_explicit_window_retains_only_currently_isolated_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            window = Path(tmp) / "next-window.jsonl"
            window.write_text(
                "\n".join(
                    [
                        json.dumps({"unit": "persons/current.md"}),
                        json.dumps({"unit": "persons/historical.md"}),
                        json.dumps({"unit": "persons/current.md"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch.object(ledger, "isolated_units", return_value=["persons/current.md"]):
                units = ledger.explicit_isolated_window(window, Path("missing.yml"))

        self.assertEqual(units, ["persons/current.md"])

    def test_full_current_coverage_can_coexist_with_smaller_review_queue(self):
        rows = [
            {"unit": "persons/standalone.md", "bucket": "valid_standalone", "unit_type": "person"},
            {"unit": "persons/pending.md", "bucket": "needs_minimum_relation_review", "unit_type": "person"},
        ]
        decisions = {row["unit"]: row for row in rows}

        with patch.object(ledger, "all_units", return_value=[row["unit"] for row in rows]):
            review_window, progress = ledger.next_isolated_review_window(Path("missing.yml"), 2, decisions)
        uncovered, summary = ledger.coverage(rows, [row["unit"] for row in rows])

        self.assertEqual(review_window, ["persons/pending.md"])
        self.assertEqual(progress["next_isolated_review_window"], 1)
        self.assertEqual(summary["current_isolated_audit_window"], 2)
        self.assertEqual(uncovered, [])

    def test_progress_summary_keeps_mechanical_output_free_of_relation_writeback(self):
        decisions = {
            "persons/standalone.md": {"unit": "persons/standalone.md", "bucket": "valid_standalone"},
            "persons/pending.md": {"unit": "persons/pending.md", "bucket": "needs_minimum_relation_review"},
        }

        with patch.object(ledger, "all_units", return_value=list(decisions)):
            _, progress = ledger.next_isolated_review_window(Path("missing.yml"), 10, decisions)

        forbidden = {"relation_type", "inverse_relation_type", "approved", "writeback"}
        self.assertTrue(forbidden.isdisjoint(progress))

    def test_coverage_reports_current_window_buckets_separately_from_historical_rows(self):
        rows = [
            {"unit": "works/applied.md", "bucket": "formal_relation_candidate", "unit_type": "work"},
            {"unit": "works/deferred.md", "bucket": "needs_minimum_relation_review", "unit_type": "work"},
        ]

        _, summary = ledger.coverage(rows, ["works/deferred.md"])

        self.assertEqual(summary["by_bucket"], {"formal_relation_candidate": 1, "needs_minimum_relation_review": 1})
        self.assertEqual(summary["current_window_by_bucket"], {"needs_minimum_relation_review": 1})

    def write_triage(self, path: Path, unit: str, bucket: str, **overrides):
        path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "batch": path.parent.name,
            "unit": unit,
            "unit_type": unit.split("/", 1)[0].rstrip("s"),
            "bucket": bucket,
            "source_count": 1,
            "confidence": "medium",
            "evidence_status": "source_backed",
            "body_link_count": 0,
            "has_related": False,
            "rationale": "test",
            "recommended_action": "test",
        }
        row.update(overrides)
        path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    def write_unit(self, root: Path, rel: str, body: str = "", weak_associations=None):
        path = root / "04-knowledge" / "units" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        weak = weak_associations or []
        frontmatter = [
            "---",
            f"title: {path.stem}",
            f"type: {rel.split('/', 1)[0].rstrip('s')}",
            "source_count: 1",
            "confidence: medium",
            "evidence_status: source_backed",
        ]
        if weak:
            frontmatter.append("weak_associations:")
            for entry in weak:
                frontmatter.append(f"  - target: {entry['target']}")
                frontmatter.append(f"    reason: {entry['reason']}")
        frontmatter.extend(["---", "", body])
        path.write_text("\n".join(frontmatter), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
