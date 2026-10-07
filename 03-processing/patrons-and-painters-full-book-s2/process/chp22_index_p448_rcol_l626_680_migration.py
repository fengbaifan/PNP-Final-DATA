#!/usr/bin/env python3
"""Review the right-column index segment on printed p.448."""

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
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "C.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l626-680"
SEGMENT_SHA = "eda298f0d86f01c327b2f3d18122323c42e67bfa19675d0f9fe1056fd49a4fad"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p448-rcol-l626-680-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_CSV: "7aa977632a7a7cdaff12ea4925a595a89b42cf168314bffde18e0b39c5b45696",
    TABLES / "entity-candidates.csv": "d3bf9c8580d512133f96d411b1738228612b1787b2ee4a2b340ae90f2bc667ff",
    TABLES / "s2-coverage.csv": "f5553f6a4dcb8aab846399a143f93e6f525fc4e6ade38368721eab4a35a43108",
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
) != (SOURCE_FILE, 626, 680, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[625:680])
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
previous_left = coverage_by_id.get("chp-22:22_CHP-22Index:l570-624")
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_left or (previous_left["disposition"], previous_left["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.448 left-column segment is not complete")

index_rows = read_csv(INDEX_CSV, encoding="cp1252")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
pre_existing_work = {
    28: ("cand-0504", "Entry of the Comte de Gergy"),
    29: ("cand-0505", "Entry of the Count of Bolagno"),
}
candidate_updates = []

for index_row in range(44):
    index_entry_id = f"C.csv#{index_row}"
    source_row = index_rows[index_row]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate or candidate["canonical_name"] != source_row["Main Entry"]:
        raise SystemExit(f"S1 candidate/main-entry mapping mismatch: {index_entry_id}")
    if candidate["status"] != "open":
        raise SystemExit(f"unexpected candidate status: {candidate['candidate_id']}")

    if index_row in pre_existing_work:
        expected_id, expected_work = pre_existing_work[index_row]
        if candidate["candidate_id"] != expected_id or candidate["suggested_type"] != "work":
            raise SystemExit(f"pre-existing work candidate changed: {index_entry_id}")
        if expected_work not in candidate["detail"]:
            raise SystemExit(f"pre-existing work evidence changed: {index_entry_id}")
        continue

    if candidate["suggested_type"]:
        raise SystemExit(f"unexpected pre-existing type: {candidate['candidate_id']}")
    candidate["suggested_type"] = "person"
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "main_entry": candidate["canonical_name"],
            "sub_entry": candidate["sub_entry"],
            "suggested_type": "person",
        }
    )

if len(candidate_updates) != 42:
    raise SystemExit(f"unexpected new type assignment count: {len(candidate_updates)}")

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L626-680",
    note=(
        "no_semantic_content: CHP-22Index.pdf physical p.6 visibly prints p.448; L626 is the running header and "
        "L627 includes a scan mark, while the right-column entries map to C.csv#0-43. The page image resolves OCR "
        "noise in Camassei's page locators and Canaletto subentry locators; S0 and C.csv were not rewritten. "
        "Typed 42 previously untyped rows person. cand-0504 and cand-0505 remain work because their p.277 note "
        "evidence is already recorded in candidate details. Subentries and locators remain index navigation; no "
        "mentions, book statements, or relations were added."
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
    "coverage_complete": 628,
    "coverage_queued": 76,
    "coverage_excluded": 128,
    "coverage_partial": 0,
    "open_index_untyped": 2335,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 448,
    "pdf_physical_page": 6,
    "index_rows_reviewed": 44,
    "candidate_type_changes": len(candidate_updates),
    "types": {"person": len(candidate_updates)},
    "pre-existing_work_candidates_retained": ["cand-0504", "cand-0505"],
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
