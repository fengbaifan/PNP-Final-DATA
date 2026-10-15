from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l3-8"
EXPECTED_STATEMENTS_SHA256 = "0ebdf0f84149bd21154d2cac52ecde572f15caadc7eaa247df6f3a0d63ea1b93"
EXPECTED_MENTIONS_SHA256 = "0644450cf12abbb2bc56f06996101c4e443b2ece528fc7349788b99b1b7f04cf"
SEGMENT_SHA256 = "285cf111b70582b26aad5dcec77375d9ceab153d933d11616dc972956d7d45c5"
NEW_STATEMENT_IDS = {
    "st-chp4-sec-ii-l3-8-cassiano-born-in-turin-1588",
    "st-chp4-sec-ii-l3-8-cassiano-educated-partly-in-bologna",
}
CLASSIFICATIONS = {
    "st-chp4-sec-ii-l3-8-cassiano-birth-and-education": {
        "predicate": "born_and_partly_educated",
        "quote": "Though born in\nTurin in 1588 and educated partly in Bologna,",
        "note": "Nonrelation/parent summary: the compound biography is separated into Cassiano's birth in Turin and partial education in Bologna below, with both place endpoints mapped to the existing candidates.",
    },
    "st-chp4-sec-ii-l3-8-cassiano-dominates-private-scene": {
        "predicate": "dominates_private_art_scene_during_papal_reign",
        "quote": "One private collector, however, entirely dominated the scene during the reign of\nUrban VIII and by his taste and intelligence exerted an influence on the arts wholly out of proportion to his income or limited political power.",
        "note": "Nonrelation: this is Haskell's broad evaluative characterization of Cassiano's position and influence across the private collecting scene and the arts; it does not identify a bounded second entity for a discrete edge.",
    },
    "st-chp4-sec-ii-l3-8-cassiano-scientific-investigation": {
        "predicate": "entered_scientific_investigation",
        "quote": "In Rome\n-he made little attempt to gain political preferment, but instead began to move in the intoxicating but risky world of scientific investigation.",
        "note": "Nonrelation: this is an authorial account of Cassiano's intellectual orientation and limited pursuit of political preferment, not a relation to an independently identified person, work, or institution.",
    },
    "st-chp4-sec-ii-l3-8-urban-accession-1623": {
        "predicate": "became_pope",
        "quote": "When Urban became Pope in 1623",
        "note": "Nonrelation: the statement records Urban VIII's office transition and date as biographical chronology; the papal office is not represented as an independent entity endpoint here.",
    },
}
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-secii-l3-8-biography-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve four chapter 4 section II opening residual claims.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    raw = STATEMENTS.read_bytes()
    mentions_raw = MENTIONS.read_bytes()
    if sha256(raw) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("protected statement table changed")
    if sha256(mentions_raw) != EXPECTED_MENTIONS_SHA256:
        raise SystemExit("protected mention table changed")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected S0 segment metadata changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected S0 source segment changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row.get("statement_id") for row in rows
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(CLASSIFICATIONS) or NEW_STATEMENT_IDS.intersection(by_id):
        raise SystemExit(f"protected segment statement set changed: {sorted(unset)}")

    for statement_id, expected in CLASSIFICATIONS.items():
        row = by_id[statement_id]
        if row.get("predicate") != expected["predicate"] or row.get("original_quote") != expected["quote"]:
            raise SystemExit(f"protected statement content changed: {statement_id}")
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = expected["note"]

    expected_mentions = {
        ("cand-2662", "Turin", "423", "428"),
        ("cand-3398", "Bologna", "460", "467"),
    }
    actual_mentions = {
        (row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"])
        for row in csv.DictReader(io.StringIO(mentions_raw.decode("utf-8-sig"), newline=""))
        if row.get("segment_id") == SEGMENT_ID
    }
    if not expected_mentions.issubset(actual_mentions):
        raise SystemExit("protected Turin/Bologna mention mapping changed")

    parent = by_id["st-chp4-sec-ii-l3-8-cassiano-birth-and-education"]
    parent["qualifiers"]["related_statement_ids"] = sorted(NEW_STATEMENT_IDS)
    new_statements = [
        {
            "statement_id": "st-chp4-sec-ii-l3-8-cassiano-born-in-turin-1588",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2036",
            "object_candidate_id": "cand-2662",
            "predicate": "born_in",
            "qualifiers": {
                "source_line_start": 4,
                "source_line_end": 5,
                "claim": "Haskell states that Cassiano was born in Turin in 1588.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "qualification": "The birth year is source-reported; the place endpoint is the named city Turin.",
                "mentioned_candidate_ids": ["cand-2036", "cand-2662"],
                "birth_year": "1588",
                "pdf_physical_page": 5,
                "printed_page_locator": "p.98",
                "relation_candidate": True,
                "relation_candidate_note": "S2 candidate: the source directly states Cassiano's birthplace; no formal S6 edge is created.",
            },
            "original_quote": "Though born in\nTurin in 1588",
            "origin": "book",
            "source_file": segment["source_file"],
        },
        {
            "statement_id": "st-chp4-sec-ii-l3-8-cassiano-educated-partly-in-bologna",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2036",
            "object_candidate_id": "cand-3398",
            "predicate": "educated_in",
            "qualifiers": {
                "source_line_start": 4,
                "source_line_end": 5,
                "claim": "Haskell says Cassiano was educated partly in Bologna.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "qualification": "Preserve partly; the source does not name an institution or give the duration of study in Bologna.",
                "mentioned_candidate_ids": ["cand-2036", "cand-3398"],
                "degree": "partly",
                "pdf_physical_page": 5,
                "printed_page_locator": "p.98",
                "relation_candidate": True,
                "relation_candidate_note": "S2 candidate: the source directly names Bologna as a place of partial education; no formal S6 edge is created.",
            },
            "original_quote": "educated partly in Bologna",
            "origin": "book",
            "source_file": segment["source_file"],
        },
    ]
    insertion_index = rows.index(parent) + 1
    rows[insertion_index:insertion_index] = new_statements
    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered

    print("Chapter 4 section II L3-8 preview:")
    print("birth-and-education parent: false; split into two city-grounded relation candidates")
    print("Cassiano scene assessment, scientific orientation, and Urban VIII accession: false")
    for row in new_statements:
        print(f"statement: {row['statement_id']} {row['subject_candidate_id']} -> {row['object_candidate_id']}")
    print(f"book-statements.jsonl: {sha256(raw)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp4-secii-l3-8")
    temporary.write_bytes(rendered)
    temporary.replace(STATEMENTS)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
