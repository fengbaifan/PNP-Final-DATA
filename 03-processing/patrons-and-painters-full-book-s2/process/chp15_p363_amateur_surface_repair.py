"""Add a missed literal S2 mention of the already indexed term Amateur on p.363."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
SOURCE_SHA = "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624"
SEGMENT = "chp-15:15_CHP-15_sec_i:l27-36"
STATEMENT_ID = "st-chp15-p363-daniele-cousin-amateur-painter"
MENTION_ID = "m-chp15-p363-0087"
BACKUP_SUFFIX = ".bak-s2-chp15-p363-amateur-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.363 S2 mention repair")
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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 15 sec_i source changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "himself an amateur painter" not in source_lines[34]:
    raise SystemExit("p.363 source mention changed at L35")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
_, coverage = read_csv(coverage_path)

if not any(row["candidate_id"] == "cand-3570" and row["canonical_name"] == "Amateur" for row in candidates):
    raise SystemExit("open term candidate cand-3570 changed")
state = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
if not state or state["migration_status"] != "complete":
    raise SystemExit("p.363 S2 segment is no longer complete")
statement = next((row for row in statements if row["statement_id"] == STATEMENT_ID), None)
if not statement or statement["segment_id"] != SEGMENT:
    raise SystemExit("expected p.363 amateur-painter statement missing")
if any(row["mention_id"] == MENTION_ID for row in mentions):
    raise SystemExit(f"mention ID already exists: {MENTION_ID}")
if any(row["segment_id"] == SEGMENT and row["candidate_id"] == "cand-3570" and row["surface_form"].casefold() == "amateur" for row in mentions):
    raise SystemExit("p.363 Amateur mention already exists")

line_start = len("\n".join(source_lines[26:34])) + 1
surface = "amateur"
line = source_lines[34]
position = line.find(surface)
if position < 0 or line.find(surface, position + 1) >= 0:
    raise SystemExit("expected a single literal ‘amateur’ span on p.363 L35")
start = line_start + position
end = start + len(surface)
occupied = [
    (int(row["start_char"]), int(row["end_char"]))
    for row in mentions if row["segment_id"] == SEGMENT
]
if any(start < other_end and other_start < end for other_start, other_end in occupied):
    raise SystemExit("new p.363 Amateur span overlaps an existing mention")

mention = {
    "mention_id": MENTION_ID, "segment_id": SEGMENT, "candidate_id": "cand-3570",
    "surface_form": surface, "start_char": str(start), "end_char": str(end),
    "note": "Literal term in Daniele Farsetti’s ‘amateur painter’ description; linked to the existing open Amateur candidate, with global semantic alignment still pending.",
}
statement["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
    statement["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-3570"]
))

result = {
    "mode": "apply" if args.apply else "dry-run", "segment_id": SEGMENT,
    "mention_id": MENTION_ID, "candidate_id": "cand-3570",
    "surface_form": surface, "start_char": start, "end_char": end,
    "source_sha256": SOURCE_SHA,
}
if args.apply:
    touched = [mention_path, statement_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(mention_path, mention_fields, mentions + [mention])
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False) as handle:
        for row in statements:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(statement_path)
print(json.dumps(result, ensure_ascii=False, indent=2))
