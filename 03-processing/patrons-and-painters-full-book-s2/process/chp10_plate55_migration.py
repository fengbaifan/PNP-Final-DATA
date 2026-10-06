"""Controlled S2 migration for Plate 55 captions; dry-run unless --apply."""
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
SEGMENT = "chp-10:10_CHP-10_sec_ii:l58-60"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "93870f7a42f3835d9a9558283c685f216de44ace37caf1ce4dcc492082216852"
BACKUP_SUFFIX = ".bak-s2-chp10-plate55-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed Plate 55 rows after creating backups")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[57:60]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if segment_lines != [
    "[Page 55]",
    "a. Canaletto: Dedicatory frontispiece to Etchings",
    "b. Marco Ricci: Village Scene",
]:
    raise SystemExit(f"unexpected Plate 55 OCR segment: {segment_lines!r}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
if (len(candidates), len(mentions), len(statements)) != (9577, 20010, 8870):
    raise SystemExit(f"table state changed: candidates={len(candidates)}, mentions={len(mentions)}, statements={len(statements)}")
EXISTING = {
    "canaletto": "cand-3738",
    "frontispiece": "cand-4013",
    "etchings_carrier": "cand-4181",
    "marco_ricci": "cand-3831",
    "village_scene": "cand-4055",
}
for label, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {label}={candidate_id}")
coverage = {row["segment_id"]: row for row in coverage_rows}
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"Plate 55 coverage state changed: {coverage[SEGMENT]}")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("Plate 55 already has S2 mention or statement rows")

new_mentions = []


def add_mention(line_no, surface, candidate_id, note):
    raw_line = source_lines[line_no - 1]
    position = raw_line.find(surface)
    if position < 0:
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r}")
    relative_line = line_no - 58
    start = sum(len(line) + 1 for line in segment_lines[:relative_line]) + position
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p55-{len(new_mentions) + 1:04d}",
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


add_mention(59, "Canaletto", EXISTING["canaletto"], "Printed Plate 55a caption names Canaletto; the existing accepted-KU candidate is reused.")
add_mention(59, "Dedicatory frontispiece to Etchings", EXISTING["frontispiece"], "Printed Plate 55a caption; reuses the existing frontispiece work candidate.")
add_mention(59, "Etchings", EXISTING["etchings_carrier"], "Caption names the frontispiece carrier only as 'Etchings'; title and edition remain unspecified.")
add_mention(60, "Marco Ricci", EXISTING["marco_ricci"], "Printed Plate 55b caption names Marco Ricci; the existing accepted-KU candidate is reused.")
add_mention(60, "Village Scene", EXISTING["village_scene"], "Printed Plate 55b caption; reuses the existing work candidate.")


def statement(statement_id, subject, object_id, predicate, lines, claim, qualification, mentioned):
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": lines[0],
            "source_line_end": lines[1],
            "pdf_physical_page": 44,
            "plate_number": 55,
            "claim": claim,
            "speaker": "printed caption",
            "text_layer": "figure caption checked against PDF",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": True,
        },
        "original_quote": "\n".join(source_lines[lines[0] - 1:lines[1]]),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


new_statements = [
    statement(
        "st-chp10-plate55a-canaletto-etchings-frontispiece-caption",
        EXISTING["canaletto"], EXISTING["frontispiece"], "plate_caption_attributes_frontispiece_to_canaletto", (59, 59),
        "The printed Plate 55a caption identifies the image as 'Canaletto: Dedicatory frontispiece to Etchings'.",
        "The inset inscription is not separately transcribed here; the caption does not establish a commission or ownership claim.",
        [EXISTING["canaletto"], EXISTING["frontispiece"], EXISTING["etchings_carrier"]],
    ),
    statement(
        "st-chp10-plate55b-marco-ricci-village-scene-caption",
        EXISTING["marco_ricci"], EXISTING["village_scene"], "plate_caption_attributes_village_scene_to_marco_ricci", (60, 60),
        "The printed Plate 55b caption identifies the image as 'Marco Ricci: Village Scene'.",
        "This records the printed attribution; it does not add a date, location, commission, or ownership claim.",
        [EXISTING["marco_ricci"], EXISTING["village_scene"]],
    ),
]

for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"mention points to missing candidate: {row['mention_id']}")
for row in new_statements:
    quoted = "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]])
    if row["original_quote"] != quoted:
        raise SystemExit(f"statement quote mismatch: {row['statement_id']}")
    if any(candidate_id not in candidate_ids for candidate_id in row["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"statement candidate missing: {row['statement_id']}")
if any(row["statement_id"] in {s["statement_id"] for s in statements} for row in new_statements):
    raise SystemExit("Plate 55 statement id already exists")

coverage[SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L58-60",
    "note": (
        "Compared with CHP-10.pdf physical page 44. '[Page 55]' is the plate number. Printed captions are "
        "55a 'Canaletto: Dedicatory frontispiece to Etchings' and 55b 'Marco Ricci: Village Scene'. "
        "Existing person and work candidates are reused; no new candidate is required. The plate's inset dedication "
        "is not transcribed separately and no commission or ownership claim is inferred."
    ),
})

mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")

print(f"Plate 55 preview: +{len(new_mentions)} mentions, +{len(new_statements)} statements, no new candidates")
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
