#!/usr/bin/env python3
"""Review the left-column OCR segment of printed index p.444."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "A.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l113-168"
SEGMENT_SHA = "0413db327fa2c0f600fdddba0613d49b0ee421d317624a4e3f52aa05aff91431"
INDEX_MD_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
INDEX_PDF_SHA = "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5"
INDEX_CSV_SHA = "b44d3ac13df58464fab2aaa1d1fca0a819ab03b1abcc56f466a70d543c4a1133"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p444-l113-168-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path, encoding="utf-8-sig"):
    with path.open(encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected, label in (
    (INDEX_MD, INDEX_MD_SHA, "index Markdown"),
    (INDEX_PDF, INDEX_PDF_SHA, "index PDF"),
    (INDEX_CSV, INDEX_CSV_SHA, "A.csv"),
):
    if sha256(path) != expected:
        raise SystemExit(f"{label} changed")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
segment = manifest.get(SEGMENT_ID)
if not segment or (
    segment.get("source_file"),
    segment.get("line_start"),
    segment.get("line_end"),
    segment.get("sha256"),
    segment.get("asset_sha256"),
) != (SOURCE_FILE, 113, 168, SEGMENT_SHA, INDEX_MD_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[112:168])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(mentions), len(statements)) != (11436, 832, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

coverage_by_id = {row["segment_id"]: row for row in coverage}
row = coverage_by_id.get(SEGMENT_ID)
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
continued = coverage_by_id.get("chp-22:22_CHP-22Index:l64-109")
if not continued or (continued["disposition"], continued["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("preceding p.443 continuation is not complete")

index_rows = read_csv(INDEX_CSV, encoding="cp1252")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
type_by_row = {}
for i in range(67, 87):
    type_by_row[i] = "person"
type_by_row[87] = "place"  # Alticchiero is a villa/building place.
for i in range(88, 91):
    type_by_row[i] = "person"
type_by_row[91] = "place"  # Altieri palace is a building place.
for i in range(92, 112):
    type_by_row[i] = "person"
type_by_row[112] = "term"  # A time-bounded literary-political phenomenon, not a discrete event.
type_by_row[113] = "person"
type_by_row[114] = "person"
type_by_row[115] = "institution"  # Arcadia is a named literary society.
if len(type_by_row) != 49:
    raise SystemExit("unexpected p.444 left-column candidate count")

candidate_updates = []
for row_number, expected_type in sorted(type_by_row.items()):
    index_entry_id = f"A.csv#{row_number}"
    candidate = candidate_by_index_id.get(index_entry_id)
    index_row = index_rows[row_number]
    if not candidate or candidate["canonical_name"] != index_row["Main Entry"]:
        raise SystemExit(f"S1 candidate/main-entry mapping mismatch: {index_entry_id}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {candidate['candidate_id']}")
    candidate["suggested_type"] = expected_type
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "main_entry": candidate["canonical_name"],
            "sub_entry": candidate["sub_entry"],
            "detail": candidate["detail"],
            "suggested_type": expected_type,
        }
    )

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L113-168",
    note=(
        "no_semantic_content: CHP-22Index.pdf physical p.2 visibly prints p.444. S0 L113-114 are the page heading/folio; "
        "L115-168 transcribe the left column from Algarotti, Francesco—continued through Arcadia, Society of. Compared "
        "against the page image and A.csv#67-115; typed 49 open index candidates (45 person, 2 place, 1 term, 1 "
        "institution). Subentries remain navigation under their main index heading. The index locators do not assert "
        "book facts; no mentions, book statements, or relations were added."
    ),
)

after = {
    "candidate_count": len(candidates),
    "mention_count": len(mentions),
    "statement_count": len(statements),
    "coverage_complete": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "complete"
        for item in coverage
    ),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "partial"
        for item in coverage
    ),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 620,
    "coverage_queued": 89,
    "coverage_excluded": 123,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 444,
    "candidate_updates": len(candidate_updates),
    "types": {
        kind: sum(update["suggested_type"] == kind for update in candidate_updates)
        for kind in sorted({update["suggested_type"] for update in candidate_updates})
    },
    "new_candidates": 0,
    "new_mentions": 0,
    "new_book_statements": 0,
    **after,
}
if ARGS.apply:
    table_paths = (candidate_path, coverage_path)
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in table_paths]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a migration backup already exists; refusing to overwrite it")
    for path, backup in zip(table_paths, backup_paths):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

print(json.dumps(result, ensure_ascii=False, indent=2))
