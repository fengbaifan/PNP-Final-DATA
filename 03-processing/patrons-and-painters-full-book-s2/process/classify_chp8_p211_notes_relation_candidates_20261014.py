"""Classify p.211 visually transcribed footnote statements for S2 relations."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_chp8_p211_notes_crop.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4"
SEGMENT_SHA = "55e7ef0c7f6fcfae4d11c6a1e6420bd409d0091b8f88961687d9905f06b3ddff"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp8-p211-notes-relation-review-20261014")
EXPECTED_HASHES = {
    STATEMENTS: "582c31bdfb313d7567d0825f434a43adc67866a74ad0fa3faf570869215d1bd1",
    SOURCE: "2a50e65bd1add38adc02bce184d6e58d286424588ef617411bd5e5c9e22877a4",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "4b929d16e9098d94efc3a352e70c070bd0418c4432ce5c5cc82c158020d9cb21",
}

TRUE_NOTES = {
    "st-chp8-p211-cinelli-inventory-incidental-biographical-information":
        "Haskell says both the 1677 account and 1689 inventory provide incidental biographical information; this is a source-to-claim relation, not independent verification of either document.",
    "st-chp8-p211-dolci-picture-burghley-exhibition-reference":
        "The note reports both a location for the identified Dolci picture and its 1960 exhibition; retain the claims as attributed and leave the exhibition endpoint unresolved.",
    "st-chp8-p211-flour-decree-citation":
        "The footnote identifies a dated decree, its nine-year term, and its archival location; this is a substantive document and repository claim, not a bare bibliographic pointer.",
    "st-chp8-p211-passerini-and-poligrafo-gargano-genealogical-sources":
        "The note locates Del Rosso genealogical information in named manuscript collections and identifies one manuscript; the underlying records were not independently consulted.",
    "st-chp8-p211-principal-sources-for-del-rosso-collection":
        "Haskell identifies two specific documents as principal sources for the Del Rosso collection; preserve the account and inventory relationships with their dates and publication locator.",
}
FALSE_NOTES = {
    "st-chp8-p211-flour-decree-further-operating-information-cited":
        "This only directs readers to other material for information about the decree's operation; it supplies no discrete operational fact or identified source item.",
    "st-chp8-p211-haskell-acknowledges-paola-zambelli":
        "This is the book author's acknowledgement of research assistance, retained as source context; it is not a relation among the historical actors and objects in the chapter.",
    "st-chp8-p211-haskell-used-florentine-archive-and-manuscript-sources":
        "This is a broad authorial method statement about unspecified source groups, with no discrete relation endpoint; retain it as contextual prose.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded dry-run checks pass")
    args = parser.parse_args()
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a reviewed table, source, PDF, or page image changed; re-review before applying")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines)
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("the p.211 visual transcription changed since review")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 1, 4, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("the S0 segment manifest does not match the reviewed transcription")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("statement identifiers are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {
        row["statement_id"] for row in page_rows
        if "relation_candidate" not in (row.get("qualifiers") or {})
    }
    if len(page_rows) != 8 or unset != set(TRUE_NOTES) | set(FALSE_NOTES):
        raise SystemExit(f"unexpected p.211 note inventory: rows={len(page_rows)}, unset={len(unset)}")

    for statement_id, note in TRUE_NOTES.items():
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        by_id[statement_id]["qualifiers"] = q
    for statement_id, note in FALSE_NOTES.items():
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        by_id[statement_id]["qualifiers"] = q

    updated = jsonl_bytes(statements)
    counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in page_rows)
    print("DRY RUN p.211 footnote visual transcription")
    print(f"segment={SEGMENT_ID} statements={len(page_rows)} classified={len(unset)} true={len(TRUE_NOTES)} false={len(FALSE_NOTES)}")
    print(f"final segment counts: true={counts[True]} false={counts[False]} unset={counts[None]}")
    print(f"file={STATEMENTS.relative_to(ROOT)} before_sha256={EXPECTED_HASHES[STATEMENTS]} after_sha256={sha(updated)}")
    if not args.apply:
        print("No files written. Use --apply to write after reviewing this summary.")
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, updated)
    print(f"APPLIED; recovery copy: {BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
