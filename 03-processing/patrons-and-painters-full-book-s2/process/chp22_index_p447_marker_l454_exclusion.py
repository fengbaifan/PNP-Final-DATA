#!/usr/bin/env python3
"""Exclude the generated page marker on printed index p.447."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l454-454"
SEGMENT_SHA = "32f6a4831e9b7ee4c1b57a23e46fdaf89cb169cfe21e689cffdb1ea45d26fc96"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p447-marker-l454-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "entity-candidates.csv": "908961f14a3d0f25199ae21df5981990cf1c64f006ae948b0142ce3ba6073f06",
    TABLES / "s2-coverage.csv": "33951cb1f3d6c68f041f29c52630b50f67be7e00cef36df84c62a285434ca124",
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


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


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
) != (SOURCE_FILE, 454, 454, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
if source_lines[453] != "[Page 447]" or hashlib.sha256(source_lines[453].encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 page marker changed")

coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous = coverage_by_id.get("chp-22:22_CHP-22Index:l398-452")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous or (previous["disposition"], previous["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("preceding p.446 right-column segment is not complete")

target.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L454-454",
    note=(
        "no_semantic_content: S0 L454 [Page 447] is a generated page locator. CHP-22Index.pdf physical p.5 "
        "visibly prints p.447; the marker is page navigation, not an index entry or book-fact claim."
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
    "coverage_complete": 624,
    "coverage_queued": 81,
    "coverage_excluded": 127,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 447,
    "pdf_physical_page": 5,
    "disposition": "excluded/complete",
    "reason": "generated_page_marker",
    "candidate_changes": 0,
    "new_mentions": 0,
    "new_book_statements": 0,
    **after,
}
if ARGS.apply:
    backup = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    shutil.copy2(coverage_path, backup)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backup"] = str(backup.relative_to(ROOT))

print(json.dumps(result, ensure_ascii=False, indent=2))
