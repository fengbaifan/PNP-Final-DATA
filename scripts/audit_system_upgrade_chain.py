#!/usr/bin/env python3
"""Check the Codex stage contract and retained evidence/writeback boundaries."""
from __future__ import annotations
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import skill_registry
from scripts.audit_rule_drift import check_codex_core_layout

BASE = Path(__file__).resolve().parents[1]

@dataclass
class CheckResult:
    check: str
    status: str
    detail: str

def exit_code_for_summary(summary: dict) -> int:
    return 1 if summary.get("fail", 0) else 0

def run_checks(base: Path = BASE) -> list[CheckResult]:
    checks = []
    def read(name):
        path = base / name
        return path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    def check(name, condition, detail):
        checks.append(CheckResult(name, "pass" if condition else "fail", detail))
    check("Codex single entry", not check_codex_core_layout(base), "AGENTS + pipeline + one Skill root; no parallel client configuration")
    pipeline = read(".agents/pipeline.md")
    stages = ["| 1 摄入 |", "| 2 处理 |", "| 3 知识元 |", "| 4 对齐 |", "| 5 补足 |", "| 6 关系 |"]
    positions = [pipeline.find(stage) for stage in stages]
    check("six ordered stages", all(pos >= 0 for pos in positions) and positions == sorted(positions), "explicit stage order and handoffs")
    check("process and results separated", all(term in pipeline for term in ("process/", "results/", "唯一当前成果", "不创建空文件")), "separate process, stage result and canonical artifact")
    agents = read("AGENTS.md")
    check("all visible user messages recorded", all(term in agents for term in ("每次收到", "普通问答也记录", "user-revisions.md")), "user messages retained verbatim; interpretations separate")
    check("discovery deferred", "当前执行第一部分" in agents and "后续部分由用户明确启动" in agents, "no automatic discovery from KU or relation changes")
    registry = skill_registry.build_registry(base)
    expected = {"ingest": "current", "verify": "current", "enrich": "current", "relate": "current", "synthesize": "later", "compose": "later", "inspector": "support", "system-upgrade": "support"}
    check("non-overlapping skills", {k: v.get("phase") for k, v in registry.items()} == expected, "eight contracts with explicit phase applicability")
    check("skill contracts valid", not skill_registry.validate(registry, base), "unique names/triggers and valid direct references")
    ingest = read(".agents/skills/ingest/SKILL.md")
    check("semantic ingest retained", all(term in ingest for term in ("完整阅读", "source_assets", "processing_scope", "semantic_acceptance", "payload.knowledge_match")), "coverage, fingerprints and semantic acceptance remain distinct")
    relation = read(".agents/skills/relate/SKILL.md")
    check("relation evidence retained", all(term in relation for term in ("weak_associations", "exact apply plan", "方向", "证据", "不自动")), "no inferred relation promotion")
    verify = read("scripts/verify_apply_evidence.py")
    check("atomic evidence apply retained", all(term in verify for term in ("--state-file", "input_fingerprint", "_atomic_commit", 'run_state.complete("verify_apply")')), "preflight, fingerprints and atomic commit")
    runner = read("scripts/evidence_batch_runner.py")
    check("no implicit Git write", not any(token in runner for token in ('["git", "add"', '["git", "commit"', '["git", "push"')), "runner does not commit or push")
    closure = read("scripts/run_sync_closure.py")
    check("closeout does not discover", 'script("plan_relation_candidates.py")' not in closure and "refresh_generated: bool = False" in closure, "explicit projection refresh only")
    versions = [re.search(r"当前版本：v(\d+\.\d+\.\d+)", read(name)) for name in ("AGENTS.md", "README.md")]
    project = re.search(r'^version\s*=\s*"(\d+\.\d+\.\d+)"', read("pyproject.toml"), re.MULTILINE)
    values = [match.group(1) for match in [*versions, project] if match]
    check("versions agree", len(values) == 3 and len(set(values)) == 1, str(values))
    return checks

def main() -> int:
    checks = run_checks()
    summary = {"total_checks": len(checks), "pass": sum(c.status == "pass" for c in checks), "fail": sum(c.status == "fail" for c in checks)}
    summary["contract_checks_passed"] = not summary["fail"]
    print(json.dumps({"summary": summary, "checks": [asdict(c) for c in checks]}, ensure_ascii=False, indent=2))
    return exit_code_for_summary(summary)

if __name__ == "__main__":
    raise SystemExit(main())
