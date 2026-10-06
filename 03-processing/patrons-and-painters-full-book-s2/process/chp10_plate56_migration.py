"""Controlled S2 migration for the Plate 56 caption; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l62-70"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "aa2a526899364c8eb56dd1f6e85986608de9a672532db30872db6062418796b5"
BACKUP_SUFFIX = ".bak-s2-chp10-plate56-20261003"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed Plate 56 rows after creating backups")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[61:70]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if segment_lines != [
    "[Page 56]", "occoR.S", "fo", "hcruhC", "ta", "noitibihxE", "erutciP", ":ihcseira", "M",
]:
    raise SystemExit(f"unexpected Plate 56 OCR segment: {segment_lines!r}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
if (len(candidates), len(mentions), len(statements)) != (9577, 20015, 8872):
    raise SystemExit(f"table state changed: candidates={len(candidates)}, mentions={len(mentions)}, statements={len(statements)}")
EXISTING = {"marieschi": "cand-3834", "picture_exhibition": "cand-4056", "church_of_s_rocco": "cand-3916"}
for label, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {label}={candidate_id}")
coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"Plate 56 coverage state changed: {coverage[SEGMENT]}")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("Plate 56 already has S2 mention or statement rows")

new_mentions = []


def add_mention(line_no, surface, candidate_id, note):
    line = source_lines[line_no - 1]
    position = line.find(surface)
    if position < 0:
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r}")
    relative_line = line_no - 62
    start = sum(len(item) + 1 for item in segment_lines[:relative_line]) + position
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p56-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch: {surface!r}")
    new_mentions.append(row)


add_mention(69, "ihcseira", EXISTING["marieschi"], "Reversed OCR fragment of the artist's name; together with the isolated initial on L70, CHP-10.pdf physical page 45 reads 'Marieschi'.")
add_mention(70, "M", EXISTING["marieschi"], "The separate OCR initial belongs to the same caption name as the reversed fragment on L69; not a separate entity.")
add_mention(68, "erutciP", EXISTING["picture_exhibition"], "Reversed OCR word; read with adjacent caption fragments as 'Picture Exhibition'.")
add_mention(67, "noitibihxE", EXISTING["picture_exhibition"], "Reversed OCR word; read with adjacent caption fragments as 'Picture Exhibition'.")
add_mention(65, "hcruhC", EXISTING["church_of_s_rocco"], "Reversed OCR word; print caption reads 'Church'.")
add_mention(63, "occoR.S", EXISTING["church_of_s_rocco"], "Reversed OCR place name; print caption reads 'S. Rocco'.")

new_statement = {
    "statement_id": "st-chp10-plate56-marieschi-picture-exhibition-caption",
    "segment_id": SEGMENT,
    "subject_candidate_id": EXISTING["marieschi"],
    "object_candidate_id": EXISTING["picture_exhibition"],
    "predicate": "plate_caption_attributes_picture_exhibition_to_marieschi",
    "qualifiers": {
        "source_line_start": 63,
        "source_line_end": 70,
        "pdf_physical_page": 45,
        "plate_number": 56,
        "claim": "The printed Plate 56 caption reads 'Marieschi: Picture Exhibition at Church of S. Rocco'.",
        "speaker": "printed caption",
        "text_layer": "caption checked against rotated PDF page",
        "qualification": "The source OCR reverses and fragments the caption; the artist name is split between L69 and L70. The caption records an artist attribution and title; no independent commission, ownership, or event relation is inferred.",
        "mentioned_candidate_ids": [EXISTING["marieschi"], EXISTING["picture_exhibition"], EXISTING["church_of_s_rocco"]],
        "relation_candidate": True,
        "printed_caption": "Marieschi: Picture Exhibition at Church of S. Rocco",
    },
    "original_quote": "\n".join(source_lines[62:70]),
    "origin": "book",
    "source_file": SOURCE_FILE,
}
if any(row["statement_id"] == new_statement["statement_id"] for row in statements):
    raise SystemExit("Plate 56 statement id already exists")
for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"mention points to missing candidate: {row['mention_id']}")
quote = "\n".join(source_lines[62:70])
if new_statement["original_quote"] != quote:
    raise SystemExit("Plate 56 statement quote mismatch")

coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L62-70",
    "note": (
        "Compared with CHP-10.pdf physical page 45, rotated for reading. '[Page 56]' is the plate number; the printed "
        "caption reads 'Marieschi: Picture Exhibition at Church of S. Rocco'. The OCR reverses and fragments the words, "
        "splitting the initial 'M' from the rest of the artist's name. Existing Marieschi, work, and church "
        "candidates are reused; no new candidate is required."
    ),
})

mention_rows = mentions + new_mentions
statement_rows = statements + [new_statement]
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")

print(f"Plate 56 preview: +{len(new_mentions)} mentions, +1 statement, no new candidates")
print(f"coverage: {SEGMENT} reviewed/complete; resulting totals {len(candidates)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
if not args.apply:
    raise SystemExit(0)

targets = [mention_path, statement_path, coverage_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; three recovery copies created with suffix {BACKUP_SUFFIX}")
