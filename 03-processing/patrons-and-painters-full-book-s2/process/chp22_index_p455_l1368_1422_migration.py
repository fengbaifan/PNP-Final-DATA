#!/usr/bin/env python3
"""Classify the left-column index candidates on printed p.455."""

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
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1368-1422"
SEGMENT_SHA = "8c5046de3419d0de78de4241439b00f4a579ce72237381faaea3a047b1658c39"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p455-left-l1368-1422-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    INDEX_DIR / "F.csv": "746710c8b4f91bb2bfc6d4659181e0c954f02be77326ba6be200b11b5b036b44",
    INDEX_DIR / "G.csv": "071ab1e6546d2d01b43e8a83042527e439598af098f8b6a7d49eef3b2234915d",
    TABLES / "entity-candidates.csv": "a32bab356e042a030bcf4050f4515606684d9f5886f73eee3950111ae02e925c",
    TABLES / "s2-coverage.csv": "634ab36322d54e51f8c9b989b1a2d72d76734d778f9b3137c99ec842a072c680",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

TYPE_BY_INDEX_ID = {
    "F.csv#93": "person",
    "F.csv#96": "person",
    "F.csv#97": "person",
    "F.csv#98": "institution",
    "F.csv#99": "term",
    "F.csv#100": "term",
    "F.csv#101": "term",
    "F.csv#102": "term",
    "F.csv#103": "person",
    "F.csv#104": "person",
    "F.csv#105": "person",
    "F.csv#106": "work",
    "F.csv#107": "work",
    "F.csv#108": "person",
    "F.csv#109": "person",
    "G.csv#0": "person",
    "G.csv#1": "person",
    "G.csv#2": "work",
    "G.csv#3": "person",
    "G.csv#4": "person",
    "G.csv#5": "person",
    "G.csv#6": "person",
    "G.csv#7": "person",
    "G.csv#8": "person",
    "G.csv#9": "person",
    "G.csv#10": "archive",
    "G.csv#11": "person",
    "G.csv#12": "person",
    "G.csv#13": "person",
    "G.csv#14": "archive",
    "G.csv#15": "person",
    "G.csv#16": "person",
    "G.csv#17": "archive",
    "G.csv#18": "person",
    "G.csv#19": "person",
    "G.csv#20": "person",
    "G.csv#21": "person",
    "G.csv#22": "person",
    "G.csv#23": "person",
    "G.csv#24": "person",
    "G.csv#25": "work",
    "G.csv#26": "work",
    "G.csv#27": "work",
    "G.csv#28": "work",
    "G.csv#29": "person",
}
EXCLUDED = {"F.csv#94": "cand-2904", "F.csv#95": "cand-2905"}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path, encoding="utf-8-sig"):
    with path.open(encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1367:1422])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")

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
    segment.get("source_file"),
    segment.get("line_start"),
    segment.get("line_end"),
    segment.get("sha256"),
    segment.get("asset_sha256"),
) != (SOURCE_FILE, 1368, 1422, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 segment manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
coverage_fields, coverage = read_csv(coverage_path)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(candidates), len(coverage), len(mentions), len(statements)) != (11436, 832, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

coverage_by_id = {row["segment_id"]: row for row in coverage}
target_coverage = coverage_by_id.get(SEGMENT_ID)
previous_marker = coverage_by_id.get("chp-22:22_CHP-22Index:l1365-1366")
next_column = coverage_by_id.get("chp-22:22_CHP-22Index:l1424-1477")
if not target_coverage or (target_coverage["disposition"], target_coverage["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
if not previous_marker or (previous_marker["disposition"], previous_marker["migration_status"]) != ("excluded", "complete"):
    raise SystemExit("p.455 marker/running header is not complete")
if not next_column or (next_column["disposition"], next_column["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.455 right-column segment is not queued")

index_csvs = {
    "F.csv": read_csv(INDEX_DIR / "F.csv")[1],
    "G.csv": read_csv(INDEX_DIR / "G.csv")[1],
}
candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
expected_index_ids = {f"F.csv#{n}" for n in range(93, 110)} | {f"G.csv#{n}" for n in range(30)}
if set(TYPE_BY_INDEX_ID) | set(EXCLUDED) != expected_index_ids:
    raise SystemExit("explicit p.455 left-column decisions do not cover exactly the source entries")
if len(TYPE_BY_INDEX_ID) != 45:
    raise SystemExit(f"expected 45 explicit type decisions, found {len(TYPE_BY_INDEX_ID)}")

candidate_updates = []
excluded = {}
type_counts = Counter()
for index_entry_id in sorted(expected_index_ids, key=lambda value: (value[0], int(value.split("#")[1]))):
    csv_name, row_text = index_entry_id.split("#")
    row_number = int(row_text)
    source_row = index_csvs[csv_name][row_number]
    candidate = candidate_by_index_id.get(index_entry_id)
    if not candidate:
        raise SystemExit(f"missing S1 candidate: {index_entry_id}")
    if csv_name == "F.csv":
        expected_number = {93: 1078, 94: 2904, 95: 2905}.get(row_number, 1079 + row_number - 96)
    else:
        expected_number = 1093 + row_number
    expected_candidate_id = f"cand-{expected_number:04d}"
    if candidate["candidate_id"] != expected_candidate_id:
        raise SystemExit(f"unexpected candidate mapping for {index_entry_id}: {candidate['candidate_id']}")
    if candidate["canonical_name"] != source_row["Main Entry"] or candidate["sub_entry"] != source_row["Sub-entry"]:
        raise SystemExit(f"S1 headword/subentry mismatch for {index_entry_id}")

    if index_entry_id in EXCLUDED:
        if candidate["candidate_id"] != EXCLUDED[index_entry_id] or candidate["status"] != "excluded":
            raise SystemExit(f"see-under alias is not preserved as excluded: {index_entry_id}")
        excluded[index_entry_id] = candidate["candidate_id"]
    else:
        suggested_type = TYPE_BY_INDEX_ID[index_entry_id]
        if candidate["status"] != "open" or candidate["suggested_type"]:
            raise SystemExit(f"candidate is not open/untyped: {candidate['candidate_id']}")
        candidate["suggested_type"] = suggested_type
        candidate_updates.append(
            {
                "index_entry_id": index_entry_id,
                "candidate_id": candidate["candidate_id"],
                "canonical_name": candidate["canonical_name"],
                "sub_entry": candidate["sub_entry"],
                "suggested_type": suggested_type,
            }
        )
        type_counts[suggested_type] += 1

expected_types = Counter({"person": 30, "work": 7, "term": 4, "archive": 3, "institution": 1})
if len(candidate_updates) != 45 or type_counts != expected_types or len(excluded) != 2:
    raise SystemExit(f"unexpected p.455 left-column decisions: types={type_counts}; excluded={excluded}")

target_coverage.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L1368-1422",
    note=(
        "no_semantic_content: index-navigation-only. CHP-22Index.pdf physical p.13 visibly prints p.455. S0 L1368-1422 "
        "covers the complete left-column entries F.csv#93-109 and G.csv#0-29; F#94-95 are excluded see-under aliases. "
        "The linewise OCR appends alphabetical navigation fragments from the right column; these are not separately "
        "classified here, and the full right-column entries are covered by L1424-1477. Forty-five open candidates are typed "
        "as 30 person, 7 work, 4 term, 3 archive and 1 institution. F#108 is Furlani in the printed page and index CSV; "
        "the S0 OCR spelling Furiani is not changed. F#98 French Academy in Rome is an institution; general French "
        "hostility/patronage headings are terms. G#10 Della Moneta, G#14 Dialogo and G#17 Trattato are documentary/literary "
        "works (archive); named pictorial subjects and Gaulli's church fresco are works. Index locators add no mentions, "
        "book statements or relations."
    ),
)

after = {
    "candidate_count": len(candidates),
    "mention_count": len(mentions),
    "statement_count": len(statements),
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
    "open_index_untyped": sum(bool(item["index_entry_id"]) and item["status"] == "open" and not item["suggested_type"] for item in candidates),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 640,
    "coverage_queued": 57,
    "coverage_excluded": 135,
    "coverage_partial": 0,
    "open_index_untyped": 1746,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_page": 455,
    "pdf_physical_page": 13,
    "candidate_updates": candidate_updates,
    "type_counts": dict(type_counts),
    "excluded_aliases": excluded,
    **after,
}
if ARGS.apply:
    backups = []
    for path in (candidate_path, coverage_path):
        backup_path = path.with_name(path.name + BACKUP_SUFFIX)
        if backup_path.exists():
            raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup_path.name}")
        backups.append((path, backup_path))
    for path, backup_path in backups:
        shutil.copy2(path, backup_path)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backups"] = [str(path.relative_to(ROOT)) for _source, path in backups]

print(json.dumps(result, ensure_ascii=False, indent=2))
