#!/usr/bin/env python3
"""Repair S2 coverage syntax and claim keys after the p.412 bibliography migration."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENT = "chp-21:21_CHP-21Bibliography:l47-85"
BACKUP = ".bak-s2-chp21-bibliography-l47-85-audit-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
if (len(statements), len(coverage)) != (11261, 832):
    raise SystemExit("unexpected applied-migration state; refusing repair")

statement_by_id = {row["statement_id"]: row for row in statements}
entry_ids = [f"st-chp21-bib-l47-85-entry-{index:02d}" for index in range(1, 30)]
required_ids = entry_ids + [
    "st-chp21-bib-l47-85-published-materials-heading",
    "st-chp21-bib-l47-85-andres-harris-cross-reference",
]
if any(statement_id not in statement_by_id for statement_id in required_ids):
    raise SystemExit("applied bibliography statements are incomplete")

claim_updates = {}
for statement_id in entry_ids:
    statement = statement_by_id[statement_id]
    qualifiers = statement.get("qualifiers", {})
    record = qualifiers.get("bibliographic_record", {})
    title = record.get("title_as_printed")
    if not title or statement.get("segment_id") != SEGMENT:
        raise SystemExit(f"invalid bibliography statement record: {statement_id}")
    claim_updates[statement_id] = f"Haskell lists {title} in the book bibliography."

coverage_by_id = {row["segment_id"]: row for row in coverage}
if SEGMENT not in coverage_by_id or coverage_by_id[SEGMENT].get("disposition") != "reviewed":
    raise SystemExit("target segment is not in reviewed state")
old_range = coverage_by_id[SEGMENT].get("source_line_ranges", "")
if old_range not in {"47-85", "L47-85"}:
    raise SystemExit(f"unexpected S2 source range: {old_range!r}")

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "segment": SEGMENT,
    "claim_natural_keys_repaired": len(claim_updates),
    "coverage_range": {"before": old_range, "after": "L47-85"},
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    for path in (statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP)
        if backup.exists():
            raise SystemExit(f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
    for statement_id, claim in claim_updates.items():
        statement_by_id[statement_id]["qualifiers"]["claim"] = claim
    coverage_by_id[SEGMENT]["source_line_ranges"] = "L47-85"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False) as handle:
        for row in statements:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(statement_path)
    write_csv(coverage_path, coverage_fields, coverage)
