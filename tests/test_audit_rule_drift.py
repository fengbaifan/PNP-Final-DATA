import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import audit_rule_drift, pre_commit_check


class EntrypointDriftTests(unittest.TestCase):
    def make_root(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / ".agents").mkdir()
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / "scripts").mkdir()
        (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
        (root / "README.md").write_text("# README\n", encoding="utf-8")
        (root / "pyproject.toml").write_text('version = "0.0.0"\n', encoding="utf-8")
        (root / "scripts" / "run_sync_closure.py").write_text("# closure\n", encoding="utf-8")
        (root / ".github" / "workflows" / "quality.yml").write_text(
            "run: python scripts/run_sync_closure.py --refresh-generated --full --check-generated\n",
            encoding="utf-8",
        )
        (root / ".agents" / "settings.json").write_text(
            json.dumps({"permissions": {"confirm": ["Bash(python scripts/run_sync_closure.py *)"], "deny": []}}),
            encoding="utf-8",
        )
        return root

    def test_entrypoint_budget_rejects_oversized_agents(self):
        root = self.make_root()
        (root / "AGENTS.md").write_text("\n".join(["line"] * 161), encoding="utf-8")

        findings = audit_rule_drift.check_entrypoint_budgets(root)

        self.assertEqual(findings[0]["issue"], "agents_line_budget_exceeded")

    def test_entrypoint_history_links_reject_direct_batch_reference(self):
        root = self.make_root()
        (root / "README.md").write_text(
            "`06-runtime/automation/2026-06-01-example-batch-1/summary.md`\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_entrypoint_history_links(root)

        self.assertEqual(findings[0]["issue"], "entrypoint_direct_batch_reference")

    def test_active_reference_targets_reject_retired_rule_files(self):
        root = self.make_root()
        references = root / ".agents" / "skills" / "05-quality" / "lint" / "references"
        references.mkdir(parents=True)
        (references / "confidence.md").write_text("See hierarchy-archive/v5.md\n", encoding="utf-8")

        findings = audit_rule_drift.check_active_reference_targets(root)

        self.assertEqual({finding["issue"] for finding in findings}, {"active_reference_to_retired_hierarchy_archive"})

    def test_active_reference_targets_reject_missing_explicit_repository_path(self):
        root = self.make_root()
        references = root / ".agents" / "skills" / "07-output" / "query" / "references"
        references.mkdir(parents=True)
        (references / "contract.md").write_text(
            "Read `.agents/skills/07-output/SKILL.md`.\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_active_reference_targets(root)

        self.assertIn("active_reference_target_missing", {finding["issue"] for finding in findings})

    def test_query_eval_targets_reject_missing_and_deprecated_units(self):
        root = self.make_root()
        eval_dir = root / "06-runtime" / "eval"
        eval_dir.mkdir(parents=True)
        (eval_dir / "query-eval-set.jsonl").write_text(
            json.dumps({"id": "q001", "expected_units": ["04-knowledge/units/ideas/missing.md"]}) + "\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_query_eval_targets(root)

        issues = {finding["issue"] for finding in findings}
        self.assertIn("query_eval_deprecated_unit_type", issues)
        self.assertIn("query_eval_unit_missing", issues)
        self.assertIn("query_eval_semantic_replay_missing", issues)

    def test_query_eval_requires_fresh_agent_replay_digest(self):
        root = self.make_root()
        unit = root / "04-knowledge" / "units" / "terms" / "example.md"
        unit.parent.mkdir(parents=True)
        unit.write_text("current knowledge", encoding="utf-8")
        eval_dir = root / "06-runtime" / "eval"
        eval_dir.mkdir(parents=True)
        target = "04-knowledge/units/terms/example.md"
        record = {
            "id": "q001",
            "expected_units": [target],
            "must_include_claims": ["current"],
            "forbidden": ["invented"],
            "evaluation": {
                "status": "accepted",
                "reviewer_kind": "agent",
                "reviewer_id": "test-agent",
                "reviewed_at": "2026-08-03T00:00:00Z",
                "knowledge_state_digest": audit_rule_drift.query_eval_knowledge_digest(root, [target]),
                "must_include_verified": ["current"],
                "forbidden_absent": ["invented"],
                "acceptance_boundary": "test replay",
            },
        }
        (eval_dir / "query-eval-set.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

        self.assertEqual(audit_rule_drift.check_query_eval_targets(root), [])
        unit.write_text("changed knowledge", encoding="utf-8")
        findings = audit_rule_drift.check_query_eval_targets(root)
        self.assertIn("query_eval_semantic_replay_stale", {finding["issue"] for finding in findings})

    def test_entrypoint_versions_reject_mismatch(self):
        root = self.make_root()
        (root / "AGENTS.md").write_text(
            "# Knowledge Distillation v4.4.151\n\n- 当前版本：v4.4.152\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("> 当前版本：v4.4.152\n", encoding="utf-8")
        (root / "pyproject.toml").write_text('version = "4.4.152"\n', encoding="utf-8")

        findings = audit_rule_drift.check_entrypoint_version_consistency(root)

        self.assertEqual(findings[0]["issue"], "entrypoint_version_mismatch")

    def test_runtime_index_rejects_stale_snapshot(self):
        root = self.make_root()
        automation = root / "06-runtime" / "automation"
        batch = automation / "2026-07-10-example-batch-1"
        batch.mkdir(parents=True)
        (batch / "summary.md").write_text("# Summary\n", encoding="utf-8")
        (automation / "index.md").write_text(
            "- Batch directories: `0`\n- Files: `0`\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_runtime_index_snapshot(root)

        self.assertEqual(findings[0]["issue"], "runtime_index_snapshot_stale")

    def test_output_navigation_rejects_stale_snapshot(self):
        root = self.make_root()
        state = root / "06-runtime" / "state"
        output = root / "05-outputs" / "index"
        state.mkdir(parents=True)
        output.mkdir(parents=True)
        (state / "current-health.json").write_text(
            json.dumps({
                "summary": {"total_units": 2},
                "claim_traceability": {"total_claims": 3},
                "relation_health": {"relation_index_total": 4},
                "structural_health": {"total": 130, "traceability": 15},
            }),
            encoding="utf-8",
        )
        (output / "index.md").write_text(
            "| 知识元总数 | **1** | — |\n"
            "| claim 数 | **3** | — |\n"
            "| relation 数 | **4** | — |\n"
            "| health_score | **130/130** | — |\n"
            "| traceability | **15/15** | — |\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_output_navigation_snapshot(root)

        self.assertEqual(findings[0]["issue"], "output_navigation_snapshot_stale")

    def test_sync_closure_contract_rejects_deny_rule(self):
        root = self.make_root()
        (root / ".agents" / "settings.json").write_text(
            json.dumps({"permissions": {"confirm": [], "deny": ["Bash(python scripts/run_sync_closure.py *)"]}}),
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_sync_closure_contract(root)

        self.assertEqual(findings[0]["issue"], "sync_closure_denied")

    def test_ci_sync_closure_contract_rejects_missing_refresh(self):
        root = self.make_root()
        (root / ".github" / "workflows" / "quality.yml").write_text(
            "run: python scripts/run_sync_closure.py --full --check-generated\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_ci_sync_closure_contract(root)

        self.assertEqual(findings[0]["issue"], "ci_sync_closure_command_invalid")
        self.assertEqual(findings[0]["missing"], ["--refresh-generated"])

    def test_ci_sync_closure_contract_accepts_release_command(self):
        root = self.make_root()

        findings = audit_rule_drift.check_ci_sync_closure_contract(root)

        self.assertEqual(findings, [])

    def test_mainline_git_contract_rejects_extra_branch(self):
        root = self.make_root()
        outputs = {
            ("rev-parse", "--abbrev-ref", "HEAD"): "main\n",
            ("for-each-ref", "--format=%(refname)", "refs/heads"): "refs/heads/main\nrefs/heads/codex/example\n",
            ("for-each-ref", "--format=%(refname)", "refs/remotes/origin"): "refs/remotes/origin/HEAD\nrefs/remotes/origin/main\n",
            ("worktree", "list", "--porcelain"): "worktree C:/repo\nHEAD abc\nbranch refs/heads/main\n",
            ("config", "--get-all", "remote.origin.fetch"): "+refs/heads/main:refs/remotes/origin/main\n",
            ("config", "--get", "remote.origin.url"): "https://github.com/fengbaifan/PNP-Final-DATA.git\n",
        }

        findings = audit_rule_drift.check_mainline_only_git_contract(root, lambda *args: outputs[args])

        self.assertEqual(findings[0]["issue"], "non_main_local_branch")

    def test_mainline_git_contract_rejects_extra_worktree_and_wide_fetch(self):
        root = self.make_root()
        outputs = {
            ("rev-parse", "--abbrev-ref", "HEAD"): "main\n",
            ("for-each-ref", "--format=%(refname)", "refs/heads"): "refs/heads/main\n",
            ("for-each-ref", "--format=%(refname)", "refs/remotes/origin"): "refs/remotes/origin/HEAD\nrefs/remotes/origin/main\n",
            ("worktree", "list", "--porcelain"): "worktree C:/repo\nHEAD abc\nbranch refs/heads/main\n\nworktree C:/repo-wt\nHEAD def\nbranch refs/heads/main\n",
            ("config", "--get-all", "remote.origin.fetch"): "+refs/heads/*:refs/remotes/origin/*\n",
            ("config", "--get", "remote.origin.url"): "https://github.com/fengbaifan/PNP-Final-DATA.git\n",
        }

        findings = audit_rule_drift.check_mainline_only_git_contract(root, lambda *args: outputs[args])

        self.assertEqual({item["issue"] for item in findings}, {"extra_worktree", "origin_fetch_not_main_only"})

    def test_theme_targets_reject_deprecated_and_missing_units(self):
        root = self.make_root()
        themes = root / "04-knowledge" / "structure" / "themes"
        themes.mkdir(parents=True)
        (themes / "example.md").write_text(
            "- ../../units/concepts/old.md\n- ../../units/terms/missing.md\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_structure_theme_targets(root)

        self.assertEqual(
            {item["issue"] for item in findings},
            {"theme_deprecated_unit_type", "theme_unit_missing"},
        )

    def test_claim_registry_header_rejects_stale_total(self):
        root = self.make_root()
        quality = root / "04-knowledge" / "quality"
        quality.mkdir(parents=True)
        (quality / "claim-registry.yml").write_text(
            "# total: 1\n- claim_id: one\n- claim_id: two\n",
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_claim_registry_header(root)

        self.assertEqual(findings[0]["issue"], "claim_registry_total_mismatch")

    def test_relation_schema_rejects_unknown_inverse_type(self):
        root = self.make_root()
        references = root / ".agents" / "skills" / "01-intake" / "ingest" / "references"
        references.mkdir(parents=True)
        (references / "relation-types.yml").write_text(
            "types: [one]\nlegacy_generic_types: []\ninverse: {one: missing}\n",
            encoding="utf-8",
        )
        (references / "relation-types.md").write_text("See `relation-types.yml`.\n", encoding="utf-8")

        findings = audit_rule_drift.check_relation_schema_contract(root)

        self.assertEqual(findings[0]["issue"], "relation_schema_invalid")

    def test_settings_coverage_rejects_stale_script_and_mutable_scan_allow(self):
        root = self.make_root()
        (root / ".agents" / "settings.json").write_text(
            json.dumps({
                "permissions": {
                    "allow": ["Bash(python scripts/scan_sources.py *)"],
                    "confirm": ["Bash(python scripts/run_sync_closure.py *)"],
                    "deny": ["Bash(python scripts/missing.py *)"],
                }
            }),
            encoding="utf-8",
        )
        (root / "scripts" / "scan_sources.py").write_text("# scan\n", encoding="utf-8")

        findings = audit_rule_drift.check_settings_coverage(root)

        self.assertIn("stale_script_permission", {item["issue"] for item in findings})
        self.assertIn("mutable_scan_sources_allowed", {item["issue"] for item in findings})

    def test_retired_surface_absence_rejects_archive_and_skill_changelog(self):
        root = self.make_root()
        archive = root / "scripts" / "archive"
        archive.mkdir()
        (archive / "old.py").write_text("# retired\n", encoding="utf-8")
        skill = root / ".agents" / "skills" / "01-intake" / "ingest"
        skill.mkdir(parents=True)
        (skill / "CHANGELOG.md").write_text("# duplicate history\n", encoding="utf-8")

        findings = audit_rule_drift.check_retired_surface_absence(root)

        self.assertEqual(
            {item["issue"] for item in findings},
            {"retired_surface_present", "duplicate_skill_history_present"},
        )

    def test_pre_commit_wrapper_reuses_canonical_findings(self):
        with patch("scripts.audit_rule_drift.collect_findings", return_value=[]):
            self.assertEqual(pre_commit_check.main(), 0)
        with patch(
            "scripts.audit_rule_drift.collect_findings",
            return_value=[{"issue": "example", "path": "AGENTS.md"}],
        ):
            self.assertEqual(pre_commit_check.main(), 1)

    def test_knowledge_graph_direct_open_requires_data_script_and_closure(self):
        root = self.make_root()
        outputs = root / "05-outputs"
        outputs.mkdir()
        (outputs / "knowledge-graph.html").write_text("<html></html>\n", encoding="utf-8")
        (root / "scripts" / "build_knowledge_graph_data.py").write_text("# builder\n", encoding="utf-8")

        findings = audit_rule_drift.check_knowledge_graph_direct_open_contract(root)

        self.assertEqual(
            {item["issue"] for item in findings},
            {
                "knowledge_graph_direct_data_script_missing",
                "knowledge_graph_direct_data_generator_missing",
                "knowledge_graph_direct_data_not_in_closure",
                "knowledge_graph_local_runtime_missing",
            },
        )

    def test_knowledge_graph_direct_open_rejects_remote_dependencies(self):
        root = self.make_root()
        outputs = root / "05-outputs"
        vendor = outputs / "vendor"
        vendor.mkdir(parents=True)
        (vendor / "d3.v7.9.0.min.js").write_text("// local d3\n", encoding="utf-8")
        (outputs / "knowledge-graph.html").write_text(
            '<script src="vendor/d3.v7.9.0.min.js"></script>\n'
            '<script src="knowledge-graph-data.js"></script>\n'
            '<link href="https://example.com/font.css" rel="stylesheet">\n',
            encoding="utf-8",
        )
        (root / "scripts" / "build_knowledge_graph_data.py").write_text("def render_data_script(): pass\n", encoding="utf-8")
        (root / "scripts" / "run_sync_closure.py").write_text('"05-outputs/knowledge-graph-data.js"\n', encoding="utf-8")

        findings = audit_rule_drift.check_knowledge_graph_direct_open_contract(root)

        self.assertIn("knowledge_graph_remote_dependency_present", [item["issue"] for item in findings])

    def test_knowledge_graph_version_contract_rejects_3d_artifacts_and_hash_drift(self):
        root = self.make_root()
        outputs = root / "05-outputs"
        vendor = outputs / "vendor"
        vendor.mkdir(parents=True)
        files = {
            "knowledge-graph.html": b'<svg id="graph"></svg>',
            "knowledge-graph-data.json": b"{}",
            "knowledge-graph-data.js": b"data",
            "knowledge-graph-3d.html": b"removed renderer",
            "knowledge-graph-2d.html": b"two-d",
            "knowledge-graph-2d-data.json": b"{}",
            "knowledge-graph-2d-data.js": b"data",
            "vendor/d3.v7.9.0.min.js": b"d3",
        }
        for relative, content in files.items():
            path = outputs / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (outputs / "knowledge-graph-2d-manifest.json").write_text(
            json.dumps(
                {
                    "hash_mode": "sha256-lf-normalized-v1",
                    "sha256": {"knowledge-graph-2d.html": "wrong"},
                }
            ),
            encoding="utf-8",
        )
        findings = audit_rule_drift.check_knowledge_graph_version_contract(root)
        issues = {item["issue"] for item in findings}

        self.assertIn("knowledge_graph_3d_artifact_present", issues)
        self.assertIn("knowledge_graph_manifest_hash_mismatch", issues)

    def test_knowledge_graph_manifest_hash_is_eol_stable(self):
        root = self.make_root()
        outputs = root / "05-outputs"
        vendor = outputs / "vendor"
        vendor.mkdir(parents=True)
        files = {
            "knowledge-graph.html": b'<svg id="graph"></svg>',
            "knowledge-graph-data.json": b"{}",
            "knowledge-graph-data.js": b"data",
            "knowledge-graph-2d.html": b"two-d\r\nline\r\n",
            "knowledge-graph-2d-data.json": b"{}",
            "knowledge-graph-2d-data.js": b"data",
            "vendor/d3.v7.9.0.min.js": b"d3",
        }
        for relative, content in files.items():
            path = outputs / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        expected = hashlib.sha256(b"two-d\nline\n").hexdigest()
        (outputs / "knowledge-graph-2d-manifest.json").write_text(
            json.dumps(
                {
                    "hash_mode": "sha256-lf-normalized-v1",
                    "sha256": {"knowledge-graph-2d.html": expected},
                }
            ),
            encoding="utf-8",
        )

        findings = audit_rule_drift.check_knowledge_graph_version_contract(root)

        self.assertNotIn("knowledge_graph_manifest_hash_mismatch", {item["issue"] for item in findings})


if __name__ == "__main__":
    unittest.main()
