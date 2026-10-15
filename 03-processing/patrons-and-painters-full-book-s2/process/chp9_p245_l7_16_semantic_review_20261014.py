"""Controlled S2 semantic review for Chapter 9, printed page 245.

Default invocation is a read-only dry run. ``--apply`` writes only the reviewed
statement, mention, and coverage rows, preserving recovery copies first.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l7-16"
SOURCE_REL = "02-sources/02-Markdown/09_CHP-9_intro.md"
SOURCE = ROOT / SOURCE_REL
BACKUP_SUFFIX = ".bak-s2-chp9-p245-l7-16-semantic-review-20261014"

EXPECTED_SHA256 = {
    "book-statements.jsonl": "209b53713ab82c2360f27c58e3c227a3a1ff0556d7dc9b58aa86a4956b4307d0",
    "mentions.csv": "d61bc94ae21a4c1b41401fdb11f6cab65ef1c303c674a47b9378e17df6ba579a",
    "s2-coverage.csv": "cddc147845404f58d2d97f693378d017f3001f3dacbc46ccba1b446fd5d9aaf1",
}


MENTION_SPECS = [
    (12, "city", "cand-2719", "The city", "Coreference to Venice.", 0),
    (13, "europe", "cand-3462", "Europe", "Geographic frame of the cosmopolitan comparison.", 0),
    (13, "tourism", "cand-8106", "international tourism", "Concept described as promoted by the government.", 0),
    (13, "government-first", "cand-8105", "government", "Venetian political authority.", 0),
    (13, "government-second", "cand-8105", "government", "Coreference to the Venetian government.", 1),
    (13, "venice-isolation", "cand-2719", "Venice", "City the government sought to isolate.", 0),
    (13, "foreign-influences", "cand-8127", "foreign influences", "Concept distinct from foreign travellers.", 0),
    (13, "enlightenment", "cand-8107", "Enlightenment", "General intellectual term used by Haskell.", 0),
    (13, "foreign-ambassadors", "cand-3562", "Foreign ambassadors", "Unnamed collective; access is described as restricted.", 0),
    (13, "ordinary-travellers", "cand-3562", "ordinary travellers", "Unnamed visitors, sometimes subject to the same restrictions.", 0),
    (13, "nobility-first", "cand-8108", "nobility", "Venetian noble estate.", 0),
    (13, "censorship", "cand-2723", "censorship", "Use the Venice index subentry on censorship.", 0),
    (13, "political-unorthodoxy", "cand-8112", "political unorthodoxy", "Ground for threatened prosecutions.", 0),
    (13, "prosecutions", "cand-8113", "prosecutions", "Threatened response to political unorthodoxy.", 0),
    (13, "travel-law", "cand-8111", "a law", "Travel restriction passed in 1709 and revived in 1783.", 0),
    (14, "patricians", "cand-8109", "patricians", "Social/legal class subject to the stated travel restriction.", 0),
    (14, "council-ten", "cand-8110", "Council of Ten", "Authority whose permission was required.", 0),
    (14, "second-nobility", "cand-8108", "nobility", "Collective social estate described as provincially informed.", 0),
    (14, "french-travellers", "cand-8115", "French travellers", "Unnamed collective whose suggestion Haskell reports.", 0),
    (14, "government-sciences", "cand-8105", "the government", "Venetian political authority.", 0),
    (14, "sciences", "cand-8114", "the sciences", "Field of study in the reported allegation.", 0),
    (15, "measures", "cand-8111", "The measures", "Coreference to the travel restriction's enforcement.", 0),
    (15, "de-brosses", "cand-0455", "de Brosses", "Haskell's cited observer, not independently checked here.", 0),
    (15, "nobles-note", "cand-8108", "nobles", "Venetian noble estate.", 0),
    (15, "foreigners-note", "cand-3562", "foreigners", "Visitors in the report attributed to de Brosses.", 0),
    (15, "law-origin", "cand-8111", "the law", "Travel restriction whose origins are cited.", 0),
    (15, "molmenti", "cand-8116", "Molmenti", "Cited author/reference; title not supplied.", 0),
    (16, "molmenti-year-page", "cand-8116", "1919. P-27", "Continuation of the Molmenti bibliographic citation; OCR punctuation is noisy.", 0),
]

TARGET_CLASSIFICATIONS = {
    "st-chp9-p245-censorship-and-prosecution": True,
    "st-chp9-p245-cosmopolitan-tourism": True,
    "st-chp9-p245-footnote1-measures-and-brosses": True,
    "st-chp9-p245-footnote1-molmenti-reference": True,
    "st-chp9-p245-isolation-policy": True,
    "st-chp9-p245-nobility-and-reform": False,
    "st-chp9-p245-sciences-allegation": True,
    "st-chp9-p245-unresolved-tension": False,
    "st-chp9-p245-visitor-access": True,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_atomic(path: Path, fields, rows) -> None:
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8-sig", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def write_jsonl_atomic(path: Path, rows) -> None:
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the reviewed rows after dry-run checks")
    args = parser.parse_args()

    statements_path = TABLES / "book-statements.jsonl"
    mentions_path = TABLES / "mentions.csv"
    coverage_path = TABLES / "s2-coverage.csv"
    candidates_path = TABLES / "entity-candidates.csv"
    segments_path = TABLES / "segments.jsonl"
    for name in EXPECTED_SHA256:
        path = TABLES / name
        actual = sha256(path)
        if actual != EXPECTED_SHA256[name]:
            raise SystemExit(f"unexpected {name} SHA-256: {actual}")

    segments = [json.loads(line) for line in segments_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row["segment_id"] == SEGMENT_ID), None)
    if not segment or segment["source_file"] != SOURCE_REL:
        raise SystemExit("segment metadata is missing or no longer points to the expected source")
    if sha256(SOURCE) != segment["asset_sha256"]:
        raise SystemExit("source asset hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_lines = source_lines[segment["line_start"] - 1 : segment["line_end"]]
    if hashlib.sha256("\n".join(segment_lines).encode("utf-8")).hexdigest() != segment["sha256"]:
        raise SystemExit("segment text hash changed")

    candidate_fields, candidates = read_csv(candidates_path)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_fields, mentions = read_csv(mentions_path)
    statement_rows = [json.loads(line) for line in statements_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    coverage_fields, coverage_rows = read_csv(coverage_path)
    mention_ids = {row["mention_id"] for row in mentions}
    statement_ids = [row["statement_id"] for row in statement_rows]
    if len(statement_ids) != len(set(statement_ids)):
        raise SystemExit("duplicate statement IDs in current table")
    by_statement = {row["statement_id"]: row for row in statement_rows}
    coverage = [row for row in coverage_rows if row["segment_id"] == SEGMENT_ID]
    if len(coverage) != 1 or (coverage[0]["disposition"], coverage[0]["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected coverage state: {coverage}")

    targets = [by_statement.get(statement_id) for statement_id in TARGET_CLASSIFICATIONS]
    if any(row is None or row["segment_id"] != SEGMENT_ID for row in targets):
        raise SystemExit("one or more expected statements are missing or outside the target segment")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in targets):
        raise SystemExit("one or more target classifications have already changed")
    expected_quotes = {
        "st-chp9-p245-censorship-and-prosecution": "censorship was strict",
        "st-chp9-p245-cosmopolitan-tourism": "international tourism",
        "st-chp9-p245-footnote1-measures-and-brosses": "The measures probably varied",
        "st-chp9-p245-footnote1-molmenti-reference": "Molmenti",
        "st-chp9-p245-isolation-policy": "systematically tried to keep Venice",
        "st-chp9-p245-nobility-and-reform": "provincialism and ignorance",
        "st-chp9-p245-sciences-allegation": "French travellers suggested",
        "st-chp9-p245-unresolved-tension": "tension that was never resolved",
        "st-chp9-p245-visitor-access": "refused contact with the nobility",
    }
    for statement_id, fragment in expected_quotes.items():
        if fragment not in by_statement[statement_id].get("original_quote", ""):
            raise SystemExit(f"unexpected source quote for {statement_id}")

    offsets = {}
    offset = 0
    for line_no, line in zip(range(segment["line_start"], segment["line_end"] + 1), segment_lines):
        offsets[line_no] = offset
        offset += len(line) + 1
    spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
    new_mentions = []
    for line_no, suffix, candidate_id, surface, note, occurrence in MENTION_SPECS:
        mention_id = f"m-chp9-p245-246-{suffix}"
        if mention_id in mention_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        if candidate_id not in candidate_ids:
            raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
        line = source_lines[line_no - 1]
        at = -1
        search_at = 0
        for _ in range(occurrence + 1):
            at = line.find(surface, search_at)
            if at < 0:
                raise SystemExit(f"surface not found at L{line_no}: {surface!r}")
            search_at = at + 1
        start = offsets[line_no] + at
        end = start + len(surface)
        span = (SEGMENT_ID, str(start), str(end))
        if span in spans:
            raise SystemExit(f"duplicate source span for {mention_id}: {span}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })
        mention_ids.add(mention_id)
        spans.add(span)

    for statement_id, value in TARGET_CLASSIFICATIONS.items():
        by_statement[statement_id]["qualifiers"]["relation_candidate"] = value

    by_statement["st-chp9-p245-censorship-and-prosecution"]["subject_candidate_id"] = "cand-8105"
    by_statement["st-chp9-p245-censorship-and-prosecution"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-2723", "cand-8112", "cand-8113", "cand-8105"
    ]

    city_tourism = by_statement["st-chp9-p245-cosmopolitan-tourism"]
    city_tourism["predicate"] = "city_as_cosmopolitan_centre_and_international_tourism_resort"
    city_tourism["original_quote"] = (
        "The city was one of the greatest cosmopolitan centres of\n"
        "Europe, an acknowledged resort of international tourism"
    )
    city_tourism["qualifiers"]["source_line_start"] = 12
    city_tourism["qualifiers"]["claim"] = (
        "Haskell describes Venice as one of Europe's greatest cosmopolitan centres and an acknowledged resort of international tourism."
    )
    city_tourism["qualifiers"]["qualification"] = (
        "The city and the international tourism activity are retained as distinct candidates; the government-promotion clause is split into its own statement."
    )
    city_tourism["qualifiers"]["mentioned_candidate_ids"] = ["cand-2719", "cand-3462", "cand-8106"]

    brosses = by_statement["st-chp9-p245-footnote1-measures-and-brosses"]
    brosses["subject_candidate_id"] = "cand-8108"
    brosses["object_candidate_id"] = "cand-3562"
    brosses["predicate"] = "nobles_rarely_received_foreigners_in_de_brosses_report"
    brosses["original_quote"] = (
        "de Brosses sounds plausible when he says (I, p. 129) that in general nobles very rarely received foreigners."
    )
    brosses["qualifiers"]["source_line_end"] = 15
    brosses["qualifiers"]["claim"] = (
        "Haskell treats de Brosses's report that Venetian nobles generally very rarely received foreigners as plausible."
    )
    brosses["qualifiers"]["qualification"] = (
        "The claim is attributed to de Brosses and endorsed as plausible by Haskell; the cited account was not independently checked."
    )
    brosses["qualifiers"]["mentioned_candidate_ids"] = ["cand-0455", "cand-8108", "cand-3562"]

    molmenti = by_statement["st-chp9-p245-footnote1-molmenti-reference"]
    molmenti["subject_candidate_id"] = "cand-2962"
    molmenti["object_candidate_id"] = "cand-8116"
    molmenti["original_quote"] = "For the origins of the law see Molmenti,\n1919. P-27- -, ,"
    molmenti["qualifiers"]["claim"] = (
        "Haskell's book cites Molmenti (1919, p. 27) for the origins of the law restricting patrician travel."
    )
    molmenti["qualifiers"]["qualification"] = (
        "The page image reads p. 27; Molmenti's cited pages were not independently consulted. This records a citation, not independent confirmation of the law's origin."
    )
    molmenti["qualifiers"]["mentioned_candidate_ids"] = ["cand-2962", "cand-8111", "cand-8116"]

    sciences = by_statement["st-chp9-p245-sciences-allegation"]
    sciences["subject_candidate_id"] = "cand-8105"
    sciences["qualifiers"]["mentioned_candidate_ids"] = ["cand-8115", "cand-8105", "cand-8114"]

    new_statements = [
        {
            "statement_id": "st-chp9-p245-government-promoted-tourism",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-8105",
            "object_candidate_id": "cand-8106",
            "predicate": "promoted_international_tourism_to_venice",
            "qualifiers": {
                "source_line_start": 12,
                "source_line_end": 13,
                "relation_candidate": True,
                "claim": "Haskell says the Venetian government did everything possible to promote international tourism to Venice.",
                "speaker": "Haskell",
                "qualification": "The source describes a governmental effort; it names no particular tourism institution or programme.",
                "mentioned_candidate_ids": ["cand-2719", "cand-8106", "cand-8105"],
            },
            "original_quote": "an acknowledged resort of international tourism which the government did everything possible to promote.",
            "origin": "book",
            "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp9-p245-footnote1-measures-varied",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-8111",
            "object_candidate_id": None,
            "predicate": "measures_varied_in_severity_across_periods",
            "qualifiers": {
                "source_line_start": 15,
                "source_line_end": 15,
                "relation_candidate": False,
                "claim": "Haskell says the measures probably varied in severity at different times.",
                "speaker": "Haskell",
                "qualification": "The footnote does not identify particular enforcement acts or dates; the statement is retained as a source-qualified claim about the measures' implementation.",
                "mentioned_candidate_ids": ["cand-8111"],
            },
            "original_quote": "The measures probably varied in severity at different times",
            "origin": "book",
            "source_file": SOURCE_REL,
        },
    ]
    for row in new_statements:
        if row["statement_id"] in by_statement:
            raise SystemExit(f"new statement ID already exists: {row['statement_id']}")
        if row["subject_candidate_id"] not in candidate_ids or row["object_candidate_id"] not in candidate_ids | {None}:
            raise SystemExit(f"new statement contains a missing candidate: {row['statement_id']}")

    updated_coverage = coverage[0]
    detail = (
        " Semantic review 2026-10-14 classified the 9 pending statements, split the city-tourism and government-promotion claims, "
        "separated the note's policy-variation claim from the de Brosses report, and restored 28 source-anchored mentions absent from the working table."
    )
    if detail.strip() in updated_coverage["note"]:
        raise SystemExit("coverage already records this semantic review")
    updated_coverage["note"] += detail

    statements_after = statement_rows + new_statements
    mentions_after = mentions + new_mentions
    classified = sum((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in targets)
    print(f"target statements classified: {classified}/{len(TARGET_CLASSIFICATIONS)}")
    print(f"atomic statements added: {len(new_statements)}")
    print(f"source-anchored mentions restored: {len(new_mentions)}")
    print("candidate endpoints and source spans: passed")
    print("coverage: remains reviewed/complete; review note extended")
    if not args.apply:
        print("mode: DRY RUN; no files written")
        return 0

    paths = [statements_path, mentions_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery copies already exist; refusing to overwrite")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_jsonl_atomic(statements_path, statements_after)
    write_csv_atomic(mentions_path, mention_fields, mentions_after)
    coverage_rows = [updated_coverage if row["segment_id"] == SEGMENT_ID else row for row in coverage_rows]
    write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
    print("mode: APPLIED")
    print("backups: " + ", ".join(str(path.relative_to(ROOT)) for path in backups))
    for path in paths:
        print(f"{path.name} sha256={sha256(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
