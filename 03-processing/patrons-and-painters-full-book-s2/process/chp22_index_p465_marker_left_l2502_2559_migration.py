#!/usr/bin/env python3
"""Classify the p.465 marker and left-column index entries, correcting printed locators."""

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
INDEX_P = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
MARKER_ID = "chp-22:22_CHP-22Index:l2502-2503"
LEFT_ID = "chp-22:22_CHP-22Index:l2505-2559"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p465-left-l2502-2559-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/P.csv": "98c13c7d1d21dea3fd8008e6504d4ba1f30a2da6532a9e2ff52c2fab17e0d792",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/03_CHP-3_sec_iv.md": "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed",
    "02-sources/02-Markdown/04_CHP-4_sec_ii.md": "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "064dc3f82c426db20b91e40b3c84c6b0be551ff3e1f9aab2e810bb4dadff1f5f",
    "04-knowledge/tables/s2-coverage.csv": "93731b8d5133cfed5ad04d2ee67ce53cc9c1e1d62ad986e573545ed05d9e3aaa",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"P.csv#{i}": "work" for i in (*range(213, 223), *range(224, 234), 247, 260, 261, 263)},
    **{f"P.csv#{i}": "person" for i in (223, *range(234, 247), *range(249, 252), *range(254, 260), 262)},
    "P.csv#248": "archive",
}
UNRESOLVED_ENTRIES = {
    "P.csv#252": "Cassiano dal Pozzo's general museum/collection context",
    "P.csv#253": "the paper-museum drawing corpus; collection is not a taxonomy type",
}
EXPECTED_ENTRIES = {f"P.csv#{i}" for i in range(213, 264)}
SEGMENTS = {
    MARKER_ID: (2502, 2503, "4acb1a55fc5303287ad1b5976ea697e6147fd5d007aa7d4043eef1072ea3970a"),
    LEFT_ID: (2505, 2559, "c30c2e7e434edb01c22938f757436ed094d07767cf93f6cae7713296f09a5465"),
}
CORRECTIONS = [
    ("cand-2011", "P.csv#214", "index_page_range", "48n", "46n"),
    ("cand-2026", "P.csv#229", "index_page_range", "155", "15"),
    ("cand-2027", "P.csv#230", "index_page_range", "112, 113, 114", "113, 114"),
    ("cand-2055", "P.csv#258", "index_page_range", "121n", "13n"),
    (
        "cand-2056", "P.csv#259", "index_page_range",
        "13n, 57, 78, 122, 149, 150, 189, 207, 208, 210, 212n",
        "13n, 57, 78, 122, 149, 150, 189, 207, 208, 210, 213n",
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
for segment_id, (start, end, expected_segment_hash) in SEGMENTS.items():
    segment_text = "\n".join(source_lines[start - 1:end])
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != expected_segment_hash:
        raise SystemExit(f"source segment changed: {segment_id}")
if "[Page 465]" not in source_lines[2501] or "INDEX" not in source_lines[2502]:
    raise SystemExit("p.465 generated marker boundary check failed")
left_text = "\n".join(source_lines[2504:2559])
if not all(token in left_text for token in ("Landscape with Man fleeing from Serpent", "Spring, 15", "Museum Chartaceum", "Marriage Feast at Cana, 207-8")):
    raise SystemExit("p.465 left-column content check failed")
if "Martyrdom of St Bartholomew, 208" in left_text or "[Page 466]" in left_text:
    raise SystemExit("right-column or next-page content leaked into the p.465 left-column segment")

with INDEX_P.open(encoding="utf-8-sig", newline="") as handle:
    p_rows = list(csv.DictReader(handle))
if len(p_rows) <= 263 or p_rows[213]["Main Entry"] != "Poussin, Nicolas" or p_rows[263]["Sub-entry"] != "Marriage Feast at Cana":
    raise SystemExit("P.csv#213-263 boundary check failed")

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
        raise SystemExit(f"p.465 manifest mismatch: {segment_id}")

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
if set(candidate_by_entry) != EXPECTED_ENTRIES or len(candidate_by_entry) != 51:
    raise SystemExit("p.465 left-column index candidate mapping is incomplete")
for entry_id in TYPE_BY_ENTRY:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected candidate pre-state: {entry_id}")
for entry_id in UNRESOLVED_ENTRIES:
    row = candidate_by_entry[entry_id]
    if row["status"] != "open" or row["suggested_type"]:
        raise SystemExit(f"unexpected unresolved collection pre-state: {entry_id}")

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
        raise SystemExit(f"p.465 coverage is not queued/pending: {segment_id}")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for candidate_id, _entry_id, field, _before, after in CORRECTIONS:
    candidate_by_id[candidate_id][field] = after

coverage_by_segment[MARKER_ID].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2502-2503",
    "note": "no_semantic_content: S0 L2502 [Page 465] and L2503 INDEX are generated navigation markers, confirmed on CHP-22Index.pdf physical p.23; they are not indexed objects.",
})
coverage_by_segment[LEFT_ID].update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2505-2559",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.23 prints p.465; the physical left column contains "
        "P.csv#213-263 (51 entries), from Poussin's Landscape with Man fleeing from Serpent through Preti's Marriage Feast at Cana. "
        "S0 lines interleave OCR fragments from the opposite column, so the physical column boundary controls this classification; the right-column "
        "Martyrdom of St Bartholomew entry belongs to the following segment. Types: 24 person, 24 work and 1 archive; P#252 museum and P#253 "
        "Museum Chartaceum remain type-unresolved collection candidates because collection is not a taxonomy type, and are not identity-merged with "
        "body candidates at S2. P#223 pressure to return to France, the artist subentries P#234-246 and P#249-251, P#254-259, and P#262 remain "
        "person context; no formal relation is inferred from the 'and' entries or Cassiano's visit with Cardinal Francesco Barberini. P#247 Bernini "
        "caricature and P#260-261, P#263 are works; P#248's edition of Leonardo's Trattato is archive. The printed page corrects derived-candidate "
        "locators only: P#214 48n→46n, P#229 155→15, P#230 112-114→113-114, P#258 121n→13n, and P#259 212n→213n. P.csv and S0 remain "
        "unchanged. Index navigation creates no mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segments": {key: {"source_lines": [SEGMENTS[key][0], SEGMENTS[key][1]], "disposition": coverage_by_segment[key]["disposition"]} for key in SEGMENTS},
    "index_rows": len(EXPECTED_ENTRIES),
    "typed_existing_candidates": len(TYPE_BY_ENTRY),
    "type_unresolved_collection_candidates": list(UNRESOLVED_ENTRIES),
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
