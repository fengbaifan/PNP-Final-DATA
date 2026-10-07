#!/usr/bin/env python3
"""Classify the left-column index entries on printed p.457."""

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
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1595-1649"
SEGMENT_SHA = "0e674aa8a7b0d17380e7f16c54b3377ef7366b059c99b978abd26c449116f031"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p457-left-l1595-1649-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "G.csv": "071ab1e6546d2d01b43e8a83042527e439598af098f8b6a7d49eef3b2234915d",
    INDEX_DIR / "H.csv": "06952633c69becc9e75bce4037bf96eb950d3e2cd3fa4c7d1c4891d45ae736e7",
    INDEX_DIR / "I.csv": "6b763c9165f2c91a7482778135ffc742b5affc9f83fb8ed887b7b1c773b4ab53",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "9bb6be07f327776cfacf87c5c8e809577b527b22f125588f7b8c59f4bf58880b",
    TABLES / "s2-coverage.csv": "b4bfc8aaa6ca9a7c2840d28bd142634ef6574d1fd5a217971af0cbf243235625",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

# This S0 span contains G.csv#177-195, H.csv#0-24 and I.csv#0-4.
# The page image separates the left column from right-column OCR fragments.
TYPE_BY_INDEX_ID = {
    "G.csv#177": "person",  # initial index-context proposal; see the p.178 event correction script
    "G.csv#178": "work",
    "G.csv#179": "work",
    "G.csv#180": "work",
    "G.csv#181": "work",
    "G.csv#182": "work",
    "G.csv#183": "work",
    "G.csv#184": "person",  # work for a patron without a distinct work title
    "G.csv#185": "person",
    "G.csv#186": "archive",  # Guicciardini's Histories
    "G.csv#187": "person",
    "G.csv#188": "work",
    "G.csv#189": "work",
    "G.csv#190": "work",
    "G.csv#191": "person",
    "G.csv#192": "person",
    "G.csv#193": "person",
    "G.csv#194": "person",
    "H.csv#0": "person",
    "H.csv#1": "person",
    "H.csv#2": "person",
    "H.csv#3": "person",
    "H.csv#5": "term",  # general patronage heading
    "H.csv#7": "person",
    "H.csv#8": "person",
    "H.csv#9": "person",
    "H.csv#10": "person",
    "H.csv#11": "person",
    "H.csv#12": "person",
    "H.csv#13": "person",
    "H.csv#14": "person",
    "H.csv#15": "person",
    "H.csv#16": "person",
    "H.csv#17": "person",
    "H.csv#18": "person",
    "H.csv#19": "person",
    "H.csv#20": "person",
    "H.csv#21": "work",
    "H.csv#22": "person",
    "H.csv#23": "work",
    "H.csv#24": "person",
    "I.csv#0": "person",
    "I.csv#1": "term",  # category of books, not a named publication
    "I.csv#2": "archive",  # named publication
    "I.csv#3": "person",
    "I.csv#4": "term",
}
PENDING_INDEX_IDS = {"H.csv#4"}  # collection, with no matching taxonomy class
EXCLUDED_INDEX_IDS = {"G.csv#195", "H.csv#6"}  # see-under aliases

EXPECTED_CANDIDATE_IDS = {
    **{f"G.csv#{i}": f"cand-{1267 + i - 177:04d}" for i in range(177, 195)},
    "G.csv#195": "cand-2909",
    **{f"H.csv#{i}": f"cand-{1285 + i:04d}" for i in range(0, 6)},
    "H.csv#6": "cand-2910",
    **{f"H.csv#{i}": f"cand-{1291 + i - 7:04d}" for i in range(7, 25)},
    **{f"I.csv#{i}": f"cand-{1309 + i:04d}" for i in range(0, 5)},
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1594:1649])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")

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
) != (SOURCE_FILE, 1595, 1649, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")

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
target = coverage_by_id.get(SEGMENT_ID)
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1593-1593")
previous_right = coverage_by_id.get("chp-22:22_CHP-22Index:l1537-1591")
next_right = coverage_by_id.get("chp-22:22_CHP-22Index:l1651-1703")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.457 page marker is not excluded/complete")
if not previous_right or (previous_right["disposition"], previous_right["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.456 right-column segment is not complete")
if not next_right or (next_right["disposition"], next_right["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.457 right-column segment is not queued")

candidate_by_index_id = {}
for candidate in candidates:
    index_id = candidate["index_entry_id"]
    if index_id:
        if index_id in candidate_by_index_id:
            raise SystemExit(f"duplicate S1 index entry ID: {index_id}")
        candidate_by_index_id[index_id] = candidate

expected_index_ids = (
    {f"G.csv#{i}" for i in range(177, 196)}
    | {f"H.csv#{i}" for i in range(0, 25)}
    | {f"I.csv#{i}" for i in range(0, 5)}
)
if len(expected_index_ids) != 49:
    raise SystemExit("p.457 left-column decisions must cover 49 distinct index rows")
if set(TYPE_BY_INDEX_ID) | PENDING_INDEX_IDS | EXCLUDED_INDEX_IDS != expected_index_ids:
    raise SystemExit("p.457 left-column type, pending and exclusion decisions do not match its exact rows")
if (
    set(TYPE_BY_INDEX_ID) & PENDING_INDEX_IDS
    or set(TYPE_BY_INDEX_ID) & EXCLUDED_INDEX_IDS
    or PENDING_INDEX_IDS & EXCLUDED_INDEX_IDS
):
    raise SystemExit("p.457 left-column dispositions overlap")
if {key for key in candidate_by_index_id if key in expected_index_ids} != expected_index_ids:
    raise SystemExit("S1 candidates do not cover exactly the p.457 left-column rows")

candidate_updates = []
type_counts = Counter()
for index_id, suggested_type in TYPE_BY_INDEX_ID.items():
    source_name, row_text = index_id.split("#")
    row_number = int(row_text)
    source_rows = read_csv(INDEX_DIR / source_name)[1]
    source_row = source_rows[row_number]
    candidate = candidate_by_index_id[index_id]
    if candidate["index_source_file"] != source_name:
        raise SystemExit(f"candidate index source mismatch for {index_id}")
    if candidate["candidate_id"] != EXPECTED_CANDIDATE_IDS[index_id]:
        raise SystemExit(f"unexpected candidate mapping for {index_id}: {candidate['candidate_id']}")
    if candidate["canonical_name"] != source_row["Main Entry"]:
        raise SystemExit(f"S1 headword mismatch for {index_id}")
    if candidate["sub_entry"] != source_row["Sub-entry"] or candidate["detail"] != source_row["Detail"]:
        raise SystemExit(f"S1 subentry/detail mismatch for {index_id}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"candidate is not open and untyped: {candidate['candidate_id']}")
    candidate["suggested_type"] = suggested_type
    candidate_updates.append({"index_entry_id": index_id, "candidate_id": candidate["candidate_id"], "suggested_type": suggested_type})
    type_counts[suggested_type] += 1

pending = candidate_by_index_id["H.csv#4"]
if pending["candidate_id"] != EXPECTED_CANDIDATE_IDS["H.csv#4"] or pending["status"] != "open" or pending["suggested_type"]:
    raise SystemExit("H.csv#4 Hapsburg collections must remain open and type-pending")
for alias_id in EXCLUDED_INDEX_IDS:
    alias = candidate_by_index_id[alias_id]
    if alias["candidate_id"] != EXPECTED_CANDIDATE_IDS[alias_id] or alias["status"] != "excluded" or not alias["exclude_reason"]:
        raise SystemExit(f"see-under alias must remain excluded: {alias_id}")

expected_types = Counter({"person": 30, "work": 11, "archive": 2, "term": 3})
if len(candidate_updates) != 46 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.457 left-column decisions: types={type_counts}")

target.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1595-1649",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.15 visibly prints p.457. The left column "
        "covers G.csv#177-195, H.csv#0-24 and I.csv#0-4; the page image separates these from right-column OCR fragments. "
        "Forty-nine index rows contain 47 open candidates: 46 typed as 30 person, 11 work, 2 archive and 3 term; H#4 "
        "Hapsburg collections from Prague stays type-pending because the taxonomy has no collection class, and G#195/H#6 "
        "Guzman/Harley see-under aliases remain excluded. Guercino's refusal of an invitation and work for Ruffo remain "
        "person context; named paintings are works. Guicciardini's Histories and Imago primi saeculi are documents "
        "(archive); the general Hapsburg patronage, book-category and indecency headings are terms. Guidi's drawings, "
        "Fame design and sculptured groups plus Houdon's busts and Huber's engraving are works. Index locators add no "
        "mentions, book statements or relations."
    ),
)

after = {
    "candidate_count": len(candidates),
    "mention_count": len(mentions),
    "statement_count": len(statements),
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
    "open_index_untyped": sum(bool(item["index_entry_id"]) and item["status"] == "open" and not item["suggested_type"] for item in candidates),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 644,
    "coverage_queued": 51,
    "coverage_excluded": 137,
    "coverage_partial": 0,
    "open_index_untyped": 1559,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 457,
    "pdf_physical_page": 15,
    "candidate_update_count": len(candidate_updates),
    "candidate_updates": candidate_updates,
    "pending_type_candidates": ["H.csv#4 cand-1289"],
    "retained_exclusions": ["G.csv#195 cand-2909", "H.csv#6 cand-2910"],
    "type_counts": dict(type_counts),
    **after,
}
if ARGS.apply:
    backups = []
    for path in (candidate_path, coverage_path):
        backup_path = path.with_name(path.name + BACKUP_SUFFIX)
        if backup_path.exists():
            raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup_path.name}")
        backups.append((path, backup_path))
    for path, backup_path in backups:
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for _source, path in backups]

print(json.dumps(result, ensure_ascii=False, indent=2))
