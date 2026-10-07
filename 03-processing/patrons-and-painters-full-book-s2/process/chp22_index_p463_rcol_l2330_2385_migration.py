#!/usr/bin/env python3
"""Classify p.463 right-column index entries and correct the Piazzetta page range."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l2330-2385"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
PIAZZETTA_CANDIDATE = "cand-1901"
PIAZZETTA_INDEX_RANGE_BEFORE = (
    "262, 264, 265, 266, 268, 269n, 270, 271, 273, 288, 293, 304, 312, 315, 324, "
    "333, 337n, 340, 345, 351, 375, 376, 377n, 407"
)
PIAZZETTA_INDEX_RANGE_AFTER = (
    "262, 264, 265, 266, 268, 269n, 270, 271, 273, 288, 293, 304, 313, 315, 322, "
    "333, 337n, 340, 345, 351, 375, 376, 377n, 407"
)
CONTEXT_CANDIDATES = {
    "cand-5197": "place",  # Church of S. Andrea della Valle
    "cand-9990": "archive",  # the 1745 illustrated book
    "cand-9991": "work",  # Piazzetta's drawings for that book
}
BACKUP_SUFFIX = ".bak-s2-chp22-index-p463-right-l2330-2385-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/P.csv": "98c13c7d1d21dea3fd8008e6504d4ba1f30a2da6532a9e2ff52c2fab17e0d792",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/03_CHP-3_sec_ii.md": "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    "02-sources/02-Markdown/07_CHP-7_sec_v.md": "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "dc278fb835636a481b3acc8489fa2005152ccfde8c541a13113a26d27084f326",
    "04-knowledge/tables/s2-coverage.csv": "e3282f7bb1379f61027fb42b565750754a688151473c12e2a203cc3db0db7c22",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"P.csv#{i}": "person" for i in (*range(67, 73), *range(74, 78), *range(79, 81), *range(82, 87), *range(88, 90), *range(91, 94), *range(95, 98), *range(99, 105), 107)},
    **{f"P.csv#{i}": "place" for i in (73, 78, 87)},
    **{f"P.csv#{i}": "work" for i in (81, 90, 94, 98, 105, 106, *range(108, 115))},
}
EXPECTED_ENTRIES = {f"P.csv#{i}" for i in range(67, 115)}


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
segment_text = "\n".join(source_lines[2329:2385])
segment_hash = hashlib.sha256(segment_text.encode("utf-8")).hexdigest()
if not all(token in segment_text for token in ("work for Johann Wilhelm", "Pepoli palace", "illustrations for Gerusalemme Liberata")):
    raise SystemExit("p.463 right-column source boundary/content check failed")
if "[Page 464]" in segment_text or "Judith with the Head of Holofernes" in segment_text:
    raise SystemExit("the following page segment leaked into p.463 right-column scope")

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
) != (SOURCE_FILE, 2330, 2385, segment_hash, EXPECTED_HASHES[SOURCE_FILE], True):
    raise SystemExit("p.463 right-column manifest mismatch")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 48:
    raise SystemExit("p.463 right-column index candidate mapping is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")

for candidate_id, expected_type in CONTEXT_CANDIDATES.items():
    row = candidate_by_id.get(candidate_id)
    if not row or row["suggested_type"] != expected_type or row["status"] != "open":
        raise SystemExit(f"supporting S2 candidate changed: {candidate_id}")

page_candidate = candidate_by_id.get(PIAZZETTA_CANDIDATE)
if not page_candidate or (
    page_candidate["index_entry_id"], page_candidate["status"], page_candidate["suggested_type"],
    page_candidate["index_page_range"],
) != ("P.csv#102", "open", "", PIAZZETTA_INDEX_RANGE_BEFORE):
    raise SystemExit("Piazzetta candidate page-range pre-state changed")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
target = coverage_by_segment.get(SEGMENT_ID)
if not target or (target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.463 right-column coverage is not queued/pending")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
page_candidate["index_page_range"] = PIAZZETTA_INDEX_RANGE_AFTER
target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2330-2385",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.21 visibly "
        "prints p.463; S0 L2330-2331 'X 463' is footer/page-number noise, and the right column contains "
        "P.csv#67-114 (48 entries), ending with Piazzetta's Gerusalemme Liberata illustrations. Types: "
        "32 person, 3 place and 13 work. P#67-72 are Pellegrini's career/work contexts and remain person "
        "context; P#78 S. Andrea della Valle is a church/place, without inferring a formal edge to the "
        "Peretti-Montalto candidate. P#81 Apotheosis of Prince Eugene is Permoser's marble sculpture; "
        "P#90 portraits, P#94 Petrarch statue, P#98 Tacca equestrian statue, and P#105-106 and #108-114 "
        "are named or grouped visual works. P#103-104 and #107 remain person context, not formal edges. "
        "The printed p.463 index reads 313 and 322 in P#102 Piazzetta's page list; the derived candidate "
        "is corrected from P.csv's 312 and 324 while P.csv and S0 remain unchanged. P#114's illustration "
        "entry stays distinct from the 1745 book/archive candidate cand-9990 and the drawing/work candidate "
        "cand-9991; no identity alignment or relation is asserted. Index navigation creates no mentions, "
        "book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "added_types": dict(sorted(counts.items())),
    "page_correction": {
        "candidate_id": PIAZZETTA_CANDIDATE,
        "index_entry_id": "P.csv#102",
        "before": PIAZZETTA_INDEX_RANGE_BEFORE,
        "after": PIAZZETTA_INDEX_RANGE_AFTER,
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
