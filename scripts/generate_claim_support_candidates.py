#!/usr/bin/env python3
"""Generate mechanical claim-support review signals from residual relations.

This script is read-only with respect to the knowledge base. It does not judge
claim support, create source spans, or apply registry writeback.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CLAIM_REGISTRY = BASE / "04-knowledge" / "quality" / "claim-registry.yml"


def load_yaml_rows(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or []
    return [row for row in data if isinstance(row, dict)]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
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


def normalize_unit_path(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    return text.removeprefix("04-knowledge/units/")


def normalize_claim_id(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    return Path(text.removeprefix("claim/")).stem


def claim_aliases(claim: dict[str, Any]) -> set[str]:
    aliases = {str(claim.get("claim_id", ""))}
    migrated_from = claim.get("migrated_from")
    if migrated_from:
        aliases.add(Path(str(migrated_from)).stem)
    return {alias for alias in aliases if alias}


def read_unit_frontmatter(path: Path) -> dict[str, Any]:
    parts = path.read_text(encoding="utf-8-sig").split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def evidence_refs(value: Any) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("evidence_ref"), dict):
            refs.append(value["evidence_ref"])
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


def build_candidates(
    claims: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
    root: Path = BASE,
    exclude_complete_claims: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    claim_map = {
        alias: claim
        for claim in claims
        for alias in claim_aliases(claim)
    }
    candidates: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for index, residual in enumerate(residual_rows, 1):
        residual_claim_slug = normalize_claim_id(residual.get("target"))
        source = normalize_unit_path(residual.get("source"))
        claim = claim_map.get(residual_claim_slug)
        claim_id = str(claim.get("claim_id")) if claim else residual_claim_slug
        source_path = root / "04-knowledge" / "units" / source
        row = {
            "candidate_id": f"claim-support-{index:03d}",
            "claim_id": claim_id,
            "residual_claim_slug": residual_claim_slug,
            "source_unit": source,
            "source_type": residual.get("source_type"),
            "historical_defer_reason": residual.get("reason"),
            "historical_defer": residual,
        }
        reasons: list[str] = []
        if residual.get("target_type") != "claim":
            reasons.append("target_not_claim")
        if claim is None:
            reasons.append("claim_missing")
        if not source_path.is_file():
            reasons.append("source_unit_missing")
        if claim and source in [normalize_unit_path(value) for value in claim.get("supported_by", [])]:
            reasons.append("duplicate_supported_by_binding")
        if reasons:
            row["blocker_reasons"] = reasons
            blockers.append(row)
            continue
        if exclude_complete_claims and claim.get("supports") and claim.get("supported_by"):
            row["excluded_reason"] = "claim_already_has_complete_binding"
            excluded.append(row)
            continue
        source_data = claim.get("source") if isinstance(claim.get("source"), dict) else {}
        source_ref = first_resolvable_evidence_ref(read_unit_frontmatter(source_path), root)
        row["signals"] = {
            "claim_source_doc_id": source_data.get("doc_id"),
            "claim_source_span": source_data.get("source_span"),
            "claim_has_source_span": bool(source_data.get("source_span")),
            "source_unit_type": residual.get("source_type"),
            "existing_supports": claim.get("supports", []),
            "existing_supported_by": claim.get("supported_by", []),
            "source_unit_evidence_ref_resolvable": source_ref is not None,
            "source_unit_evidence_ref": source_ref,
        }
        candidates.append(row)
    if exclude_complete_claims:
        return candidates, blockers, excluded
    return candidates, blockers


def summary_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Claim Support Candidate Preflight",
            "",
            "## Results",
            "",
            f"- Residual coverage: {summary['residual_coverage']}",
            f"- Candidate queue: {summary['candidate_count']}",
            f"- Blocker queue: {summary['blocker_count']}",
            f"- Excluded complete-claim queue: {summary['excluded_count']}",
            f"- Existing source span signal: {summary['claim_source_span_count']}",
            f"- Resolvable KU evidence ref signal: {summary['source_unit_evidence_ref_resolvable_count']}",
            "",
            "## Boundary",
            "",
            "- Mechanical signal extraction only.",
            "- No source-span generation, semantic approval, relation-type selection, or registry writeback.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-registry", type=Path, default=DEFAULT_CLAIM_REGISTRY)
    parser.add_argument("--residual-ledger", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--exclude-complete-claims", action="store_true")
    args = parser.parse_args()
    registry = args.claim_registry if args.claim_registry.is_absolute() else BASE / args.claim_registry
    residual_ledger = args.residual_ledger if args.residual_ledger.is_absolute() else BASE / args.residual_ledger
    out_dir = args.out_dir if args.out_dir.is_absolute() else BASE / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    residual_rows = load_jsonl(residual_ledger)
    result = build_candidates(
        load_yaml_rows(registry),
        residual_rows,
        exclude_complete_claims=args.exclude_complete_claims,
    )
    if args.exclude_complete_claims:
        candidates, blockers, excluded = result
    else:
        candidates, blockers = result
        excluded = []
    write_jsonl(out_dir / "ready_queue.jsonl", candidates)
    write_jsonl(out_dir / "blocker_queue.jsonl", blockers)
    write_jsonl(out_dir / "excluded_complete_claim_queue.jsonl", excluded)
    summary = {
        "residual_total": len(residual_rows),
        "residual_coverage": f"{len(candidates) + len(blockers) + len(excluded)}/{len(residual_rows)}",
        "candidate_count": len(candidates),
        "blocker_count": len(blockers),
        "excluded_count": len(excluded),
        "claim_source_span_count": sum(1 for row in candidates if row["signals"]["claim_has_source_span"]),
        "source_unit_evidence_ref_resolvable_count": sum(
            1 for row in candidates if row["signals"]["source_unit_evidence_ref_resolvable"]
        ),
        "candidate_by_pair": dict(Counter(f"{row['source_type']}->claim" for row in candidates).most_common()),
        "state_honesty": "mechanical candidate generation only; no source-span generation, semantic approval, or writeback",
    }
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
