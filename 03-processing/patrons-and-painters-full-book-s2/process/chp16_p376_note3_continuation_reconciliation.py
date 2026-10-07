"""Close the p.376 note 3 link to its continuation on p.377.

The statement table, S0 transcription, and printed PDF are hash-locked.
Dry-run is the default; pass --apply only after reviewing the plan.
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-16.pdf"

BODY_ID = "st-chp16-p376-swajer-secret-manuscripts-partial"
NOTE_ID = "st-chp16-p376-note3-swajer-correspondence-partial"
NOTE_SEGMENT = "chp-16:16_CHP-16_intro:l69-89"
CONTINUATION_SEGMENT = "chp-16:16_CHP-16_intro:l48-64"
CONTINUATION_IDS = (
    "st-chp16-p377-note3-vannetti-correspondence",
    "st-chp16-p377-note3-durazzo-correspondence",
    "st-chp16-p377-note3-published-swajer-tiepolo-letter",
    "st-chp16-p377-note3-published-gian-domenico-swajer-letter",
    "st-chp16-p377-note3-letter-and-consaputo-quadro",
    "st-chp16-p377-note3-ghelthof-provenance-claim",
    "st-chp16-p377-note3-ghelthof-reliability-caution",
    "st-chp16-p377-note3-state-archive-locator",
)

EXPECTED_HASHES = {
    STATEMENTS: "48d1f209cd56b394f028d5ab81125e94bceb7881999952604d4cb3bdda30b9a0",
    SOURCE: "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff",
    PDF: "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f",
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
parser.add_argument("--apply", action="store_true", help="write the reviewed p.376 note 3 reconciliation")
args = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"hash lock failed for {path.relative_to(ROOT)}: {actual}")

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
source_checks = {
    84: "3 A good deal of Swajer",
    60: "by Valerio Vannetti in Roveredo",
    64: "His papers and manuscripts are mentioned in the Archivio di Stato",
}
for line_number, fragment in source_checks.items():
    if fragment not in source_lines[line_number - 1]:
        raise SystemExit(f"unexpected Chapter 16 S0 OCR at L{line_number}")

rows = read_rows()
indexed = by_id(rows)
required_ids = {BODY_ID, NOTE_ID, *CONTINUATION_IDS}
if not required_ids.issubset(indexed):
    raise SystemExit(f"missing Chapter 16 statements: {sorted(required_ids - indexed.keys())}")

body = indexed[BODY_ID]
body_q = body.get("qualifiers", {})
if body.get("segment_id") != "chp-16:16_CHP-16_intro:l38-46":
    raise SystemExit("unexpected p.376 body segment")
if body_q.get("printed_page") != 376 or body_q.get("source_line_start") != 46:
    raise SystemExit("unexpected p.376 body locator")
if body_q.get("footnote_marker") != "3" or body_q.get("footnote_text_pending") is not True:
    raise SystemExit("expected p.376 marker 3 pending state is not present")

note = indexed[NOTE_ID]
note_q = note.get("qualifiers", {})
if note.get("segment_id") != NOTE_SEGMENT or note_q.get("source_line_start") != 84:
    raise SystemExit("unexpected p.376 note 3 source locator")
if note_q.get("footnote_marker") != "3" or body_q.get("footnote_note_statement_ids") != [NOTE_ID]:
    raise SystemExit("p.376 body and note 3 are not linked as expected")

covered_lines: set[int] = set()
for statement_id in CONTINUATION_IDS:
    row = indexed[statement_id]
    q = row.get("qualifiers", {})
    if row.get("segment_id") != CONTINUATION_SEGMENT:
        raise SystemExit(f"unexpected continuation segment on {statement_id}")
    if q.get("footnote_marker") != "3" or q.get("footnote_line_range") != "L84-L84":
        raise SystemExit(f"unexpected note 3 association on {statement_id}")
    if NOTE_ID not in q.get("footnote_note_statement_ids", []):
        raise SystemExit(f"continuation statement is not associated with {NOTE_ID}: {statement_id}")
    start, end = q.get("source_line_start"), q.get("source_line_end")
    if not isinstance(start, int) or not isinstance(end, int) or not (60 <= start <= end <= 64):
        raise SystemExit(f"unexpected continuation line range on {statement_id}")
    covered_lines.update(range(start, end + 1))
if covered_lines != set(range(60, 65)):
    raise SystemExit(f"existing note statements do not cover p.377 L60-L64: {sorted(covered_lines)}")

updated = copy.deepcopy(rows)
work = by_id(updated)
body_q = work[BODY_ID]["qualifiers"]
note_q = work[NOTE_ID]["qualifiers"]

body_q.update({
    "footnote_segment": NOTE_SEGMENT,
    "footnote_segment_id": NOTE_SEGMENT,
    "footnote_source_line": 84,
    "footnote_source_lines": [84, 60],
    "footnote_line_range": "L84-L84",
    "footnote_refs": [{
        "footnote_marker": "3",
        "footnote_printed_page": 376,
        "footnote_segment": NOTE_SEGMENT,
        "footnote_line_range": "L84-L84",
        "continuation_segment": CONTINUATION_SEGMENT,
        "continuation_line_range": "L60-L64",
        "footnote_note_statement_ids": [NOTE_ID],
        "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
    }],
    "footnote_statement_ids": [NOTE_ID],
    "footnote_note_statement_ids": [NOTE_ID],
    "footnote_link_status": "resolved_source_migration",
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "footnote_pending": False,
    "footnote_link_note": (
        "Printed note 3 begins at p.376 L84 and continues at p.377 L60-L64; "
        "the continuation is represented by the eight existing p.377 note statements."
    ),
})

note_q.update({
    "claim": (
        "Haskell's note locates Swajer's correspondence at Seminario Patriarcale and "
        "describes letter groups, published Tiepolo correspondence, a provenance claim "
        "and caution, and a State Archive locator."
    ),
    "text_layer": "cross-page printed note",
    "qualification": (
        "The cited letters, archive records, and Ateneo Veneto item were not independently "
        "consulted; the provenance claim and reliability caution remain Haskell's report."
    ),
    "continuation_quote": "\n".join(source_lines[59:64]),
    "continuation_source_segment_id": CONTINUATION_SEGMENT,
    "continuation_source_lines": [60, 64],
    "continuation_source_line_range": "L60-L64",
    "footnote_source_lines": [84, 60],
    "footnote_pending": False,
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "footnote_continuation": True,
    "linked_body_statement_ids": [BODY_ID],
    "footnote_link_note": "Printed note 3 starts at p.376 L84 and continues on p.377 at L60-L64.",
})

print("verified the p.376 marker, p.376 note opening, p.377 note continuation, and eight existing continuation statements")
print("planned links: resolve the single body footnote and record its exact cross-page note span")
print("planned note repair: retain the opening quote, add continuation provenance, and close pending status")
print("expected table effect: update 2 existing statements; no rows, candidates, mentions, coverage, or relations added")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp16-p376-note3-"))
shutil.copy2(STATEMENTS, backup_dir / STATEMENTS.name)
write_rows(updated)

written = by_id(read_rows())
written_body_q = written[BODY_ID]["qualifiers"]
written_note_q = written[NOTE_ID]["qualifiers"]
if written_body_q.get("footnote_text_pending") is not False or written_body_q.get("footnote_pending") is not False:
    raise SystemExit(f"post-write body pending state remains; backup: {backup_dir}")
if written_body_q.get("footnote_body_link_status") != "linked" or written_body_q.get("footnote_note_statement_ids") != [NOTE_ID]:
    raise SystemExit(f"post-write body link failed; backup: {backup_dir}")
if written_note_q.get("continuation_source_line_range") != "L60-L64" or written_note_q.get("footnote_text_pending") is not False:
    raise SystemExit(f"post-write continuation provenance failed; backup: {backup_dir}")
if len(written) != len(rows):
    raise SystemExit(f"post-write statement count changed; backup: {backup_dir}")
print(f"applied p.376 note 3 reconciliation; recovery copy: {backup_dir}")
