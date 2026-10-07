#!/usr/bin/env python3
"""Classify the right-column index candidates on printed p.453."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1196-1249"
SEGMENT_SHA = "534100587edeba6f8c8a9a9e631461992491b257b128b066dc92fb4fcd91cd26"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p453-rcol-l1196-1249-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "D.csv": "54be09948205d0cf43663d0d7ddb055a97102f139547387b195c6ed81f55815a",
    INDEX_DIR / "E.csv": "3ca4a5f8d7acd73e7a9b732a5989d1b9d433a44d872a6150b20bfca95a40dd0e",
    TABLES / "entity-candidates.csv": "fe36d85c65d2308754374c9314117ec45f738a10ad80012e69015a590260cced",
    TABLES / "s2-coverage.csv": "f2aec053932f10eaf2a1dbf1afd465604e5a94c7c00ebabe121683ce2cfa1181",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ID = {
    "D.csv#37": "person",
    "D.csv#38": "work",
    "D.csv#39": "work",
    "D.csv#40": "person",
    "D.csv#41": "place",
    "D.csv#42": "work",
    "D.csv#43": "institution",
    "D.csv#44": "person",
    "D.csv#45": "person",
    "D.csv#46": "person",
    "D.csv#47": "person",
    "D.csv#48": "person",
    "D.csv#49": "place",
    "D.csv#50": "person",
    "D.csv#51": "person",
    "D.csv#52": "person",
    "D.csv#53": "person",
    "D.csv#54": "person",
    "D.csv#55": "person",
    "D.csv#56": "person",
    "D.csv#57": "place",
    "D.csv#58": "term",
    "D.csv#59": "person",
    "D.csv#60": "person",
    "D.csv#61": "work",
    "D.csv#62": "work",
    "D.csv#63": "work",
    "D.csv#64": "work",
    "D.csv#65": "work",
    "D.csv#66": "work",
    "E.csv#0": "person",
    "E.csv#1": "person",
    "E.csv#2": "person",
    "E.csv#3": "person",
    "E.csv#4": "term",
    "E.csv#5": "term",
    "E.csv#6": "term",
    "E.csv#7": "term",
    "E.csv#8": "term",
    "E.csv#9": "term",
    "E.csv#10": "term",
    "E.csv#11": "term",
    "E.csv#12": "person",
    "E.csv#13": "person",
    "E.csv#14": "person",
    "E.csv#15": "person",
}
PRETYPED = {"D.csv#57": ("cand-0955", "place")}
NAME_OVERRIDES = {"D.csv#57": ("Dusseldorf", "Düsseldorf")}

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
segment_text = "\n".join(source_lines[1195:1249])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")
if "and Count of Monterey" not in source_lines[1196] or "Lord, 311n" not in source_lines[1248]:
    raise SystemExit("p.453 right-column boundaries changed")

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
) != (SOURCE_FILE, 1196, 1249, SEGMENT_SHA, ASSET_SHA):
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
previous_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1140-1194")
next_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1251-1251")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_column or (previous_column["disposition"], previous_column["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.453 left column is not complete")
if not next_marker or (next_marker["disposition"], next_marker["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.454 generated page marker is not queued")

index_csvs = {
    "D.csv": read_csv(INDEX_DIR / "D.csv", encoding="utf-8-sig")[1],
    "E.csv": read_csv(INDEX_DIR / "E.csv", encoding="utf-8-sig")[1],
}
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
if len(TYPE_BY_INDEX_ID) != 46:
    raise SystemExit(f"expected 46 explicit index decisions, found {len(TYPE_BY_INDEX_ID)}")

candidate_updates = []
name_updates = []
retained = {}
type_counts = Counter()
for index_entry_id, suggested_type in TYPE_BY_INDEX_ID.items():
    csv_name, row_number = index_entry_id.split("#")
    row_number = int(row_number)
    source_row = index_csvs[csv_name][row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    expected_candidate_number = (898 + row_number) if csv_name == "D.csv" else (965 + row_number)
    expected_candidate_id = f"cand-{expected_candidate_number:04d}"
    if candidate["candidate_id"] != expected_candidate_id:
        raise SystemExit(f"unexpected candidate mapping for {index_entry_id}: {candidate['candidate_id']}")

    old_name, new_name = NAME_OVERRIDES.get(
        index_entry_id, (source_row["Main Entry"], source_row["Main Entry"])
    )
    if candidate["canonical_name"] != old_name:
        raise SystemExit(f"unexpected candidate name for {index_entry_id}: {candidate['canonical_name']}")
    expected_source_name = old_name if index_entry_id not in NAME_OVERRIDES else "Dusseldorf"
    if source_row["Main Entry"] != expected_source_name:
        raise SystemExit(f"S1 source mapping changed: {index_entry_id}")
    if candidate["sub_entry"] != source_row["Sub-entry"]:
        raise SystemExit(f"S1 subentry mismatch for {index_entry_id}: {candidate['sub_entry']}")
    if candidate["status"] != "open":
        raise SystemExit(f"unexpected candidate status: {candidate['candidate_id']}")

    if index_entry_id in PRETYPED:
        expected_id, expected_type = PRETYPED[index_entry_id]
        if candidate["candidate_id"] != expected_id or candidate["suggested_type"] != expected_type:
            raise SystemExit(f"pre-existing candidate classification changed: {index_entry_id}")
        retained[index_entry_id] = {"candidate_id": expected_id, "suggested_type": expected_type}
    else:
        if candidate["suggested_type"]:
            raise SystemExit(f"unexpected pre-existing type: {candidate['candidate_id']}")
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

    if index_entry_id in NAME_OVERRIDES:
        candidate["canonical_name"] = new_name
        name_updates.append(
            {"index_entry_id": index_entry_id, "candidate_id": candidate["candidate_id"], "from": old_name, "to": new_name}
        )

expected_types = Counter({"person": 24, "work": 9, "place": 2, "institution": 1, "term": 9})
if len(candidate_updates) != 45 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.453 right-column type assignments: {type_counts}")
if set(retained) != {"D.csv#57"} or len(name_updates) != 1 or name_updates[0]["to"] != "Düsseldorf":
    raise SystemExit(f"unexpected pretyped candidates or name corrections: {retained}, {name_updates}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1196-1249",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.11 visibly prints p.453; D.csv#37-66 "
        "and E.csv#0-15 are the complete right-column entries. Earlier S0 L1140-1194 contains only OCR fragments from "
        "this column, already accounted for as left-column coverage and not double-counted. Forty-five open candidates are "
        "typed as 24 person, 9 work, 2 place, 1 institution and 9 term; pretyped D#57 cand-0955 remains place. The "
        "Domenichino subentries distinguish Count of Monterey (person), Naples Cathedral frescoes and Hunt of Diana "
        "(works), payments (person-context topic), the tribune of S. Andrea della Valle (architectural place), and the "
        "specific fresco scheme in S. Carlo ai Catinari (work, described in the p.76 note). D#43 Dominicans in Venice "
        "denotes the religious order (institution); D#58 Dutch artists in Rome is a generic group/topic (term). The English "
        "patronage, tourist and Enlightenment entries are generic subjects (terms). Printed p.453 spells Düsseldorf; the "
        "candidate spelling is corrected while S0, PDF and D.csv remain unchanged. Index locators add no mentions, book "
        "statements or relations."
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
    "coverage_complete": 637,
    "coverage_queued": 62,
    "coverage_excluded": 133,
    "coverage_partial": 0,
    "open_index_untyped": 1880,
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
    "retained": retained,
    "name_updates": name_updates,
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
