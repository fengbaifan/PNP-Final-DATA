#!/usr/bin/env python3
"""
audit_rule_drift.py — 规则漂移检测
=====================================
对比 AGENTS / skills / README 中的规则声明与磁盘事实，
检测文档与脚本事实之间的不一致。
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

import yaml


BASE = Path(__file__).resolve().parents[1]
AGENTS_LINE_BUDGET = 160
README_LINE_BUDGET = 190
DIRECT_BATCH_REFERENCE = re.compile(r"06-runtime/automation/[^`\s)]+/")
MAIN_FETCH_REFSPEC = "+refs/heads/main:refs/remotes/origin/main"
EXPECTED_ORIGIN_URL = "https://github.com/fengbaifan/PNP-Final-DATA.git"
DEPRECATED_UNIT_TYPES = {"ideas", "propositions", "arguments", "concepts", "techniques", "cases"}
CURRENT_UNIT_TYPES = {"person", "institution", "place", "work", "archive", "term", "procedure", "event"}
CURRENT_UNIT_DIRECTORIES = {f"{unit_type}s" for unit_type in CURRENT_UNIT_TYPES}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def literal_assignment(path: Path, name: str):
    tree = ast.parse(read_text(path))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return ast.literal_eval(node.value)
    return None


def mapping_assignment_keys(path: Path, name: str) -> set[str]:
    tree = ast.parse(read_text(path))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
            and isinstance(node.value, ast.Dict)
        ):
            return {ast.literal_eval(key) for key in node.value.keys}
    return set()


def check_agents_key_entries() -> list[dict]:
    """Check all key references listed in AGENTS.md §6 exist on disk."""
    agents = read_text(BASE / "AGENTS.md")
    findings: list[dict] = []

    # Extract all markdown file references from section 6.3
    refs_section = agents.split("### 6.3 关键细则")[1].split("---")[0] if "### 6.3 关键细则" in agents else ""
    for m in re.finditer(r"`([^`]+\.(md|json))`", refs_section):
        path_str = m.group(1)
        p = BASE / path_str
        if not p.exists():
            findings.append({
                "issue": "missing_referenced_file",
                "declared_in": "AGENTS.md §6.3",
                "path": path_str,
            })

    # Check section 6.1 references
    sec61 = agents.split("### 6.1 系统状态")[1].split("###")[0] if "### 6.1 系统状态" in agents else ""
    for m in re.finditer(r"`([^`]+\.(json|md))`", sec61):
        path_str = m.group(1)
        p = BASE / path_str
        if not p.exists():
            findings.append({
                "issue": "missing_referenced_file",
                "declared_in": "AGENTS.md §6.1",
                "path": path_str,
            })

    return findings


def check_current_agents_key_entries(base: Path = BASE) -> list[dict]:
    """Check file references in the current AGENTS key-entry section."""
    agents = read_text(base / "AGENTS.md")
    findings: list[dict] = []
    section = agents
    for match in re.finditer(r"`([^`]+\.(?:md|json))`", section):
        path_str = match.group(1)
        if any(token in path_str for token in ("<", ">", "*")):
            continue
        if not (base / path_str).exists():
            findings.append({
                "issue": "missing_referenced_file",
                "declared_in": "AGENTS.md key entries",
                "path": path_str,
            })
    return findings


def check_entrypoint_history_links(base: Path = BASE) -> list[dict]:
    findings: list[dict] = []
    for name in ("AGENTS.md", "README.md"):
        if DIRECT_BATCH_REFERENCE.search(read_text(base / name)):
            findings.append({"issue": "entrypoint_direct_batch_reference", "file": name})
    return findings


def check_sync_closure_contract(base: Path = BASE) -> list[dict]:
    closure = base / "scripts" / "run_sync_closure.py"
    if not closure.exists():
        return [{"issue": "sync_closure_missing", "script": "scripts/run_sync_closure.py"}]

    return []


def check_ci_sync_closure_contract(base: Path = BASE) -> list[dict]:
    """Require CI to rebuild generated snapshots before checking their Git diff."""
    workflow = base / ".github" / "workflows" / "quality.yml"
    if not workflow.exists():
        return [{"issue": "quality_workflow_missing", "file": ".github/workflows/quality.yml"}]

    commands = [
        line.strip()
        for line in read_text(workflow).splitlines()
        if "python scripts/run_sync_closure.py" in line
    ]
    if not commands:
        return [{"issue": "ci_sync_closure_command_missing", "file": ".github/workflows/quality.yml"}]

    required_flags = {"--refresh-generated", "--full", "--check-generated"}
    for command in commands:
        missing = sorted(flag for flag in required_flags if flag not in command.split())
        if missing:
            return [{
                "issue": "ci_sync_closure_command_invalid",
                "file": ".github/workflows/quality.yml",
                "missing": missing,
                "command": command,
            }]
    return []


def run_git_command(base: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=base, text=True, capture_output=True)
    return proc.stdout if proc.returncode == 0 else ""


def check_mainline_only_git_contract(
    base: Path = BASE,
    git_command: Callable[..., str] | None = None,
) -> list[dict]:
    if not (base / ".git").exists() and git_command is None:
        return []
    run = git_command or (lambda *args: run_git_command(base, *args))
    findings: list[dict] = []

    current_branch = run("rev-parse", "--abbrev-ref", "HEAD").strip()
    if current_branch != "main":
        findings.append({"issue": "current_branch_not_main", "branch": current_branch or "unknown"})

    local_refs = set(run("for-each-ref", "--format=%(refname)", "refs/heads").splitlines())
    for ref in sorted(local_refs - {"refs/heads/main"}):
        findings.append({"issue": "non_main_local_branch", "branch": ref})

    remote_refs = set(run("for-each-ref", "--format=%(refname)", "refs/remotes/origin").splitlines())
    allowed_remote_refs = {"refs/remotes/origin/HEAD", "refs/remotes/origin/main"}
    for ref in sorted(remote_refs - allowed_remote_refs):
        findings.append({"issue": "non_main_origin_tracking_branch", "branch": ref})

    worktree_count = sum(1 for line in run("worktree", "list", "--porcelain").splitlines() if line.startswith("worktree "))
    if worktree_count != 1:
        findings.append({"issue": "extra_worktree", "count": worktree_count})

    fetch_refspecs = set(run("config", "--get-all", "remote.origin.fetch").splitlines())
    if fetch_refspecs != {MAIN_FETCH_REFSPEC}:
        findings.append({"issue": "origin_fetch_not_main_only", "refspecs": sorted(fetch_refspecs)})

    origin_url = run("config", "--get", "remote.origin.url").strip()
    if origin_url != EXPECTED_ORIGIN_URL:
        findings.append({"issue": "origin_url_mismatch", "url": origin_url or "missing"})

    return findings


def check_active_reference_targets(base: Path = BASE) -> list[dict]:
    """Reject retired rules and missing explicit targets in active contracts."""
    findings: list[dict] = []
    agents_dir = base / ".agents"
    if not agents_dir.exists():
        return findings
    paths = [base / "AGENTS.md", base / "README.md", agents_dir / "pipeline.md"]
    paths += sorted((base / "01-domain").glob("*.md"))
    paths += sorted((agents_dir / "skills").glob("**/SKILL.md"))
    paths += sorted((agents_dir / "skills").glob("**/references/*.md"))
    paths += sorted((agents_dir / "guards").glob("*.md"))
    # Directory entrypoints are active rules too, not historical research records.
    paths += [base / name for name in (
        "03-processing/README.md", "04-knowledge/README.md",
        "04-knowledge/results/README.md", "06-runtime/README.md", "scripts/README.md",
        "04-knowledge/structure/hierarchy/index.md",
        "04-knowledge/structure/dimension-candidates.md",
        "04-knowledge/structure/taxonomy/type-candidates.md",
    )]
    paths += sorted((base / "04-knowledge/structure").glob("*/README.md"))
    for path in paths:
        if not path.is_file():
            continue
        text = read_text(path)
        relative = path.relative_to(base).as_posix()
        if "hierarchy-archive/" in text:
            findings.append({"issue": "active_reference_to_retired_hierarchy_archive", "file": relative})
        if "growth-protocol/" in text:
            findings.append({"issue": "active_reference_to_retired_growth_protocol", "file": relative})
        for script_ref in sorted(set(re.findall(r"scripts/[A-Za-z0-9_-]+\.py", text))):
            if not (base / script_ref).is_file():
                findings.append({"issue": "active_reference_to_missing_script", "file": relative, "path": script_ref})
        explicit_paths = set(re.findall(
            r"`((?:\.agents|01-domain|02-sources|03-processing|04-knowledge|05-outputs|06-runtime|scripts|tests)/[^`\s]+)`",
            text,
        ))
        for target in sorted(explicit_paths):
            target = target.split("#", 1)[0].rstrip(".,;:")
            if any(token in target for token in ("*", "<", ">", "{", "}")):
                continue
            if not (base / target).exists():
                findings.append({"issue": "active_reference_target_missing", "file": relative, "path": target})
        for target in sorted(set(re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", text))):
            if "://" in target or target.startswith("#") or any(c in target for c in "*<>{}"):
                continue
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).resolve().exists():
                findings.append({"issue": "active_markdown_link_missing", "file": relative, "path": target})
    return findings


def query_eval_knowledge_digest(base: Path, targets: list[str]) -> str:
    state: dict[str, str] = {}
    for target in sorted(set(targets)):
        path = base / target
        if path.is_file():
            state[target] = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    payload = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def check_query_eval_targets(base: Path = BASE) -> list[dict]:
    """Require fresh Agent query replay evidence against current knowledge targets."""
    path = base / "06-runtime" / "eval" / "query-eval-set.jsonl"
    if not path.exists():
        return [{"issue": "query_eval_set_missing", "file": path.relative_to(base).as_posix()}]
    findings: list[dict] = []
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            findings.append({"issue": "query_eval_json_invalid", "file": path.relative_to(base).as_posix(), "line": line_number})
            continue
        targets = list(record.get("expected_units", [])) + list(record.get("supporting_targets", []))
        for target in targets:
            parts = Path(target).parts
            if any(part in DEPRECATED_UNIT_TYPES for part in parts):
                findings.append({"issue": "query_eval_deprecated_unit_type", "path": target, "id": record.get("id")})
            if not (base / target).is_file():
                findings.append({"issue": "query_eval_unit_missing", "path": target, "id": record.get("id")})
        evaluation = record.get("evaluation")
        if not isinstance(evaluation, dict):
            findings.append({"issue": "query_eval_semantic_replay_missing", "id": record.get("id")})
            continue
        required = {"status", "reviewer_kind", "reviewer_id", "reviewed_at", "knowledge_state_digest", "must_include_verified", "forbidden_absent", "acceptance_boundary"}
        if required - set(evaluation):
            findings.append({"issue": "query_eval_semantic_replay_incomplete", "id": record.get("id")})
            continue
        if evaluation.get("status") not in {"accepted", "accepted_with_findings"} or evaluation.get("reviewer_kind") != "agent":
            findings.append({"issue": "query_eval_semantic_replay_invalid", "id": record.get("id")})
        if set(evaluation.get("must_include_verified") or []) != set(record.get("must_include_claims") or []):
            findings.append({"issue": "query_eval_required_claims_unreviewed", "id": record.get("id")})
        if set(evaluation.get("forbidden_absent") or []) != set(record.get("forbidden") or []):
            findings.append({"issue": "query_eval_forbidden_claims_unreviewed", "id": record.get("id")})
        if all((base / target).is_file() for target in targets):
            expected_digest = query_eval_knowledge_digest(base, targets)
            if evaluation.get("knowledge_state_digest") != expected_digest:
                findings.append({"issue": "query_eval_semantic_replay_stale", "id": record.get("id")})
    return findings


def check_structure_theme_targets(base: Path = BASE) -> list[dict]:
    """Reject retired KU directories and missing explicit KU links in formal themes."""
    findings: list[dict] = []
    theme_dir = base / "04-knowledge" / "structure" / "themes"
    if not theme_dir.exists():
        return findings
    target_pattern = re.compile(
        r"(?P<target>(?:\.\./\.\./units/)?(?:persons|institutions|places|works|archives|terms|procedures|events|ideas|propositions|arguments|concepts|techniques|cases)/[a-z0-9-]+\.md)"
    )
    for path in sorted(theme_dir.glob("*.md")):
        relative = path.relative_to(base).as_posix()
        for match in target_pattern.finditer(read_text(path)):
            target = match.group("target")
            parts = Path(target).parts
            if any(part in DEPRECATED_UNIT_TYPES for part in parts):
                findings.append({"issue": "theme_deprecated_unit_type", "file": relative, "path": target})
                continue
            normalized = target.split("units/", 1)[-1]
            if not (base / "04-knowledge" / "units" / normalized).is_file():
                findings.append({"issue": "theme_unit_missing", "file": relative, "path": target})
    return findings


def check_claim_registry_header(base: Path = BASE) -> list[dict]:
    path = base / "04-knowledge" / "quality" / "claim-registry.yml"
    text = read_text(path)
    declared = re.search(r"^# total: (\d+)$", text, re.MULTILINE)
    actual = len(re.findall(r"^- claim_id:", text, re.MULTILINE))
    if declared is None or int(declared.group(1)) != actual:
        return [{"issue": "claim_registry_total_mismatch", "file": path.relative_to(base).as_posix(), "declared": int(declared.group(1)) if declared else None, "actual": actual}]
    return []


def check_relation_schema_contract(base: Path = BASE) -> list[dict]:
    schema_path = base / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml"
    doc_path = schema_path.with_suffix(".md")
    if not schema_path.is_file():
        return [{"issue": "relation_schema_missing", "file": schema_path.relative_to(base).as_posix()}]
    try:
        data = yaml.safe_load(read_text(schema_path)) or {}
        raw_types = data.get("types") or []
        raw_legacy = data.get("legacy_generic_types") or []
        inverse = data.get("inverse") or {}
        if not isinstance(raw_types, list) or len(raw_types) != len(set(raw_types)):
            raise ValueError("controlled types must be a unique list")
        if not isinstance(raw_legacy, list) or set(raw_types) & set(raw_legacy):
            raise ValueError("legacy generic types must be a disjoint list")
        if not isinstance(inverse, dict):
            raise ValueError("inverse must be a mapping")
        unknown = (set(inverse) | set(inverse.values())) - set(raw_types)
        if unknown:
            raise ValueError(f"inverse references unknown types: {sorted(unknown)}")
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        return [{"issue": "relation_schema_invalid", "file": schema_path.relative_to(base).as_posix(), "detail": str(exc)}]

    findings: list[dict] = []
    if not doc_path.is_file() or "relation-types.yml" not in read_text(doc_path):
        findings.append({"issue": "relation_schema_doc_not_linked", "file": doc_path.relative_to(base).as_posix()})
    duplicate_pattern = re.compile(r"^(?:RELATION_TYPES|VALID_TYPES|INVERSE_MAP)\s*=\s*\{", re.MULTILINE)
    for relative in (
        "scripts/build_relation_index.py",
        "scripts/audit_relation_consistency.py",
        "scripts/audit_repo.py",
        "scripts/evidence_batch_runner.py",
    ):
        path = base / relative
        if path.is_file() and duplicate_pattern.search(read_text(path)):
            findings.append({"issue": "relation_schema_duplicated_in_code", "file": relative})
    return findings


def check_active_taxonomy_scripts(base: Path = BASE) -> list[dict]:
    """Keep active verification and queue scripts on the current eight-type taxonomy."""
    findings: list[dict] = []
    matcher_keys = mapping_assignment_keys(base / "scripts" / "verify_collect_wikidata.py", "TYPE_MATCHER")
    if matcher_keys != CURRENT_UNIT_TYPES:
        findings.append({"issue": "wikidata_matcher_taxonomy_drift", "script": "scripts/verify_collect_wikidata.py", "actual": sorted(matcher_keys)})
    wikipedia_aliases = literal_assignment(base / "scripts" / "verify_collect_wikipedia.py", "TYPE_ALIASES") or {}
    if not isinstance(wikipedia_aliases, dict) or set(wikipedia_aliases.values()) != CURRENT_UNIT_TYPES:
        findings.append({"issue": "wikipedia_collector_taxonomy_drift", "script": "scripts/verify_collect_wikipedia.py", "actual": sorted(set(wikipedia_aliases.values())) if isinstance(wikipedia_aliases, dict) else []})
    llm_types = set(literal_assignment(base / "scripts" / "audit_unverified_queue.py", "LLM_FIRST_TYPES") or [])
    direct_types = set(literal_assignment(base / "scripts" / "audit_unverified_queue.py", "DIRECT_TYPES") or [])
    if llm_types | direct_types != CURRENT_UNIT_DIRECTORIES or llm_types & direct_types:
        findings.append({"issue": "unverified_queue_taxonomy_drift", "script": "scripts/audit_unverified_queue.py", "actual": sorted(llm_types | direct_types)})
    return findings


def check_display_taxonomy_contract(base: Path = BASE) -> list[dict]:
    findings: list[dict] = []
    script = base / "scripts" / "build_knowledge_graph_data.py"
    colors = literal_assignment(script, "TYPE_COLORS")
    labels = literal_assignment(script, "TYPE_ZH")
    if set(colors or {}) != CURRENT_UNIT_TYPES or set(labels or {}) != CURRENT_UNIT_TYPES:
        findings.append({"issue": "knowledge_graph_taxonomy_drift", "script": script.relative_to(base).as_posix()})
    for relative in (
        ".agents/skills/compose/references/data-schema.md",
    ):
        path = base / relative
        text = read_text(path)
        if not all(unit_type in text for unit_type in CURRENT_UNIT_TYPES) or re.search(r"\b(?:concept|technique|case|idea)\b", text):
            findings.append({"issue": "knowledge_graph_document_taxonomy_drift", "file": relative})
    return findings


def check_output_file_back_contract(base: Path = BASE) -> list[dict]:
    try:
        from scripts.build_output_gallery import validate_output_metadata
    except ModuleNotFoundError:
        from build_output_gallery import validate_output_metadata

    return validate_output_metadata(base)


def check_knowledge_graph_direct_open_contract(base: Path = BASE) -> list[dict]:
    """Require the graph to carry a fully local file:// runtime and data path."""
    findings: list[dict] = []
    html_path = base / "05-outputs" / "knowledge-graph.html"
    builder_path = base / "scripts" / "build_knowledge_graph_data.py"
    closure_path = base / "scripts" / "run_sync_closure.py"
    html = read_text(html_path) if html_path.exists() else ""
    if 'src="knowledge-graph-data.js"' not in html:
        findings.append({"issue": "knowledge_graph_direct_data_script_missing", "file": "05-outputs/knowledge-graph.html"})
    d3_runtime = base / "05-outputs" / "vendor" / "d3.v7.9.0.min.js"
    if (
        'src="vendor/d3.v7.9.0.min.js"' not in html
        or not d3_runtime.exists()
    ):
        findings.append({"issue": "knowledge_graph_local_runtime_missing", "file": "05-outputs/knowledge-graph.html"})
    if re.search(r"(?:src|href)=[\"']https?://|@import\s+url\([\"']?https?://", html):
        findings.append({"issue": "knowledge_graph_remote_dependency_present", "file": "05-outputs/knowledge-graph.html"})
    if not builder_path.exists() or "render_data_script" not in read_text(builder_path):
        findings.append({"issue": "knowledge_graph_direct_data_generator_missing", "script": "scripts/build_knowledge_graph_data.py"})
    if not closure_path.exists() or '"05-outputs/knowledge-graph-data.js"' not in read_text(closure_path):
        findings.append({"issue": "knowledge_graph_direct_data_not_in_closure", "script": "scripts/run_sync_closure.py"})
    return findings


def check_knowledge_graph_version_contract(base: Path = BASE) -> list[dict]:
    """Require a D3-only current entry and validate the frozen 2D archive."""
    findings: list[dict] = []
    output_root = base / "05-outputs"
    required = (
        "knowledge-graph.html",
        "knowledge-graph-data.json",
        "knowledge-graph-data.js",
        "knowledge-graph-2d.html",
        "knowledge-graph-2d-data.json",
        "knowledge-graph-2d-data.js",
        "knowledge-graph-2d-manifest.json",
        "vendor/d3.v7.9.0.min.js",
    )
    for relative in required:
        if not (output_root / relative).is_file():
            findings.append({"issue": "knowledge_graph_version_artifact_missing", "path": f"05-outputs/{relative}"})

    forbidden = (
        "knowledge-graph-3d.html",
        "knowledge-graph-3d.js",
        "knowledge-graph-3d-manifest.json",
        "vendor/knowledge-graph-3d.bundle.js",
        "vendor/three.module.0.185.1.min.js",
        "vendor/three.core.min.js",
        "vendor/OrbitControls.0.185.1.js",
    )
    for relative in forbidden:
        if (output_root / relative).exists():
            findings.append({"issue": "knowledge_graph_3d_artifact_present", "path": f"05-outputs/{relative}"})

    main_entry = output_root / "knowledge-graph.html"
    if main_entry.is_file():
        main_html = read_text(main_entry)
        if '<svg id="graph"' not in main_html or '<canvas id="graph"' in main_html:
            findings.append({"issue": "knowledge_graph_main_not_2d", "path": "05-outputs/knowledge-graph.html"})

    for manifest_name in ("knowledge-graph-2d-manifest.json",):
        manifest_path = output_root / manifest_name
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(read_text(manifest_path))
        except (json.JSONDecodeError, OSError):
            findings.append({"issue": "knowledge_graph_manifest_invalid", "path": f"05-outputs/{manifest_name}"})
            continue
        declared = manifest.get("sha256")
        if not isinstance(declared, dict) or not declared:
            findings.append({"issue": "knowledge_graph_manifest_invalid", "path": f"05-outputs/{manifest_name}"})
            continue
        if manifest.get("hash_mode") != "sha256-lf-normalized-v1":
            findings.append({"issue": "knowledge_graph_manifest_hash_mode_invalid", "path": f"05-outputs/{manifest_name}"})
        for relative, expected in declared.items():
            target = (output_root / str(relative)).resolve()
            try:
                target.relative_to(output_root.resolve())
            except ValueError:
                findings.append({"issue": "knowledge_graph_manifest_path_escape", "path": f"05-outputs/{manifest_name}"})
                continue
            if not target.is_file():
                findings.append({"issue": "knowledge_graph_manifest_target_missing", "path": f"05-outputs/{relative}"})
                continue
            canonical_bytes = target.read_bytes().replace(b"\r\n", b"\n")
            actual = hashlib.sha256(canonical_bytes).hexdigest().upper()
            normalized = str(expected).removeprefix("sha256:").upper()
            if actual != normalized:
                findings.append({"issue": "knowledge_graph_manifest_hash_mismatch", "path": f"05-outputs/{relative}"})

    return findings


def check_entrypoint_version_consistency(base: Path = BASE) -> list[dict]:
    """A single project version is required; document declarations are optional."""
    project = re.search(r'^version\s*=\s*"(\d+\.\d+\.\d+)"', read_text(base / "pyproject.toml"), re.MULTILINE)
    if not project:
        return [{"issue": "project_version_missing", "file": "pyproject.toml"}]
    versions = {"project": project.group(1)}
    for name in ("AGENTS.md", "README.md"):
        text = read_text(base / name)
        declarations = re.findall(r"(?:当前版本[：:]\s*v?|项目初始化版本[：:]\s*|^# .*?v)(\d+\.\d+\.\d+)", text, re.MULTILINE)
        for index, value in enumerate(declarations):
            versions[f"{name}:{index}"] = value
    if len(set(versions.values())) != 1:
        return [{"issue": "entrypoint_version_mismatch", "versions": versions}]
    return []


def check_runtime_index_snapshot(base: Path = BASE) -> list[dict]:
    automation = base / "06-runtime" / "automation"
    index_path = automation / "index.md"
    if not index_path.exists():
        return [{"issue": "runtime_index_missing", "file": "06-runtime/automation/index.md"}]
    index = read_text(index_path)
    declared_dirs = re.search(r"Batch directories: `(\d+)`", index)
    declared_files = re.search(r"Files: `(\d+)`", index)
    if declared_dirs is None or declared_files is None:
        return [{"issue": "runtime_index_snapshot_missing", "file": "06-runtime/automation/index.md"}]
    actual_dirs = sum(1 for path in automation.iterdir() if path.is_dir())
    actual_files = sum(1 for path in automation.rglob("*") if path.is_file() and path != index_path)
    declared = {"directories": int(declared_dirs.group(1)), "files": int(declared_files.group(1))}
    actual = {"directories": actual_dirs, "files": actual_files}
    if declared != actual:
        return [{"issue": "runtime_index_snapshot_stale", "file": "06-runtime/automation/index.md", "declared": declared, "actual": actual}]
    return []


def check_output_navigation_snapshot(base: Path = BASE) -> list[dict]:
    health_path = base / "06-runtime" / "state" / "current-health.json"
    index_path = base / "05-outputs" / "index" / "index.md"
    if not health_path.exists() or not index_path.exists():
        return [{"issue": "output_navigation_snapshot_input_missing", "file": "05-outputs/index/index.md"}]
    health = json.loads(read_text(health_path))
    index = read_text(index_path)
    expected = {
        "知识元总数": health["summary"]["total_units"],
        "claim 数": health["claim_traceability"]["total_claims"],
        "relation 数": health["relation_health"]["relation_index_total"],
        "structural_health": health["structural_health"]["total"],
        "traceability": health["structural_health"]["traceability"],
    }
    expected = {label: value for label, value in expected.items()
                if label not in {"structural_health", "traceability"}
                or re.search(rf"\|\s*{re.escape(label)}\s*\|", index)}
    declared: dict[str, int | None] = {}
    for label in expected:
        match = re.search(rf"\|\s*{re.escape(label)}\s*\|\s*\*\*(\d+)(?:/\d+)?\*\*", index)
        declared[label] = int(match.group(1)) if match else None
    if declared != expected:
        return [{"issue": "output_navigation_snapshot_stale", "file": "05-outputs/index/index.md", "declared": declared, "expected": expected}]
    return []


def check_skill_coverage(base: Path = BASE) -> list[dict]:
    """Check all skills declared in AGENTS.md §4 have corresponding SKILL.md."""
    findings: list[dict] = []
    skill_names = set()

    # Collect all skill names from AGENTS.md §4
    agents = read_text(base / "AGENTS.md")
    skills_section = agents.split("## 四、技能与管线")[1].split("## 五、")[0] if "## 四、技能与管线" in agents else ""
    for m in re.finditer(r"`(\w+(?:-\w+)*)`", skills_section):
        skill_names.add(m.group(1))
    # Current entrypoint uses links, without depending on a numbered heading.
    skill_names.update(re.findall(r"\]\(\.agents/skills/([^/]+)/SKILL\.md\)", agents))

    # Also check skill-registry.json
    registry_path = base / "06-runtime" / "state" / "skill-registry.json"
    if registry_path.exists():
        try:
            registry = json.loads(read_text(registry_path))
            for name in registry.get("skills", {}):
                skill_names.add(name)
        except json.JSONDecodeError:
            findings.append({"issue": "corrupt_skill_registry_json"})

    declared_names: set[str] = set()
    for skill_file in (base / ".agents" / "skills").rglob("SKILL.md"):
        match = re.search(r"^name:\s*(.+?)\s*$", read_text(skill_file), re.MULTILINE)
        if match:
            declared_names.add(match.group(1))

    # Check each registered skill has one canonical frontmatter declaration.
    for name in sorted(skill_names):
        if name not in declared_names and name not in ("quality", "growth", "inspection"):
            findings.append({
                "issue": "skill_missing_skill_md",
                "skill": name,
            })

    return findings


def check_codex_core_layout(base: Path = BASE) -> list[dict]:
    """Reject redundant client systems; require the Codex entry and one Skill root."""
    findings: list[dict] = []
    for relative in ("AGENTS.md", ".agents/pipeline.md"):
        if not (base / relative).is_file():
            findings.append({"issue": "codex_core_missing", "path": relative})
    if not (base / ".agents/skills").is_dir():
        findings.append({"issue": "codex_skill_root_missing", "path": ".agents/skills"})
    for relative in (".claude", "CLAUDE.md", ".agents/settings.json", ".codex/hooks.json"):
        if (base / relative).exists():
            findings.append({"issue": "redundant_client_surface", "path": relative})
    return findings


def check_retired_surface_absence(base: Path = BASE) -> list[dict]:
    """Prevent retired control surfaces and duplicate skill histories from returning."""
    findings: list[dict] = []
    retired_paths = (
        ".agents/adapters",
        ".agents/skills/00-coordination/feedback-tracker",
        ".agents/skills/02-multisource",
        ".agents/skills/07-output/draft-outline",
        ".legacy",
        ".opencli",
        "docs/superpowers",
        "scripts/archive",
        "design-qa.md",
        "04-knowledge/quality/name-authority-index.yml",
        "04-knowledge/quality/semantic-profile-index.yml",
        "05-outputs/exports/units-index.jsonl",
        "scripts/build_units_index.py",
        "04-knowledge/process",
        "portable/run_tests.py",
    )
    for relative in retired_paths:
        path = base / relative
        has_retired_content = path.is_file()
        if path.is_dir():
            has_retired_content = any(
                child.is_file() and "__pycache__" not in child.parts
                for child in path.rglob("*")
            )
        if has_retired_content:
            findings.append({"issue": "retired_surface_present", "path": relative})

    for path in sorted((base / ".agents" / "skills").glob("**/CHANGELOG.md")):
        findings.append({
            "issue": "duplicate_skill_history_present",
            "path": path.relative_to(base).as_posix(),
        })
    return findings


def check_readme_structure(base: Path = BASE) -> list[dict]:
    """Check README.md directory structure matches disk."""
    findings: list[dict] = []
    readme = read_text(base / "README.md")

    # Extract directories mentioned in README
    for m in re.finditer(r"`(0\d-[^`]+)/`", readme):
        dir_name = m.group(1)
        p = base / dir_name
        if not p.exists():
            findings.append({
                "issue": "readme_dir_missing",
                "dir": dir_name,
            })

    return findings


def check_log_responsibility_boundaries(base: Path = BASE) -> list[dict]:
    """Check the single current verification log has an explicit success boundary."""
    findings: list[dict] = []
    verify_log = base / "04-knowledge" / "quality" / "verification-log.md"
    if not verify_log.exists() or "只记录成功提交" not in read_text(verify_log):
        findings.append({
            "issue": "verification_log_scope_unclear",
            "file": "04-knowledge/quality/verification-log.md",
        })

    return findings


def collect_findings(base: Path = BASE) -> list[dict]:
    findings: list[dict] = []

    findings.extend(check_current_agents_key_entries(base))
    findings.extend(check_skill_coverage(base))
    findings.extend(check_codex_core_layout(base))
    findings.extend(check_retired_surface_absence(base))
    findings.extend(check_readme_structure(base))
    findings.extend(check_log_responsibility_boundaries(base))
    findings.extend(check_entrypoint_history_links(base))
    findings.extend(check_active_reference_targets(base))
    findings.extend(check_query_eval_targets(base))
    findings.extend(check_structure_theme_targets(base))
    findings.extend(check_claim_registry_header(base))
    findings.extend(check_relation_schema_contract(base))
    findings.extend(check_active_taxonomy_scripts(base))
    findings.extend(check_display_taxonomy_contract(base))
    findings.extend(check_output_file_back_contract(base))
    findings.extend(check_knowledge_graph_direct_open_contract(base))
    findings.extend(check_knowledge_graph_version_contract(base))
    findings.extend(check_entrypoint_version_consistency(base))
    findings.extend(check_runtime_index_snapshot(base))
    findings.extend(check_output_navigation_snapshot(base))
    findings.extend(check_sync_closure_contract(base))
    findings.extend(check_ci_sync_closure_contract(base))
    findings.extend(check_mainline_only_git_contract(base))
    return findings


def main() -> int:
    findings = collect_findings()

    if findings:
        print(f"规则漂移: {len(findings)} 个问题")
        for f in findings:
            detail = f.get("path") or f.get("skill") or f.get("event") or f.get("file") or f.get("dir") or f.get("script") or "?"
            print(f"  [{f['issue']}] {detail}")
    else:
        print("规则漂移: 0 (所有规则文档与磁盘一致)")

    return len(findings)


if __name__ == "__main__":
    sys.exit(main())
