"""Controlled S2 migration for Plate 54; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l55-56"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "8195057081b3e6703042c243e0f5e129f7cfce2bb387cae107c5047667eac34e"
BACKUP_SUFFIX = ".bak-s2-chp10-plate54-20261003"


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
parser.add_argument("--apply", action="store_true", help="write the reviewed Plate 54 rows after making backups")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[54:56]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if segment_lines != ["[Page 54]", "P : Idyll"]:
    raise SystemExit(f"unexpected Plate 54 OCR segment: {segment_lines!r}")

mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_path = TABLES / "entity-candidates.csv"
_, candidates = read_csv(candidate_path)
candidate_ids = {row["candidate_id"] for row in candidates}
if (len(candidates), len(mentions), len(statements)) != (9577, 20008, 8869):
    raise SystemExit(f"table state changed: candidates={len(candidates)}, mentions={len(mentions)}, statements={len(statements)}")
for required in ("cand-1901", "cand-4076"):
    if required not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {required}")
coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"Plate 54 coverage state changed: {coverage[SEGMENT]}")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("Plate 54 already has S2 mention or statement rows")

new_mentions = []


def add_mention(surface, candidate_id, note):
    raw_line = source_lines[55]
    position = raw_line.find(surface)
    if position < 0:
        raise SystemExit(f"mention text not found in OCR line: {surface!r}")
    start = len(segment_lines[0]) + 1 + position
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p54-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    if segment_text[start: start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch: {surface!r}")
    new_mentions.append(row)


add_mention("P", "cand-1901", "OCR abbreviation; CHP-10.pdf physical page 43 prints the artist name as 'Piazzetta'.")
add_mention("Idyll", "cand-4076", "Reuses the existing work candidate; CHP-10.pdf physical page 43 confirms the Plate 54 caption 'Piazzetta: Idyll'.")

new_statement = {
    "statement_id": "st-chp10-plate54-piazzetta-idyll-caption",
    "segment_id": SEGMENT,
    "subject_candidate_id": "cand-1901",
    "object_candidate_id": "cand-4076",
    "predicate": "plate_caption_attributes_idyll_to_piazzetta",
    "qualifiers": {
        "source_line_start": 55,
        "source_line_end": 56,
        "pdf_physical_page": 43,
        "plate_number": 54,
        "claim": "The printed Plate 54 caption reads 'Piazzetta: Idyll'.",
        "speaker": "printed caption",
        "text_layer": "figure caption checked against PDF",
        "qualification": "The OCR abbreviates Piazzetta as 'P'. The section heading does not establish ownership, commission, or patronage for this work.",
        "mentioned_candidate_ids": ["cand-1901", "cand-4076"],
        "relation_candidate": True,
        "printed_caption": "PIAZZETTA: Idyll",
    },
    "original_quote": "\n".join(segment_lines),
    "origin": "book",
    "source_file": SOURCE_FILE,
}
if any(row["statement_id"] == new_statement["statement_id"] for row in statements):
    raise SystemExit("Plate 54 statement id already exists")
if any(row["mention_id"] == new_mentions[0]["mention_id"] for row in mentions):
    raise SystemExit("Plate 54 mention ids already exist")

coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L55-56",
    "note": (
        "Compared with CHP-10.pdf physical page 43: OCR '[Page 54]' is the plate number, and the caption reads "
        "'PIAZZETTA: Idyll'. Reuses the existing Piazzetta and Idyll candidates. The caption supports an artist attribution; "
        "the section heading is not used to infer ownership, commission, or patronage."
    ),
})

mention_rows = mentions + new_mentions
statement_rows = statements + [new_statement]
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")

print(f"Plate 54 preview: +{len(new_mentions)} mentions, +1 statement, no new candidate")
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
