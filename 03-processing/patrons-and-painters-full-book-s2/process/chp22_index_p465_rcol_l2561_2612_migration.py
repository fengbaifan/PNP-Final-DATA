#!/usr/bin/env python3
"""Classify the p.465 right-column index entries and correct printed locators."""

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
P_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv"
QR_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "Q-R.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l2561-2612"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p465-right-l2561-2612-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/P.csv": "98c13c7d1d21dea3fd8008e6504d4ba1f30a2da6532a9e2ff52c2fab17e0d792",
    "02-sources/03-Index/03-2-Index-CSV/Q-R.csv": "8a95726a58f59efc58cff819448acb23f36608e469fd1c8aeda9dca656f3a15c",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "76f57db85da3cbd5a4595bafa8e23587ca28e1820526f5c31b0188838137c717",
    "04-knowledge/tables/s2-coverage.csv": "af01f8104efeb0c447b6fc3091f269765924824d0b2edb626f8b75c32a0bd9bd",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"P.csv#{i}": "work" for i in (264, 274)},
    **{f"P.csv#{i}": "term" for i in (265, 268, 269, 270, 271)},
    **{f"P.csv#{i}": "person" for i in (266, 267, 272, 273, 275)},
    **{f"Q-R.csv#{i}": "person" for i in (*range(0, 6), *range(9, 15), *range(16, 22), 24, 25)},
    **{f"Q-R.csv#{i}": "place" for i in (7, 8, 15)},
    "Q-R.csv#6": "event",
    "Q-R.csv#22": "work",
    **{f"Q-R.csv#{i}": "work" for i in range(26, 34)},
}
PRESERVED_TYPES = {
    "Q-R.csv#23": ("cand-2096", "Ranuzzi, Vincenzo", "person"),
}
EXPECTED_ENTRIES = {
    *(f"P.csv#{i}" for i in range(264, 276)),
    *(f"Q-R.csv#{i}" for i in range(34)),
}
EXPECTED_SEGMENT_SHA256 = "7dab8f155884e0183bdaf219b3470fa9da93dfb6a019160fed237f2e896dd142"
SEGMENT_RANGE = (2561, 2612)
CORRECTIONS = [
    (
        "cand-2062", "P.csv#265", "index_page_range",
        "12n, 14, 16, 17, 88, 131, 135, 137, 170, 209, 218, 219, 220, 221, 226, 262, 273",
        "13n, 14, 16, 17, 88, 131, 135, 137, 170, 209, 218, 219, 220, 221, 226, 262, 273",
    ),
    (
        "cand-2098", "Q-R.csv#25", "index_page_range",
        "27, 28, 30, 38, 39, 54n, 98, 128, 131, 150, 159, 160, 165, 197, 222, 283, 312, 354, 362n",
        "27, 28, 30, 38, 39, 54, 55, 56, 98, 128, 131, 150, 159, 160, 165, 197, 222, 283, 312, 354, 362, 363",
    ),
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
parser.add_argument("--apply", action="store_true", help="write reviewed index types, locator corrections and coverage")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2560:2612])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA256:
    raise SystemExit("p.465 right-column source segment changed")
if not all(token in segment_text for token in (
    "Martyrdom of St Bartholomew, 208", "Prices paid to artists", "Querini, Angelo", "Quirinal, Rome", "St Michael, 185",
)):
    raise SystemExit("p.465 right-column content check failed")
if "[Page 466]" in segment_text or "Rastatt, Treaty of" in segment_text:
    raise SystemExit("next-page content leaked into p.465 right-column scope")

p_rows, qr_rows = [], []
for path, target in ((P_INDEX, p_rows), (QR_INDEX, qr_rows)):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        target.extend(csv.DictReader(handle))
if len(p_rows) <= 275 or p_rows[264]["Main Entry"] != "Preti, Mattia" or p_rows[275]["Main Entry"] != "Pulzone, Scipione":
    raise SystemExit("P.csv#264-275 boundary check failed")
if len(qr_rows) <= 33 or qr_rows[0]["Main Entry"] != "Quaini, Luigi" or (
    qr_rows[33]["Main Entry"], qr_rows[33]["Sub-entry"]
) != ("Raphael", "St Michael"):
    raise SystemExit("Q-R.csv#0-33 boundary check failed")

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
    raise SystemExit("p.465 right-column manifest mismatch")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 46:
    raise SystemExit("p.465 right-column index candidate mapping is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
for entry_id, (candidate_id, canonical_name, entity_type) in PRESERVED_TYPES.items():
    row = candidate_by_entry[entry_id]
    if (row["candidate_id"], row["canonical_name"], row["suggested_type"], row["status"]) != (
        candidate_id, canonical_name, entity_type, "open"
    ):
        raise SystemExit(f"pre-existing candidate type changed: {entry_id}")

for candidate_id, entry_id, field, before, _after in CORRECTIONS:
    row = candidate_by_id.get(candidate_id)
    if not row or row["index_entry_id"] != entry_id or row[field] != before or row["status"] != "open":
        raise SystemExit(f"printed-page correction pre-state changed: {candidate_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
target = coverage_by_segment.get(SEGMENT_ID)
if not target or (target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]) != (
    "queued", "pending", "", ""
):
    raise SystemExit("p.465 right-column coverage is not queued/pending")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for candidate_id, _entry_id, field, _before, after in CORRECTIONS:
    candidate_by_id[candidate_id][field] = after

target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2561-2612",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.23 prints p.465; the right column contains "
        "P.csv#264-275 and Q-R.csv#0-33 (46 entries), from Preti's Martyrdom of St Bartholomew through Raphael's St Michael. "
        "Types: 26 person, 11 work, 5 term, 3 place and 1 event; existing Q-R#23 Ranuzzi person type is preserved. P#265 Prices paid to artists, "
        "P#268-271 professional classes, provincial art-patronage centres, neglect of Roman painting and publishers in Venice are topical terms. "
        "Q-R#6 Querini arrest and detention is an event; #7-8 country house and garden, and #15 Quirinal, Rome, are places. Named visual works "
        "remain separate from their artist entries. The printed page corrects derived locators only: P#265 12n→13n; Q-R#25 Raphael 54n→54-56 "
        "and 362n→362-363. P.csv, Q-R.csv and S0 remain unchanged. Index navigation creates no mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "preserved_existing_types": list(PRESERVED_TYPES),
    "final_type_counts_in_segment": {
        "person": counts["person"] + len(PRESERVED_TYPES),
        **{entity_type: count for entity_type, count in sorted(counts.items()) if entity_type != "person"},
    },
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
