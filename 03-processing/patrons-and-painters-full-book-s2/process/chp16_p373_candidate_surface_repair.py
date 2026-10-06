"""Repair the two typed candidate-surface omissions on p.373."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
BODY = "chp-16:16_CHP-16_intro:l3-14"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
BACKUP_SUFFIX = ".bak-s2-chp16-p373-candidate-surface-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the two audited p.373 mention repairs")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 16 source changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_fields, coverage = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY, NOTES):
    state = coverage_by_id.get(segment_id)
    if not state or state["disposition"] != "reviewed" or state["migration_status"] != "partial":
        raise SystemExit(f"unexpected p.373 coverage state: {segment_id}")

segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(3, 15)},
    NOTES: {number: source_lines[number - 1] for number in range(69, 90)},
}
segment_offsets = {}
for segment_id, lines in segment_lines.items():
    offset = 0
    segment_offsets[segment_id] = {}
    for number, line in lines.items():
        segment_offsets[segment_id][number] = offset
        offset += len(line) + 1

repairs = [
    ("m-chp16-p373-sasso-surfacefix-0001", "cand-4129", "art patrons", BODY, 6,
     "Existing typed term candidate; the phrase is a general category, not an individually identified patron."),
    ("m-chp16-p373-sasso-surfacefix-0002", "cand-3401", "Venice", NOTES, 71,
     "Place named in the note's repository locator; print reading separately records the OCR correction Cotter to Correr."),
]

planned = []
for mention_id, candidate_id, surface, segment_id, line_number, note in repairs:
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"missing candidate: {candidate_id}")
    line = segment_lines[segment_id][line_number]
    position = line.find(surface)
    if position < 0:
        raise SystemExit(f"source surface not found: {surface} at L{line_number}")
    start = segment_offsets[segment_id][line_number] + position
    end = start + len(surface)
    if any(row["mention_id"] == mention_id for row in mentions + planned):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if any(row["segment_id"] == segment_id and start < int(row["end_char"]) and int(row["start_char"]) < end
           for row in mentions + planned):
        raise SystemExit(f"mention span overlaps an existing span: {surface}")
    planned.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })

statement_changes = {
    "st-chp16-p373-patronage-tastes-and-venetian-tradition": "cand-4129",
    "st-chp16-p373-note2-strange-sasso-letters-in-epistolario": "cand-3401",
}
updated = []
for statement_id, candidate_id in statement_changes.items():
    statement = next((row for row in statements if row["statement_id"] == statement_id), None)
    if not statement:
        raise SystemExit(f"missing statement: {statement_id}")
    ids = statement["qualifiers"].setdefault("mentioned_candidate_ids", [])
    if candidate_id not in ids:
        ids.append(candidate_id)
        updated.append(statement_id)
    else:
        raise SystemExit(f"candidate already linked in statement: {statement_id}/{candidate_id}")

if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_mentions": planned, "updated_statement_ids": updated,
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (mention_path, statement_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)

mentions.extend(planned)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
print(json.dumps({
    "mode": "applied", "new_mentions": len(planned), "updated_statement_ids": updated,
    "backups": [path.name + BACKUP_SUFFIX for path in (mention_path, statement_path)],
}, ensure_ascii=False))
