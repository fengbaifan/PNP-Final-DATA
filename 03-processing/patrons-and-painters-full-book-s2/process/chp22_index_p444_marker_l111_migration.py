#!/usr/bin/env python3
"""Dispose the OCR page marker at S0 L111 (printed folio p.444)."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
SEGMENT_ID = "chp-22:22_CHP-22Index:l111-111"
SOURCE_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
PDF_SHA = "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5"
SEGMENT_SHA = "416bb56c937dafac08927855f582202f906144153af00982e7881b0581e62cb5"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p444-marker-l111-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(SOURCE) != SOURCE_SHA or sha256(PDF) != PDF_SHA:
    raise SystemExit("index source or PDF changed")
segments = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
segment = segments.get(SEGMENT_ID)
if not segment or (
    segment.get("source_file"),
    segment.get("line_start"),
    segment.get("line_end"),
    segment.get("sha256"),
    segment.get("asset_sha256"),
) != (
    "02-sources/02-Markdown/22_CHP-22Index.md",
    111,
    111,
    SEGMENT_SHA,
    SOURCE_SHA,
):
    raise SystemExit("page-marker manifest changed")
source_line = SOURCE.read_text(encoding="utf-8-sig").splitlines()[110]
if source_line != "[Page 444]" or hashlib.sha256(source_line.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("page-marker text changed")

coverage_path = TABLES / "s2-coverage.csv"
fields, rows = read_csv(coverage_path)
if len(rows) != 832:
    raise SystemExit("unexpected coverage table size")
by_id = {row["segment_id"]: row for row in rows}
target = by_id.get(SEGMENT_ID)
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("page-marker segment is not queued")
for required in (
    "chp-22:22_CHP-22Index:l64-109",
    "chp-22:22_CHP-22Index:l113-168",
):
    item = by_id.get(required)
    if not item or (item["disposition"], item["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"adjacent index page segment is incomplete: {required}")

target.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L111-111",
    note=(
        "no_semantic_content: S0 [Page 444] is a generated page locator matching the visible p.444 folio at the top of "
        "CHP-22Index.pdf physical p.2. It contains no index entry or book-fact claim."
    ),
)

after = {
    "coverage_complete": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "complete"
        for item in rows
    ),
    "coverage_queued": sum(item["disposition"] == "queued" for item in rows),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in rows),
    "coverage_partial": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "partial"
        for item in rows
    ),
}
expected = {
    "coverage_complete": 620,
    "coverage_queued": 88,
    "coverage_excluded": 124,
    "coverage_partial": 0,
}
if after != expected:
    raise SystemExit(f"unexpected coverage post-state: {after}")

result = {"mode": "apply" if ARGS.apply else "dry-run", "segment": SEGMENT_ID, **after}
if ARGS.apply:
    backup = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("coverage backup already exists; refusing to overwrite it")
    shutil.copy2(coverage_path, backup)
    write_csv(coverage_path, fields, rows)
    result["backup"] = str(backup.relative_to(ROOT))
print(json.dumps(result, ensure_ascii=False, indent=2))
