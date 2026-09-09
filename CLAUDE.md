@AGENTS.md

# Claude Code adapter

- `.agents/skills/` is the only semantic Skill authority. `.claude/skills/` contains flat discovery symlinks only; never edit Skill content through the adapter path.
- `.claude/settings.json` and `.codex/hooks.json` both call `scripts/agent_guard.py`; Markdown guards explain policy but do not replace executable enforcement.
- User-level instructions and auto memory are non-authoritative context. Recheck mutable facts against the current checkout before reporting or writing.
