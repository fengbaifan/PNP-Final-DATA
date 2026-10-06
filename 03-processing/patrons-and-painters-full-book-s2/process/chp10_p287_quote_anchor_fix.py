"""Correct the terminal comma in the p.287 note-4 quotation anchor."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
NOTES_LINES_SHA = "3b00c3d3c0d437990930793bc40735a651dfe3ef96f14dc24d302e8a60631156"
STATEMENT_ID = "st-chp10-notes-p287-mcswiny-spelling-variants"
BACKUP_SUFFIX = ".bak-s2-chp10-p287-quote-anchor-fix-20261002"
SPELLING_QUOTE = "McSwiny spelt his name in a great number of different ways at various stages in his career"

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("source asset changed")
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256("\n".join(lines[534:539]).encode("utf-8")).hexdigest() != NOTES_LINES_SHA:
    raise SystemExit("p.287 footnote source lines changed")
expected_quote = SPELLING_QUOTE + ","
if expected_quote not in lines[536]:
    raise SystemExit("source quote no longer matches expected p.287 text")

rows = [json.loads(item) for item in TABLE.read_text(encoding="utf-8-sig").splitlines() if item.strip()]
target = next((row for row in rows if row["statement_id"] == STATEMENT_ID), None)
if not target:
    raise SystemExit("p.287 spelling statement missing")
q = target.get("qualifiers", {})
if q.get("source_line_start") != 537 or q.get("source_line_end") != 537:
    raise SystemExit("statement anchor changed")
wrong_quote = SPELLING_QUOTE + "."
if target.get("original_quote") != wrong_quote:
    raise SystemExit("statement original_quote is not the expected punctuation-only mismatch")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the exact punctuation correction")
args = parser.parse_args()
print("confirmed the cited source ends the spelling claim with a comma before the DNB clause")
print("only the terminal character in this statement original_quote changes; no claim, anchor or count changes")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup}")
shutil.copy2(TABLE, backup)
target["original_quote"] = expected_quote
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
    for row in rows:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(TABLE)
print(f"applied; recovery copy: {backup.name}")
