#!/usr/bin/env python3
"""Classify the right-column index candidates on printed p.455."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1424-1477"
SEGMENT_SHA = "d211b81cc64cb6cf5fbf5aa3d5ad0c466007b58a51e16ed93bdc9e2d89bdcb09"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p455-right-l1424-1477-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "G.csv": "071ab1e6546d2d01b43e8a83042527e439598af098f8b6a7d49eef3b2234915d",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "bacaf89bd5ed77669b291cce9482e1eec714786ce738035970d195a6e152e75f",
    TABLES / "s2-coverage.csv": "b8ff975cbce8b2099f0be64ae43d30c54792feb210fece70c481b16ff8e0d88a",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

# Decisions apply to the index headword/subentry as printed, not to locator numbers.
# Broad activity subentries stay in the artist's person context unless the index
# identifies a distinct work; see the process record for the semantic rationale.
TYPE_BY_INDEX_ID = {
    "G.csv#30": "person",
    "G.csv#31": "person",
    "G.csv#32": "person",
    "G.csv#33": "archive",
    "G.csv#34": "person",
    "G.csv#35": "work",
    "G.csv#36": "work",
    "G.csv#37": "person",
    "G.csv#38": "place",
    "G.csv#39": "term",
    "G.csv#40": "person",
    "G.csv#41": "person",
    "G.csv#42": "person",
    "G.csv#43": "work",
    "G.csv#44": "person",
    "G.csv#45": "person",
    "G.csv#46": "person",
    "G.csv#47": "person",
    "G.csv#48": "person",
    "G.csv#49": "person",
    "G.csv#50": "person",
    "G.csv#51": "term",
    "G.csv#52": "term",
    "G.csv#53": "term",
    "G.csv#54": "term",
    "G.csv#55": "term",
    "G.csv#56": "person",
    "G.csv#57": "institution",
    "G.csv#58": "term",
    "G.csv#59": "person",
    "G.csv#60": "person",
    "G.csv#61": "work",
    "G.csv#62": "person",
    "G.csv#63": "person",
    "G.csv#64": "person",
    "G.csv#65": "person",
    "G.csv#66": "person",
    "G.csv#67": "person",
    "G.csv#68": "work",
    "G.csv#69": "work",
    "G.csv#70": "person",
    "G.csv#71": "person",
    "G.csv#72": "person",
    "G.csv#73": "person",
    "G.csv#74": "person",
    "G.csv#75": "person",
    "G.csv#76": "person",
    "G.csv#77": "person",
    "G.csv#78": "person",
    "G.csv#79": "person",
}
PRETYPED_BY_INDEX_ID = {"G.csv#48": "person"}

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
segment_text = "\n".join(source_lines[1423:1477])
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
) != (SOURCE_FILE, 1424, 1477, SEGMENT_SHA, ASSET_SHA):
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
previous_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1368-1422")
next_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1479-1479")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_left or (previous_left["disposition"], previous_left["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.455 left-column segment is not complete")
if not next_marker or (next_marker["disposition"], next_marker["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.455 page marker is not queued")

index_rows = read_csv(INDEX_DIR / "G.csv")[1]
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
expected_index_ids = {f"G.csv#{number}" for number in range(30, 80)}
if set(TYPE_BY_INDEX_ID) != expected_index_ids:
    raise SystemExit("explicit p.455 right-column decisions do not cover exactly G.csv#30-79")

candidate_updates = []
retained_existing = []
type_counts = Counter()
for index_entry_id in sorted(TYPE_BY_INDEX_ID, key=lambda value: int(value.split("#")[1])):
    row_number = int(index_entry_id.split("#")[1])
    source_row = index_rows[row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    expected_candidate_id = f"cand-{1093 + row_number:04d}"
    if candidate["candidate_id"] != expected_candidate_id:
        raise SystemExit(f"unexpected candidate mapping for {index_entry_id}: {candidate['candidate_id']}")
    if candidate["canonical_name"] != source_row["Main Entry"] or candidate["sub_entry"] != source_row["Sub-entry"]:
        raise SystemExit(f"S1 headword/subentry mismatch for {index_entry_id}")
    if candidate["status"] != "open":
        raise SystemExit(f"candidate is not open: {candidate['candidate_id']}")
    suggested_type = TYPE_BY_INDEX_ID[index_entry_id]
    if candidate["suggested_type"]:
        if PRETYPED_BY_INDEX_ID.get(index_entry_id) != candidate["suggested_type"] or candidate["suggested_type"] != suggested_type:
            raise SystemExit(f"unexpected pre-existing type for {index_entry_id}: {candidate['suggested_type']}")
        retained_existing.append(
            {
                "index_entry_id": index_entry_id,
                "candidate_id": candidate["candidate_id"],
                "suggested_type": candidate["suggested_type"],
            }
        )
    else:
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

expected_types = Counter({"person": 34, "work": 6, "term": 7, "archive": 1, "institution": 1, "place": 1})
if len(candidate_updates) != 49 or retained_existing != [
    {"index_entry_id": "G.csv#48", "candidate_id": "cand-1141", "suggested_type": "person"}
] or type_counts != expected_types:
    raise SystemExit(f"unexpected p.455 right-column decisions: types={type_counts}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1424-1477",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.13 visibly prints p.455. S0 L1424-1477 "
        "contains the complete right-column entries G.csv#30-79 (50 open-status candidates); 49 are newly typed and "
        "the existing person type on G#48 cand-1141 is retained, for totals of 34 person, 6 work, "
        "7 term, 1 archive, 1 institution and 1 place. G#30 'work in Gesù' and G#44-45 'work for Charles I/Marie de "
        "Medici' describe artistic activity or commissions without identifying separate works; retain person context. "
        "G#35-36, G#43, G#61 and G#68-69 identify Danaë, Elizabeth Felton as Cleopatra, Public Felicity, the Battle of "
        "Lepanto fresco cycle, the equestrian statue of Henri IV and Mercury; these are works. G#33 Gazzeta Veneta is a "
        "periodical/document (archive); G#38 Genoa is a place; G#39 Genoese aristocracy and G#51-55/G#58 are general "
        "concepts (terms). G#57 Gesuati refers to the religious order (institution); the new church and adjoining spatial "
        "references remain distinct place candidates, with cross-entry identity handled at S3. The index page image and "
        "G.csv read G#73 as Gibbon; S0 OCR 'Gibhon' is not edited. Index locators add no mentions, book statements or "
        "relations."
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
    "coverage_complete": 641,
    "coverage_queued": 56,
    "coverage_excluded": 135,
    "coverage_partial": 0,
    "open_index_untyped": 1697,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 455,
    "pdf_physical_page": 13,
    "candidate_updates": candidate_updates,
    "retained_existing_types": retained_existing,
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
