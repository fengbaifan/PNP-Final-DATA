"""Correct p.280's forward pointer after confirming inserted Plate 49–52 segments."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENT_ID = "st-chp10-p280-sheffield-description-open"
P280 = "chp-10:10_CHP-10_intro:l51-61"
PLATE_49 = "chp-10:10_CHP-10_intro:l63-89"
P281_BODY = "chp-10:10_CHP-10_intro:l125-139"
OLD_NOTE = "continues at p.281 L63"
NEW_NOTE = "resumes in the p.281 body at canonical L126 after the inserted Plates 49–52"
BACKUP_SUFFIX = ".bak-s2-chp10-p280-crossref-fix-20261002"


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
statement = next((row for row in statements if row["statement_id"] == STATEMENT_ID), None)
coverage_by_id = {row["segment_id"]: row for row in coverage}
plate = coverage_by_id.get(PLATE_49)
page_280 = coverage_by_id.get(P280)
if statement is None or plate is None or page_280 is None:
    raise SystemExit("expected p.280 statement and adjacent coverage rows missing")
refs = statement["qualifiers"].get("cross_reference_segments", [])
if refs != [{"segment_id": PLATE_49, "source_line_start": 63, "source_line_end": 89}]:
    raise SystemExit(f"unexpected existing p.280 continuation pointer: {refs}")
if OLD_NOTE not in page_280["note"]:
    raise SystemExit("expected stale p.280 coverage continuation note not found")
if not plate["note"].startswith("Next source-order body segment; expected to close the Prince Eugene description"):
    raise SystemExit("unexpected p.281 inserted-plate cursor note")
body_lines = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig").splitlines()
if body_lines[124].strip() != "[Page 281]" or not body_lines[125].startswith("1712 as"):
    raise SystemExit("expected p.281 body to resume after Plates 49–52")

statement["qualifiers"]["cross_reference_segments"] = [
    {"segment_id": P281_BODY, "source_line_start": 126, "source_line_end": 126}
]
page_280["note"] = page_280["note"].replace(OLD_NOTE, NEW_NOTE)
plate["note"] = (
    "Next source-order segment is the rotated Plate 49 visual/caption material; it does not continue the Prince Eugene sentence. "
    "The narrative resumes at canonical L126 on p.281 after Plates 49–52."
)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
print(json.dumps({"mode": "APPLY" if args.apply else "DRY-RUN", "statement": STATEMENT_ID,
                  "old_reference": refs, "new_reference": statement["qualifiers"]["cross_reference_segments"],
                  "plate49_note": plate["note"]}, ensure_ascii=False, indent=2))
if not args.apply:
    raise SystemExit(0)

for path in (statement_path, coverage_path):
    backup = Path(str(path) + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
print("Applied p.280 continuation pointer correction; backups retained.")
