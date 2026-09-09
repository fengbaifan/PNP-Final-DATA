import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.audit_repo import rule_authority_check


class AgentProjectAdapterTests(unittest.TestCase):
    def make_root(self, root: Path) -> None:
        skill = root / ".agents" / "skills" / "01-intake" / "ingest"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: ingest\n---\n", encoding="utf-8")
        (root / ".agents" / "settings.json").write_text("{}\n", encoding="utf-8")
        (root / "scripts").mkdir()
        (root / "scripts" / "agent_guard.py").write_text("# guard\n", encoding="utf-8")
        (root / ".codex").mkdir()
        (root / ".codex" / "hooks.json").write_text(
            json.dumps({"command": "python scripts/agent_guard.py"}), encoding="utf-8"
        )
        (root / ".claude" / "skills").mkdir(parents=True)
        (root / ".claude" / "settings.json").write_text(
            json.dumps({"command": "python scripts/agent_guard.py"}), encoding="utf-8"
        )
        (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        (root / ".claude" / "skills" / "ingest").write_text(
            "../../.agents/skills/01-intake/ingest", encoding="utf-8"
        )

    def test_complete_adapters_are_accepted(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_root(root)
            result = rule_authority_check(root)
            self.assertEqual(result["adapter_issues"], [])
            self.assertTrue(result["codex_hooks_exists"])
            self.assertTrue(result["claude_skill_adapters_exist"])

    def test_wrong_skill_alias_is_reported(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_root(root)
            alias = root / ".claude" / "skills" / "ingest"
            alias.write_text("../../missing", encoding="utf-8")
            result = rule_authority_check(root)
            self.assertIn("Claude Skill adapter target mismatch: ingest", result["adapter_issues"])


if __name__ == "__main__":
    unittest.main()
