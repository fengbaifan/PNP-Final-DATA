"""Reconcile Chapter 13 pp.332-338 footnote links and inherited markers.

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
NOTES = "chp-13:13_CHP-13_intro:l179-251"

EXPECTED_HASHES = {
    STATEMENTS: "c4b092798124df74374b88179f195765e49ea7ca313050e72d891b1e55029758",
    SOURCE: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
}

# statement_id: (printed marker, printed page, note OCR line, note statements)
BODY_LINKS = {
    "st-chp13-p332-publishing-role-in-venetian-economy": (1, 332, 180, [
        "st-chp13-p332-n1-brown-survey-citation",
    ]),
    "st-chp13-p332-republic-efforts-to-maintain-publishing-supremacy": (1, 332, 180, [
        "st-chp13-p332-n1-brown-survey-citation",
    ]),
    "st-chp13-p332-grosley-venice-paris-publication-permission-report": (2, 332, 181, [
        "st-chp13-p332-n2-berengo-citation",
    ]),
    "st-chp13-p332-bookshops-cultural-contact": (3, 332, 182, [
        "st-chp13-p332-n3-goethe-citation",
    ]),
    "st-chp13-p332-government-copyright-encouragement": (4, 332, 183, [
        "st-chp13-p332-n4-berengo-citation", "st-chp13-p332-n4-morazzoni-citation",
        "st-chp13-p332-n4-gallo-citation", "st-chp13-p332-n4-marin-counterview",
    ]),
    "st-chp13-p332-marieschi-views-appealed-to-fragonard": (5, 332, 184, [
        "st-chp13-p332-n5-morazzoni-citation",
    ]),
    "st-chp13-p333-barbarigo-1765-pamphlet-instructions-through-gozzi": (1, 333, 185, [
        "st-chp13-p333-n1-roberti-citation",
    ]),
    "st-chp13-p334-albrizzi-birth-and-inherited-business": (2, 334, 187, [
        "st-chp13-p334-n2-morazzoni-citation",
    ]),
    "st-chp13-p334-albrizzi-travel-and-vienna-education": (3, 334, 188, [
        "st-chp13-p334-n3-bossuet-eighth-volume-1755",
    ]),
    "st-chp13-p334-almoro-organized-academy": (4, 334, 189, [
        "st-chp13-p334-n4-battagia-citation",
    ]),
    "st-chp13-p334-albrizzi-edited-weekly-bulletin": (5, 334, 190, [
        "st-chp13-p334-n5-novelle-publication-from-1729",
    ]),
    "st-chp13-p334-bossuet-interest-and-heresy-context": (6, 334, 191, [
        "st-chp13-p334-n6-hazard-citation",
    ]),
}

MISATTACHED = {
    "st-chp13-p332-copyright-effects-on-local-and-export-books": (
        4,
        "印本注4落在前一句关于政府版权政策的句末；本句随后讨论本地市场与奢华出口版的长期影响，未见独立脚注标记。注4中的Marin反向评价仍连于前句，不在此重复挂接。",
    ),
    "st-chp13-p337-officium-commissioned-and-financed-by-caime": (
        5,
        "印本注5落在前一句关于《Beatae Mariae Virginis Officium》插图宗教亲密感的句末；随后点名Caime的委托与资助句没有独立脚注标记。保留原文姓氏和断言范围。",
    ),
    "st-chp13-p338-goldoni-biographical-episodes-in-illustrations": (
        1,
        "印本注1落在前一句Goldoni提出各卷扉页表现其生平场景之后，并已连接至该方案statement；本句列举传记插图内容，没有独立脚注标记，不重复使用注1。",
    ),
}

REMOVE_FOOTNOTE_FIELDS = (
    "footnote_marker", "footnote_pending", "footnote_text_pending",
    "footnote_link_status", "footnote_body_link_status", "footnote_segment",
    "footnote_segment_id", "footnote_source_line", "footnote_source_lines",
    "footnote_refs", "footnote_statement_ids",
)


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
parser.add_argument("--apply", action="store_true", help="write the reviewed Chapter 13 footnote reconciliation")
args = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"hash lock failed for {path.relative_to(ROOT)}: {actual}")

source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
source_checks = {
    180: "1 For a general survey",
    181: "2 Quoted by M. Berengo",
    182: "3 See, for instance",
    183: "4 Berengo, 1957",
    184: "5 Morazzoni, p. 70",
    185: "1 Roberti, 1900",
    187: "2 Morazzoni, p. 131",
    188: "3 This seems clear",
    189: "4 Battagia, p. 76",
    190: "6 The Novelle della Repubblica",
    191: "6 Hazard, 1946",
}
for line_number, fragment in source_checks.items():
    if fragment not in source_lines[line_number - 1]:
        raise SystemExit(f"unexpected Chapter 13 S0 OCR at L{line_number}")

rows = read_rows()
indexed = by_id(rows)
all_note_ids = {note_id for _, _, _, note_ids in BODY_LINKS.values() for note_id in note_ids}
if not (set(BODY_LINKS) | set(MISATTACHED) | all_note_ids).issubset(indexed):
    missing = (set(BODY_LINKS) | set(MISATTACHED) | all_note_ids) - indexed.keys()
    raise SystemExit(f"missing Chapter 13 statements: {sorted(missing)}")

for body_id, (marker, printed_page, source_line, note_ids) in BODY_LINKS.items():
    row = indexed[body_id]
    q = row.get("qualifiers", {})
    if q.get("printed_page") != printed_page or q.get("footnote_marker") != marker:
        raise SystemExit(f"unexpected printed marker or page on {body_id}")
    if q.get("footnote_text_pending") is not True and q.get("footnote_pending") is not True:
        raise SystemExit(f"expected old pending flag not present on {body_id}")
    for note_id in note_ids:
        note = indexed[note_id]
        nq = note.get("qualifiers", {})
        if note.get("segment_id") != NOTES or nq.get("source_line_start") != source_line:
            raise SystemExit(f"note locator mismatch for {note_id}")
        if body_id not in nq.get("linked_body_statement_ids", []):
            raise SystemExit(f"note-to-body link missing: {note_id} -> {body_id}")

for body_id, (marker, _) in MISATTACHED.items():
    q = indexed[body_id].get("qualifiers", {})
    if q.get("footnote_marker") != marker or q.get("footnote_text_pending") is not True:
        raise SystemExit(f"unexpected inherited-marker state on {body_id}")
    if any(body_id in indexed[note_id].get("qualifiers", {}).get("linked_body_statement_ids", []) for note_id in all_note_ids):
        raise SystemExit(f"a note statement still links to misattached body statement {body_id}")

weekly_note = indexed["st-chp13-p334-n5-novelle-publication-from-1729"]["qualifiers"]
if not any(
    correction.get("source_line") == 190 and correction.get("print", "").startswith("5 The Novelle")
    for correction in weekly_note.get("ocr_corrections", [])
):
    raise SystemExit("the p.334 printed note-5/OCR-note-6 correction is not recorded")

updated = copy.deepcopy(rows)
work = by_id(updated)
for body_id, (marker, printed_page, source_line, note_ids) in BODY_LINKS.items():
    q = work[body_id]["qualifiers"]
    refs = copy.deepcopy(q.get("footnote_refs") or [])
    if len(refs) > 1:
        raise SystemExit(f"unexpected multiple footnote refs on {body_id}")
    if refs:
        ref = refs[0]
        ref.update({"marker": marker, "segment_id": NOTES, "source_line": source_line})
        for key in ("footnote_note_statement_ids", "note_statement_ids"):
            if key in ref:
                ref[key] = note_ids
        if "footnote_body_link_status" in ref:
            ref["footnote_body_link_status"] = "linked"
        if "footnote_text_pending" in ref:
            ref["footnote_text_pending"] = False
        refs[0] = ref
    else:
        refs = [{"marker": marker, "segment_id": NOTES, "source_line": source_line}]
    q.update({
        "footnote_marker": marker,
        "footnote_segment": NOTES,
        "footnote_segment_id": NOTES,
        "footnote_source_line": source_line,
        "footnote_source_lines": [source_line],
        "footnote_refs": refs,
        "footnote_statement_ids": note_ids,
        "footnote_link_status": "resolved_source_migration",
        "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_pending": False,
    })

for body_id, (marker, qualification_note) in MISATTACHED.items():
    q = work[body_id]["qualifiers"]
    for key in REMOVE_FOOTNOTE_FIELDS:
        q.pop(key, None)
    q["qualification"] = f"{q.get('qualification', '').rstrip()} {qualification_note}".strip()

print("verified CHP-13 printed pp.332-338 against page images, source notes L180-191, and migrated note statements")
print("planned valid links: 12 legacy pending body statements, each mapped to existing note statements by exact page/line")
print("planned scope corrections: remove inherited markers from p.332 local/export effect, p.337 Caime, and p.338 illustrated episodes")
print("p.334 printed note 5 / S0 OCR note 6 correction is present and retained")
print("expected table effect: update 15 existing statement qualifiers; no rows, candidates, mentions, coverage, or relations added")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp13-p332-338-footnotes-"))
shutil.copy2(STATEMENTS, backup_dir / STATEMENTS.name)
write_rows(updated)

written = by_id(read_rows())
for body_id, (marker, printed_page, source_line, note_ids) in BODY_LINKS.items():
    q = written[body_id]["qualifiers"]
    if q.get("footnote_body_link_status") != "linked" or q.get("footnote_pending") is not False:
        raise SystemExit(f"post-write linked status failed for {body_id}; backup: {backup_dir}")
    if q.get("footnote_source_line") != source_line or q.get("footnote_statement_ids") != note_ids:
        raise SystemExit(f"post-write link target failed for {body_id}; backup: {backup_dir}")
for body_id in MISATTACHED:
    q = written[body_id]["qualifiers"]
    if any(key in q for key in REMOVE_FOOTNOTE_FIELDS):
        raise SystemExit(f"post-write inherited marker remains on {body_id}; backup: {backup_dir}")
print(f"applied Chapter 13 footnote reconciliation; recovery copy: {backup_dir}")
