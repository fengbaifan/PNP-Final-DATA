#!/usr/bin/env python3
"""Classify the p.467 generated marker and left-column index entries."""

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
MARKER_ID = "chp-22:22_CHP-22Index:l2728-2729"
LEFT_ID = "chp-22:22_CHP-22Index:l2731-2785"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p467-left-l2728-2785-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/Q-R.csv": "8a95726a58f59efc58cff819448acb23f36608e469fd1c8aeda9dca656f3a15c",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/02_CHP-2_sec_iv.md": "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
    "02-sources/02-Markdown/05_CHP-5_sec_iv.md": "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f",
    "02-sources/02-Markdown/08_CHP-8.md": "667039dcd7e79cd30d4f412faf90f0854eba38eab163050455b1947ed78fa184",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "11d42d95776cc8298a61bd3e42a8019945fde475b2f16bd8deaa4cfd35efe63b",
    "04-knowledge/tables/s2-coverage.csv": "94eb47fe17557ef1d69c4cfdf5bf2908a5888ba9027c03c861260105d8c2179b",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"Q-R.csv#{i}": "person" for i in (
        125, 127, 129, 131, 132, 133, 134, 135, 145, 150, 151, 152, 153, 155, 157, 158,
        159, 161, 162, 163, 165, 168, 171, 172,
    )},
    **{f"Q-R.csv#{i}": "work" for i in (
        126, 128, *range(137, 143), 143, 144, 146, 147, 148, 149, 154, 164, 167, 169, 173,
    )},
    "Q-R.csv#130": "archive",
    **{f"Q-R.csv#{i}": "event" for i in (136, 156, 166, 170)},
    "Q-R.csv#160": "term",
}
EXPECTED_ENTRIES = {f"Q-R.csv#{i}" for i in range(125, 174)}
SEGMENTS = {
    MARKER_ID: (2728, 2729, "03501b7a9700b7edb046f3b547b25b1102b5ab2d138638a33498db36fad49521"),
    LEFT_ID: (2731, 2785, "fa9ca0d3ac512f60f37395cd3c5a351727b5f1c984c744e024d898b81c9f0c52"),
}
CORRECTIONS = [
    ("cand-2206", "Q-R.csv#133", "index_page_range", "211n", "311n"),
    (
        "cand-2236", "Q-R.csv#163", "index_page_range",
        "11, 15, 111, 120, 124, 126, 127, 128, 134, 137, 142, 143, 144, 145, 152, 153, 155, 183, 187, 190, 197n, 210, 234n, 354, 384",
        "11, 15, 111, 120, 124, 126, 127, 128, 134, 137, 142, 143, 144, 145, 152, 153, 155, 169, 187, 190, 197n, 210, 234n, 354, 384",
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
if "[Page 467]" not in source_lines[2727] or "INDEX" not in source_lines[2728]:
    raise SystemExit("p.467 generated marker boundary check failed")
left_text = "\n".join(source_lines[2730:2785])
if not all(token in left_text for token in (
    "Rigaud, Hyacinthe", "Rockingham, Lord", "Roomer, Gaspar", "Rosa, Salvator", "Landscape with Apollo, 184",
)):
    raise SystemExit("p.467 left-column content check failed")
if "[Page 468]" in left_text:
    raise SystemExit("next-page content leaked into p.467 left-column scope")

with QR_INDEX.open(encoding="utf-8-sig", newline="") as handle:
    qr_rows = list(csv.DictReader(handle))
if len(qr_rows) <= 173 or (qr_rows[125]["Main Entry"], qr_rows[173]["Sub-entry"]) != (
    "Rigaud, Hyacinthe", "Landscape with Apollo"
):
    raise SystemExit("Q-R.csv#125-173 boundary check failed")

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
        raise SystemExit(f"p.467 manifest mismatch: {segment_id}")

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
    raise SystemExit("p.467 left-column index candidate mapping is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
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
        raise SystemExit(f"p.467 coverage is not queued/pending: {segment_id}")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for candidate_id, _entry_id, field, _before, after in CORRECTIONS:
    candidate_by_id[candidate_id][field] = after

coverage_by_segment[MARKER_ID].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2728-2729",
    "note": "no_semantic_content: S0 L2728 [Page 467] and L2729 INDEX are generated navigation markers, confirmed on CHP-22Index.pdf physical p.25; they are not indexed objects.",
})
coverage_by_segment[LEFT_ID].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2731-2785",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.25 prints p.467; the physical left column contains "
        "Q-R.csv#125-173 (49 entries), from Rigaud, Hyacinthe through Salvator Rosa's Landscape with Apollo. S0 OCR interleaves right-column "
        "fragments, so the physical column boundary controls this classification. Types: 24 person, 19 work, 1 archive, 4 event and 1 term. "
        "Q-R#130 Ripa's Iconologia is a book/archive; #136 Romanelli's appointment to the Accademia di S. Luca, #156 Roomer's escape during "
        "the Masaniello revolt, #166 Rosa's attack on the bambocciate, and #170 an exhibition at S. Giovanni Decollato are event candidates. "
        "Q-R#160 relationship between North and South European cultures in Roomer's collection is a conceptual term, not a formal relation. Named "
        "paintings and work-context subentries remain work candidates; artist associations and career/person context do not create relations. Printed "
        "p.467 corrects derived-candidate locators only: Q-R#133 Rockingham 211n→311n and Q-R#163 Salvator Rosa 183→169. Q-R.csv and S0 remain "
        "unchanged. Index navigation creates no mentions, book statements or formal relations."
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
