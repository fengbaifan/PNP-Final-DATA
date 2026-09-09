from pathlib import Path
import tempfile
import unittest

from scripts import agent_guard


def bash(command: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


class AgentGuardTests(unittest.TestCase):
    def test_blocks_hard_destructive_shell_operations(self):
        for command in (
            "rm -rf build",
            " sudo /bin/rm -r -f build",
            "rm --recursive --force build",
            "git push --force origin main",
            "git reset --hard HEAD~1",
            "git rm tracked.md",
            "git switch -c feature",
            "git switch --create feature",
            "git branch --delete feature",
            "git update-ref refs/heads/feature HEAD",
            "git worktree add ../other feature",
            "python scripts/rebuild_everything.py",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(agent_guard.decision_for(bash(command)))

    def test_allows_read_only_shell_operations(self):
        for command in (
            "git status --short",
            "git branch --show-current",
            "rg --files 02-sources",
            "python scripts/audit_repo.py --summary",
        ):
            with self.subTest(command=command):
                self.assertIsNone(agent_guard.decision_for(bash(command)))

    def test_normal_push_is_left_to_native_approval(self):
        self.assertIsNone(agent_guard.decision_for(bash("git push origin main")))

    def test_blocks_generic_edits_to_read_only_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "02-sources" / "doc" / "source.md"
            source.parent.mkdir(parents=True)
            source.write_text("source", encoding="utf-8")
            write = {
                "cwd": temp_dir,
                "tool_name": "Write",
                "tool_input": {"file_path": "02-sources/doc/source.md"},
            }
            self.assertIsNotNone(agent_guard.decision_for(write))

        for operation in ("Update", "Delete"):
            patch = {
                "tool_name": "apply_patch",
                "tool_input": {"command": f"*** {operation} File: 02-sources/doc/source.md\n"},
            }
            self.assertIsNotNone(agent_guard.decision_for(patch))

    def test_registry_update_allows_absolute_paths(self):
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": "C:/repo/02-sources/source-registry.md"},
        }
        self.assertIsNone(agent_guard.decision_for(payload))

    def test_allows_updates_to_sources_registry_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = Path(temp_dir) / "02-sources" / "source-registry.md"
            registry.parent.mkdir(parents=True)
            registry.write_text("registry", encoding="utf-8")
            for tool_name in ("Write", "Edit"):
                payload = {
                    "cwd": temp_dir,
                    "tool_name": tool_name,
                    "tool_input": {"file_path": "02-sources/source-registry.md"},
                }
                self.assertIsNone(agent_guard.decision_for(payload))

        patch = {
            "tool_name": "apply_patch",
            "tool_input": {"command": "*** Update File: 02-sources/README.md\n"},
        }
        self.assertIsNone(agent_guard.decision_for(patch))

    def test_still_blocks_deletes_and_source_content_edits(self):
        patch = {
            "tool_name": "apply_patch",
            "tool_input": {"command": "*** Delete File: 02-sources/README.md\n"},
        }
        self.assertIsNotNone(agent_guard.decision_for(patch))
        for operation in ("Update", "Delete"):
            patch = {
                "tool_name": "apply_patch",
                "tool_input": {"command": f"*** {operation} File: 02-sources/doc/source.md\n"},
            }
            self.assertIsNotNone(agent_guard.decision_for(patch))

    def test_allows_new_source_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            write = {
                "cwd": temp_dir,
                "tool_name": "Write",
                "tool_input": {"file_path": "02-sources/doc/new-source.md"},
            }
            self.assertIsNone(agent_guard.decision_for(write))

        patch = {
            "tool_name": "apply_patch",
            "tool_input": {"command": "*** Add File: 02-sources/doc/new-source.md\n"},
        }
        self.assertIsNone(agent_guard.decision_for(patch))

    def test_allows_edits_outside_sources(self):
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": "/repo/AGENTS.md"},
        }
        self.assertIsNone(agent_guard.decision_for(payload))

    def test_malformed_input_fails_closed(self):
        self.assertIsNotNone(agent_guard.decision_for([]))
        self.assertIsNotNone(agent_guard.decision_for({"tool_name": "Bash"}))


if __name__ == "__main__":
    unittest.main()
