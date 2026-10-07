#!/usr/bin/env python3
"""Classify the right-column index entries on printed p.457."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1651-1703"
SEGMENT_SHA = "1a5a168b7204677d3770c96d3b5b95d6bc32b4244a015c2a6bc78c8d41ca43f0"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p457-right-l1651-1703-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "I.csv": "6b763c9165f2c91a7482778135ffc742b5affc9f83fb8ed887b7b1c773b4ab53",
    INDEX_DIR / "J，K.csv": "977da31c7a4f8d38e4999315dcd76166f21cf30b333e5af47c9a4786a8902518",
    INDEX_DIR / "L.csv": "c32c7a0f784b88625ea5635deaccb0e2734b629e051edacccc6f0d222aa30db1",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "fc8fe8cc976515311cd5e992a83d690c5f1a2c5ef7224e32906d6dd4e28d9a1b",
    TABLES / "s2-coverage.csv": "1d24f1e7a2b171509b6c837a01ebb8b8cdb3993d6e10dc6b96462f19fabd34e4",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

# The physical page image separates this complete right column from the OCR
# fragments in the left-column segment: I.csv#5-10, J，K.csv#0-26, L.csv#0-8.
TYPE_BY_INDEX_ID = {
    "I.csv#5": "term",
    "I.csv#10": "person",
    "J，K.csv#0": "person",
    "J，K.csv#1": "person",
    "J，K.csv#2": "person",
    "J，K.csv#3": "institution",
    "J，K.csv#4": "term",
    "J，K.csv#5": "institution",
    "J，K.csv#6": "institution",
    "J，K.csv#7": "term",
    "J，K.csv#8": "person",
    "J，K.csv#9": "person",
    "J，K.csv#10": "person",
    "J，K.csv#11": "term",
    "J，K.csv#12": "term",
    "J，K.csv#13": "term",
    "J，K.csv#14": "term",
    "J，K.csv#16": "person",
    "J，K.csv#17": "person",
    "J，K.csv#18": "person",
    "J，K.csv#19": "person",
    "J，K.csv#20": "person",
    "J，K.csv#21": "person",
    "J，K.csv#22": "person",
    "J，K.csv#23": "person",
    "J，K.csv#24": "person",
    "J，K.csv#25": "work",
    "J，K.csv#26": "person",
    "L.csv#0": "person",
    "L.csv#1": "person",
    "L.csv#2": "archive",
    "L.csv#3": "person",
    "L.csv#4": "person",
    "L.csv#6": "family",
    "L.csv#7": "person",
    "L.csv#8": "person",
}
PENDING_INDEX_IDS = {"J，K.csv#15", "L.csv#5"}
EXCLUDED_INDEX_IDS = {f"I.csv#{i}" for i in range(6, 10)}
EXPECTED_CANDIDATE_IDS = {
    "I.csv#5": "cand-1314",
    **{f"I.csv#{i}": f"cand-{2911 + i - 6:04d}" for i in range(6, 10)},
    "I.csv#10": "cand-1315",
    **{f"J，K.csv#{i}": f"cand-{1316 + i:04d}" for i in range(27)},
    **{f"L.csv#{i}": f"cand-{1343 + i:04d}" for i in range(9)},
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
segment_text = "\n".join(source_lines[1650:1703])
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
) != (SOURCE_FILE, 1651, 1703, SEGMENT_SHA, ASSET_SHA):
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
previous_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1595-1649")
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1593-1593")
next_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1705-1705")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_left or (previous_left["disposition"], previous_left["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.457 left-column segment is not complete")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.457 page marker is not excluded/complete")
if not next_marker or (next_marker["disposition"], next_marker["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.458 page marker is not queued")

candidate_by_index_id = {}
for candidate in candidates:
    index_id = candidate["index_entry_id"]
    if index_id:
        if index_id in candidate_by_index_id:
            raise SystemExit(f"duplicate S1 index entry ID: {index_id}")
        candidate_by_index_id[index_id] = candidate

expected_index_ids = (
    {f"I.csv#{i}" for i in range(5, 11)}
    | {f"J，K.csv#{i}" for i in range(27)}
    | {f"L.csv#{i}" for i in range(9)}
)
if len(expected_index_ids) != 42 or set(TYPE_BY_INDEX_ID) | PENDING_INDEX_IDS | EXCLUDED_INDEX_IDS != expected_index_ids:
    raise SystemExit("p.457 right-column decisions do not cover exactly its 42 rows")
if (
    set(TYPE_BY_INDEX_ID) & PENDING_INDEX_IDS
    or set(TYPE_BY_INDEX_ID) & EXCLUDED_INDEX_IDS
    or PENDING_INDEX_IDS & EXCLUDED_INDEX_IDS
):
    raise SystemExit("p.457 right-column dispositions overlap")
if {key for key in candidate_by_index_id if key in expected_index_ids} != expected_index_ids:
    raise SystemExit("S1 candidates do not cover exactly the p.457 right-column rows")

candidate_updates = []
type_counts = Counter()
for index_id, suggested_type in TYPE_BY_INDEX_ID.items():
    source_name, row_text = index_id.split("#")
    row_number = int(row_text)
    source_row = read_csv(INDEX_DIR / source_name)[1][row_number]
    candidate = candidate_by_index_id[index_id]
    if candidate["candidate_id"] != EXPECTED_CANDIDATE_IDS[index_id]:
        raise SystemExit(f"unexpected candidate mapping for {index_id}: {candidate['candidate_id']}")
    if candidate["index_source_file"] != source_name:
        raise SystemExit(f"candidate index source mismatch for {index_id}")
    if candidate["canonical_name"] != source_row["Main Entry"]:
        raise SystemExit(f"S1 headword mismatch for {index_id}")
    if candidate["sub_entry"] != source_row["Sub-entry"] or candidate["detail"] != source_row["Detail"]:
        raise SystemExit(f"S1 subentry/detail mismatch for {index_id}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"candidate is not open and untyped: {candidate['candidate_id']}")
    candidate["suggested_type"] = suggested_type
    candidate_updates.append({"index_entry_id": index_id, "candidate_id": candidate["candidate_id"], "suggested_type": suggested_type})
    type_counts[suggested_type] += 1

for index_id, candidate_id in (("J，K.csv#15", "cand-1331"), ("L.csv#5", "cand-1348")):
    pending = candidate_by_index_id[index_id]
    if pending["candidate_id"] != candidate_id or pending["status"] != "open" or pending["suggested_type"]:
        raise SystemExit(f"collection/group without a current entity class must remain pending: {index_id}")
for index_id in EXCLUDED_INDEX_IDS:
    alias = candidate_by_index_id[index_id]
    if alias["candidate_id"] != EXPECTED_CANDIDATE_IDS[index_id] or alias["status"] != "excluded" or not alias["exclude_reason"]:
        raise SystemExit(f"see-under alias must remain excluded: {index_id}")

expected_types = Counter({"person": 23, "institution": 3, "term": 7, "work": 1, "archive": 1, "family": 1})
if len(candidate_updates) != 36 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.457 right-column decisions: types={type_counts}")

target.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1651-1703",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.15 visibly prints p.457. The right column "
        "covers I.csv#5-10, J，K.csv#0-26 and L.csv#0-8; the page image separates it from the left-column entries. "
        "Forty-two index rows contain 38 open candidates: 36 typed as 23 person, 3 institution, 7 term, 1 work, 1 archive "
        "and 1 family; J，K#15 Van Dyck and Rubens paintings in Johann Wilhelm's collection and L#5 Labia collection "
        "stay type-pending because the taxonomy has no collection/group class. I#6-9 Innocent see-under aliases remain "
        "excluded. Jesuits are an institution (including Rome/Venice locator variants); their art characteristics and "
        "hostility-of-Gesuati heading are terms, not formal relations. Johann Wilhelm's named-person, patronage and taste "
        "headings remain person/term context; unspecified grouped holdings do not become invented individual works. "
        "Juvarra's Madrid decorating scheme is a design work; Il Filosofo dell'Alpi is a published ode (archive). Index "
        "locators add no mentions, book statements or relations."
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
    "coverage_complete": 645,
    "coverage_queued": 50,
    "coverage_excluded": 137,
    "coverage_partial": 0,
    "open_index_untyped": 1523,
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
    "pending_type_candidates": ["J，K.csv#15 cand-1331", "L.csv#5 cand-1348"],
    "retained_exclusions": [f"{i} {candidate_by_index_id[i]['candidate_id']}" for i in sorted(EXCLUDED_INDEX_IDS)],
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
