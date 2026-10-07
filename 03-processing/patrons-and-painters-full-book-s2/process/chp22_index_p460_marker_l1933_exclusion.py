#!/usr/bin/env python3
"""Exclude the generated page marker for printed p.460 on physical p.18."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1933-1933"
SEGMENT_SHA = "82e85195364932abd7a6083390af12cdcb4ca76f3ee899343ba7afa305c11405"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p460-marker-l1933-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "11c04337cf5e11eaf130353d2afc19fad64d0b7cf58c770bc3ab12cc7438e9e9",
    TABLES / "s2-coverage.csv": "664c4323be940aff7a2b0dd0696e818ddbc3afb3a6d934a2fd040f6fc9c5ea81",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}


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
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the reviewed coverage exclusion; default is dry-run")
ARGS = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1932:1933])
if segment_text != "[Page 460]" or hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.460 page marker changed")

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
    segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
    segment.get("sha256"), segment.get("asset_sha256"), segment.get("release_excluded"),
) != (SOURCE_FILE, 1933, 1933, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.460 page-marker manifest changed")

coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous = coverage_by_id.get("chp-22:22_CHP-22Index:l1878-1931")
next_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1935-1989")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.460 page-marker segment is not queued")
if not previous or (previous["disposition"], previous["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("preceding p.459 right-column segment is not complete")
if not next_left or (next_left["disposition"], next_left["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.460 left-column segment is not queued")

target.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L1933-1933",
    note=(
        "no_semantic_content: S0 L1933 [Page 460] is a generated page marker, not a printed index entry or book claim. "
        "CHP-22Index.pdf physical p.18 visibly prints p.460; the following index entries begin at L1935."
    ),
)

after = {
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
}
expected_after = {"coverage_complete": 649, "coverage_queued": 43, "coverage_excluded": 140, "coverage_partial": 0}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {"mode": "apply" if ARGS.apply else "dry-run", "source_segment": SEGMENT_ID,
          "printed_page": 460, "pdf_physical_page": 18, **after}
if ARGS.apply:
    backup_path = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup_path.exists():
        raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup_path.name}")
    shutil.copy2(coverage_path, backup_path)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backup"] = str(backup_path.relative_to(ROOT))

print(json.dumps(result, ensure_ascii=False, indent=2))
