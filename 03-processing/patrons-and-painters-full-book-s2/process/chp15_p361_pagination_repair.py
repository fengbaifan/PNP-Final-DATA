"""Correct the printed-page label for the chapter-opening scan; dry-run by default."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
BACKUP_SUFFIX = ".bak-s2-chp15-p361-pagination-fix-20261004"
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply verified p.361 pagination correction")
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
        temp_path = Path(handle.name)
    temp_path.replace(path)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)

target_ids = {f"cand-{number}" for number in range(10423, 10431)}
target_candidates = [row for row in candidates if row["candidate_id"] in target_ids]
target_mentions = [row for row in mentions if row["mention_id"].startswith("m-chp15-p362-")]
target_statements = [row for row in statements if row["statement_id"].startswith("st-chp15-p362-")]
if len(target_candidates) != 8 or len(target_mentions) != 53 or len(target_statements) != 27:
    raise SystemExit(f"unexpected p.361 migration record counts: candidates={len(target_candidates)}, mentions={len(target_mentions)}, statements={len(target_statements)}")
if any(row.get("qualifiers", {}).get("printed_page") != 362 for row in target_statements):
    raise SystemExit("target statements no longer carry the expected incorrect printed_page value 362")


def renamed_statement_refs(value):
    if isinstance(value, str):
        return value.replace("st-chp15-p362-", "st-chp15-p361-")
    if isinstance(value, list):
        return [renamed_statement_refs(item) for item in value]
    if isinstance(value, dict):
        return {key: renamed_statement_refs(item) for key, item in value.items()}
    return value


for row in target_candidates:
    row["canonical_name"] = row["canonical_name"].replace("p.362", "p.361")
target_mentions_ids = {row["mention_id"] for row in target_mentions}
for row in mentions:
    if row["mention_id"] in target_mentions_ids:
        row["mention_id"] = row["mention_id"].replace("m-chp15-p362-", "m-chp15-p361-")
for row in target_statements:
    row.update(renamed_statement_refs(row))
    row["qualifiers"]["printed_page"] = 361
    if row["qualifiers"].get("cross_reference_text"):
        row["qualifiers"]["cross_reference_text"] = (
            row["qualifiers"]["cross_reference_text"]
            .replace("P.362 L14", "P.361 L14")
            .replace("p.363 L17", "p.362 L17")
        )
for row in coverage:
    if row["segment_id"] in {
        "chp-15:15_CHP-15_intro:l3-5",
        "chp-15:15_CHP-15_intro:l7-9",
        "chp-15:15_CHP-15_sec_i:l3-14",
    }:
        row["note"] = row["note"].replace("p.362", "p.361").replace("p.363", "p.362")

result = {
    "mode": "apply" if args.apply else "dry-run",
    "verified_printed_page": 361,
    "pdf_physical_page": 1,
    "next_printed_page": 362,
    "renamed_candidates": len(target_candidates),
    "renamed_mentions": len(target_mentions),
    "corrected_statements": len(target_statements),
}
if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in touched:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
