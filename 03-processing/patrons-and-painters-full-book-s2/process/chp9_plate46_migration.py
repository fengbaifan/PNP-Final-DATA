"""Controlled S2 migration for chapter 9 Plate 46; defaults to read-only dry run."""
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
OCR_SEGMENT = "chp-9:09_CHP-9_intro:l258-277"
VISUAL_SEGMENT = "chp-9:09_CHP-9_intro_plates_visual-transcription:l8-9"
EXPECTED_OCR_SEGMENT = "bccf0575ee1133067f3dbe8b859f91326d115b0f67520f0e77efaacfc358a618"
EXPECTED_VISUAL_SEGMENT = "4dc74001aac09cca5fe9521b8fa2127e49f5c6732c927ff6442d20183ed72167"
EXPECTED_VISUAL_ASSET = "8a8401c8c87e2579695f9dbd11df1624c115b203a5c2a5e6a9ae0f7f087188d9"
BACKUP_SUFFIX = ".bak-s2-chp9-plate46-20261001"
SEGMENT_BACKUP = TABLES / "segments.jsonl.bak-s2-chp9-plate46-s0-20261001"
OCR_NOTE = (
    "no_semantic_content: The OCR segment contains reversed glyph fragments for the Plate 46 editorial heading and caption; "
    "both are represented in derived visual-transcription lines 8-9. Consolidated notes L428 repeats the editorial heading "
    "and is excluded as duplicate OCR. CHP-9.pdf physical p.28 was reviewed; the OCR source remains unchanged."
)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if not SEGMENT_BACKUP.exists():
    raise SystemExit("required recovery copy for the S0 segment rebuild is missing")
ocr_bytes = OCR_SOURCE.read_bytes()
visual_bytes = VISUAL_SOURCE.read_bytes()
if hashlib.sha256(visual_bytes).hexdigest() != EXPECTED_VISUAL_ASSET:
    raise SystemExit("visual-transcription source asset changed")
visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
if len(visual_lines) < 9 or visual_lines[7] != (
    "Venetian artists in England during the early years of the eighteenth century (see Plates 46 and 47)"
) or visual_lines[8] != "Pellegrini: Pierre Motteux and his family":
    raise SystemExit("Plate 46 visual transcription is missing or changed")
segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {r["segment_id"]: r for r in segments}
if segment_by_id.get(OCR_SEGMENT, {}).get("sha256") != EXPECTED_OCR_SEGMENT:
    raise SystemExit("Plate 46 OCR segment changed")
visual_meta = segment_by_id.get(VISUAL_SEGMENT)
if not visual_meta or visual_meta["sha256"] != EXPECTED_VISUAL_SEGMENT or visual_meta["asset_sha256"] != EXPECTED_VISUAL_ASSET:
    raise SystemExit("Plate 46 visual segment missing or changed")
if hashlib.sha256(ocr_bytes).hexdigest() != segment_by_id[OCR_SEGMENT]["asset_sha256"]:
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
used_candidate_ids = {"cand-3859", "cand-3865", "cand-4073"}
if not used_candidate_ids <= candidate_ids:
    raise SystemExit(f"existing Plate 46 candidates are missing: {used_candidate_ids - candidate_ids}")
coverage_by_id = {r["segment_id"]: r for r in coverage}
ocr_cov = coverage_by_id.get(OCR_SEGMENT)
if not ocr_cov or (ocr_cov["disposition"], ocr_cov["migration_status"], ocr_cov["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"unexpected OCR segment coverage: {ocr_cov}")
if VISUAL_SEGMENT in coverage_by_id:
    raise SystemExit("Plate 46 visual segment already has a coverage decision")

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_statement_ids = {r["statement_id"] for r in statements}
caption = visual_lines[8]
segment_text = "\n".join(visual_lines[7:9])
line9_offset = len(visual_lines[7]) + 1
new_mentions = []
for mid, candidate_id, surface, note in [
    ("m-chp9-plate46-artist", "cand-3859", "Pellegrini", "Surname-only caption attribution; the matching front-matter plate entry supplies the same named work."),
    ("m-chp9-plate46-work", "cand-4073", "Pierre Motteux and his family", "Captioned work; same title as Plate 46 in the front-matter list."),
    ("m-chp9-plate46-sitter", "cand-3865", "Pierre Motteux", "Named subject in the work title; other family members remain unnamed."),
]:
    if mid in existing_mention_ids:
        raise SystemExit(f"duplicate mention id: {mid}")
    pos = caption.find(surface)
    if pos < 0 or caption.find(surface, pos + len(surface)) >= 0:
        raise SystemExit(f"surface is missing or ambiguous: {surface}")
    start = line9_offset + pos
    new_mentions.append({
        "mention_id": mid,
        "segment_id": VISUAL_SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })

new_statements = []
for statement_id, subject, object_, predicate, claim, qualification in [
    (
        "st-chp9-plate46-creator", "cand-4073", "cand-3859", "caption_attribution",
        "The Plate 46 caption credits Pellegrini with Pierre Motteux and his family.",
        "Printed caption attribution, repeated in the front-matter plate list; no external identity matching or attribution validation is added.",
    ),
    (
        "st-chp9-plate46-sitter", "cand-4073", "cand-3865", "caption_subject",
        "The title identifies Pierre Motteux as a depicted subject in Pierre Motteux and his family.",
        "The title names Motteux and an unnamed family group; no other family member is separately identified.",
    ),
]:
    if statement_id in existing_statement_ids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": VISUAL_SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 9,
            "source_line_end": 9,
            "plate_number": 46,
            "pdf_physical_page": 28,
            "claim": claim,
            "speaker": "plate caption",
            "text_layer": "visual transcription",
            "qualification": qualification,
            "mentioned_candidate_ids": [subject, object_],
            "relation_candidate": True,
            "cross_reference_segments": [
                {"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 124, "source_line_end": 124},
            ],
        },
        "original_quote": caption,
        "source_file": VISUAL_SOURCE.relative_to(ROOT).as_posix(),
        "origin": "book",
    })

for row in new_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    refs = {row["subject_candidate_id"], row["object_candidate_id"], *q["mentioned_candidate_ids"]}
    if not refs <= candidate_ids or row["original_quote"] != visual_lines[q["source_line_start"] - 1]:
        raise SystemExit(f"statement source or foreign key mismatch: {row['statement_id']}")

ocr_cov.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L258-277",
    "note": OCR_NOTE,
})
coverage_by_id[VISUAL_SEGMENT] = {
    "chapter": "chp-9",
    "segment_id": VISUAL_SEGMENT,
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L8-9",
    "note": "Plate 46 editorial group heading and artwork caption transcribed from CHP-9.pdf physical p.28; the heading is retained as navigation metadata for Plates 46-47, not treated as a separate named entity.",
}

summary = {
    "new_candidates": 0,
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "visual_segment": VISUAL_SEGMENT,
    "heading": "editorial grouping label retained as navigation metadata",
    "duplicate_ocr": "consolidated notes L428 repeats the Plate 46 editorial heading",
    "next_segment": "chp-9:09_CHP-9_intro:l279-285 (Plate 47)",
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
    for src, bak in zip(paths, backups):
        shutil.copy2(src, bak)
    try:
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for dst, bak in zip(paths, backups):
            shutil.copy2(bak, dst)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
