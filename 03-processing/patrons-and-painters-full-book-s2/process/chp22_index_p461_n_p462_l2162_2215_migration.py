#!/usr/bin/env python3
"""Backfill p.461 N entries and classify the p.462 left-column index segment."""

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
INDEX_N = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "N.csv"
INDEX_O = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "O.csv"
SEGMENT_461 = "chp-22:22_CHP-22Index:l2105-2158"
SEGMENT_462 = "chp-22:22_CHP-22Index:l2162-2215"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p461-n-p462-left-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/N.csv": "416676c4b08a0bee46db109993290d4467ac1dd57fbc038d536248ac9d07095b",
    "02-sources/03-Index/03-2-Index-CSV/O.csv": "604778b1341dc2b32954bf1b1861f73207a7f0e996d5e85c672c462a536c6759",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/03_CHP-3_sec_iv.md": "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    "02-sources/02-Markdown/08_CHP-8_sec_i.md": "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "eb3c215a5d8ff479d006c17b10f128fef6903c72a686bfa05c3d145cd9c88f76",
    "04-knowledge/tables/s2-coverage.csv": "5b03fb837a97be3ea7ac51899fa72b4eb88c816d64a159b5212d187edf1a4fd9",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

P461_N_TYPES = {
    "N.csv#0": "person",
    "N.csv#1": "place",
    "N.csv#2": "term",
    "N.csv#4": "person",
    "N.csv#5": "term",
    "N.csv#6": "person",
    "N.csv#7": "person",
    "N.csv#8": "work",
    "N.csv#9": "term",
}
P462_TYPES = {
    **{f"N.csv#{i}": "person" for i in (10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 28, 29, 32, 34, 35, 36, 37, 38, 43, 44, 45)},
    **{f"N.csv#{i}": "work" for i in (24, 25, 26, 30, 31, 33, 39, 40, 41, 42)},
    "N.csv#13": "place",
    "N.csv#14": "term",
    "N.csv#27": "term",
    **{f"O.csv#{i}": "person" for i in (0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11)},
    "O.csv#4": "archive",
}
P462_ENTRIES = {f"N.csv#{i}" for i in range(10, 46)} | {f"O.csv#{i}" for i in range(12)}


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
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write reviewed candidate and coverage changes")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    path = ROOT / relative
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segments_to_check = {
    SEGMENT_461: (2105, 2158, "Nadal, Jerome", "Neapolitan painting, diffusion of"),
    SEGMENT_462: (2162, 2215, "Negri, Paolo", "Olivarez, Count Duke"),
}
segment_hashes = {}
for segment_id, (start, end, first, last) in segments_to_check.items():
    text = "\n".join(source_lines[start - 1:end])
    if first not in text or last not in text:
        raise SystemExit(f"S0 segment boundary/content check failed: {segment_id}")
    segment_hashes[segment_id] = hashlib.sha256(text.encode("utf-8")).hexdigest()
if "Olivieri" in "\n".join(source_lines[2161:2215]):
    raise SystemExit("p.462 right-column entries leaked into the left-column segment")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
for segment_id, (start, end, _, _) in segments_to_check.items():
    row = manifest.get(segment_id)
    if not row or (
        row.get("source_file"), row.get("line_start"), row.get("line_end"), row.get("sha256"),
        row.get("asset_sha256"), row.get("release_excluded"),
    ) != (SOURCE_FILE, start, end, segment_hashes[segment_id], EXPECTED_HASHES[SOURCE_FILE], True):
        raise SystemExit(f"S0 manifest mismatch: {segment_id}")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
if len(candidates) != 11436 or len(coverage) != 832:
    raise SystemExit("unexpected S2 table dimensions")

candidate_by_entry = {}
for row in candidates:
    entry_id = row.get("index_entry_id", "")
    if entry_id in P461_N_TYPES or entry_id in P462_ENTRIES or entry_id == "N.csv#3":
        if entry_id in candidate_by_entry:
            raise SystemExit(f"duplicate candidate mapping: {entry_id}")
        candidate_by_entry[entry_id] = row
expected_entries = set(P461_N_TYPES) | P462_ENTRIES | {"N.csv#3"}
if set(candidate_by_entry) != expected_entries:
    raise SystemExit("p.461/p.462 candidate mapping is incomplete or contains extra entries")
if candidate_by_entry["N.csv#3"]["status"] != "excluded":
    raise SystemExit("N.csv#3 cross-reference must remain excluded")
for entry_id in set(P461_N_TYPES) | P462_ENTRIES:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state for {entry_id}")

corrections = {
    "N.csv#14": {"index_page_range": ("4, 31, 147, 154n, 161", "4, 31, 147, 154, 161")},
    "N.csv#34": {"canonical_name": ("Nordiall, John", "Northall, John")},
    "N.csv#35": {"canonical_name": ("Novaroli, P. Octavio", "Novaroli, P. Ottavio")},
    "O.csv#4": {"sub_entry": ("Uccelliera", "Uccelleria")},
}
for entry_id, fields in corrections.items():
    row = candidate_by_entry[entry_id]
    for field, (before, _) in fields.items():
        if row[field] != before:
            raise SystemExit(f"unexpected candidate correction pre-state: {entry_id}.{field}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
p461 = coverage_by_segment.get(SEGMENT_461)
if not p461 or (p461["disposition"], p461["migration_status"], p461["source_line_ranges"]) != (
    "reviewed", "complete", "L2105-2158"
):
    raise SystemExit("p.461 right-column coverage state changed")
p462 = coverage_by_segment.get(SEGMENT_462)
if not p462 or (p462["disposition"], p462["migration_status"], p462["source_line_ranges"], p462["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.462 left-column coverage is not queued/pending")

for entry_id, entity_type in {**P461_N_TYPES, **P462_TYPES}.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for entry_id, fields in corrections.items():
    for field, (_, corrected) in fields.items():
        candidate_by_entry[entry_id][field] = corrected

p461["note"] += (
    " Supplemental scope check: S0 L2148-2158 also contains N.csv#0-9; the prior migration covered "
    "only M.csv#224-261. N#3 remains the pre-excluded see-under alias; the other nine candidates are "
    "typed here (4 person, 1 place, 3 term, 1 work). The corrected segment total is 48 index records "
    "across M#224-261 and N#0-9, with 46 typed and two pre-excluded aliases."
)
p462.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2162-2215",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.20 visibly "
        "prints p.462; the left column covers N.csv#10-45 and O.csv#0-11 (48 entries), ending at "
        "Olivarez; the right column begins with O.csv#12 Olivieri and is outside this segment. Types: "
        "34 person, 10 work, 1 place, 2 term and 1 archive. N#13 chapel of St Francis Xavier is a "
        "place; N#14 Nepotism in Rome and N#27 teste di fantasia are terms; N#24-26, #30-31, #33 and "
        "#39-42 are works; O#4 Uccelleria is Olina's cited 1622 book and is archive. Oliva's 'and' "
        "subentries retain person typing as index context; index navigation does not create relations. "
        "Print-checked candidate corrections: N#14 page 154n to 154; N#34 Nordiall to Northall; "
        "N#35 Octavio to Ottavio; O#4 sub-entry Uccelliera to Uccelleria. Original S0 and N/O CSVs "
        "remain unchanged. Index navigation creates no mentions, book statements or formal relations."
    ),
})

added_types = Counter({**P461_N_TYPES, **P462_TYPES}.values())
summary = {
    "segments": {
        SEGMENT_461: {"source_records": 48, "new_types": 9, "pre_excluded_aliases": 2},
        SEGMENT_462: {"source_records": 48, "new_types": 48, "pre_excluded_aliases": 0},
    },
    "added_types": dict(sorted(added_types.items())),
    "candidate_corrections": {
        entry_id: {field: after for field, (_, after) in fields.items()}
        for entry_id, fields in corrections.items()
    },
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
