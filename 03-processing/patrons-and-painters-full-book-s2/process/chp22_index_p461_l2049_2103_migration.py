#!/usr/bin/env python3
"""Classify the p.461 left-column index entries with print-checked corrections."""

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
INDEX_M = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "M.csv"
SEGMENT_ID = "chp-22:22_CHP-22Index:l2049-2103"
SEGMENT_SHA = "371c20a03d17983562607b3e0e6c52a484999b30feff65203483cbb5209d43e3"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p461-left-l2049-2103-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_M: "4443a44bdbbce2e0ad3b758e8853b026e79edfba4d06b742ddd3043c0e215b4c",
    ROOT / "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md": "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md": "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    ROOT / "02-sources/02-Markdown/12_CHP-12.md": "cc062734cdbbae045e799647e6200407e0cb988cf5599dea9cd65496b33b7f4b",
    ROOT / "02-sources/02-Markdown/15_CHP-15_sec_i.md": "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624",
    ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    ROOT / "02-sources/02-Markdown/17_CHP-17_sec_ii.md": "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3",
    ROOT / "02-sources/02-Markdown/19_CHP-19Appendix.md": "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "add092d9ac0fad483ce1e8ef4ab9852a528507c84954506d11d85b277bf85d85",
    TABLES / "s2-coverage.csv": "defd6b792ea087423c5aac9e86e9eb709139480de75f87e9509257290a076086",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ENTRY = {
    **{f"M.csv#{i}": "person" for i in (
        176, 179, 180, 181, 182, 183, 185, 188, 192, 193, 194, 196, 199,
        200, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213,
        215, 216, 218, 219, 220, 223,
    )},
    **{f"M.csv#{i}": "work" for i in (174, 175, 177, 178, 190, 197, 201, 217)},
    **{f"M.csv#{i}": "archive" for i in (187, 189, 221)},
    **{f"M.csv#{i}": "event" for i in (184, 191)},
    "M.csv#195": "place",
    "M.csv#198": "family",
    "M.csv#214": "term",
}
PREEXISTING_TYPES = {"M.csv#222": "person"}
TYPE_PENDING_ENTRIES = {"M.csv#186"}
PAGE_RANGE_CORRECTIONS = {
    "M.csv#214": (
        "11, 12, 97, 104, 213, 232, 233, 222n, 273n, 352, 353, 374",
        "11, 12, 97, 104, 213, 232, 233, 255n, 273n, 352, 353, 374",
    ),
}
ENTRY_CORRECTIONS = {
    "M.csv#218": {
        "expected": {
            "canonical_name": "Mola, Pier Francesco",
            "sub_entry": "Five Elements",
            "index_page_range": "12n",
        },
        "replacement": {"sub_entry": "payments", "index_page_range": "13n"},
    }
}


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


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write reviewed candidate types, corrections, and coverage")
ARGS = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2048:2103])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.461 left-column segment changed")

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
    segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
    segment.get("sha256"), segment.get("asset_sha256"), segment.get("release_excluded"),
) != (SOURCE_FILE, 2049, 2103, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.461 left-column manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(mentions), len(statements)) != (11436, 832, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

candidate_by_entry = {
    row["index_entry_id"]: row
    for row in candidates
    if row.get("index_entry_id") in {f"M.csv#{i}" for i in range(174, 224)}
}
expected_entries = {f"M.csv#{i}" for i in range(174, 224)}
if set(candidate_by_entry) != expected_entries or len(candidate_by_entry) != 50:
    raise SystemExit("p.461 left-column candidate mapping is incomplete or duplicated")
for entry_id, row in candidate_by_entry.items():
    if row["status"] != "open":
        raise SystemExit(f"unexpected candidate status for {entry_id}: {row['status']}")
for entry_id, expected_type in PREEXISTING_TYPES.items():
    if candidate_by_entry[entry_id]["suggested_type"] != expected_type:
        raise SystemExit(f"pre-existing type changed for {entry_id}")
for entry_id in TYPE_BY_INDEX_ENTRY.keys() | TYPE_PENDING_ENTRIES:
    if entry_id not in PREEXISTING_TYPES and candidate_by_entry[entry_id]["suggested_type"]:
        raise SystemExit(f"unexpected prior type for {entry_id}")
if set(TYPE_BY_INDEX_ENTRY) & (set(TYPE_PENDING_ENTRIES) | set(PREEXISTING_TYPES)):
    raise SystemExit("type map overlaps pending or pre-existing entries")
if len(TYPE_BY_INDEX_ENTRY) != 48 or len(TYPE_PENDING_ENTRIES) != 1 or len(PREEXISTING_TYPES) != 1:
    raise SystemExit("unexpected reviewed classification counts")

for entry_id, (before, after) in PAGE_RANGE_CORRECTIONS.items():
    if candidate_by_entry[entry_id]["index_page_range"] != before:
        raise SystemExit(f"unexpected page range for {entry_id}")
for entry_id, correction in ENTRY_CORRECTIONS.items():
    row = candidate_by_entry[entry_id]
    if any(row[field] != value for field, value in correction["expected"].items()):
        raise SystemExit(f"unexpected source text or page range for {entry_id}")

target = next((row for row in coverage if row["segment_id"] == SEGMENT_ID), None)
if not target or (
    target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]
) != ("queued", "pending", "", ""):
    raise SystemExit("p.461 left-column coverage state changed")

for entry_id, entity_type in TYPE_BY_INDEX_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for entry_id, (_, corrected_range) in PAGE_RANGE_CORRECTIONS.items():
    candidate_by_entry[entry_id]["index_page_range"] = corrected_range
for entry_id, correction in ENTRY_CORRECTIONS.items():
    candidate_by_entry[entry_id].update(correction["replacement"])

target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2049-2103",
    "note": (
        "no_semantic_content: index-seed classification only. On CHP-22Index.pdf physical p.19, "
        "L2049 is the running INDEX head and the left column contains M.csv#174-223 (50 entries); "
        "the OCR also carries fragments from the right column, which is handled by the next segment. "
        "Forty-eight new types: 32 person, 8 work, 3 archive, 2 event, 1 place, 1 family, 1 term; "
        "preserve existing person type M.csv#222. M.csv#186 (Memmo's personal collection) remains "
        "open/type-pending because taxonomy has no collection type. The print reads Modelli p.255n, "
        "so candidate cand-1674 M.csv#214 page range is corrected from 222n to 255n. The print reads "
        "Mola subentry 'payments, 13n', not M.csv#218 'Five Elements, 12n'; candidate cand-1678 is "
        "corrected to payments p.13n and person context, since this is general payment information, "
        "not a distinct event or work. Preserve S0 and M.csv transcriptions. Mei's Justice and Peace "
        "and Youth rescued from the Pleasures of Venus, Melanconici's Abraham and David with the Head "
        "of Goliath, Mola's Four Elements, Antonello's Deposition, and Michelangelo's Risen Christ are "
        "works; Memmo's Elementi and notes are archives, his Procuratore appointment and publication "
        "of Lodoli's Apologhi are events, and the Prà della Valle design is a work. Index links do not "
        "create mentions, book statements, or formal relations."
    ),
})

added_types = Counter(TYPE_BY_INDEX_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": 50,
    "new_types": len(TYPE_BY_INDEX_ENTRY),
    "preserved_types": PREEXISTING_TYPES,
    "type_pending": sorted(TYPE_PENDING_ENTRIES),
    "added_types": dict(sorted(added_types.items())),
    "page_range_corrections": {key: list(value) for key, value in PAGE_RANGE_CORRECTIONS.items()},
    "entry_corrections": {
        key: {"from": correction["expected"], "to": correction["replacement"]}
        for key, correction in ENTRY_CORRECTIONS.items()
    },
    "apply": ARGS.apply,
}

if ARGS.apply:
    backups = [candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX), coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)]
    if any(path.exists() for path in backups):
        raise SystemExit("a backup with this task suffix already exists")
    for source, backup in zip((candidate_path, coverage_path), backups):
        shutil.copy2(source, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    if sha256(candidate_path) == EXPECTED_HASHES[candidate_path] or sha256(coverage_path) == EXPECTED_HASHES[coverage_path]:
        raise SystemExit("apply did not update both S2 tables")
    summary["backups"] = [str(path.relative_to(ROOT)) for path in backups]

print(json.dumps(summary, ensure_ascii=False, indent=2))
