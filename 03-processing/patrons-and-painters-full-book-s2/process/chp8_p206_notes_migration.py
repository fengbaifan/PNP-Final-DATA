"""Controlled S2 migration for p.206 notes 1-2 in the composite note segment.

Default invocation validates and previews only. --apply writes the S2 tables
with recoverable backups after checking source fingerprints and current coverage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
P206_BODY_ID = "chp-8:08_CHP-8_sec_i:l30-41"
EXPECTED_MAX_CANDIDATE = 7591
BACKUP_SUFFIX = ".bak-s2-chp8-p206-notes-20260930"

BODY_NOTE1_ID = "st-chp8-p206-falcone-painted-battle-scenes-for-roomer"
BODY_NOTE2_ID = "st-chp8-p206-rubens-feast-of-herod-maturity-and-approximate-date"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)

segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}

segment = segments.get(SEGMENT_ID)
if not segment or segment["source_file"] != SOURCE_REL:
    raise SystemExit(f"source segment metadata missing or changed: {SEGMENT_ID}")
if (int(segment["line_start"]), int(segment["line_end"])) != (126, 157):
    raise SystemExit(f"source segment line range changed: {SEGMENT_ID}")

source_path = ROOT / SOURCE_REL
source_bytes = source_path.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {SOURCE_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[125:157]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {SEGMENT_ID}")
if segment_lines[8:10] != [
    "1 For Falcone’s relations with Roomer, see Saxl, p. 80.",
    "2 For the history of this picture, now in the National Gallery of Scotland, see L. Burchard, pp. 383— 387.",
]:
    raise SystemExit("p.206 note source text changed; re-review before migration")

note_coverage = coverage_by_id.get(SEGMENT_ID)
if not note_coverage or (
    note_coverage["disposition"],
    note_coverage["migration_status"],
    note_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L127-133"):
    raise SystemExit(f"unexpected composite-note coverage state: {note_coverage}")
body_coverage = coverage_by_id.get(P206_BODY_ID)
if not body_coverage or (
    body_coverage["disposition"],
    body_coverage["migration_status"],
    body_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L31-41"):
    raise SystemExit(f"unexpected p.206 body coverage state: {body_coverage}")

body_statement_ids = {row["statement_id"] for row in statement_rows if row["segment_id"] == P206_BODY_ID}
if not {BODY_NOTE1_ID, BODY_NOTE2_ID} <= body_statement_ids:
    raise SystemExit("one or more p.206 body statements for notes 1-2 are missing")
for marker, expected_id in [(1, BODY_NOTE1_ID), (2, BODY_NOTE2_ID)]:
    marker_ids = {
        row["statement_id"]
        for row in statement_rows
        if row.get("segment_id") == P206_BODY_ID and row.get("qualifiers", {}).get("footnote_marker") == marker
    }
    if marker_ids != {expected_id}:
        raise SystemExit(f"unexpected p.206 body-link set for footnote {marker}: {sorted(marker_ids)}")

current_max = max(
    int(row["candidate_id"].split("-")[1])
    for row in candidate_rows
    if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()
)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")

EXISTING = {
    "falcone": "cand-0987",
    "roomer": "cand-2223",
    "saxl_person": "cand-6153",
    "saxl_article": "cand-7138",
    "feast_of_herod": "cand-4092",
    "national_gallery_scotland": "cand-3667",
}
if not set(EXISTING.values()) <= candidate_ids:
    raise SystemExit("one or more planned existing candidate IDs are absent")

new_candidate = {
    "candidate_id": "cand-7592",
    "index_entry_id": "",
    "canonical_name": "L. Burchard, ‘Rubens’ “Feast of Herod” at Port Sunlight’ (1953)",
    "index_page_range": "",
    "suggested_type": "archive",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": (
        "The bibliography identifies L. Burchard's 1953 article ‘Rubens’ “Feast of Herod” at Port Sunlight’, "
        "pp.383-387. Haskell cites those pages for the history of the Rubens picture; neither article nor cited pages "
        "were independently read."
    ),
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT_ID}#L135",
}
if new_candidate["candidate_id"] in candidate_ids:
    raise SystemExit("planned candidate ID already exists")
if any(row.get("canonical_name") == new_candidate["canonical_name"] for row in candidate_rows):
    raise SystemExit("Burchard article natural key already exists; reuse or reconcile it")


def line_offset(source_line: int) -> int:
    return sum(len(line) + 1 for line in segment_lines[: source_line - 126])


def make_mention(mention_id: str, source_line: int, surface: str, candidate_key: str, note: str):
    source_text = segment_lines[source_line - 126]
    if source_text.count(surface) != 1:
        raise SystemExit(f"mention surface is absent or ambiguous on L{source_line}: {surface!r}")
    start = line_offset(source_line) + source_text.index(surface)
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": new_candidate["candidate_id"] if candidate_key == "burchard_article" else EXISTING[candidate_key],
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


new_mentions = [
    make_mention("m-chp8-p206-note-001", 134, "Falcone", "falcone", "Painter named in the bibliographic pointer; reuse the p.206 body candidate."),
    make_mention("m-chp8-p206-note-002", 134, "Roomer", "roomer", "Patron named in the bibliographic pointer; the note gives no details of the relations."),
    make_mention("m-chp8-p206-note-003", 134, "Saxl", "saxl_person", "Author named in a short citation; reuse the existing Fritz Saxl candidate."),
    make_mention("m-chp8-p206-note-004", 134, "Saxl, p. 80", "saxl_article", "Bibliographic pointer to the already identified Saxl article, p.80; cited page not read."),
    make_mention("m-chp8-p206-note-005", 135, "this picture", "feast_of_herod", "Anaphoric reference to Rubens’s Feast of Herod described in the p.206 body."),
    make_mention("m-chp8-p206-note-006", 135, "National Gallery of Scotland", "national_gallery_scotland", "Reported present location in Haskell’s note; reuse the existing institution candidate."),
    make_mention("m-chp8-p206-note-007", 135, "L. Burchard, pp. 383— 387", "burchard_article", "Short citation mapped to the bibliography-identified Burchard article; cited pages not read."),
]


def make_citation_statement(statement_id, source_line, body_id, target_candidate, claim, quote, mentioned_ids, page_locator, correction=None):
    qualifiers = {
        "source_line_start": source_line,
        "source_line_end": source_line,
        "printed_page": 206,
        "pdf_physical_page": 4,
        "claim": claim,
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic pointer",
        "qualification": "The cited page range is a locator only; it was not independently read. Do not infer details beyond the note’s wording.",
        "mentioned_candidate_ids": mentioned_ids,
        "footnote_marker": source_line - 133,
        "linked_body_statement_ids": [body_id],
        "footnote_body_link_status": "linked",
        "citations": [{"source_candidate_id": target_candidate, **page_locator}],
    }
    if correction:
        qualifiers["ocr_corrections"] = [correction]
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": None,
        "object_candidate_id": target_candidate,
        "predicate": "footnote_citation",
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


new_statements = [
    make_citation_statement(
        "st-chp8-p206-n1-cite-saxl",
        134,
        BODY_NOTE1_ID,
        EXISTING["saxl_article"],
        "Haskell directs readers to Saxl, p.80, for Falcone’s relations with Roomer.",
        "1 For Falcone’s relations with Roomer, see Saxl, p. 80.",
        [EXISTING[k] for k in ("falcone", "roomer", "saxl_person", "saxl_article")],
        {"page": "80"},
    ),
    make_citation_statement(
        "st-chp8-p206-n2-cite-burchard",
        135,
        BODY_NOTE2_ID,
        new_candidate["candidate_id"],
        "Haskell directs readers to L. Burchard, pp.383–387, for the history of the Rubens picture identified as now in the National Gallery of Scotland.",
        "2 For the history of this picture, now in the National Gallery of Scotland, see L. Burchard, pp. 383— 387.",
        [EXISTING[k] for k in ("feast_of_herod", "national_gallery_scotland")] + [new_candidate["candidate_id"]],
        {"page_start": "383", "page_end": "387"},
        correction={
            "source_file": SOURCE_REL,
            "source_line": 135,
            "ocr": "pp. 383— 387",
            "print": "pp. 383-387",
            "basis": "CHP-8.pdf physical page 4.",
        },
    ),
]

planned_mention_ids = {row["mention_id"] for row in new_mentions}
planned_statement_ids = {row["statement_id"] for row in new_statements}
if len(planned_mention_ids) != len(new_mentions) or mention_ids & planned_mention_ids:
    raise SystemExit("planned mention IDs collide")
if len(planned_statement_ids) != len(new_statements) or statement_ids & planned_statement_ids:
    raise SystemExit("planned statement IDs collide")

all_candidate_ids = candidate_ids | {new_candidate["candidate_id"]}
for row in new_mentions:
    if row["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']}")
for row in new_statements:
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement has unknown candidate: {row['statement_id']} -> {candidate_id}")

candidate_new = candidate_rows + [new_candidate]
mention_new = mention_rows + new_mentions
statement_new = statement_rows + new_statements
coverage_new = []
for row in coverage_rows:
    copied = dict(row)
    if copied["segment_id"] == SEGMENT_ID:
        copied["source_line_ranges"] = "L127-135"
        copied["note"] = (
            "P.204 notes 1-3 (L127-129), p.205 notes 1-4 (L130-133), and p.206 notes 1-2 (L134-135) "
            "read against CHP-8.pdf physical pp.2-4 and migrated. Cited pages remain bibliographic locators, not independent verification. "
            "The 1637 Museo di San Martino Flaying of Marsyas remains distinct from the Roomer-listed 1634 picture; "
            "the Marcotti print is separate from any Ribera painting. The Burchard article is identified from the book bibliography. "
            "OCR corrections are recorded in S2 only. L136-L157 remain pending."
        )
    elif copied["segment_id"] == P206_BODY_ID:
        copied["migration_status"] = "complete"
        copied["note"] = (
            "P.206 body read against CHP-8.pdf physical p.4. Notes 1-2 have been migrated from composite source lines L134-L135 "
            "and linked to the Falcone-Roomer and Rubens Feast of Herod body statements. Saxl and Burchard citations are locators; "
            "cited pages were not independently read."
        )
    coverage_new.append(copied)


def preview():
    print(f"validated segment: {SEGMENT_ID} lines 126-157")
    print("processed source range: L134-135 (p.206 notes 1-2)")
    print("new candidate: cand-7592 (Burchard 1953 article)")
    print(f"new mentions: {len(new_mentions)}")
    print(f"new citation statements: {len(new_statements)}")
    print("p.206 body coverage: reviewed/complete")
    print("composite note coverage: reviewed/partial, L127-135; L136-157 pending")


def apply():
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidate_new)
    write_csv_atomic(mention_path, mention_fields, mention_new)
    write_jsonl_atomic(statement_path, statement_new)
    write_csv_atomic(coverage_path, coverage_fields, coverage_new)
    print("APPLIED; recovery backups retained pending audits:")
    for backup in backups:
        print(backup.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
    args = parser.parse_args()
    preview()
    if args.apply:
        apply()
    else:
        print("DRY RUN: no files written")


if __name__ == "__main__":
    main()
