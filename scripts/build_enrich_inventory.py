#!/usr/bin/env python3
"""Build mechanical enrich signals without making semantic enrich decisions."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


BASE = Path(__file__).resolve().parents[1]
DEFAULT_UNITS = BASE / "04-knowledge" / "units"
UNIT_DIRS = ("persons", "institutions", "places", "works", "publications", "terms", "procedures", "events")


def read_unit(path: Path, units_dir: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    parts = text.split("---", 2)
    frontmatter = yaml.safe_load(parts[1]) or {} if len(parts) >= 3 else {}
    body = parts[2] if len(parts) >= 3 else ""
    body_chars = len(re.sub(r"\s+", "", body))
    source_count = int(frontmatter.get("source_count") or 0)
    evidence_status = str(frontmatter.get("evidence_status") or "")
    lower = text.lower()
    reasons: list[str] = []
    score = 0
    if body_chars < 300:
        score += 5
        reasons.append("thin_body_under_300_chars")
    if evidence_status == "partially_verified":
        score += 3
        reasons.append("partially_verified")
    if source_count <= 1:
        score += 2
        reasons.append("single_source")
    if "wikipedia.org" not in lower and "wikidata.org" not in lower:
        score += 1
        reasons.append("no_wikipedia_or_wikidata_anchor")
    unit_type = path.parent.name.removesuffix("s")
    if unit_type in {"person", "publication", "term"}:
        score += 1
        reasons.append("priority_unit_type")
    return {
        "unit": path.relative_to(units_dir).as_posix(),
        "unit_type": unit_type,
        "title": frontmatter.get("title"),
        "name_en": frontmatter.get("name_en"),
        "source_count": source_count,
        "evidence_status": evidence_status,
        "confidence": frontmatter.get("confidence"),
        "body_nonspace_chars": body_chars,
        "has_wikipedia": "wikipedia.org" in lower,
        "has_wikidata": "wikidata.org" in lower,
        "has_reference_section": bool(re.search(r"(?m)^##\s*(参考文献|References|Bibliography|Further reading)", body)),
        "priority_score": score,
        "priority_reasons": reasons,
        "enrich_status": "pending_semantic_review",
    }


def build_inventory(units_dir: Path) -> list[dict[str, Any]]:
    rows = [read_unit(path, units_dir) for dirname in UNIT_DIRS for path in sorted((units_dir / dirname).glob("*.md"))]
    return sorted(rows, key=lambda row: (-row["priority_score"], row["body_nonspace_chars"], row["unit"]))


def apply_reviewed_triage(rows: list[dict[str, Any]], paths: list[Path]) -> None:
    decisions: dict[str, tuple[dict[str, Any], Path]] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                row = json.loads(line)
                if isinstance(row.get("unit"), str) and isinstance(row.get("enrich_status"), str):
                    decisions[row["unit"]] = (row, path)
    for row in rows:
        reviewed = decisions.get(row["unit"])
        if reviewed:
            decision, source_path = reviewed
            row["enrich_status"] = decision["enrich_status"]
            row["enrich_decision_source"] = source_path.as_posix()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--units-dir", type=Path, default=DEFAULT_UNITS)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--queue-limit", type=int, default=25)
    parser.add_argument("--reviewed-triage", type=Path, nargs="*", default=[])
    args = parser.parse_args()
    units_dir = args.units_dir if args.units_dir.is_absolute() else BASE / args.units_dir
    out_dir = args.out_dir if args.out_dir.is_absolute() else BASE / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = build_inventory(units_dir)
    reviewed_paths = [path if path.is_absolute() else BASE / path for path in args.reviewed_triage]
    apply_reviewed_triage(rows, reviewed_paths)
    queue = [row for row in rows if row["enrich_status"] == "pending_semantic_review"][: args.queue_limit]
    write_jsonl(out_dir / "enrich_inventory.jsonl", rows)
    write_jsonl(out_dir / "enrich_review_queue.jsonl", queue)
    status_counts = Counter(row["evidence_status"] for row in rows)
    summary = {
        "total_units": len(rows),
        "inventory_covered": len(rows),
        "pending_semantic_review": sum(row["enrich_status"] == "pending_semantic_review" for row in rows),
        "reviewed": sum(row["enrich_status"] != "pending_semantic_review" for row in rows),
        "reviewed_by_status": dict(Counter(row["enrich_status"] for row in rows if row["enrich_status"] != "pending_semantic_review")),
        "queue_size": len(queue),
        "thin_body_under_300_chars": sum(row["body_nonspace_chars"] < 300 for row in rows),
        "single_source": sum(row["source_count"] <= 1 for row in rows),
        "with_wikipedia": sum(row["has_wikipedia"] for row in rows),
        "with_wikidata": sum(row["has_wikidata"] for row in rows),
        "evidence_status": dict(status_counts),
        "semantic_decisions_made": sum(row["enrich_status"] != "pending_semantic_review" for row in rows),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out_dir / "summary.md").write_text(
        "# Enrich Inventory\n\n"
        f"- Inventory coverage: {len(rows)}/{len(rows)}\n"
        f"- First semantic-review queue: {len(queue)}\n"
        f"- Thin body signal: {summary['thin_body_under_300_chars']}\n"
        f"- Single-source signal: {summary['single_source']}\n"
        f"- Semantic enrich decisions imported: {summary['semantic_decisions_made']}\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
