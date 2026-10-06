"""Repair Plate 45 coverage metadata to match the S2 audit contract; dry run by default."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PATH = TABLES / "s2-coverage.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
OCR = "chp-9:09_CHP-9_intro:l251-256"
VISUAL = "chp-9:09_CHP-9_intro_plates_visual-transcription:l6-6"
BACKUP = PATH.with_name(PATH.name + ".bak-s2-chp9-plate45-coverage-fix-20261001")
OCR_NOTE = (
    "no_semantic_content: The OCR segment contains a page marker and unreadable reversed caption fragments; "
    "its readable caption is represented in the derived visual-transcription segment L6. "
    "CHP-9.pdf physical p.27 was reviewed and the OCR source remains unchanged."
)

with PATH.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    coverage = list(reader)
by_id = {r["segment_id"]: r for r in coverage}
ocr, visual = by_id.get(OCR), by_id.get(VISUAL)
if not ocr or (ocr["disposition"], ocr["migration_status"], ocr["source_line_ranges"]) != (
    "reviewed", "complete", "L251-256; visual transcription L6"
):
    raise SystemExit(f"unexpected OCR coverage state: {ocr}")
if not visual or (visual["disposition"], visual["migration_status"], visual["source_line_ranges"]) != (
    "reviewed", "complete", "L6"
):
    raise SystemExit(f"unexpected visual coverage state: {visual}")
statement_rows = [json.loads(x) for x in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
statement = next((r for r in statement_rows if r["statement_id"] == "st-chp9-plate45-caption"), None)
if not statement or statement["segment_id"] != VISUAL or statement["qualifiers"]["source_line_start"] != 6:
    raise SystemExit("Plate 45 caption statement is missing or moved")

ocr["source_line_ranges"] = "L251-256"
ocr["note"] = OCR_NOTE
visual["source_line_ranges"] = "L6-6"
summary = {
    OCR: {"source_line_ranges": ocr["source_line_ranges"], "note": ocr["note"]},
    VISUAL: {"source_line_ranges": visual["source_line_ranges"]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP.name}")
    shutil.copy2(PATH, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=PATH.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(coverage)
        temporary = Path(f.name)
    temporary.replace(PATH)
    print(f"APPLIED; recovery backup retained: {BACKUP.name}")
else:
    print("DRY RUN: no coverage rows written")
