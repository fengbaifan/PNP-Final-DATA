#!/usr/bin/env python3
"""Classify the p.466 right-column index entries and correct the printed locator."""

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
QR_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "Q-R.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l2672-2726"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p466-right-l2672-2726-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/Q-R.csv": "8a95726a58f59efc58cff819448acb23f36608e469fd1c8aeda9dca656f3a15c",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/10_CHP-10.md": "fe5e51c703a2004790c2d219c11782ae20a2791cac7fffdedda39354f6522a19",
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "f4ea61b3dcc8ae8f9d1fe7226baa6bfe89ef76591c9948d51f33d0348cb679b1",
    "04-knowledge/tables/s2-coverage.csv": "34d737cdb4e258c47628d914ef4f8e3bc041a31af27454b530b87a69559c9667",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"Q-R.csv#{i}": "work" for i in (
        77, 78, 79, 80, 82, *range(84, 90), 91, 92, *range(94, 100), 100, 101, 103, 105, *range(107, 113), 118
    )},
    **{f"Q-R.csv#{i}": "person" for i in (83, 114, 115, 116, 119, 120, 121, 122, 123, 124)},
    "Q-R.csv#117": "event",
    "Q-R.csv#93": "term",
}
PRESERVED_TYPES = {
    "Q-R.csv#81": ("cand-2154", "Ricci, Sebastiano", "person"),
    "Q-R.csv#90": ("cand-2163", "Ricci, Sebastiano", "work"),
    "Q-R.csv#102": ("cand-2175", "Ricci, Sebastiano", "work"),
    "Q-R.csv#104": ("cand-2177", "Ricci, Sebastiano", "work"),
    "Q-R.csv#106": ("cand-2179", "Ricci, Sebastiano", "work"),
    "Q-R.csv#113": ("cand-2186", "Ricci, Sebastiano", "work"),
}
EXPECTED_ENTRIES = {f"Q-R.csv#{i}" for i in range(77, 125)}
EXPECTED_SEGMENT_SHA256 = "4b49d15842658f7fe3f9ba20b9daa15789770570664a9a8812b3f9f36e504e42"
SEGMENT_RANGE = (2672, 2726)
CORRECTIONS = [
    (
        "cand-2154", "Q-R.csv#81", "index_page_range",
        "9n, 165, 199, 214, 226, 228, 251, 269n, 270, 271, 273, 276n, 279, 284, 286, 293, 295, 296, 297, 304, 311, 313, 315, 337, 341, 342, 374, 376, 377, 394, 405, 407",
        "9n, 165, 199, 214, 226, 228, 251, 269n, 270, 271, 273, 276n, 279, 284, 286, 293, 295, 296, 297, 304, 310, 313, 315, 337, 341, 342, 374, 376, 377, 394, 405, 407",
    ),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write reviewed index types, locator correction and coverage")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[SEGMENT_RANGE[0] - 1:SEGMENT_RANGE[1]])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA256:
    raise SystemExit("p.466 right-column source segment changed")
if not all(token in segment_text for token in (
    "Monuments to (McSwiny’s British Worthies)", "Ricci, Sebastiano", "fear of style being corrupted by Rome",
    "attempt to bring Italian artists to Paris", "Ridolfi, Carlo",
)):
    raise SystemExit("p.466 right-column content check failed")
if "[Page 467]" in segment_text or "Rapparini, Giorgio Maria" in segment_text:
    raise SystemExit("left-column or next-page content leaked into the p.466 right-column segment")

with QR_INDEX.open(encoding="utf-8-sig", newline="") as handle:
    qr_rows = list(csv.DictReader(handle))
if len(qr_rows) <= 124 or (qr_rows[77]["Main Entry"], qr_rows[124]["Main Entry"]) != (
    "Ricci, Marco", "Ridolfi, Carlo"
):
    raise SystemExit("Q-R.csv#77-124 boundary check failed")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
manifest_row = manifest.get(SEGMENT_ID)
if not manifest_row or (
    manifest_row.get("source_file"), manifest_row.get("line_start"), manifest_row.get("line_end"),
    manifest_row.get("sha256"), manifest_row.get("asset_sha256"), manifest_row.get("release_excluded"),
) != (SOURCE_FILE, *SEGMENT_RANGE, EXPECTED_SEGMENT_SHA256, EXPECTED_HASHES[SOURCE_FILE], True):
    raise SystemExit("p.466 right-column manifest mismatch")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
if len(candidates) != 11436 or len(coverage) != 832:
    raise SystemExit("unexpected S2 table dimensions")

candidate_by_entry = {}
candidate_by_id = {}
for row in candidates:
    candidate_by_id[row["candidate_id"]] = row
    entry_id = row.get("index_entry_id", "")
    if entry_id in EXPECTED_ENTRIES:
        if entry_id in candidate_by_entry:
            raise SystemExit(f"duplicate candidate mapping: {entry_id}")
        candidate_by_entry[entry_id] = row
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 48:
    raise SystemExit("p.466 right-column index candidate mapping is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
for entry_id, (candidate_id, canonical_name, entity_type) in PRESERVED_TYPES.items():
    row = candidate_by_entry[entry_id]
    if (row["candidate_id"], row["canonical_name"], row["suggested_type"], row["status"]) != (
        candidate_id, canonical_name, entity_type, "open"
    ):
        raise SystemExit(f"pre-existing candidate type changed: {entry_id}")

for candidate_id, entry_id, field, before, _after in CORRECTIONS:
    row = candidate_by_id.get(candidate_id)
    if not row or row["index_entry_id"] != entry_id or row[field] != before or row["status"] != "open":
        raise SystemExit(f"printed-page correction pre-state changed: {candidate_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
target = coverage_by_segment.get(SEGMENT_ID)
if not target or (target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.466 right-column coverage is not queued/pending")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for candidate_id, _entry_id, field, _before, after in CORRECTIONS:
    candidate_by_id[candidate_id][field] = after

target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2672-2726",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.24 prints p.466; the physical right column contains "
        "Q-R.csv#77-124 (48 entries), from Ricci, Marco's McSwiny's British Worthies entries through Ridolfi, Carlo. New types: 30 work, "
        "10 person, 1 event and 1 term; preserve six pre-existing types: Q-R#81 Ricci Sebastiano person and #90, #102, #104, #106, #113 work. "
        "The McSwiny British Worthies entries refer to the documented commemorative painting series and named subjects; they classify the index "
        "seeds as works without asserting a new artist-work relation. Q-R#80 and #106-112 work-for/in subentries are work-context candidates only; "
        "they do not create formal patronage relations. Q-R#83 and #121-122 remain person context, with no relation inferred from 'and' or ownership "
        "wording. Q-R#93 fear of style being corrupted by Rome is a term. Q-R#117 Richelieu's attempt to bring Italian artists to Paris is a historical "
        "initiative/event, not a set of formal relations. Q-R#118 Bernini bust is a work. Printed p.466 corrects cand-2154/Q-R#81 Ricci Sebastiano "
        "locator 311→310. Q-R.csv and S0 remain unchanged. Index navigation creates no mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
preserved_counts = Counter(entity_type for _candidate_id, _canonical_name, entity_type in PRESERVED_TYPES.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "preserved_existing_types": list(PRESERVED_TYPES),
    "final_type_counts_in_segment": {
        entity_type: counts[entity_type] + preserved_counts[entity_type]
        for entity_type in sorted(set(counts) | set(preserved_counts))
    },
    "candidate_corrections": [
        {"candidate_id": candidate_id, "index_entry_id": entry_id, "field": field, "before": before, "after": after}
        for candidate_id, entry_id, field, before, after in CORRECTIONS
    ],
    "mentions_or_statements_changed": False,
    "apply": args.apply,
}

if args.apply:
    backups = [
        candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
        coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
    ]
    if any(path.exists() for path in backups):
        raise SystemExit("a backup with this task suffix already exists")
    for original, backup in zip((candidate_path, coverage_path), backups):
        shutil.copy2(original, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    summary["backups"] = [str(path.relative_to(ROOT)) for path in backups]

print(json.dumps(summary, ensure_ascii=False, indent=2))
