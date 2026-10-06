#!/usr/bin/env python3
"""Add three missed institutional mentions found by the p.399 surface audit."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
P399 = "chp-20:20_CHP-20Postscript:l38-44"
EXPECTED_SOURCE = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
EXPECTED_SEGMENT = "38b28c432e7d2451ab366543fb1f16f675b2e391192879bc0f160b4f9662b1d7"
BACKUP_SUFFIX = ".bak-s2-chp20-p399-mention-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

source_bytes = SOURCE.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_SOURCE:
    raise SystemExit("postscript source changed; refusing mention repair")
segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment = next((row for row in segments if row["segment_id"] == P399), None)
if segment is None or segment["sha256"] != EXPECTED_SEGMENT:
    raise SystemExit("registered p.399 segment changed")
source_lines = source_bytes.decode("utf-8-sig").splitlines()
text = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
if hashlib.sha256(text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT:
    raise SystemExit("p.399 segment text changed")

expected = [
    ("m-chp20-p399-050", 1979, "Haskell recalls the Jesuits accepting powerful patrons’ choices."),
    ("m-chp20-p399-051", 2851, "The article is partly concerned with Bernini’s relationship to the Jesuits; split the institution mention from the nested article span."),
    ("m-chp20-p399-052", 3242, "Haskell retracts his earlier hypothesis about the Jesuits rejecting the Blood of Christ theme."),
]
for mention_id, start, _note in expected:
    if text[start : start + len("Jesuits")] != "Jesuits":
        raise SystemExit(f"source anchor changed for {mention_id}: {start}")

with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    mentions = list(reader)
if not fields:
    raise SystemExit("mentions table has no header")
if any(row["mention_id"] in {item[0] for item in expected} for row in mentions):
    raise SystemExit("repair mention ID already exists")
if not any(row["candidate_id"] == "cand-3403" and row["status"] == "open"
           for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))):
    raise SystemExit("institution candidate cand-3403 is not available")

new_rows = [{
    "mention_id": mention_id,
    "segment_id": P399,
    "candidate_id": "cand-3403",
    "surface_form": "Jesuits",
    "start_char": str(start),
    "end_char": str(start + len("Jesuits")),
    "note": note,
} for mention_id, start, note in expected]

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_rows] if row["segment_id"] == P399)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing p.399 spans: {left[2]} / {right[2]}")

if args.apply:
    backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup exists; refusing overwrite: {backup.name}")
    shutil.copy2(MENTIONS, backup)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=MENTIONS.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows([*mentions, *new_rows])
        temporary = Path(stream.name)
    temporary.replace(MENTIONS)
    print(f"applied {len(new_rows)} mention repairs; backup: {backup.name}")
else:
    print(f"DRY RUN: no files written; validated {len(new_rows)} p.399 mention repairs")
    for row in new_rows:
        print(f"{row['mention_id']}: {row['surface_form']} @ {row['start_char']}:{row['end_char']} — {row['note']}")
