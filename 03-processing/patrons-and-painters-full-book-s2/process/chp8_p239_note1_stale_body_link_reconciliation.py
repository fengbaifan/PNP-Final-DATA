"""Repair stale body-statement links on the p.239 note 1 statements.

The original target identifier no longer exists; the corresponding p.238
Florence-stay statement is present and retains the same claim. The statement
table, OCR source, and printed PDF are hash-locked. Dry-run is the default.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"

OLD_BODY_ID = "st-chp8-p239-returned-to-florence-and-housed-at-pratolino"
BODY_ID = "st-chp8-p238-returned-to-florence-and-housed-at-pratolino"
NOTE_IDS = (
    "st-chp8-p239-note1-luigi-crespi-stay",
    "st-chp8-p239-note1-haskell-eight-month-maximum",
    "st-chp8-p239-note1-zanotti-multiple-visits",
)

EXPECTED_HASHES = {
    STATEMENTS: "d099b8e0ab25f2637bb3530ebfd8fba5328078d0d259dd5bce729ddfbc3eae33",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows() -> list[dict]:
    return [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def by_id(rows: list[dict]) -> dict[str, dict]:
    result = {row["statement_id"]: row for row in rows}
    if len(result) != len(rows):
        raise SystemExit("duplicate statement_id in book-statements.jsonl")
    return result


def write_rows(rows: list[dict]) -> None:
    with STATEMENTS.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.239 note 1 link correction")
args = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"hash lock failed for {path.relative_to(ROOT)}: {actual}")

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
source_checks = {
    333: "In 1709 Crespi returned to Florence",
    334: "where he stayed for several months",
    339: "great days of his patronage were over.1",
    449: "L. Crespi, p. 211",
}
for line_number, fragment in source_checks.items():
    if fragment not in source_lines[line_number - 1]:
        raise SystemExit(f"unexpected Chapter 8 S0 OCR at L{line_number}")

rows = read_rows()
indexed = by_id(rows)
required = {BODY_ID, *NOTE_IDS}
if not required.issubset(indexed):
    raise SystemExit(f"missing Chapter 8 statements: {sorted(required - indexed.keys())}")
if OLD_BODY_ID in indexed:
    raise SystemExit("old body target unexpectedly exists; review before changing links")

body = indexed[BODY_ID]
body_q = body.get("qualifiers", {})
if body.get("segment_id") != "chp-8:08_CHP-8_sec_ii:l327-336":
    raise SystemExit("unexpected p.238 body segment")
if (body_q.get("printed_page"), body_q.get("pdf_physical_page"), body_q.get("source_line_start"), body_q.get("source_line_end")) != (238, 44, 333, 334):
    raise SystemExit("unexpected Florence-stay body locator")
if "where he stayed for several months" not in body.get("original_quote", ""):
    raise SystemExit("Florence-stay body claim no longer matches the note content")

for note_id in NOTE_IDS:
    row = indexed[note_id]
    q = row.get("qualifiers", {})
    if (row.get("segment_id"), q.get("printed_page"), q.get("pdf_physical_page"), q.get("source_line_start")) != (
        "chp-8:08_CHP-8_sec_ii:l372-461", 239, 45, 449
    ):
        raise SystemExit(f"unexpected p.239 note locator: {note_id}")
    if q.get("footnote_marker") != 1 or q.get("linked_body_statement_ids") != [OLD_BODY_ID]:
        raise SystemExit(f"unexpected old note link state: {note_id}")

updated = copy.deepcopy(rows)
work = by_id(updated)
for note_id in NOTE_IDS:
    work[note_id]["qualifiers"]["linked_body_statement_ids"] = [BODY_ID]

print("verified the p.239 marker/note and the p.238 Florence-stay statement against S0 and the printed PDF hash")
print("planned repair: remap 3 note statements from a missing legacy body ID to the existing p.238 statement")
print("expected table effect: update 3 existing statement qualifiers; no rows or other table counts change")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp8-p239-note1-link-"))
shutil.copy2(STATEMENTS, backup_dir / STATEMENTS.name)
write_rows(updated)

written = by_id(read_rows())
if any(written[sid]["qualifiers"].get("linked_body_statement_ids") != [BODY_ID] for sid in NOTE_IDS):
    raise SystemExit(f"post-write target verification failed; backup: {backup_dir}")
if len(written) != len(rows):
    raise SystemExit(f"post-write statement count changed; backup: {backup_dir}")
print(f"applied p.239 note 1 body-link reconciliation; recovery copy: {backup_dir}")
