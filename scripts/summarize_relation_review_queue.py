#!/usr/bin/env python3
"""Read-only summary for relation review queues.

This script does not change relation, claim, confidence, or consensus data.
It only reports current priority counts from the relation index and review
queue artifacts.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


BASE = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_DIR = BASE / "06-runtime" / "automation" / "2026-05-18-relation-review-queue"
RELATION_INDEX = BASE / "04-knowledge" / "quality" / "relation-index.yml"
AUTOMATION_DIR = BASE / "06-runtime" / "automation"
DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")
BATCH_NUMBER = re.compile(r"batch-(\d+)")

IGNORED_WEAK_TYPES = {"related_to", "involves_person", "relates_to_term", "relates_to_work"}


def artifact_sort_key(path: Path) -> tuple[str, int, str]:
    try:
        name = path.relative_to(AUTOMATION_DIR).parts[0]
    except (ValueError, IndexError):
        name = path.parent.name
    date_match = DATE_PREFIX.match(name)
    batch_match = BATCH_NUMBER.search(name)
    return (
        date_match.group(1) if date_match else "",
        int(batch_match.group(1)) if batch_match else -1,
        name,
    )


def isolated_ledger_sort_key(path: Path) -> tuple[str, int, str, int, str]:
    """Prefer the latest batch, then its final/current ledger over checkpoints."""
    parent_names = set(path.relative_to(AUTOMATION_DIR).parts[:-1])
    if "current-isolated-ledger" in parent_names:
        priority = 3
    elif "final-isolated-ledger" in parent_names:
        priority = 2
    elif "checkpoint" in " ".join(parent_names):
        priority = 0
    else:
        priority = 1
    return (*artifact_sort_key(path), priority, path.as_posix())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            rows.append({"_parse_error": True, "line": line_no})
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def load_relation_index() -> list[dict[str, Any]]:
    if not RELATION_INDEX.exists():
        return []
    data = yaml.safe_load(RELATION_INDEX.read_text(encoding="utf-8")) or []
    return [row for row in data if isinstance(row, dict)]


def relation_index_summary(relations: list[dict[str, Any]]) -> dict[str, Any]:
    weak_evidence = [
        row
        for row in relations
        if row.get("confidence") in {"low", "medium"}
        and not (row.get("evidence") or row.get("evidence_ref") or row.get("claim_id"))
        and row.get("relation_type") not in IGNORED_WEAK_TYPES
    ]
    weak_inference = [row for row in relations if row.get("review_status") == "weak_inference"]
    return {
        "relation_index_total": len(relations),
        "weak_evidence_count": len(weak_evidence),
        "weak_inference_count": len(weak_inference),
        "weak_evidence_by_relation_type": dict(Counter(row.get("relation_type", "unknown") for row in weak_evidence).most_common()),
        "weak_evidence_by_source_type": dict(Counter(row.get("source_type", "unknown") for row in weak_evidence).most_common()),
        "weak_inference_by_relation_type": dict(Counter(row.get("relation_type", "unknown") for row in weak_inference).most_common()),
    }


def queue_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    parse_errors = sum(1 for row in rows if row.get("_parse_error"))
    valid = [row for row in rows if not row.get("_parse_error")]
    return {
        "total": len(valid),
        "parse_errors": parse_errors,
        "by_bucket": dict(Counter(row.get("bucket", "unknown") for row in valid).most_common()),
        "by_relation_type": dict(Counter(row.get("relation_type", "unknown") for row in valid).most_common()),
        "by_source_type": dict(Counter(str(row.get("source", "")).split("/", 1)[0] or "unknown" for row in valid).most_common()),
    }


def triage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    parse_errors = sum(1 for row in rows if row.get("_parse_error"))
    valid = [row for row in rows if not row.get("_parse_error")]
    return {
        "total": len(valid),
        "parse_errors": parse_errors,
        "by_unit_type": dict(Counter(row.get("unit_type", "unknown") for row in valid).most_common()),
        "by_bucket": dict(Counter(row.get("bucket", "unknown") for row in valid).most_common()),
    }


def prescreen_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    parse_errors = sum(1 for row in rows if row.get("_parse_error"))
    valid = [row for row in rows if not row.get("_parse_error")]
    return {
        "total": len(valid),
        "parse_errors": parse_errors,
        "by_prescreen_bucket": dict(Counter(row.get("prescreen_bucket", "unknown") for row in valid).most_common()),
        "by_relation_type": dict(Counter(row.get("relation_type", "unknown") for row in valid).most_common()),
    }


def defer_summary(rows: list[dict[str, Any]], relations: list[dict[str, Any]]) -> dict[str, Any]:
    parse_errors = sum(1 for row in rows if row.get("_parse_error"))
    valid = [row for row in rows if not row.get("_parse_error")]
    relation_keys = {
        (row.get("source"), row.get("target"), row.get("relation_type"))
        for row in relations
    }
    presence = Counter(
        "present_in_relation_index"
        if (row.get("source"), row.get("target"), row.get("relation_type")) in relation_keys
        else "absent_from_relation_index"
        for row in valid
    )
    return {
        "total": len(valid),
        "parse_errors": parse_errors,
        "manual_semantic_review_count": sum(
            1 for row in valid if row.get("applied_action") == "manual_semantic_review_required"
        ),
        "by_batch": dict(Counter(row.get("batch", "unknown") for row in valid).most_common()),
        "by_bucket": dict(Counter(row.get("bucket", "unknown") for row in valid).most_common()),
        "by_relation_type": dict(Counter(row.get("relation_type", "unknown") for row in valid).most_common()),
        "by_applied_action": dict(Counter(row.get("applied_action", "unknown") for row in valid).most_common()),
        "by_relation_index_presence": dict(presence.most_common()),
    }


def latest_defer_ledger_summary() -> dict[str, Any]:
    ledger_paths = sorted(
        AUTOMATION_DIR.glob("*/defer_ledger.jsonl"),
        key=artifact_sort_key,
    )
    if not ledger_paths:
        return {
            "path": None,
            "detail_rows": 0,
            "aggregate_only_deferred": 0,
            "combined_adjudicated_defer_count": 0,
            "by_pair": {},
        }
    ledger_path = ledger_paths[-1]
    detail_rows = load_jsonl(ledger_path)
    aggregate_rows = load_jsonl(ledger_path.with_name("defer_ledger_aggregate.jsonl"))
    coverage_path = ledger_path.with_name("defer_ledger_normalized_coverage.json")
    coverage = {}
    if coverage_path.exists():
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            coverage = {"parse_error": True}
    aggregate_count = sum(int(row.get("deferred_count") or 0) for row in aggregate_rows if not row.get("_parse_error"))
    by_pair = Counter(
        f"{row.get('source_type', 'unknown')}->{row.get('target_type', 'unknown')}"
        for row in detail_rows
        if not row.get("_parse_error")
    )
    return {
        "path": str(ledger_path),
        "detail_rows": sum(1 for row in detail_rows if not row.get("_parse_error")),
        "aggregate_only_deferred": aggregate_count,
        "combined_adjudicated_defer_count": sum(1 for row in detail_rows if not row.get("_parse_error")) + aggregate_count,
        "by_pair": dict(by_pair.most_common()),
        "normalized_coverage": coverage,
    }


def latest_isolated_unit_ledger_summary() -> dict[str, Any]:
    ledger_paths = sorted(
        AUTOMATION_DIR.rglob("isolated_unit_ledger.jsonl"),
        key=isolated_ledger_sort_key,
    )
    if not ledger_paths:
        return {
            "path": None,
            "ledger_rows": 0,
            "current_isolated_audit_window": 0,
            "covered_current_window": 0,
            "remaining_uncovered_current_window": 0,
            "by_bucket": {},
        }
    ledger_path = ledger_paths[-1]
    rows = load_jsonl(ledger_path)
    coverage_path = ledger_path.with_name("isolated_unit_ledger_coverage.json")
    coverage: dict[str, Any] = {}
    if coverage_path.exists():
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            coverage = {"parse_error": True}
    by_bucket = Counter(
        row.get("bucket", "unknown")
        for row in rows
        if not row.get("_parse_error")
    )
    return {
        "path": str(ledger_path),
        "ledger_rows": sum(1 for row in rows if not row.get("_parse_error")),
        "current_isolated_audit_window": coverage.get("current_isolated_audit_window", 0),
        "covered_current_window": coverage.get("covered_current_window", 0),
        "remaining_uncovered_current_window": coverage.get("remaining_uncovered_current_window", 0),
        "by_bucket": coverage.get("current_window_by_bucket") or coverage.get("by_bucket") or dict(by_bucket.most_common()),
    }


def build_summary(queue_dir: Path) -> dict[str, Any]:
    relations = load_relation_index()
    return {
        "queue_dir": str(queue_dir),
        "relation_index": relation_index_summary(relations),
        "weak_relation_review_queue": queue_summary(load_jsonl(queue_dir / "weak_relation_review_queue.jsonl")),
        "isolated_unit_review_queue": triage_summary(load_jsonl(queue_dir / "isolated_unit_review_queue.jsonl")),
        "isolated_person_term_triage": triage_summary(load_jsonl(queue_dir / "isolated_person_term_triage.jsonl")),
        "isolated_unit_triage_batch_20": triage_summary(load_jsonl(queue_dir / "isolated_unit_triage_batch_20.jsonl")),
        "uses_procedure_prescreen": prescreen_summary(load_jsonl(queue_dir / "uses_procedure_prescreen.jsonl")),
        "relation_defer_queue": defer_summary(load_jsonl(queue_dir / "relation_defer_queue.jsonl"), relations),
        "latest_relation_defer_ledger": latest_defer_ledger_summary(),
        "latest_isolated_unit_ledger": latest_isolated_unit_ledger_summary(),
    }


def print_text(summary: dict[str, Any]) -> None:
    print("relation review queue summary")
    print(f"  queue_dir: {summary['queue_dir']}")
    idx = summary["relation_index"]
    print(f"  relation_index_total: {idx['relation_index_total']}")
    print(f"  weak_evidence_count: {idx['weak_evidence_count']}")
    print(f"  weak_inference_count: {idx['weak_inference_count']}")
    print("  weak_evidence_by_relation_type:")
    for key, value in idx["weak_evidence_by_relation_type"].items():
        print(f"    {key}: {value}")
    print("  weak_relation_review_queue:")
    for key, value in summary["weak_relation_review_queue"]["by_bucket"].items():
        print(f"    {key}: {value}")
    triage = summary["isolated_person_term_triage"]
    print("  isolated_person_term_triage:")
    for key, value in triage["by_bucket"].items():
        print(f"    {key}: {value}")
    batch_20 = summary["isolated_unit_triage_batch_20"]
    if batch_20["total"]:
        print("  isolated_unit_triage_batch_20:")
        for key, value in batch_20["by_bucket"].items():
            print(f"    {key}: {value}")
    prescreen = summary["uses_procedure_prescreen"]
    print("  uses_procedure_prescreen:")
    for key, value in prescreen["by_prescreen_bucket"].items():
        print(f"    {key}: {value}")
    defer = summary["relation_defer_queue"]
    print("  relation_defer_queue:")
    for key, value in defer["by_bucket"].items():
        print(f"    {key}: {value}")
    print(f"  manual_semantic_review_count: {defer['manual_semantic_review_count']}")
    print("  relation_defer_applied_action:")
    for key, value in defer["by_applied_action"].items():
        print(f"    {key}: {value}")
    print("  relation_defer_index_presence:")
    for key, value in defer["by_relation_index_presence"].items():
        print(f"    {key}: {value}")
    ledger = summary["latest_relation_defer_ledger"]
    if ledger["path"]:
        print("  latest_relation_defer_ledger:")
        print(f"    path: {ledger['path']}")
        print(f"    detail_rows: {ledger['detail_rows']}")
        print(f"    aggregate_only_deferred: {ledger['aggregate_only_deferred']}")
        print(f"    combined_adjudicated_defer_count: {ledger['combined_adjudicated_defer_count']}")
        coverage = ledger.get("normalized_coverage") or {}
        if coverage:
            print("    normalized_coverage:")
            print(f"      relation_index_migrated_total: {coverage.get('relation_index_migrated_total')}")
            print(f"      covered_by_normalized_detail_ledger: {coverage.get('covered_by_normalized_detail_ledger')}")
            print(f"      uncovered_migrated_total: {coverage.get('uncovered_migrated_total')}")
    isolated = summary.get("latest_isolated_unit_ledger") or {}
    if isolated.get("path"):
        print("  latest_isolated_unit_ledger:")
        print(f"    path: {isolated['path']}")
        print(f"    ledger_rows: {isolated['ledger_rows']}")
        print(f"    current_isolated_audit_window: {isolated['current_isolated_audit_window']}")
        print(f"    covered_current_window: {isolated['covered_current_window']}")
        print(f"    remaining_uncovered_current_window: {isolated['remaining_uncovered_current_window']}")
        print("    by_bucket:")
        for key, value in isolated.get("by_bucket", {}).items():
            print(f"      {key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize relation review queue artifacts without mutating repo data.")
    parser.add_argument("--queue-dir", type=Path, default=DEFAULT_QUEUE_DIR)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    queue_dir = args.queue_dir
    if not queue_dir.is_absolute():
        queue_dir = BASE / queue_dir
    summary = build_summary(queue_dir)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_text(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
