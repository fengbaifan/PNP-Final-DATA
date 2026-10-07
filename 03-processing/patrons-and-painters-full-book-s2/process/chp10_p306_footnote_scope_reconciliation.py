"""Correct the p.306 marker scope and link note 1 to its printed anchor.

The PDF, OCR source, and pre-write statement table are hash-locked. Dry-run is
the default; pass --apply only after reviewing the printed plan.
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
SEGMENT = "chp-10:10_CHP-10_intro:l435-443"
NOTE_ID = "st-chp10-p306-note1-blunt-citation"
DRAWING_ID = "st-chp10-p306-pasquali-visentini-drawings"
MISATTACHED_IDS = (
    "st-chp10-p306-smith-acquired-ricci-studio",
    "st-chp10-p306-smith-bought-old-masters",
    "st-chp10-p306-smith-formed-drawing-collection",
)

EXPECTED_HASHES = {
    STATEMENTS: "e9955b1ea223f74e52b9ad26e80117083a38d205f057772b4d16884587a9a433",
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
}

QUALIFICATIONS = {
    "st-chp10-p306-smith-acquired-ricci-studio": (
        "这是Haskell关于Ricci去世后Smith可能购入工作室内容的推测。印本注1位于后续Visentini原稿句后，"
        "既有注释statement也将其映射到该绘稿陈述；不把注1当作本条的独立佐证。"
    ),
    "st-chp10-p306-smith-bought-old-masters": (
        "Haskell以‘No doubt’表达推测，具体画作未具名。印本注1位于本段末Visentini原稿句后，"
        "不将该标号重复附到此项购藏判断。"
    ),
    "st-chp10-p306-smith-formed-drawing-collection": (
        "Haskell以‘must’表达推测，没有提供库存清单。印本注1紧随后文关于Visentini原稿的句子，"
        "不把该标号重复附到这条单独的收藏推断。"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows() -> list[dict]:
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


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
parser.add_argument("--apply", action="store_true", help="write the reviewed p.306 scope correction")
args = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"hash lock failed for {path.relative_to(ROOT)}: {actual}")

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
if "Smith retained the original" not in source_lines[436] or "Visentini.1" not in source_lines[436]:
    raise SystemExit("unexpected S0 body text at p.306 L437")
if "Blunt and Croft-Murray" not in source_lines[440] or "pp. 67 if" not in source_lines[440]:
    raise SystemExit("unexpected S0 inline footnote text at p.306 L441")

rows = read_rows()
indexed = by_id(rows)
if not set(MISATTACHED_IDS + (DRAWING_ID, NOTE_ID)).issubset(indexed):
    raise SystemExit("one or more expected p.306 statements are missing")
for statement_id in MISATTACHED_IDS:
    q = indexed[statement_id].get("qualifiers", {})
    if q.get("printed_page") != 306 or q.get("footnote_marker") != 1 or q.get("footnote_text_pending") is not True:
        raise SystemExit(f"unexpected pre-state for stale marker {statement_id}")

note = indexed[NOTE_ID]
note_q = note.get("qualifiers", {})
if note_q.get("body_statement_id") != DRAWING_ID or note_q.get("printed_marker_line") != 437:
    raise SystemExit("note 1 is not explicitly mapped to the Visentini drawings statement")
body = indexed[DRAWING_ID]
body_q = body.get("qualifiers", {})
if body_q.get("footnote_marker") != 1 or body_q.get("footnote_text_pending") is not False:
    raise SystemExit("unexpected pre-state for the printed note 1 anchor")

updated = copy.deepcopy(rows)
work = by_id(updated)
for statement_id in MISATTACHED_IDS:
    q = work[statement_id]["qualifiers"]
    q.pop("footnote_marker", None)
    q.pop("footnote_text_pending", None)
    q["qualification"] = QUALIFICATIONS[statement_id]

body_q = work[DRAWING_ID]["qualifiers"]
body_q.update({
    "footnote_segment": SEGMENT,
    "footnote_segment_id": SEGMENT,
    "footnote_source_line": 441,
    "footnote_source_lines": [441],
    "footnote_refs": [{"marker": 1, "segment_id": SEGMENT, "source_line": 441}],
    "footnote_statement_ids": [NOTE_ID],
    "footnote_link_status": "resolved_source_migration",
    "footnote_text_pending": False,
    "footnote_body_link_status": "linked",
    "footnote_pending": False,
})

print("verified CHP-10 physical p.306: printed note 1 follows the Visentini drawings sentence")
print("planned change: remove the inherited marker and stale pending flag from three preceding claims")
print("planned link: connect the printed marker to the existing Blunt/Croft-Murray note statement and drawings claim")
print("expected data effect: 4 existing statement qualifiers updated; no rows, candidates, mentions, coverage, or relations added")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp10-p306-footnote-scope-"))
shutil.copy2(STATEMENTS, backup_dir / STATEMENTS.name)
write_rows(updated)

written = by_id(read_rows())
for statement_id in MISATTACHED_IDS:
    q = written[statement_id]["qualifiers"]
    if "footnote_marker" in q or "footnote_text_pending" in q:
        raise SystemExit(f"stale marker remains on {statement_id}; backup: {backup_dir}")
body_q = written[DRAWING_ID]["qualifiers"]
if body_q.get("footnote_body_link_status") != "linked" or body_q.get("footnote_statement_ids") != [NOTE_ID]:
    raise SystemExit(f"p.306 note 1 body link failed; backup: {backup_dir}")
print(f"applied p.306 footnote scope correction; recovery copy: {backup_dir}")
