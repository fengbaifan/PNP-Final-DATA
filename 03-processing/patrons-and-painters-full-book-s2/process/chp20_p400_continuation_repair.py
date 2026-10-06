#!/usr/bin/env python3
"""Correct the p.400 open-statement link to printed p.401 after page-order review."""

import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
STATEMENT_ID = "st-chp20-p400-cassiano-journal-publication-open"
OLD_TARGET = "chp-20:20_CHP-20Postscript:l59-67"
NEW_TARGET = "chp-20:20_CHP-20Postscript:l81-96"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp20-p400-continuation-repair-20261004")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the corrected continuation link")
args = parser.parse_args()

segments = [json.loads(line) for line in SEGMENTS.open(encoding="utf-8")]
segment_by_id = {row["segment_id"]: row for row in segments}
if OLD_TARGET not in segment_by_id or NEW_TARGET not in segment_by_id:
    raise SystemExit("expected plate and printed-page segments are not registered")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
plate = segment_by_id[OLD_TARGET]
printed_page = segment_by_id[NEW_TARGET]
plate_text = "\n".join(source_lines[plate["line_start"] - 1 : plate["line_end"]])
p401_text = "\n".join(source_lines[printed_page["line_start"] - 1 : printed_page["line_end"]])
if "[Page 65]" not in plate_text:
    raise SystemExit("old target is not the expected Plate 65 segment")
if "[Page 401]" not in p401_text or "Escorial has been published in full." not in p401_text:
    raise SystemExit("new target does not contain the printed p.401 sentence continuation")

with COVERAGE.open(encoding="utf-8-sig", newline="") as stream:
    coverage = {row["segment_id"]: row for row in csv.DictReader(stream)}
if coverage.get(NEW_TARGET, {}).get("migration_status") != "pending":
    raise SystemExit("printed p.401 must still be pending before the continuation is linked")

original = STATEMENTS.read_bytes()
lines = original.decode("utf-8").splitlines(keepends=True)
matches = 0
updated = []
for raw in lines:
    ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
    body = raw[:-len(ending)] if ending else raw
    row = json.loads(body)
    if row.get("statement_id") == STATEMENT_ID:
        matches += 1
        qualifiers = row.get("qualifiers", {})
        if qualifiers.get("open_across_segment") is not True or qualifiers.get("continues_in_segment") != OLD_TARGET:
            raise SystemExit("p.400 open statement does not match the expected old continuation")
        qualifiers["continues_in_segment"] = NEW_TARGET
        row["qualifiers"] = qualifiers
        body = json.dumps(row, ensure_ascii=False, separators=(",", ":"))
    updated.append(body + ending)
if matches != 1:
    raise SystemExit(f"expected exactly one target statement, found {matches}")

print(f"statement: {STATEMENT_ID}")
print(f"continuation: {OLD_TARGET} -> {NEW_TARGET}")
if args.apply:
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    data = "".join(updated).encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=STATEMENTS.parent, prefix=".p400-link-", delete=False) as tmp:
        tmp.write(data)
        temp_path = Path(tmp.name)
    temp_path.replace(STATEMENTS)
    print(f"applied; backup: {BACKUP.name}")
else:
    print("DRY RUN: no files written")
