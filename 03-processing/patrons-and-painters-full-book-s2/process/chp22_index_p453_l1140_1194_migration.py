#!/usr/bin/env python3
"""Classify the left-column index candidates on printed p.453."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1140-1194"
SEGMENT_SHA = "7695adbbc21828cbbe663bd402f2217554a08cfee5bc7b22e3b9931fe8141266"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p453-left-l1140-1194-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "C.csv": "7aa977632a7a7cdaff12ea4925a595a89b42cf168314bffde18e0b39c5b45696",
    INDEX_DIR / "D.csv": "54be09948205d0cf43663d0d7ddb055a97102f139547387b195c6ed81f55815a",
    TABLES / "entity-candidates.csv": "93f7c5431727139a3872ee4c8ec4c093e334298e66ac1b215489e51f4fb2189c",
    TABLES / "s2-coverage.csv": "3e88e4cf092c37663f5baf59c6f54e1ac2b7b9cdefde92d60f00011600efd95d",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ID = {
    "C.csv#421": "work",
    "C.csv#422": "person",
    "C.csv#423": "person",
    "C.csv#424": "work",
    "C.csv#425": "person",
    "C.csv#426": "term",
    "C.csv#427": "person",
    "C.csv#428": "person",
    "C.csv#429": "person",
    "C.csv#430": "person",
    "C.csv#431": "procedure",
    "D.csv#0": "person",
    "D.csv#1": "person",
    "D.csv#2": "person",
    "D.csv#3": "archive",
    "D.csv#4": "person",
    "D.csv#5": "work",
    "D.csv#6": "person",
    "D.csv#7": "person",
    "D.csv#8": "person",
    "D.csv#9": "person",
    "D.csv#10": "place",
    "D.csv#11": "person",
    "D.csv#12": "work",
    "D.csv#13": "place",
    "D.csv#14": "work",
    "D.csv#15": "work",
    "D.csv#16": "person",
    "D.csv#17": "person",
    "D.csv#18": "person",
    "D.csv#19": "person",
    "D.csv#20": "person",
    "D.csv#21": "person",
    "D.csv#22": "person",
    "D.csv#23": "person",
    "D.csv#24": "person",
    "D.csv#25": "person",
    "D.csv#26": "work",
    "D.csv#27": "person",
    "D.csv#28": "person",
    "D.csv#29": "person",
    "D.csv#30": "person",
    "D.csv#31": "person",
    "D.csv#32": "family",
    "D.csv#33": "family",
    "D.csv#34": "person",
    "D.csv#35": "person",
    "D.csv#36": "person",
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
segment_text = "\n".join(source_lines[1139:1194])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")
if "[Page 453]" not in source_lines[1137] or "INDEX" not in source_lines[1139]:
    raise SystemExit("p.453 marker/index heading moved")

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
) != (SOURCE_FILE, 1140, 1194, SEGMENT_SHA, ASSET_SHA):
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
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1138-1138")
next_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1196-1249")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.453 generated page marker is not complete")
if not next_column or (next_column["disposition"], next_column["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.453 right-column segment is not queued")

index_csvs = {
    "C.csv": read_csv(INDEX_DIR / "C.csv", encoding="cp1252")[1],
    "D.csv": read_csv(INDEX_DIR / "D.csv", encoding="cp1252")[1],
}
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
if len(TYPE_BY_INDEX_ID) != 48:
    raise SystemExit(f"expected 48 explicit index decisions, found {len(TYPE_BY_INDEX_ID)}")

candidate_updates = []
type_counts = Counter()
for index_entry_id, suggested_type in TYPE_BY_INDEX_ID.items():
    csv_name, row_number = index_entry_id.split("#")
    row_number = int(row_number)
    source_row = index_csvs[csv_name][row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    expected_candidate_number = (887 + row_number - 421) if csv_name == "C.csv" else (898 + row_number)
    expected_candidate_id = f"cand-{expected_candidate_number:04d}"
    if candidate["candidate_id"] != expected_candidate_id:
        raise SystemExit(f"unexpected candidate mapping for {index_entry_id}: {candidate['candidate_id']}")
    if candidate["canonical_name"] != source_row["Main Entry"]:
        raise SystemExit(f"S1 headword mismatch for {index_entry_id}: {candidate['canonical_name']}")
    if candidate["sub_entry"] != source_row["Sub-entry"]:
        raise SystemExit(f"S1 subentry mismatch for {index_entry_id}: {candidate['sub_entry']}")
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

expected_types = Counter(
    {"person": 34, "work": 7, "term": 1, "procedure": 1, "archive": 1, "place": 2, "family": 2}
)
if len(candidate_updates) != 48 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.453 left-column type assignments: {type_counts}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1140-1194",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.11 visibly prints p.453. S0 L1140-1194 "
        "contains left-column C.csv#421-431 and D.csv#0-36 entries plus OCR fragments from the right column; the full "
        "right-column transcription is separately covered by L1196-1249 and is not double-counted here. The 48 left-column "
        "candidates are typed as 34 person, 7 work, 1 term, 1 procedure, 1 archive, 2 place and 2 family. C#422 and C#425 "
        "remain their Crespi/Creti person headwords despite generic 'work for' subentries; C#426 is a generic term and "
        "C#431 a fiscal procedure. D#3 'Daphnis and Chloe' is the literary source (archive), distinct from indexed visual "
        "works; D#5 'Apotheosis of Aeneas' is a work. D#9 remains Daun person under an explanatory subentry, D#10 is the "
        "Vienna palace (place), and D#13 names S. Maria Maggiore, Bergamo (place). Index locators do not assert book facts; "
        "no mentions, book statements or relations are added."
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
    "coverage_complete": 636,
    "coverage_queued": 63,
    "coverage_excluded": 133,
    "coverage_partial": 0,
    "open_index_untyped": 1925,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 453,
    "pdf_physical_page": 11,
    "candidate_updates": candidate_updates,
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
