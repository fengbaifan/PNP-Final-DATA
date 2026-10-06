#!/usr/bin/env python3
"""Add p.392 spans identified by the chapter candidate-surface review."""

import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
SEGMENT_ID = "chp-19:19_CHP-19Appendix:l126-138"
EXPECTED_SOURCE_HASH = "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1"
EXPECTED_PDF_HASH = "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb"
BACKUP_SUFFIX = ".bak-s2-chp19-p392-surface-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed span repair")
args = parser.parse_args()

for path, expected in ((SOURCE, EXPECTED_SOURCE_HASH), (PDF, EXPECTED_PDF_HASH)):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

segment_rows = [
    __import__("json").loads(line)
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()
]
segment = next((row for row in segment_rows if row["segment_id"] == SEGMENT_ID), None)
if not segment:
    raise SystemExit("S0 p.392 segment is missing")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("p.392 segment hash mismatch")

mention_path = TABLES / "mentions.csv"
with mention_path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
segment_mentions = [row for row in rows if row["segment_id"] == SEGMENT_ID]
if len(segment_mentions) != 40:
    raise SystemExit(f"expected 40 existing p.392 mentions; found {len(segment_mentions)}")

candidate_path = TABLES / "entity-candidates.csv"
with candidate_path.open(encoding="utf-8-sig", newline="") as stream:
    candidates = {row["candidate_id"]: row for row in csv.DictReader(stream)}
specs = [
    ("m-chp19-p392-041", "cand-8983", "England", 128, 1,
     "Second England reference in the 1761–1762 plans paragraph: Smith's reported plan to return; not evidence he moved."),
    ("m-chp19-p392-042", "cand-8983", "England", 131, 0,
     "England in Haskell's summary of the unresolved report about pictures taken by Smith's widow."),
    ("m-chp19-p392-043", "cand-7386", "Biblioteca Comunale, Bologna", 134, 0,
     "Repository named for the cited MS B.153 letter; the Bologna place is separately mentioned for the unknown correspondent."),
]
existing_ids = {row["mention_id"] for row in rows}
line_offsets = {}
offset = 0
for line_number, line in zip(range(segment["line_start"], segment["line_end"] + 1), segment_text.split("\n")):
    line_offsets[line_number] = offset
    offset += len(line) + 1

new_rows = []
for mention_id, candidate_id, surface, line_number, occurrence, note in specs:
    if mention_id in existing_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    candidate = candidates.get(candidate_id)
    if not candidate or candidate.get("status") != "open":
        raise SystemExit(f"candidate unavailable for {mention_id}: {candidate_id}")
    source_line = source_lines[line_number - 1]
    cursor = 0
    start_in_line = -1
    for _ in range(occurrence + 1):
        start_in_line = source_line.find(surface, cursor)
        if start_in_line < 0:
            raise SystemExit(f"span not found on line {line_number}: {surface!r}")
        cursor = start_in_line + 1
    start = line_offsets[line_number] + start_in_line
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"span mismatch: {mention_id}")
    new_rows.append({
        "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    existing_ids.add(mention_id)

if any(
    int(new["start_char"]) < int(old["end_char"]) and int(old["start_char"]) < int(new["end_char"])
    for new in new_rows for old in segment_mentions
):
    raise SystemExit("new span crosses an existing p.392 mention")

rows.extend(new_rows)
if args.apply:
    backup = mention_path.with_name(mention_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
    shutil.copy2(mention_path, backup)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=mention_path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(mention_path)
    print(f"applied {len(new_rows)} p.392 spans; backup: {backup.name}")
else:
    print("DRY RUN: no files written")
    for row in new_rows:
        print(row["mention_id"], row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"])
