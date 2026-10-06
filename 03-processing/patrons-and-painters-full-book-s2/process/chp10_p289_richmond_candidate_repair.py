"""Correct p.289 Richmond mapping to its index-specific British Worthies candidate."""
import csv
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
BACKUP = ".bak-s2-chp10-p289-richmond-candidate-20261002"
OLD = "cand-2193"
NEW = "cand-2194"
MID = "m-chp10-p289-richmond"
SID = "st-chp10-p289-pictures-started-richmond-acquisition"


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


mentions_path = TABLES / "mentions.csv"
statements_path = TABLES / "book-statements.jsonl"
candidates_path = TABLES / "entity-candidates.csv"
_, candidates = read_csv(candidates_path)
candidate = next((row for row in candidates if row["candidate_id"] == NEW), None)
if not candidate or candidate["canonical_name"] != "Richmond, Duke of" or candidate["index_page_range"] != "289, 290, 291" or candidate["sub_entry"] != "and McSwiny's British Worthies":
    raise SystemExit("index-specific Richmond candidate no longer matches p.289 context")
mf, mentions = read_csv(mentions_path)
mention = next((row for row in mentions if row["mention_id"] == MID), None)
if not mention or mention["candidate_id"] not in (OLD, NEW):
    raise SystemExit(f"unexpected p.289 Richmond mention mapping: {mention}")
statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
statement = next((row for row in statements if row["statement_id"] == SID), None)
if not statement or statement["object_candidate_id"] not in (OLD, NEW):
    raise SystemExit(f"unexpected p.289 Richmond statement mapping: {statement}")
ids = statement["qualifiers"].get("mentioned_candidate_ids", [])
if OLD not in ids and NEW not in ids:
    raise SystemExit("p.289 Richmond candidate absent from statement mentions")

print(json.dumps({"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "mention": {"id": MID, "from": mention["candidate_id"], "to": NEW},
                  "statement": {"id": SID, "object_from": statement["object_candidate_id"], "object_to": NEW}}, ensure_ascii=False, indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (mentions_path, statements_path):
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    mention["candidate_id"] = NEW
    statement["object_candidate_id"] = NEW
    statement["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(NEW if cid == OLD else cid for cid in ids))
    write_csv(mentions_path, mf, mentions)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statements_path.parent, delete=False) as stream:
        for row in statements:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(statements_path)
    print("Applied mapping correction; p.289 Richmond mention now uses the index-specific British Worthies candidate.")
