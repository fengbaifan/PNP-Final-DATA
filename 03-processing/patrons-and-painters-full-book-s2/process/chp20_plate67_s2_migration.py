#!/usr/bin/env python3
"""Controlled S2 migration for Plate 67 in the second-edition postscript."""

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
P66 = "chp-20:20_CHP-20Postscript:l69-70"
P67 = "chp-20:20_CHP-20Postscript:l72-76"
P68 = "chp-20:20_CHP-20Postscript:l78-79"
CHP8 = "chp-8:08_CHP-8_sec_ii:l206-214"
BACKUP_SUFFIX = ".bak-s2-chp20-plate67-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed Plate 67 migration")
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

for sid in (P66, P67, P68, CHP8):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if coverage_by_id[P66]["migration_status"] != "complete":
    raise SystemExit("Plate 66 must be complete before Plate 67")
if (coverage_by_id[P67]["disposition"], coverage_by_id[P67]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("Plate 67 must still be queued/pending")
if coverage_by_id[P68]["disposition"] != "queued":
    raise SystemExit("Plate 68 must remain queued")
if segment_by_id[P67]["sha256"] != "e99af189bd790a59d794f111809774b65537ba3e9bc05fc218389b5d0028f0e6":
    raise SystemExit("registered Plate 67 S0 hash changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text67 = "\n".join(source_lines[segment_by_id[P67]["line_start"] - 1 : segment_by_id[P67]["line_end"]])
if hashlib.sha256(text67.encode("utf-8")).hexdigest() != segment_by_id[P67]["sha256"]:
    raise SystemExit("Plate 67 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P67]["line_start"], segment_by_id[P67]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

mention_specs = [
    ("cand-0879", "def eb ot setnabyroC eht ot elebyC yb revo dednah retipuJ", 73, 73, "The OCR reverses the Plate 67 title; page image and PDF text layer read ‘Jupiter handed over by Cybele to the Corybantes to be fed’. Reuse the index work subentry from p.228.", 0),
    ("cand-4178", "retipuJ", 73, 73, "Reversed OCR surface for Jupiter; reuse the mythological person candidate from the List of Plates.", 0),
    ("cand-4187", "elebyC", 73, 73, "Reversed OCR surface for Cybele; reuse the mythological person candidate from the List of Plates.", 0),
    ("cand-4188", "setnabyroC", 73, 73, "Reversed OCR surface for the Corybantes; preserve them as a mythological group.", 0),
    ("cand-0871", "ipser", 74, 74, "OCR fragment of Crespi, reversed and missing a character; the page image and PDF text layer confirm the artist credit.", 0),
    ("cand-0871", "C.M", 75, 75, "OCR fragment of the artist’s initials, split from the surname.", 0),
    ("cand-0871", ".G", 76, 76, "Final OCR fragment of the reversed initials; visually read with L75 as ‘G. M.’.", 0),
]

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-plate67-{ordinal:03d}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or not open: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text67.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on Plate 67 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P67, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    existing_mention_ids.add(mention_id)

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_mentions] if row["segment_id"] == P67)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing Plate 67 mention spans: {left[2]} / {right[2]}")

statement = {
    "statement_id": "st-chp20-plate67-crespi-jupiter-cybele",
    "segment_id": P67,
    "subject_candidate_id": "cand-0871",
    "object_candidate_id": "cand-0879",
    "predicate": "plate_caption_attributes_jupiter_cybele_painting_to_crespi",
    "qualifiers": {
        "source_line_start": 73, "source_line_end": 76,
        "printed_page": None, "pdf_physical_page": 8, "plate_number": 67,
        "claim": "The Plate 67 caption attributes to G. M. Crespi a painting of Jupiter being handed over by Cybele to the Corybantes to be fed.",
        "speaker": "book plate caption", "text_layer": "illustration caption",
        "qualification": "The OCR reverses the title and splits the initials and surname; the caption is transcribed from the page image and PDF text layer. Reuse the p.228 index candidate and the mythology candidates from the List of Plates; the caption does not give a date, medium, or present location.",
        "mentioned_candidate_ids": ["cand-0871", "cand-0879", "cand-4178", "cand-4187", "cand-4188"],
        "relation_candidate": True,
        "ocr_corrections": [{
            "source_lines": "L73-L76",
            "ocr": "\n".join(source_lines[72:76]),
            "print": "G. M. Crespi: Jupiter handed over by Cybele to the Corybantes to be fed",
            "basis": "CHP-20Postscript.pdf physical page 8, page image and PDF text layer",
        }],
        "cross_reference_segments": [{"segment_id": CHP8, "source_line_start": 206, "source_line_end": 214}],
        "cross_reference_statement_ids": [
            "st-chp8-p228-crespi-chosen-subject-sketch",
            "st-chp8-p228-crespi-retitles-finding-of-moses",
        ],
    },
    "original_quote": "\n".join(source_lines[72:76]),
    "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    "origin": "book",
}

if any(row["statement_id"] == statement["statement_id"] for row in statements):
    raise SystemExit(f"statement ID already exists: {statement['statement_id']}")
if statement["original_quote"] not in text67:
    raise SystemExit("Plate 67 statement quote is not contained in the registered segment")
for cid in statement["qualifiers"]["mentioned_candidate_ids"]:
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"statement references unavailable candidate {cid}")
for sid in statement["qualifiers"]["cross_reference_statement_ids"]:
    if not any(row.get("statement_id") == sid for row in statements):
        raise SystemExit(f"missing cross-reference statement: {sid}")

coverage_by_id[P67]["disposition"] = "reviewed"
coverage_by_id[P67]["migration_status"] = "complete"
coverage_by_id[P67]["source_line_ranges"] = "L73-76"
coverage_by_id[P67]["note"] = (
    "Plate 67 (PDF physical page 8) visually checked; raw OCR reverses the title and splits the artist credit. "
    "Corrected caption text remains in statement metadata; no new work candidate was created because the index and p.228 text already register it."
)

backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (candidate_path, mention_path, statement_path, coverage_path)]
if args.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("a Plate 67 recovery backup already exists; refusing overwrite")
    for original, backup in zip((candidate_path, mention_path, statement_path, coverage_path), backups):
        shutil.copy2(original, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, [*mentions, *new_mentions])
    write_jsonl(statement_path, [*statements, statement])
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied Plate 67 S2 migration; backups use suffix {BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print("reused candidates: 5; new candidates: 0; mentions: 7; statements: 1")
    print("caption OCR and the chapter 8 work identity were validated")
