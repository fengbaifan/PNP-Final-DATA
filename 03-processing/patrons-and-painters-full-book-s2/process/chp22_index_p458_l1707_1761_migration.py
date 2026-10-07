#!/usr/bin/env python3
"""Classify the printed p.458 left-column index entries, preserving OCR sources."""

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
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "L.csv"
TAXONOMY = ROOT / "01-domain" / "taxonomy-registry.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1707-1761"
SEGMENT_SHA = "a50d6e2e273aa92b960529677bb10ca78e8c47036fb206fd14b59034d1ade70d"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p458-left-l1707-1761-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_CSV: "c32c7a0f784b88625ea5635deaccb0e2734b629e051edacccc6f0d222aa30db1",
    TAXONOMY: "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md": "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md": "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    ROOT / "02-sources/02-Markdown/05_CHP-5_sec_iii.md": "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md": "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "97322364947e7ab285be022f9dba87112b375da6ee3feea4ed4f43456093d1a6",
    TABLES / "s2-coverage.csv": "fe488699e75c5750456daf9fab23d4f4c2b4b53e79f29f0ec817cf0859ff58ba",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

# Index-only context remains attached to its person; independently named works and documents get their own types.
TYPE_BY_INDEX_ENTRY = {
    **{f"L.csv#{i}": "person" for i in (10, 12, 14, 16, 18, 19, 20, 21, 22, 23, 24, 25, 31, 32, 33, 34, 35, 36, 40, 41, 42, 43, 44, 45, 46, 47, 51, 52, 54, 55, 56)},
    **{f"L.csv#{i}": "work" for i in (9, 11, 17, 26, 27, 28, 29, 30, 37, 38, 39, 48, 49, 53)},
    "L.csv#13": "archive",
    "L.csv#50": "archive",
    "L.csv#15": "term",
}

PAGE_RANGE_CORRECTIONS = {
    "L.csv#13": ("311", "3n"),
    "L.csv#15": ("105, 111, 143, 155, 172, 173, 378", "105, 111, 143, 155, 172, 173, 328"),
    "L.csv#34": ("122, 184", "133, 184"),
    "L.csv#41": ("122n", "135n"),
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
segment_text = "\n".join(source_lines[1706:1761])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.458 left-column segment changed")

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
) != (SOURCE_FILE, 1707, 1761, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 p.458 left-column manifest changed")

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

by_entry = {row["index_entry_id"]: row for row in candidates}
expected_entries = {f"L.csv#{i}" for i in range(9, 57)}
scope = [row for row in candidates if row["index_entry_id"] in expected_entries]
if len(scope) != 48 or set(by_entry) & expected_entries != expected_entries:
    raise SystemExit("p.458 left-column candidate mapping is incomplete or duplicated")
if set(TYPE_BY_INDEX_ENTRY) != expected_entries:
    raise SystemExit("type map does not cover exactly L.csv#9-56")
for entry in sorted(expected_entries, key=lambda item: int(item.split("#")[1])):
    row = by_entry[entry]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"candidate is not in expected open/untyped state: {entry}")

for entry, (old, new) in PAGE_RANGE_CORRECTIONS.items():
    if by_entry[entry]["index_page_range"] != old:
        raise SystemExit(f"unexpected CSV page range for {entry}: {by_entry[entry]['index_page_range']!r}")
    by_entry[entry]["index_page_range"] = new

for entry, entity_type in TYPE_BY_INDEX_ENTRY.items():
    by_entry[entry]["suggested_type"] = entity_type

typed_counts = Counter(by_entry[entry]["suggested_type"] for entry in expected_entries)
expected_types = Counter({"person": 31, "work": 14, "archive": 2, "term": 1})
if typed_counts != expected_types:
    raise SystemExit(f"unexpected p.458 left-column type counts: {typed_counts}")

coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous = coverage_by_id.get("chp-22:22_CHP-22Index:l1705-1705")
previous_right = coverage_by_id.get("chp-22:22_CHP-22Index:l1651-1703")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.458 left-column segment is not queued")
if not previous or (previous["disposition"], previous["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.458 page marker is not complete")
if not previous_right or (previous_right["disposition"], previous_right["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.457 right-column segment is not complete")

target.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1707-1761",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.16 visibly prints p.458. S0 L1707-1761 "
        "contains the complete left-column entries L.csv#9-56 (48 open candidates), typed as 31 person, 14 work, "
        "2 archive and 1 term. Named paintings by Van Laer and Legros, Lanfranco's dome, Lazzarini's painted "
        "Triumphal Arch, Leonardo's named paintings and Leoni's etching are works; L'Hoggidi and Leonardo's "
        "Trattato della pittura are documents (archive). Van Laer's prices, Lanfranco's payments and commissions, "
        "and Lazzarini's unspecified work for S. Paolo d'Argan remain person context. Landscapes with varying "
        "reactions in Rome and Venice is a term. The S0 page image corrects candidate-only locators L.csv#13 "
        "311->3n, #15 378->328, #34 122->133 and #41 122n->135n; original S0 and L.csv are unchanged. Index "
        "locators add no mentions, book statements or relations."
    ),
)

after = {
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
}
expected_after = {"coverage_complete": 646, "coverage_queued": 48, "coverage_excluded": 138, "coverage_partial": 0}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 458,
    "pdf_physical_page": 16,
    "typed_candidates": 48,
    "type_counts": dict(typed_counts),
    "candidate_locator_corrections": {
        entry: {"from": old, "to": new} for entry, (old, new) in PAGE_RANGE_CORRECTIONS.items()
    },
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
