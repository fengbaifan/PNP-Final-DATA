#!/usr/bin/env python3
"""Dry-run/apply the evidenced CHP-11/12 comparison-OCR exclusions in S2 coverage."""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENTS_PATH = TABLES / "segments.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
BACKUP_PATH = COVERAGE_PATH.with_name(
    "s2-coverage.csv.bak-scope-overlap-20261003"
)
COMPARISON_FILES = {
    "02-sources/02-Markdown/11_CHP-11_intro.md",
    "02-sources/02-Markdown/11_CHP-11_sec_ii.md",
    "02-sources/02-Markdown/12_CHP-12_intro.md",
}
FILE_TITLE_IDS = {
    "chp-11:11_CHP-11_intro:l1-1",
    "chp-11:11_CHP-11_sec_ii:l1-1",
    "chp-12:12_CHP-12_intro:l1-1",
}
TEXT_MATCHES = {
    "chp-11:11_CHP-11_intro:l3-15":
        "chp-10:10_CHP-10_intro:l354-366",
    "chp-11:11_CHP-11_intro:l140-197":
        "chp-10:10_CHP-10_intro:l491-634",
    "chp-11:11_CHP-11_sec_ii:l119-143":
        "chp-10:10_CHP-10_sec_ii:l273-349",
    "chp-12:12_CHP-12_intro:l3-15":
        "chp-10:10_CHP-10_sec_ii:l119-131",
    "chp-12:12_CHP-12_intro:l157-209":
        "chp-10:10_CHP-10_sec_ii:l273-349",
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def segment_text(row: dict) -> str:
    path = ROOT / row["source_file"]
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    return "\n".join(lines[row["line_start"] - 1 : row["line_end"]])


def normalized_text(text: str) -> str:
    text = re.sub(r"\[?page\s*\d+\]?", "", text, flags=re.IGNORECASE)
    return "".join(char.lower() for char in text if char.isalnum())


def target_reason(segment: dict, by_hash: dict[str, list[dict]], by_id: dict[str, dict]) -> str:
    segment_id = segment["segment_id"]
    if segment_id in FILE_TITLE_IDS:
        return "排除：仅为Markdown文件名标题，不是原书内容。"

    exact = [row for row in by_hash[segment["sha256"]] if row["chapter"] == "chp-10"]
    if len(exact) == 1:
        return (
            f"排除：与规范合并源段`{exact[0]['segment_id']}`的段文本SHA-256完全相同；"
            "该行属于CHP-11/12同版扫描的重复切片OCR，保留本文件作校勘对照，不重复计入S2。"
        )

    canonical_id = TEXT_MATCHES.get(segment_id)
    if not canonical_id or canonical_id not in by_id:
        raise ValueError(f"No reviewed canonical mapping for comparison segment {segment_id}")
    source = normalized_text(segment_text(segment))
    canonical = normalized_text(segment_text(by_id[canonical_id]))
    if not source:
        raise ValueError(f"Comparison segment has no source text: {segment_id}")
    matched = sum(block.size for block in SequenceMatcher(None, source, canonical, autojunk=False).get_matching_blocks())
    if matched != len(source):
        raise ValueError(
            f"Comparison text not fully represented in canonical segment: {segment_id} -> {canonical_id} ({matched}/{len(source)})"
        )
    return (
        f"排除：对应正文/脚注文本已由规范合并源段`{canonical_id}`覆盖；"
        "去除非字母数字字符后的文本序列匹配覆盖100%。CHP-11/12与CHP-10对应页图栅格完全一致；"
        "本段为同页另一OCR，不重复计入S2。"
    )


def build_plan() -> tuple[list[dict], list[dict], dict[str, dict]]:
    segments = load_jsonl(SEGMENTS_PATH)
    by_id = {row["segment_id"]: row for row in segments}
    by_hash: dict[str, list[dict]] = defaultdict(list)
    for row in segments:
        by_hash[row["sha256"]].append(row)

    targets = [row for row in segments if row["source_file"] in COMPARISON_FILES]
    if len(targets) != 44:
        raise ValueError(f"Expected 44 CHP-11/12 comparison segments, found {len(targets)}")
    if sum(row["chapter"] == "chp-10" for row in segments) == 0:
        raise ValueError("Canonical composite OCR segments are missing")

    coverage = list(csv.DictReader(COVERAGE_PATH.open(encoding="utf-8-sig", newline="")))
    coverage_by_id = {row["segment_id"]: row for row in coverage}
    if len(coverage_by_id) != len(coverage):
        raise ValueError("s2-coverage.csv has duplicate segment IDs")
    plan: list[dict] = []
    for segment in targets:
        segment_id = segment["segment_id"]
        row = coverage_by_id.get(segment_id)
        if not row:
            raise ValueError(f"Missing coverage row: {segment_id}")
        if (row["disposition"], row["migration_status"]) != ("queued", "pending"):
            raise ValueError(f"Comparison segment is not untouched/queued: {segment_id}")
        plan.append({
            "segment_id": segment_id,
            "reason": target_reason(segment, by_hash, by_id),
        })

    exact_count = sum("SHA-256完全相同" in item["reason"] for item in plan)
    title_count = sum(item["segment_id"] in FILE_TITLE_IDS for item in plan)
    mapped_count = len(plan) - exact_count - title_count
    if (exact_count, mapped_count, title_count) != (36, 5, 3):
        raise ValueError(
            f"Unexpected exclusion classes: exact={exact_count}, mapped={mapped_count}, headers={title_count}"
        )

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    mention_segments = {row["segment_id"] for row in mentions}
    statements = load_jsonl(TABLES / "book-statements.jsonl")
    statement_segments = {row["segment_id"] for row in statements}
    for item in plan:
        sid = item["segment_id"]
        if sid in mention_segments or sid in statement_segments:
            raise ValueError(f"Cannot exclude a segment already referenced by S2 rows: {sid}")
    return coverage, plan, coverage_by_id


def write_coverage(rows: list[dict]) -> None:
    raw = COVERAGE_PATH.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lineterminator = "\r\n" if b"\r\n" in raw else "\n"
    fields = list(rows[0]) if rows else ["chapter", "segment_id", "disposition", "migration_status", "source_line_ranges", "note"]
    temp_path = COVERAGE_PATH.with_name(COVERAGE_PATH.name + ".scope-tmp")
    with temp_path.open("w", encoding="utf-8-sig" if has_bom else "utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator=lineterminator)
        writer.writeheader()
        writer.writerows(rows)
    temp_path.replace(COVERAGE_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the reviewed exclusions")
    args = parser.parse_args()

    coverage, plan, _ = build_plan()
    print("PDF raster map: CHP-11 pages 1-22 = CHP-10 pages 28-49; CHP-12 pages 1-15 = CHP-10 pages 50-64")
    print("comparison_segments=44 exact_text_matches=36 normalized_text_mappings=5 markdown_headers=3")
    for item in plan:
        print(f"{item['segment_id']} -> excluded")
    if not args.apply:
        print("preview only; pass --apply to write s2-coverage.csv")
        return 0
    if BACKUP_PATH.exists():
        raise FileExistsError(f"Refusing to overwrite recovery copy: {BACKUP_PATH}")

    plan_by_id = {item["segment_id"]: item["reason"] for item in plan}
    updated: list[dict] = []
    for row in coverage:
        copy = dict(row)
        if copy["segment_id"] in plan_by_id:
            copy["disposition"] = "excluded"
            copy["migration_status"] = "complete"
            copy["source_line_ranges"] = ""
            copy["note"] = plan_by_id[copy["segment_id"]]
        updated.append(copy)

    shutil.copy2(COVERAGE_PATH, BACKUP_PATH)
    write_coverage(updated)
    final = {row["segment_id"]: row for row in csv.DictReader(COVERAGE_PATH.open(encoding="utf-8-sig", newline=""))}
    for segment_id in plan_by_id:
        row = final.get(segment_id)
        if not row or row["disposition"] != "excluded" or row["migration_status"] != "complete" or not row["note"]:
            raise RuntimeError(f"Post-write coverage verification failed: {segment_id}")
    print(f"applied=44 backup={BACKUP_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
