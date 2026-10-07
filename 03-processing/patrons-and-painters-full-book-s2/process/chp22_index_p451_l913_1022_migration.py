#!/usr/bin/env python3
"""Classify S1 index candidates from both columns of printed p.451."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l913-1022"
SEGMENT_SHA = "118667f1927b47bf0217c2e27c292cf1a6d0c3e608888f6f60772da1d693f3c6"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p451-l913-1022-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_CSV: "7aa977632a7a7cdaff12ea4925a595a89b42cf168314bffde18e0b39c5b45696",
    TABLES / "entity-candidates.csv": "5a18b89bf695cc0d45919671025fa482d98c7f36d1e5626b872e2123ce33f205",
    TABLES / "s2-coverage.csv": "f8d68d60e68772a877f3d81db1ca3493ce888937e4672e9699757c5e0044bf1a",
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
) != (SOURCE_FILE, 913, 1022, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[912:1022])
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
previous_segment = coverage_by_id.get("chp-22:22_CHP-22Index:l910-911")
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_segment or (
    previous_segment["disposition"], previous_segment["migration_status"]
) != ("excluded", "complete"):
    raise SystemExit("p.451 generated marker/header segment is not complete")

index_rows = read_csv(INDEX_CSV, encoding="cp1252")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}

# Index subentries follow their S1 main headword unless S2 evidence identifies a distinct object.
work_rows = {
    238, 239, 240, 241, 274, 275, 276, 277, 281, 296, 297,
    *range(299, 306), 307, 309, 310, 311,
}
place_rows = (set(range(227, 268)) - {238, 239, 240, 241}) | {270, 273, 298, 308, 320}
source_main_entry_overrides = {
    290: "Città di Castello, Matteo da",
    313: "Clément, Abbé",
}
candidate_name_before_overrides = {313: "Clement, Abbé"}
excluded_before = {314: "cand-2893", 315: "cand-2894", 316: "cand-2895", 317: "cand-2896", 318: "cand-2897", 319: "cand-2898"}
candidate_updates = []
name_corrections = []
type_counts = Counter()

for index_row in range(227, 322):
    index_entry_id = f"C.csv#{index_row}"
    source_row = index_rows[index_row]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")

    expected_main_entry = source_main_entry_overrides.get(index_row, source_row["Main Entry"])
    expected_before_name = candidate_name_before_overrides.get(index_row, expected_main_entry)
    if candidate["canonical_name"] != expected_before_name:
        raise SystemExit(f"S1 candidate/main-entry mismatch: {index_entry_id}")

    if index_row in excluded_before:
        if candidate["candidate_id"] != excluded_before[index_row] or candidate["status"] != "excluded":
            raise SystemExit(f"pre-existing see-under exclusion changed: {index_entry_id}")
        continue

    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"unexpected candidate status/type: {candidate['candidate_id']}")

    suggested_type = (
        "work" if index_row in work_rows else "place" if index_row in place_rows else "person"
    )
    candidate["suggested_type"] = suggested_type
    type_counts[suggested_type] += 1
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "suggested_type": suggested_type,
        }
    )

    if index_row in source_main_entry_overrides:
        old_name = candidate["canonical_name"]
        candidate["canonical_name"] = source_main_entry_overrides[index_row]
        if old_name != candidate["canonical_name"]:
            name_corrections.append(
                {
                    "index_entry_id": index_entry_id,
                    "candidate_id": candidate["candidate_id"],
                    "previous_name": old_name,
                    "printed_name": source_main_entry_overrides[index_row],
                    "source_csv_main_entry": source_row["Main Entry"],
                }
            )

if len(candidate_updates) != 89 or type_counts != Counter({"person": 25, "place": 42, "work": 22}):
    raise SystemExit(f"unexpected p.451 type assignments: {type_counts}")

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L913-1022",
    note=(
        "index-navigation-only: CHP-22Index.pdf physical p.9 visibly prints p.451; L913-1022 covers both columns and "
        "C.csv#227-321 (95 rows). Six existing see-under aliases C#314-319 remain excluded; 89 open candidates are "
        "typed as 25 person, 42 place, and 22 work. Church/building subentries are places except the distinct St Peter's "
        "internal works at C#238-241. Cignani's Bacchanal (C#274), Forli cupola painting (C#275; 08_CHP-8_sec_ii.md "
        "L102 and existing S2 work mapping), Jupiter giving Suck and St John the Baptist (C#276-277; "
        "10_CHP-10_intro.md L522), and Cigoli's Deposition (C#281; 08_CHP-8_sec_ii.md L248) are works. "
        "Clément, Abbé is corrected from the S1 transcription to match the printed accent; Città di Castello is likewise "
        "verified against print. Source Markdown, PDF, and C.csv are unchanged. Index navigation adds no mentions, book "
        "statements, or relations."
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
    "coverage_complete": 633,
    "coverage_queued": 68,
    "coverage_excluded": 131,
    "coverage_partial": 0,
    "open_index_untyped": 2065,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 451,
    "pdf_physical_page": 9,
    "index_rows_reviewed": 95,
    "candidate_type_changes": len(candidate_updates),
    "types": dict(type_counts),
    "pre-existing_exclusions_retained": excluded_before,
    "name_corrections": name_corrections,
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
