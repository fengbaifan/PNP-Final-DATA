#!/usr/bin/env python3
"""Exclude the generated page marker for printed p.450."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l796-796"
SEGMENT_SHA = "76e429597707c00a870be43757ccc5b5625c34a7a1a1419fe84eab986f18a04f"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p450-marker-l796-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "entity-candidates.csv": "6934f46fd5f4cb51496e6618a21bc9be0f838e84e769685f5a419a8e094ebf41",
    TABLES / "s2-coverage.csv": "ebaec4837ad5f50b5730b2a395cf31c25573053f57bd1a0f9a128757dd79e14a",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
segment = manifest.get(SEGMENT_ID)
if not segment or (
    segment.get("source_file"),
    segment.get("line_start"),
    segment.get("line_end"),
    segment.get("sha256"),
    segment.get("asset_sha256"),
) != (SOURCE_FILE, 796, 796, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[795:796])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")
if segment_text.strip() != "[Page 450]":
    raise SystemExit("target source line is not the expected page marker")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage}
row = coverage_by_id.get(SEGMENT_ID)
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
previous = coverage_by_id.get("chp-22:22_CHP-22Index:l740-794")
next_segment = coverage_by_id.get("chp-22:22_CHP-22Index:l798-852")
if not previous or (previous["disposition"], previous["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.449 right-column segment is not complete")
if not next_segment or (next_segment["disposition"], next_segment["migration_status"]) != ("queued", "pending"):
    raise SystemExit("following p.450 left-column segment is not queued")

if (len(candidates), len(coverage)) != (11436, 832):
    raise SystemExit("unexpected S2 pre-state")
row.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L796-796",
    note=(
        "no_semantic_content: S0 L796 [Page 450] is a generated page locator. CHP-22Index.pdf physical p.8 "
        "visibly prints p.450; the marker is page navigation, not an index entry or book-fact claim."
    ),
)

after = {
    "coverage_complete": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "complete"
        for item in coverage
    ),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "partial"
        for item in coverage
    ),
}
expected_after = {
    "coverage_complete": 630,
    "coverage_queued": 72,
    "coverage_excluded": 130,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 450,
    "pdf_physical_page": 8,
    "candidate_count": len(candidates),
    "coverage_rows": len(coverage),
    "new_candidates": 0,
    "new_mentions": 0,
    "new_book_statements": 0,
    **after,
}
if ARGS.apply:
    backup_path = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup_path.exists():
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    shutil.copy2(coverage_path, backup_path)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=coverage_path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=coverage_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(coverage)
        temporary = Path(handle.name)
    temporary.replace(coverage_path)
    result["backup"] = str(backup_path.relative_to(ROOT))

print(json.dumps(result, ensure_ascii=False, indent=2))
