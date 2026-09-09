#!/usr/bin/env python3
"""Fail-closed PreToolUse guard shared by Codex and Claude Code.

The hook only enforces repository-wide hard prohibitions. Operations that merely
need ordinary user approval stay in the clients' native permission systems.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shlex
import sys
from typing import Any


SHELL_DENY_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgit\s+push\b[^\n]*(?:--force(?:-with-lease)?\b|-f\b)", re.IGNORECASE), "force-push is prohibited by mainline-only governance"),
    (re.compile(r"\bgit\s+reset\b", re.IGNORECASE), "git reset is prohibited by repository policy"),
    (re.compile(r"\bgit\s+rm\b", re.IGNORECASE), "git rm is prohibited by repository policy"),
    (re.compile(r"\bgit\s+(?:checkout\s+(?:-[bB]\b|--orphan\b)|switch\s+(?:-[cC]\b|--(?:create|force-create)\b))", re.IGNORECASE), "creating Git branches is prohibited by mainline-only governance"),
    (re.compile(r"\bgit\s+branch\s+(?:-[dDmMcC]\b|--(?:delete|move|copy)\b|[^-\s][^\s]*)", re.IGNORECASE), "mutating Git branches is prohibited by mainline-only governance"),
    (re.compile(r"\bgit\s+update-ref\b[^\n]*(?:refs/heads/|HEAD\b)", re.IGNORECASE), "mutating Git branch refs is prohibited by mainline-only governance"),
    (re.compile(r"\bgit\s+worktree\s+(?:add|move|remove|prune)\b", re.IGNORECASE), "mutating Git worktrees is prohibited by mainline-only governance"),
    (re.compile(r"\bpython(?:3)?\s+scripts/(?:legacy_|migration_|phase[^/\s]*_migration|repair_|backfill_|normalize_|apply_|bulk_update_|merge_|rebuild_)[^\s]*\.py\b", re.IGNORECASE), "unreviewed bulk or legacy writer is prohibited"),
)

RM_COMMAND = re.compile(
    r"(?:^|[;&|])\s*(?:(?:sudo|command)\s+)?(?:/[\w./-]+/)?rm\s+([^\n;&|]*)",
    re.IGNORECASE,
)

SOURCES_DESTRUCTIVE_PATCH_MARKER = re.compile(
    r"^\*\*\*\s+(?:Update|Delete)\s+File:\s+(?:\./)?02-sources/",
    re.MULTILINE,
)


def _normalized_path(raw: object) -> str:
    if not isinstance(raw, str):
        return ""
    return raw.replace("\\", "/")


def _is_recursive_forced_rm(command: str) -> bool:
    for match in RM_COMMAND.finditer(command):
        try:
            tokens = shlex.split(match.group(1), posix=True)
        except ValueError:
            tokens = match.group(1).split()
        recursive = False
        forced = False
        for token in tokens:
            if token == "--":
                break
            if token == "--recursive":
                recursive = True
            elif token == "--force":
                forced = True
            elif token.startswith("-") and not token.startswith("--"):
                flags = token[1:]
                recursive = recursive or "r" in flags.lower()
                forced = forced or "f" in flags.lower()
        if recursive and forced:
            return True
    return False


def _is_sources_path(path: str) -> bool:
    return "/02-sources/" in f"/{path.lstrip('/')}" or path.endswith("/02-sources")


def _targets_read_only_sources(
    tool_name: str,
    tool_input: dict[str, Any],
    cwd: object,
) -> bool:
    if tool_name in {"Write", "Edit"}:
        path = _normalized_path(tool_input.get("file_path"))
        if not _is_sources_path(path):
            return False
        if tool_name == "Edit":
            return True
        target = Path(path)
        if not target.is_absolute():
            base = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
            target = base / target
        return target.exists()
    if tool_name == "apply_patch":
        command = str(tool_input.get("command") or "")
        return bool(SOURCES_DESTRUCTIVE_PATCH_MARKER.search(command))
    return False


def decision_for(payload: object) -> str | None:
    """Return a blocking reason, or ``None`` when native permissions may decide."""
    if not isinstance(payload, dict):
        return "hook input is not a JSON object"
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return "hook input is missing tool_input"

    if _targets_read_only_sources(tool_name, tool_input, payload.get("cwd")):
        return "02-sources is append-only: existing source files cannot be overwritten, edited, or deleted"

    if tool_name == "Bash":
        command = str(tool_input.get("command") or "")
        if _is_recursive_forced_rm(command):
            return "recursive forced deletion is prohibited"
        for pattern, reason in SHELL_DENY_RULES:
            if pattern.search(command):
                return reason
    return None


def deny_payload(reason: str) -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps(deny_payload(f"cannot validate tool call: {exc}"), ensure_ascii=False))
        return 0

    reason = decision_for(payload)
    if reason:
        print(json.dumps(deny_payload(reason), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
