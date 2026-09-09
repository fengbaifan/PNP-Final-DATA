#!/usr/bin/env python3
"""Validate a compact-v4 processing package without semantic adjudication."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from scripts._source_fingerprint import source_assets_state
except ModuleNotFoundError:
    from _source_fingerprint import source_assets_state


BASE = Path(__file__).resolve().parents[1]
LOGICAL_FILES = ("source-map.jsonl", "semantic-units.jsonl", "candidate-ledger.jsonl", "summary.md")
REQUIRED_FILES = (*LOGICAL_FILES, "manifest.json")
CANDIDATE_REQUIRED_FIELDS = {
    "candidate_id",
    "origin_type",
    "origin_ref",
    "candidate_type",
    "payload",
    "evidence_refs",
    "state",
    "decision",
    "created_at",
    "updated_at",
}
KNOWLEDGE_MATCH_STATUSES = {
    "novel",
    "existing_target",
    "potential_duplicate",
    "potential_conflict",
    "undetermined",
}
SEMANTIC_ACCEPTANCE_STATUSES = {"accepted", "accepted_with_findings"}
SEMANTIC_ACCEPTANCE_REQUIRED_FIELDS = {
    "reread_status",
    "reviewer_kind",
    "reviewer_id",
    "reviewed_at",
    "source_version",
    "omission_count",
    "acceptance_boundary",
}
PROCESSING_SCOPE_MODE = "full_asset"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    issues: list[str] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                issues.append(f"{path.name}:{number}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(item, dict):
                issues.append(f"{path.name}:{number}: record must be an object")
                continue
            records.append(item)
    return records, issues


def merged_line_count(spans: list[tuple[int, int]]) -> tuple[int, list[tuple[int, int]]]:
    """Return covered line count and uncovered gaps between line 1 and the last span."""
    if not spans:
        return 0, []
    merged: list[list[int]] = []
    for start, end in sorted(spans):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    gaps: list[tuple[int, int]] = []
    cursor = 1
    for start, end in merged:
        if start > cursor:
            gaps.append((cursor, start - 1))
        cursor = end + 1
    return sum(end - start + 1 for start, end in merged), gaps


def package_source_state(package: Path, root: Path = BASE) -> dict:
    """Return declared/effective ingest state for one compact package."""
    manifest_path = package / "manifest.json"
    if not manifest_path.is_file():
        return {
            "declared_status": "missing",
            "effective_status": "reopened_source_drift",
            "issues": ["manifest.json is missing"],
        }
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return {
            "declared_status": "invalid",
            "effective_status": "reopened_source_drift",
            "issues": [f"manifest.json: invalid JSON: {exc.msg}"],
        }
    return source_assets_state(manifest, root)


def compact_package_issues(package: Path, root: Path = BASE) -> list[str]:
    issues: list[str] = []
    missing = [name for name in REQUIRED_FILES if not (package / name).is_file()]
    if missing:
        return [f"missing {name}" for name in missing]
    try:
        manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return [f"manifest.json: invalid JSON: {exc.msg}"]
    if manifest.get("processing_profile") != "compact-v4":
        issues.append("manifest processing_profile must be compact-v4")

    source_state = source_assets_state(manifest, root)
    issues.extend(source_state["issues"])
    if source_state["effective_status"] == "reopened_source_drift":
        issues.append("effective_status=reopened_source_drift")

    source_map, source_issues = read_jsonl(package / "source-map.jsonl")
    semantic_units, semantic_issues = read_jsonl(package / "semantic-units.jsonl")
    candidates, candidate_issues = read_jsonl(package / "candidate-ledger.jsonl")
    issues.extend(source_issues + semantic_issues + candidate_issues)

    block_ids = [str(item.get("block_id") or "") for item in source_map]
    semantic_ids = {str(item.get("semantic_unit_id") or "") for item in semantic_units}
    candidate_id_list = [str(item.get("candidate_id") or "") for item in candidates]
    candidate_ids = set(candidate_id_list)
    if "" in block_ids or len(set(block_ids)) != len(block_ids):
        issues.append("source-map block_id values must be present and unique")
    if "" in semantic_ids:
        issues.append("semantic unit IDs must be present")
    if "" in candidate_ids:
        issues.append("candidate IDs must be present")
    if len(candidate_id_list) != len(candidate_ids):
        issues.append("candidate IDs must be unique")

    for item in candidates:
        candidate_id = item.get("candidate_id") or "<missing>"
        missing_fields = sorted(CANDIDATE_REQUIRED_FIELDS - set(item))
        if missing_fields:
            issues.append(f"candidate {candidate_id}: missing envelope fields {missing_fields}")
        decision = item.get("decision")
        if not isinstance(decision, dict):
            issues.append(f"candidate {candidate_id}: decision must be an object")
        else:
            missing_decision = sorted({"status", "reason", "decided_by", "decided_at"} - set(decision))
            if missing_decision:
                issues.append(f"candidate {candidate_id}: missing decision fields {missing_decision}")
        payload = item.get("payload")
        knowledge_match = payload.get("knowledge_match") if isinstance(payload, dict) else None
        if not isinstance(knowledge_match, dict):
            issues.append(f"candidate {candidate_id}: payload.knowledge_match is required")
            continue
        match_status = knowledge_match.get("status")
        if match_status not in KNOWLEDGE_MATCH_STATUSES:
            issues.append(f"candidate {candidate_id}: invalid knowledge_match status {match_status!r}")
        if not isinstance(knowledge_match.get("target_refs"), list):
            issues.append(f"candidate {candidate_id}: knowledge_match.target_refs must be a list")
        if match_status == "undetermined" and item.get("state") in {"approved", "applied", "no_delta"}:
            issues.append(f"candidate {candidate_id}: undetermined match cannot be {item.get('state')}")

    processing_scope = manifest.get("processing_scope")
    scope_assets: list[str] = []
    if not isinstance(processing_scope, dict):
        issues.append("manifest processing_scope is required")
    else:
        if processing_scope.get("mode") != PROCESSING_SCOPE_MODE:
            issues.append(f"processing_scope.mode must be {PROCESSING_SCOPE_MODE}")
        raw_scope_assets = processing_scope.get("assets")
        if not isinstance(raw_scope_assets, list) or not raw_scope_assets:
            issues.append("processing_scope.assets must be a non-empty list")
        elif not all(isinstance(value, str) and value for value in raw_scope_assets):
            issues.append("processing_scope.assets must contain repository-relative paths")
        elif len(raw_scope_assets) != len(set(raw_scope_assets)):
            issues.append("processing_scope.assets must be unique")
        else:
            scope_assets = raw_scope_assets
    fingerprinted_assets = {
        str(item.get("path") or "")
        for item in manifest.get("source_assets") or []
        if isinstance(item, dict)
    }
    for asset in scope_assets:
        if asset not in fingerprinted_assets:
            issues.append(f"processing scope asset is not fingerprinted: {asset}")

    reviewed = 0
    unread = 0
    without_candidate_review = 0
    line_counts: dict[Path, int] = {}
    mapped_spans: dict[str, list[tuple[int, int]]] = {}
    for item in source_map:
        status = item.get("read_status")
        if status in {"read", "merged", "excluded_with_reason"}:
            reviewed += 1
        else:
            unread += 1
        if status == "excluded_with_reason" and not item.get("notes"):
            issues.append(f"block {item.get('block_id')}: exclusion requires notes")
        if not item.get("candidate_refs") and not item.get("no_candidate_reason"):
            without_candidate_review += 1
        missing_semantic = sorted(set(item.get("semantic_unit_refs") or []) - semantic_ids)
        missing_candidates = sorted(set(item.get("candidate_refs") or []) - candidate_ids)
        if missing_semantic:
            issues.append(f"block {item.get('block_id')}: unknown semantic refs {missing_semantic}")
        if missing_candidates:
            issues.append(f"block {item.get('block_id')}: unknown candidate refs {missing_candidates}")
        source_file = item.get("source_file")
        source_path = root / str(source_file or "")
        if not source_file or not source_path.is_file():
            issues.append(f"block {item.get('block_id')}: source_file is missing")
        else:
            start = item.get("line_start")
            end = item.get("line_end")
            if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
                issues.append(f"block {item.get('block_id')}: valid line_start/line_end are required")
            else:
                if source_path not in line_counts:
                    line_counts[source_path] = len(source_path.read_text(encoding="utf-8-sig").splitlines())
                if end > line_counts[source_path]:
                    issues.append(f"block {item.get('block_id')}: source span exceeds current file")
                else:
                    mapped_spans.setdefault(str(source_file), []).append((start, end))
        for parallel in item.get("parallel_sources") or []:
            if not isinstance(parallel, dict):
                issues.append(f"block {item.get('block_id')}: parallel source must be an object")
                continue
            parallel_path = root / str(parallel.get("source_file") or "")
            parallel_start = parallel.get("line_start")
            parallel_end = parallel.get("line_end")
            if not parallel_path.is_file():
                issues.append(f"block {item.get('block_id')}: parallel source_file is missing")
            elif not isinstance(parallel_start, int) or not isinstance(parallel_end, int) or parallel_start < 1 or parallel_end < parallel_start:
                issues.append(f"block {item.get('block_id')}: valid parallel line span is required")
            else:
                if parallel_path not in line_counts:
                    line_counts[parallel_path] = len(parallel_path.read_text(encoding="utf-8-sig").splitlines())
                if parallel_end > line_counts[parallel_path]:
                    issues.append(f"block {item.get('block_id')}: parallel source span exceeds current file")
                else:
                    mapped_spans.setdefault(str(parallel.get("source_file")), []).append(
                        (parallel_start, parallel_end)
                    )

    mapped_assets = set(mapped_spans)
    for asset in sorted(mapped_assets - set(scope_assets)):
        issues.append(f"source-map asset is outside processing_scope: {asset}")
    scope_lines_total = 0
    scope_lines_reviewed = 0
    scope_assets_reviewed = 0
    for asset in scope_assets:
        source_path = root / asset
        if not source_path.is_file():
            issues.append(f"processing scope asset is missing: {asset}")
            continue
        total_lines = len(source_path.read_text(encoding="utf-8-sig").splitlines())
        scope_lines_total += total_lines
        covered, internal_gaps = merged_line_count(mapped_spans.get(asset, []))
        scope_lines_reviewed += covered
        if covered == total_lines and not internal_gaps:
            scope_assets_reviewed += 1
        else:
            if not mapped_spans.get(asset):
                issues.append(f"processing scope asset is unmapped: {asset}")
            else:
                last_end = max(end for _, end in mapped_spans[asset])
                gaps = list(internal_gaps)
                if last_end < total_lines:
                    gaps.append((last_end + 1, total_lines))
                issues.append(f"processing scope asset has uncovered lines: {asset}: {gaps}")

    coverage = manifest.get("coverage") or {}
    observed = {
        "source_blocks_total": len(source_map),
        "source_blocks_reviewed": reviewed,
        "unread_blocks": unread,
        "blocks_without_candidate_review": without_candidate_review,
        "scope_assets_total": len(scope_assets),
        "scope_assets_reviewed": scope_assets_reviewed,
        "scope_lines_total": scope_lines_total,
        "scope_lines_reviewed": scope_lines_reviewed,
    }
    for field, value in observed.items():
        if coverage.get(field) != value:
            issues.append(f"coverage.{field}={coverage.get(field)!r}, observed={value}")
    if manifest.get("status") == "completed" and (unread or without_candidate_review):
        issues.append("completed package has unresolved coverage gaps")

    acceptance = manifest.get("semantic_acceptance")
    if manifest.get("status") == "completed":
        if not isinstance(acceptance, dict):
            issues.append("completed package requires semantic_acceptance")
        else:
            missing_acceptance = sorted(SEMANTIC_ACCEPTANCE_REQUIRED_FIELDS - set(acceptance))
            if missing_acceptance:
                issues.append(f"semantic_acceptance missing fields {missing_acceptance}")
            if acceptance.get("reread_status") not in SEMANTIC_ACCEPTANCE_STATUSES:
                issues.append("semantic_acceptance.reread_status must be accepted or accepted_with_findings")
            if acceptance.get("reviewer_kind") != "agent":
                issues.append("semantic_acceptance.reviewer_kind must be agent")
            omission_count = acceptance.get("omission_count")
            if not isinstance(omission_count, int) or omission_count < 0:
                issues.append("semantic_acceptance.omission_count must be a non-negative integer")
            if acceptance.get("reread_status") == "accepted" and omission_count != 0:
                issues.append("accepted semantic reread cannot report omissions")
            if acceptance.get("source_version") != manifest.get("input_fingerprint"):
                issues.append("semantic_acceptance.source_version must match input_fingerprint")
            if not str(acceptance.get("acceptance_boundary") or "").strip():
                issues.append("semantic_acceptance.acceptance_boundary is required")

    output_hashes = manifest.get("output_hashes") or {}
    for name in LOGICAL_FILES:
        expected = f"sha256:{sha256(package / name)}"
        if output_hashes.get(name) != expected:
            issues.append(f"output_hashes.{name} does not match")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="compact-v4 package directory")
    args = parser.parse_args()
    package = Path(args.package)
    if not package.is_absolute():
        package = BASE / package
    issues = compact_package_issues(package)
    print(json.dumps({"package": package.as_posix(), "issues": issues, "valid": not issues}, ensure_ascii=False, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
