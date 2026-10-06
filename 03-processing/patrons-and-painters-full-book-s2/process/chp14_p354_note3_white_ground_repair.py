"""Add the source-reported white-ground proposal as a separate p.354 note claim."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
BODY = "chp-14:14_CHP-14_intro:l73-83"
STATEMENT_ID = "st-chp14-p354-note3-white-ground-proposal"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp14-p354-note3-white-ground-20261003")
ORIGINAL_QUOTE = "in which he implies that the ‘fantasia’ that artists should paint on white grounds rather than on the more usual reddish brown has only just occurred to him"
BODY_STATEMENTS = [
    "st-chp14-p354-algarotti-advocated-study-of-newton-optics",
    "st-chp14-p354-discussed-optics-and-encouraged-lighter-palette",
    "st-chp14-p354-algarotti-on-colourist-works",
]

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
if STATEMENT_ID in by_id:
    raise SystemExit(f"statement already exists: {STATEMENT_ID}")
if any(statement_id not in by_id for statement_id in BODY_STATEMENTS):
    raise SystemExit("one or more linked p.354 body statements are missing")
for statement_id in BODY_STATEMENTS:
    q = by_id[statement_id]["qualifiers"]
    if q.get("footnote_segment") != NOTES or q.get("footnote_line_range") != "L188":
        raise SystemExit(f"unexpected footnote link on {statement_id}")
    if "st-chp14-p354-note3-color-theory-sources" not in q.get("footnote_note_statement_ids", []):
        raise SystemExit(f"note 3 source link missing from {statement_id}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if ORIGINAL_QUOTE not in source_lines[187]:
    raise SystemExit("white-ground note claim no longer matches source L188")

row = {
    "statement_id": STATEMENT_ID, "segment_id": NOTES,
    "subject_candidate_id": "cand-0052", "object_candidate_id": "cand-10303",
    "predicate": "letter_reported_as_saying_white_ground_idea_had_only_just_occurred",
    "qualifiers": {
        "source_line_start": 188, "source_line_end": 188, "printed_page": 354,
        "pdf_physical_page": 8,
        "claim": "Haskell says the 13 May 1756 letter implies that the idea of artists painting fantasia on white rather than reddish-brown ground had only just occurred to Algarotti.",
        "speaker": "Haskell", "text_layer": "authorial report of a letter",
        "qualification": "The letter itself was not consulted; retain Haskell’s ‘implies’ and ‘only just occurred’ wording without claiming a verified date of invention.",
        "mentioned_candidate_ids": ["cand-0052", "cand-10303", "cand-2863"],
        "cross_reference_segments": [BODY],
        "cross_reference_text": "qualifies the color-theory discussion linked to footnote 3",
    },
    "original_quote": ORIGINAL_QUOTE, "origin": "book",
    "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
}
for statement_id in BODY_STATEMENTS:
    ids = by_id[statement_id]["qualifiers"]["footnote_note_statement_ids"]
    if STATEMENT_ID not in ids:
        ids.append(STATEMENT_ID)
rows.append(row)
print(json.dumps({"mode": "apply" if args.apply else "dry-run", "added_statement": STATEMENT_ID,
                  "linked_body_statements": len(BODY_STATEMENTS), "source_line": 188}, ensure_ascii=False))

if args.apply:
    if BACKUP.exists():
        if hashlib.sha256(BACKUP.read_bytes()).digest() != hashlib.sha256(TABLE.read_bytes()).digest():
            raise SystemExit(f"existing backup differs from current table: {BACKUP.name}")
    else:
        shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
        for item in rows:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(TABLE)
