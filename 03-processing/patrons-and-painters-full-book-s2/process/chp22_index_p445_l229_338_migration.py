#!/usr/bin/env python3
"""Review the two-column index segment on printed p.445."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "B.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l229-338"
SEGMENT_SHA = "7a721bc7b0d263c7f02511d5294e872c0edc528b3fcf68d52f334379c9b2fa8b"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p445-l229-338-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_CSV: "cb75290976d362c68297faf41e30ff1f6fb019219968d14dc083d1117b216120",
    TABLES / "entity-candidates.csv": "a2420e7c81c31c61a5bab62cd8dc66d2bd6d66d628ed9cec77a2d8f12b3693ac",
    TABLES / "s2-coverage.csv": "63452fdc7115fa1e53bcaf9b909423e43268bc16ae5cc036296dd8c2de138cb9",
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
) != (SOURCE_FILE, 229, 338, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[228:338])
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
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l226-227")
previous_page = coverage_by_id.get("chp-22:22_CHP-22Index:l170-224")
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.445 marker/header is not complete")
if not previous_page or (previous_page["disposition"], previous_page["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("preceding p.444 right column is not complete")

index_rows = read_csv(INDEX_CSV, encoding="cp1252")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}

# Index subentries remain navigation under the S1 main headword.
type_by_row = {}
pending = None
for index_row in range(2, 92):
    index_entry_id = f"B.csv#{index_row}"
    source_row = index_rows[index_row]
    candidate = candidate_by_index_id.get(index_entry_id)
    expected_main_entry = source_row["Main Entry"]
    if index_row in (18, 19):
        # B.csv stores Niccolò as UTF-8 bytes misread through cp1252; the page image and S1 candidate retain it correctly.
        if expected_main_entry != "Bambini, NiccolÃ²":
            raise SystemExit(f"unexpected B.csv encoding pre-state: {index_entry_id}")
        expected_main_entry = "Bambini, Niccolò"
    if not candidate or candidate["canonical_name"] != expected_main_entry:
        raise SystemExit(f"S1 candidate/main-entry mapping mismatch: {index_entry_id}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {candidate['candidate_id']}")
    if index_row == 6:
        pending = candidate
        continue
    if 20 <= index_row <= 25:
        expected_type = "term"  # Bamboccianti as a style/artist grouping, not an institution.
    elif index_row == 45:
        expected_type = "family"
    elif index_row in (87, 88):
        expected_type = "place"
    else:
        expected_type = "person"
    type_by_row[index_row] = expected_type

if not pending or (pending["candidate_id"], pending["canonical_name"], pending["status"], pending["suggested_type"]) != (
    "cand-0159", "Baglioni collection", "open", ""
):
    raise SystemExit("Baglioni collection candidate changed")
if len(type_by_row) != 89:
    raise SystemExit("unexpected p.445 typed candidate count")

candidate_updates = []
groups = defaultdict(lambda: {"suggested_type": "", "index_entry_ids": [], "candidate_ids": []})
for index_row, expected_type in sorted(type_by_row.items()):
    index_entry_id = f"B.csv#{index_row}"
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
    group = groups[candidate["canonical_name"]]
    group["suggested_type"] = expected_type
    group["index_entry_ids"].append(index_entry_id)
    group["candidate_ids"].append(candidate["candidate_id"])

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L229-338",
    note=(
        "no_semantic_content: CHP-22Index.pdf physical p.3 visibly prints p.445; L229-338 transcribes both columns "
        "from Bacon, Sir Francis through Barelli, Agostino. Compared against the page image and B.csv#2-91; typed "
        "89 open candidates (80 person, 6 term, 1 family, 2 place) by their S1 headwords. cand-0159 Baglioni collection "
        "remains type-unresolved: the current taxonomy has no collection type, and the index alone does not establish "
        "an organization or place. Subentries and locators are navigation, not assertions or relations. No mentions, "
        "book statements, or relations were added."
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
    "coverage_complete": 622,
    "coverage_queued": 85,
    "coverage_excluded": 125,
    "coverage_partial": 0,
    "open_index_untyped": 2603,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

type_counts = {
    kind: sum(update["suggested_type"] == kind for update in candidate_updates)
    for kind in sorted({update["suggested_type"] for update in candidate_updates})
}
if type_counts != {"family": 1, "person": 80, "place": 2, "term": 6}:
    raise SystemExit(f"unexpected candidate type distribution: {type_counts}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 445,
    "pdf_physical_page": 3,
    "candidate_updates": len(candidate_updates),
    "types": type_counts,
    "candidate_groups": [
        {"main_entry": name, **details, "count": len(details["candidate_ids"])}
        for name, details in sorted(groups.items())
    ],
    "type_pending": {
        "index_entry_id": "B.csv#6",
        "candidate_id": "cand-0159",
        "main_entry": "Baglioni collection",
        "reason": "No collection type in the current taxonomy; index alone does not establish an institution or place.",
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
