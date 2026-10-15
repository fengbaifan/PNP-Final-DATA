"""Classify p.214 section-II opening statements for S2 relation candidates."""
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p214_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l3-9"
SEGMENT_SHA = "7f6b9c5db0dbec4681c52467cfb5f786815710aea929e957183cd6024fffb1ba"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp8-sec-ii-p214-intro-relation-review-20261014")
EXPECTED_HASHES = {
    STATEMENTS: "ce6681f5b0d676978cea0365d86ced1ef5a1f1cbfd01949abd6a51c7f06df18f",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "f56a895bad78ea0d7bc4c5ac96ce6f9ce3ce33a502a1d9e4039ae0b20a544670",
}

RELATION_NOTES = {
    "st-chp8-sec-ii-intro-roman-variety":
        "This is Haskell's attributed synthesis linking the collections of previously discussed non-Roman patrons to the variety of Roman patronage; individual patrons and works are not enumerated here.",
    "st-chp8-sec-ii-intro-local-centres":
        "The sentence asserts a geographic relation between the previously discussed patrons and centres with active local painting traditions; Don Antonio Ruffo is explicitly excluded, and the remaining endpoints are a source-defined group.",
    "st-chp8-sec-ii-intro-local-artists-backbone":
        "Haskell describes local artists as supplying the main body of most collections, with additions from elsewhere, usually Naples; retain the generalization and its 'most' and 'usually' limits.",
    "st-chp8-sec-ii-intro-outside-commissioning":
        "The statement relates patrons in cities without local schools to commissions from outside their province and a wider choice; the comparative pattern does not identify individual commissions.",
    "st-chp8-sec-ii-intro-collections_in_nonlocal_centres":
        "The claim locates some notable Italian-art collections in cities Haskell characterizes as lacking distinguished native painters; keep the evaluative wording attributed and do not invent named collections.",
    "st-chp8-sec-ii-intro-younger-painters":
        "This preserves Haskell's modal travel scenario and the attributed claim that named younger painters declined to visit or remain in Rome; it does not assert that each painter's works were in every listed city.",
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
    segment_text = "\n".join(source_lines[2:9])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("the p.214 section-II opening segment changed since review")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 3, 9, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("the S0 segment manifest does not match the reviewed source")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("statement identifiers are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {
        row["statement_id"] for row in page_rows
        if "relation_candidate" not in (row.get("qualifiers") or {})
    }
    if len(page_rows) != 6 or unset != set(RELATION_NOTES):
        raise SystemExit(f"unexpected section-II opening inventory: rows={len(page_rows)}, unset={len(unset)}")
    if any(row.get("predicate") == "previously_discussed_patrons_except_ruffo_lived_in_centres_with_local_art_schools"
           for row in page_rows) and not by_id["st-chp8-sec-ii-intro-local-centres"]["qualifiers"].get("ocr_corrections"):
        raise SystemExit("the Russo/Ruffo page-image correction is missing")

    for statement_id, note in RELATION_NOTES.items():
        q = dict(by_id[statement_id].get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        by_id[statement_id]["qualifiers"] = q

    updated = jsonl_bytes(statements)
    counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in page_rows)
    print("DRY RUN p.214 section-II opening")
    print(f"segment={SEGMENT_ID} statements={len(page_rows)} classified={len(unset)} true={len(RELATION_NOTES)} false=0")
    print(f"final segment counts: true={counts[True]} false={counts[False]} unset={counts[None]}")
    print(f"file={STATEMENTS.relative_to(ROOT)} before_sha256={EXPECTED_HASHES[STATEMENTS]} after_sha256={sha(updated)}")
    print("Page image confirms printed Don Antonio Ruffo; S0 OCR reading Russo remains unchanged and correction stays in qualifiers.")
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
