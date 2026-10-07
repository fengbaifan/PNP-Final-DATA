#!/usr/bin/env python3
"""Review and classify the right-column index segment on printed p.444."""

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
INDEX_A_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "A.csv"
INDEX_B_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "B.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l170-224"
SEGMENT_SHA = "33466681b2ad88008d510756b85e16f4760a07034658660a5f001e457a1f1ca5"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p444-rcol-l170-224-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_A_CSV: "b44d3ac13df58464fab2aaa1d1fca0a819ab03b1abcc56f466a70d543c4a1133",
    INDEX_B_CSV: "cb75290976d362c68297faf41e30ff1f6fb019219968d14dc083d1117b216120",
    TABLES / "entity-candidates.csv": "84873ffa07e35fb570ddfacc10ace8e34f31893887397efb1a9ff04ec093c2e5",
    TABLES / "s2-coverage.csv": "aae9931ab532751a18a3d731d97bc342ff70d4a1c4f2135d5ecb80eadc298d30",
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
) != (SOURCE_FILE, 170, 224, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[169:224])
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
left_column = coverage_by_id.get("chp-22:22_CHP-22Index:l113-168")
if not left_column or (left_column["disposition"], left_column["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("preceding p.444 left column is not complete")

a_rows = read_csv(INDEX_A_CSV, encoding="cp1252")[1]
b_rows = read_csv(INDEX_B_CSV, encoding="cp1252")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}

# Candidate typing follows the S1 headword, not the navigational sub-entry.
type_by_index_id = {}
for index_row in range(116, 155):
    index_entry_id = f"A.csv#{index_row}"
    expected_type = "term" if 126 <= index_row <= 142 else "person"
    source_row = a_rows[index_row]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate or candidate["canonical_name"] != source_row["Main Entry"]:
        raise SystemExit(f"S1 candidate/main-entry mapping mismatch: {index_entry_id}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {candidate['candidate_id']}")
    type_by_index_id[index_entry_id] = expected_type

baccinelli_id = "B.csv#1"
baccinelli = candidate_by_index_id.get(baccinelli_id)
if (
    not baccinelli
    or b_rows[1]["Main Entry"] != "Baccinelli"
    or b_rows[1]["Sub-entry"] != "Susanna"
    or baccinelli["canonical_name"] != "Baccinelli"
    or baccinelli["sub_entry"] != "Susanna"
    or baccinelli["status"] != "open"
    or baccinelli["suggested_type"]
):
    raise SystemExit("Baccinelli candidate mapping or pre-state changed")
type_by_index_id[baccinelli_id] = "person"

# The index explicitly redirects this alias and S1 already excludes it.
baciccio = candidate_by_index_id.get("B.csv#0")
if (
    not baciccio
    or b_rows[0]["Sub-entry"] != "see under Gaulli, Giovanni Battista"
    or baciccio["status"] != "excluded"
):
    raise SystemExit("Baciccio see-under alias pre-state changed")

if len(type_by_index_id) != 40:
    raise SystemExit("unexpected right-column candidate count")
candidate_updates = []
for index_entry_id, expected_type in type_by_index_id.items():
    candidate = candidate_by_index_id[index_entry_id]
    candidate["suggested_type"] = expected_type
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "main_entry": candidate["canonical_name"],
            "sub_entry": candidate["sub_entry"],
            "suggested_type": expected_type,
        }
    )

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L170-224",
    note=(
        "no_semantic_content: CHP-22Index.pdf physical p.2 visibly prints p.444; this is the right column. "
        "S0 L170-224 runs from Arconato, Galeazzo through Baccinelli/Susanna. Compared against the page image "
        "and A.csv#116-154 plus B.csv#1; typed 40 open candidates (23 person, 17 term) by their S1 headwords. "
        "Subentries and page locators remain index navigation, not separate assertions or relations. "
        "The explicit Baciccio see-under redirect remains the existing excluded alias to Gaulli; no new entity. "
        "No mentions, book statements, or relations were added."
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
    "coverage_complete": 621,
    "coverage_queued": 87,
    "coverage_excluded": 124,
    "coverage_partial": 0,
    "open_index_untyped": 2692,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

type_counts = {
    kind: sum(update["suggested_type"] == kind for update in candidate_updates)
    for kind in sorted({update["suggested_type"] for update in candidate_updates})
}
if type_counts != {"person": 23, "term": 17}:
    raise SystemExit(f"unexpected candidate type distribution: {type_counts}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 444,
    "pdf_physical_page": 2,
    "candidate_updates": len(candidate_updates),
    "types": type_counts,
    "candidate_rows": candidate_updates,
    "coverage_update": {
        key: row[key]
        for key in ("disposition", "migration_status", "source_line_ranges", "note")
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
