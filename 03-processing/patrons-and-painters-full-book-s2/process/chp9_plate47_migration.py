"""Controlled S2 migration for chapter 9 Plate 47; defaults to read-only dry run."""
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
OCR_SEGMENT = "chp-9:09_CHP-9_intro:l279-285"
VISUAL_SEGMENT = "chp-9:09_CHP-9_intro_plates_visual-transcription:l11-11"
EXPECTED_OCR_SEGMENT = "5f9a8b098c578d4adecf95e39c8d14be3d2a7fef4394634cc84014d37f582b93"
EXPECTED_VISUAL_SEGMENT = "4b77c50b5be02b855e6d7dc769784a8f84b7c835e42d848fbce4c866b84d95a8"
EXPECTED_VISUAL_ASSET = "1c67a7c7ebabd071d8c56bfe45ba5ceb98c3fdddcc090116154972776d9b5f36"
BACKUP_SUFFIX = ".bak-s2-chp9-plate47-20261001"
SEGMENT_BACKUP = TABLES / "segments.jsonl.bak-s2-chp9-plate47-s0-20261001"


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
if hashlib.sha256(VISUAL_SOURCE.read_bytes()).hexdigest() != EXPECTED_VISUAL_ASSET:
    raise SystemExit("visual-transcription source asset changed")
visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
caption = "Marco Ricci: An operatic rehearsal"
if len(visual_lines) < 11 or visual_lines[10] != caption:
    raise SystemExit("Plate 47 visual transcription is missing or changed")
segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {r["segment_id"]: r for r in segments}
if segment_by_id.get(OCR_SEGMENT, {}).get("sha256") != EXPECTED_OCR_SEGMENT:
    raise SystemExit("Plate 47 OCR segment changed")
visual_meta = segment_by_id.get(VISUAL_SEGMENT)
if not visual_meta or visual_meta["sha256"] != EXPECTED_VISUAL_SEGMENT or visual_meta["asset_sha256"] != EXPECTED_VISUAL_ASSET:
    raise SystemExit("Plate 47 visual segment missing or changed")
if hashlib.sha256(OCR_SOURCE.read_bytes()).hexdigest() != segment_by_id[OCR_SEGMENT]["asset_sha256"]:
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
if not {"cand-3831", "cand-4054"} <= candidate_ids:
    raise SystemExit("existing Marco Ricci/work candidates are missing")
coverage_by_id = {r["segment_id"]: r for r in coverage}
ocr_cov = coverage_by_id.get(OCR_SEGMENT)
if not ocr_cov or (ocr_cov["disposition"], ocr_cov["migration_status"], ocr_cov["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"unexpected OCR segment coverage: {ocr_cov}")
if VISUAL_SEGMENT in coverage_by_id:
    raise SystemExit("Plate 47 visual segment already has a coverage decision")

existing_mention_ids = {r["mention_id"] for r in mentions}
new_mentions = []
for mid, candidate_id, surface, note in [
    ("m-chp9-plate47-artist", "cand-3831", "Marco Ricci", "Printed Plate 47 attribution; reuse the matching front-matter artist candidate."),
    ("m-chp9-plate47-work", "cand-4054", "An operatic rehearsal", "Captioned work already listed for Plate 47 in the front matter."),
]:
    if mid in existing_mention_ids:
        raise SystemExit(f"duplicate mention id: {mid}")
    start = caption.find(surface)
    if start < 0 or caption.find(surface, start + len(surface)) >= 0:
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

statement_id = "st-chp9-plate47-caption"
if any(r["statement_id"] == statement_id for r in statements):
    raise SystemExit("duplicate statement id")
new_statement = {
    "statement_id": statement_id,
    "segment_id": VISUAL_SEGMENT,
    "subject_candidate_id": "cand-4054",
    "object_candidate_id": "cand-3831",
    "predicate": "caption_attribution",
    "qualifiers": {
        "source_line_start": 11,
        "source_line_end": 11,
        "plate_number": 47,
        "pdf_physical_page": 29,
        "claim": "The Plate 47 caption credits Marco Ricci with An operatic rehearsal.",
        "speaker": "plate caption",
        "text_layer": "visual transcription",
        "qualification": "Printed caption attribution, repeated in the front-matter plate list; no external identity matching or attribution validation is added.",
        "mentioned_candidate_ids": ["cand-4054", "cand-3831"],
        "relation_candidate": True,
        "cross_reference_segments": [
            {"segment_id": "front-matter:00_05_List_of_Plates:l123-138", "source_line_start": 125, "source_line_end": 125},
        ],
    },
    "original_quote": caption,
    "source_file": VISUAL_SOURCE.relative_to(ROOT).as_posix(),
    "origin": "book",
}
if not {"cand-4054", "cand-3831"} <= candidate_ids or caption != visual_lines[10]:
    raise SystemExit("statement source or foreign key mismatch")
for row in new_mentions:
    if caption[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")

ocr_cov.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L279-285",
    "note": "no_semantic_content: OCR contains the page marker and reversed Plate 47 caption fragments; the caption is represented in derived visual-transcription line 11. CHP-9.pdf physical p.29 was reviewed; OCR remains unchanged.",
})
coverage_by_id[VISUAL_SEGMENT] = {
    "chapter": "chp-9",
    "segment_id": VISUAL_SEGMENT,
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L11-11",
    "note": "Plate 47 caption visually transcribed from CHP-9.pdf physical p.29; the work and attribution match the Plate 47 entry in the front-matter list.",
}

summary = {
    "new_candidates": 0,
    "new_mentions": len(new_mentions),
    "new_statements": 1,
    "visual_segment": VISUAL_SEGMENT,
    "next_segment": "chp-9:09_CHP-9_intro:l287-289 (Plate 48)",
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
