#!/usr/bin/env python3
"""Attach the explicit France endpoint to the p.335 book-success statement.

Default mode is a no-write preview. Apply only after the table/source/mention
preconditions and endpoint interpretation have been reviewed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp13-p335-france-endpoint-20261015"
STATEMENT_ID = "st-chp13-p335-gerusalemme-success-in-france"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l32-39"
FRANCE_CANDIDATE_ID = "cand-5317"
FRANCE_MENTION_ID = "m-s2-ch13-p335-031"
EXPECTED_STATEMENTS_SHA256 = "86fef0a906bbad4710a557a4d8d6f9aef24ba5ff9bd4826d9f5e4f3aba0829da"
EXPECTED_SOURCE_SHA256 = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def check_preconditions() -> tuple[list[str], int]:
    if sha256(STATEMENTS) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("statement table hash changed; re-review before applying")
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("p.335 source hash changed; re-review before applying")

    rows = load_rows(STATEMENTS)
    matches = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"expected one {STATEMENT_ID}, found {len(matches)}")
    row = matches[0]
    if (
        row.get("segment_id") != SEGMENT_ID
        or row.get("subject_candidate_id") != "cand-9990"
        or row.get("object_candidate_id") is not None
        or row.get("predicate") != "successful_in_france"
        or row.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("statement no longer has the reviewed blank-object state")

    candidates = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
    france = [row for row in candidates if row.get("candidate_id") == FRANCE_CANDIDATE_ID]
    if len(france) != 1 or france[0].get("canonical_name") != "France" or france[0].get("suggested_type") != "place":
        raise SystemExit("France candidate identity/type changed; re-review before applying")

    mentions = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
    mention = [row for row in mentions if row.get("mention_id") == FRANCE_MENTION_ID]
    if len(mention) != 1:
        raise SystemExit(f"expected one {FRANCE_MENTION_ID}, found {len(mention)}")
    mention = mention[0]
    if (
        mention.get("candidate_id") != FRANCE_CANDIDATE_ID
        or mention.get("segment_id") != SEGMENT_ID
        or mention.get("surface_form") != "France"
    ):
        raise SystemExit("France mention mapping changed; re-review before applying")

    segments = [row for row in load_rows(SEGMENTS) if row.get("segment_id") == SEGMENT_ID]
    if len(segments) != 1:
        raise SystemExit(f"expected one source segment {SEGMENT_ID}, found {len(segments)}")
    segment = segments[0]
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
    start, end = int(mention["start_char"]), int(mention["end_char"])
    if segment_text[start:end] != "France":
        raise SystemExit("France mention span no longer matches the source segment")
    if "success in France" not in row.get("original_quote", ""):
        raise SystemExit("statement quote does not identify the France success claim")
    return rows, next(i for i, item in enumerate(rows) if item.get("statement_id") == STATEMENT_ID)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed endpoint after all preconditions pass")
    args = parser.parse_args()

    rows, index = check_preconditions()
    before = rows[index]
    after = dict(before)
    after["object_candidate_id"] = FRANCE_CANDIDATE_ID
    print(json.dumps({"mode": "apply" if args.apply else "preview", "before": before, "after": after}, ensure_ascii=False))
    if not args.apply:
        return 0
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    original_lines = STATEMENTS.read_text(encoding="utf-8").splitlines(keepends=True)
    row_index = next(i for i, line in enumerate(original_lines) if json.loads(line).get("statement_id") == STATEMENT_ID)
    shutil.copy2(STATEMENTS, BACKUP)
    newline = "\r\n" if original_lines[row_index].endswith("\r\n") else "\n"
    original_lines[row_index] = json.dumps(after, ensure_ascii=False, separators=(",", ":")) + newline
    fd, temp_name = tempfile.mkstemp(prefix="book-statements-", suffix=".tmp", dir=TABLES)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.writelines(original_lines)
        os.replace(temp_name, STATEMENTS)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)

    verified = load_rows(STATEMENTS)
    final = next(item for item in verified if item.get("statement_id") == STATEMENT_ID)
    if final.get("object_candidate_id") != FRANCE_CANDIDATE_ID:
        raise SystemExit("post-write verification failed; restore from the recorded backup")
    print(json.dumps({"backup": str(BACKUP), "statements_sha256": sha256(STATEMENTS), "object_candidate_id": final["object_candidate_id"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
