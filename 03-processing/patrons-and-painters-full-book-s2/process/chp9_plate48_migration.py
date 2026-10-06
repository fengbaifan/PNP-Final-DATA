"""Controlled S2 migration for chapter 9 Plate 48; defaults to read-only dry run."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
OCR_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
VISUAL_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro_plates_visual-transcription.md"
OCR_SEGMENT = "chp-9:09_CHP-9_intro:l287-289"
VISUAL_SEGMENT = "chp-9:09_CHP-9_intro_plates_visual-transcription:l13-15"
EXPECTED_OCR_SEGMENT = "901ce0b067740a09bc0d3fd6685e54390d90e003c8297f16966567b184e54b6b"
EXPECTED_VISUAL_SEGMENT = "77ba6751adfa5ebddfae7e9d996b6bad88cc6017eb3eb6f7a7ae07e167f65eb0"
EXPECTED_VISUAL_ASSET = "1e37527d1115bf27159527ba08d832f30a2ac551b41b5e954c7de93f72a88857"
SEGMENT_BACKUP = TABLES / "segments.jsonl.bak-s2-chp9-plate48-s0-20261001"
BACKUP_SUFFIX = ".bak-s2-chp9-plate48-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if not SEGMENT_BACKUP.is_file():
    raise SystemExit("required recovery copy for the S0 segment rebuild is missing")
if hashlib.sha256(VISUAL_SOURCE.read_bytes()).hexdigest() != EXPECTED_VISUAL_ASSET:
    raise SystemExit("Plate 48 visual-transcription source asset changed")
visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_lines = [
    "Venetian patrons during the first half of the eighteenth century",
    "a. Pitteri: Flaminio Corner",
    "b. Faldoni: Zaccaria Sagredo",
]
if visual_lines[12:15] != expected_lines:
    raise SystemExit("Plate 48 visual transcription is missing or changed")

segment_path = TABLES / "segments.jsonl"
segments = read_jsonl(segment_path)
segment_by_id = {r["segment_id"]: r for r in segments}
ocr_meta = segment_by_id.get(OCR_SEGMENT)
visual_meta = segment_by_id.get(VISUAL_SEGMENT)
if not ocr_meta or ocr_meta.get("sha256") != EXPECTED_OCR_SEGMENT:
    raise SystemExit("Plate 48 OCR segment missing or changed")
if not visual_meta or visual_meta.get("sha256") != EXPECTED_VISUAL_SEGMENT or visual_meta.get("asset_sha256") != EXPECTED_VISUAL_ASSET:
    raise SystemExit("Plate 48 visual segment missing or changed")
if hashlib.sha256(OCR_SOURCE.read_bytes()).hexdigest() != ocr_meta["asset_sha256"]:
    raise SystemExit("chapter 9 OCR source asset changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {r["candidate_id"] for r in candidates}
used_candidate_ids = {"cand-4053", "cand-3830", "cand-3764", "cand-4044", "cand-3782", "cand-3901"}
if not used_candidate_ids <= candidate_ids:
    raise SystemExit(f"existing Plate 48 candidates are missing: {used_candidate_ids - candidate_ids}")

coverage_by_id = {r["segment_id"]: r for r in coverage}
ocr_cov = coverage_by_id.get(OCR_SEGMENT)
if not ocr_cov or (ocr_cov["disposition"], ocr_cov["migration_status"], ocr_cov["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"unexpected Plate 48 OCR coverage: {ocr_cov}")
if VISUAL_SEGMENT in coverage_by_id:
    raise SystemExit("Plate 48 visual segment already has a coverage decision")

visual_segment_text = "\n".join(visual_lines[12:15])
line14_start = len(visual_lines[12]) + 1
line15_start = line14_start + len(visual_lines[13]) + 1
mentions_by_segment = {m["segment_id"] for m in mentions}
new_mentions = []
for plate, line, base_offset, artist_id, sitter_id, work_id, artist, sitter, work_surface in [
    ("48a", visual_lines[13], line14_start, "cand-3830", "cand-3764", "cand-4053", "Pitteri", "Flaminio Corner", "Pitteri: Flaminio Corner"),
    ("48b", visual_lines[14], line15_start, "cand-3782", "cand-3901", "cand-4044", "Faldoni", "Zaccaria Sagredo", "Faldoni: Zaccaria Sagredo"),
]:
    spans = [
        (f"m-chp9-plate{plate}-work", work_id, work_surface,
         "Caption identifies the pictured portrait; this wording is not asserted to be a formal work title."),
        (f"m-chp9-plate{plate}-artist", artist_id, artist,
         "Surname-only attribution in the printed Plate 48 caption; reuse the existing candidate and defer global identity alignment."),
        (f"m-chp9-plate{plate}-sitter", sitter_id, sitter,
         "Named sitter in the printed Plate 48 caption; reuse the existing candidate and defer global identity alignment."),
    ]
    line_offset = base_offset
    for mention_id, candidate_id, surface, note in spans:
        if any(m["mention_id"] == mention_id for m in mentions):
            raise SystemExit(f"duplicate mention id: {mention_id}")
        local_start = line.find(surface)
        if local_start < 0 or line.find(surface, local_start + len(surface)) >= 0:
            raise SystemExit(f"surface is missing or ambiguous in Plate {plate}: {surface}")
        start = line_offset + local_start
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": VISUAL_SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })

existing_statement_ids = {r["statement_id"] for r in statements}
new_statements = []
for plate, line_number, line, artist_id, sitter_id, work_id, artist, sitter, work_surface, crossrefs in [
    ("48a", 14, visual_lines[13], "cand-3830", "cand-3764", "cand-4053", "Pitteri", "Flaminio Corner", "Pitteri: Flaminio Corner", [
        {"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 126, "source_line_end": 126},
    ]),
    ("48b", 15, visual_lines[14], "cand-3782", "cand-3901", "cand-4044", "Faldoni", "Zaccaria Sagredo", "Faldoni: Zaccaria Sagredo", [
        {"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 126, "source_line_end": 126},
        {"segment_id": "chp-9:09_CHP-9_intro:l231-238", "source_line_start": 233, "source_line_end": 233},
    ]),
]:
    for suffix, object_id, predicate, claim, qualification in [
        (
            "attribution", artist_id, "caption_attribution",
            f"The Plate {plate} caption credits {artist} with a portrait of {sitter}.",
            "The caption identifies the maker and sitter of the pictured reproduction but does not provide a formal work title; no external attribution or identity judgment is added.",
        ),
        (
            "subject", sitter_id, "caption_subject",
            f"The Plate {plate} caption names {sitter} as the subject of the pictured portrait.",
            "The sitter is identified by the printed caption; the pictured reproduction is represented by the existing work candidate, without asserting that the caption wording is its formal title.",
        ),
    ]:
        statement_id = f"st-chp9-plate{plate}-{suffix}"
        if statement_id in existing_statement_ids:
            raise SystemExit(f"duplicate statement id: {statement_id}")
        new_statements.append({
            "statement_id": statement_id,
            "segment_id": VISUAL_SEGMENT,
            "subject_candidate_id": work_id,
            "object_candidate_id": object_id,
            "predicate": predicate,
            "qualifiers": {
                "source_line_start": line_number,
                "source_line_end": line_number,
                "plate_number": 48,
                "plate_label": plate,
                "pdf_physical_page": 30,
                "claim": claim,
                "speaker": "printed plate caption",
                "text_layer": "visual transcription",
                "qualification": qualification,
                "mentioned_candidate_ids": [work_id, artist_id, sitter_id],
                "relation_candidate": True,
                "cross_reference_segments": crossrefs,
            },
            "original_quote": line,
            "source_file": VISUAL_SOURCE.relative_to(ROOT).as_posix(),
            "origin": "book",
        })

for row in new_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if visual_segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    refs = {row["subject_candidate_id"], row["object_candidate_id"], *q["mentioned_candidate_ids"]}
    if not refs <= candidate_ids:
        raise SystemExit(f"statement foreign key mismatch: {row['statement_id']}")
    if row["original_quote"] != visual_lines[q["source_line_start"] - 1]:
        raise SystemExit(f"statement quote mismatch: {row['statement_id']}")

ocr_cov.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L287-289",
    "note": "no_semantic_content: OCR caption fragments are corrupted; Plate 48a-b caption text is represented in the derived visual transcription at L14-15. The two lower portraits and their inscriptions were inspected; the inscription text is not reliably legible here. CHP-9.pdf physical p.30 was reviewed and the OCR source remains unchanged.",
})
coverage_by_id[VISUAL_SEGMENT] = {
    "chapter": "chp-9",
    "segment_id": VISUAL_SEGMENT,
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L13-15",
    "note": "Plate 48 heading is editorial navigation metadata. Captions a-b were visually transcribed and migrated. Four portraits are visible; c-d caption/inscription text is not reliably legible on this reproduction, and their structured identities are represented by the separately processed List of Plates rather than inferred from unreadable marks.",
}

summary = {
    "new_candidates": 0,
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_rows_added": 1,
    "ocr_segment": ["reviewed", "complete"],
    "visual_segment": VISUAL_SEGMENT,
    "next_segment": "chp-9:09_CHP-9_intro:l291-301 (p.265; includes p.264 note 8 continuation)",
    "counts": {
        "candidates": len(candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements),
        "coverage_rows": len(coverage_by_id),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [mention_path, statement_path, coverage_path]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
