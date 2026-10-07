#!/usr/bin/env python3
"""Classify p.467 right-column index seeds and close the S2 source segment."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l2787-2840"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p467-right-l2787-2840-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/Q-R.csv": "8a95726a58f59efc58cff819448acb23f36608e469fd1c8aeda9dca656f3a15c",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/02_CHP-2_sec_iv.md": "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
    "02-sources/02-Markdown/02_CHP-2_sec_vii.md": "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c",
    "02-sources/02-Markdown/05_CHP-5_sec_iii.md": "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a",
    "02-sources/02-Markdown/05_CHP-5_sec_iv.md": "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f",
    "02-sources/02-Markdown/06_CHP-6_sec_iv.md": "65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775",
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/entity-candidates.csv": "eb2d554eb6a9992aafab0582aee532421ce2bc54a15c840bca535d54dce6714c",
    "04-knowledge/tables/s2-coverage.csv": "62e636475489f4e5cf1f24a4c428339fcbf61167c58d5d0cd6fa10118088212a",
    "04-knowledge/tables/mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    "04-knowledge/tables/book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_ENTRY = {
    **{f"Q-R.csv#{i}": "person" for i in (
        174, 175, 176, 177, 178, 183, 185, 186, 188, 189, 190, 191,
        *range(195, 215), *range(215, 220), 221,
    )},
    **{f"Q-R.csv#{i}": "work" for i in (179, 181, 184, 192, 194, 222)},
    **{f"Q-R.csv#{i}": "archive" for i in (182, 193)},
    "Q-R.csv#180": "event",
}
PENDING_TYPE = {
    "Q-R.csv#220": ("cand-2292", "Royal Collection", "collection"),
}
PRESERVED_EXCLUSIONS = {
    "Q-R.csv#187": (
        "cand-2927", "Rosenberg, Mme", "索引交叉引用：see under Wynne, Giustiniana",
    ),
}
EXPECTED_ENTRIES = {f"Q-R.csv#{i}" for i in range(174, 223)}
EXPECTED_SEGMENT_SHA256 = "2c81d1f96694e3f543218a28a71eaf941d702ee6f6f888764e5b19d81f01cdd5"
SEGMENT_RANGE = (2787, 2840)


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
    "method of selling pictures", "Rosenberg, Count", "Rospigliosi, Giulio",
    "Rosso, Andrea del", "Royal Collection", "Rubens, Peter Paul", "altarpiece for Chiesa Nuova",
)):
    raise SystemExit("p.467 right-column content check failed")
if "[Page 468]" in segment_text:
    raise SystemExit("next-page content leaked into p.467 right-column scope")

with QR_INDEX.open(encoding="utf-8-sig", newline="") as handle:
    qr_rows = list(csv.DictReader(handle))
if len(qr_rows) <= 222 or (qr_rows[174]["Main Entry"], qr_rows[222]["Sub-entry"]) != (
    "Rosa, Salvator", "altarpiece for Chiesa Nuova"
):
    raise SystemExit("Q-R.csv#174-222 boundary check failed")

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
) != (
    SOURCE_FILE, SEGMENT_RANGE[0], SEGMENT_RANGE[1], EXPECTED_SEGMENT_SHA256,
    EXPECTED_HASHES[SOURCE_FILE], True,
):
    raise SystemExit(f"p.467 manifest mismatch: {SEGMENT_ID}")

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
    raise SystemExit("p.467 right-column candidate mapping is incomplete")

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
for entry_id, (candidate_id, canonical_name, exclude_reason) in PRESERVED_EXCLUSIONS.items():
    row = candidate_by_entry[entry_id]
    if (row["candidate_id"], row["canonical_name"], row["status"], row["suggested_type"], row["exclude_reason"]) != (
        candidate_id, canonical_name, "excluded", "", exclude_reason,
    ):
        raise SystemExit(f"preserved index exclusion changed: {entry_id}")

coverage_by_segment = {row["segment_id"]: row for row in coverage}
coverage_row = coverage_by_segment.get(SEGMENT_ID)
if not coverage_row or (
    coverage_row["disposition"], coverage_row["migration_status"],
    coverage_row["source_line_ranges"], coverage_row["note"],
) != ("queued", "pending", "", ""):
    raise SystemExit("p.467 right-column coverage is not queued/pending")

for entry_id, entity_type in TYPE_BY_ENTRY.items():
    candidate_by_entry[entry_id]["suggested_type"] = entity_type

coverage_row.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L2787-2840",
    "note": (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.25 prints p.467; the physical right column contains "
        "Q-R.csv#174-222 (49 entries), from Salvator Rosa's method-of-selling-pictures subentry through Rubens's altarpiece for Chiesa Nuova. "
        "Types: 38 person, 6 work, 2 archive and 1 event; preserve Q-R#187 see-under alias as excluded. Q-R#220 Royal Collection is an "
        "identified collection, but taxonomy has no collection type; leave its type pending rather than substituting institution, archive or place. "
        "Rosa's Prometheus, Regulus, Tityus and Satire entries are distinguished as visual works or a textual work; #193 operatic librettos "
        "are archive, while the named opera S. Alessio (#194) is work. Rosa's refusal of the Paris invitation (#180) is a specific event; general "
        "career, opinion, patronage and person-association subentries remain person context. #178, #197, #204 and #211 do not establish formal "
        "relations. #207's grandfather wording and #202's paired Rossi names remain index context for later identity alignment. Printed p.467 "
        "confirms Pope Clement IX where S0 OCR reads EX and confirms Rousseau page digits where OCR spacing is split; candidate locators already "
        "match Q-R.csv and the printed page, so no locator correction was needed. Q-R.csv and S0 remain unchanged. Index navigation creates no "
        "mentions, book statements or formal relations."
    ),
})

counts = Counter(TYPE_BY_ENTRY.values())
summary = {
    "segment": SEGMENT_ID,
    "source_lines": [SEGMENT_RANGE[0], SEGMENT_RANGE[1], EXPECTED_SEGMENT_SHA256],
    "index_rows": len(EXPECTED_ENTRIES),
    "new_types": len(TYPE_BY_ENTRY),
    "final_type_counts_in_segment": dict(sorted(counts.items())),
    "preserved_excluded": sorted(PRESERVED_EXCLUSIONS),
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
