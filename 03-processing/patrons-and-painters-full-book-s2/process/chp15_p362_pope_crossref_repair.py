"""Correct the p.362 Clement XIII index cross-reference; dry-run by default."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
BACKUP_SUFFIX = ".bak-s2-chp15-p362-pope-crossref-20261004"
TARGETS = {
    "m-chp15-p362-0025": "Pope Clement",
    "m-chp15-p362-0026": "XIII",
}
STATEMENT_ID = "st-chp15-p362-rezzonico-became-pope-clement-xiii-1758"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed redirect correction")
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


mention_fields, mentions = read_csv(MENTIONS)
statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
mentions_by_id = {row["mention_id"]: row for row in mentions}
statements_by_id = {row["statement_id"]: row for row in statements}

for mention_id, surface in TARGETS.items():
    row = mentions_by_id.get(mention_id)
    if not row or row["candidate_id"] != "cand-2898" or row["surface_form"] != surface:
        raise SystemExit(f"unexpected p.362 mention state: {mention_id}")
    row["candidate_id"] = "cand-2137"
    row["note"] = (
        "Haskell identifies Pope Clement XIII as Carlo Rezzonico; the index entry ‘Clement XIII, Pope’ "
        "is only a ‘see under Rezzonico’ cross-reference, not a separate person."
    )

statement = statements_by_id.get(STATEMENT_ID)
if (
    not statement
    or statement["subject_candidate_id"] != "cand-2137"
    or statement["object_candidate_id"] != "cand-2898"
    or statement["qualifiers"].get("mentioned_candidate_ids") != ["cand-2137", "cand-2898"]
):
    raise SystemExit("unexpected p.362 Pope Clement XIII statement state")
statement["object_candidate_id"] = None
statement["qualifiers"]["mentioned_candidate_ids"] = ["cand-2137"]
statement["qualifiers"]["qualification"] = (
    "Pope Clement XIII is the papal name/title of Carlo Rezzonico, not a second person; "
    "the index entry ‘Clement XIII, Pope’ is only a cross-reference to Rezzonico."
)

result = {
    "mode": "apply" if args.apply else "dry-run",
    "updated_mentions": sorted(TARGETS),
    "updated_statement": STATEMENT_ID,
    "candidate_redirect": "cand-2898 -> cand-2137",
}
if args.apply:
    touched = [MENTIONS, STATEMENTS]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(MENTIONS, mention_fields, mentions)
    write_jsonl(STATEMENTS, statements)
print(json.dumps(result, ensure_ascii=False, indent=2))
