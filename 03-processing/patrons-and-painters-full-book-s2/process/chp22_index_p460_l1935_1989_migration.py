#!/usr/bin/env python3
"""Classify p.460 left-column index entries without changing source transcriptions."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1935-1989"
SEGMENT_SHA = "3d8080e00d019ee3eaeb3855ed9e9b9a0f7906b01c6f988f0ba41536d9cf7cb7"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p460-left-l1935-1989-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_M: "4443a44bdbbce2e0ad3b758e8853b026e79edfba4d06b742ddd3043c0e215b4c",
    ROOT / "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
    ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    ROOT / "02-sources/02-Markdown/06_CHP-6_sec_iv.md": "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "11c04337cf5e11eaf130353d2afc19fad64d0b7cf58c770bc3ab12cc7438e9e9",
    TABLES / "s2-coverage.csv": "bca3ddd1eaa8dfd84d0ec0b5d4a97a2bfb30d6039779c468af77cffbb3e4de3b",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ENTRY = {
    **{f"M.csv#{i}": "person" for i in (
        82, 83, 84, 85, 87, 89, 91, 92, 93, 96, 99, 100, 101, 102, 103,
        104, 105, 106, 107, 109, 115, 116, 117, 118, 120, 122, 123, 124,
        125, 126, 127, 128, 129,
    )},
    **{f"M.csv#{i}": "place" for i in (97, 119)},
    **{f"M.csv#{i}": "work" for i in (111, 121)},
    **{f"M.csv#{i}": "archive" for i in (88, 90, 95)},
    **{f"M.csv#{i}": "event" for i in (98, 108, 112, 114)},
}
PREEXISTING_TYPES = {"M.csv#93": "person"}
TYPE_PENDING_ENTRIES = {"M.csv#94", "M.csv#110", "M.csv#113"}
EXCLUDED_ENTRIES = {"M.csv#86"}
PAGE_RANGE_CORRECTIONS = {"M.csv#116": ("395", "393")}


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
segment_text = "\n".join(source_lines[1934:1989])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.460 left-column segment changed")

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
) != (SOURCE_FILE, 1935, 1989, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.460 left-column manifest changed")

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

expected_entries = {f"M.csv#{i}" for i in range(82, 130)}
if len(expected_entries) != 48 or set(TYPE_BY_INDEX_ENTRY) | TYPE_PENDING_ENTRIES | EXCLUDED_ENTRIES != expected_entries:
    raise SystemExit("type map, pending set, and alias exclusion do not cover exactly M.csv#82-129")
if set(TYPE_BY_INDEX_ENTRY) & TYPE_PENDING_ENTRIES or set(TYPE_BY_INDEX_ENTRY) & EXCLUDED_ENTRIES:
    raise SystemExit("classification sets overlap")
if set(PREEXISTING_TYPES) != {"M.csv#93"} or any(
    TYPE_BY_INDEX_ENTRY.get(entry) != entity_type for entry, entity_type in PREEXISTING_TYPES.items()
):
    raise SystemExit("unexpected pre-existing classification")
if len(TYPE_BY_INDEX_ENTRY) != 44 or len(TYPE_PENDING_ENTRIES) != 3:
    raise SystemExit("unexpected classifiable or type-pending entry count")

all_by_entry = {}
for row in candidates:
    if row["index_entry_id"]:
        all_by_entry.setdefault(row["index_entry_id"], []).append(row)
if any(len(all_by_entry.get(entry, [])) != 1 for entry in expected_entries):
    raise SystemExit("each index row must map to exactly one candidate")

m_by_entry = {f"M.csv#{i}": m_rows[i] for i in range(len(m_rows))}
if m_by_entry["M.csv#86"]["Sub-entry"] != "see under Vandières":
    raise SystemExit("M.csv#86 is no longer the expected see-under alias")
if m_by_entry["M.csv#117"]["Main Entry"] != "Matina, L.":
    raise SystemExit("M.csv#117 changed; recheck the printed index entry")
if m_by_entry["M.csv#116"]["Page Numbers"] != "395":
    raise SystemExit("M.csv#116 page range changed; recheck the printed index")

for entry in expected_entries:
    row = all_by_entry[entry][0]
    if entry in EXCLUDED_ENTRIES:
        if (row["status"], row["suggested_type"], row["exclude_reason"]) != (
            "excluded", "", "索引交叉引用：see under Vandières"
        ):
            raise SystemExit("expected excluded alias state changed")
    elif entry in PREEXISTING_TYPES:
        if row["status"] != "open" or row["suggested_type"] != PREEXISTING_TYPES[entry]:
            raise SystemExit("pre-existing candidate type changed")
    elif row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"candidate is no longer open/untyped: {entry}")

for entry, entity_type in TYPE_BY_INDEX_ENTRY.items():
    all_by_entry[entry][0]["suggested_type"] = entity_type
for entry, (old_value, new_value) in PAGE_RANGE_CORRECTIONS.items():
    row = all_by_entry[entry][0]
    if row["index_page_range"] != old_value:
        raise SystemExit(f"candidate page-range precondition failed: {entry}")
    row["index_page_range"] = new_value

target_coverage = next((row for row in coverage if row["segment_id"] == SEGMENT_ID), None)
if not target_coverage or (
    target_coverage["disposition"], target_coverage["migration_status"],
    target_coverage["source_line_ranges"], target_coverage["note"],
) != ("queued", "pending", "", ""):
    raise SystemExit("p.460 left-column coverage state changed")
target_coverage.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L1935-1989",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.18 visibly prints p.460; "
        "S0 L1935-1989 contains M.csv#82-129 (48 rows): 47 open candidates and one pre-excluded see-under alias. "
        "Types for 44 classifiable entries: 33 person (including the pre-existing M.csv#93 type), 2 place, 2 work, "
        "3 archive and 4 event; M.csv#94 and #113 are Marucelli's personal library, and #110 is Massimi's antiquities "
        "collection, all left open/type-pending because the taxonomy has no collection type. M.csv#86 remains the "
        "excluded Vandières alias. Marino's Adone and the untitled poems on artists' works, and Marucelli's lives of "
        "painters, are textual works (archive); Bartoli's copies of Virgil manuscript illustrations are visual works. "
        "Massimi's appointment as Cardinal, the posthumous dispersal of his collection, the 1670 reorganisation of the "
        "Accademia degli Umoristi and the Masaniello revolt are events. His Nunzio role, the 'and' subentries and generic "
        "work for Shaftesbury remain person context; index navigation creates no formal relations, mentions or book "
        "statements. The page image confirms Marino's p.122 against S0's OCR p.123; M.csv#117 is Matina (S0 OCR reads "
        "Marina); candidate-only correction: M.csv#116 Mastelletta p.395 -> printed p.393. Preserve S0 and M.csv."
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
    "candidate_page_range_corrections": PAGE_RANGE_CORRECTIONS,
    "candidate_rows": len(candidates),
    "coverage": {"complete": 650, "excluded": 140, "queued": 42},
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
