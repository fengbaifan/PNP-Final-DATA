"""Reuse the existing Morassi author and 1955 book candidates for p.352 note 2."""
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
suffix = ".bak-s2-chp14-p352-candidate-reuse-20261003"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

candidate_by_id = {row["candidate_id"]: row for row in candidates}
duplicate = candidate_by_id.get("cand-10282")
if duplicate is None or duplicate["canonical_name"] != "Morassi, 1955, p.21 (citation in p.352 note 2)":
    raise SystemExit("unexpected p.352 Morassi candidate precondition")
for candidate_id in ("cand-8257", "cand-8258"):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"existing bibliography candidate missing: {candidate_id}")

target_mentions = [row for row in mentions if row["mention_id"] == "m-chp14-p352-0047"]
if len(target_mentions) != 1 or target_mentions[0]["candidate_id"] != "cand-10282" or target_mentions[0]["surface_form"] != "Morassi":
    raise SystemExit("unexpected p.352 Morassi mention precondition")
target_statements = [row for row in statements if row["statement_id"] == "st-chp14-p352-note2-prior-contact"]
if len(target_statements) != 1 or "cand-10282" not in target_statements[0]["qualifiers"].get("mentioned_candidate_ids", []):
    raise SystemExit("unexpected p.352 note 2 statement precondition")

for path in (candidate_path, mention_path, statement_path):
    backup = path.with_name(path.name + suffix)
    if not backup.exists():
        shutil.copy2(path, backup)

candidates = [row for row in candidates if row["candidate_id"] != "cand-10282"]
target_mentions[0]["candidate_id"] = "cand-8257"
for row in target_statements:
    old = row["qualifiers"]["mentioned_candidate_ids"]
    updated = []
    for candidate_id in old:
        replacement = ["cand-8257", "cand-8258"] if candidate_id == "cand-10282" else [candidate_id]
        for new_id in replacement:
            if new_id not in updated:
                updated.append(new_id)
    row["qualifiers"]["mentioned_candidate_ids"] = updated

write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False) as f:
    for row in statements:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp = Path(f.name)
tmp.replace(statement_path)

print(json.dumps({"removed_duplicate_candidate": "cand-10282", "reused_candidates": ["cand-8257", "cand-8258"],
                  "mention_id": target_mentions[0]["mention_id"], "backups_suffix": suffix}, ensure_ascii=False))
