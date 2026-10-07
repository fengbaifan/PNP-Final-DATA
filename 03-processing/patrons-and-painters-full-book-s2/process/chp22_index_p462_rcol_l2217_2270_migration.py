#!/usr/bin/env python3
"""Classify p.462 right-column index entries and type its cited theatre venue."""

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
INDEX_O = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "O.csv"
INDEX_P = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv"
SEGMENT_ID = "chp-22:22_CHP-22Index:l2217-2270"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BODY_THEATRE_CANDIDATE = "cand-6545"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p462-right-l2217-2270-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/O.csv": "604778b1341dc2b32954bf1b1861f73207a7f0e996d5e85c672c462a536c6759",
    "02-sources/03-Index/03-2-Index-CSV/P.csv": "98c13c7d1d21dea3fd8008e6504d4ba1f30a2da6532a9e2ff52c2fab17e0d792",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/02_CHP-2_sec_iv.md": "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
    "02-sources/02-Markdown/03_CHP-3_sec_ii.md": "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    "02-sources/02-Markdown/06_CHP-6_sec_v.md": "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    "02-sources/02-Markdown/14_CHP-14_intro.md": "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7",
    "02-sources/02-Markdown/15_CHP-15_sec_ii.md": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "a168b78b16bd0d1f8524f4e4b48e4445c36f7baaa2be2b3cefb2393084643d94",
    "04-knowledge/tables/s2-coverage.csv": "f0bc3323b328fc1397be502dcbddcbebf010252dba3e72a40491064f519035e9",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"O.csv#{i}": "person" for i in (12, 13, 15, 19, 20, 22, 24, 25, 27, 28, 29, 30, 33, 35, 36)},
    **{f"O.csv#{i}": "institution" for i in (16, 17)},
    **{f"O.csv#{i}": "place" for i in (18, 34)},
    **{f"O.csv#{i}": "term" for i in (14, 31, 32)},
    "O.csv#21": "work",
    "O.csv#26": "archive",
    **{f"P.csv#{i}": "person" for i in (0, 6, 8, 9, 10, 11, 12)},
    **{f"P.csv#{i}": "place" for i in (2, 3, 5, 7)},
    "P.csv#4": "term",
}
EXCLUDED_ENTRIES = {"O.csv#23", "P.csv#1"}
EXPECTED_ENTRIES = {f"O.csv#{i}" for i in range(12, 37)} | {f"P.csv#{i}" for i in range(13)}


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
parser.add_argument("--apply", action="store_true", help="write reviewed candidate types and coverage")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2216:2270])
segment_hash = hashlib.sha256(segment_text.encode("utf-8")).hexdigest()
if "Olivieri, Monsignor" not in segment_text or "Paltronieri, Pietro" not in segment_text:
    raise SystemExit("p.462 right-column boundary/content check failed")
if "Olivarez, Count Duke" in segment_text:
    raise SystemExit("adjacent-column or following-page entries leaked into this segment")

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
    segment.get("source_file"), segment.get("line_start"), segment.get("line_end"), segment.get("sha256"),
    segment.get("asset_sha256"), segment.get("release_excluded"),
) != (SOURCE_FILE, 2217, 2270, segment_hash, EXPECTED_HASHES[SOURCE_FILE], True):
    raise SystemExit("p.462 right-column manifest mismatch")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 38:
    raise SystemExit("p.462 right-column index candidate mapping is incomplete")
for entry_id in EXCLUDED_ENTRIES:
    if candidate_by_entry[entry_id]["status"] != "excluded":
        raise SystemExit(f"pre-excluded see-under state changed: {entry_id}")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")

body_candidate = candidate_by_id.get(BODY_THEATRE_CANDIDATE)
if not body_candidate or (
    body_candidate["canonical_name"], body_candidate["status"], body_candidate["suggested_type"],
    body_candidate["candidate_origin"], body_candidate["candidate_source_ref"],
) != (
    "Ottoboni’s theatre in the Cancelleria (formal venue name unspecified)", "open", "", "body-mention",
    "chp-6:06_CHP-6_sec_v:l28-33#L30",
):
    raise SystemExit("Ottoboni theatre body-candidate pre-state changed")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
target = coverage_by_segment.get(SEGMENT_ID)
if not target or (target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.462 right-column coverage is not queued/pending")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
body_candidate["suggested_type"] = "place"
target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2217-2270",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.20 visibly "
        "prints p.462; S0 L2217 is the running header and the right column covers O.csv#12-36 and "
        "P.csv#0-12 (38 entries), ending with the p.462 right column's Pamfili entries. Thirty-six "
        "open candidates receive types: 22 person, "
        "6 place, 2 institution, 4 term, 1 work and 1 archive. O#14 Opera in Rome, O#31 effect of "
        "patronage and O#32 failure to attract painters are topical concepts/patterns, not individual "
        "events or works; O#16-17 Oratorians are institutions; O#18 Oratorio and O#34 the Cancelleria "
        "theatre are places; O#21 Daphnis and Chloe illustrations are work; O#26 Osservatore Veneto "
        "is a periodical archive. P#2-3, #5 and #7 are places; P#4 painting's social significance is "
        "a term. O#33 patronage of Trevisani remains person context and creates no formal relation. "
        "Two pre-excluded see-under aliases O#23 and P#1 remain excluded. The corresponding body "
        "candidate cand-6545 is typed place from the same p.164-165 venue evidence; no candidate "
        "identity merge is asserted. Index navigation creates no mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "excluded_aliases": sorted(EXCLUDED_ENTRIES),
    "added_types": dict(sorted(counts.items())),
    "supplemental_body_candidate_type": {BODY_THEATRE_CANDIDATE: "place"},
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
