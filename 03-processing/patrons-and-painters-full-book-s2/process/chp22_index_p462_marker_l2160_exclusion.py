#!/usr/bin/env python3
"""Exclude the generated p.462 page marker; it is not an index entry."""

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
SEGMENT_ID = "chp-22:22_CHP-22Index:l2160-2160"
SEGMENT_SHA = "90c5fdd0ebd9b2d61215fa47d924a6fc65806b34136a4af326cad54ef301fb09"
ASSET_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p462-marker-l2160-20261007"

EXPECTED_HASHES = {
    INDEX_MD: ASSET_SHA,
    INDEX_PDF: "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "eb3c215a5d8ff479d006c17b10f128fef6903c72a686bfa05c3d145cd9c88f76",
    TABLES / "s2-coverage.csv": "d5bffdf1ec7c0ebc7c907f1c14d1e762e32f8adad07802ab61cc2b132c8e2bba",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
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
parser.add_argument("--apply", action="store_true", help="write the coverage exclusion")
ARGS = parser.parse_args()

for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
marker = source_lines[2159]
if marker != "[Page 462]" or hashlib.sha256(marker.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 L2160 is no longer the expected page marker")

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
) != (SOURCE_FILE, 2160, 2160, SEGMENT_SHA, ASSET_SHA, True):
    raise SystemExit("S0 p.462 marker manifest changed")

candidate_path = TABLES / "entity-candidates.csv"
candidates = read_csv(candidate_path)[1]
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

target = next((row for row in coverage if row["segment_id"] == SEGMENT_ID), None)
if not target or (
    target["disposition"], target["migration_status"], target["source_line_ranges"], target["note"]
) != ("queued", "pending", "", ""):
    raise SystemExit("p.462 marker coverage state changed")
target.update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L2160",
    "note": (
        "no_semantic_content: S0 L2160 `[Page 462]` is a generated page marker. CHP-22Index.pdf "
        "physical p.20 visibly prints p.462; the one-line segment is excluded/complete as navigation, "
        "with no candidate, mention, book statement or relation."
    ),
})

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "coverage_after_apply": {"complete": 653, "excluded": 142, "queued": 37},
    "candidate_rows": len(candidates),
    "mentions_unchanged": len(mentions),
    "statements_unchanged": len(statements),
}
if ARGS.apply:
    backup = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"migration backup already exists; refusing to overwrite: {backup.name}")
    shutil.copy2(coverage_path, backup)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backup"] = str(backup.relative_to(ROOT))
print(json.dumps(result, ensure_ascii=False, indent=2))
