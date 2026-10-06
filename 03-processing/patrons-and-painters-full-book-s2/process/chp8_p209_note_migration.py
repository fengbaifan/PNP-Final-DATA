"""Controlled S2 migration for p.209 note 1 (composite source line L145)."""
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
NOTE_SEGMENT_ID = SEGMENT_ID
BODY_SEGMENTS = [
    "chp-8:08_CHP-8_sec_i:l62-70",
    "chp-8:08_CHP-8_sec_i:l72-82",
    "chp-8:08_CHP-8_sec_i:l84-96",
    "chp-8:08_CHP-8_sec_i:l98-106",
    "chp-8:08_CHP-8_sec_i:l108-118",
    "chp-8:08_CHP-8_sec_i:l120-124",
]
EXPECTED_MAX_CANDIDATE = 7598
BACKUP_SUFFIX = ".bak-s2-chp8-p209-note-20261001"
EXPECTED_LINE = "1 For all this section see the admirable and fully documented account by Vincenzo Russo. For Russo’s relations with Rembrandt see also Slivc, pp. 59 ff."

RUFFO_AUTHOR = "cand-3474"
RUFFO_PERSON = "cand-2297"
REMBRANDT = "cand-2117"
RUFFO_WORK = "cand-6454"
SLIVE_AUTHOR = "cand-7599"
SLIVE_WORK = "cand-7600"
NEW_CANDIDATES = [
    {
        "candidate_id": SLIVE_AUTHOR,
        "index_entry_id": "",
        "canonical_name": "S. Slive",
        "index_page_range": "",
        "suggested_type": "person",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Author named as Slive in Haskell's p.209 note and as S. Slive in the book bibliography. First name and identity are not expanded here.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L145",
    },
    {
        "candidate_id": SLIVE_WORK,
        "index_entry_id": "",
        "canonical_name": "Rembrandt and his critics 1630-1730 (S. Slive, The Hague, 1953)",
        "index_page_range": "",
        "suggested_type": "archive",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Identified from the book bibliography entry for S. Slive. Haskell cites pp.59 ff. for Ruffo's relations with Rembrandt; cited pages were not independently read.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L145",
    },
]


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
candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}

segment = segments.get(SEGMENT_ID)
if not segment or segment["source_file"] != SOURCE_REL:
    raise SystemExit(f"source segment metadata missing or changed: {SEGMENT_ID}")
if (int(segment["line_start"]), int(segment["line_end"])) != (126, 157):
    raise SystemExit(f"source segment line range changed: {SEGMENT_ID}")
source_path = ROOT / SOURCE_REL
if hashlib.sha256(source_path.read_bytes()).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {SOURCE_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[125:157]
if hashlib.sha256("\n".join(segment_lines).encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {SEGMENT_ID}")
if segment_lines[19] != EXPECTED_LINE:
    raise SystemExit("p.209 note source text changed; re-review before migration")

note_coverage = coverage_by_id.get(NOTE_SEGMENT_ID)
if not note_coverage or (
    note_coverage["disposition"],
    note_coverage["migration_status"],
    note_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L127-144"):
    raise SystemExit(f"unexpected composite-note coverage state: {note_coverage}")
body_coverage = coverage_by_id.get(BODY_SEGMENTS[0])
if not body_coverage or (
    body_coverage["disposition"],
    body_coverage["migration_status"],
    body_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L63-70"):
    raise SystemExit(f"unexpected p.209 body coverage state: {body_coverage}")

bibliography_text = (ROOT / "02-sources/02-Markdown/21_CHP-21Bibliography.md").read_text(encoding="utf-8-sig")
SLIVE_BIB_ENTRY = "Slive, S.: Rembrandt and his critics 1630-1730, The Hague 1953."
if SLIVE_BIB_ENTRY not in bibliography_text:
    raise SystemExit("the cited Slive publication is no longer identifiable from the book bibliography")
if RUFFO_AUTHOR not in candidate_by_id or candidate_by_id[RUFFO_AUTHOR]["canonical_name"] != "V. Ruffo (editor of cited publications; identity unresolved)":
    raise SystemExit("the existing V. Ruffo person candidate changed; review before resolving")
if RUFFO_WORK not in candidate_by_id or candidate_by_id[RUFFO_WORK]["suggested_type"] != "archive":
    raise SystemExit("the existing V. Ruffo publication candidate is absent or has changed type")
if RUFFO_PERSON not in candidate_ids or REMBRANDT not in candidate_ids:
    raise SystemExit("an existing Ruffo/Rembrandt candidate is absent")
if SLIVE_AUTHOR in candidate_ids or SLIVE_WORK in candidate_ids:
    raise SystemExit("a planned Slive candidate ID already exists")
current_max = max(
    int(row["candidate_id"].split("-")[1])
    for row in candidate_rows
    if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()
)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")

body_statement_by_id = {
    row["statement_id"]: row for row in statement_rows if row.get("segment_id") in BODY_SEGMENTS
}
if len(body_statement_by_id) != 115:
    raise SystemExit(f"expected 115 p.209-p.214 body statements, found {len(body_statement_by_id)}")
p209_body_id = "st-chp8-p209-ruffo-born-messina-aristocratic-family"
if p209_body_id not in body_statement_by_id or body_statement_by_id[p209_body_id].get("qualifiers", {}).get("footnote_marker") != 1:
    raise SystemExit("p.209 note 1 body marker changed or is missing")
rembrandt_body_ids = [
    row["statement_id"] for row in body_statement_by_id.values()
    if REMBRANDT in row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
]
expected_rembrandt_ids = {
    "st-chp8-p209-guercino-picture-required-to-match-rembrandt-aristotle",
    "st-chp8-p210-ruffo-bought-three-rembrandt-pictures",
    "st-chp8-p210-rembrandt-reception-in-italy",
    "st-chp8-p210-breughel-reported-rembrandt-reception-1665",
    "st-chp8-p210-ruffo-returned-blind-homer-for-completion",
    "st-chp8-p210-ruffo-admired-rembrandt-despite-reservation",
    "st-chp8-p210-guercino-picture-to-match-rembrandt-aristotle",
    "st-chp8-p210-ruffo-owned-189-rembrandt-prints",
}
if set(rembrandt_body_ids) != expected_rembrandt_ids:
    raise SystemExit(f"unexpected Rembrandt-linked body statements: {sorted(rembrandt_body_ids)}")
if set(row["statement_id"] for row in statement_rows) & {"st-chp8-p209-n1-cite-ruffo", "st-chp8-p209-n1-cite-slive"}:
    raise SystemExit("one or more planned statement IDs already exist")


def offset_for_line(source_line: int) -> int:
    return sum(len(line) + 1 for line in segment_lines[: source_line - 126])


def make_mention(mention_id, surface, candidate_id, note, occurrence=0):
    source_line = segment_lines[19]
    starts = []
    pos = 0
    while True:
        pos = source_line.find(surface, pos)
        if pos < 0:
            break
        starts.append(pos)
        pos += max(1, len(surface))
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface occurrence is absent on L145: {surface!r} #{occurrence}")
    start = offset_for_line(145) + starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"planned mention span does not reproduce source: {surface!r}")
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


segment_text = "\n".join(segment_lines)
new_mentions = [
    make_mention("m-chp8-p209-note-001", "Vincenzo Russo", RUFFO_AUTHOR,
                 "Source OCR reads Russo; the physical page reads Ruffo. Mapped to the in-book V. Ruffo 1916 author candidate."),
    make_mention("m-chp8-p209-note-002", "Russo’s", RUFFO_PERSON,
                 "Source OCR reads Russo’s; the physical page reads Ruffo’s, referring to Don Antonio Ruffo."),
    make_mention("m-chp8-p209-note-003", "Rembrandt", REMBRANDT,
                 "Artist named in the source's pointer to Slive."),
    make_mention("m-chp8-p209-note-004", "Slivc", SLIVE_AUTHOR,
                 "Source OCR reads Slivc; the physical page reads Slive. The cited work is identified from the book bibliography."),
]

all_body_ids = list(body_statement_by_id)
new_statements = [
    {
        "statement_id": "st-chp8-p209-n1-cite-ruffo",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": None,
        "object_candidate_id": RUFFO_WORK,
        "predicate": "footnote_citation",
        "qualifiers": {
            "source_line_start": 145,
            "source_line_end": 145,
            "printed_page": 209,
            "pdf_physical_page": 7,
            "claim": "Haskell directs readers to Vincenzo Ruffo's fully documented account for this section, covering the p.209-p.214 account of Don Antonio Ruffo.",
            "speaker": "Haskell footnote",
            "text_layer": "bibliographic pointer",
            "qualification": "The book bibliography identifies V. Ruffo's 1916 article. Haskell gives no page locator here; the article was not independently read.",
            "mentioned_candidate_ids": [RUFFO_AUTHOR, RUFFO_WORK, RUFFO_PERSON],
            "footnote_marker": 1,
            "linked_body_statement_ids": all_body_ids,
            "footnote_segment": SEGMENT_ID,
            "footnote_body_link_status": "linked",
            "citations": [{"source_candidate_id": RUFFO_WORK}],
            "ocr_corrections": [
                {"source_file": SOURCE_REL, "source_line": 145, "ocr": "Vincenzo Russo", "print": "Vincenzo Ruffo", "basis": "CHP-8.pdf physical page 7."}
            ],
        },
        "original_quote": "For all this section see the admirable and fully documented account by Vincenzo Russo.",
        "origin": "book",
        "source_file": SOURCE_REL,
    },
    {
        "statement_id": "st-chp8-p209-n1-cite-slive",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": None,
        "object_candidate_id": SLIVE_WORK,
        "predicate": "footnote_citation",
        "qualifiers": {
            "source_line_start": 145,
            "source_line_end": 145,
            "printed_page": 209,
            "pdf_physical_page": 7,
            "claim": "Haskell cites Slive, pp.59 ff., for Ruffo's relations with Rembrandt.",
            "speaker": "Haskell footnote",
            "text_layer": "bibliographic pointer",
            "qualification": "The book bibliography identifies S. Slive's 1953 book. The cited pages were not independently read.",
            "mentioned_candidate_ids": [RUFFO_PERSON, REMBRANDT, SLIVE_AUTHOR, SLIVE_WORK],
            "footnote_marker": 1,
            "linked_body_statement_ids": rembrandt_body_ids,
            "footnote_segment": SEGMENT_ID,
            "footnote_body_link_status": "linked",
            "citations": [{"source_candidate_id": SLIVE_WORK, "page": "59 ff."}],
            "ocr_corrections": [
                {"source_file": SOURCE_REL, "source_line": 145, "ocr": "Russo’s", "print": "Ruffo’s", "basis": "CHP-8.pdf physical page 7."},
                {"source_file": SOURCE_REL, "source_line": 145, "ocr": "Slivc", "print": "Slive", "basis": "CHP-8.pdf physical page 7."},
            ],
        },
        "original_quote": "For Russo’s relations with Rembrandt see also Slivc, pp. 59 ff.",
        "origin": "book",
        "source_file": SOURCE_REL,
    },
]

planned_mention_ids = {row["mention_id"] for row in new_mentions}
planned_statement_ids = {row["statement_id"] for row in new_statements}
if len(planned_mention_ids) != len(new_mentions) or mention_ids & planned_mention_ids:
    raise SystemExit("planned mention IDs collide")
if len(planned_statement_ids) != len(new_statements) or statement_ids & planned_statement_ids:
    raise SystemExit("planned statement IDs collide")
available_candidate_ids = candidate_ids | {row["candidate_id"] for row in NEW_CANDIDATES}
for row in new_mentions:
    if row["candidate_id"] not in available_candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
for row in new_statements:
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in available_candidate_ids:
            raise SystemExit(f"statement has unknown candidate: {row['statement_id']} -> {candidate_id}")
    if not set(row["qualifiers"]["linked_body_statement_ids"]) <= set(body_statement_by_id):
        raise SystemExit(f"statement links to missing body statement: {row['statement_id']}")

candidate_new = [dict(row) for row in candidate_rows]
for row in candidate_new:
    if row["candidate_id"] == RUFFO_AUTHOR:
        row["canonical_name"] = "Vincenzo Ruffo"
        row["detail"] = (
            "The p.209 footnote names Vincenzo Ruffo as author of the fully documented account for the section; "
            "the book bibliography lists V. Ruffo's 1916 La galleria Ruffo nel secolo XVII in Messina article. "
            "Keep distinct from Don Antonio Ruffo, the collector discussed in the section. The article was cited, not independently read here."
        )
if len(candidate_new) != len(candidate_rows) or candidate_new == candidate_rows:
    raise SystemExit("existing Ruffo author candidate update was not applied")
candidate_new.extend(NEW_CANDIDATES)

mention_new = mention_rows + new_mentions
statement_new = statement_rows + new_statements
coverage_new = []
for row in coverage_rows:
    copied = dict(row)
    if copied["segment_id"] == NOTE_SEGMENT_ID:
        copied["source_line_ranges"] = "L127-145"
        copied["note"] += " P.209 note 1 (L145) migrated against CHP-8.pdf physical p.7. The first citation points to V. Ruffo's 1916 article for the p.209-p.214 section; the second points to S. Slive's 1953 book, pp.59 ff., for the Ruffo-Rembrandt statements. Both cited sources/pages remain unread here. OCR readings Vincenzo Russo, Russo’s, and Slivc are corrected in S2 only; S0 remains unchanged. L146-L157 remain pending; compare L146-L148 with the p.211 visual transcription before reuse."
    elif copied["segment_id"] == BODY_SEGMENTS[0]:
        copied["migration_status"] = "complete"
        copied["note"] = "P.209 body segment read against CHP-8.pdf physical p.7; footnote 1 in composite line L145 migrated and linked. Representative-collection sentence closes at p.210 L73. OCR and print correction notes remain in S2 qualifiers; S0 remains unchanged."
    coverage_new.append(copied)


def preview():
    print(f"validated segment: {SEGMENT_ID} lines 126-157")
    print("processed source range: L145 (p.209 note 1)")
    print("new candidates: 2 (S. Slive; Rembrandt and his critics 1630-1730)")
    print("existing candidate updated: cand-3474 resolved from V. Ruffo to Vincenzo Ruffo based on print and book bibliography")
    print(f"new mentions: {len(new_mentions)}")
    print(f"new statements: {len(new_statements)} (two citation pointers; no cited pages independently read)")
    print(f"Ruffo account linked to {len(all_body_ids)} body statements; Slive citation linked to {len(rembrandt_body_ids)} Rembrandt-related statements")
    print("p.209 body coverage: reviewed/complete; composite note coverage: reviewed/partial, L127-145")


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
