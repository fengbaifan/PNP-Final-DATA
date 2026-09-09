#!/usr/bin/env python3
"""Behavioral audit for the system-upgrade execution contract."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from scripts import skill_registry
except ImportError:  # pragma: no cover - direct script execution
    import skill_registry


BASE = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CheckResult:
    check: str
    status: str
    detail: str


def read_text(base: Path, relative: str) -> str:
    path = base / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def exit_code_for_summary(summary: dict) -> int:
    return 1 if summary.get("fail", 0) else 0


def _result(check: str, passed: bool, ok: str, failure: str) -> CheckResult:
    return CheckResult(check, "pass" if passed else "fail", ok if passed else failure)


def _declared_skill_names(base: Path) -> list[str]:
    names: list[str] = []
    for path in sorted((base / ".agents" / "skills").rglob("SKILL.md")):
        match = re.search(r"^name:\s*(.+?)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            names.append(match.group(1))
    return names


def run_checks(base: Path = BASE) -> list[CheckResult]:
    checks: list[CheckResult] = []
    required = [
        "AGENTS.md",
        ".agents/pipeline.md",
        ".agents/skills/00-coordination/system-upgrade/SKILL.md",
        ".agents/skills/00-coordination/system-upgrade/references/work-package-contract.md",
        ".agents/skills/08-inspection/system-review/SKILL.md",
        ".codex/hooks.json",
        ".claude/settings.json",
        "CLAUDE.md",
        "scripts/agent_guard.py",
        "scripts/run_sync_closure.py",
        "scripts/skill_registry.py",
    ]
    missing = [path for path in required if not (base / path).is_file()]
    checks.append(_result(
        "required upgrade contracts",
        not missing,
        "all current contracts exist",
        f"missing: {', '.join(missing)}",
    ))

    pipeline = read_text(base, ".agents/pipeline.md")
    checks.append(_result(
        "event routing replaces fixed pipeline",
        "三条工作循环" in pipeline and "五类事件路由" in pipeline and "P6.5" not in pipeline,
        "router defines loops and event routes without fixed stage numbering",
        "workflow router is missing loop/event semantics or still contains P6.5",
    ))

    processing_entry = read_text(base, "03-processing/README.md")
    checks.append(_result(
        "new processing uses the compact profile",
        "只保留五类工件" in processing_entry
        and "不是现行处理 profile" in processing_entry
        and "不作为新任务入口" in processing_entry,
        "new sources use five compact artifacts; legacy packages are history only",
        "the processing entry can still route new work into the legacy chapter artifact set",
    ))

    ingest = read_text(base, ".agents/skills/01-intake/ingest/SKILL.md")
    reconcile = read_text(base, ".agents/skills/05-quality/reconcile/SKILL.md")
    checks.append(_result(
        "duplicate and conflict screening is signal-routed",
        "payload.knowledge_match" in ingest and "没有冲突信号时不运行完整冲突裁决" in ingest and "无冲突信号不是本 Skill 的输入" in reconcile,
        "every source candidate is screened; full reconcile runs only on conflict signals",
        "candidate screening is absent or reconcile remains a mandatory fixed stage",
    ))

    hierarchy_contract = read_text(base, ".agents/skills/06-growth/build-hierarchy/SKILL.md")
    audit_source = read_text(base, "scripts/audit_repo.py")
    checks.append(_result(
        "hierarchy roles and attachment debt are explicit",
        "Level 3 theme" in hierarchy_contract and "topic_memberships" in hierarchy_contract and "Cluster" in hierarchy_contract and "hierarchy_assignment_check" in audit_source,
        "domain, dimension, theme, topic and KU roles are distinct; Cluster is discovery-only; missing attachment is measured",
        "hierarchy roles are mixed or the audit can hide missing KU attachment",
    ))

    names = _declared_skill_names(base)
    duplicates = sorted({name for name in names if names.count(name) > 1})
    checks.append(_result(
        "skill names are unique",
        not duplicates,
        f"{len(names)} declared names are unique",
        f"duplicates: {', '.join(duplicates)}",
    ))

    registry = skill_registry.build_registry(base)
    leaves = sum(entry.get("kind") == "leaf" for entry in registry.values())
    routers = sum(entry.get("kind") == "router" for entry in registry.values())
    checks.append(_result(
        "skill roles match the lean architecture",
        len(registry) == 18 and leaves == 18 and routers == 0,
        "18 active skills are classified as independent leaf workflows",
        f"found {len(registry)} skills: {leaves} leaf, {routers} router",
    ))

    claude_entry = read_text(base, "CLAUDE.md")
    codex_hooks = read_text(base, ".codex/hooks.json")
    claude_settings = read_text(base, ".claude/settings.json")
    checks.append(_result(
        "Codex and Claude use thin project adapters",
        "@AGENTS.md" in claude_entry
        and "scripts/agent_guard.py" in codex_hooks
        and "scripts/agent_guard.py" in claude_settings,
        "both clients share AGENTS and the executable guard without duplicating semantic rules",
        "project adapters do not share AGENTS.md and scripts/agent_guard.py",
    ))

    external_skills = skill_registry.external_skill_files(base)
    checks.append(_result(
        "repository has one active skill root",
        not external_skills,
        ".agents/skills is the only repository Skill root",
        "external SKILL.md files: " + ", ".join(
            path.relative_to(base).as_posix() for path in external_skills
        ),
    ))

    category_navigation = (
        ".agents/skills/05-quality/README.md",
        ".agents/skills/06-growth/README.md",
        ".agents/skills/07-output/README.md",
    )
    category_skill_files = (
        ".agents/skills/05-quality/SKILL.md",
        ".agents/skills/06-growth/SKILL.md",
        ".agents/skills/07-output/SKILL.md",
    )
    navigation_ok = (
        all((base / path).is_file() for path in category_navigation)
        and not any((base / path).exists() for path in category_skill_files)
    )
    checks.append(_result(
        "navigation categories are not runnable skills",
        navigation_ok,
        "quality, growth and output are README navigation categories",
        "a navigation README is missing or a retired aggregate SKILL.md still exists",
    ))

    active_contract = "\n".join(
        path.read_text(encoding="utf-8-sig")
        for path in sorted((base / ".agents" / "skills").rglob("*.md"))
    )
    retired_markers = (
        "GROWTH-PROTOCOL.md",
        "/loop 30d",
        "自动触发enrich",
        "synthesize → 知识库（新增theme）",
        "3+个来源一致 + 外部验证",
        "Wikipedia + Wikidata QID 双匹配 | `externally_verified`",
        "Concept / Technique / Idea 兜底",
    )
    present_markers = [marker for marker in retired_markers if marker in active_contract]
    checks.append(_result(
        "retired skill semantics stay absent",
        not present_markers,
        "fixed loops, implicit enrich and count-based promotion are absent",
        "retired markers: " + ", ".join(present_markers),
    ))

    registry_source = read_text(base, "scripts/skill_registry.py")
    checks.append(_result(
        "skill registry fails closed",
        "return 1" in registry_source and "raise SystemExit(main())" in registry_source,
        "registry returns non-zero when issues exist",
        "registry can report issues without failing",
    ))

    closure_source = read_text(base, "scripts/run_sync_closure.py")
    refresh_is_explicit = (
        "refresh_generated: bool = False" in closure_source
        and "if refresh_generated:" in closure_source
        and "--refresh-generated" in closure_source
    )
    checks.append(_result(
        "generated refresh is explicit",
        refresh_is_explicit,
        "default closure is read-only; generated refresh is opt-in",
        "closure still refreshes generated state implicitly",
    ))

    runner = read_text(base, "scripts/evidence_batch_runner.py")
    git_exec_tokens = ('["git", "add"', '["git", "commit"', '["git", "push"')
    checks.append(_result(
        "batch runner cannot perform git closeout",
        not any(token in runner for token in git_exec_tokens) and "def run_git_closeout" not in runner,
        "runner has no git add/commit/push executor",
        "runner still contains implicit git closeout",
    ))

    verify_apply = read_text(base, "scripts/verify_apply_evidence.py")
    checks.append(_result(
        "verification state is batch-local",
        "--state-file" in verify_apply
        and "input_fingerprint" in verify_apply
        and "_atomic_commit" in verify_apply
        and "run_state.complete(\"verify_apply\")" in verify_apply
        and "runtime-state.json" not in verify_apply,
        "verify apply fingerprints batch input, commits atomically and uses only batch-local state",
        "verify apply lacks fingerprint, atomic commit or truthful batch-local completion",
    ))

    work_package = read_text(
        base,
        ".agents/skills/00-coordination/system-upgrade/references/work-package-contract.md",
    )
    required_terms = ("candidate_id", "origin_type", "candidate_type", "evidence_refs", "reviewed_no_candidates")
    checks.append(_result(
        "candidate and file-back contract is traceable",
        all(term in work_package for term in required_terms),
        "unified candidate envelope and honest file-back state are present",
        "candidate envelope or file-back state is incomplete",
    ))

    relation_planner = read_text(base, "scripts/plan_relation_candidates.py")
    checks.append(_result(
        "relation discovery excludes formal pairs",
        "formal_pairs" in relation_planner and '"candidate_type": "relation"' in relation_planner,
        "relation candidates use the unified envelope and exclude already-formal pairs",
        "relation discovery can requeue formal pairs or lacks the candidate envelope",
    ))

    agents = read_text(base, "AGENTS.md")
    readme = read_text(base, "README.md")
    pyproject = read_text(base, "pyproject.toml")
    version_patterns = (
        re.search(r"当前版本：v(\d+\.\d+\.\d+)", agents),
        re.search(r"当前版本：v(\d+\.\d+\.\d+)", readme),
        re.search(r'^version\s*=\s*"(\d+\.\d+\.\d+)"', pyproject, re.MULTILINE),
    )
    versions = [match.group(1) for match in version_patterns if match]
    checks.append(_result(
        "entrypoint versions agree",
        len(versions) == 3 and len(set(versions)) == 1,
        f"version {versions[0] if versions else '?'} is consistent",
        f"versions found: {versions}",
    ))

    return checks


def main() -> int:
    checks = run_checks()
    summary = {
        "total_checks": len(checks),
        "pass": sum(item.status == "pass" for item in checks),
        "fail": sum(item.status == "fail" for item in checks),
    }
    summary["behavioral_ready"] = summary["fail"] == 0
    print(json.dumps({"summary": summary, "checks": [asdict(item) for item in checks]}, ensure_ascii=False, indent=2))
    return exit_code_for_summary(summary)


if __name__ == "__main__":
    raise SystemExit(main())
