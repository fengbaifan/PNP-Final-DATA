#!/usr/bin/env python3
"""Classify p.464 left-column index entries and exclude its generated page marker."""

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
INDEX_P = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
MARKER_ID = "chp-22:22_CHP-22Index:l2387-2387"
LEFT_ID = "chp-22:22_CHP-22Index:l2389-2444"
PIOLA_CANDIDATE = "cand-1936"
PITTERI_CANDIDATE = "cand-1948"
PITTONI_CANDIDATE = "cand-1950"
PIOLA_DETAIL_BEFORE = "Danita"
PITTERI_RANGE_BEFORE = "260, 312, 222n"
PITTERI_RANGE_AFTER = "260, 312, 335n"
PITTONI_RANGE_BEFORE = "214, 260n, 288, 296, 297, 315n, 345, 351, 361, 374"
PITTONI_RANGE_AFTER = "214, 260n, 288, 296, 297, 315, 345, 351, 361, 374"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p464-left-l2387-2444-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/P.csv": "98c13c7d1d21dea3fd8008e6504d4ba1f30a2da6532a9e2ff52c2fab17e0d792",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    "02-sources/02-Markdown/09_CHP-9_sec_ii.md": "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "02-sources/02-Markdown/14_CHP-14_intro.md": "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "9b6ea6c51ec1987779aa95ba2e76f306b53fdbfe5b5cc68d6648228bb85dec3e",
    "04-knowledge/tables/s2-coverage.csv": "023911c15321a319adc26d09174f861a33aa500ee99ad6cd53996ffa8cfd0a31",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"P.csv#{i}": "work" for i in (115, 116, 117, 118, 119, 121, 122, 123, 124, 125, 137, 152, 154, 155, 156, 157, 158, 159, 160)},
    **{f"P.csv#{i}": "person" for i in (*range(120, 121), *range(126, 137), 138, 139, 141, 142, 143, 148, 149, 151, 153, 161, 163)},
    **{f"P.csv#{i}": "place" for i in (147, 150)},
    **{f"P.csv#{i}": "event" for i in (140, 144, 145)},
    **{f"P.csv#{i}": "archive" for i in (146, 162)},
}
EXPECTED_ENTRIES = {f"P.csv#{i}" for i in range(115, 164)}
SEGMENTS = {
    MARKER_ID: (2387, 2387, "e3fb49fcbac2f3391293ccbc4d283ba9f9d2bfc9770adf404f2ef17a6e87166b"),
    LEFT_ID: (2389, 2444, "8dbc64cc34f9e254fb245748aaeb816ba703e21e51f68dfeefdf97d5c1d83f28"),
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
parser.add_argument("--apply", action="store_true", help="write reviewed index types, corrections and coverage")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
for segment_id, (start, end, expected_segment_hash) in SEGMENTS.items():
    segment_text = "\n".join(source_lines[start - 1:end])
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != expected_segment_hash:
        raise SystemExit(f"source segment changed: {segment_id}")
if "[Page 464]" not in source_lines[2386] or "Plutarch, 143" not in source_lines[2443]:
    raise SystemExit("p.464 marker/left-column source boundary check failed")
left_text = "\n".join(source_lines[2388:2444])
if not all(token in left_text for token in ("Judith with the Head of Holofernes", "Vanità, 195", "Pisa, Treaty of", "Institutiones Chirurgicae")):
    raise SystemExit("p.464 left-column content check failed")
if "Po, Giacomo del" in left_text or "[Page 465]" in left_text:
    raise SystemExit("p.464 right-column or next-page content leaked into the left-column segment")

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
        raise SystemExit(f"p.464 manifest mismatch: {segment_id}")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 49:
    raise SystemExit("p.464 left-column index candidate mapping is incomplete")
for entry_id, entity_type in TYPE_BY_ENTRY.items():
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")

corrections = [
    (PIOLA_CANDIDATE, "P.csv#137", "sub_entry", PIOLA_DETAIL_BEFORE, "Vanità"),
    (PITTERI_CANDIDATE, "P.csv#149", "index_page_range", PITTERI_RANGE_BEFORE, PITTERI_RANGE_AFTER),
    (PITTONI_CANDIDATE, "P.csv#151", "index_page_range", PITTONI_RANGE_BEFORE, PITTONI_RANGE_AFTER),
]
for candidate_id, entry_id, field, before, after in corrections:
    row = candidate_by_id.get(candidate_id)
    if not row or row["index_entry_id"] != entry_id or row[field] != before or row["status"] != "open":
        raise SystemExit(f"derived candidate correction pre-state changed: {candidate_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
for segment_id in SEGMENTS:
    row = coverage_by_segment.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
        "queued", "pending", "", ""
    ):
        raise SystemExit(f"p.464 coverage is not queued/pending: {segment_id}")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for candidate_id, _entry_id, field, _before, after in corrections:
    candidate_by_id[candidate_id][field] = after

coverage_by_segment[MARKER_ID].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2387-2387",
    "note": "no_semantic_content: S0 L2387 [Page 464] is a generated page marker, confirmed on CHP-22Index.pdf physical p.22; it is navigation only.",
})
coverage_by_segment[LEFT_ID].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2389-2444",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.22 prints p.464; "
        "the left column contains P.csv#115-163 (49 entries), ending at Plutarch, before the right column starts at Po. "
        "Types: 23 person, 19 work, 2 place, 3 event and 2 archive. The Piazzetta picture titles and Pittoni's "
        "paintings/monument series are works; P#120 prices and P#153 German patrons remain person-context entries, "
        "consistent with other artist index subentries, and do not create a term, unnamed group identity or formal relation. "
        "P#144 arrest and P#145 election are events; P#146 poems and pamphlets are textual works/archive material. "
        "P#137 is printed Vanita with accent (S0 reads Vanità) and is corrected from P.csv's Danita only in the derived "
        "candidate. P#149 printed locator is 335n, correcting P.csv/candidate 222n; P#151 printed locator is 315, "
        "correcting P.csv/candidate 315n. P#139's printed 358 agrees with the derived candidate despite OCR noise in S0. "
        "P.csv and S0 remain unchanged. Index navigation creates no mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segments": {key: {"source_lines": [SEGMENTS[key][0], SEGMENTS[key][1]], "disposition": coverage_by_segment[key]["disposition"]} for key in SEGMENTS},
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "added_types": dict(sorted(counts.items())),
    "candidate_corrections": [
        {"candidate_id": candidate_id, "index_entry_id": entry_id, "field": field, "before": before, "after": after}
        for candidate_id, entry_id, field, before, after in corrections
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
