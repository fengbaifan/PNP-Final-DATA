#!/usr/bin/env python3
"""Correct the p.457 Guercino refusal subentry from person to event."""

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
BOOK_SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
TAXONOMY = ROOT / "01-domain" / "taxonomy-registry.md"
BACKUP_SUFFIX = ".bak-s2-p457-guercino-refusal-event-20261007"

EXPECTED_HASHES = {
    INDEX_MD: "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    BOOK_SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
    TAXONOMY: "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    TABLES / "segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    TABLES / "entity-candidates.csv": "5745a9056d2ff3342b66394340aa8cae279171f7a273aede3157e3bc252e9033",
    TABLES / "s2-coverage.csv": "fa4112da4089950dd41f3b41ea937e4571f575cdd17bf36808829e46b4eb773a",
    TABLES / "mentions.csv": "40369a368c447b70d4a98ae4d11e96153f1d8b301b71b29552f5c92cdae75477",
    TABLES / "book-statements.jsonl": "ad073451203e5172739b13859d2b58f80af8debc57eda3c8a0b08eee5d0b16b5",
}
SEGMENT_ID = "chp-22:22_CHP-22Index:l1595-1649"
OLD_NOTE = "Guercino's refusal of an invitation and work for Ruffo remain person context; named paintings are works."
NEW_NOTE = "G#177 Guercino's refusal of Charles I's invitation is a discrete event (book p.178); G#184 work for Ruffo remains person context, and named paintings are works."
OLD_TYPE_COUNTS = "46 typed as 30 person, 11 work, 2 archive and 3 term;"
NEW_TYPE_COUNTS = "46 typed as 29 person, 11 work, 2 archive, 3 term and 1 event;"

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
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"source or S2 pre-state changed: {path.relative_to(ROOT)}")

book_text = BOOK_SOURCE.read_text(encoding="utf-8-sig")
if "[Page 178]" not in book_text or "Guercino ‘refused to accept" not in book_text:
    raise SystemExit("book p.178 evidence for the discrete refusal is missing")
taxonomy_text = TAXONOMY.read_text(encoding="utf-8-sig")
if "| event | 事件 |" not in taxonomy_text:
    raise SystemExit("event is not a current taxonomy type")

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
    raise SystemExit("unexpected S2 state")

by_candidate = {row["candidate_id"]: row for row in candidates}
target = by_candidate.get("cand-1267")
if not target or (target["index_entry_id"], target["canonical_name"], target["suggested_type"], target["status"]) != (
    "G.csv#177", "Guercino (Francesco Barbieri)", "person", "open"
):
    raise SystemExit("cand-1267 is not in the expected pre-correction state")

by_segment = {row["segment_id"]: row for row in coverage}
coverage_row = by_segment.get(SEGMENT_ID)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.457 left-column segment is not complete")
if OLD_NOTE not in coverage_row["note"]:
    raise SystemExit("expected p.457 left-column rationale was not found")
if OLD_TYPE_COUNTS not in coverage_row["note"]:
    raise SystemExit("expected p.457 left-column type counts were not found")

target["suggested_type"] = "event"
coverage_row["note"] = coverage_row["note"].replace(OLD_NOTE, NEW_NOTE)
coverage_row["note"] = coverage_row["note"].replace(OLD_TYPE_COUNTS, NEW_TYPE_COUNTS)
if OLD_NOTE in coverage_row["note"]:
    raise SystemExit("old classification rationale remains")
if OLD_TYPE_COUNTS in coverage_row["note"]:
    raise SystemExit("old p.457 left-column type counts remain")

scope_ids = (
    {f"G.csv#{i}" for i in range(177, 196)}
    | {f"H.csv#{i}" for i in range(0, 25)}
    | {f"I.csv#{i}" for i in range(0, 5)}
)
scope = [row for row in candidates if row["index_entry_id"] in scope_ids]
typed_counts = Counter(row["suggested_type"] for row in scope if row["suggested_type"])
expected_types = Counter({"person": 29, "work": 11, "archive": 2, "term": 3, "event": 1})
if len(scope) != 49 or typed_counts != expected_types:
    raise SystemExit(f"unexpected p.457 left-column types after correction: {typed_counts}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "candidate_update": {"candidate_id": "cand-1267", "index_entry_id": "G.csv#177", "from": "person", "to": "event"},
    "evidence": "07_CHP-7_sec_i.md p.178; taxonomy-registry.md event type",
    "type_counts": dict(typed_counts),
    "coverage_disposition": [coverage_row["disposition"], coverage_row["migration_status"]],
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
