"""Add the Venice mention omitted from p.375 note 5 after the surface audit."""
import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
SEGMENT = "chp-16:16_CHP-16_intro:l69-89"
MENTION_ID = "m-chp16-p375-della-lena-note5-venice"
BACKUP_SUFFIX = ".bak-s2-chp16-p375-della-lena-surface-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 16 source changed")
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "5 Biblioteca Correr, Venice—MSS. Raccolta Cicogna 3006/9" not in lines[79]:
    raise SystemExit("p.375 note 5 source anchor changed")

mentions_path = TABLES / "mentions.csv"
statements_path = TABLES / "book-statements.jsonl"
with mentions_path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    mentions = list(reader)
import json
statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

note5 = next((row for row in statements if row.get("statement_id") == "st-chp16-p375-note5-della-lena-account-manuscript"), None)
if not note5 or "cand-2719" not in note5["qualifiers"].get("mentioned_candidate_ids", []):
    raise SystemExit("p.375 note 5 statement is missing its Venice candidate mapping")
if any(row["mention_id"] == MENTION_ID for row in mentions):
    raise SystemExit("repair mention ID already exists")
if any(row["segment_id"] == SEGMENT and row["surface_form"] == "Venice"
       and int(row["start_char"]) == sum(len(line) + 1 for line in lines[68:79]) + lines[79].index("Venice")
       for row in mentions):
    raise SystemExit("p.375 note 5 Venice mention already exists")

segment_text = "\n".join(lines[68:89])
start = sum(len(line) + 1 for line in lines[68:79]) + lines[79].index("Venice")
end = start + len("Venice")
if segment_text[start:end] != "Venice":
    raise SystemExit("computed Venice span does not match segment text")
mention = {
    "mention_id": MENTION_ID, "segment_id": SEGMENT, "candidate_id": "cand-2719",
    "surface_form": "Venice", "start_char": str(start), "end_char": str(end),
    "note": "Place in Haskell's repository locator.",
}

print(json.dumps({"mode": "apply" if args.apply else "dry-run", "mention": mention}, ensure_ascii=False))
if not args.apply:
    raise SystemExit(0)

backup = mentions_path.with_name(mentions_path.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup.name}")
shutil.copy2(mentions_path, backup)
mentions.append(mention)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=mentions_path.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(mentions)
    temporary = Path(stream.name)
temporary.replace(mentions_path)
print(f"applied; recovery copy: {backup.name}")
