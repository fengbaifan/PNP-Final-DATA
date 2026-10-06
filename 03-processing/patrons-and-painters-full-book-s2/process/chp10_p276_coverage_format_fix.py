"""Correct p.276 coverage range notation to the audit parser's Lstart-end format."""
from __future__ import annotations

import argparse
import csv
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "s2-coverage.csv"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp10-p276-range-format-fix-20261002")
EXPECTED = {
    "chp-10:10_CHP-10_intro:l1-1": ("excluded", "complete", "L1-L1", "L1-1"),
    "chp-10:10_CHP-10_intro:l3-13": ("reviewed", "complete", "L3-L13", "L3-13"),
}

with TABLE.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
by_id = {row["segment_id"]: row for row in rows}
for segment_id, (disposition, migration_status, old_range, new_range) in EXPECTED.items():
    row = by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != (
        disposition, migration_status, old_range
    ):
        raise SystemExit(f"unexpected coverage pre-state for {segment_id}: {row}")
    row["source_line_ranges"] = new_range

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the two corrected source ranges")
args = parser.parse_args()
for segment_id, (_, _, old_range, new_range) in EXPECTED.items():
    print(f"{segment_id}: {old_range} -> {new_range}")
if not args.apply:
    print("DRY RUN: no files changed")
else:
    if BACKUP.exists():
        raise SystemExit(f"refusing to overwrite backup: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(TABLE)
    print(f"applied; backup={BACKUP.name}")
