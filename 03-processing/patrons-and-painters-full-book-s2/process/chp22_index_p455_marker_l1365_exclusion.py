#!/usr/bin/env python3
"""Exclude the generated page marker and running header for printed p.455."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1365-1366"
SEGMENT_SHA = "2ac24aad023e082b6fa22c145fd10e6813c4f66ab37e31b3df3eb484ab1e9bb5"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p455-marker-l1365-1366-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "entity-candidates.csv": "a32bab356e042a030bcf4050f4515606684d9f5886f73eee3950111ae02e925c",
    TABLES / "s2-coverage.csv": "45b8787a8b00f8f2cd63c8f40008f5172c765778dc889de633bd622db406f8c7",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1364:1366])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")
if source_lines[1364].strip() != "[Page 455]" or source_lines[1365].strip() != "INDEX":
    raise SystemExit("p.455 marker/running header moved")

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
) != (SOURCE_FILE, 1365, 1366, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")

coverage_path = TABLES / "s2-coverage.csv"
with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames
    coverage = list(reader)
by_id = {row["segment_id"]: row for row in coverage}
target = by_id.get(SEGMENT_ID)
previous = by_id.get("chp-22:22_CHP-22Index:l1309-1363")
next_column = by_id.get("chp-22:22_CHP-22Index:l1368-1422")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target page marker is not queued")
if not previous or (previous["disposition"], previous["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.454 right column is not complete")
if not next_column or (next_column["disposition"], next_column["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.455 left-column segment is not queued")
if len(coverage) != 832:
    raise SystemExit("unexpected coverage row count")

target.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L1365-1366",
    note=(
        "no_semantic_content: S0 L1365 [Page 455] is a generated page locator and L1366 INDEX is a running section "
        "header. CHP-22Index.pdf physical p.13 visibly prints p.455 and the INDEX header; neither line is an index entry "
        "or book-fact claim."
    ),
)

after = {
    "coverage_complete": sum(row["disposition"] == "reviewed" and row["migration_status"] == "complete" for row in coverage),
    "coverage_queued": sum(row["disposition"] == "queued" for row in coverage),
    "coverage_excluded": sum(row["disposition"] == "excluded" for row in coverage),
    "coverage_partial": sum(row["disposition"] == "reviewed" and row["migration_status"] == "partial" for row in coverage),
}
expected_after = {
    "coverage_complete": 639,
    "coverage_queued": 58,
    "coverage_excluded": 135,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 455,
    "pdf_physical_page": 13,
    **after,
}
if ARGS.apply:
    backup_path = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup_path.exists():
        raise SystemExit("migration backup already exists; refusing to overwrite it")
    shutil.copy2(coverage_path, backup_path)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=coverage_path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(coverage)
        temporary = Path(handle.name)
    temporary.replace(coverage_path)
    result["backup"] = str(backup_path.relative_to(ROOT))

print(json.dumps(result, ensure_ascii=False, indent=2))
