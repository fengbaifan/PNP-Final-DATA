#!/usr/bin/env python3
"""Classify S1 index candidates in the left column of printed p.452."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "C.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1026-1080"
SEGMENT_SHA = "fa268b8d68231d0582638c54310e839be895a8f2e5706f16fb548eb34096c9fa"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p452-l1026-1080-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_CSV: "7aa977632a7a7cdaff12ea4925a595a89b42cf168314bffde18e0b39c5b45696",
    TABLES / "entity-candidates.csv": "9a7d26be14eb6b47a6ec663402719cca268c2657226cd8f529070cc0f2be02b4",
    TABLES / "s2-coverage.csv": "e11ecdf07d000afd0df37157243b1be742a421df963fe7155c867c38630b82bb",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

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


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

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
) != (SOURCE_FILE, 1026, 1080, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[1025:1080])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")
if "452" not in source_lines[1025] or "PATRONS" not in source_lines[1025]:
    raise SystemExit("first source line no longer contains the p.452 running header")

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
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1024-1024")
previous_column = coverage_by_id.get("chp-22:22_CHP-22Index:l913-1022")
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.452 generated page marker is not complete")
if not previous_column or (previous_column["disposition"], previous_column["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.451 index columns are not complete")

index_rows = read_csv(INDEX_CSV, encoding="cp1252")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}

# Index subentries follow their S1 main headword unless S2 evidence identifies a distinct object.
work_rows = {325, 326, 327, 328, 333}
place_rows = {345, 346, 355, 366}
term_rows = {347, 367, 368, 369, 370, 371}
family_rows = {354}
institution_rows = {351}
typed_before = {364: ("cand-0834", "person")}
candidate_updates = []
type_counts = Counter()
retained = {}

for index_row in range(322, 372):
    index_entry_id = f"C.csv#{index_row}"
    source_row = index_rows[index_row]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate or candidate["canonical_name"] != source_row["Main Entry"]:
        raise SystemExit(f"S1 candidate/main-entry mapping mismatch: {index_entry_id}")
    if candidate["status"] != "open":
        raise SystemExit(f"unexpected candidate status: {candidate['candidate_id']}")

    if index_row in typed_before:
        expected_id, expected_type = typed_before[index_row]
        if candidate["candidate_id"] != expected_id or candidate["suggested_type"] != expected_type:
            raise SystemExit(f"pre-existing candidate classification changed: {index_entry_id}")
        retained[index_entry_id] = {"candidate_id": expected_id, "suggested_type": expected_type}
        continue
    if candidate["suggested_type"]:
        raise SystemExit(f"unexpected pre-existing type: {candidate['candidate_id']}")

    if index_row in work_rows:
        suggested_type = "work"
    elif index_row in place_rows:
        suggested_type = "place"
    elif index_row in term_rows:
        suggested_type = "term"
    elif index_row in family_rows:
        suggested_type = "family"
    elif index_row in institution_rows:
        suggested_type = "institution"
    else:
        suggested_type = "person"

    candidate["suggested_type"] = suggested_type
    type_counts[suggested_type] += 1
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "canonical_name": candidate["canonical_name"],
            "sub_entry": candidate["sub_entry"],
            "suggested_type": suggested_type,
        }
    )

expected_types = Counter(
    {"person": 32, "place": 4, "work": 5, "term": 6, "family": 1, "institution": 1}
)
if len(candidate_updates) != 49 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.452 left-column type assignments: {type_counts}")

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1026-1080",
    note=(
        "index-navigation-only: CHP-22Index.pdf physical p.10 visibly prints p.452. S0 L1026 is the page number/running "
        "header; C.csv#322-371 covers the left-column index entries on L1027-1080 (50 rows). Forty-nine open candidates "
        "are typed as 32 person, 4 place, 5 work, 6 term, 1 family, and 1 institution. Codazzi's four titled paintings "
        "(C#325-328) and Coli's Lepanto frescoes (C#333) are work candidates, consistent with existing S2 evidence. "
        "C#347 'Competitions' and C#367-371's generic contract topics are terms; no distinct named event or surviving "
        "contract is asserted by these index headings. C#351 is the named Congregazione institution; C#354 family and "
        "C#355 Contarini villa are kept distinct. Existing C#364 cand-0834 remains person (Stefano Conti); the index "
        "subentry does not replace it with the appendix documents. C#361 remains the person Antonio Conti; the lost "
        "treatise is separately represented by archive candidate cand-9728. Source Markdown, PDF, and C.csv are unchanged. "
        "Index navigation adds no mentions, book statements, or relations."
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
    "open_index_untyped": sum(
        bool(item["index_entry_id"])
        and item["status"] == "open"
        and not item["suggested_type"]
        for item in candidates
    ),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 634,
    "coverage_queued": 66,
    "coverage_excluded": 132,
    "coverage_partial": 0,
    "open_index_untyped": 2016,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 452,
    "pdf_physical_page": 10,
    "index_rows_reviewed": 50,
    "candidate_type_changes": len(candidate_updates),
    "types": dict(type_counts),
    "pre-existing_types_retained": retained,
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
