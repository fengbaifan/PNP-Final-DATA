"""Add the candidate surface found in the p.380 post-migration review."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
BODY = "chp-17:17_CHP-17_sec_i:l8-20"
STATEMENT_ID = "st-chp17-p380-manfrin-few-connoisseurship-pretensions"
MENTION_ID = "m-chp17-p380-manfrin-surface-0001"
BACKUP_SUFFIX = ".bak-s2-chp17-p380-candidate-surface-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "connoisseurship" not in source_lines[13]:
    raise SystemExit("expected p.380 source surface changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
_, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
if not any(row["candidate_id"] == "cand-3567" for row in candidates):
    raise SystemExit("the connoisseurship term candidate is missing")
statement = next((row for row in statements if row["statement_id"] == STATEMENT_ID), None)
if statement is None or "cand-1512" not in statement["qualifiers"].get("mentioned_candidate_ids", []):
    raise SystemExit("the p.380 connoisseurship statement is missing or changed")
if "cand-3567" in statement["qualifiers"].get("mentioned_candidate_ids", []):
    raise SystemExit("candidate mapping is already present")
if any(row["mention_id"] == MENTION_ID for row in mentions):
    raise SystemExit("surface repair mention already exists")

line_offsets = {}
offset = 0
for line_number in range(8, 21):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1
line_start = 14
start = line_offsets[line_start] + source_lines[line_start - 1].index("connoisseurship")
end = start + len("connoisseurship")
for row in mentions:
    if row["segment_id"] != BODY:
        continue
    other_start, other_end = int(row["start_char"]), int(row["end_char"])
    if start < other_end and other_start < end:
        raise SystemExit("candidate surface overlaps an existing mention")

mentions.append({
    "mention_id": MENTION_ID, "segment_id": BODY, "candidate_id": "cand-3567",
    "surface_form": "connoisseurship", "start_char": str(start), "end_char": str(end),
    "note": "Reuses the existing term candidate for the private collecting quality discussed by Haskell.",
})
statement["qualifiers"]["mentioned_candidate_ids"].append("cand-3567")

if not args.apply:
    print(json.dumps({"mode": "dry-run", "mention_id": MENTION_ID, "candidate_id": "cand-3567", "start_char": start, "end_char": end, "statement_id": STATEMENT_ID}, ensure_ascii=False))
    raise SystemExit(0)

for path in (mention_path, statement_path):
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(mention_path, mention_fields, mentions)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False) as stream:
    for row in statements:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(statement_path)
print(json.dumps({"mode": "applied", "mention_id": MENTION_ID, "candidate_id": "cand-3567", "statement_id": STATEMENT_ID,
                  "backups": [path.name + BACKUP_SUFFIX for path in (mention_path, statement_path)]}, ensure_ascii=False))
