#!/usr/bin/env python3
"""Controlled S2 migration for Plate 68 in the second-edition postscript."""

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
P67 = "chp-20:20_CHP-20Postscript:l72-76"
P68 = "chp-20:20_CHP-20Postscript:l78-79"
P401 = "chp-20:20_CHP-20Postscript:l81-96"
FRONT_PLATES = "front-matter:00_05_List_of_Plates:l140-172"
BACKUP_SUFFIX = ".bak-s2-chp20-plate68-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed Plate 68 migration")
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

for sid in (P67, P68, P401, FRONT_PLATES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if coverage_by_id[P67]["migration_status"] != "complete":
    raise SystemExit("Plate 67 must be complete before Plate 68")
if (coverage_by_id[P68]["disposition"], coverage_by_id[P68]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("Plate 68 must still be queued/pending")
if coverage_by_id[P401]["disposition"] != "queued":
    raise SystemExit("printed p.401 must remain queued")
if segment_by_id[P68]["sha256"] != "8daa30aa7f04cd6488b22fca8dca006062bf6a4d753d9d898828a5acafc7f606":
    raise SystemExit("registered Plate 68 S0 hash changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text68 = "\n".join(source_lines[segment_by_id[P68]["line_start"] - 1 : segment_by_id[P68]["line_end"]])
if hashlib.sha256(text68.encode("utf-8")).hexdigest() != segment_by_id[P68]["sha256"]:
    raise SystemExit("Plate 68 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P68]["line_start"], segment_by_id[P68]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    ("cand-10961", "Tiepolo (Plate 68b painter credit; identity unresolved)", "person", 79,
     "The caption gives only the surname. Do not resolve the artist to a specific Tiepolo before S3."),
    ("cand-10962", "Leonardis (Plate 68b engraver credit; identity unresolved)", "person", 79,
     "The caption gives only the surname and engraving role. Do not infer a full name or institutional identity."),
    ("cand-10963", "Tiepolo composition of Maecenas presenting the Arts to Augustus (original object and medium unspecified)", "work", 79,
     "The caption attributes the composition to Tiepolo but does not identify an original object, date, medium, or location."),
    ("cand-10964", "Leonardis engraving after Tiepolo's Maecenas presenting the Arts to Augustus composition (Plate 68b)", "work", 79,
     "The caption identifies an engraving after Tiepolo; its edition, date, collection, and exact physical copy are unspecified."),
]

existing_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
for cid, name, kind, line_number, detail in candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P68}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-1489", "Francesco Maggiotto", 79, 79, "Reuse the indexed Francesco Maggiotto person candidate.", 0),
    ("cand-4190", "Three portraits of Doges", 79, 79, "Reuse the Plate 68a work candidate from the List of Plates; the three sitters remain unnamed.", 0),
    ("cand-10961", "Tiepolo", 79, 79, "Surname-only painter credit; source-specific identity remains unresolved.", 0),
    ("cand-10962", "Leonardis", 79, 79, "Surname-only engraver credit; source-specific identity remains unresolved.", 0),
    ("cand-10964", "engraved Leonardis", 79, 79, "The caption identifies the Plate 68b image as an engraving by Leonardis.", 0),
    ("cand-10963", "Mæcenas presenting the Arts to Augustus", 79, 79, "Reuse the title wording for the underlying composition; its specific original object is not identified.", 0),
    ("cand-4191", "Mæcenas", 79, 79, "Reuse the depicted Maecenas candidate from the List of Plates.", 0),
    ("cand-4193", "Arts", 79, 79, "Reuse the personified Arts candidate from the List of Plates.", 0),
    ("cand-4192", "Augustus", 79, 79, "Reuse the Roman Augustus candidate from the List of Plates; identity alignment is deferred.", 0),
]

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-plate68-{ordinal:03d}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or not open: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text68.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on Plate 68 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P68, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    existing_mention_ids.add(mention_id)

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_mentions] if row["segment_id"] == P68)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing Plate 68 mention spans: {left[2]} / {right[2]}")

def make_statement(statement_id, subject, obj, predicate, claim, ids, qualification):
    return {
        "statement_id": statement_id, "segment_id": P68,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 79, "source_line_end": 79,
            "printed_page": None, "pdf_physical_page": 9, "plate_number": 68,
            "claim": claim, "speaker": "book plate caption", "text_layer": "illustration caption",
            "qualification": qualification, "mentioned_candidate_ids": ids,
            "relation_candidate": True,
            "ocr_corrections": [{
                "source_line": 79, "ocr": "-Three portraits of Doges",
                "print": "Three portraits of Doges",
                "basis": "CHP-20Postscript.pdf physical page 9, page image and PDF text layer",
            }],
            "cross_reference_segments": [{
                "segment_id": FRONT_PLATES, "source_line_start": 158, "source_line_end": 159,
            }],
        },
        "original_quote": source_lines[78],
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement("st-chp20-plate68a-maggiotto-three-doge-portraits", "cand-4190", "cand-1489",
        "plate_caption_attributes_three_doge_portraits_to_maggiotto",
        "The Plate 68a caption attributes a group of three portraits of Doges to Francesco Maggiotto.",
        ["cand-4190", "cand-1489"],
        "The sitters are unnamed. Keep this captioned group distinct from the separate 168-portrait Maggiotto group pending identity/collection evidence."),
    make_statement("st-chp20-plate68b-tiepolo-composition", "cand-10963", "cand-10961",
        "plate_caption_attributes_maecenas_composition_to_tiepolo",
        "The Plate 68b caption attributes the composition of Maecenas presenting the Arts to Augustus to a Tiepolo identified only by surname.",
        ["cand-10963", "cand-10961", "cand-4191", "cand-4192", "cand-4193"],
        "The caption does not identify which Tiepolo or specify the original composition's medium, date, or location; the scene is iconographic, not a claim that the presentation occurred."),
    make_statement("st-chp20-plate68b-leonardis-engraving", "cand-10964", "cand-10962",
        "plate_caption_identifies_leonardis_as_engraver_after_tiepolo",
        "The Plate 68b caption identifies the reproduced image as an engraving by Leonardis after the Tiepolo composition.",
        ["cand-10964", "cand-10962", "cand-10963", "cand-10961"],
        "Leonardis is named by surname only. The engraved object is distinct from the underlying Tiepolo composition; its edition, date, and present location are unspecified."),
    make_statement("st-chp20-plate68b-maecenas-arts-augustus-scene", "cand-10964", "cand-4191",
        "plate68b_title_depicts_maecenas_presenting_arts_to_augustus",
        "The Plate 68b title describes Maecenas presenting personified Arts to Augustus in the engraved scene.",
        ["cand-10964", "cand-4191", "cand-4192", "cand-4193"],
        "Treat the caption as the scene's title and personifications; it does not establish a historical event."),
]

existing_statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    if row["statement_id"] in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {row['statement_id']}")
    existing_statement_ids.add(row["statement_id"])
    if row["original_quote"] not in text68:
        raise SystemExit(f"statement quote not contained in Plate 68 segment: {row['statement_id']}")
    for cid in row["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {cid}")

coverage_by_id[P68]["disposition"] = "reviewed"
coverage_by_id[P68]["migration_status"] = "complete"
coverage_by_id[P68]["source_line_ranges"] = "L79-79"
coverage_by_id[P68]["note"] = (
    "Plate 68 (PDF physical page 9) visually checked. Reuses the existing three-Doge portrait group and caption subjects from the List of Plates. "
    "Plate 68b is modeled as a Leonardis engraving distinct from its Tiepolo composition; surname-only artists remain unresolved."
)

backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (candidate_path, mention_path, statement_path, coverage_path)]
if args.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("a Plate 68 recovery backup already exists; refusing overwrite")
    for original, backup in zip((candidate_path, mention_path, statement_path, coverage_path), backups):
        shutil.copy2(original, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, [*mentions, *new_mentions])
    write_jsonl(statement_path, [*statements, *new_statements])
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied Plate 68 S2 migration; backups use suffix {BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("Plate 68a/68b object, artist, engraver, and allegory boundaries validated")
