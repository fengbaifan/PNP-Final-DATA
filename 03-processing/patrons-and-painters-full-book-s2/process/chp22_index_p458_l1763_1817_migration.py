#!/usr/bin/env python3
"""Classify the printed p.458 right-column index entries, preserving source OCR."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l1763-1817"
SEGMENT_SHA = "ffa0c0e05974b9f104b814285e2bc0affd92883f6ed02ef2434be0cb177450bc"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p458-right-l1763-1817-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_CSV: "c32c7a0f784b88625ea5635deaccb0e2734b629e051edacccc6f0d222aa30db1",
    TAXONOMY: "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md": "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    ROOT / "02-sources/02-Markdown/15_CHP-15.md": "812ce8d49fe086bb9a16efbb446a5d533a7c26edc1a353af31194654f33f2489",
    ROOT / "02-sources/02-Markdown/19_CHP-19Appendix.md": "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "a6fd52a84167f96603d09724ee63f950b4f7182836204cab595d9d9ab0ec48e3",
    TABLES / "s2-coverage.csv": "a66d7005f0fc5bc4f18aa797617f02719231cac2484e5b58445dda1b4fc9a988",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ENTRY = {
    **{f"L.csv#{i}": "person" for i in (57, 58, 62, 65, 66, 67, 68, 69, 73, 75, 80, 81, 84, 85, 86, 87, 89, 90, 92, 93, 94, 95, 96, 97, 99, 100, 101, 104, 105)},
    **{f"L.csv#{i}": "work" for i in (59, 74, 82, 83, 88, 91, 102)},
    **{f"L.csv#{i}": "archive" for i in (61, 70, 71)},
    **{f"L.csv#{i}": "term" for i in (60, 72, 77, 78)},
    **{f"L.csv#{i}": "place" for i in (64, 79)},
    "L.csv#63": "family",
    "L.csv#76": "institution",
}

PAGE_RANGE_CORRECTIONS = {
    "L.csv#62": (
        "169, 194, 195, 234n, 345",
        "169, 194, 195, 341n, 345",
    ),
    "L.csv#68": (
        "300, 301, 320, 321, 322, 323, 337, 338, 340, 350, 361, 362, 370, 373, 381, 408",
        "300, 301, 320, 321, 322, 323, 337, 338, 340, 350, 361, 362, 370, 373, 384, 408",
    ),
    "L.csv#105": (
        "118, 153, 155, 182, 186, 187, 188, 189, 195, 284, 285, 402, 403",
        "118, 153, 155, 182, 186, 187, 188, 189, 196, 284, 285, 402, 403",
    ),
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
segment_text = "\n".join(source_lines[1762:1817])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.458 right-column segment changed")

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
) != (SOURCE_FILE, 1763, 1817, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 p.458 right-column manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
index_rows = read_csv(INDEX_CSV)[1]
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(index_rows), len(mentions), len(statements)) != (11436, 832, 121, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

by_entry = {row["index_entry_id"]: row for row in candidates if row["index_entry_id"]}
expected_entries = {f"L.csv#{i}" for i in range(57, 106)}
if len(expected_entries) != 49 or set(by_entry) & expected_entries != expected_entries:
    raise SystemExit("p.458 right-column candidate mapping is incomplete or duplicated")
scope = [by_entry[entry] for entry in expected_entries]
scope_rows = [row for row in candidates if row["index_entry_id"] in expected_entries]
if len(scope_rows) != 49 or any(row["index_source_file"] != "L.csv" for row in scope):
    raise SystemExit("p.458 right-column candidate source mapping changed")
if set(TYPE_BY_INDEX_ENTRY) != expected_entries - {"L.csv#98", "L.csv#103"}:
    raise SystemExit("type map does not cover exactly the 47 untyped open entries")

index_by_entry = {f"L.csv#{i}": row for i, row in enumerate(index_rows)}
if index_by_entry["L.csv#59"]["Sub-entry"] != "Rood, The":
    raise SystemExit("unexpected S1 OCR value for L.csv#59")
if index_by_entry["L.csv#62"]["Page Numbers"] != "169, 194, 195, 234n, 345":
    raise SystemExit("unexpected S1 page locator for L.csv#62")
if "381" not in index_by_entry["L.csv#68"]["Page Numbers"].split(", "):
    raise SystemExit("unexpected S1 page locator for L.csv#68")
if "195" not in index_by_entry["L.csv#105"]["Page Numbers"].split(", "):
    raise SystemExit("unexpected S1 page locator for L.csv#105")
if by_entry["L.csv#98"]["status"] != "excluded":
    raise SystemExit("Claude Lorrain see-under alias is no longer excluded")
if (by_entry["L.csv#103"]["status"], by_entry["L.csv#103"]["suggested_type"]) != ("open", "work"):
    raise SystemExit("pre-existing Lot and his Daughters work classification changed")
for entry in TYPE_BY_INDEX_ENTRY:
    row = by_entry[entry]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"candidate is not in expected open/untyped state: {entry}")

for entry, (old, new) in PAGE_RANGE_CORRECTIONS.items():
    if by_entry[entry]["index_page_range"] != old:
        raise SystemExit(f"unexpected candidate page range for {entry}: {by_entry[entry]['index_page_range']!r}")
    by_entry[entry]["index_page_range"] = new

if by_entry["L.csv#59"]["sub_entry"] != "Rood, The":
    raise SystemExit("unexpected candidate OCR value for L.csv#59")
by_entry["L.csv#59"]["sub_entry"] = "Flood, The"

for entry, entity_type in TYPE_BY_INDEX_ENTRY.items():
    by_entry[entry]["suggested_type"] = entity_type

typed_counts = Counter(by_entry[entry]["suggested_type"] for entry in expected_entries if entry != "L.csv#98")
expected_types = Counter({"person": 29, "work": 8, "archive": 3, "term": 4, "place": 2, "family": 1, "institution": 1})
if typed_counts != expected_types:
    raise SystemExit(f"unexpected p.458 right-column type counts: {typed_counts}")

coverage_by_id = {row["segment_id"]: row for row in coverage}
target = coverage_by_id.get(SEGMENT_ID)
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1705-1705")
previous_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1707-1761")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.458 right-column segment is not queued")
for previous in (previous_marker, previous_left):
    if not previous or previous["migration_status"] != "complete":
        raise SystemExit("p.458 marker or left-column segment is not complete")

target.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1763-1817",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.16 visibly prints p.458. S0 L1763-1817 "
        "contains the complete right-column entries L.csv#57-105 (49 rows): 48 open candidates, including 47 newly "
        "typed as 29 person, 8 work (one pre-existing), 3 archive, 4 term, 2 place, 1 family and 1 institution; "
        "L.csv#98 Claude Lorrain remains the excluded see-under alias. p.217 identifies The Flood as Liberi's "
        "canvas and records the contract for the S. Maria Maggiore commission; p.265 identifies Longhi's Fall of "
        "the Giants fresco. Lodoli's private school is a specific teaching institution; Apologhi and Elementi are "
        "documents (archive), while his educational ideas and views on architecture/painting are terms. Portraits "
        "and the specifically described Longhi paintings are works; the page 393 auction description 'two "
        "conversations, Mr Murray and family' remains uncertain in attribution as the book states. Unspecified "
        "paintings in Teodoro Correr's collection and 'and' subentries remain person context; index navigation "
        "creates no formal relations, mentions or book statements. Page-image corrections are candidate-only: "
        "L.csv#59 'Rood, The' -> 'Flood, The'; #62 234n -> 341n; #68 381 -> 384; #105 195 -> 196. Original S0 "
        "and L.csv are unchanged."
    ),
)

after = {
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
}
expected_after = {"coverage_complete": 647, "coverage_queued": 47, "coverage_excluded": 138, "coverage_partial": 0}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 458,
    "pdf_physical_page": 16,
    "newly_typed_candidates": len(TYPE_BY_INDEX_ENTRY),
    "type_counts_including_preexisting": dict(typed_counts),
    "candidate_only_corrections": {
        entry: {"from": old, "to": new} for entry, (old, new) in PAGE_RANGE_CORRECTIONS.items()
    } | {"L.csv#59.sub_entry": {"from": "Rood, The", "to": "Flood, The"}},
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
