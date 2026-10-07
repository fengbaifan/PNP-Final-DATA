#!/usr/bin/env python3
"""Classify p.461 right-column index entries with print-checked corrections."""

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
INDEX_M = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "M.csv"
SEGMENT_ID = "chp-22:22_CHP-22Index:l2105-2158"
SEGMENT_SHA = "d8472bf922a68619a757e940e0fdb3d131c51e80535ff4c82fc2eecbf21faff7"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p461-right-l2105-2158-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_M: "4443a44bdbbce2e0ad3b758e8853b026e79edfba4d06b742ddd3043c0e215b4c",
    ROOT / "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md": "d620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077",
    ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "39ca507752f69258b77f5aa23e1bf5fead10b3ab2a8fe2c46f87d996f96c16c0",
    TABLES / "s2-coverage.csv": "c3970a783dfe2d58825d5cb05f43b3ec61f2245bac5726f3df381a9a2eba5b6d",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ENTRY = {
    **{f"M.csv#{i}": "person" for i in (
        224, 225, 227, 228, 229, 230, 232, 233, 234, 235, 237, 238, 239,
        240, 241, 242, 243, 244, 245, 246, 248, 249, 250, 252, 253, 254,
        257, 258, 260, 261,
    )},
    **{f"M.csv#{i}": "place" for i in (231, 251, 255, 256)},
    "M.csv#236": "event",
    "M.csv#247": "family",
    "M.csv#259": "archive",
}
EXCLUDED_ENTRIES = {"M.csv#226": "excluded"}
PAGE_RANGE_CORRECTIONS = {
    "M.csv#234": (
        "126, 171, 172",
        "136, 171, 172",
    ),
    "M.csv#258": (
        "261n, 274, 275n, 300n, 302n, 318, 336n, 350",
        "261n, 271n, 275n, 300n, 302n, 318, 336n, 350",
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--apply", action="store_true", help="write reviewed candidate types, corrections, and coverage"
)
ARGS = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[2104:2158])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 p.461 right-column segment changed")

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
    segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
    segment.get("sha256"), segment.get("asset_sha256"), segment.get("release_excluded"),
) != (SOURCE_FILE, 2105, 2158, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.461 right-column manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_path = TABLES / "s2-coverage.csv"
coverage_fields, coverage = read_csv(coverage_path)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(mentions), len(statements)) != (11436, 832, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

expected_entries = {f"M.csv#{i}" for i in range(224, 262)}
candidate_by_entry = {
    row["index_entry_id"]: row for row in candidates if row.get("index_entry_id") in expected_entries
}
if set(candidate_by_entry) != expected_entries or len(candidate_by_entry) != 38:
    raise SystemExit("p.461 right-column candidate mapping is incomplete or duplicated")
for entry_id, expected_status in EXCLUDED_ENTRIES.items():
    if candidate_by_entry[entry_id]["status"] != expected_status:
        raise SystemExit(f"pre-excluded alias state changed for {entry_id}")
for entry_id, row in candidate_by_entry.items():
    if entry_id in EXCLUDED_ENTRIES:
        continue
    if row["status"] != "open":
        raise SystemExit(f"unexpected candidate status for {entry_id}: {row['status']}")
    if row["suggested_type"]:
        raise SystemExit(f"unexpected prior type for {entry_id}")
if set(TYPE_BY_INDEX_ENTRY) & set(EXCLUDED_ENTRIES):
    raise SystemExit("type map overlaps excluded aliases")
if len(TYPE_BY_INDEX_ENTRY) != 37 or len(EXCLUDED_ENTRIES) != 1:
    raise SystemExit("unexpected reviewed classification counts")

for entry_id, (before, _) in PAGE_RANGE_CORRECTIONS.items():
    if candidate_by_entry[entry_id]["index_page_range"] != before:
        raise SystemExit(f"unexpected page range for {entry_id}")
if candidate_by_entry["M.csv#249"]["canonical_name"] != "Moscheni, Pietro":
    raise SystemExit("Moscheni candidate spelling changed")
if candidate_by_entry["M.csv#249"]["index_page_range"] != "322":
    raise SystemExit("Moscheni page locator changed")

target = next((row for row in coverage if row["segment_id"] == SEGMENT_ID), None)
if not target or (
    target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]
) != ("queued", "pending", "", ""):
    raise SystemExit("p.461 right-column coverage state changed")

for entry_id, entity_type in TYPE_BY_INDEX_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type
for entry_id, (_, corrected_range) in PAGE_RANGE_CORRECTIONS.items():
    candidate_by_entry[entry_id]["index_page_range"] = corrected_range

target.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2105-2158",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.19 visibly "
        "prints p.461; S0 L2105 'X 461' is page-number OCR noise, and the right column contains "
        "M.csv#224-261 (38 entries), including the pre-excluded see-under alias M.csv#226. Thirty-seven "
        "open candidates receive types: 30 person, 4 place, 1 event, 1 family and 1 archive. The print "
        "reads Count of Monterey p.136 (not M.csv/candidate p.126), so cand-1693 M.csv#234 is corrected "
        "to p.136 while preserving S0 and M.csv. The print reads Muratori p.271n (not M.csv/candidate "
        "p.274), so cand-1717 M.csv#258 is corrected to p.271n. The printed and M.csv spelling for "
        "Pietro Moscheni is confirmed against the body; S0 OCR 'Moschetti' is preserved as a transcription "
        "variant. Monterey's employment-of-Ribera subentry remains person context; the specific purchase "
        "of the Aldobrandini Titians from the Ludovisi family is an event. Munich, Moscow, Montanari "
        "palace and Nymphenburg palace are places; Morosini family is family; Muratori's Della pubblica "
        "felicità is an archive/text. Index navigation creates no mentions, book statements or formal "
        "relations."
    ),
})

added_types = Counter(TYPE_BY_INDEX_ENTRY.values())
summary = {
    "segment_id": SEGMENT_ID,
    "index_rows": 38,
    "new_types": len(TYPE_BY_INDEX_ENTRY),
    "excluded_aliases": sorted(EXCLUDED_ENTRIES),
    "added_types": dict(sorted(added_types.items())),
    "page_range_corrections": {key: list(value) for key, value in PAGE_RANGE_CORRECTIONS.items()},
    "moscheni_spelling": "print and M.csv confirmed; preserve candidate spelling and S0 OCR variant",
    "apply": ARGS.apply,
}

if ARGS.apply:
    backups = [
        candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
        coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
    ]
    if any(path.exists() for path in backups):
        raise SystemExit("a backup with this task suffix already exists")
    for source, backup in zip((candidate_path, coverage_path), backups):
        shutil.copy2(source, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    if sha256(candidate_path) == EXPECTED_HASHES[candidate_path] or sha256(coverage_path) == EXPECTED_HASHES[coverage_path]:
        raise SystemExit("apply did not update both S2 tables")
    summary["backups"] = [str(path.relative_to(ROOT)) for path in backups]

print(json.dumps(summary, ensure_ascii=False, indent=2))
