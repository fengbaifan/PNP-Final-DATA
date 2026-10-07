#!/usr/bin/env python3
"""Exclude the printed page marker on physical p.14 / printed p.456."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l1479-1479"
SEGMENT_SHA = "017e3e0fde4174d0c1c045f7d6dc3bfc390f5511b7430324bdd9656db6eae4a5"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p456-marker-l1479-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "a73139532f4b5d18a7e0994c7d007c5dc5bb3109f7133e6506476ba5d6161eef",
    TABLES / "s2-coverage.csv": "e732439350b59ee94782f98b9ac5d43ad804ded4351e1730d9394a7f4fc50222",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


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
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[1478:1479])
if segment_text != "[Page 456]" or hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 page marker changed")

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
) != (SOURCE_FILE, 1479, 1479, SEGMENT_SHA, ASSET_SHA):
    raise SystemExit("S0 page-marker manifest changed")

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
target = coverage_by_id.get(SEGMENT_ID)
previous = coverage_by_id.get("chp-22:22_CHP-22Index:l1424-1477")
next_left = coverage_by_id.get("chp-22:22_CHP-22Index:l1481-1535")
if not target or (target["disposition"], target["migration_status"]) != ("queued", "pending"):
    raise SystemExit("page-marker segment is not queued")
if not previous or (previous["disposition"], previous["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.455 right-column segment is not complete")
if not next_left or (next_left["disposition"], next_left["migration_status"]) != ("queued", "pending"):
    raise SystemExit("next p.456 left-column segment is not queued")

target.update(
    disposition="excluded",
    migration_status="complete",
    source_line_ranges="L1479-1479",
    note=(
        "no_semantic_content: S0 L1479 [Page 456] is a generated page locator. CHP-22Index.pdf physical p.14 visibly "
        "prints p.456; the marker is navigation, not an index entry or book-fact claim. The running header at L1481 is "
        "covered with the following left-column segment."
    ),
)

after = {
    "coverage_complete": sum(item["disposition"] == "reviewed" and item["migration_status"] == "complete" for item in coverage),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(item["disposition"] == "reviewed" and item["migration_status"] == "partial" for item in coverage),
}
expected_after = {"coverage_complete": 641, "coverage_queued": 55, "coverage_excluded": 136, "coverage_partial": 0}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {"mode": "apply" if ARGS.apply else "dry-run", "source_segment": SEGMENT_ID, "printed_page": 456, "pdf_physical_page": 14, **after}
if ARGS.apply:
    backup_path = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup_path.exists():
        raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup_path.name}")
    shutil.copy2(coverage_path, backup_path)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backup"] = str(backup_path.relative_to(ROOT))

print(json.dumps(result, ensure_ascii=False, indent=2))
