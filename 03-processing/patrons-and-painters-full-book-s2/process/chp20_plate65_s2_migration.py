#!/usr/bin/env python3
"""Controlled S2 migration for the Plate 65 captions in the second-edition postscript."""

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
P400 = "chp-20:20_CHP-20Postscript:l46-57"
P65 = "chp-20:20_CHP-20Postscript:l59-67"
P401 = "chp-20:20_CHP-20Postscript:l81-96"
BACKUP_SUFFIX = ".bak-s2-chp20-plate65-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed Plate 65 migration")
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

for sid in (P400, P65, P401):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if (coverage_by_id[P400]["disposition"], coverage_by_id[P400]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.400 must remain reviewed/partial while the sentence continues")
if (coverage_by_id[P65]["disposition"], coverage_by_id[P65]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("Plate 65 must still be queued/pending")
if coverage_by_id[P401]["disposition"] != "queued":
    raise SystemExit("printed p.401 must remain queued")
if segment_by_id[P65]["sha256"] != "b85d7784ee94a159b26fe13f4d1a1969292cda57b417db9fa8d42799b5d64e27":
    raise SystemExit("registered Plate 65 S0 hash changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text65 = "\n".join(source_lines[segment_by_id[P65]["line_start"] - 1 : segment_by_id[P65]["line_end"]])
if hashlib.sha256(text65.encode("utf-8")).hexdigest() != segment_by_id[P65]["sha256"]:
    raise SystemExit("Plate 65 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P65]["line_start"], segment_by_id[P65]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    ("cand-10957", "Joint caricature of Simonelli and Mola (Plate 65a; object details unspecified)", "work", 64,
     "The plate caption identifies a joint caricature but supplies no date, medium, repository, or independently verified object identity."),
    ("cand-10958", "Agostino Masucci image of Mola painting Pope Alexander VII (Plate 65b; title and medium unspecified)", "work", 60,
     "The caption identifies the depicted scene and artist, but provides no date, medium, repository, or fuller title."),
    ("cand-10959", "Agostino Masucci", "person", 62,
     "Named as the artist of Plate 65b; S0 OCR splits and reverses the printed credit, which is confirmed by the page image and PDF text layer."),
    ("cand-10960", "Unspecified portrait of Pope Alexander VII shown being painted by Mola in Plate 65b", "work", 60,
     "The caption describes Mola painting a portrait; whether the depicted portrait was completed or survives is not established."),
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
        "candidate_source_ref": f"{P65}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-10957", "erutacirac tnioJ", 64, 64, "Reversed OCR fragment visually transcribed as ‘Joint caricature’ in Plate 65a.", 0),
    ("cand-1676", "aloM", 60, 60, "Reversed OCR surface for Pier Francesco Mola in the Plate 65b caption; S3 will align duplicate index entries.", 0),
    ("cand-1676", "alo", 65, 65, "Truncated reversed OCR fragment for Mola in the Plate 65a credit/title; the page image and PDF text layer confirm the name.", 0),
    ("cand-2434", "illenomiS", 65, 65, "Reversed OCR surface for Simonelli in the Plate 65a caption.", 0),
    ("cand-1676", "aloM", 67, 67, "Reversed OCR surface for Mola in the Plate 65a caption.", 0),
    ("cand-2434", "illenomiS", 67, 67, "Second reversed OCR occurrence of Simonelli in the Plate 65a caption.", 0),
    ("cand-10958", "tiartrop eht gnitniap", 60, 60, "Reversed OCR surface for ‘painting the portrait’ in the Plate 65b description.", 0),
    ("cand-10959", "iccusa", 62, 62, "Reversed OCR fragment of the printed Masucci credit; confirmed visually and in PDF text extraction.", 0),
    ("cand-10959", "Monitsog", 63, 63, "OCR fragment of the printed Agostino credit, with letters reversed and missegmented; page image and PDF text layer confirm the reading.", 0),
    ("cand-10959", "Ma", 66, 66, "OCR fragment of the Masucci credit, confirmed from the full caption on the page image.", 0),
    ("cand-10960", "tiartrop", 60, 60, "Nested reversed OCR fragment for ‘portrait’; the caption does not establish completion or survival.", 0),
    ("cand-0665", "IIV rednaxelA epoP", 67, 67, "Reversed OCR surface for Pope Alexander VII; reuse the index candidate whose page range includes p.401.", 0),
]

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-plate65-{ordinal:03d}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or not open: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text65.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on Plate 65 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P65, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    existing_mention_ids.add(mention_id)

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_mentions] if row["segment_id"] == P65)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing Plate 65 mention spans: {left[2]} / {right[2]}")

RAW_CAPTION = "\n".join(source_lines[59:67])
CORRECTIONS = [{
    "source_lines": "L60-L67",
    "ocr": RAW_CAPTION,
    "print": "a Mola and Simonelli: Joint caricature of Simonelli and Mola; b Agostino Masucci: Mola painting the portrait of Pope Alexander VII",
    "basis": "CHP-20Postscript.pdf physical page 6, page image and PDF text layer",
}]


def make_statement(statement_id, subject, obj, predicate, claim, first, last, candidate_ids, qualification):
    return {
        "statement_id": statement_id, "segment_id": P65,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": first, "source_line_end": last,
            "printed_page": None, "pdf_physical_page": 6,
            "plate_number": 65, "claim": claim,
            "speaker": "book plate caption", "text_layer": "illustration caption",
            "qualification": qualification,
            "mentioned_candidate_ids": candidate_ids,
            "relation_candidate": True,
            "ocr_corrections": CORRECTIONS,
        },
        "original_quote": "\n".join(source_lines[first - 1 : last]),
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement("st-chp20-plate65a-joint-caricature", "cand-10957", "cand-1676",
        "plate_caption_identifies_joint_caricature_of_mola_and_simonelli",
        "The Plate 65a caption identifies a joint caricature of Simonelli and Mola and credits it to Mola and Simonelli.",
        64, 65, ["cand-10957", "cand-1676", "cand-2434"],
        "The caption supports a joint attribution and identifies both caricature subjects. Date, medium, repository, and independently verified object identity are not supplied; reversed OCR has been visually corrected in the qualifier."),
    make_statement("st-chp20-plate65b-masucci-credit", "cand-10958", "cand-10959",
        "plate_caption_credits_masucci_as_artist",
        "The Plate 65b caption credits Agostino Masucci with the image of Mola painting the portrait of Pope Alexander VII.",
        60, 67, ["cand-10958", "cand-10959", "cand-1676", "cand-0665", "cand-10960"],
        "The OCR fragments are interleaved because the caption is rotated in the scan; the page image and PDF text layer confirm the normalized reading. The depicted portrait’s completion and survival are unknown."),
    make_statement("st-chp20-plate65b-depicted-portrait", "cand-10958", "cand-10960",
        "plate_caption_depicts_mola_painting_alexander_vii_portrait",
        "The Plate 65b caption describes Mola painting a portrait of Pope Alexander VII within Masucci’s image.",
        60, 67, ["cand-10958", "cand-10960", "cand-1676", "cand-0665"],
        "This records the scene described by the caption and does not assert that the portrait was completed, survives, or is independently identified."),
]

statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    if row["statement_id"] in statement_ids:
        raise SystemExit(f"statement ID already exists: {row['statement_id']}")
    statement_ids.add(row["statement_id"])
    if row["original_quote"] not in text65:
        raise SystemExit(f"statement quote not contained in Plate 65 segment: {row['statement_id']}")
    for cid in row["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {cid}")

coverage_by_id[P65]["disposition"] = "reviewed"
coverage_by_id[P65]["migration_status"] = "complete"
coverage_by_id[P65]["source_line_ranges"] = "L60-67"
coverage_by_id[P65]["note"] = (
    "Plate 65 (PDF physical page 6) visually read and cross-checked against the PDF text layer. "
    "The Markdown OCR reverses and fragments rotated captions; original OCR remains unchanged, "
    "while corrected caption text and exact OCR surfaces are recorded in statements and mentions. "
    "Plate 65a describes a joint caricature of Simonelli and Mola; Plate 65b depicts Mola painting Pope Alexander VII's portrait."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, [*mentions, *new_mentions])
    write_jsonl(statement_path, [*statements, *new_statements])
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied Plate 65 S2 migration; backups use suffix {BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("captions were normalized from PDF physical page 6 while raw S0 OCR remains unchanged")
