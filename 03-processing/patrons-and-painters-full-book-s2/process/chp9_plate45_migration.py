"""Controlled S2 migration for chapter 9 Plate 45; defaults to read-only dry run."""
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
OCR_SEGMENT = "chp-9:09_CHP-9_intro:l251-256"
VISUAL_SEGMENT = "chp-9:09_CHP-9_intro_plates_visual-transcription:l6-6"
EXPECTED_OCR_SEGMENT = "27673e0dfd55646b970857892b2845184ec8243598cfbf054c1ab5ad67fb1d2a"
EXPECTED_VISUAL_SEGMENT = "4f71c6d96b0e008037cc50a76f05eaa8e662049f0756ea1a3a7079552209f4bb"
EXPECTED_VISUAL_ASSET = "1caccf5b44cb2f0706d41b51eab995e1b575d751f4a20a90131aa86869339704"
BACKUP_SUFFIX = ".bak-s2-chp9-plate45-20261001"
SEGMENT_BACKUP = TABLES / "segments.jsonl.bak-s2-chp9-plate45-s0-20261001"


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
if len(visual_lines) < 6 or visual_lines[5] != "Batoni: Triumph of Venice":
    raise SystemExit("Plate 45 visual transcription is missing or changed")
segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {r["segment_id"]: r for r in segments}
if segment_by_id.get(OCR_SEGMENT, {}).get("sha256") != EXPECTED_OCR_SEGMENT:
    raise SystemExit("Plate 45 OCR segment changed")
visual_meta = segment_by_id.get(VISUAL_SEGMENT)
if not visual_meta or visual_meta["sha256"] != EXPECTED_VISUAL_SEGMENT or visual_meta["asset_sha256"] != EXPECTED_VISUAL_ASSET:
    raise SystemExit("Plate 45 visual segment missing or changed")
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
if not {"cand-0262", "cand-4085"} <= candidate_ids:
    raise SystemExit("existing Batoni/work candidates are missing")
coverage_by_id = {r["segment_id"]: r for r in coverage}
ocr_cov = coverage_by_id.get(OCR_SEGMENT)
if not ocr_cov or (ocr_cov["disposition"], ocr_cov["migration_status"], ocr_cov["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"unexpected OCR segment coverage: {ocr_cov}")
if VISUAL_SEGMENT in coverage_by_id:
    raise SystemExit("Plate 45 visual segment already has a coverage decision")

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_statement_ids = {r["statement_id"] for r in statements}
new_mentions = []
line = visual_lines[5]
for mid, candidate_id, surface, note in [
    ("m-chp9-plate45-artist", "cand-0262", "Batoni", "Surname-only caption attribution; reuse the chapter 9 index candidate and defer identity alignment."),
    ("m-chp9-plate45-work", "cand-4085", "Triumph of Venice", "Captioned work also named in the chapter text and the front-matter plate list."),
]:
    if mid in existing_mention_ids:
        raise SystemExit(f"duplicate mention id: {mid}")
    start = line.find(surface)
    if start < 0 or line.find(surface, start + len(surface)) >= 0:
        raise SystemExit(f"surface is missing or ambiguous: {surface}")
    new_mentions.append({
        "mention_id": mid,
        "segment_id": VISUAL_SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })

if "st-chp9-plate45-caption" in existing_statement_ids:
    raise SystemExit("duplicate statement id")
quote = line
new_statement = {
    "statement_id": "st-chp9-plate45-caption",
    "segment_id": VISUAL_SEGMENT,
    "subject_candidate_id": "cand-4085",
    "object_candidate_id": "cand-0262",
    "predicate": "caption_attribution",
    "qualifiers": {
        "source_line_start": 6,
        "source_line_end": 6,
        "plate_number": 45,
        "pdf_physical_page": 27,
        "claim": "The Plate 45 caption attributes The Triumph of Venice to Batoni.",
        "speaker": "plate caption",
        "text_layer": "visual transcription",
        "qualification": "Printed caption attribution; no external identity matching or attribution judgment is added.",
        "mentioned_candidate_ids": ["cand-4085", "cand-0262"],
        "relation_candidate": True,
        "cross_reference_segments": [
            {"segment_id": "chp-9:09_CHP-9_intro:l188-200", "source_line_start": 195, "source_line_end": 195},
            {"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 123, "source_line_end": 123},
        ],
    },
    "original_quote": quote,
    "source_file": VISUAL_SOURCE.relative_to(ROOT).as_posix(),
    "origin": "book",
}

coverage_by_id[OCR_SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L251-256",
    "note": "no_semantic_content: The OCR segment contains a page marker and unreadable reversed caption fragments; its readable caption is represented in the derived visual-transcription segment L6. CHP-9.pdf physical p.27 was reviewed and the OCR source remains unchanged.",
})
coverage_by_id[VISUAL_SEGMENT] = {
    "chapter": "chp-9",
    "segment_id": VISUAL_SEGMENT,
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L6-6",
    "note": "Plate 45 caption visually transcribed from CHP-9.pdf physical p.27; source OCR remains unchanged.",
}

for row in new_mentions:
    if line[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
if quote != visual_lines[new_statement["qualifiers"]["source_line_start"] - 1]:
    raise SystemExit("statement quote mismatch")
if not {"cand-0262", "cand-4085"} <= candidate_ids:
    raise SystemExit("statement foreign key error")

summary = {
    "new_candidates": 0,
    "new_mentions": len(new_mentions),
    "new_statements": 1,
    "new_visual_segment": VISUAL_SEGMENT,
    "coverage_rows_added": 1,
    "ocr_segment": ["reviewed", "complete"],
    "plate_number": 45,
    "next_segment": "chp-9:09_CHP-9_intro:l258-277 (Plate 46)",
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
        write_jsonl(statement_path, statements + [new_statement])
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for dst, bak in zip(paths, backups):
            shutil.copy2(bak, dst)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
