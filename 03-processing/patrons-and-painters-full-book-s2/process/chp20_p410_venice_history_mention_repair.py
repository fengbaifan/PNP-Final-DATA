#!/usr/bin/env python3
"""Add the missing place mention in the nineteenth-century Venice statement."""
import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
P410 = "chp-20:20_CHP-20Postscript:l201-209"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP = ".bak-s2-chp20-p410-venice-history-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def digest(data):
    return hashlib.sha256(data).hexdigest()

if digest(SOURCE.read_bytes()) != SOURCE_SHA or digest(PDF.read_bytes()) != PDF_SHA:
    raise SystemExit("source or PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[200:209])
segment_rows = [__import__("json").loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment = next((row for row in segment_rows if row["segment_id"] == P410), None)
if segment is None or digest(segment_text.encode("utf-8")) != segment["sha256"]:
    raise SystemExit("p.410 segment changed")

path = TABLES / "mentions.csv"
with path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, rows = reader.fieldnames, list(reader)
if any(row["mention_id"] == "m-chp20-p410-027" for row in rows):
    raise SystemExit("repair mention ID already exists")
if not any(row["candidate_id"] == "cand-3401" for row in rows):
    raise SystemExit("Venice place candidate is missing")

line_start = sum(len(source_lines[n - 1]) + 1 for n in range(201, 209))
line_end = line_start + len(source_lines[208])
start = segment_text.find("Venice", line_start, line_end)
if start < 0:
    raise SystemExit("nineteenth-century Venice is not present on p.410 L209")
end = start + len("Venice")
if any(row["segment_id"] == P410 and row["candidate_id"] == "cand-3401"
       and int(row["start_char"]) == start and int(row["end_char"]) == end for row in rows):
    raise SystemExit("exact Venice title mention already exists")
new_row = {"mention_id": "m-chp20-p410-027", "segment_id": P410, "candidate_id": "cand-3401",
           "surface_form": "Venice", "start_char": str(start), "end_char": str(end),
           "note": "Place named in the description of nineteenth-century Venetian history; maps to the existing Venice candidate."}
print(f"{'APPLY' if args.apply else 'DRY RUN'} {new_row['mention_id']} at chars {start}-{end}")
if args.apply:
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit("recovery backup already exists")
    shutil.copy2(path, backup)
    rows.append(new_row)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)
    print(f"APPLIED; backup={backup.name}")
