#!/usr/bin/env python3
"""Add the missed fourth Canaletto mention on printed p.407."""
import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
SEGMENT = "chp-20:20_CHP-20Postscript:l164-172"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
SEGMENT_SHA = "b9b3ba9f777bdcf5d0af79db02511e032f706f6927605ead0717e7c7180e92f0"
MENTIONS_SHA = "5369e2d527f2d215e20008b86748ad3dd4878618abca3d2fedc357f9cca24815"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp20-p407-canaletto-mention-20261004")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated repair")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

if sha(SOURCE.read_bytes()) != SOURCE_SHA:
    raise SystemExit("source file changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[163:172])
if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
    raise SystemExit("p.407 segment hash mismatch")
if segment_text[732:741] != "Canaletto":
    raise SystemExit("expected Canaletto span does not match source")
if sha(TABLE.read_bytes()) != MENTIONS_SHA:
    raise SystemExit("mentions table changed since the reviewed state")

with TABLE.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, rows = reader.fieldnames, list(reader)
if any(r["segment_id"] == SEGMENT and r["start_char"] == "732" for r in rows):
    raise SystemExit("p.407 offset 732 already has a mention")
if not any(r["mention_id"] == "m-chp20-p407-045" for r in rows):
    raise SystemExit("expected p.407 mention sequence is not present")
new_row = {
    "mention_id": "m-chp20-p407-046",
    "segment_id": SEGMENT,
    "candidate_id": "cand-0498",
    "surface_form": "Canaletto",
    "start_char": "732",
    "end_char": "741",
    "note": "Fourth printed occurrence on p.407; the artist is described as altering the earlier Venice view in 1751.",
}
rows.append(new_row)
print("DRY RUN: add m-chp20-p407-046 -> cand-0498 at chars 732-741 (Canaletto)")
if not args.apply:
    raise SystemExit(0)
if BACKUP.exists():
    raise SystemExit(f"backup already exists: {BACKUP.name}")
shutil.copy2(TABLE, BACKUP)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    temp = Path(handle.name)
temp.replace(TABLE)
print(f"APPLIED: {TABLE.relative_to(ROOT)}; backup={BACKUP.name}; rows={len(rows)}")
