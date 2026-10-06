"""Correct two p.332 statements that must not imply unstated agents/endpoints."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP_SUFFIX = ".bak-s2-chp13-p332-endpoint-review-20261003"
TARGETS = {
    "st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy",
    "st-chp13-p332-travellers-created-demand-for-engraving",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed endpoint corrections")
args = parser.parse_args()

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
if not TARGETS <= by_id.keys():
    raise SystemExit("one or more p.332 statement IDs are missing")

state = {
    "st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy": ("cand-8105", "cand-2068"),
    "st-chp13-p332-travellers-created-demand-for-engraving": (None, "cand-2068"),
}
for sid, expected in state.items():
    row = by_id[sid]
    actual = (row["subject_candidate_id"], row["object_candidate_id"])
    if actual != expected:
        raise SystemExit(f"unexpected pre-state for {sid}: {actual}")

first = by_id["st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy"]
first["subject_candidate_id"] = None
first["object_candidate_id"] = None
first["predicate"] = "efforts_made_to_uphold_venetian_publishing_supremacy"
first["qualifiers"]["claim"] = (
    "Haskell says substantial, sometimes successful efforts were made to preserve Venetian supremacy in publishing "
    "during the Republic's last hundred years; the sentence does not identify who made them."
)
first["qualifiers"]["qualification"] = (
    "The period is Haskell's approximate description of the Republic's final century. The source uses passive voice "
    "and supplies no actor, specific law, official, or success measure."
)
first["qualifiers"].pop("relation_candidate", None)
first["qualifiers"]["agency_status"] = "not_explicit_in_source"

second = by_id["st-chp13-p332-travellers-created-demand-for-engraving"]
second["object_candidate_id"] = None
second["qualifiers"]["qualification"] = (
    "The travellers are unnamed and their inability to acquire views or hire copyists is stated as a general tendency, "
    "not a universal condition. The passage does not identify who experienced the resulting demand."
)

print("endpoint review:")
for sid in sorted(TARGETS):
    row = by_id[sid]
    print(f"  {sid}: subject={row['subject_candidate_id']!r}, object={row['object_candidate_id']!r}")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"recovery copy already exists: {backup.name}")
shutil.copy2(TABLE, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
    for row in rows:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(TABLE)
print(f"applied; recovery copy created with suffix {BACKUP_SUFFIX}")
