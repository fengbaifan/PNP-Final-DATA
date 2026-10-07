"""Reconcile reviewed Chapter 7 pp.188-193 footnote links.

The source, PDF, and pre-write statement table are hash-locked. Dry-run is the
default; pass --apply only after reviewing the printed plan.
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
SOURCE_I = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
SOURCE_IV = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_iv.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"

EXPECTED_HASHES = {
    STATEMENTS: "2b087680602ca31f2cc4b4d8f38a90b7093eecc48a7436a50b2ca87dcd4c007c",
    SOURCE_I: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    SOURCE_IV: "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    PDF: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}

NOTES_I = "chp-7:07_CHP-7_sec_i:l293-389"
NOTES_IV = "chp-7:07_CHP-7_sec_iv:l97-119"

# statement_id: (marker, note segment, OCR source line, linked note statements)
BODY_LINKS = {
    "st-chp7-p188-i17": (1, NOTES_I, 368, ["st-chp7-p188-n1-cite-wittkower"]),
    "st-chp7-p188-i21": (2, NOTES_I, 369, ["st-chp7-p188-n2-cite-ibid-wittkower"]),
    "st-chp7-p189-i05": (1, NOTES_I, 370, ["st-chp7-p189-n1-cite-soprani"]),
    "st-chp7-p189-i07": (2, NOTES_I, 370, [
        "st-chp7-p189-n2-cite-pascoli", "st-chp7-p189-n2-cite-wittkower",
    ]),
    "st-chp7-p189-i12": (3, NOTES_I, 371, [
        "st-chp7-p189-n3-cite-montaiglon", "st-chp7-p189-n3-cite-bellori",
    ]),
    # The printed marker follows the full sentence, including the second clause.
    "st-chp7-p189-i13": (3, NOTES_I, 371, [
        "st-chp7-p189-n3-cite-montaiglon", "st-chp7-p189-n3-cite-bellori",
    ]),
    "st-chp7-p189-i15": (4, NOTES_I, 372, [
        "st-chp7-p189-n4-cite-zanotti", "st-chp7-p189-n4-cite-montaiglon",
        "st-chp7-p189-n4-cite-alazard", "st-chp7-p189-n4-claim-attempt",
        "st-chp7-p189-n4-claim-default",
    ]),
    "st-chp7-p189-i16": (4, NOTES_I, 372, [
        "st-chp7-p189-n4-cite-zanotti", "st-chp7-p189-n4-cite-montaiglon",
        "st-chp7-p189-n4-cite-alazard", "st-chp7-p189-n4-claim-attempt",
        "st-chp7-p189-n4-claim-default",
    ]),
    "st-chp7-p189-i24": (5, NOTES_I, 373, ["st-chp7-p189-n5-cite-zanotti"]),
    "st-chp7-p189-i27": (6, NOTES_I, 374, ["st-chp7-p189-n6-cite-dedominici"]),
    "st-chp7-p193-leopold-patronizes-vecchia": (1, NOTES_IV, 98, [
        "st-chp7-p193-n1-von-holst",
    ]),
    "st-chp7-p193-vecchia-forgeries": (1, NOTES_IV, 98, [
        "st-chp7-p193-n1-von-holst",
    ]),
    "st-chp7-p193-wittelsbach-alliance": (3, NOTES_IV, 99, [
        "st-chp7-p193-n3-lavagnino-heilbronner",
    ]),
}

QUALIFICATIONS = {
    "st-chp7-p188-i17": "注1位于脚注段L368，引用Wittkower 1955年本第230–231页；书目用于识别该书，所引页未独立查阅。此处仍是Haskell的表述。",
    "st-chp7-p188-i21": "注2位于脚注段L369，以ibid.承接注1并引Wittkower第234–236页；所引页未独立查阅。",
    "st-chp7-p189-i05": "注1位于L370，引用Soprani I, p.254；所引页未独立查阅。“new reign”不据此精确化为某个年份。",
    "st-chp7-p189-i07": "注2与注1同在OCR行L370，引用Pascoli I, p.255和Wittkower 1938；所引材料未独立查阅。原文说明的是计划依据Le Brun提供的图样。",
    "st-chp7-p189-i12": "注3位于L371，引用Montaiglon I, p.104及Bellori 1942, pp.101、126；所引页未独立查阅。被动语态没有指明委托者，不补造委托端点。",
    "st-chp7-p189-i13": "注3位于L371，引用Montaiglon I, p.104及Bellori 1942, pp.101、126；所引页未独立查阅。保留原文关于报酬和称号的表述，不扩写授予程序。",
    "st-chp7-p189-i15": "注4位于L372，引用Zanotti I, p.245、Montaiglon I, p.190，并在同一注中补述1685年Giordano事件及Alazard, p.142；均未独立查阅。两幅作品未具名。",
    "st-chp7-p189-i16": "注4位于L372，引用Zanotti I, p.245、Montaiglon I, p.190，并在同一注中补述1685年Giordano事件及Alazard, p.142；均未独立查阅。句末评价是Haskell的解释；印本大小写校读保留在原OCR订正记录中。",
    "st-chp7-p189-i24": "印本注5位于L373，OCR将注号识为6；注中引Zanotti I, pp.155、170、199及II, p.121，未独立查阅。‘suspect’所表达的判断仍是Haskell的推测。",
    "st-chp7-p189-i27": "注6位于L374，引用De Dominici IV, p.50；所引页未独立查阅。画作身份与后续去向仍按正文限定。",
    "st-chp7-p193-leopold-patronizes-vecchia": "印本注1位于L98，引用von Holst, p.132；所引页未独立查阅。最高级评价属于Haskell，未指明具体委托。",
    "st-chp7-p193-vecchia-forgeries": "印本注1位于L98，引用von Holst, p.132；所引页未独立查阅。没有具名伪作；此处是Haskell对Vecchia声誉的陈述，不构成独立核验。",
    "st-chp7-p193-wittelsbach-alliance": "印本注3位于L99，引用Lavagnino, p.69及Heilbronner, pp.887–904；所引资料未独立查阅。句中未点名统治家族，邻近的Savoy线索不足以确定身份；‘most astute’是Haskell的评价。",
}

NOTE_BODY_LINKS = {
    "st-chp7-p189-n4-cite-zanotti": ["st-chp7-p189-i15", "st-chp7-p189-i16"],
    "st-chp7-p189-n4-cite-montaiglon": ["st-chp7-p189-i15", "st-chp7-p189-i16"],
    "st-chp7-p189-n4-cite-alazard": ["st-chp7-p189-i15", "st-chp7-p189-i16"],
    "st-chp7-p189-n4-claim-attempt": ["st-chp7-p189-i15", "st-chp7-p189-i16"],
    "st-chp7-p189-n4-claim-default": ["st-chp7-p189-i15", "st-chp7-p189-i16"],
    "st-chp7-p193-n1-von-holst": [
        "st-chp7-p193-leopold-patronizes-vecchia", "st-chp7-p193-vecchia-forgeries",
    ],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows() -> tuple[str, list[dict]]:
    text = STATEMENTS.read_text(encoding="utf-8")
    return text, [json.loads(line) for line in text.splitlines() if line.strip()]


def write_rows(rows: list[dict]) -> None:
    with STATEMENTS.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def by_id(rows: list[dict]) -> dict[str, dict]:
    result = {row["statement_id"]: row for row in rows}
    if len(result) != len(rows):
        raise SystemExit("duplicate statement_id in book-statements.jsonl")
    return result


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed pp.188-193 footnote reconciliation")
args = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"hash lock failed for {path.relative_to(ROOT)}: {actual}")

_, rows = read_rows()
indexed = by_id(rows)
if set(BODY_LINKS) != set(QUALIFICATIONS):
    raise SystemExit("body-link and qualification plans do not have the same statement ids")

source_i_lines = SOURCE_I.read_text(encoding="utf-8").splitlines()
source_iv_lines = SOURCE_IV.read_text(encoding="utf-8").splitlines()
for line_number, required in {
    368: "1 Wittkower, 1955",
    369: "2 ibid.",
    370: "1 Soprani, I, p. 254. 2 Pascoli",
    371: "3 Montaiglon, I, p. 104",
    372: "4 Zanotti, I, p. 245",
    373: "Zanotti, I, pp. 155",
    374: "6 De Dominici, IV, p. 50",
}.items():
    if required not in source_i_lines[line_number - 1]:
        raise SystemExit(f"unexpected Chapter 7 section I OCR at L{line_number}")
for line_number, required in {98: "von Holst, p. 132", 99: "Lavagnino, p. 69"}.items():
    if required not in source_iv_lines[line_number - 1]:
        raise SystemExit(f"unexpected Chapter 7 section IV OCR at L{line_number}")

all_note_ids = {note_id for _, _, _, note_ids in BODY_LINKS.values() for note_id in note_ids}
if not all_note_ids.issubset(indexed):
    raise SystemExit(f"missing note statements: {sorted(all_note_ids - indexed.keys())}")
if not set(NOTE_BODY_LINKS).issubset(indexed):
    raise SystemExit(f"missing note statements for body-link update: {sorted(set(NOTE_BODY_LINKS) - indexed.keys())}")

statements = copy.deepcopy(rows)
work = by_id(statements)
for statement_id, (marker, segment_id, source_line, note_ids) in BODY_LINKS.items():
    row = work.get(statement_id)
    if row is None:
        raise SystemExit(f"missing body statement: {statement_id}")
    q = row.setdefault("qualifiers", {})
    if q.get("footnote_marker") not in (None, marker):
        raise SystemExit(f"unexpected marker on {statement_id}: {q.get('footnote_marker')}")
    expected_page = 188 if "p188" in statement_id else 189 if "p189" in statement_id else 193
    if q.get("printed_page") != expected_page:
        raise SystemExit(f"unexpected printed page on {statement_id}")
    q.update({
        "footnote_marker": marker,
        "footnote_segment": segment_id,
        "footnote_segment_id": segment_id,
        "footnote_source_line": source_line,
        "footnote_source_lines": [source_line],
        "footnote_refs": [{"marker": marker, "segment_id": segment_id, "source_line": source_line}],
        "footnote_statement_ids": note_ids,
        "footnote_link_status": "resolved_source_migration",
        "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_pending": False,
        "qualification": QUALIFICATIONS[statement_id],
    })

for note_id, body_ids in NOTE_BODY_LINKS.items():
    q = work[note_id].setdefault("qualifiers", {})
    q["linked_body_statement_ids"] = body_ids

for body_id, (marker, segment_id, source_line, note_ids) in BODY_LINKS.items():
    for note_id in note_ids:
        q = work[note_id]["qualifiers"]
        if q.get("footnote_marker") not in (None, marker) or q.get("source_line_start") != source_line:
            raise SystemExit(f"note locator mismatch for {note_id}")
        if body_id not in q.get("linked_body_statement_ids", []):
            raise SystemExit(f"note-to-body link missing: {note_id} -> {body_id}")

print("verified CHP-7 physical pp.188, 189, and 193 against the locked PDF and S0 note lines")
print("planned body links: 13 statements; p.189 marker 3 covers both clauses in the Maratta sentence")
print("planned note anchors: add the p.189 marker-4 body span and p.193 marker-1 compound sentence to existing note links")
print("expected legacy flags cleared: 12; no statements, mentions, candidates, coverage rows, or formal relations added")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp7-p188-193-footnotes-"))
shutil.copy2(STATEMENTS, backup_dir / STATEMENTS.name)
write_rows(statements)

_, written_rows = read_rows()
written = by_id(written_rows)
for statement_id, (marker, segment_id, source_line, note_ids) in BODY_LINKS.items():
    q = written[statement_id]["qualifiers"]
    if q.get("footnote_pending") is not False or q.get("footnote_body_link_status") != "linked":
        raise SystemExit(f"post-write footnote status failed for {statement_id}; backup: {backup_dir}")
    if q.get("footnote_source_line") != source_line or q.get("footnote_statement_ids") != note_ids:
        raise SystemExit(f"post-write footnote locator failed for {statement_id}; backup: {backup_dir}")
for note_id, body_ids in NOTE_BODY_LINKS.items():
    if written[note_id]["qualifiers"].get("linked_body_statement_ids") != body_ids:
        raise SystemExit(f"post-write note-to-body link failed for {note_id}; backup: {backup_dir}")
print(f"applied Chapter 7 footnote reconciliation; recovery copy: {backup_dir}")
