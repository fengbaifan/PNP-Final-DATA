"""Keep the p.371 statement's source quote within its own segment."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
STATEMENT_ID = "st-chp15-p371-querini-renier-canova-bust-commission-partial"
SUFFIX = "\nto become Doge in 1779."
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp15-p372-cross-reference-repair-20261004")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the audited cross-segment reference repair")
args = parser.parse_args()

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
matches = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
if len(matches) != 1:
    raise SystemExit(f"expected one continuation statement, found {len(matches)}")
row = matches[0]
q = row["qualifiers"]
if row["segment_id"] != "chp-15:15_CHP-15_sec_ii:l69-83" or q.get("source_line_end") != 86 or not row["original_quote"].endswith(SUFFIX):
    raise SystemExit("continuation statement no longer matches the expected repair precondition")

q["source_line_end"] = 83
q["claim"] = (
    "Haskell says Querini had been closely associated with the potential reformer Paolo Renier and commissioned "
    "Canova to make a bust of him after Renier's successful, though exceedingly corrupt in Haskell's description, "
    "campaign; p.372 continues by specifying that the campaign was to become Doge in 1779."
)
q["qualification"] = (
    "P.372 closes the sentence and specifies the campaign's aim and year in a separate statement. "
    "'Exceedingly corrupt' is Haskell's characterization, not an independently established fact."
)
q["mentioned_candidate_ids"] = [cid for cid in q.get("mentioned_candidate_ids", []) if cid != "cand-8450"]
q["predicate_status"] = "complete"
q["cross_reference_text"] = "P.371 L83 ends with 'campaign'; p.372 L86 completes it with 'to become Doge in 1779.'"
q["cross_reference_text_pending"] = False
q["cross_reference_statement_ids"] = ["st-chp15-p372-renier-became-doge-1779"]
row["original_quote"] = row["original_quote"][:-len(SUFFIX)]

if not args.apply:
    print(json.dumps({"mode": "dry-run", "statement_id": STATEMENT_ID, "source_line_end": 83,
                      "cross_reference_statement_ids": q["cross_reference_statement_ids"]}, ensure_ascii=False))
    raise SystemExit(0)
if BACKUP.exists():
    raise SystemExit(f"backup already exists: {BACKUP.name}")
shutil.copy2(TABLE, BACKUP)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
    for item in rows:
        handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    temp = Path(handle.name)
temp.replace(TABLE)
print(json.dumps({"mode": "applied", "statement_id": STATEMENT_ID, "backup": BACKUP.name}, ensure_ascii=False))
