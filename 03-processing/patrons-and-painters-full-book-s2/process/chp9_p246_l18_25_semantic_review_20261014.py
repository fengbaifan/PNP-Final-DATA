"""Controlled S2 semantic review for Chapter 9, printed page 246.

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
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l18-25"
SOURCE_REL = "02-sources/02-Markdown/09_CHP-9_intro.md"
SOURCE = ROOT / SOURCE_REL
BASE_COMMIT = "c65900801de1cb3af9089345250774161d67f5c9"
BACKUP_SUFFIX = ".bak-s2-chp9-p246-l18-25-semantic-review-20261014"

EXPECTED_SHA256 = {
    "book-statements.jsonl": "0eff6b1b83b457961cf060717adacc91d11a982baae9074946dfed3b8c98b0aa",
    "mentions.csv": "315452b4926a61eb5f6579fa66d7a5a63bdba33fbf9e18a908e451dfa9ed28dc",
    "s2-coverage.csv": "1cf38a90536d458403a63919caffeb3772d6c8aa1f572b64d0946858a54e78d6",
}

TARGET_CLASSIFICATIONS = {
    "st-chp9-p246-betrothal-judgment": True,
    "st-chp9-p246-customs-and-tourism": True,
    "st-chp9-p246-decline-neutrality": True,
    "st-chp9-p246-footnote1-citation-tail": True,
    "st-chp9-p246-morosini-triumphs": True,
    "st-chp9-p246-reforms": False,
    "st-chp9-p246-sciences-qualification": False,
    "st-chp9-p246-status-quo": True,
    "st-chp9-p246-tiepolo-belief": True,
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
    for name, expected in EXPECTED_SHA256.items():
        actual = sha256(TABLES / name)
        if actual != expected:
            raise SystemExit(f"unexpected {name} SHA-256: {actual}")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if head != BASE_COMMIT:
        raise SystemExit(f"versioned mention source changed: expected {BASE_COMMIT}, got {head}")

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
    if not (ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p246_page_review.png").is_file():
        raise SystemExit("p.246 page-review image is missing")

    candidate_fields, candidates = read_csv(candidates_path)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_fields, mentions = read_csv(mentions_path)
    statement_rows = [json.loads(line) for line in statements_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    coverage_fields, coverage_rows = read_csv(coverage_path)
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

    previous = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:04-knowledge/tables/mentions.csv"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8-sig")
    previous_mentions = [
        row for row in csv.DictReader(previous.splitlines()) if row["segment_id"] == SEGMENT_ID
    ]
    if len(previous_mentions) != 36:
        raise SystemExit(f"expected 36 versioned p.246 mentions, found {len(previous_mentions)}")
    current_ids = {row["mention_id"] for row in mentions}
    current_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
    offsets = {}
    offset = 0
    for line_no, line in zip(range(segment["line_start"], segment["line_end"] + 1), segment_lines):
        offsets[line_no] = offset
        offset += len(line) + 1
    restored = []
    for row in previous_mentions:
        if row["mention_id"] in current_ids:
            raise SystemExit(f"mention ID already exists: {row['mention_id']}")
        if row["candidate_id"] not in candidate_ids:
            raise SystemExit(f"mention candidate is missing: {row['mention_id']} -> {row['candidate_id']}")
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_lines and "".join(segment_lines):
            text = "\n".join(segment_lines)
            if text[start:end] != row["surface_form"]:
                raise SystemExit(f"source-span mismatch for {row['mention_id']}")
        span = (SEGMENT_ID, str(start), str(end))
        if span in current_spans:
            raise SystemExit(f"duplicate source span for {row['mention_id']}")
        restored.append(row)
        current_ids.add(row["mention_id"])
        current_spans.add(span)

    for statement_id, value in TARGET_CLASSIFICATIONS.items():
        by_statement[statement_id]["qualifiers"]["relation_candidate"] = value

    betrothal = by_statement["st-chp9-p246-betrothal-judgment"]
    betrothal["original_quote"] = (
        "Indeed it was mainly the tourists who found such ceremonies as The Betrothal of the Sea somewhat ridiculous,"
    )
    betrothal["qualifiers"]["claim"] = (
        "Haskell says tourists mainly found the Betrothal of the Sea ceremony ridiculous."
    )
    betrothal["qualifiers"]["qualification"] = (
        "This is Haskell's generalization about tourists. The separate claim about more thoughtful Venetians beginning to doubt the ceremony is recorded independently; note 2 remains a cited report, not independent verification."
    )
    betrothal["qualifiers"]["mentioned_candidate_ids"] = ["cand-3562", "cand-8122"]

    decline = by_statement["st-chp9-p246-decline-neutrality"]
    decline["original_quote"] = (
        "From then on, though still extraordinarily rich despite her declining trade and though still able to Uve on past capital, "
        "she confessed herself too weak to take any further part in the struggles of Europe. Neutrality was the only hope,"
    )
    decline["qualifiers"]["claim"] = (
        "Haskell says that despite wealth, declining trade, and reliance on past capital, Venice was too weak to join further European struggles and neutrality was the only hope."
    )
    decline["qualifiers"]["qualification"] = (
        "This is Haskell's state-level political interpretation. The survival claim about the great powers' forbearance is recorded separately."
    )
    decline["qualifiers"]["ocr_correction"] = "L22 S0 OCR 'Uve'; CHP-9.pdf physical p.4 reads 'live'."
    decline["qualifiers"]["mentioned_candidate_ids"] = ["cand-8105", "cand-2719", "cand-3462", "cand-8120", "cand-8128"]

    morosini = by_statement["st-chp9-p246-morosini-triumphs"]
    morosini["original_quote"] = (
        "The triumphs of\nFrancesco Morosini in the Peloponnese, celebrated with almost hysterical enthusiasm in 1686, were short-lived."
    )
    morosini["qualifiers"]["claim"] = (
        "Haskell says Francesco Morosini's triumphs in the Peloponnese were celebrated in 1686 but were short-lived."
    )

    citation = by_statement["st-chp9-p246-footnote1-citation-tail"]
    citation["subject_candidate_id"] = "cand-2962"
    citation["object_candidate_id"] = "cand-8126"
    citation["predicate"] = "cites_unresolved_m_silhouette_reference_for_p246_note_1"
    citation["qualifiers"]["claim"] = (
        "Haskell's p.246 note 1 continues a citation to M. S[ilhouette], volume I, page 157."
    )
    citation["qualifiers"]["qualification"] = (
        "The page image shows the prefix 'M.' before S[ilhouette], omitted from S0 L25. The author's identity and full work title remain unresolved; the cited page was not consulted."
    )
    citation["qualifiers"]["ocr_correction"] = "The p.246 note image shows 'M.' before S[ilhouette], omitted from S0 L25; identity remains unresolved."
    citation["qualifiers"]["mentioned_candidate_ids"] = ["cand-2962", "cand-8126"]

    for row in TARGET_CLASSIFICATIONS.values():
        if not isinstance(row, bool):
            raise SystemExit("invalid classification value")

    new_statements = [
        {
            "statement_id": "st-chp9-p246-thoughtful-venetians-doubt-betrothal",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-8125",
            "object_candidate_id": "cand-8122",
            "predicate": "thoughtful_venetians_began_to_doubt_betrothal_ceremony",
            "qualifiers": {
                "source_line_start": 22,
                "source_line_end": 22,
                "printed_page": 246,
                "pdf_physical_page": 4,
                "relation_candidate": True,
                "claim": "Haskell says more thoughtful Venetians were beginning to doubt the Betrothal of the Sea ceremony.",
                "speaker": "Haskell",
                "text_layer": "body",
                "qualification": "The unnamed Venetians are a source-bounded collective; the passage gives no individual names or count.",
                "mentioned_candidate_ids": ["cand-8125", "cand-8122"],
            },
            "original_quote": "though more thoughtful Venetians were also beginning to have doubts.",
            "origin": "book",
            "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp9-p246-survival-great-powers-forbearance",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-8105",
            "object_candidate_id": "cand-8121",
            "predicate": "venice_survival_depended_on_forbearance_of_great_powers",
            "qualifiers": {
                "source_line_start": 22,
                "source_line_end": 22,
                "printed_page": 246,
                "pdf_physical_page": 4,
                "relation_candidate": True,
                "claim": "Haskell says Venice's survival depended more on the great powers' forbearance than on its own ability to resist.",
                "speaker": "Haskell",
                "text_layer": "body",
                "qualification": "The great powers are unnamed; this is Haskell's interpretation, not a specific treaty or guarantee.",
                "mentioned_candidate_ids": ["cand-8105", "cand-8121"],
            },
            "original_quote": "her survival depended more on the forbearance of the great powers than on her own ability to resist them.",
            "origin": "book",
            "source_file": SOURCE_REL,
        },
    ]
    for row in new_statements:
        if row["statement_id"] in by_statement:
            raise SystemExit(f"new statement ID already exists: {row['statement_id']}")
        if row["subject_candidate_id"] not in candidate_ids or row["object_candidate_id"] not in candidate_ids:
            raise SystemExit(f"new statement has a missing candidate: {row['statement_id']}")

    target_coverage = coverage[0]
    target_coverage["note"] += (
        " Semantic review 2026-10-14 classified the 9 pending statements, separated tourist ridicule from Venetian doubts and "
        "great-power forbearance from the neutrality claim, and restored 36 exact source mentions absent from the working table. "
        "The page-image readings 'live' (S0 'Uve') and the omitted citation prefix 'M.' are recorded in S2 only."
    )

    statement_rows.extend(new_statements)
    mentions.extend(restored)
    print(f"target statements classified: {len(TARGET_CLASSIFICATIONS)}/{len(TARGET_CLASSIFICATIONS)}")
    print(f"atomic statements added: {len(new_statements)}")
    print(f"source-anchored mentions restored: {len(restored)}")
    print("source spans, candidates, page image, and statement IDs: passed")
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
    write_jsonl_atomic(statements_path, statement_rows)
    write_csv_atomic(mentions_path, mention_fields, mentions)
    write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
    print("mode: APPLIED")
    print("backups: " + ", ".join(str(path.relative_to(ROOT)) for path in backups))
    for path in paths:
        print(f"{path.name} sha256={sha256(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
