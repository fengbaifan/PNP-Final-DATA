"""Classify four still-open p.251 footnote statements after page-image review."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md"
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp9-p251-footnote-classification-20261014")
EXPECTED_SOURCE_SHA = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
EXPECTED_STATEMENTS_SHA = "3e323e48690857930eecb104f3cec8bbc885bfa41fe4061e3df6a3c8dacbb30b"
SEGMENT = "chp-9:09_CHP-9_intro:l323-445"

for path, expected in ((SOURCE, EXPECTED_SOURCE_SHA), (STATEMENTS, EXPECTED_STATEMENTS_SHA)):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[348] != "1 See p. 268, note 5." or "The influence of St Peter’s was noted" not in source_lines[349] or source_lines[351] != "4 Daniele Florio, p. xli.":
    raise SystemExit("p.251 footnote anchors changed")

classifications = {
    # Cross-reference and restoration status are narrative/source-navigation statements.
    "st-chp9-p251-p251-note1-page-reference": False,
    "st-chp9-p251-st-peters-poetic-influence-note": True,
    "st-chp9-p251-villa-restoration-note": False,
    # Haskell's citation explicitly associates Florio with the verse; the cited text is not independently checked.
    "st-chp9-p251-florio-citation-note4": True,
}
rows = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
if not set(classifications) <= by_id.keys():
    raise SystemExit("one or more target p.251 statements are missing")
for statement_id, value in classifications.items():
    row = by_id[statement_id]
    if row.get("segment_id") != SEGMENT or row["qualifiers"].get("relation_candidate") is not None:
        raise SystemExit(f"target row changed or is already classified: {statement_id}")

florio = by_id["st-chp9-p251-florio-citation-note4"]
florio["qualifiers"]["qualification"] = "Note 4 attributes the preceding country-house verse to Daniele Florio and gives p. xli; p.251 note 2 supplies the full Le Grazie citation. Haskell's citation was checked against the printed page, but the cited poem was not independently consulted."
florio["qualifiers"]["related_statement_ids"] = ["st-chp9-p251-florio-country-house-verse", "st-chp9-p251-st-peters-poetic-influence-note"]

for statement_id, value in classifications.items():
    by_id[statement_id]["qualifiers"]["relation_candidate"] = value

print(json.dumps({
    "segment": SEGMENT,
    "page_image": "p251_page_review_20261014.png (CHP-9.pdf physical page 13)",
    "reviewed_statements": classifications,
    "result": {"relation_candidate_true": sum(classifications.values()), "relation_candidate_false": len(classifications) - sum(classifications.values()), "unset": 0},
}, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENTS.parent, delete=False) as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            temp_path = Path(handle.name)
        temp_path.replace(STATEMENTS)
    except Exception:
        shutil.copy2(BACKUP, STATEMENTS)
        raise
    print(f"APPLIED; backup={BACKUP.relative_to(ROOT)}")
