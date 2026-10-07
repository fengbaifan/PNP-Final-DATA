#!/usr/bin/env python3
"""Exclude the p.463 marker and classify p.463 left-column index candidates."""

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
MARKER_SEGMENT_ID = "chp-22:22_CHP-22Index:l2272-2272"
LEFT_SEGMENT_ID = "chp-22:22_CHP-22Index:l2274-2328"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
EXISTING_GALLERY_CANDIDATES = {"cand-8963": "place", "cand-8964": "work"}
BACKUP_SUFFIX = ".bak-s2-chp22-index-p463-marker-left-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/P.csv": "98c13c7d1d21dea3fd8008e6504d4ba1f30a2da6532a9e2ff52c2fab17e0d792",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
    "02-sources/02-Markdown/05_CHP-5_sec_i.md": "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "02-sources/02-Markdown/14_CHP-14_intro.md": "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "960020a651935d512e800c154125373afc98e666c5b687a7dcd11b9878fa6af2",
    "04-knowledge/tables/s2-coverage.csv": "f352c485cd7fe62e60a9ac86dc479adc92dbf4e17a342515dfa15f4e69dcea15",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"P.csv#{i}": "person" for i in (13, 14, 17, 18, 22, 24, 25, 26, 28, 34, 39, 41, 42, 43, 44, 45, 46, 53, 54, 56, 57, 58, 61, 62, 63, 64)},
    **{f"P.csv#{i}": "place" for i in (15, 16, 23, 35, 66)},
    **{f"P.csv#{i}": "institution" for i in (30, 37)},
    **{f"P.csv#{i}": "work" for i in (27, 29, 33, 40, 65)},
    **{f"P.csv#{i}": "archive" for i in (47, 48, 49, 51, 52)},
    **{f"P.csv#{i}": "term" for i in (19, 21, 31, 32, 50, 59)},
    **{f"P.csv#{i}": "event" for i in (20, 55)},
}
NEWLY_EXCLUDED = {"P.csv#36": "索引交叉引用：see also under French patronage"}
PRESERVED_EXCLUDED = {"P.csv#38", "P.csv#60"}
EXPECTED_ENTRIES = {f"P.csv#{i}" for i in range(13, 67)}


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
marker_text = "\n".join(source_lines[2271:2272])
left_text = "\n".join(source_lines[2273:2328])
marker_hash = hashlib.sha256(marker_text.encode("utf-8")).hexdigest()
left_hash = hashlib.sha256(left_text.encode("utf-8")).hexdigest()
if "[Page 463]" not in marker_text:
    raise SystemExit("p.463 marker source check failed")
if not all(token in left_text for token in ("conservative nature of patronage", "Mississippi Gallery of Banque Royale", "Pellegrini, Giovanni Antonio")):
    raise SystemExit("p.463 left-column source boundary/content check failed")
if "work for Johann Wilhelm" in left_text:
    raise SystemExit("the following right-column segment leaked into the p.463 left-column range")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
marker = manifest.get(MARKER_SEGMENT_ID)
left = manifest.get(LEFT_SEGMENT_ID)
if not marker or (
    marker.get("source_file"), marker.get("line_start"), marker.get("line_end"), marker.get("sha256"),
    marker.get("asset_sha256"), marker.get("release_excluded"),
) != (SOURCE_FILE, 2272, 2272, marker_hash, EXPECTED_HASHES[SOURCE_FILE], True):
    raise SystemExit("p.463 marker manifest mismatch")
if not left or (
    left.get("source_file"), left.get("line_start"), left.get("line_end"), left.get("sha256"),
    left.get("asset_sha256"), left.get("release_excluded"),
) != (SOURCE_FILE, 2274, 2328, left_hash, EXPECTED_HASHES[SOURCE_FILE], True):
    raise SystemExit("p.463 left-column manifest mismatch")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 54:
    raise SystemExit("p.463 left-column index candidate mapping is incomplete")
for entry_id in PRESERVED_EXCLUDED:
    row = candidate_by_entry[entry_id]
    if row["status"] != "excluded" or not row["exclude_reason"]:
        raise SystemExit(f"pre-excluded see-under state changed: {entry_id}")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
for entry_id in NEWLY_EXCLUDED:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"] or row["exclude_reason"]:
        raise SystemExit(f"unexpected see-also candidate pre-state: {entry_id}")

for candidate_id, expected_type in EXISTING_GALLERY_CANDIDATES.items():
    row = candidate_by_id.get(candidate_id)
    if not row or row["suggested_type"] != expected_type or row["status"] != "open":
        raise SystemExit(f"gallery body-candidate evidence changed: {candidate_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
marker_target = coverage_by_segment.get(MARKER_SEGMENT_ID)
left_target = coverage_by_segment.get(LEFT_SEGMENT_ID)
if not marker_target or (marker_target["disposition"], marker_target["migration_status"], marker_target["source_line_ranges"], marker_target["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.463 marker coverage is not queued/pending")
if not left_target or (left_target["disposition"], left_target["migration_status"], left_target["source_line_ranges"], left_target["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.463 left-column coverage is not queued/pending")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for entry_id, reason in NEWLY_EXCLUDED.items():
    candidate_by_entry[entry_id]["status"] = "excluded"
    candidate_by_entry[entry_id]["exclude_reason"] = reason

marker_target.update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2272-2272",
    "note": (
        "no_semantic_content: CHP-22Index.pdf physical p.21 visibly prints p.463; S0 L2272 '[Page 463]' "
        "is generated page navigation, not an index entry or book-fact claim. The one-line segment is "
        "excluded/complete with no candidate, mention, book statement or relation."
    ),
})
left_target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2274-2328",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.21 visibly "
        "prints p.463; the left column and P.csv#13-66 contain 54 entries through the Mississippi Gallery "
        "of Banque Royale. The OCR lines interleave right-column fragments; candidate scope was checked "
        "against the printed left column and the indexed P rows. Fifty-one open entries receive types: "
        "26 person, 5 place, 2 institution, 5 work, 5 archive, 6 term and 2 event. P#36 is a see-also "
        "navigation entry and is excluded; pre-excluded P#38 and P#60 remain excluded. P#19, #21, #31, "
        "#32, #50 and #59 are indexed topics/conditions, not standalone events; P#20 burial dispute and "
        "P#55 Peace of Passarowitz are events. P#45-46 retain Pasquali's person context and create no "
        "formal relation. Pasquali's cited illustrated books and editions are archives. P#27 Interior of "
        "the Pantheon is Pannini's painting. P#66 names the physical gallery (place); existing body "
        "candidates separately record that venue as cand-8963/place and Pellegrini's fresco programme "
        "as cand-8964/work, with identity alignment deferred to S3. Index navigation creates no mentions, "
        "book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "marker_segment_id": MARKER_SEGMENT_ID,
    "left_segment_id": LEFT_SEGMENT_ID,
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "newly_excluded": NEWLY_EXCLUDED,
    "preserved_excluded": sorted(PRESERVED_EXCLUDED),
    "added_types": dict(sorted(counts.items())),
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
