from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii_notes_p73_visual-transcription.md"
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii_notes_p73_visual-transcription:l1-2"
EXPECTED_STATEMENTS_SHA256 = "7cde0dde0abf51a6782efee56a0d671e384d3a837b1be8184bb53e0078031497"
EXPECTED_SOURCE_SHA256 = "3fd65a6cf5f1ea446b9a1348835cc8af706af1fa85c6b16cc9737ddb1a481d5f"
TARGETS = {
    "st-chp3-secii-p73-note3-ibid": {
        "quote": "3 ibid.",
        "line": 1,
        "candidate": "cand-5129",
        "note": "This is a bibliographic locator resolving 'ibid.' to the immediately preceding Biblioteca Corsini manuscript citation; it does not assert a separate historical relation.",
    },
    "st-chp3-secii-p73-note4-passeri": {
        "quote": "4 Passeri, pp. 66-7.",
        "line": 2,
        "candidate": "cand-4376",
        "note": "This is a bibliographic locator for the cited Passeri passage; it preserves the citation and does not independently assert or verify a historical relation.",
    },
}
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp3-secii-p73-residual-citations-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify two residual p.73 footnote citation locators.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    statement_bytes = STATEMENTS.read_bytes()
    source_bytes = SOURCE.read_bytes()
    if sha256(statement_bytes) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("protected statement table changed")
    if sha256(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("protected S0 source changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if source_lines != ["3 ibid.", "4 Passeri, pp. 66-7."]:
        raise SystemExit("protected source lines changed")

    rows = [json.loads(line) for line in statement_bytes.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows) or not set(TARGETS).issubset(by_id):
        raise SystemExit("statement IDs changed or are not unique")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(TARGETS):
        raise SystemExit(f"segment unset statement set changed: {sorted(unset)}")

    for statement_id, expected in TARGETS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers", {})
        if (
            row.get("segment_id") != SEGMENT_ID
            or row.get("predicate") != "footnote_citation"
            or row.get("original_quote") != expected["quote"]
            or qualifiers.get("source_line_start") != expected["line"]
            or qualifiers.get("source_line_end") != expected["line"]
            or qualifiers.get("cited_source_candidate_id") != expected["candidate"]
            or row.get("object_candidate_id") != expected["candidate"]
        ):
            raise SystemExit(f"protected citation evidence changed: {statement_id}")
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = expected["note"]

    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if statement_bytes.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print("Chapter 3 p.73 visual-transcription citation preview:")
    for statement_id in TARGETS:
        print(f"{statement_id}: footnote_citation -> false")
    print(f"book-statements.jsonl: {sha256(statement_bytes)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp3-secii-p73-citations")
    temporary.write_bytes(rendered)
    temporary.replace(STATEMENTS)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
