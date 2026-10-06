#!/usr/bin/env python3
"""Controlled S2 migration for Plate 66 in the second-edition postscript."""

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
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
EXPECTED_SOURCE = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
EXPECTED_PDF = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P65 = "chp-20:20_CHP-20Postscript:l59-67"
P66 = "chp-20:20_CHP-20Postscript:l69-70"
P401 = "chp-20:20_CHP-20Postscript:l81-96"
CHP7 = "chp-7:07_CHP-7_sec_i:l224-230"
FRONT_PLATES = "front-matter:00_05_List_of_Plates:l140-172"
BACKUP_SUFFIX = ".bak-s2-chp20-plate66-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed Plate 66 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


for path, expected in ((SOURCE, EXPECTED_SOURCE), (PDF, EXPECTED_PDF)):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(x) for x in statement_path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
coverage_fields, coverage = read_csv(coverage_path)
segments = [json.loads(x) for x in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for sid in (P65, P66, P401, CHP7, FRONT_PLATES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if coverage_by_id[P65]["migration_status"] != "complete":
    raise SystemExit("Plate 65 must be complete before Plate 66")
if (coverage_by_id[P66]["disposition"], coverage_by_id[P66]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("Plate 66 must still be queued/pending")
if coverage_by_id[P401]["disposition"] != "queued":
    raise SystemExit("printed p.401 must remain queued")
if segment_by_id[P66]["sha256"] != "d9776cccc0bb851ded8c08143807d543ab316c47101db653c13ea9475a50b6c3":
    raise SystemExit("registered Plate 66 S0 hash changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text66 = "\n".join(source_lines[segment_by_id[P66]["line_start"] - 1 : segment_by_id[P66]["line_end"]])
if hashlib.sha256(text66.encode("utf-8")).hexdigest() != segment_by_id[P66]["sha256"]:
    raise SystemExit("Plate 66 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P66]["line_start"], segment_by_id[P66]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

mention_specs = [
    ("cand-1066", "Baldassare Franceschini", 70, 70, "Reuse the main Baldassare Franceschini index candidate; Plate 66 gives the artist attribution.", 0),
    ("cand-6888", "Fame carrying the name of Louis XIV to the Temple of Immortality", 70, 70, "Reuse the work candidate from chapter 7; this Plate 66 caption gives its more specific identification.", 0),
    ("cand-4186", "Fame", 70, 70, "Reuse the allegorical personification candidate from the List of Plates.", 0),
    ("cand-1447", "Louis XIV", 70, 70, "Reuse the Louis XIV index candidate.", 0),
    ("cand-4189", "Temple of Immortality", 70, 70, "Reuse the allegorical setting candidate from the List of Plates; not a geographic place.", 0),
]

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-plate66-{ordinal:03d}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or not open: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text66.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on Plate 66 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P66, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    existing_mention_ids.add(mention_id)

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_mentions] if row["segment_id"] == P66)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing Plate 66 mention spans: {left[2]} / {right[2]}")

statement = {
    "statement_id": "st-chp20-plate66-franceschini-painting-attribution",
    "segment_id": P66,
    "subject_candidate_id": "cand-6888",
    "object_candidate_id": "cand-1066",
    "predicate": "plate_caption_attributes_fame_painting_to_franceschini",
    "qualifiers": {
        "source_line_start": 70, "source_line_end": 70,
        "printed_page": None, "pdf_physical_page": 7, "plate_number": 66,
        "claim": "The Plate 66 caption attributes the painting of Fame carrying the name of Louis XIV to the Temple of Immortality to Baldassare Franceschini.",
        "speaker": "book plate caption", "text_layer": "illustration caption",
        "qualification": "Reuse the work candidate already described in chapter 7 and the personification/setting candidates from the List of Plates. This caption identifies the painting and artist; it does not establish a date, commission, medium, or present location.",
        "mentioned_candidate_ids": ["cand-6888", "cand-1066", "cand-4186", "cand-1447", "cand-4189"],
        "relation_candidate": True,
        "cross_reference_segments": [
            {"segment_id": CHP7, "source_line_start": 224, "source_line_end": 230},
            {"segment_id": FRONT_PLATES, "source_line_start": 154, "source_line_end": 155},
        ],
        "cross_reference_statement_ids": ["st-chp7-p187-i04"],
    },
    "original_quote": source_lines[69],
    "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    "origin": "book",
}

if any(row["statement_id"] == statement["statement_id"] for row in statements):
    raise SystemExit(f"statement ID already exists: {statement['statement_id']}")
if statement["original_quote"] not in text66:
    raise SystemExit("Plate 66 statement quote is not contained in the registered segment")
for cid in statement["qualifiers"]["mentioned_candidate_ids"]:
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"statement references unavailable candidate {cid}")
if not any(row.get("statement_id") == "st-chp7-p187-i04" for row in statements):
    raise SystemExit("the chapter 7 commissioning statement is missing")

coverage_by_id[P66]["disposition"] = "reviewed"
coverage_by_id[P66]["migration_status"] = "complete"
coverage_by_id[P66]["source_line_ranges"] = "L70-70"
coverage_by_id[P66]["note"] = (
    "Plate 66 (PDF physical page 7) visually checked; caption names Baldassare Franceschini and the Fame/Louis XIV allegory. "
    "Reuses the painting candidate from chapter 7 and allegorical entities from the List of Plates; no new candidate was needed."
)

candidate_backup = candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX)
mention_backup = mention_path.with_name(mention_path.name + BACKUP_SUFFIX)
statement_backup = statement_path.with_name(statement_path.name + BACKUP_SUFFIX)
coverage_backup = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
backups = [candidate_backup, mention_backup, statement_backup, coverage_backup]
if args.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("a Plate 66 recovery backup already exists; refusing overwrite")
    for original, backup in zip((candidate_path, mention_path, statement_path, coverage_path), backups):
        shutil.copy2(original, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, [*mentions, *new_mentions])
    write_jsonl(statement_path, [*statements, statement])
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied Plate 66 S2 migration; backups use suffix {BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"reused candidates: {len({x[0] for x in mention_specs})}; new candidates: 0; mentions: {len(new_mentions)}; statements: 1")
    print("caption and existing chapter 7/list-of-plates references validated")
