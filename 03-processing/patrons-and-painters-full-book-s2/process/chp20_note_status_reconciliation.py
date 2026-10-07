"""Reconcile stale Chapter 20 footnote-status wording in S2 statements.

The corresponding note segment is reviewed and linked. This migration changes
only qualifier text; it does not alter claims, endpoints, evidence, or statuses.
Default mode is dry-run. Use --apply after reviewing the displayed diff.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"

EXPECTED_STATEMENTS_SHA256 = "194dd0aabb70c1837481e688dd91bd9310922c87969245ac0133d3f02c0669d3"
EXPECTED_SOURCE_SHA256 = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
EXPECTED_PDF_SHA256 = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
EXPECTED_NOTE_SEGMENT_HASH = "c9b13ab8df240cbf07c4f19f102fde2c99efe285fda9138c95300fac3393ff1a"
EXPECTED_STATEMENT_COUNT = 12251
EXPECTED_CHANGED_ROWS = 63
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
NOTE_SEGMENT_ID = "chp-20:20_CHP-20Postscript:l211-280"
NOTE_STATEMENT_ID = "st-chp20-p403-n01-citation"

SPECIAL_REPLACEMENTS = (
    (
        "Footnote 7 cites the diary edition; it remains pending and the extracts have not been independently consulted",
        "Footnote 7 cites the diary edition and is transcribed and linked; the diary edition and extracts have not been independently consulted",
    ),
    (
        "Rosenberg's publication is cited by footnote 1, whose note text remains queued and has not been independently consulted",
        "Rosenberg's publication is cited by footnote 1, whose note is transcribed and linked; the cited article has not been independently consulted",
    ),
    (
        "Footnote 6 is linked to the queued notes segment and remains pending",
        "Footnote 6 is transcribed and linked in the reviewed notes segment",
    ),
    (
        "footnote 6 is linked to the queued notes segment and remains pending",
        "footnote 6 is transcribed and linked in the reviewed notes segment",
    ),
    (
        "Footnote 1 is linked to the queued notes segment",
        "Footnote 1 is transcribed and linked in the reviewed notes segment",
    ),
    (
        "Footnote 4 and the cited article remain unreviewed",
        "Footnote 4 is transcribed and linked; the cited article has not been independently consulted",
    ),
    (
        "Footnote 5 and the cited work remain pending",
        "Footnote 5 is transcribed and linked; the cited work has not been independently consulted",
    ),
    (
        "Footnote 3 and bibliographic reconciliation remain pending",
        "Footnote 3 is transcribed and linked; bibliographic reconciliation remains unresolved",
    ),
    (
        "The citations are footnotes 1-3 and remain queued",
        "The citations are footnotes 1-3 and are transcribed and linked",
    ),
    (
        "Footnote 1 identifies Matina's volume and remains queued",
        "Footnote 1 identifies Matina's volume and is transcribed and linked",
    ),
    (
        "The catalogue is cited by footnote 6, which remains pending",
        "The catalogue is cited by footnote 6, whose note is transcribed and linked",
    ),
    (
        "Footnote 1 is in the queued notes segment",
        "Footnote 1 is transcribed and linked in the reviewed notes segment",
    ),
    (
        "The footnote 1 reference remains pending note review",
        "The footnote 1 reference is transcribed and linked",
    ),
    (
        "retain the identity conflict pending the note and bibliography review/S3",
        "retain the identity conflict for S3 review after completed note and bibliography processing",
    ),
    (
        "the precise publication identities await note and bibliography review",
        "the precise publication identities remain unresolved for S3 comparison",
    ),
    (
        "the cited-source relation is pending note review",
        "footnote 4 is transcribed and linked to an unidentified Haskell 1967 publication; exact bibliography matching remains unresolved",
    ),
)

NUMBER = r"\d+(?:[-–]\d+)?"
STATUS_RE = re.compile(
    rf"\b((?:body\s+)?footnotes?)\s+({NUMBER}(?:\s*,\s*{NUMBER})?)\s+"
    r"(remains?|remain|is|are)\s+(pending|queued|unreviewed)\b",
    re.IGNORECASE,
)
STALE_RE = re.compile(
    rf"(?:footnotes?\s+{NUMBER}.{{0,100}}(?:pending|queued|unreviewed)"
    r"|pending note review|await note and bibliography review)",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_status(match: re.Match[str]) -> str:
    label, numbers, _verb, _status = match.groups()
    plural = label.lower().endswith("s") or any(mark in numbers for mark in (",", "-", "–"))
    return f"{label} {numbers} {'are' if plural else 'is'} transcribed and linked"


def normalize_qualification(value: str) -> str:
    for old, new in SPECIAL_REPLACEMENTS:
        value = value.replace(old, new)
    value = value.replace("the queued notes segment", "the reviewed notes segment")
    return STATUS_RE.sub(replace_status, value)


def validate_preconditions(lines: list[str]) -> tuple[list[str], list[tuple[str, str, str]]]:
    if sha256(STATEMENTS) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("book-statements.jsonl hash differs from the reviewed pre-state")
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256 or sha256(PDF) != EXPECTED_PDF_SHA256:
        raise SystemExit("Chapter 20 source or PDF differs from the reviewed source")
    if len(lines) != EXPECTED_STATEMENT_COUNT:
        raise SystemExit(f"expected {EXPECTED_STATEMENT_COUNT} statements, got {len(lines)}")

    segments = {}
    for line in SEGMENTS.open(encoding="utf-8"):
        row = json.loads(line)
        segments[row["segment_id"]] = row
    note_segment = segments.get(NOTE_SEGMENT_ID)
    if not note_segment or note_segment.get("sha256") != EXPECTED_NOTE_SEGMENT_HASH:
        raise SystemExit("reviewed Chapter 20 notes segment changed")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = {row["segment_id"]: row for row in csv.DictReader(handle)}
    note_coverage = coverage.get(NOTE_SEGMENT_ID)
    if not note_coverage or note_coverage.get("migration_status") != "complete":
        raise SystemExit("Chapter 20 notes are not marked reviewed/complete")

    rows = []
    rendered = []
    changes = []
    note_link_ids = set()
    for line in lines:
        row = json.loads(line)
        if row.get("segment_id", "").startswith("chp-20:"):
            q = row.get("qualifiers", {})
            old = q.get("qualification", "")
            new = normalize_qualification(old)
            if new != old:
                if q.get("footnote_text_pending") not in (False, None):
                    raise SystemExit(f"unexpected note-pending state: {row['statement_id']}")
                linked_segment = q.get("footnote_segment")
                if linked_segment and linked_segment != NOTE_SEGMENT_ID:
                    raise SystemExit(f"unexpected note segment: {row['statement_id']} -> {linked_segment}")
                refs = q.get("footnote_refs", [])
                if refs and any(ref.get("segment_id") != NOTE_SEGMENT_ID for ref in refs):
                    raise SystemExit(f"unexpected footnote ref segment: {row['statement_id']}")
                if not linked_segment and not refs:
                    note_link_ids.add(row["statement_id"])
                q["qualification"] = new
                row["qualifiers"] = q
                changes.append((row["statement_id"], old, new))
                ending = "\r\n" if line.endswith("\r\n") else "\n"
                line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + ending
        rows.append(row)
        rendered.append(line)

    if len(changes) != EXPECTED_CHANGED_ROWS:
        raise SystemExit(f"expected {EXPECTED_CHANGED_ROWS} qualifier changes, got {len(changes)}")
    if note_link_ids != {"st-chp20-p403-alazard-commissioned-franceschini-picture"}:
        raise SystemExit(f"unexpected unstructured footnote-link cases: {sorted(note_link_ids)}")
    if not any(row.get("statement_id") == NOTE_STATEMENT_ID for row in rows):
        raise SystemExit(f"required note statement missing: {NOTE_STATEMENT_ID}")
    for row in rows:
        if row.get("segment_id", "").startswith("chp-20:") and STALE_RE.search(
            row.get("qualifiers", {}).get("qualification", "")
        ):
            raise SystemExit(f"stale footnote status remains: {row['statement_id']}")
    return rendered, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write reviewed qualifier changes")
    args = parser.parse_args()

    original = STATEMENTS.read_text(encoding="utf-8")
    rendered, changes = validate_preconditions(original.splitlines(keepends=True))
    print(f"mode={'apply' if args.apply else 'dry-run'} changed_qualifiers={len(changes)}")
    for statement_id, old, new in changes:
        print(f"{statement_id}\n  - {old}\n  + {new}")
    if not args.apply:
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp20-note-status-"))
    backup = backup_dir / STATEMENTS.name
    shutil.copy2(STATEMENTS, backup)
    fd, temp_name = tempfile.mkstemp(prefix="book-statements-", suffix=".tmp", dir=TABLES)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.writelines(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, STATEMENTS)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise

    print(f"backup={backup}")
    print(f"new_sha256={sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
