"""Correct the p.280 Pellegrini mention's candidate foreign key."""
from __future__ import annotations

import csv
import argparse
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
BACKUP = Path(str(TABLE) + ".bak-s2-chp10-p280-pellegrini-mention-fk-20261002")
MENTION_ID = "m-chp10-p280-pellegrini"
OLD_CANDIDATE = "cand-1979"  # Portland, Henry, first Duke of
NEW_CANDIDATE = "cand-1870"  # Pellegrini, Giovanni Antonio; index sub-entry on English work
STATEMENT_ID = "st-chp10-p280-portland-commissioned-pellegrini"

with TABLE.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields, rows = reader.fieldnames, list(reader)
row = next((item for item in rows if item["mention_id"] == MENTION_ID), None)
if row is None or (row["candidate_id"], row["surface_form"], row["segment_id"]) != (
    OLD_CANDIDATE, "Pellegrini", "chp-10:10_CHP-10_intro:l51-61"
):
    raise SystemExit("unexpected p.280 Pellegrini mention; table left unchanged")
if not any(r["candidate_id"] == NEW_CANDIDATE and r["canonical_name"] == "Pellegrini, Giovanni Antonio" for r in csv.DictReader((ROOT / "04-knowledge/tables/entity-candidates.csv").open(encoding="utf-8-sig"))):
    raise SystemExit("expected existing Pellegrini candidate is missing")
statements = [
    __import__("json").loads(line)
    for line in (ROOT / "04-knowledge/tables/book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
statement = next((item for item in statements if item["statement_id"] == STATEMENT_ID), None)
if statement is None or statement["object_candidate_id"] != NEW_CANDIDATE:
    raise SystemExit("the linked p.280 commission statement does not point to Pellegrini")
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
print(f"mode={'APPLY' if args.apply else 'DRY-RUN'} mention={MENTION_ID} candidate={OLD_CANDIDATE}->{NEW_CANDIDATE}")
if not args.apply:
    raise SystemExit(0)
if BACKUP.exists():
    raise SystemExit(f"recovery copy already exists: {BACKUP}")
shutil.copy2(TABLE, BACKUP)
row["candidate_id"] = NEW_CANDIDATE
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    temporary = Path(stream.name)
temporary.replace(TABLE)
print(f"Corrected {MENTION_ID}: {OLD_CANDIDATE} -> {NEW_CANDIDATE}; backup retained.")
