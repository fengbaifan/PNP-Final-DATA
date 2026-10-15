"""Resolve the remaining Plate 33b caption-space status in S2."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_plate33_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l37-39"
SEGMENT_SHA = "e523de32b06db1322554b38d4db77979f9c5c709672826e587a7224b6aaf0f8a"
EXPECTED_HASHES = {
    TABLE: "12c82b0b26bf362135333b611c4531d9f92cbb9b369db5ac5bffbd3fae2f1b4d",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "2b26ef5bde887a23dc8ce8214fe5f5e4db17af359a9accfddba4ff421e8a7ee0",
}
STATEMENT_ID = "st-chp8-pl33b-space"
BACKUP_SUFFIX = ".bak-s2-chp8-pl33b-space-review-20261014"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a reviewed table, source, PDF, or page image changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[36:39])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA or "b. The gallery of the Palazzo Buonaccorsi, Macerata" not in segment_text:
        raise SystemExit("the reviewed Plate 33b source span changed")
    manifest = [json.loads(line) for line in (ROOT / "04-knowledge" / "tables" / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in manifest if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (segment.get("source_file"), segment.get("line_start"), segment.get("line_end"), segment.get("sha256")) != (SOURCE_REL, 37, 39, SEGMENT_SHA):
        raise SystemExit("segment manifest mismatch")

    raw_lines = raw[TABLE].decode("utf-8-sig").splitlines()
    rows = [json.loads(line) for line in raw_lines if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows) or STATEMENT_ID not in by_id:
        raise SystemExit("statement IDs are missing or duplicated")
    page_rows = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    if len(page_rows) != 6 or sum("relation_candidate" not in row.get("qualifiers", {}) for row in page_rows) != 1:
        raise SystemExit("Plate 33 segment inventory changed")
    row = by_id[STATEMENT_ID]
    if row.get("original_quote") != "b. The gallery of the Palazzo Buonaccorsi, Macerata" or row["qualifiers"].get("relation_candidate") is not None:
        raise SystemExit("the target statement changed since review")
    if "st-chp8-pl33b-palace" not in by_id:
        raise SystemExit("the related gallery-to-palace statement is missing")

    q = dict(row["qualifiers"])
    q["relation_candidate"] = False
    q["relation_candidate_note"] = (
        "This caption statement identifies the named gallery as an architectural space, not a separate entity relation. "
        "The gallery's spatial relation to Palazzo Buonaccorsi is recorded in st-chp8-pl33b-palace."
    )
    q["linked_statement_ids"] = ["st-chp8-pl33b-palace"]
    row["qualifiers"] = q

    output_lines = [
        json.dumps(item, ensure_ascii=False) if item["statement_id"] == STATEMENT_ID else raw_line
        for raw_line, item in zip(raw_lines, rows, strict=True)
    ]
    output = ("\n".join(output_lines) + "\n").encode("utf-8")
    checked = [json.loads(line) for line in output.decode("utf-8").splitlines()]
    checked_page = [item for item in checked if item.get("segment_id") == SEGMENT_ID]
    counts = {True: 0, False: 0, None: 0}
    for item in checked_page:
        value = (item.get("qualifiers") or {}).get("relation_candidate")
        counts[value] = counts.get(value, 0) + 1
    if counts != {True: 5, False: 1, None: 0}:
        raise SystemExit(f"serialized Plate 33 status check failed: {counts}")

    print("DRY RUN Plate 33b caption")
    print(f"segment={SEGMENT_ID} statements=6 true={counts[True]} false={counts[False]} unset={counts[None]}")
    print("resolution: architectural-space description is non-relational; the gallery-to-palace relation remains linked separately")
    print(f"book-statements before={sha(raw[TABLE])} after={sha(output)}")
    if not args.apply:
        print("No files written. Use --apply after reviewing the result.")
        return

    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("recovery backup already exists")
    shutil.copy2(TABLE, backup)
    with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False, suffix=".tmp") as stream:
        stream.write(output)
        temporary = Path(stream.name)
    temporary.replace(TABLE)
    print(f"APPLIED; recovery copy: {backup.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
