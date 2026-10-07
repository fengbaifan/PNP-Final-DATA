#!/usr/bin/env python3
"""Classify the printed p.459 left-column index entries, preserving source OCR."""

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
INDEX_L = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "L.csv"
INDEX_M = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "M.csv"
TAXONOMY = ROOT / "01-domain" / "taxonomy-registry.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1822-1876"
SEGMENT_SHA = "bbb774c7bbdae9ee75442754360126239d6bcccefb8738a8e5ebe500a01c6159"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p459-left-l1822-1876-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_L: "c32c7a0f784b88625ea5635deaccb0e2734b629e051edacccc6f0d222aa30db1",
    INDEX_M: "4443a44bdbbce2e0ad3b758e8853b026e79edfba4d06b742ddd3043c0e215b4c",
    TAXONOMY: "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
    ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md": "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
    ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md": "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md": "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "7c9f907f84978ca8c64830540ac46156fd9c814c231dca70252cb0c3151a7a21",
    TABLES / "s2-coverage.csv": "3016e99a6f3d3d4ce465a353683c288ac403511cf43afe8d493b41d3c890c590",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ENTRY = {
    **{f"L.csv#{i}": "person" for i in (106, 107, 110, 113, 114, 117, 118, 120)},
    **{f"L.csv#{i}": "place" for i in (108, 112, 115, 116, 119)},
    "L.csv#109": "work",
    "L.csv#111": "archive",
    **{f"M.csv#{i}": "person" for i in (0, 1, 3, 4, 5, 8, 9, 14, 23, 24, 25, 26, 29, 30, 31, 32)},
    **{f"M.csv#{i}": "place" for i in (12, 13, 17, 18, 19, 20, 21, 22)},
    **{f"M.csv#{i}": "work" for i in (6, 7, 15, 16, 28)},
    **{f"M.csv#{i}": "archive" for i in (2, 10, 11, 27)},
}

PAGE_RANGE_CORRECTIONS = {
    "L.csv#118": ("231, 194", "23n, 194"),
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
segment_text = "\n".join(source_lines[1821:1876])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.459 left-column segment changed")

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
    segment.get("release_excluded"),
) != (SOURCE_FILE, 1822, 1876, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.459 left-column manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
l_fields, l_rows = read_csv(INDEX_L)
m_fields, m_rows = read_csv(INDEX_M)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(l_rows), len(m_rows), len(mentions), len(statements)) != (11436, 832, 121, 262, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

expected_entries = {f"L.csv#{i}" for i in range(106, 121)} | {f"M.csv#{i}" for i in range(33)}
if len(expected_entries) != 48 or set(TYPE_BY_INDEX_ENTRY) != expected_entries:
    raise SystemExit("type map does not cover exactly the 48 p.459 left-column entries")

all_by_entry = {}
for row in candidates:
    entry = row["index_entry_id"]
    if entry:
        all_by_entry.setdefault(entry, []).append(row)
scope_rows = [row for row in candidates if row["index_entry_id"] in expected_entries]
if len(scope_rows) != 48 or any(len(all_by_entry.get(entry, [])) != 1 for entry in expected_entries):
    raise SystemExit("p.459 left-column candidate mapping is incomplete or duplicated")
by_entry = {entry: all_by_entry[entry][0] for entry in expected_entries}

index_rows_by_file = {"L.csv": l_rows, "M.csv": m_rows}
for entry, candidate in by_entry.items():
    filename, row_number = entry.split("#")
    index_row = index_rows_by_file[filename][int(row_number)]
    expected_id = 1448 + int(row_number) - 106 if filename == "L.csv" else 1463 + int(row_number)
    if candidate["candidate_id"] != f"cand-{expected_id}":
        raise SystemExit(f"unexpected candidate ID for {entry}: {candidate['candidate_id']}")
    if candidate["index_source_file"] != filename:
        raise SystemExit(f"unexpected index source file for {entry}")
    for candidate_field, index_field in (("canonical_name", "Main Entry"), ("sub_entry", "Sub-entry"), ("detail", "Detail")):
        if candidate[candidate_field] != index_row[index_field]:
            raise SystemExit(f"candidate/index transcription mismatch for {entry}: {candidate_field}")
    expected_pages = PAGE_RANGE_CORRECTIONS[entry][0] if entry in PAGE_RANGE_CORRECTIONS else index_row["Page Numbers"]
    if candidate["index_page_range"] != expected_pages:
        raise SystemExit(f"candidate page-range pre-state changed for {entry}: {candidate['index_page_range']!r}")
    if candidate["status"] != "open" or candidate["suggested_type"]:
        raise SystemExit(f"candidate is not open/untyped: {entry}")

if (l_rows[118]["Main Entry"], l_rows[118]["Page Numbers"]) != ("Luti, Benedetto", "231, 194"):
    raise SystemExit("unexpected original L.csv row for Benedetto Luti")

by_candidate_id = {row["candidate_id"]: row for row in candidates}
body_plan = by_candidate_id.get("cand-9006")
if not body_plan or (
    body_plan["suggested_type"],
    body_plan["status"],
    body_plan["candidate_origin"],
    body_plan["candidate_source_ref"],
) != ("work", "open", "body-mention", "chp-10:10_CHP-10_intro:l206-216#L212"):
    raise SystemExit("existing body-level Van Dyck engraving plan candidate changed")

for entry, entity_type in TYPE_BY_INDEX_ENTRY.items():
    by_entry[entry]["suggested_type"] = entity_type
for entry, (old, new) in PAGE_RANGE_CORRECTIONS.items():
    by_entry[entry]["index_page_range"] = new

typed_counts = Counter(by_entry[entry]["suggested_type"] for entry in expected_entries)
expected_types = Counter({"person": 24, "place": 13, "work": 6, "archive": 5})
if typed_counts != expected_types:
    raise SystemExit(f"unexpected p.459 left-column type counts: {typed_counts}")

coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1819-1820")
previous_right = coverage_by_id.get("chp-22:22_CHP-22Index:l1763-1817")
next_right = coverage_by_id.get("chp-22:22_CHP-22Index:l1878-1931")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.459 left-column segment is not queued")
for previous in (previous_marker, previous_right):
    if not previous or previous["migration_status"] != "complete":
        raise SystemExit("preceding p.459 marker or p.458 right-column segment is not complete")
if not next_right or (next_right["disposition"], next_right["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.459 right-column segment is not queued")

target.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1822-1876",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.17 visibly prints p.459; S0 L1822-1875 "
        "contains the complete left-column entries L.csv#106-120 and M.csv#0-32 (48 open candidates). Types: 24 person, "
        "13 place, 6 work, 5 archive. Named cities, palaces and churches remain places; the St Peter's facade and "
        "identified architectural/design projects are works. McSwiny's p.287 plan for Van Dyck portrait engravings is "
        "typed work as an identifiable proposed design/series, matching the existing body candidate cand-9006; the book "
        "says this project came to nothing, so no execution is asserted. The McSwiny series of commemorative paintings "
        "and Maggiotto's Good Inclinations are works; Prince, To the Ladies and Gentlemen of Taste, Tombeaux des Princes, "
        "Il Gran Teatro delle Pitture e Prospettive di Venezia and Considerazioni elettriche are documents (archive). "
        "Index subentries about artists, patronage or work at a building do not create formal relations. Page-image "
        "correction is candidate-only: L.csv#118 Benedetto Luti p.231 -> p.23n; original S0 OCR and L.csv remain unchanged. "
        "Index navigation creates no mentions, book statements or relations."
    ),
)

after = {
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
    "index_open_untyped": sum(bool(item["index_entry_id"]) and item["status"] == "open" and not item["suggested_type"] for item in candidates),
}
expected_after = {
    "coverage_complete": 648,
    "coverage_queued": 45,
    "coverage_excluded": 139,
    "coverage_partial": 0,
    "index_open_untyped": 1380,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 459,
    "pdf_physical_page": 17,
    "classified_candidates": len(TYPE_BY_INDEX_ENTRY),
    "type_counts": dict(typed_counts),
    "candidate_only_corrections": {
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
