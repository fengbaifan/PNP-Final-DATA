#!/usr/bin/env python3
"""Classify p.468 left-column index seeds and close its page marker."""

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
S_INDEX = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "S.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
MARKER_ID = "chp-22:22_CHP-22Index:l2842-2842"
LEFT_ID = "chp-22:22_CHP-22Index:l2844-2897"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p468-left-l2842-2897-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/Q-R.csv": "8a95726a58f59efc58cff819448acb23f36608e469fd1c8aeda9dca656f3a15c",
    "02-sources/03-Index/03-2-Index-CSV/S.csv": "a73a199a0d4e2c01dfe12fd77e562e30298edb2357c54b341da887bad306393f",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/00_05_List_of_Plates.md": "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83",
    "02-sources/02-Markdown/02_CHP-2_sec_iv.md": "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
    "02-sources/02-Markdown/08_CHP-8_sec_i.md": "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    "02-sources/02-Markdown/08_CHP-8_sec_ii.md": "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    "02-sources/02-Markdown/09_CHP-9_intro.md": "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "6ae3302816b82dddeb47a0c471466b751961e32613dfbb8d386e26e00a7b56de",
    "04-knowledge/tables/s2-coverage.csv": "3149e5fa5000a84eeef33af65c5d6314d91ae5a07ee51d4d50a80c5f2c937e97",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"Q-R.csv#{i}": "person" for i in (*range(225, 234), 236, 237, 238, 239)},
    "Q-R.csv#223": "work",
    "Q-R.csv#224": "work",
    "Q-R.csv#234": "place",
    **{f"S.csv#{i}": "person" for i in (0, 1, 2, 4, 5, 6, 7, 9, 11, *range(13, 20), 23, 26, 27, 28)},
    **{f"S.csv#{i}": "work" for i in (8, 12, 20, 21)},
    "S.csv#3": "place",
    "S.csv#10": "term",
    "S.csv#24": "event",
    "S.csv#25": "archive",
}
PENDING_TYPE = {
    "Q-R.csv#235": ("cand-2307", "Ruffo, Cardinal Tommaso", "collection"),
    "S.csv#22": ("cand-2334", "Sagredo, Zaccaria", "collection"),
}
EXPECTED_ENTRIES = {
    *(f"Q-R.csv#{i}" for i in range(223, 240)),
    *(f"S.csv#{i}" for i in range(0, 29)),
}
SEGMENTS = {
    MARKER_ID: (2842, 2842, "ccb6ef00ad066d55494bfcd323c607da52b412d89f6f117a43069378a39ee686"),
    LEFT_ID: (2844, 2897, "a8b08996d576e0236a15808f628ff37f5220185e3083902bbe63d06ca3cf956d"),
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
if "[Page 468]" not in source_lines[2841]:
    raise SystemExit("p.468 generated marker check failed")
left_text = "\n".join(source_lines[2843:2897])
if not all(token in left_text for token in (
    "Rubens, Peter Paul—continued", "Ruffo, Cardinal Tommaso", "Sacchetti, Marcello",
    "Sacchi, Andrea", "Sagredo, Zaccaria", "Sagrestani, Giovan Camillo",
)):
    raise SystemExit("p.468 left-column content check failed")
if "Saint-Non" in left_text or "AND  PAINTERS" in left_text or "[Page 469]" in left_text:
    raise SystemExit("right-column or next-page content leaked into p.468 left-column scope")

with QR_INDEX.open(encoding="utf-8-sig", newline="") as handle:
    qr_rows = list(csv.DictReader(handle))
with S_INDEX.open(encoding="utf-8-sig", newline="") as handle:
    s_rows = list(csv.DictReader(handle))
if len(qr_rows) <= 239 or (qr_rows[223]["Main Entry"], qr_rows[239]["Main Entry"]) != (
    "Rubens, Peter Paul", "Ruspoli, Marchese",
):
    raise SystemExit("Q-R.csv#223-239 boundary check failed")
if len(s_rows) <= 28 or (s_rows[0]["Main Entry"], s_rows[28]["Main Entry"]) != (
    "Sacchetti, Giovanni Francesco", "Sagrestani, Giovan Camillo",
):
    raise SystemExit("S.csv#0-28 boundary check failed")

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
        raise SystemExit(f"p.468 manifest mismatch: {segment_id}")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 46:
    raise SystemExit("p.468 left-column candidate mapping is incomplete")
if len(TYPE_BY_ENTRY) != 44 or len(PENDING_TYPE) != 2:
    raise SystemExit("p.468 left-column type disposition map is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
for entry_id, (candidate_id, canonical_name, _type) in PENDING_TYPE.items():
    row = candidate_by_entry[entry_id]
    if (row["candidate_id"], row["canonical_name"], row["status"], row["suggested_type"]) != (
        candidate_id, canonical_name, "open", "",
    ):
        raise SystemExit(f"collection type-pending pre-state changed: {entry_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
for segment_id in SEGMENTS:
    row = coverage_by_segment.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
        "queued", "pending", "", "",
    ):
        raise SystemExit(f"p.468 coverage is not queued/pending: {segment_id}")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type

coverage_by_segment[MARKER_ID].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2842-2842",
    "note": "no_semantic_content: S0 L2842 [Page 468] is a generated navigation marker, confirmed on CHP-22Index.pdf physical p.26; it is not an indexed object.",
})
coverage_by_segment[LEFT_ID].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2844-2897",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.26 prints p.468; the physical left column contains "
        "Q-R.csv#223-239 and S.csv#0-28 (46 entries), from Rubens's Feast of Herod through Sagrestani, Giovan Camillo. Types: 33 person, "
        "6 work, 2 place, 1 term, 1 event and 1 archive. Q-R#234 Archbishop's Palace, Ferrara and S#3 the Sacchetti country house at "
        "Castel Fusano are places; Q-R#235 Cardinal Ruffo's collection and S#22 Sagredo's collection of prints and drawings remain type-pending "
        "because taxonomy has no collection type. Sacchi's Divine Wisdom, work in the Barberini Palace, and the Carracci/Castiglione drawings "
        "are work-context seeds; modelli is a term; Sagredo's collection dispersal is an event and its inventories are archive. Personal patronage, "
        "taste, nervous disposition, 'and' entries, and Ruffo's attempts to obtain public commissions remain person context and do not establish "
        "formal relations. Printed p.468 confirms candidate locators already normalized in Q-R.csv/S.csv; S0 OCR has 160n as i6on, 111 as III, "
        "and 343n/346 as a joined mark. No candidate locator corrections were needed. Q-R.csv, S.csv and S0 remain unchanged. Index navigation "
        "creates no mentions, book statements or formal relations."
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
    "final_type_counts_in_segment": dict(sorted(counts.items())),
    "type_pending": sorted(PENDING_TYPE),
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
