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
SEGMENT_ID = "chp-4:04_CHP-4_sec_i:l6-18"
EXPECTED_STATEMENTS_SHA256 = "c97eeac6670a7c1fc17a1574f54e41a6242a4b3df82ae34eb25fa588bbc659f7"
SEGMENT_SHA256 = "29c07d307d371be4c1eb8020f7e3d300bffccb38edc2e5d651777501aa58790f"
CLASSIFICATIONS = {
    "st-chp4-sec-i-l6-18-claude-figures": {
        "predicate": "reported_work_description",
        "quote": "The figures in the Claude, formerly in Berlin, are described merely as ‘ninfe’.",
        "note": "Nonrelation/parent description: the specific painting-to-'ninfe' label and the reported Berlin location are recorded in separate atomic statements; this row adds no distinct edge.",
    },
    "st-chp4-sec-i-l6-18-early-commissions": {
        "predicate": "commission_reported",
        "quote": "With great discrimination he commissioned early works by these masters which showed that he retained all his suppleness of taste where his sympathies were engaged.",
        "note": "Nonrelation/parent summary: the commissions to Poussin, Claude, and Testa are recorded in separate atomic statements. This row's broader assessment of Giustiniani's flexibility of taste remains part of the source claim.",
    },
    "st-chp4-sec-i-l6-18-massacre-note": {
        "predicate": "dating_attribution_reported",
        "quote": "Poussin’s Massacre of the Innocents at Chantilly, incidentally the one of his pictures most likely to appeal to an admirer of Caravaggio, probably dates from 1628-9",
        "note": "Nonrelation: this footnote combines a probable date and Haskell's speculative reception assessment about one work. The hypothetical admirer is not a separately identified endpoint; the specific work and its location remain recorded independently.",
    },
    "st-chp4-sec-i-l6-18-new-generation": {
        "predicate": "authorial_taste_assessment",
        "quote": "Now, however, he found himself unable to appreciate the Baroque masters of the new generation. Though he lived until 1637, he showed an interest only in three of the painters who had come to the fore under the aegis of the Barberini: Nicolas Poussin,\nClaude Lorrain and Pietro Testa, all of whom lay outside immediate court circles.",
        "note": "Nonrelation/parent assessment: Giustiniani's relation to the new-generation group and his interest in Poussin, Claude, and Testa are recorded separately. Preserve 'only' and the statement that all three lay outside immediate court circles.",
    },
    "st-chp4-sec-i-l6-18-orsini-title": {
        "predicate": "title_and_inheritance_reported",
        "quote": "Paolo\nGiordano II Orsini, Duke of Bracciano, was the last but one of his family to hold the title which he inherited in 1615 at the age of 24?",
        "note": "Nonrelation: this is a person-level title, succession, and age/date account. Paolo's family membership is recorded separately; the passage does not supply a distinct title entity endpoint.",
    },
    "st-chp4-sec-i-l6-18-rothlisberger-identification": {
        "predicate": "scholarly_identification_reported",
        "quote": "Rothlisberger, 1961, p. 512, suggests that they represent Cephalus and Procris reunited by Diana.",
        "note": "Nonrelation/parent report: the suggested work-to-Cephalus and work-to-Procris identifications are recorded in separate attributed relation candidates. Diana remains in the source claim and its mention mapping; this row does not add another edge.",
    },
}
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-seci-l6-18-composite-assessments-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify six chapter 4 composite or attribute statements after checking their atomic relations.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    raw = STATEMENTS.read_bytes()
    if sha256(raw) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("protected statement table changed")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected S0 segment metadata changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected S0 source segment changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row.get("statement_id") for row in rows
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(CLASSIFICATIONS):
        raise SystemExit(f"protected segment unset set changed: {sorted(unset)}")
    for statement_id, expected in CLASSIFICATIONS.items():
        row = by_id[statement_id]
        if row.get("predicate") != expected["predicate"] or row.get("original_quote") != expected["quote"]:
            raise SystemExit(f"protected statement content changed: {statement_id}")
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = expected["note"]

    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print("Chapter 4 section I L6-18 residual preview:")
    for statement_id in CLASSIFICATIONS:
        print(f"{statement_id}: nonrelation/parent or scalar description")
    print(f"book-statements.jsonl: {sha256(raw)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp4-seci-l6-18-assessments")
    temporary.write_bytes(rendered)
    temporary.replace(STATEMENTS)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
