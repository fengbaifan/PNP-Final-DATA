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
    # Mechanical contracts only. Semantic completeness is reviewed by reading.
    from scripts._accepted_knowledge import load_catalog
    from scripts.audit_rule_drift import check_entrypoint_version_consistency
    checks = []
    def check(name, issues):
        checks.append(CheckResult(name, "fail" if issues else "pass", str(issues) if issues else "valid"))
    check("Codex entry", check_codex_core_layout(base))
    try:
        registry = skill_registry.build_registry(base)
        check("Skill references and metadata", skill_registry.validate(registry, base))
    except (ValueError, OSError) as exc:
        check("Skill references and metadata", [str(exc)])
    try:
        load_catalog(base)
        check("Project input catalog", [])
    except (ValueError, OSError) as exc:
        check("Project input catalog", [str(exc)])
    check("Project version", check_entrypoint_version_consistency(base))
    return checks


def main() -> int:
    checks = run_checks()
    summary = {"total_checks": len(checks), "pass": sum(c.status == "pass" for c in checks), "fail": sum(c.status == "fail" for c in checks)}
    summary["contract_checks_passed"] = not summary["fail"]
    print(json.dumps({"summary": summary, "checks": [asdict(c) for c in checks]}, ensure_ascii=False, indent=2))
    return exit_code_for_summary(summary)

if __name__ == "__main__":
    raise SystemExit(main())
