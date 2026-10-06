#!/usr/bin/env python3
"""Repair the p.408/p.409 statement anchor after the p.409 migration."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
STATEMENTS = TABLES / "book-statements.jsonl"
P408 = "chp-20:20_CHP-20Postscript:l174-185"
P409 = "chp-20:20_CHP-20Postscript:l187-199"
STATEMENT_ID = "st-chp20-p408-parker-piccinio-engraving-models-partial"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP = ".bak-s2-chp20-p409-crosspage-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def digest(data):
    return hashlib.sha256(data).hexdigest()

if digest(SOURCE.read_bytes()) != SOURCE_SHA or digest(PDF.read_bytes()) != PDF_SHA:
    raise SystemExit("source or PDF changed")
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
raw = STATEMENTS.read_text(encoding="utf-8-sig")
rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
row = next((item for item in rows if item.get("statement_id") == STATEMENT_ID), None)
if row is None or row.get("segment_id") != P408:
    raise SystemExit("target p.408 statement is missing or moved")
q = row.get("qualifiers", {})
if q.get("source_line_start") != 185 or q.get("source_line_end") != 188:
    raise SystemExit("target statement is not in the expected pre-repair state")
if row.get("original_quote") != "\n".join((lines[184], lines[187])):
    raise SystemExit("target quote differs from the expected cross-page quote")
refs = q.get("cross_reference_segments", [])
if not any(item.get("segment_id") == P409 for item in refs):
    raise SystemExit("p.409 continuation reference is missing")

q["source_line_end"] = 185
q["cross_reference_segments"] = [
    {"segment_id": item["segment_id"], "source_line_start": 188, "source_line_end": 188}
    if item.get("segment_id") == P409 else item
    for item in refs
]
row["original_quote"] = lines[184]
new_raw = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in rows)
if new_raw == raw:
    raise SystemExit("repair would make no change")

print("DRY RUN" if not args.apply else "APPLY", STATEMENT_ID)
print("  source anchor: L185-L188 -> L185")
print("  continuation anchor: p.409 L187-L199 -> p.409 L188")
print("  original_quote: two page fragments -> p.408 L185 only")
if args.apply:
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP)
    if backup.exists():
        raise SystemExit("recovery backup already exists")
    shutil.copy2(STATEMENTS, backup)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENTS.parent, delete=False) as handle:
        handle.write(new_raw)
        temp = Path(handle.name)
    temp.replace(STATEMENTS)
    print(f"APPLIED; backup={backup.name}")
