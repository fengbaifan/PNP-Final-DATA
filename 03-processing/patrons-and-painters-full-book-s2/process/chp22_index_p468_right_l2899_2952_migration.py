#!/usr/bin/env python3
"""Classify p.468 right-column index seeds and close its S2 source segment."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l2899-2952"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p468-right-l2899-2952-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/S.csv": "a73a199a0d4e2c01dfe12fd77e562e30298edb2357c54b341da887bad306393f",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/07_CHP-7_sec_v.md": "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    "02-sources/02-Markdown/09_CHP-9_sec_ii.md": "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/13_CHP-13_intro.md": "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    "02-sources/02-Markdown/05_CHP-5_sec_i.md": "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
    "02-sources/02-Markdown/16_CHP-16_intro.md": "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff",
    "02-sources/02-Markdown/00_05_List_of_Plates.md": "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "bf8666f150096b18bb564b158867392895285a431b47e9de28e25418c4056e22",
    "04-knowledge/tables/s2-coverage.csv": "1634047819662b6b040a95d7c874481a366f1747526696ba49998eccfbd0ea79",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"S.csv#{i}": "person" for i in (
        29, 32, 33, 34, 35, 37, 41, 42, 44, 45, 46, 47, 48, 49, 51, 52,
        56, 57, 60, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76,
    )},
    **{f"S.csv#{i}": "work" for i in (38, 43, 50, 53, 58, 59, 61, 62)},
    **{f"S.csv#{i}": "institution" for i in (39, 67, 77)},
    **{f"S.csv#{i}": "place" for i in (31, 40)},
    **{f"S.csv#{i}": "archive" for i in (30, 54)},
    "S.csv#36": "family",
    "S.csv#55": "event",
}
EXPECTED_ENTRIES = {f"S.csv#{i}" for i in range(29, 78)}
EXPECTED_SEGMENT_SHA256 = "69c6f646dfac54bd9b475622b4b26596fc731e42265504b21489eced0a6a397e"
SEGMENT_RANGE = (2899, 2952)


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
segment_text = "\n".join(source_lines[SEGMENT_RANGE[0] - 1:SEGMENT_RANGE[1]])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA256:
    raise SystemExit(f"source segment changed: {SEGMENT_ID}")
if not all(token in segment_text for token in (
    "Saint-Non", "St Petersburg", "Salviati family", "San Rocco, Scuola di",
    "Osservazioni sopra i lavori di niello", "Sassoferrato", "Savoy, Prince Eugene",
    "Scalzi, Venice",
)):
    raise SystemExit("p.468 right-column content check failed")
if "[Page 469]" in segment_text or "Sagrestani, Giovan Camillo" in segment_text:
    raise SystemExit("left-column or next-page content leaked into p.468 right-column scope")

s_fields, s_rows = read_csv(S_INDEX)
if len(s_rows) <= 77 or (s_rows[29]["Main Entry"], s_rows[77]["Main Entry"]) != (
    "Saint-Non, Abbé de", "Scalzi",
):
    raise SystemExit("S.csv#29-77 boundary check failed")

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
    raise SystemExit(f"p.468 manifest mismatch: {SEGMENT_ID}")

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
    raise SystemExit("p.468 right-column candidate mapping is incomplete")
if len(TYPE_BY_ENTRY) != 49 or Counter(TYPE_BY_ENTRY.values()) != Counter({
    "person": 32, "work": 8, "institution": 3, "place": 2,
    "archive": 2, "family": 1, "event": 1,
}):
    raise SystemExit("p.468 right-column type disposition map is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_segment.get(SEGMENT_ID)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"], coverage_row["note"]) != (
    "queued", "pending", "", "",
):
    raise SystemExit(f"p.468 right-column coverage is not queued/pending: {SEGMENT_ID}")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type

coverage_by_segment[SEGMENT_ID].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2899-2952",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.26 prints p.468; the physical right column contains "
        "S.csv#29-77 (49 entries), from Saint-Non, Abbé de through Scalzi, Venice. Types: 32 person, 8 work, 3 institution, 2 place, 2 archive, "
        "1 family and 1 event. S#30 Voyage Pittoresque and #54 Osservazioni sopra i lavori di niello are archive; named paintings, frescoes, "
        "Bacchus and the Sasso portrait are work. S#36 Salviati family is family; #39 Scuola di San Rocco is institution (p.334 identifies "
        "Albrizzi as member and Guardiano); #67 Savoy is the historical state/political entity (p.202); #77 Scalzi refers to the Discalced "
        "Carmelite order, an institutional subject of pp.269-270. St Petersburg (#31) and Sandi palace (#40) are places. S#55 records the "
        "series of purchases for John Strange as an event candidate; it does not assert a formal relation. Patronage and taste subentries under "
        "Prince Eugene and the other personal entries remain person context. Printed p.468 confirms OCR locator readings S#59 131n, #69 341n, "
        "and #70 201n; S.csv and candidates already match the print, so no locator correction was needed. S.csv and S0 remain unchanged. Index "
        "navigation creates no mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "source_lines": list(SEGMENT_RANGE),
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
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
