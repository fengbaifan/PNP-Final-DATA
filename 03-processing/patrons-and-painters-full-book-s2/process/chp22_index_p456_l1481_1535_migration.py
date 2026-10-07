#!/usr/bin/env python3
"""Classify the left-column index candidates on printed p.456."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1481-1535"
SEGMENT_SHA = "de851c0a19348c0fec4e53aa4f220c4ac83f54a66cc7f2a35bcf643169275d13"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p456-left-l1481-1535-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "G.csv": "071ab1e6546d2d01b43e8a83042527e439598af098f8b6a7d49eef3b2234915d",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "a73139532f4b5d18a7e0994c7d007c5dc5bb3109f7133e6506476ba5d6161eef",
    TABLES / "s2-coverage.csv": "37c8e46bde4747b05ccf727722fc5720ca9e66713ea7d2462a8feddabca0bcdc",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

# Decisions apply to the printed index entry and subentry, not its page locators.
# Generic work/activity and payment subentries stay in the artist's person context.
TYPE_BY_INDEX_ID = {
    "G.csv#80": "term",
    "G.csv#81": "person",
    "G.csv#82": "family",
    "G.csv#83": "work",
    "G.csv#84": "work",
    "G.csv#85": "work",
    "G.csv#86": "work",
    "G.csv#87": "work",
    "G.csv#88": "work",
    "G.csv#89": "work",
    "G.csv#90": "work",
    "G.csv#91": "work",
    "G.csv#92": "person",
    "G.csv#93": "person",
    "G.csv#94": "person",
    "G.csv#95": "person",
    "G.csv#96": "work",
    "G.csv#97": "person",
    "G.csv#98": "person",
    "G.csv#100": "person",
    "G.csv#101": "person",
    "G.csv#102": "person",
    "G.csv#103": "person",
    "G.csv#104": "family",
    "G.csv#105": "person",
    "G.csv#106": "person",
    "G.csv#107": "person",
    "G.csv#108": "person",
    "G.csv#109": "archive",
    "G.csv#110": "term",
    "G.csv#111": "person",
    "G.csv#112": "person",
    "G.csv#113": "person",
    "G.csv#114": "archive",
    "G.csv#115": "archive",
    "G.csv#116": "archive",
    "G.csv#117": "archive",
    "G.csv#118": "archive",
    "G.csv#119": "place",
    "G.csv#121": "person",
    "G.csv#122": "person",
    "G.csv#123": "archive",
    "G.csv#124": "person",
    "G.csv#125": "person",
    "G.csv#126": "person",
}
PENDING_INDEX_IDS = {"G.csv#99"}
EXCLUDED_INDEX_IDS = {"G.csv#120"}
CANONICAL_NAME_UPDATES = {
    "G.csv#125": ("Gozadini, Bonisezio", "Gozadini, Bonifazio"),
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
segment_text = "\n".join(source_lines[1480:1535])
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
) != (SOURCE_FILE, 1481, 1535, SEGMENT_SHA, ASSET_SHA):
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
previous_right = coverage_by_id.get("chp-22:22_CHP-22Index:l1424-1477")
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1479-1479")
next_right = coverage_by_id.get("chp-22:22_CHP-22Index:l1537-1591")
next_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1593-1593")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_right or (previous_right["disposition"], previous_right["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.455 right-column segment is not complete")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.456 page marker is not excluded/complete")
if not next_right or (next_right["disposition"], next_right["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.456 right-column segment is not queued")
if not next_marker or (next_marker["disposition"], next_marker["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.457 page marker is not queued")

index_rows = read_csv(INDEX_DIR / "G.csv")[1]
candidate_rows = [candidate for candidate in candidates if candidate["index_entry_id"]]
candidate_by_index_id = {candidate["index_entry_id"]: candidate for candidate in candidate_rows}
expected_index_ids = {f"G.csv#{number}" for number in range(80, 127)}
if len(candidate_rows) != len(candidate_by_index_id):
    raise SystemExit("duplicate S1 index entry IDs in candidate table")
if {key for key in candidate_by_index_id if key in expected_index_ids} != expected_index_ids:
    raise SystemExit("S1 candidates do not cover exactly G.csv#80-126")
if set(TYPE_BY_INDEX_ID) | PENDING_INDEX_IDS | EXCLUDED_INDEX_IDS != expected_index_ids:
    raise SystemExit("p.456 left-column decisions do not account for exactly G.csv#80-126")
if (set(TYPE_BY_INDEX_ID) & PENDING_INDEX_IDS) or (set(TYPE_BY_INDEX_ID) & EXCLUDED_INDEX_IDS) or (PENDING_INDEX_IDS & EXCLUDED_INDEX_IDS):
    raise SystemExit("overlapping p.456 left-column decisions")

candidate_updates = []
type_counts = Counter()
for index_entry_id in sorted(TYPE_BY_INDEX_ID, key=lambda value: int(value.split("#")[1])):
    row_number = int(index_entry_id.split("#")[1])
    source_row = index_rows[row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    expected_candidate_id = (
        f"cand-{1173 + row_number - 80:04d}" if row_number <= 119 else f"cand-{1092 + row_number:04d}"
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
            "sub_entry": candidate["sub_entry"],
            "suggested_type": suggested_type,
        }
    )
    type_counts[suggested_type] += 1

pending_candidate = candidate_by_index_id["G.csv#99"]
if pending_candidate["candidate_id"] != "cand-1192" or pending_candidate["status"] != "open" or pending_candidate["suggested_type"]:
    raise SystemExit("G.csv#99 collection must remain open and type-pending")
excluded_candidate = candidate_by_index_id["G.csv#120"]
if excluded_candidate["candidate_id"] != "cand-2906" or excluded_candidate["status"] != "excluded":
    raise SystemExit("G.csv#120 see-under alias must remain excluded")

expected_types = Counter({"person": 23, "work": 10, "archive": 7, "family": 2, "term": 2, "place": 1})
if len(candidate_updates) != 45 or type_counts != expected_types:
    raise SystemExit(f"unexpected p.456 left-column decisions: types={type_counts}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1481-1535",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.14 visibly prints p.456. S0 L1481 is the "
        "running header; L1482-1535 contain the complete left-column entries G.csv#80-126. Forty-six candidates are open: "
        "45 are typed as 23 person, 10 work, 7 archive, 2 family, 2 term and 1 place; G#99 Giovanelli collection stays "
        "type-pending because the taxonomy has no collection class, and G#120 Gonzaga remains an excluded see-under alias. "
        "G#80 admirers in Venice is a generic reception group (term); G#82 del Rosso is a family. Named Luca Giordano "
        "pictures/cycles G#83-91 are works, including the commissioned Crossing of the Red Sea and paintings enumerated "
        "for the Labia collection. Generic work in Spain, work at S. Maria Maggiore in Bergamo and payment subentries "
        "G#92-94 remain in Giordano's person context; G#93 does not identify a separate work, consistent with the Ciro "
        "Ferri index wording. G#96 Tempesta is a work; Giustiniani and Goldoni relation/activity headings do not create "
        "formal relations here. Giustiniani's publication and Goldoni's plays, memoirs and editions plus Gori's Museum "
        "Etruscum are documents (archive); art views are a concept (term). The page image reads G#97 Giori (S0 OCR "
        "Gioii is left unchanged). It reads G#125 Gozadini, Bonifazio, while G.csv transcribes Bonisezio; correct only the "
        "candidate name to the printed spelling and retain the source transcription. Index locators add no mentions, book "
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
    "coverage_complete": 642,
    "coverage_queued": 54,
    "coverage_excluded": 136,
    "coverage_partial": 0,
    "open_index_untyped": 1652,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 456,
    "pdf_physical_page": 14,
    "candidate_updates": candidate_updates,
    "pending_type_candidates": ["G.csv#99 cand-1192"],
    "retained_exclusions": ["G.csv#120 cand-2906"],
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
