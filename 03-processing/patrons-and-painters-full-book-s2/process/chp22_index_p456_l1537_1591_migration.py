#!/usr/bin/env python3
"""Classify the right-column index candidates on printed p.456."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1537-1591"
SEGMENT_SHA = "13fe60e3cd80def20d85b4ab44265cc65e06efad1eb35ece34a604b4c3661dfb"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p456-right-l1537-1591-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "G.csv": "071ab1e6546d2d01b43e8a83042527e439598af098f8b6a7d49eef3b2234915d",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "c981e537632b53c9755ea7b55474050a5c7dbd18d83d88cbc5699a227acaca71",
    TABLES / "s2-coverage.csv": "76e122f3a8ab63eb3d89d5075a1db5f74b4b81c15e824e461bb2201ffaf21388",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

# The printed index carries both artist contexts and named subentries. Locators
# are not facts, and relationship-only headings do not create formal relations.
TYPE_BY_INDEX_ID = {
    "G.csv#127": "person",
    "G.csv#128": "person",
    "G.csv#129": "archive",
    "G.csv#130": "term",
    "G.csv#131": "person",
    "G.csv#132": "term",
    "G.csv#133": "person",
    "G.csv#134": "person",
    "G.csv#136": "family",
    "G.csv#137": "person",
    "G.csv#140": "person",
    "G.csv#141": "person",
    "G.csv#142": "person",
    "G.csv#143": "person",
    "G.csv#144": "person",
    "G.csv#145": "person",
    "G.csv#146": "person",
    "G.csv#147": "person",
    "G.csv#148": "work",
    "G.csv#149": "person",
    "G.csv#150": "person",
    "G.csv#151": "work",
    "G.csv#152": "work",
    "G.csv#153": "person",
    "G.csv#154": "person",
    "G.csv#155": "person",
    "G.csv#156": "work",
    "G.csv#157": "work",
    "G.csv#158": "work",
    "G.csv#159": "work",
    "G.csv#160": "work",
    "G.csv#161": "work",
    "G.csv#162": "person",
    "G.csv#163": "work",
    "G.csv#164": "work",
    "G.csv#165": "work",
    "G.csv#166": "work",
    "G.csv#167": "work",
    "G.csv#168": "person",
    "G.csv#169": "work",
    "G.csv#170": "work",
    "G.csv#171": "archive",
    "G.csv#172": "work",
    "G.csv#173": "work",
    "G.csv#174": "work",
    "G.csv#175": "person",
    "G.csv#176": "term",
}
PENDING_INDEX_IDS = {"G.csv#135"}
EXCLUDED_INDEX_IDS = {"G.csv#138", "G.csv#139"}
CANONICAL_NAME_UPDATES = {
    "G.csv#141": ("Grill, Angelica", "Griè, Angelica"),
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
segment_text = "\n".join(source_lines[1536:1591])
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
) != (SOURCE_FILE, 1537, 1591, SEGMENT_SHA, ASSET_SHA):
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
previous_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1481-1535")
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1479-1479")
next_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1593-1593")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_left or (previous_left["disposition"], previous_left["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.456 left-column segment is not complete")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.456 page marker is not excluded/complete")
if not next_marker or (next_marker["disposition"], next_marker["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next page marker is not queued")

index_rows = read_csv(INDEX_DIR / "G.csv")[1]
candidate_rows = [candidate for candidate in candidates if candidate["index_entry_id"]]
candidate_by_index_id = {candidate["index_entry_id"]: candidate for candidate in candidate_rows}
expected_index_ids = {f"G.csv#{number}" for number in range(127, 177)}
if len(candidate_rows) != len(candidate_by_index_id):
    raise SystemExit("duplicate S1 index entry IDs in candidate table")
if {key for key in candidate_by_index_id if key in expected_index_ids} != expected_index_ids:
    raise SystemExit("S1 candidates do not cover exactly G.csv#127-176")
if set(TYPE_BY_INDEX_ID) | PENDING_INDEX_IDS | EXCLUDED_INDEX_IDS != expected_index_ids:
    raise SystemExit("p.456 right-column decisions do not account for exactly G.csv#127-176")
if (set(TYPE_BY_INDEX_ID) & PENDING_INDEX_IDS) or (set(TYPE_BY_INDEX_ID) & EXCLUDED_INDEX_IDS) or (PENDING_INDEX_IDS & EXCLUDED_INDEX_IDS):
    raise SystemExit("overlapping p.456 right-column decisions")

candidate_updates = []
type_counts = Counter()
for index_entry_id in sorted(TYPE_BY_INDEX_ID, key=lambda value: int(value.split("#")[1])):
    row_number = int(index_entry_id.split("#")[1])
    source_row = index_rows[row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    expected_candidate_id = (
        f"cand-{1092 + row_number:04d}" if row_number <= 137 else f"cand-{1090 + row_number:04d}"
    )
    if candidate["candidate_id"] != expected_candidate_id:
        raise SystemExit(f"unexpected candidate mapping for {index_entry_id}: {candidate['candidate_id']}")
    if candidate["canonical_name"] != source_row["Main Entry"]:
        raise SystemExit(f"S1 headword mismatch for {index_entry_id}")
    if candidate["sub_entry"] != source_row["Sub-entry"] or candidate["detail"] != source_row["Detail"]:
        raise SystemExit(f"S1 subentry/detail mismatch for {index_entry_id}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"candidate is not open and untyped: {candidate['candidate_id']}")
    suggested_type = TYPE_BY_INDEX_ID[index_entry_id]
    candidate["suggested_type"] = suggested_type
    if index_entry_id in CANONICAL_NAME_UPDATES:
        old_name, new_name = CANONICAL_NAME_UPDATES[index_entry_id]
        if candidate["canonical_name"] != old_name:
            raise SystemExit(f"unexpected name before page-image correction: {index_entry_id}")
        candidate["canonical_name"] = new_name
    candidate_updates.append(
        {
            "index_entry_id": index_entry_id,
            "candidate_id": candidate["candidate_id"],
            "canonical_name": candidate["canonical_name"],
            "suggested_type": suggested_type,
        }
    )
    type_counts[suggested_type] += 1

pending_candidate = candidate_by_index_id["G.csv#135"]
if pending_candidate["candidate_id"] != "cand-1227" or pending_candidate["status"] != "open" or pending_candidate["suggested_type"]:
    raise SystemExit("G.csv#135 collection must remain open and type-pending")
for alias_id, candidate_id in (("G.csv#138", "cand-2907"), ("G.csv#139", "cand-2908")):
    alias = candidate_by_index_id[alias_id]
    if alias["candidate_id"] != candidate_id or alias["status"] != "excluded":
        raise SystemExit(f"see-under alias must remain excluded: {alias_id}")

expected_types = Counter({"person": 22, "work": 19, "archive": 2, "term": 3, "family": 1})
if len(candidate_updates) != 47 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.456 right-column decisions: types={type_counts}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1537-1591",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.14 visibly prints p.456. L1537 is the "
        "running header; the right column contains G.csv#127-176. The left-column OCR fragments embedded in S0 L1544-1557 "
        "and L1569-1574 are not reclassified; the page image separates the two columns. Fifty entries contain 48 open "
        "candidates: 47 typed as 22 person, 19 work, 2 archive, 3 term and 1 family; G#135 Grassi collection stays "
        "type-pending because the taxonomy has no collection class, while G#138-139 Gregory see-under aliases remain "
        "excluded. G#129 Gasparo Gozzi's articles on Pietro Longhi are documents (archive); the social value of painting "
        "and views on art are indexed concepts (terms); support for Pisani remains in Gozzi's person context. G#151 and "
        "G#159 Sala del Maggior Consiglio refer to an artwork attributed to both Guardis (book p.316); keep the candidates "
        "separate for S3 identity alignment. G#152/G#160 scenes from Gerusalemme Liberata and G#156 Parlatorio/G#158 "
        "Ridotto are Guardi works (book pp.336, 383), not place entries. G#162 is the general copyist context; G#163-167 "
        "identify the copied Tintoretto, Veronese and Bassano paintings. G#171 is a contract (archive); titled Guercino "
        "paintings are works, and payment/rates remain person-context/term entries. The page image reads G#141 Griè, "
        "Angelica; correct only the candidate name from the G.csv OCR 'Grill'. Index locators add no mentions, book "
        "statements or relations."
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
    "coverage_complete": 643,
    "coverage_queued": 53,
    "coverage_excluded": 136,
    "coverage_partial": 0,
    "open_index_untyped": 1605,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 456,
    "pdf_physical_page": 14,
    "candidate_update_count": len(candidate_updates),
    "candidate_updates": candidate_updates,
    "pending_type_candidates": ["G.csv#135 cand-1227"],
    "retained_exclusions": ["G.csv#138 cand-2907", "G.csv#139 cand-2908"],
    "corrected_candidate_names": CANONICAL_NAME_UPDATES,
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
