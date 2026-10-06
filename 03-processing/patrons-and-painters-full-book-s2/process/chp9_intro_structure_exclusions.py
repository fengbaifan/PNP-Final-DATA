"""Record non-content structure at the start of Chapter 9 in the S2 ledger.

Default invocation is a read-only dry run. Source assets and OCR are untouched.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENTS = {
    "chp-9:09_CHP-9_intro:l1-1": "Generated Markdown filename heading; not printed book content.",
    "chp-9:09_CHP-9_intro:l3-5": "Printed page marker and Part III/VENICE section heading are structural navigation only; no entity mention or factual passage is present.",
}
BACKUP_SUFFIX = ".bak-s2-chp9-intro-structure-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
if not SEGMENTS.keys() <= segment_by_id.keys():
    raise SystemExit("missing target segment metadata")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != segment_by_id[next(iter(SEGMENTS))]["asset_sha256"]:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for segment_id in SEGMENTS:
    meta = segment_by_id[segment_id]
    selected = source_lines[meta["line_start"] - 1 : meta["line_end"]]
    if hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")

coverage_path = TABLES / "s2-coverage.csv"
fields, rows = read_csv(coverage_path)
by_id = {row["segment_id"]: row for row in rows}
for segment_id in SEGMENTS:
    row = by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")

for segment_id, reason in SEGMENTS.items():
    row = by_id[segment_id]
    row["disposition"] = "excluded"
    row["migration_status"] = "complete"
    row["source_line_ranges"] = f"L{segment_by_id[segment_id]['line_start']}-{segment_by_id[segment_id]['line_end']}"
    row["note"] = reason

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed ledger changes")
args = parser.parse_args()
print(f"targets={len(SEGMENTS)}; excluded={len(SEGMENTS)}; source={SOURCE.relative_to(ROOT)}")
for segment_id, reason in SEGMENTS.items():
    print(f"{segment_id}: {reason}")
if not args.apply:
    print("DRY RUN: no files changed")
else:
    backup = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    shutil.copy2(coverage_path, backup)
    write_csv_atomic(coverage_path, fields, rows)
    print(f"applied; backup={backup.name}")
