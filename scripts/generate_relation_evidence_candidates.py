#!/usr/bin/env python3
"""Generate mechanical evidence signals for migrated relation review.

This script is read-only with respect to the knowledge base. It does not select
relation types or apply relation writeback.
"""
from __future__ import annotations

try:
    from scripts._relation_tables import load_relations
except ModuleNotFoundError:
    from _relation_tables import load_relations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


BASE = Path(__file__).resolve().parents[1]
DEFAULT_RELATION_INDEX = BASE / "04-knowledge" / "tables" / "relations.csv"


def load_yaml_rows(path: Path) -> list[dict[str, Any]]:
    data = load_relations(path)
    return [row for row in data if isinstance(row, dict)]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            row["_ledger_line"] = line_no
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def normalize_endpoint(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    return text.removeprefix("04-knowledge/units/").removeprefix("04-knowledge/")


def unit_path(root: Path, endpoint: str) -> Path:
    return root / "04-knowledge" / "units" / endpoint


def read_unit(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8-sig")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    return yaml.safe_load(parts[1]) or {}, parts[2]


def linked_endpoints(body: str, current_endpoint: str) -> set[str]:
    current_dir = Path(current_endpoint).parent
    links: set[str] = set()
    for raw in re.findall(r"\[[^\]]*\]\(([^)#]+)", body):
        raw = raw.strip().replace("\\", "/")
        if "://" in raw:
            continue
        path = Path(raw)
        if raw.startswith("../"):
            normalized = (current_dir / path).as_posix()
        else:
            normalized = path.as_posix()
        parts: list[str] = []
        for part in normalized.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        links.add(normalize_endpoint("/".join(parts)))
    return links


def evidence_refs(value: Any) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("evidence_ref"), dict):
            refs.append(value["evidence_ref"])
        if value.get("source_file"):
            refs.append(value)
        for nested in value.values():
            refs.extend(evidence_refs(nested))
    elif isinstance(value, list):
        for nested in value:
            refs.extend(evidence_refs(nested))
    return refs


def first_resolvable_evidence_ref(frontmatter: dict[str, Any], root: Path) -> dict[str, Any] | None:
    for ref in evidence_refs(frontmatter.get("sources", [])):
        source_file = ref.get("source_file")
        if source_file and (root / str(source_file)).is_file():
            return ref
    return None


def ledger_map(rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    result: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (normalize_endpoint(row.get("source")), normalize_endpoint(row.get("target")))
        result.setdefault(key, []).append(row)
    return result


def build_candidates(
    relation_rows: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
    root: Path = BASE,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    history = ledger_map(ledger_rows)
    for index, relation in enumerate(relation_rows, 1):
        if relation.get("relation_source") != "migrated_from_related":
            continue
        source = normalize_endpoint(relation.get("source"))
        target = normalize_endpoint(relation.get("target"))
        source_path = unit_path(root, source)
        target_path = unit_path(root, target)
        row = {
            "candidate_id": f"relation-evidence-{index:04d}",
            "source": source,
            "source_type": relation.get("source_type"),
            "target": target,
            "target_type": relation.get("target_type"),
            "legacy_relation_type": relation.get("relation_type"),
            "relation_source": relation.get("relation_source"),
            "review_status": relation.get("review_status"),
            "historical_defer": history.get((source, target), []),
        }
        reasons: list[str] = []
        if not source_path.is_file():
            reasons.append("source_endpoint_missing")
        if not target_path.is_file():
            reasons.append("target_endpoint_missing")
        if reasons:
            row["blocker_reasons"] = reasons
            blockers.append(row)
            continue
        source_fm, source_body = read_unit(source_path)
        target_fm, target_body = read_unit(target_path)
        source_ref = first_resolvable_evidence_ref(source_fm, root)
        target_ref = first_resolvable_evidence_ref(target_fm, root)
        row["signals"] = {
            "source_body_links_target": target in linked_endpoints(source_body, source),
            "target_body_links_source": source in linked_endpoints(target_body, target),
            "source_evidence_ref_resolvable": source_ref is not None,
            "target_evidence_ref_resolvable": target_ref is not None,
            "source_evidence_ref": source_ref,
            "target_evidence_ref": target_ref,
        }
        candidates.append(row)
    return candidates, blockers


def unordered_pair(row: dict[str, Any]) -> tuple[str, str]:
    return tuple(sorted((normalize_endpoint(row.get("source")), normalize_endpoint(row.get("target")))))


def build_canonical_queues(
    relation_rows: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    queues: dict[str, list[dict[str, Any]]] = {
        "canonical_strong": [],
        "canonical_fresh": [],
        "canonical_historical_defer": [],
        "excluded_existing_pair": [],
        "excluded_mirror": [],
        "defer_signal": [],
        "blockers": [],
    }
    explicit_pairs = {
        unordered_pair(row)
        for row in relation_rows
        if row.get("relation_source") == "explicit"
    }
    seen_pairs: set[tuple[str, str]] = set()
    for row in sorted(candidates, key=lambda item: (unordered_pair(item), str(item.get("candidate_id", "")))):
        pair = unordered_pair(row)
        if pair[0] == pair[1]:
            blocker = dict(row)
            blocker["blocker_reasons"] = ["self_link"]
            queues["blockers"].append(blocker)
            continue
        if pair in explicit_pairs:
            queues["excluded_existing_pair"].append(row)
            continue
        if pair in seen_pairs:
            queues["excluded_mirror"].append(row)
            continue
        seen_pairs.add(pair)
        signals = row.get("signals", {})
        if (
            signals.get("source_body_links_target")
            and signals.get("target_body_links_source")
            and signals.get("source_evidence_ref_resolvable")
        ):
            queues["canonical_strong"].append(row)
            if row.get("historical_defer"):
                queues["canonical_historical_defer"].append(row)
            else:
                queues["canonical_fresh"].append(row)
        else:
            queues["defer_signal"].append(row)
    return queues


def summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Relation Evidence Candidate Preflight",
        "",
        "## Results",
        "",
        f"- Migrated relation coverage: {summary['migrated_relation_coverage']}",
        f"- Candidate queue: {summary['candidate_count']}",
        f"- Blocker queue: {summary['blocker_count']}",
        f"- Bidirectional body-link signal: {summary['bidirectional_body_link_count']}",
        f"- Resolvable source evidence ref: {summary['source_evidence_ref_resolvable_count']}",
    ]
    if "canonical_strong_count" in summary:
        lines.extend(
            [
                f"- Canonical strong window: {summary['canonical_strong_count']}",
                f"- Canonical fresh review window: {summary['canonical_fresh_count']}",
                f"- Canonical historical-defer window: {summary['canonical_historical_defer_count']}",
                f"- Excluded existing explicit pair: {summary['excluded_existing_pair_count']}",
                f"- Excluded mirror residual: {summary['excluded_mirror_count']}",
                f"- Deferred mechanical signal: {summary['defer_signal_count']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Mechanical signal extraction only.",
            "- No relation type selection, semantic adjudication, or writeback.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--relation-index", type=Path, default=DEFAULT_RELATION_INDEX)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--canonical-strong-window", action="store_true")
    args = parser.parse_args()
    relation_index = args.relation_index if args.relation_index.is_absolute() else BASE / args.relation_index
    ledger = args.ledger if args.ledger.is_absolute() else BASE / args.ledger
    out_dir = args.out_dir if args.out_dir.is_absolute() else BASE / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    relation_rows = load_yaml_rows(relation_index)
    migrated = [row for row in relation_rows if row.get("relation_source") == "migrated_from_related"]
    candidates, blockers = build_candidates(relation_rows, load_jsonl(ledger))
    write_jsonl(out_dir / "candidate_queue.jsonl", candidates)
    write_jsonl(out_dir / "blocker_queue.jsonl", blockers)
    summary = {
        "migrated_relation_total": len(migrated),
        "migrated_relation_coverage": f"{len(candidates) + len(blockers)}/{len(migrated)}",
        "candidate_count": len(candidates),
        "blocker_count": len(blockers),
        "bidirectional_body_link_count": sum(
            1
            for row in candidates
            if row["signals"]["source_body_links_target"] and row["signals"]["target_body_links_source"]
        ),
        "source_evidence_ref_resolvable_count": sum(
            1 for row in candidates if row["signals"]["source_evidence_ref_resolvable"]
        ),
        "candidate_by_pair": dict(
            Counter(f"{row['source_type']}->{row['target_type']}" for row in candidates).most_common()
        ),
        "state_honesty": "mechanical candidate generation only; no relation type selection or writeback",
    }
    if args.canonical_strong_window:
        queues = build_canonical_queues(relation_rows, candidates)
        blockers.extend(queues["blockers"])
        write_jsonl(out_dir / "blocker_queue.jsonl", blockers)
        write_jsonl(out_dir / "canonical_strong_queue.jsonl", queues["canonical_strong"])
        write_jsonl(out_dir / "canonical_fresh_queue.jsonl", queues["canonical_fresh"])
        write_jsonl(out_dir / "canonical_historical_defer_queue.jsonl", queues["canonical_historical_defer"])
        write_jsonl(out_dir / "excluded_existing_pair_queue.jsonl", queues["excluded_existing_pair"])
        write_jsonl(out_dir / "excluded_mirror_queue.jsonl", queues["excluded_mirror"])
        write_jsonl(out_dir / "defer_signal_queue.jsonl", queues["defer_signal"])
        summary.update(
            {
                "blocker_count": len(blockers),
                "canonical_strong_count": len(queues["canonical_strong"]),
                "canonical_fresh_count": len(queues["canonical_fresh"]),
                "canonical_historical_defer_count": len(queues["canonical_historical_defer"]),
                "excluded_existing_pair_count": len(queues["excluded_existing_pair"]),
                "excluded_mirror_count": len(queues["excluded_mirror"]),
                "defer_signal_count": len(queues["defer_signal"]),
                "canonical_historical_defer_reason_count": dict(
                    Counter(
                        defer.get("reason", "unknown")
                        for row in queues["canonical_historical_defer"]
                        for defer in (row.get("historical_defer") or [])
                    ).most_common()
                ),
            }
        )
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (out_dir / "summary.md").write_text(summary_markdown(summary), encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
