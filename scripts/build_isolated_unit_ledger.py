#!/usr/bin/env python3
"""Build a consolidated isolated-unit governance ledger.

This script reads isolated-unit triage artifacts and the current relation index.
It does not mutate knowledge units, claims, relation frontmatter, or relation
facts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


BASE = Path(__file__).resolve().parents[1]
DEFAULT_AUTOMATION_ROOT = BASE / "06-runtime" / "automation"
DEFAULT_RELATION_INDEX = BASE / "04-knowledge" / "quality" / "relation-index.yml"
UNITS = BASE / "04-knowledge" / "units"
BATCH_RE = re.compile(r"batch-(\d+)")
DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")
FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
UNIT_DIRS = ["persons", "families", "institutions", "places", "works", "archives", "terms", "procedures", "events"]
PENDING_REVIEW_BUCKETS = {
    "needs_minimal_relation",
    "needs_minimum_relation_review",
    "needs_source_review",
    "formal_relation_candidate",
    "needs_identity_or_boundary_review",
    "candidate_duplicate_or_merge",
}


def repo_path(path: Path, base: Path = BASE) -> str:
    """Use a stable repository-relative path when possible."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(base.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_manifest_record(path: Path, base: Path = BASE) -> dict[str, Any]:
    return {
        "path": repo_path(path, base),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def complete_ku_state_digest(units_dir: Path = UNITS, base: Path = BASE) -> dict[str, Any]:
    """Digest every KU path and byte hash without inflating the manifest."""
    paths = sorted(
        path
        for directory_name in UNIT_DIRS
        for path in (units_dir / directory_name).rglob("*.md")
        if path.is_file()
    )
    digest = hashlib.sha256()
    total_bytes = 0
    for path in paths:
        relative_path = path.relative_to(units_dir).as_posix()
        file_hash = sha256_file(path)
        total_bytes += path.stat().st_size
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return {
        "root": repo_path(units_dir, base),
        "algorithm": "sha256(relative_path\\0sha256(file)\\n)",
        "file_count": len(paths),
        "total_bytes": total_bytes,
        "sha256": digest.hexdigest(),
    }


def build_generation_manifest(
    *,
    generator_path: Path,
    automation_root: Path,
    relation_index_path: Path,
    triage_paths: list[Path],
    reviewed_ledger_paths: list[Path],
    current_window_path: Path | None,
    units_dir: Path,
    output_paths: list[Path],
    original_argv: list[str],
    audit_window_limit: int,
    current_window_only: bool,
    base: Path = BASE,
) -> dict[str, Any]:
    """Describe every live dependency needed to reproduce this projection."""
    rebuild_command = [
        "python",
        repo_path(generator_path, base),
        "--automation-root",
        repo_path(automation_root, base),
        "--relation-index",
        repo_path(relation_index_path, base),
    ]
    if triage_paths:
        rebuild_command.extend(["--triage", *(repo_path(path, base) for path in triage_paths)])
    if reviewed_ledger_paths:
        rebuild_command.extend(
            ["--reviewed-ledger", *(repo_path(path, base) for path in reviewed_ledger_paths)]
        )
    rebuild_command.extend(["--out-dir", "{out_dir}", "--audit-window-limit", str(audit_window_limit)])
    if current_window_path is not None:
        rebuild_command.extend(["--current-window", repo_path(current_window_path, base)])
    if current_window_only:
        rebuild_command.append("--current-window-only")

    return {
        "schema_version": 1,
        "artifact_role": "isolated_unit_ledger_reproducibility_manifest",
        "generator": {
            **file_manifest_record(generator_path, base),
            "runtime": "Python >=3.10",
        },
        "invocation": {
            "original_command": ["python", repo_path(generator_path, base), *original_argv],
            "original_argv": original_argv,
            "rebuild_command": rebuild_command,
            "out_dir_placeholder": "{out_dir}",
        },
        "inputs": {
            "relation_index": file_manifest_record(relation_index_path, base),
            "triage": [file_manifest_record(path, base) for path in triage_paths],
            "reviewed_ledgers": [file_manifest_record(path, base) for path in reviewed_ledger_paths],
            "current_window": (
                file_manifest_record(current_window_path, base)
                if current_window_path is not None
                else None
            ),
            "ku_state": complete_ku_state_digest(units_dir, base),
        },
        "outputs": [file_manifest_record(path, base) for path in output_paths],
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            rows.append({"_parse_error": True, "line": line_no, "source_file": repo_path(path)})
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def artifact_directory(path: Path) -> Path:
    """Return the nearest dated batch directory for a runtime artifact."""
    for directory in (path.parent, *path.parents):
        if DATE_PREFIX.match(directory.name) and BATCH_RE.search(directory.name):
            return directory
    return path.parent


def batch_number(path: Path) -> int | None:
    match = BATCH_RE.search(artifact_directory(path).name)
    if not match:
        return None
    return int(match.group(1))


def artifact_sort_key(path: Path) -> tuple[str, int, str]:
    name = artifact_directory(path).name
    date_match = DATE_PREFIX.match(name)
    return (
        date_match.group(1) if date_match else "",
        batch_number(path) or -1,
        name,
    )


def discover_reviewed_ledger_paths(automation_root: Path) -> list[Path]:
    """Discover immutable reviewed-decision artifacts for active queue routing."""
    paths = {
        path.resolve(): path
        for pattern in ("*/reviewed-units.jsonl", "*/**/isolated_unit_ledger.jsonl")
        for path in automation_root.glob(pattern)
    }
    return sorted(paths.values(), key=artifact_sort_key)


def unique_sorted_paths(paths: list[Path]) -> list[Path]:
    unique = {path.resolve(): path for path in paths}
    return sorted(unique.values(), key=artifact_sort_key)


def read_current_signals(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "unit_exists": False,
            "source_count": None,
            "confidence": None,
            "evidence_status": None,
            "body_link_count": 0,
            "weak_association_count": 0,
            "relation_count": 0,
        }
    text = path.read_text(encoding="utf-8-sig")
    match = FRONTMATTER_RE.match(text)
    frontmatter = yaml.safe_load(match.group(1)) or {} if match else {}
    body = text[match.end():] if match else ""
    return {
        "unit_exists": True,
        "source_count": frontmatter.get("source_count"),
        "confidence": frontmatter.get("confidence"),
        "evidence_status": frontmatter.get("evidence_status"),
        "body_link_count": len(re.findall(r"\[[^\]]*\]\([^)]+\)", body)),
        "weak_association_count": len(frontmatter.get("weak_associations") or []),
        "relation_count": len(frontmatter.get("relations") or []),
    }


def build_ledger_from_triage(paths: list[Path], units_dir: Path = UNITS) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    latest_by_unit: dict[str, tuple[tuple[str, int, str, int], Path, int | None, dict[str, Any]]] = {}
    for path in sorted(paths, key=artifact_sort_key):
        batch_no = batch_number(path)
        for row in load_jsonl(path):
            if row.get("_parse_error"):
                rows.append(
                    {
                        "batch_number": batch_no,
                        "batch": path.parent.name,
                        "source_file": repo_path(path),
                        "parse_error": True,
                        "line": row.get("line"),
                    }
                )
                continue
            unit = row.get("unit")
            if not isinstance(unit, str) or not unit:
                continue
            row_batch_no = row.get("batch_number")
            if not isinstance(row_batch_no, int):
                row_batch_no = batch_no or 0
            candidate_key = (*artifact_sort_key(path), row_batch_no)
            previous = latest_by_unit.get(unit)
            if previous is not None and candidate_key < previous[0]:
                continue
            latest_by_unit[unit] = (candidate_key, path, batch_no, row)

    for unit, (_, path, batch_no, row) in latest_by_unit.items():
        historical = {
            "source_count": row.get("source_count"),
            "confidence": row.get("confidence"),
            "evidence_status": row.get("evidence_status"),
            "body_link_count": row.get("body_link_count"),
        }
        recorded_historical_keys = {key for key in historical if key in row}
        current = read_current_signals(units_dir / unit)
        rows.append(
            {
                "batch_number": batch_no,
                "batch": row.get("batch") or path.parent.name,
                "unit": unit,
                "unit_type": row.get("unit_type") or ("family" if unit.startswith("families/") else unit.split("/", 1)[0].rstrip("s")),
                "bucket": row.get("bucket") or row.get("decision") or "unknown",
                "historical_bucket": row.get("historical_bucket") or row.get("bucket") or row.get("decision") or "unknown",
                "historical_snapshot": historical,
                **current,
                "stale_snapshot": any(historical[key] != current[key] for key in recorded_historical_keys),
                "has_related": row.get("has_related"),
                "rationale": row.get("rationale"),
                "recommended_action": row.get("recommended_action"),
                "source_file": repo_path(path),
            }
        )
    rows.sort(key=lambda row: (row.get("batch_number") or 0, row.get("unit") or ""))
    return rows


def build_signal_queues(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    valid_rows = [row for row in rows if not row.get("parse_error")]
    return {
        "stale_snapshot_queue": [row for row in valid_rows if row.get("stale_snapshot")],
        "source_backed_no_relation_signal_queue": [
            row
            for row in valid_rows
            if (row.get("source_count") or 0) > 0
            and row.get("body_link_count") == 0
            and row.get("weak_association_count") == 0
            and row.get("relation_count") == 0
        ],
        "weak_association_signal_queue": [
            row
            for row in valid_rows
            if (row.get("weak_association_count") or 0) > 0
        ],
    }


def load_relation_index(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if isinstance(data, dict):
        data = data.get("relations", [])
    return [row for row in data if isinstance(row, dict)]


def all_units() -> list[str]:
    units: list[str] = []
    for dname in UNIT_DIRS:
        directory = UNITS / dname
        if not directory.exists():
            continue
        for path in directory.rglob("*.md"):
            units.append(str(path.relative_to(UNITS)).replace("\\", "/"))
    return sorted(units)


def isolated_units(relation_index_path: Path) -> list[str]:
    degrees: defaultdict[str, int] = defaultdict(int)
    for relation in load_relation_index(relation_index_path):
        source = relation.get("source")
        target = relation.get("target")
        if source:
            degrees[str(source)] += 1
        if target:
            degrees[str(target)] += 1
    return [unit for unit in all_units() if degrees.get(unit, 0) == 0]


def current_isolated_window(relation_index_path: Path, limit: int) -> list[str]:
    return isolated_units(relation_index_path)[:limit]


def explicit_isolated_window(path: Path, relation_index_path: Path) -> list[str]:
    """Read a saved review window while retaining only currently isolated KUs."""
    isolated = set(isolated_units(relation_index_path))
    seen: set[str] = set()
    window: list[str] = []
    for row in load_jsonl(path):
        unit = row.get("unit")
        if isinstance(unit, str) and unit in isolated and unit not in seen:
            window.append(unit)
            seen.add(unit)
    return window


def filter_ledger_to_units(rows: list[dict[str, Any]], units: list[str]) -> list[dict[str, Any]]:
    current = set(units)
    return [row for row in rows if row.get("unit") in current]


def merge_reviewed_decisions(paths: list[Path]) -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    decision_keys: dict[str, tuple[str, int, str]] = {}
    for path in sorted(paths, key=artifact_sort_key):
        path_batch_number = batch_number(path) or 0
        path_key = artifact_sort_key(path)
        for row in load_jsonl(path):
            unit = row.get("unit")
            if not isinstance(unit, str) or not unit:
                continue
            row_batch_number = row.get("batch_number")
            if not isinstance(row_batch_number, int):
                row_batch_number = path_batch_number
            candidate = {**row, "batch_number": row_batch_number, "source_file": repo_path(path)}
            candidate_key = (path_key[0], row_batch_number, path_key[2])
            if unit not in decisions or candidate_key >= decision_keys[unit]:
                decisions[unit] = candidate
                decision_keys[unit] = candidate_key
    return decisions


def next_isolated_review_window(
    relation_index_path: Path,
    limit: int,
    reviewed_decisions: dict[str, dict[str, Any]],
    units_dir: Path = UNITS,
) -> tuple[list[str], dict[str, int]]:
    isolated = isolated_units(relation_index_path)
    excluded = {
        unit
        for unit, row in reviewed_decisions.items()
        if row.get("bucket") == "valid_standalone"
    }
    retained_pending = {
        unit
        for unit, row in reviewed_decisions.items()
        if unit in isolated
        and row.get("bucket") in PENDING_REVIEW_BUCKETS
    }
    fresh_weak_associations = {
        unit
        for unit in isolated
        if unit not in reviewed_decisions
        and read_current_signals(units_dir / unit)["weak_association_count"] > 0
    }
    window = [
        unit
        for unit in isolated
        if unit not in excluded
        and (unit in retained_pending or unit not in fresh_weak_associations)
    ][:limit]
    return window, {
        "isolated_total": len(isolated),
        "excluded_valid_standalone": len(excluded.intersection(isolated)),
        "excluded_fresh_weak_associations": len(fresh_weak_associations),
        "retained_pending": len(retained_pending),
        "next_isolated_review_window": len(window),
    }


def discover_triage_paths(automation_root: Path, batch_min: int, batch_max: int) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(automation_root.glob("*/triage.jsonl")):
        batch_no = batch_number(path)
        if batch_no is None or not (batch_min <= batch_no <= batch_max):
            continue
        paths.append(path)
    return paths


def build_ledger(automation_root: Path, batch_min: int, batch_max: int) -> list[dict[str, Any]]:
    return build_ledger_from_triage(discover_triage_paths(automation_root, batch_min, batch_max))


def coverage(rows: list[dict[str, Any]], current_window: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    covered_units = {row.get("unit") for row in rows if not row.get("parse_error")}
    uncovered = [{"unit": unit} for unit in current_window if unit not in covered_units]
    by_bucket = Counter(row.get("bucket", "unknown") for row in rows if not row.get("parse_error"))
    current_window_units = set(current_window)
    current_window_by_bucket = Counter(
        row.get("bucket", "unknown")
        for row in rows
        if not row.get("parse_error") and row.get("unit") in current_window_units
    )
    by_type = Counter(row.get("unit_type", "unknown") for row in rows if not row.get("parse_error"))
    summary = {
        "current_isolated_audit_window": len(current_window),
        "ledger_rows": sum(1 for row in rows if not row.get("parse_error")),
        "covered_current_window": len(current_window) - len(uncovered),
        "remaining_uncovered_current_window": len(uncovered),
        "by_bucket": dict(by_bucket.most_common()),
        "current_window_by_bucket": dict(current_window_by_bucket.most_common()),
        "by_unit_type": dict(by_type.most_common()),
    }
    return uncovered, summary


def summary_markdown(summary: dict[str, Any], uncovered: list[dict[str, Any]], input_label: str) -> str:
    lines = [
        "# Isolated Unit Ledger Summary",
        "",
        f"Triage input: {input_label}",
        "",
        "## Totals",
        "",
        f"- Current isolated audit-window: {summary['current_isolated_audit_window']}",
        f"- Ledger rows: {summary['ledger_rows']}",
        f"- Covered current window: {summary['covered_current_window']}",
        f"- Remaining uncovered current window: {summary['remaining_uncovered_current_window']}",
        f"- Stale snapshots: {summary['signals']['stale_snapshot_queue']}",
        f"- Source-backed without relation signal: {summary['signals']['source_backed_no_relation_signal_queue']}",
        f"- Weak-association signals: {summary['signals']['weak_association_signal_queue']}",
        f"- Reviewed-decision inputs: {summary['progress']['reviewed_ledger_inputs']}",
        f"- Excluded reviewed valid-standalone units: {summary['progress']['excluded_valid_standalone']}",
        f"- Retained pending review units: {summary['progress']['retained_pending']}",
        f"- Next isolated review window: {summary['progress']['next_isolated_review_window']}",
        "",
        "## By Bucket",
        "",
        "| Bucket | Count |",
        "|---|---:|",
    ]
    for bucket, count in summary["by_bucket"].items():
        lines.append(f"| {bucket} | {count} |")
    lines.extend(["", "## Current Window By Bucket", "", "| Bucket | Count |", "|---|---:|"])
    for bucket, count in summary["current_window_by_bucket"].items():
        lines.append(f"| {bucket} | {count} |")
    lines.extend(["", "## By Unit Type", "", "| Unit type | Count |", "|---|---:|"])
    for unit_type, count in summary["by_unit_type"].items():
        lines.append(f"| {unit_type} | {count} |")
    lines.extend(["", "## Uncovered Current Window", ""])
    if uncovered:
        lines.extend(f"- `{row['unit']}`" for row in uncovered)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build isolated-unit governance ledger from triage batches.")
    parser.add_argument("--automation-root", type=Path, default=DEFAULT_AUTOMATION_ROOT)
    parser.add_argument("--relation-index", type=Path, default=DEFAULT_RELATION_INDEX)
    parser.add_argument("--triage", type=Path, nargs="+", help="explicit isolated-unit triage JSONL input(s)")
    parser.add_argument("--reviewed-ledger", type=Path, nargs="+", help="reviewed isolated ledgers or triage JSONL inputs")
    parser.add_argument(
        "--all-reviewed-ledgers",
        action="store_true",
        help="include all immutable reviewed-units and isolated-ledger artifacts for active queue routing",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--batch-min", type=int, default=47)
    parser.add_argument("--batch-max", type=int, default=47)
    parser.add_argument("--audit-window-limit", type=int, default=100)
    parser.add_argument(
        "--current-window",
        type=Path,
        help="explicit isolated review-window JSONL used for coverage and current-window filtering",
    )
    parser.add_argument(
        "--current-window-only",
        action="store_true",
        help="filter explicit triage rows to the current isolated audit window",
    )
    args = parser.parse_args()

    automation_root = args.automation_root if args.automation_root.is_absolute() else BASE / args.automation_root
    relation_index = args.relation_index if args.relation_index.is_absolute() else BASE / args.relation_index
    out_dir = args.out_dir if args.out_dir.is_absolute() else BASE / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    triage_paths = [
        path if path.is_absolute() else BASE / path
        for path in (args.triage or [])
    ]
    reviewed_ledger_paths = [
        path if path.is_absolute() else BASE / path
        for path in (args.reviewed_ledger or [])
    ]
    if args.all_reviewed_ledgers:
        reviewed_ledger_paths.extend(discover_reviewed_ledger_paths(automation_root))
    reviewed_ledger_paths = unique_sorted_paths(reviewed_ledger_paths)
    current_window_path = (
        args.current_window if args.current_window is None or args.current_window.is_absolute() else BASE / args.current_window
    )
    full_current_window = (
        explicit_isolated_window(current_window_path, relation_index)
        if current_window_path is not None
        else current_isolated_window(relation_index, args.audit_window_limit)
    )
    effective_triage_paths = triage_paths or discover_triage_paths(automation_root, args.batch_min, args.batch_max)
    ledger_rows = build_ledger_from_triage(effective_triage_paths)
    if args.current_window_only:
        ledger_rows = filter_ledger_to_units(ledger_rows, full_current_window)
    signal_queues = build_signal_queues(ledger_rows)
    reviewed_decisions = merge_reviewed_decisions(reviewed_ledger_paths)
    isolated_window, progress_summary = next_isolated_review_window(
        relation_index,
        args.audit_window_limit,
        reviewed_decisions,
    )
    progress_summary["reviewed_ledger_inputs"] = len(reviewed_ledger_paths)
    coverage_window = full_current_window if args.current_window_only else isolated_window
    uncovered, coverage_summary = coverage(ledger_rows, coverage_window)
    coverage_summary["signals"] = {name: len(rows) for name, rows in signal_queues.items()}
    coverage_summary["progress"] = progress_summary

    output_paths = [
        out_dir / "isolated_unit_ledger.jsonl",
        out_dir / "isolated_unit_uncovered.jsonl",
        out_dir / "next_isolated_review_window.jsonl",
        *(out_dir / f"{name}.jsonl" for name in signal_queues),
        out_dir / "isolated_unit_ledger_coverage.json",
        out_dir / "isolated_unit_ledger_summary.md",
    ]
    write_jsonl(output_paths[0], ledger_rows)
    write_jsonl(output_paths[1], uncovered)
    write_jsonl(output_paths[2], [{"unit": unit} for unit in isolated_window])
    for name, rows in signal_queues.items():
        write_jsonl(out_dir / f"{name}.jsonl", rows)
    (out_dir / "isolated_unit_ledger_coverage.json").write_text(
        json.dumps(coverage_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    input_label = ", ".join(path.relative_to(BASE).as_posix() for path in triage_paths) if triage_paths else f"batch range {args.batch_min}-{args.batch_max}"
    (out_dir / "isolated_unit_ledger_summary.md").write_text(
        summary_markdown(coverage_summary, uncovered, input_label),
        encoding="utf-8",
        newline="\n",
    )
    generation_manifest = build_generation_manifest(
        generator_path=Path(__file__),
        automation_root=automation_root,
        relation_index_path=relation_index,
        triage_paths=effective_triage_paths,
        reviewed_ledger_paths=reviewed_ledger_paths,
        current_window_path=current_window_path,
        units_dir=UNITS,
        output_paths=output_paths,
        original_argv=sys.argv[1:],
        audit_window_limit=args.audit_window_limit,
        current_window_only=args.current_window_only,
    )
    (out_dir / "generation-manifest.json").write_text(
        json.dumps(generation_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"ledger_rows={coverage_summary['ledger_rows']}")
    print(f"covered_current_window={coverage_summary['covered_current_window']}")
    print(f"remaining_uncovered_current_window={coverage_summary['remaining_uncovered_current_window']}")
    print(f"excluded_valid_standalone={progress_summary['excluded_valid_standalone']}")
    print(f"retained_pending={progress_summary['retained_pending']}")
    print(f"next_isolated_review_window={progress_summary['next_isolated_review_window']}")
    print(f"generation_manifest={out_dir / 'generation-manifest.json'}")
    print(f"written={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
