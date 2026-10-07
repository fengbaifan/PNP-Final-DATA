#!/usr/bin/env python3
"""Classify the p.466 generated marker and left-column index entries."""

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
QR_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "Q-R.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
MARKER_ID = "chp-22:22_CHP-22Index:l2614-2614"
LEFT_ID = "chp-22:22_CHP-22Index:l2616-2670"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p466-left-l2614-2670-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/Q-R.csv": "8a95726a58f59efc58cff819448acb23f36608e469fd1c8aeda9dca656f3a15c",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/05_CHP-5_sec_iii.md": "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a",
    "02-sources/02-Markdown/15_CHP-15_sec_ii.md": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "6998839f163a34766e710b9ad5acaca67ff26e97d4155a07fbec012031c18164",
    "04-knowledge/tables/s2-coverage.csv": "38acfe53e7c69630e8ee4c74e8956004783173c45686ffc3cb510f888bfd139a",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"Q-R.csv#{i}": "person" for i in (34, 38, 39, 44, 51, 54, *range(60, 69), 73, 74, 75)},
    **{f"Q-R.csv#{i}": "work" for i in (*range(45, 49), 52, 53, *range(55, 60), *range(69, 72))},
    **{f"Q-R.csv#{i}": "term" for i in (37, 40, 41, 42, 43)},
    "Q-R.csv#49": "institution",
    "Q-R.csv#50": "institution",
    "Q-R.csv#36": "event",
    "Q-R.csv#72": "place",
}
PRESERVED_TYPES = {
    "Q-R.csv#35": ("cand-2108", "Rapparini, Giorgio Maria", "archive"),
    "Q-R.csv#76": ("cand-2149", "Ricci, Marco", "person"),
}
EXPECTED_ENTRIES = {f"Q-R.csv#{i}" for i in range(34, 77)}
SEGMENTS = {
    MARKER_ID: (2614, 2614, "edd1dd6b31cba123814b79054a8fd35247fe9d3d5c253b64e1d842c9203a592e"),
    LEFT_ID: (2616, 2670, "8bd14e1f80499338d2b752549ee212d15e071e5de531b5f81cc2e60876613eb4"),
}
CORRECTIONS = [
    (
        "cand-2124", "Q-R.csv#51", "index_page_range",
        "14, 21, 28, 30, 43, 45, 49, 56, 71, 78, 95, 162, 197, 222, 262, 283, 321, 348",
        "14, 21, 28, 30, 43, 45, 49, 56, 71, 78, 95, 162, 197, 222, 262, 283, 324, 348",
    ),
    (
        "cand-2137", "Q-R.csv#64", "index_page_range", "254, 323", "254, 362, 363",
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
parser.add_argument("--apply", action="store_true", help="write reviewed types, locator corrections and coverage")
args = parser.parse_args()

for relative, expected in EXPECTED_HASHES.items():
    if sha256(ROOT / relative) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {relative}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
for segment_id, (start, end, expected_segment_hash) in SEGMENTS.items():
    segment_text = "\n".join(source_lines[start - 1:end])
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != expected_segment_hash:
        raise SystemExit(f"source segment changed: {segment_id}")
if "[Page 466]" not in source_lines[2613]:
    raise SystemExit("p.466 generated marker boundary check failed")
left_text = "\n".join(source_lines[2615:2670])
if not all(token in left_text for token in (
    "Rapparini, Giorgio Maria", "Religious orders, patronage by", "attack on Bamboccianti",
    "Riccardi palace, Florence", "Ricci, Marco",
)):
    raise SystemExit("p.466 left-column content check failed")
if "[Page 467]" in left_text or "Monuments to" in left_text:
    raise SystemExit("next-page or right-column content leaked into p.466 left-column scope")

with QR_INDEX.open(encoding="utf-8-sig", newline="") as handle:
    qr_rows = list(csv.DictReader(handle))
if len(qr_rows) <= 76 or (qr_rows[34]["Main Entry"], qr_rows[76]["Main Entry"]) != (
    "Rapparini, Giorgio Maria", "Ricci, Marco"
):
    raise SystemExit("Q-R.csv#34-76 boundary check failed")

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
        raise SystemExit(f"p.466 manifest mismatch: {segment_id}")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 43:
    raise SystemExit("p.466 left-column index candidate mapping is incomplete")
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
for segment_id in SEGMENTS:
    row = coverage_by_segment.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
        "queued", "pending", "", ""
    ):
        raise SystemExit(f"p.466 coverage is not queued/pending: {segment_id}")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for candidate_id, _entry_id, field, _before, after in CORRECTIONS:
    candidate_by_id[candidate_id][field] = after

coverage_by_segment[MARKER_ID].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2614-2614",
    "note": "no_semantic_content: S0 L2614 [Page 466] is a generated navigation marker, confirmed on CHP-22Index.pdf physical p.24; it is not an indexed object.",
})
coverage_by_segment[LEFT_ID].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2616-2670",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.24 prints p.466; the physical left column contains "
        "Q-R.csv#34-76 (43 entries), from Rapparini's Portrait du Vrai Mérite entry through Ricci, Marco. Types: 18 person, 14 work, "
        "5 term, 2 institution, 1 place and 1 event; existing Q-R#35 Rapparini publication/archive and Q-R#76 Ricci Marco person types are "
        "preserved. Q-R#37 reason and fantasy and #40-43 religious-order patronage topics remain terms; #36 Treaty of Rastatt is an event; "
        "#49-50 Remondini's publisher entry and prints-for subentry remain in institution context; #72 Riccardi palace is a place. Named works "
        "remain distinct from artist entries. Q-R#54 Reni's attack-on-Bamboccianti subentry remains person context; the p.141 discussion notes "
        "that Passeri may be attributing some of his own feelings to Reni, so the index does not establish authorship. Q-R#68 altarpieces for "
        "Monterey and #75 patronage of Crespi remain person context and do not create formal relations. The printed page corrects derived-candidate "
        "locators only: Q-R#51 Guido Reni 321→324 and Q-R#64 Carlo Rezzonico 254,323→254,362,363. Q-R.csv and S0 remain unchanged. "
        "Index navigation creates no mentions, book statements or formal relations."
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
    "preserved_existing_types": list(PRESERVED_TYPES),
    "final_type_counts_in_segment": {
        "person": counts["person"] + 1,
        **{entity_type: count for entity_type, count in sorted(counts.items()) if entity_type != "person"},
        "archive": 1,
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
