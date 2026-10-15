"""Restore p.267 section-II opening mentions and classify its two open claims."""
from __future__ import annotations

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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
BODY_BACKUP = TABLES / "mentions.csv.bak-s2-chp9-notes-p268-p275-20261002"
SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l3-4"
EXPECTED_HASHES = {
    MENTIONS: "a2d657512d0a2219597001b8abb264f7b10d940735711c30d4fc1833257f8204",
    STATEMENTS: "d1f0bed6a8a979ad611d117616e8a09380b14f5e7ca40b98679781e6a0975bd1",
    COVERAGE: "3c8cd33a99fdedd8d4eb6dc31eb3fb91c9a22b5d4c5391b447b09a7c4cd2bcd8",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    BODY_BACKUP: "d9a81391d871228faba35176e19eab145ab85733f88b556881365864e059c32e",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p267-section2-reconciliation-20261014"
CLASSIFICATIONS = {
    "st-chp9-sec2-casanova-attitude-source-reference": False,
    "st-chp9-sec2-religious-political-dissent-maxim": False,
}
REASONS = {
    "st-chp9-sec2-casanova-attitude-source-reference": (
        "S2: the note is an internal source pointer to Bozzòla and supplies no description of Casanova's attitude; "
        "it is not a substantive entity relation."
    ),
    "st-chp9-sec2-religious-political-dissent-maxim": (
        "S2: this is Haskell's report of a general maxim, not a concrete relation between identified historical entities; "
        "retain the statement with its attributed and qualified status."
    ),
}
EXPECTED_GLOBAL_BEFORE = {True: 9684, False: 4016, None: 1129}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(f.name)
    temp_path.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(f.name)
    temp_path.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"fingerprint changed; inspect before continuing: {path.relative_to(ROOT)}")

segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
meta = segments.get(SEGMENT_ID)
if meta is None or meta["sha256"] != "4a2b6206e3c4df9b60be079003432ebc618752ba7791e3904f2267eb9b5b964b" or meta["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
    raise SystemExit(f"unexpected reviewed p.267 section-II segment: {SEGMENT_ID}")

candidate_fields, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

_, backup_rows = read_csv(BODY_BACKUP)
new_mentions = [row for row in backup_rows if row["segment_id"] == SEGMENT_ID]
if len(new_mentions) != 12 or len({row["mention_id"] for row in new_mentions}) != 12:
    raise SystemExit(f"expected 12 unique p.267 section-II mentions, found {len(new_mentions)}")
if any(row["mention_id"] in {m["mention_id"] for m in current_mentions} for row in new_mentions):
    raise SystemExit("one or more p.267 section-II mentions are already present")
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in current_mentions}
new_spans = set()
segment_text = "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])
for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in existing_spans or span in new_spans:
        raise SystemExit(f"duplicate mention span: {row['mention_id']}")
    if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"source-span mismatch: {row['mention_id']}")
    new_spans.add(span)

unset_ids = {
    row["statement_id"] for row in statement_rows
    if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
}
if unset_ids != set(CLASSIFICATIONS) or set(CLASSIFICATIONS) != set(REASONS):
    raise SystemExit(f"unexpected p.267 section-II unset statements: {sorted(unset_ids)}")
for statement_id, value in CLASSIFICATIONS.items():
    qualifiers = statement_by_id[statement_id]["qualifiers"]
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit(f"statement is no longer unset: {statement_id}")
    qualifiers["relation_candidate"] = value
    reason = REASONS[statement_id]
    qualification = qualifiers.get("qualification", "").strip()
    if reason not in qualification:
        qualifiers["qualification"] = (qualification + " " + reason).strip()

before = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in read_jsonl(STATEMENTS))
after = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in statement_rows)
if dict(before) != EXPECTED_GLOBAL_BEFORE:
    raise SystemExit(f"unexpected global classification baseline: {dict(before)}")
if after[True] != before[True] or after[False] != before[False] + 2 or after[None] != before[None] - 2:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

coverage = coverage_by_id.get(SEGMENT_ID)
if coverage is None or coverage["migration_status"] != "complete":
    raise SystemExit(f"unexpected p.267 S2 coverage state: {coverage}")
coverage["note"] += (
    " 2026-10-14 reconciliation restored 12 omitted p.267 section-II opening and note 6 mentions from the dated "
    "migration backup after source-span checks; the two remaining claims were classified as non-relational source pointer/general maxim."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_page": 267,
    "pdf_physical_page": 33,
    "recovered_mentions": len(new_mentions),
    "mention_line_distribution": dict(Counter(row["start_char"] for row in new_mentions)),
    "classified_statements": {"true": 0, "false": 2, "unset_closed": 2},
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write verified p.267 section-II mentions and classifications")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.267 section-II backups already exist")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    try:
        write_csv(MENTIONS, mention_fields, current_mentions + new_mentions)
        write_jsonl(STATEMENTS, statement_rows)
        write_csv(COVERAGE, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(path.name for path in backups))
