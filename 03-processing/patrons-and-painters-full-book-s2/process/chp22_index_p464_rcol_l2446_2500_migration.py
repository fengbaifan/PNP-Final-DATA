#!/usr/bin/env python3
"""Classify p.464 right-column index entries and correct Poussin locators from print."""

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
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l2446-2500"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p464-right-l2446-2500-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/P.csv": "98c13c7d1d21dea3fd8008e6504d4ba1f30a2da6532a9e2ff52c2fab17e0d792",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "0adf78e8cbd339f4d44ddf1a618db62d1dbe41488e51e865bc377c17a73dd6cd",
    "04-knowledge/tables/s2-coverage.csv": "a20dbf5ce4fdceadfd351d8af8bd78c426458a6d19add4d7b5f8da9ce2407920",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"P.csv#{i}": "person" for i in (164, 165, 166, 168, 169, 170, 171, 174, 175, 176, 177, 178, 179, 181, 182, 185, 187, 188, 189, 190, 191, 192, 193)},
    **{f"P.csv#{i}": "place" for i in (167, 173, 183)},
    **{f"P.csv#{i}": "work" for i in (180, 184, *range(194, 213))},
}
EXCLUDED_ALIASES = {
    "P.csv#172": ("cand-2925", "Pomerancio", "see under Roncalli, Cristoforo"),
    "P.csv#186": ("cand-2926", "Poussin, Gaspard", "see under Dughet, Gaspard"),
}
EXPECTED_ENTRIES = {f"P.csv#{i}" for i in range(164, 213)}
SEGMENT_RANGE = (2446, 2500)
EXPECTED_SEGMENT_SHA256 = "129b7843aa2b211c58f3631788058e33eec9327af73457bd859518fe8aada936"
CORRECTIONS = [
    (
        "cand-1984", "P.csv#187", "index_page_range",
        "15, 28, 44, 45, 46, 57, 95, 101n, 110, 113, 114, 115n, 120, 121n, 124, 128, 142, 146, 159, 166, 172, 173, 175, 176, 180, 181, 197, 341, 353, 354, 384, 401",
        "15, 38, 44, 45, 46, 57, 95, 101n, 110, 113, 114, 115, 120, 121n, 124, 138, 142, 146, 159, 166, 172, 173, 175, 176, 180, 181, 197, 341, 353, 354, 384, 401",
    ),
    ("cand-1987", "P.csv#190", "index_page_range", "106, 112", "106, 113"),
    ("cand-1989", "P.csv#192", "index_page_range", "112, 117, 118", "115, 117, 118"),
]


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
parser.add_argument("--apply", action="store_true", help="write reviewed candidate types and locator corrections")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2445:2500])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA256:
    raise SystemExit("p.464 right-column source segment changed")
if not all(token in segment_text for token in ("Po, Giacomo del", "Pomerancio, see under Roncalli", "Poussin, Nicolas", "King Midas, 117")):
    raise SystemExit("p.464 right-column content check failed")
if "[Page 465]" in segment_text or "Landscape with Man fleeing from Serpent" in segment_text:
    raise SystemExit("the following page segment leaked into p.464 right-column scope")

manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
manifest_row = manifest.get(SEGMENT_ID)
if not manifest_row or (
    manifest_row.get("source_file"), manifest_row.get("line_start"), manifest_row.get("line_end"),
    manifest_row.get("sha256"), manifest_row.get("asset_sha256"), manifest_row.get("release_excluded"),
) != (SOURCE_FILE, *SEGMENT_RANGE, EXPECTED_SEGMENT_SHA256, EXPECTED_HASHES[SOURCE_FILE], True):
    raise SystemExit("p.464 right-column manifest mismatch")

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
    raise SystemExit("p.464 right-column index candidate mapping is incomplete")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
for entry_id, (candidate_id, canonical_name, alias) in EXCLUDED_ALIASES.items():
    row = candidate_by_entry.get(entry_id)
    if not row or (
        row["candidate_id"], row["canonical_name"], row["sub_entry"], row["status"], row["suggested_type"], row["exclude_reason"]
    ) != (candidate_id, canonical_name, alias, "excluded", "", f"索引交叉引用：{alias}"):
        raise SystemExit(f"pre-excluded index alias changed: {entry_id}")

for candidate_id, entry_id, field, before, _after in CORRECTIONS:
    row = candidate_by_id.get(candidate_id)
    if not row or row["index_entry_id"] != entry_id or row[field] != before or row["status"] != "open":
        raise SystemExit(f"printed-page correction pre-state changed: {candidate_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
target = coverage_by_segment.get(SEGMENT_ID)
if not target or (target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.464 right-column coverage is not queued/pending")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for candidate_id, _entry_id, field, _before, after in CORRECTIONS:
    candidate_by_id[candidate_id][field] = after
target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2446-2500",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.22 visibly prints p.464; "
        "the right column contains P.csv#164-212 (49 entries), from Po, Giacomo del through Poussin's King Midas. "
        "Forty-seven existing candidates receive types: 23 person, 3 place and 21 work; the two see-under aliases "
        "P#172 and P#186 remain excluded. P#181-184 remain Portland person-context, Bulstrode Park place and Rigaud "
        "portrait work; no formal edge is inferred from 'and Sebastiano Ricci'. P#188 altarpieces and P#189-193 "
        "artist-person contexts do not assert individual work/relationship records. P#194-212 are visual works, including "
        "the Arcadian Shepherds versions and Poussin's illustrations to the dal Pozzo edition; the illustrated book "
        "remains a separate archive object. Printed p.464 corrects candidate P#187 locators 28→38, 115n→115, 128→138; "
        "P#190 112→113; and P#192 112→115. P.csv and S0 remain unchanged. No mentions, book statements or formal "
        "relations are added by index navigation."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": len(EXPECTED_ENTRIES),
    "typed_existing_candidates": len(TYPE_BY_ENTRY),
    "preserved_excluded_aliases": list(EXCLUDED_ALIASES),
    "added_types": dict(sorted(counts.items())),
    "candidate_corrections": [
        {"candidate_id": candidate_id, "index_entry_id": entry_id, "field": field, "before": before, "after": after}
        for candidate_id, entry_id, field, before, after in CORRECTIONS
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
