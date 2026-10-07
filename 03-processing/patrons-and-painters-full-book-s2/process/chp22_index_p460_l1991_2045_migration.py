#!/usr/bin/env python3
"""Classify p.460 right-column index entries without changing source transcriptions."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1991-2045"
SEGMENT_SHA = "f9bcb1fcb6be1429a8468a3511dd5daafee037fda7a69621600e4417a5591c3b"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p460-right-l1991-2045-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_M: "4443a44bdbbce2e0ad3b758e8853b026e79edfba4d06b742ddd3043c0e215b4c",
    ROOT / "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "4204780d36032b3ce5b9f92bd48390632a61676ad3d158b9a8fab555bfc3f682",
    TABLES / "s2-coverage.csv": "9b004520c217e45693f937d98f25703fbdce8bbe5af64a317a4bcb7b25fd03a7",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ENTRY = {
    **{f"M.csv#{i}": "person" for i in (
        130, 131, 132, 140, 141, 143, 144, 145, 146, 147, 148, 149,
        151, 152, 153, 154, 155, 156, 157, 159, 161, 162, 163, 164,
        166, 167, 168, 169, 170, 171, 172, 173,
    )},
    **{f"M.csv#{i}": "event" for i in (133, 134, 137, 138)},
    **{f"M.csv#{i}": "archive" for i in (135, 136)},
    **{f"M.csv#{i}": "term" for i in (139, 158, 165)},
    "M.csv#150": "procedure",
}
PREEXISTING_TYPES = {"M.csv#151": "person", "M.csv#157": "person"}
TYPE_PENDING_ENTRIES = {"M.csv#160"}
EXCLUDED_ENTRIES = {"M.csv#142"}


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
parser.add_argument("--apply", action="store_true", help="write the reviewed candidate types and coverage")
ARGS = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1990:2045])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.460 right-column segment changed")

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
) != (SOURCE_FILE, 1991, 2045, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.460 right-column manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
_m_fields, m_rows = read_csv(INDEX_M)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(m_rows), len(mentions), len(statements)) != (11436, 832, 262, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

expected_entries = {f"M.csv#{i}" for i in range(130, 174)}
if len(expected_entries) != 44 or set(TYPE_BY_INDEX_ENTRY) | TYPE_PENDING_ENTRIES | EXCLUDED_ENTRIES != expected_entries:
    raise SystemExit("type map, pending set, and alias exclusion do not cover exactly M.csv#130-173")
if set(TYPE_BY_INDEX_ENTRY) & TYPE_PENDING_ENTRIES or set(TYPE_BY_INDEX_ENTRY) & EXCLUDED_ENTRIES:
    raise SystemExit("classification sets overlap")
if set(PREEXISTING_TYPES) != {"M.csv#151", "M.csv#157"} or any(
    TYPE_BY_INDEX_ENTRY.get(entry) != entity_type for entry, entity_type in PREEXISTING_TYPES.items()
):
    raise SystemExit("unexpected pre-existing classifications")
if len(TYPE_BY_INDEX_ENTRY) != 42 or len(TYPE_PENDING_ENTRIES) != 1:
    raise SystemExit("unexpected classifiable or type-pending entry count")

all_by_entry = {}
for row in candidates:
    if row["index_entry_id"]:
        all_by_entry.setdefault(row["index_entry_id"], []).append(row)
if any(len(all_by_entry.get(entry, [])) != 1 for entry in expected_entries):
    raise SystemExit("each index row must map to exactly one candidate")

m_by_entry = {f"M.csv#{i}": m_rows[i] for i in range(len(m_rows))}
if m_by_entry["M.csv#142"]["Sub-entry"] != "see under Mazarin":
    raise SystemExit("M.csv#142 is no longer the expected see-under alias")
if m_by_entry["M.csv#160"]["Sub-entry"] != "collection":
    raise SystemExit("M.csv#160 changed; recheck the printed index entry")

for entry in expected_entries:
    row = all_by_entry[entry][0]
    if entry in EXCLUDED_ENTRIES:
        if (row["status"], row["suggested_type"], row["exclude_reason"]) != (
            "excluded", "", "索引交叉引用：see under Mazarin"
        ):
            raise SystemExit("expected excluded alias state changed")
    elif entry in PREEXISTING_TYPES:
        if row["status"] != "open" or row["suggested_type"] != PREEXISTING_TYPES[entry]:
            raise SystemExit("pre-existing candidate type changed")
    elif row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"candidate is no longer open/untyped: {entry}")

for entry, entity_type in TYPE_BY_INDEX_ENTRY.items():
    all_by_entry[entry][0]["suggested_type"] = entity_type

target_coverage = next((row for row in coverage if row["segment_id"] == SEGMENT_ID), None)
if not target_coverage or (
    target_coverage["disposition"], target_coverage["migration_status"],
    target_coverage["source_line_ranges"], target_coverage["note"],
) != ("queued", "pending", "", ""):
    raise SystemExit("p.460 right-column coverage state changed")
target_coverage.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L1991-2045",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.18 visibly prints p.460; "
        "S0 L1991-2045 contains the running head and M.csv#130-173 (44 index rows): 43 open candidates and one "
        "pre-excluded see-under alias. Types for 42 classifiable entries: 32 person (including the two pre-existing "
        "person types M.csv#151 and #157), 4 event, 2 archive, 3 term and 1 procedure; M.csv#160 Ferdinand collection "
        "remains open/type-pending because taxonomy has no collection type. M.csv#142 remains the excluded Mazarin alias. "
        "Mazarin's specific attempts to recruit Bernini/Algardi, the Fronde opposition and purchase of Bentivoglio Palace "
        "are events; Brienne's farewell account and the collection inventory are archives; his taste is a term. "
        "Ferdinand's recurring public-exhibition practice is a procedure, the Venetian sixteenth-century painting tradition "
        "and taste in painting are terms. Generic artist/family associations, Venice, employment, patronage and writing "
        "support remain person context; index navigation creates no formal relations, mentions or book statements. "
        "Preserve S0 transcription and M.csv; no candidate page-range correction is needed."
    ),
})

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "index_rows": len(expected_entries),
    "newly_typed": len(TYPE_BY_INDEX_ENTRY) - len(PREEXISTING_TYPES),
    "type_counts_including_preexisting": dict(Counter(TYPE_BY_INDEX_ENTRY.values())),
    "type_pending": sorted(TYPE_PENDING_ENTRIES),
    "excluded_alias": sorted(EXCLUDED_ENTRIES),
    "candidate_rows": len(candidates),
    "coverage": {"complete": 651, "excluded": 140, "queued": 41},
    "mentions_unchanged": len(mentions),
    "statements_unchanged": len(statements),
}
if ARGS.apply:
    backups = []
    for path in (candidate_path, coverage_path):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup.name}")
        shutil.copy2(path, backup)
        backups.append(backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for path in backups]
print(json.dumps(result, ensure_ascii=False, indent=2))
