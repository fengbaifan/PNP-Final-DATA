#!/usr/bin/env python3
"""Exclude the generated page marker for printed p.454."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1251-1251"
SEGMENT_SHA = "2684de0cefa73e197e50633fabea149c81752eeebdc85a25b82413b5c769a431"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p454-marker-l1251-20261007"
EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "s2-coverage.csv": "4590f9b15f4b271a74511f48cb45c2bbaf163379e370e219867799ba6063188d",
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
if source_lines[1250].strip() != "[Page 454]":
    raise SystemExit("S0 page marker changed")
if hashlib.sha256(source_lines[1250].encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 marker segment text changed")
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
) != (SOURCE_FILE, 1251, 1251, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")

coverage_path = TABLES / "s2-coverage.csv"
with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, coverage = reader.fieldnames, list(reader)
coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1196-1249")
next_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1253-1307")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target page marker is not queued")
if not previous_column or (previous_column["disposition"], previous_column["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.453 right column is not complete")
if not next_column or (next_column["disposition"], next_column["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.454 left-column segment is not queued")
if len(coverage) != 832:
    raise SystemExit("unexpected coverage row count")

target.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L1251-1251",
    note=(
        "no_semantic_content: S0 L1251 [Page 454] is a generated page locator. CHP-22Index.pdf physical p.12 visibly "
        "prints p.454; the marker is navigation, not an index entry or book-fact claim."
    ),
)
after = {
    "coverage_complete": sum(
        row["disposition"] == "reviewed" and row["migration_status"] == "complete"
        for row in coverage
    ),
    "coverage_queued": sum(row["disposition"] == "queued" for row in coverage),
    "coverage_excluded": sum(row["disposition"] == "excluded" for row in coverage),
    "coverage_partial": sum(
        row["disposition"] == "reviewed" and row["migration_status"] == "partial"
        for row in coverage
    ),
}
expected_after = {
    "coverage_complete": 637,
    "coverage_queued": 61,
    "coverage_excluded": 134,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 454,
    "pdf_physical_page": 12,
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
