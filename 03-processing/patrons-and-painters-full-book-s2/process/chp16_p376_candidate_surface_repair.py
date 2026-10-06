"""Record the existing Old masters term candidate in the p.376 statement."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
SEGMENT = "chp-16:16_CHP-16_intro:l38-46"
STATEMENT_ID = "st-chp16-p376-toninotto-attributed-old-masters"
MENTION_ID = "m-chp16-p376-old-masters-candidate-surface"
BACKUP_SUFFIX = ".bak-s2-chp16-p376-surface-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 16 source changed")
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "old masters" not in lines[43]:
    raise SystemExit("p.376 old masters source anchor changed")

mentions_path = TABLES / "mentions.csv"
statements_path = TABLES / "book-statements.jsonl"
with mentions_path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    mention_fields = reader.fieldnames
    mentions = list(reader)
statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

statement = next((row for row in statements if row.get("statement_id") == STATEMENT_ID), None)
if not statement:
    raise SystemExit("p.376 old masters statement is missing")
mentioned_ids = statement["qualifiers"].get("mentioned_candidate_ids", [])
if "cand-4288" not in mentioned_ids:
    mentioned_ids.append("cand-4288")
    statement["qualifiers"]["mentioned_candidate_ids"] = mentioned_ids
if any(row["mention_id"] == MENTION_ID for row in mentions):
    raise SystemExit("repair mention ID already exists")

segment_text = "\n".join(lines[37:46])
start = sum(len(line) + 1 for line in lines[37:43]) + lines[43].index("old masters")
end = start + len("old masters")
if segment_text[start:end] != "old masters":
    raise SystemExit("computed Old masters span does not match segment text")
if any(row["segment_id"] == SEGMENT and int(row["start_char"]) == start and int(row["end_char"]) == end
       for row in mentions):
    raise SystemExit("p.376 Old masters mention already exists")

mention = {
    "mention_id": MENTION_ID, "segment_id": SEGMENT, "candidate_id": "cand-4288",
    "surface_form": "old masters", "start_char": str(start), "end_char": str(end),
    "note": "Reuses the existing term candidate for the collection category described in this sentence.",
}

print(json.dumps({"mode": "apply" if args.apply else "dry-run", "mention": mention,
                  "statement_candidate_ids": mentioned_ids}, ensure_ascii=False))
if not args.apply:
    raise SystemExit(0)

backups = []
for path in (mentions_path, statements_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    backups.append((path, backup))
for path, backup in backups:
    shutil.copy2(path, backup)

mentions.append(mention)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=mentions_path.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(mentions)
    temporary = Path(stream.name)
temporary.replace(mentions_path)

with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statements_path.parent, delete=False) as stream:
    for row in statements:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(statements_path)
print(json.dumps({"mode": "applied", "backups": [backup.name for _, backup in backups]}, ensure_ascii=False))
