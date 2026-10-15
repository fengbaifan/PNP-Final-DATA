from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
EXPECTED_STATEMENTS_SHA256 = "8a81eeadf12ead075af6ae624bfbb4a62804ccd0f0e3ed13cc932c30c761cbe7"
SEGMENT_HASHES = {
    "chp-4:04_CHP-4_intro:l10-13": "a11c2ca837f0c82b75b680df1cfe120d564a2326b3d0a3ffd4ef421d5590a513",
    "chp-4:04_CHP-4_sec_i:l3-4": "27dec2bd731dd381940245692b7b42f9676ce892a0e685cf59b15bb7ae99c826",
}
CLASSIFICATIONS = {
    "st-chp4-intro-notes-03-date-reassessment": {
        "segment_id": "chp-4:04_CHP-4_intro:l10-13",
        "predicate": "authorial_date_reassessment",
        "quote": "We can now date the letter much earlier in the century—probably well before 1620.",
        "note": "Nonrelation: this is Haskell's approximate reassessment of the letter's date. The undated letter and the competing chronology remain in the claim and its qualification; time is not modeled here as a separate entity endpoint.",
    },
    "st-chp4-sec-i-l3-4-taste-formation": {
        "segment_id": "chp-4:04_CHP-4_sec_i:l3-4",
        "predicate": "authorial_temporal_characterization",
        "quote": "artistically his taste had been formed during the first twenty years of the century, and now at the age of 59 he made little attempt to change it. It was a taste",
        "note": "Nonrelation: this describes Giustiniani's taste and the author's broad chronology/age characterization; it does not assert a relation to a second identified entity.",
    },
}
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-intro-seci-scalar-claims-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify two chapter 4 scalar authorial claims.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    raw = STATEMENTS.read_bytes()
    if sha256(raw) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("protected statement table changed")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        segment = next((row for row in segment_rows if row.get("segment_id") == segment_id), None)
        if not segment or segment.get("sha256") != expected_hash:
            raise SystemExit(f"protected segment metadata changed: {segment_id}")
        source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
        segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
        if sha256(segment_text.encode("utf-8")) != expected_hash:
            raise SystemExit(f"protected source segment changed: {segment_id}")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows) or not set(CLASSIFICATIONS).issubset(by_id):
        raise SystemExit("statement IDs changed or are not unique")
    for statement_id, expected in CLASSIFICATIONS.items():
        row = by_id[statement_id]
        if (
            row.get("segment_id") != expected["segment_id"]
            or row.get("predicate") != expected["predicate"]
            or row.get("original_quote") != expected["quote"]
            or row.get("qualifiers", {}).get("relation_candidate") is not None
        ):
            raise SystemExit(f"protected statement changed: {statement_id}")
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = expected["note"]

    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print("Chapter 4 scalar claim preview:")
    for statement_id in CLASSIFICATIONS:
        print(f"{statement_id}: nonrelation")
    print(f"book-statements.jsonl: {sha256(raw)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp4-intro-seci-scalar-claims")
    temporary.write_bytes(rendered)
    temporary.replace(STATEMENTS)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
