#!/usr/bin/env python3
"""Classify the left-column index candidates on printed p.454."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1253-1307"
SEGMENT_SHA = "c209e928053aaa28a458a8707b555c6fa976e2cddb100c1611dc9c76a25f9591"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p454-left-l1253-1307-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "E.csv": "3ca4a5f8d7acd73e7a9b732a5989d1b9d433a44d872a6150b20bfca95a40dd0e",
    INDEX_DIR / "F.csv": "746710c8b4f91bb2bfc6d4659181e0c954f02be77326ba6be200b11b5b036b44",
    TABLES / "entity-candidates.csv": "de3f3bdf069090fb2216b0dc4db2c4ee47bbe8eb559d1ef84eb9871fec90232a",
    TABLES / "s2-coverage.csv": "0062103cc574361a207eab5dc6a7b14256d99e6b3660bee19981661a282a9a6f",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ID = {
    "E.csv#16": "person",
    "E.csv#17": "person",
    "E.csv#18": "person",
    "E.csv#20": "person",
    "F.csv#0": "person",
    "F.csv#1": "person",
    "F.csv#2": "person",
    "F.csv#3": "person",
    "F.csv#4": "person",
    "F.csv#5": "work",
    "F.csv#6": "work",
    "F.csv#7": "term",
    "F.csv#8": "person",
    "F.csv#9": "person",
    "F.csv#10": "person",
    "F.csv#11": "person",
    "F.csv#12": "person",
    "F.csv#13": "place",
    "F.csv#14": "place",
    "F.csv#15": "person",
    "F.csv#16": "person",
    "F.csv#17": "person",
    "F.csv#18": "person",
    "F.csv#19": "person",
    "F.csv#22": "place",
    "F.csv#23": "place",
    "F.csv#24": "person",
    "F.csv#25": "place",
    "F.csv#26": "person",
    "F.csv#27": "event",
    "F.csv#28": "person",
    "F.csv#30": "person",
    "F.csv#31": "person",
    "F.csv#32": "place",
    "F.csv#33": "place",
    "F.csv#34": "family",
    "F.csv#35": "person",
    "F.csv#36": "person",
    "F.csv#37": "person",
    "F.csv#38": "person",
    "F.csv#39": "work",
    "F.csv#40": "work",
    "F.csv#41": "person",
    "F.csv#42": "person",
    "F.csv#43": "person",
    "F.csv#44": "work",
}
PENDING_INDEX_IDS = {"F.csv#20", "F.csv#21"}
PRETYPED = {"F.csv#29": ("cand-1014", "person")}
EXCLUDED = {"E.csv#19": "cand-2903"}

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
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1252:1307])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")
if source_lines[1250].strip() != "[Page 454]" or "PATRONS" not in source_lines[1252]:
    raise SystemExit("p.454 marker/index heading moved")

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
) != (SOURCE_FILE, 1253, 1307, SEGMENT_SHA, ASSET_SHA):
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
target_coverage = coverage_by_id.get(SEGMENT_ID)
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1251-1251")
next_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1309-1363")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.454 generated page marker is not complete")
if not next_column or (next_column["disposition"], next_column["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.454 right-column segment is not queued")

index_csvs = {
    "E.csv": read_csv(INDEX_DIR / "E.csv")[1],
    "F.csv": read_csv(INDEX_DIR / "F.csv")[1],
}
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
expected_index_ids = {f"E.csv#{n}" for n in range(16, 21)} | {f"F.csv#{n}" for n in range(45)}
if not set(TYPE_BY_INDEX_ID) | PENDING_INDEX_IDS | set(PRETYPED) | set(EXCLUDED) == expected_index_ids:
    raise SystemExit("explicit p.454 left-column decisions do not cover exactly the source entries")
if len(TYPE_BY_INDEX_ID) != 46:
    raise SystemExit(f"expected 46 explicit type decisions, found {len(TYPE_BY_INDEX_ID)}")

candidate_updates = []
retained = {}
pending = []
type_counts = Counter()
for index_entry_id in sorted(expected_index_ids, key=lambda value: (value[0], int(value.split("#")[1]))):
    csv_name, row_number = index_entry_id.split("#")
    row_number = int(row_number)
    source_row = index_csvs[csv_name][row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    if csv_name == "E.csv":
        expected_number = {16: 981, 17: 982, 18: 983, 19: 2903, 20: 984}[row_number]
    else:
        expected_number = 985 + row_number
    expected_candidate_id = f"cand-{expected_number:04d}"
    if candidate["candidate_id"] != expected_candidate_id:
        raise SystemExit(f"unexpected candidate mapping for {index_entry_id}: {candidate['candidate_id']}")
    if candidate["canonical_name"] != source_row["Main Entry"] or candidate["sub_entry"] != source_row["Sub-entry"]:
        raise SystemExit(f"S1 headword/subentry mismatch for {index_entry_id}")

    if index_entry_id in EXCLUDED:
        if candidate["candidate_id"] != EXCLUDED[index_entry_id] or candidate["status"] != "excluded":
            raise SystemExit(f"see-under alias is not preserved as excluded: {index_entry_id}")
        retained[index_entry_id] = {"candidate_id": candidate["candidate_id"], "status": candidate["status"]}
    elif index_entry_id in PRETYPED:
        expected_id, expected_type = PRETYPED[index_entry_id]
        if candidate["candidate_id"] != expected_id or (candidate["status"], candidate["suggested_type"]) != ("open", expected_type):
            raise SystemExit(f"pre-existing candidate classification changed: {index_entry_id}")
        retained[index_entry_id] = {"candidate_id": expected_id, "suggested_type": expected_type}
    elif index_entry_id in PENDING_INDEX_IDS:
        if candidate["status"] != "open" or candidate["suggested_type"]:
            raise SystemExit(f"type-pending collection candidate has unexpected state: {index_entry_id}")
        pending.append({"index_entry_id": index_entry_id, "candidate_id": candidate["candidate_id"], "reason": "taxonomy has no faithful collection type"})
    else:
        suggested_type = TYPE_BY_INDEX_ID[index_entry_id]
        if candidate["status"] != "open" or candidate["suggested_type"]:
            raise SystemExit(f"candidate is not open/untyped: {candidate['candidate_id']}")
        candidate["suggested_type"] = suggested_type
        candidate_updates.append(
            {
                "index_entry_id": index_entry_id,
                "candidate_id": candidate["candidate_id"],
                "canonical_name": candidate["canonical_name"],
                "sub_entry": candidate["sub_entry"],
                "suggested_type": suggested_type,
            }
        )
        type_counts[suggested_type] += 1

expected_types = Counter({"person": 31, "work": 5, "place": 7, "term": 1, "family": 1, "event": 1})
if len(candidate_updates) != 46 or type_counts != expected_types or len(pending) != 2:
    raise SystemExit(f"unexpected p.454 left-column decisions: types={type_counts}; pending={pending}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1253-1307",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.12 visibly prints p.454. S0 L1253-1307 "
        "contains left-column E.csv#16-20 and F.csv#0-44 entries plus OCR fragments from the right column; the full "
        "right-column transcription is separately covered by L1309-1363 and is not double-counted here. Forty-six open "
        "candidates are typed as 31 person, 5 work, 7 place, 1 term, 1 family and 1 event; F#29 cand-1014 remains person, "
        "and E#19 cand-2903 remains an excluded see-under alias. Farsetti's casts and paintings remain type-pending because "
        "the taxonomy has no collection type. The Bentivoglio family, the actual early-nineteenth-century sale of collections, "
        "Ferrerio's Vigilance statue and staircase stucco decoration follow the corresponding book passages. Index locators "
        "add no mentions, book statements or relations."
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
    "coverage_complete": 638,
    "coverage_queued": 60,
    "coverage_excluded": 134,
    "coverage_partial": 0,
    "open_index_untyped": 1834,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 454,
    "pdf_physical_page": 12,
    "candidate_updates": candidate_updates,
    "type_counts": dict(type_counts),
    "pending": pending,
    "retained": retained,
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
