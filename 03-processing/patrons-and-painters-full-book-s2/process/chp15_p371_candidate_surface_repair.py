"""Controlled repair for two missed literal candidate mentions on p.371."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
SEGMENT = "chp-15:15_CHP-15_sec_ii:l69-83"
STATEMENT_MAPPINGS = {
    "st-chp15-p371-de-non-saint-non-travel-book-work": "cand-3534",
    "st-chp15-p371-literary-inspiration-and-renaissance-art-life": "cand-3578",
}
BACKUP_SUFFIX = ".bak-s2-chp15-p371-candidate-surface-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed two-mention repair")
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
    raise SystemExit("chapter 15 source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[68:83])
repairs = [
    ("m-chp15-p371-querini-0054", "cand-3534", "Naples", 2295,
     "st-chp15-p371-de-non-saint-non-travel-book-work"),
    ("m-chp15-p371-querini-0055", "cand-3578", "Renaissance", 2836,
     "st-chp15-p371-literary-inspiration-and-renaissance-art-life"),
]

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}

for mention_id, candidate_id, surface, start, statement_id in repairs:
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"candidate missing: {candidate_id}")
    if mention_id in {row["mention_id"] for row in mentions}:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"source anchor changed: {surface} at {start}")
    statement = statement_by_id.get(statement_id)
    if not statement or statement.get("segment_id") != SEGMENT:
        raise SystemExit(f"statement missing or moved: {statement_id}")
    if candidate_id in statement.get("qualifiers", {}).get("mentioned_candidate_ids", []):
        raise SystemExit(f"statement already references {candidate_id}: {statement_id}")
    mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": "",
    })
    statement["qualifiers"].setdefault("mentioned_candidate_ids", []).append(candidate_id)

if not args.apply:
    print(json.dumps({"mode": "dry-run", "mentions_to_add": 2, "candidate_ids": [r[1] for r in repairs],
                      "segment": SEGMENT}, ensure_ascii=False))
    raise SystemExit(0)

for path in (mention_path, statement_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)

write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
print(json.dumps({"mode": "applied", "mentions_added": 2, "backups": [
    mention_path.name + BACKUP_SUFFIX, statement_path.name + BACKUP_SUFFIX]}, ensure_ascii=False))
