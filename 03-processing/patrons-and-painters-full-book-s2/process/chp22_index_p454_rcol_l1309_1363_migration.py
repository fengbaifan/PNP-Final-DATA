#!/usr/bin/env python3
"""Classify the right-column index candidates on printed p.454."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1309-1363"
SEGMENT_SHA = "bcbf7d4bcbfc9e7df0a5ac703afbdec7ee1c3fb21951d2fa7664d7e545bcb84f"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p454-right-l1309-1363-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "F.csv": "746710c8b4f91bb2bfc6d4659181e0c954f02be77326ba6be200b11b5b036b44",
    TABLES / "entity-candidates.csv": "647b3b7828e6942868691691e6940b8158959b23e4604365a27e05f5ac33a1da",
    TABLES / "s2-coverage.csv": "22db7672f3b667d6b86f62994839dd5eade8c2c48591ce81f19e9a04b6e22435",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ID = {
    "F.csv#45": "person",
    "F.csv#46": "person",
    "F.csv#47": "person",
    "F.csv#48": "person",
    "F.csv#49": "person",
    "F.csv#50": "person",
    "F.csv#51": "person",
    "F.csv#52": "person",
    "F.csv#53": "person",
    "F.csv#54": "person",
    "F.csv#55": "term",
    "F.csv#56": "place",
    "F.csv#57": "place",
    "F.csv#58": "person",
    "F.csv#59": "person",
    "F.csv#60": "person",
    "F.csv#61": "person",
    "F.csv#62": "person",
    "F.csv#63": "work",
    "F.csv#64": "work",
    "F.csv#65": "person",
    "F.csv#66": "archive",
    "F.csv#67": "person",
    "F.csv#70": "person",
    "F.csv#71": "person",
    "F.csv#73": "family",
    "F.csv#75": "person",
    "F.csv#76": "place",
    "F.csv#77": "person",
    "F.csv#78": "person",
    "F.csv#79": "person",
    "F.csv#80": "work",
    "F.csv#81": "person",
    "F.csv#82": "work",
    "F.csv#83": "work",
    "F.csv#84": "person",
    "F.csv#86": "work",
    "F.csv#87": "work",
    "F.csv#88": "work",
    "F.csv#89": "person",
    "F.csv#90": "person",
    "F.csv#91": "person",
    "F.csv#92": "person",
}
PENDING_INDEX_IDS = {"F.csv#69"}
PRETYPED = {
    "F.csv#68": ("cand-1053", "person"),
    "F.csv#72": ("cand-1057", "family"),
    "F.csv#74": ("cand-1059", "place"),
    "F.csv#85": ("cand-1070", "person"),
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
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1308:1363])
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
) != (SOURCE_FILE, 1309, 1363, SEGMENT_SHA, ASSET_SHA):
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
previous_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1253-1307")
next_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1365-1366")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_column or (previous_column["disposition"], previous_column["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.454 left column is not complete")
if not next_marker or (next_marker["disposition"], next_marker["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.455 generated page marker is not queued")

index_rows = read_csv(INDEX_DIR / "F.csv")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
expected_index_ids = {f"F.csv#{n}" for n in range(45, 93)}
if set(TYPE_BY_INDEX_ID) | PENDING_INDEX_IDS | set(PRETYPED) != expected_index_ids:
    raise SystemExit("explicit p.454 right-column decisions do not cover exactly the source entries")
if len(TYPE_BY_INDEX_ID) != 43:
    raise SystemExit(f"expected 43 explicit type decisions, found {len(TYPE_BY_INDEX_ID)}")

candidate_updates = []
retained = {}
pending = []
type_counts = Counter()
for index_entry_id in sorted(expected_index_ids, key=lambda value: int(value.split("#")[1])):
    row_number = int(index_entry_id.split("#")[1])
    source_row = index_rows[row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    expected_candidate_id = f"cand-{985 + row_number:04d}"
    if candidate["candidate_id"] != expected_candidate_id:
        raise SystemExit(f"unexpected candidate mapping for {index_entry_id}: {candidate['candidate_id']}")
    if candidate["canonical_name"] != source_row["Main Entry"] or candidate["sub_entry"] != source_row["Sub-entry"]:
        raise SystemExit(f"S1 headword/subentry mismatch for {index_entry_id}")

    if index_entry_id in PRETYPED:
        expected_id, expected_type = PRETYPED[index_entry_id]
        if candidate["candidate_id"] != expected_id or (candidate["status"], candidate["suggested_type"]) != ("open", expected_type):
            raise SystemExit(f"pre-existing candidate classification changed: {index_entry_id}")
        retained[index_entry_id] = {"candidate_id": expected_id, "suggested_type": expected_type}
    elif index_entry_id in PENDING_INDEX_IDS:
        if candidate["status"] != "open" or candidate["suggested_type"]:
            raise SystemExit(f"type-pending candidate has unexpected state: {index_entry_id}")
        pending.append({"index_entry_id": index_entry_id, "candidate_id": candidate["candidate_id"], "reason": "private library is a collection; taxonomy has no faithful collection type"})
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

expected_types = Counter({"person": 29, "work": 8, "place": 3, "term": 1, "archive": 1, "family": 1})
if len(candidate_updates) != 43 or type_counts != expected_types or len(pending) != 1:
    raise SystemExit(f"unexpected p.454 right-column decisions: types={type_counts}; pending={pending}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1309-1363",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.12 visibly prints p.454. S0 L1309-1363 "
        "contains the complete right-column F.csv#45-92 entries; OCR fragments also occur at the end of L1253-1307 and "
        "are not counted twice. Forty-three open candidates are typed as 29 person, 8 work, 3 place, 1 term, 1 archive "
        "and 1 family; pretyped F#68, F#72, F#74 and F#85 retain their person/family/place classifications. F#45-46 remain "
        "Ciro Ferri person-context entries because the generic index wording does not identify a single work. Florence and "
        "its role as an artistic centre remain a place entry; Flemish artists in Rome is a generic group term. Fontenelle's "
        "Eloge is a literary document (archive). The paintings, sculpture/fountain, and named fresco or canvas subjects are "
        "works. F#69 Foscarini's private library remains type-pending because the taxonomy lacks a collection type. Index "
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
    "coverage_complete": 639,
    "coverage_queued": 59,
    "coverage_excluded": 134,
    "coverage_partial": 0,
    "open_index_untyped": 1791,
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
