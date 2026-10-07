#!/usr/bin/env python3
"""Exclude the printed page marker and running header on physical p.17 / p.459."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1819-1820"
SEGMENT_SHA = "212b07088987bbb82b2a1b99c8817e71836ce68c56da6fc88dfc8cfeff03199c"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p459-marker-l1819-1820-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "7c9f907f84978ca8c64830540ac46156fd9c814c231dca70252cb0c3151a7a21",
    TABLES / "s2-coverage.csv": "f7cfd17bbc59c249bff7186647bfc7c46ddede997904a7615c84d337ab8d0c1a",
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


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1818:1820])
if (
    not segment_text.startswith("[Page 459]")
    or "INDEX" not in segment_text
    or hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA
):
    raise SystemExit("S0 p.459 page marker/header changed")

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
    segment.get("release_excluded"),
) != (SOURCE_FILE, 1819, 1820, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.459 page-marker manifest changed")

coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous = coverage_by_id.get("chp-22:22_CHP-22Index:l1763-1817")
next_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1822-1876")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.459 page-marker segment is not queued")
if not previous or (previous["disposition"], previous["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.458 right-column segment is not complete")
if not next_left or (next_left["disposition"], next_left["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.459 left-column segment is not queued")

target.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L1819-1820",
    note=(
        "no_semantic_content: S0 L1819 [Page 459] and L1820 INDEX are generated page navigation/running header. "
        "CHP-22Index.pdf physical p.17 visibly prints p.459; these lines are not index entries or book-fact claims. "
        "The next substantive material begins in the left column at L1822."
    ),
)

after = {
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
}
expected_after = {"coverage_complete": 647, "coverage_queued": 46, "coverage_excluded": 139, "coverage_partial": 0}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 459,
    "pdf_physical_page": 17,
    **after,
}
if ARGS.apply:
    backup_path = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup_path.exists():
        raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup_path.name}")
    shutil.copy2(coverage_path, backup_path)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backup"] = str(backup_path.relative_to(ROOT))

print(json.dumps(result, ensure_ascii=False, indent=2))
