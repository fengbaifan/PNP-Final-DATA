#!/usr/bin/env python3
"""Classify p.469 left-column index seeds and close its page marker."""

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
S_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "S.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
MARKER_ID = "chp-22:22_CHP-22Index:l2954-2954"
LEFT_ID = "chp-22:22_CHP-22Index:l2956-3010"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p469-left-l2954-3010-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/S.csv": "a73a199a0d4e2c01dfe12fd77e562e30298edb2357c54b341da887bad306393f",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    "02-sources/02-Markdown/09_CHP-9_sec_ii.md": "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    "02-sources/02-Markdown/05_CHP-5_sec_iii.md": "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a",
    "02-sources/02-Markdown/05_CHP-5_sec_i.md": "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "f1994fe74586ad5bd6f15100a9f6b6ed8ee595fb2647e0846f0e7f1b8b65d14f",
    "04-knowledge/tables/s2-coverage.csv": "94edf4a36cf0f8239d3bebbf20ad8bf9f4644a74f0f831b0ee617bc41d99fd37",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"S.csv#{i}": "person" for i in (
        78, 80, 81, 82, 83, 84, 85, 86, 87, 89, 90, 91, 92, 96, 102, 103,
        105, 106, 107, 108, 109, 110, 112, 113, 114, 115, 120, 121, 122, 123,
        125, 126,
    )},
    **{f"S.csv#{i}": "work" for i in (79, 94, 95, 97, 98, 100)},
    **{f"S.csv#{i}": "event" for i in (93, 99, 101, 116, 118)},
    "S.csv#88": "family",
    "S.csv#104": "institution",
    "S.csv#111": "procedure",
    "S.csv#117": "term",
    "S.csv#119": "archive",
}
PRESERVED_EXCLUSIONS = {
    "S.csv#124": ("cand-2928", "Sixtus V", "索引交叉引用：see under Peretti, Felice"),
}
CANDIDATE_NAME_CORRECTIONS = {
    "S.csv#111": ("Servizio particolare", "Servitù particolare"),
}
EXPECTED_ENTRIES = {f"S.csv#{i}" for i in range(78, 127)}
SEGMENTS = {
    MARKER_ID: (2954, 2954, "f60ec360b481c8519ed9cc3ebee9eccf757b9ed7ccaad63dec5e626b5118f08b"),
    LEFT_ID: (2956, 3010, "eeecbeec45a1d20ed50e238bcf48478b954f08e41706d7b161ac339dc7734b3f"),
}


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
parser.add_argument("--apply", action="store_true", help="write reviewed index types and S2 coverage")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
for segment_id, (start, end, expected_segment_hash) in SEGMENTS.items():
    segment_text = "\n".join(source_lines[start - 1:end])
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != expected_segment_hash:
        raise SystemExit(f"source segment changed: {segment_id}")
if "[Page 469]" not in source_lines[2953]:
    raise SystemExit("p.469 generated marker check failed")
left_text = "\n".join(source_lines[2955:3010])
if not all(token in left_text for token in (
    "Scaramuccia, Luigi", "Schulenburg, Marshal Johann Matthias", "Servitù particolare",
    "Shaftesbury, 3rd Earl of", "Second Characters", "Skippe, John",
)):
    raise SystemExit("p.469 left-column content check failed")
if "Skippon, Philip" in left_text or "Smith, Joseph" in left_text or "[Page 470]" in left_text:
    raise SystemExit("right-column or next-page content leaked into p.469 left-column scope")

s_fields, s_rows = read_csv(S_INDEX)
if len(s_rows) <= 126 or (s_rows[78]["Main Entry"], s_rows[126]["Main Entry"]) != (
    "Scaramuccia, Luigi", "Skippe, John",
):
    raise SystemExit("S.csv#78-126 boundary check failed")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
for segment_id, (start, end, expected_hash) in SEGMENTS.items():
    row = manifest.get(segment_id)
    if not row or (
        row.get("source_file"), row.get("line_start"), row.get("line_end"), row.get("sha256"),
        row.get("asset_sha256"), row.get("release_excluded"),
    ) != (SOURCE_FILE, start, end, expected_hash, EXPECTED_HASHES[SOURCE_FILE], True):
        raise SystemExit(f"p.469 manifest mismatch: {segment_id}")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
if len(candidates) != 11436 or len(coverage) != 832:
    raise SystemExit("unexpected S2 table dimensions")

candidate_by_entry = {}
for row in candidates:
    entry_id = row.get("index_entry_id", "")
    if entry_id in EXPECTED_ENTRIES:
        if entry_id in candidate_by_entry:
            raise SystemExit(f"duplicate candidate mapping: {entry_id}")
        candidate_by_entry[entry_id] = row
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 49:
    raise SystemExit("p.469 left-column candidate mapping is incomplete")
if len(TYPE_BY_ENTRY) != 48 or Counter(TYPE_BY_ENTRY.values()) != Counter({
    "person": 32, "work": 6, "event": 5, "family": 1,
    "institution": 1, "procedure": 1, "term": 1, "archive": 1,
}):
    raise SystemExit("p.469 left-column type disposition map is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
for entry_id, (candidate_id, canonical_name, exclude_reason) in PRESERVED_EXCLUSIONS.items():
    row = candidate_by_entry[entry_id]
    if (row["candidate_id"], row["canonical_name"], row["status"], row["exclude_reason"]) != (
        candidate_id, canonical_name, "excluded", exclude_reason,
    ):
        raise SystemExit(f"preserved see-under exclusion changed: {entry_id}")
for entry_id, (expected_name, corrected_name) in CANDIDATE_NAME_CORRECTIONS.items():
    row = candidate_by_entry[entry_id]
    if row["canonical_name"] != expected_name:
        raise SystemExit(f"unexpected candidate-name pre-state: {entry_id}")
    row["canonical_name"] = corrected_name

coverage_by_segment = {row["segment_id"]: row for row in coverage}
for segment_id in SEGMENTS:
    row = coverage_by_segment.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
        "queued", "pending", "", "",
    ):
        raise SystemExit(f"p.469 coverage is not queued/pending: {segment_id}")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type

coverage_by_segment[MARKER_ID].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2954-2954",
    "note": "no_semantic_content: S0 L2954 [Page 469] is a generated navigation marker, confirmed on CHP-22Index.pdf physical p.27; it is not an indexed object.",
})
coverage_by_segment[LEFT_ID].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2956-3010",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.27 prints p.469; the physical left column contains "
        "S.csv#78-126 (49 entries), from Scaramuccia, Luigi through Skippe, John. Types: 32 person, 6 work, 5 event, 1 family, 1 institution, "
        "1 procedure, 1 term and 1 archive; retain S#124 Sixtus V as its existing see-under exclusion. S#79 is Scaramuccia's dedicated print "
        "(p.124); Schulenburg's paintings and his battle records by Simonini are work, while the Corfu defense, Rota purchase and picture shipments "
        "are event candidates. S#88 Schönborn family is family; #104 Scuola Grande dei Carmini is an institution; #111 servitù particolare is "
        "the patron-artist service mechanism (procedure). Shaftesbury's artist instructions are commissioning acts, #117 civilising role is a term, "
        "#118 retirement is an event, and #119 Second Characters is a book/archive. Person links and 'and' subentries do not establish relations. "
        "Printed p.469 confirms S0 OCR readings #85 293n, #121 237n and #102 taste 'for'; S.csv and candidates already match those locators. "
        "S.csv#111 transcribes Servitù particolare as 'Servizio particolare'; the scan and chp.1 pp.6-8 support Servitù, so the candidate "
        "canonical name is corrected while S.csv and S0 remain unchanged. No locator correction was needed. Index navigation creates no mentions, "
        "book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segments": {
        key: {"source_lines": [SEGMENTS[key][0], SEGMENTS[key][1], SEGMENTS[key][2]], "disposition": coverage_by_segment[key]["disposition"]}
        for key in SEGMENTS
    },
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "preserved_exclusions": sorted(PRESERVED_EXCLUSIONS),
    "candidate_name_corrections": [
        {"entry_id": entry_id, "from": names[0], "to": names[1]}
        for entry_id, names in sorted(CANDIDATE_NAME_CORRECTIONS.items())
    ],
    "final_type_counts_in_segment": dict(sorted(counts.items())),
    "candidate_locator_corrections": [],
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
