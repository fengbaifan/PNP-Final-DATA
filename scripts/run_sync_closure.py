#!/usr/bin/env python3
"""Run deterministic repository closeout checks without semantic writeback."""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


BASE = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
GENERATED_PATHS = [
    "04-knowledge/quality/relation-index.yml",
    "04-knowledge/quality/relation-candidates.yml",
    "04-knowledge/quality/translation-index.yml",
    "06-runtime/automation/index.md",
    "06-runtime/state/current-health.json",
    "06-runtime/state/skill-registry.json",
    "06-runtime/state/generated-projections-manifest.json",
    "06-runtime/state/candidate-index.jsonl",
    "06-runtime/state/discovery-manifest.json",
    "06-runtime/governance/governance-backlog.md",
]
PAGE_GENERATED_PATHS = [
    "05-outputs/knowledge-graph-data.json",
    "05-outputs/knowledge-graph-data.js",
]


@dataclass(frozen=True)
class Step:
    name: str
    command: list[str]


def script(name: str, *args: str) -> list[str]:
    return [PYTHON, f"scripts/{name}", *args]


def changed_paths_from_git(base: Path = BASE) -> set[str] | None:
    commands = (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    changed: set[str] = set()
    for command in commands:
        proc = subprocess.run(command, cwd=base, text=True, capture_output=True)
        if proc.returncode != 0:
            return None
        changed.update(line.replace("\\", "/") for line in proc.stdout.splitlines() if line.strip())
    return changed


def routed_audit_names(changed_paths: Iterable[str] | None) -> set[str]:
    """Return nearest-neighbour audits; unknown Git state fails open to all audits."""
    if changed_paths is None:
        return {"content", "relation", "repository"}
    paths = {path.replace("\\", "/") for path in changed_paths}
    names: set[str] = set()
    if any(path.startswith("04-knowledge/units/") for path in paths):
        names.update({"content", "relation", "repository"})
    if any(path.startswith("04-knowledge/quality/") for path in paths):
        names.update({"relation", "repository"})
    if any(path.startswith(("02-sources/", "03-processing/", "04-knowledge/structure/", "05-outputs/")) for path in paths):
        names.add("repository")
    if any(path in {"scripts/audit_content_quality.py"} for path in paths):
        names.update({"content", "repository"})
    if any(path in {"scripts/build_relation_index.py", "scripts/audit_relation_consistency.py", "scripts/_relation_schema.py"} for path in paths):
        names.update({"relation", "repository"})
    if any(path in {"scripts/audit_repo.py", "scripts/write_current_health.py", "scripts/generate_governance_backlog.py"} for path in paths):
        names.add("repository")
    return names


def build_steps(
    full: bool,
    check_generated: bool = False,
    refresh_generated: bool = False,
    refresh_page: bool = False,
    changed_paths: Iterable[str] | None = None,
) -> list[Step]:
    steps: list[Step] = []
    if refresh_generated:
        steps.extend(
            [
                Step("build relation index", script("build_relation_index.py")),
                Step("build runtime index", script("build_runtime_index.py")),
                Step("build translation index", script("build_translation_index.py")),
                Step("index existing candidates", script("build_discovery_index.py")),
                Step("export skill registry", script("skill_registry.py", "--export")),
                Step("write health and backlog", script("write_current_health.py")),
                Step("build generated projection manifest", script("build_generated_projection_manifest.py")),
            ]
        )
        if refresh_page:
            steps.insert(3, Step("build knowledge graph data", script("build_knowledge_graph_data.py")))
    if changed_paths is None:
        changed_paths = changed_paths_from_git()
    audit_names = {"content", "relation", "repository"} if full or refresh_generated else routed_audit_names(changed_paths)
    if "content" in audit_names:
        steps.append(Step("audit content quality", script("audit_content_quality.py")))
    if "relation" in audit_names:
        steps.append(Step("audit relation consistency", script("audit_relation_consistency.py")))
    if "repository" in audit_names:
        steps.append(Step("audit repository", script("audit_repo.py", "--summary")))
    steps.extend([
        Step("audit rule drift", script("audit_rule_drift.py")),
        Step("validate skill registry", script("skill_registry.py")),
        Step("check whitespace", ["git", "diff", "--check"]),
    ])
    if check_generated:
        generated_paths = [*GENERATED_PATHS, *PAGE_GENERATED_PATHS] if refresh_page else GENERATED_PATHS
        steps.append(
            Step(
                "check generated snapshots",
                ["git", "diff", "--exit-code", "HEAD", "--", *generated_paths],
            )
        )
    if full:
        steps.append(Step("audit system upgrade chain", script("audit_system_upgrade_chain.py")))
        steps.append(Step("run tests", [PYTHON, "-m", "pytest", "tests"]))
    return steps


def run_command(command: list[str]) -> int:
    return subprocess.run(command, cwd=BASE).returncode


def execute_steps(steps: list[Step], runner: Callable[[list[str]], int] = run_command) -> int:
    for index, step in enumerate(steps, 1):
        print(f"[{index}/{len(steps)}] {step.name}")
        code = runner(step.command)
        if code != 0:
            print(f"FAILED: {step.name} (exit={code})")
            return code
    print("sync closure passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="also run the full test suite")
    parser.add_argument(
        "--refresh-generated",
        action="store_true",
        help="refresh generated indexes and snapshots before validation",
    )
    parser.add_argument(
        "--check-generated",
        action="store_true",
        help="fail when deterministic generated snapshots differ from HEAD",
    )
    parser.add_argument(
        "--refresh-page",
        action="store_true",
        help="also refresh the paused website data projection",
    )
    args = parser.parse_args()
    if args.check_generated and not args.refresh_generated:
        parser.error("--check-generated requires --refresh-generated")
    if args.refresh_page and not args.refresh_generated:
        parser.error("--refresh-page requires --refresh-generated")
    return execute_steps(
        build_steps(
            full=args.full,
            check_generated=args.check_generated,
            refresh_generated=args.refresh_generated,
            refresh_page=args.refresh_page,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
