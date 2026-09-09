import tempfile
import unittest
import subprocess
import sys
import json
from pathlib import Path
from scripts.audit_repo import rule_authority_check
from scripts.audit_rule_drift import check_codex_core_layout

class CodexLayoutTests(unittest.TestCase):
    def test_audit_cli_runs_without_importing_as_package(self):
        root = Path(__file__).resolve().parents[1]
        run = subprocess.run([sys.executable, "scripts/audit_repo.py", "--summary"],
                             cwd=root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["rule_authority"]["client"], "codex")

    def make_root(self, directory):
        root = Path(directory)
        (root / ".agents/skills").mkdir(parents=True)
        (root / "AGENTS.md").write_text("Codex", encoding="utf-8")
        (root / ".agents/pipeline.md").write_text("stages", encoding="utf-8")
        return root

    def test_clean_checkout_needs_no_machine_local_adapters(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            result = rule_authority_check(root)
            self.assertEqual(result["adapter_issues"], [])
            self.assertEqual(result["hook_status"], "not_configured")
            self.assertEqual(result["client"], "codex")

    def test_redundant_client_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            (root / ".claude").mkdir()
            (root / ".agents/settings.json").write_text("{}", encoding="utf-8")
            self.assertEqual({f["path"] for f in check_codex_core_layout(root)}, {".claude", ".agents/settings.json"})

    def test_missing_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            (root / "AGENTS.md").unlink()
            self.assertIn("codex_core_missing", {f["issue"] for f in check_codex_core_layout(root)})
