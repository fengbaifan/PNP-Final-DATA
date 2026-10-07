"""Reconcile p.180 statements with completed notes 1, 3, and 4.

Only qualifier wording changes. Default mode is dry-run; --apply writes the
reviewed plan after exact source, table, segment, and row preconditions pass.
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
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"

EXPECTED_STATEMENTS_SHA256 = "d385ab8a4836c88926b8dcfc77fc55c912dd3f2007510e38df23755b4b3b15fb"
EXPECTED_SOURCE_SHA256 = "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3"
EXPECTED_PDF_SHA256 = "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212"
EXPECTED_NOTES_SEGMENT_SHA256 = "ad9ae34a8e0247ade77cf812cd0d5943582c3fd615590da5064cef79c38ae28b"
NOTES_SEGMENT_ID = "chp-7:07_CHP-7_sec_i:l293-389"

REPLACEMENTS = {
    "st-chp7-p180-i22": (
        "This is Haskell's historiographic characterization; p.180 footnote 1 at composite L335 remains to be migrated.",
        "This is Haskell's historiographic characterization; p.180 footnote 1 at composite L335 is transcribed and linked. The cited work was not independently consulted.",
    ),
    "st-chp7-p180-i30": (
        "Retain 'seems'; footnote 3 at composite L337 gives a chronology qualification and is still pending.",
        "Retain 'seems'; footnote 3 at composite L337 is transcribed and linked. It gives Haskell's qualified chronology assessment and reports Mahon's suggested 1632 purchase date, which does not itself establish the commission date.",
    ),
    "st-chp7-p180-i34": (
        "Retain 'may' and the aesthetic judgment. Footnotes 3–4 at composite L337–338 remain pending and may qualify chronology and locations.",
        "Retain 'may' and the aesthetic judgment. Footnote 3 is transcribed and linked; it gives a qualified chronology assessment and reports Mahon's suggested purchase date for 'the two Poussins'. Footnote 4 is transcribed and linked; it lists the Louvre and Institute of Arts, Detroit and cites Nicolas Poussin, pp.46 and 65, without mapping each work to a location. The cited pages were not independently consulted, so the pair-level endpoint mapping remains unresolved.",
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_plan(lines: list[str]) -> tuple[list[str], list[tuple[str, str, str]]]:
    if digest(STATEMENTS) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("statement table differs from the reviewed pre-state")
    if digest(SOURCE) != EXPECTED_SOURCE_SHA256 or digest(PDF) != EXPECTED_PDF_SHA256:
        raise SystemExit("Chapter 7 source or PDF differs from the reviewed material")

    segment_rows = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.open(encoding="utf-8"))
    }
    segment = segment_rows.get(NOTES_SEGMENT_ID)
    if not segment or segment.get("sha256") != EXPECTED_NOTES_SEGMENT_SHA256:
        raise SystemExit("p.180 note segment changed")
    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = {row["segment_id"]: row for row in csv.DictReader(handle)}
    status = coverage.get(NOTES_SEGMENT_ID)
    if not status or status.get("disposition") != "reviewed" or status.get("migration_status") != "complete":
        raise SystemExit("p.180 note segment is not reviewed/complete")

    found: set[str] = set()
    changes: list[tuple[str, str, str]] = []
    rendered: list[str] = []
    for line in lines:
        row = json.loads(line)
        sid = row.get("statement_id")
        if sid in REPLACEMENTS:
            if sid in found:
                raise SystemExit(f"duplicate target statement: {sid}")
            found.add(sid)
            if row.get("segment_id") != "chp-7:07_CHP-7_sec_i:l128-138":
                raise SystemExit(f"unexpected source segment for {sid}")
            old, new = REPLACEMENTS[sid]
            q = row.get("qualifiers", {})
            if q.get("qualification") != old:
                raise SystemExit(f"qualification precondition failed: {sid}")
            q["qualification"] = new
            row["qualifiers"] = q
            changes.append((sid, old, new))
            ending = "\r\n" if line.endswith("\r\n") else "\n"
            line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + ending
        rendered.append(line)

    if found != set(REPLACEMENTS):
        raise SystemExit(f"target statements missing: {sorted(set(REPLACEMENTS) - found)}")
    if len(changes) != 3:
        raise SystemExit(f"expected 3 qualifier updates, got {len(changes)}")

    # The pair-level note remains an open candidate with the reviewed endpoint sets.
    pair = None
    for line in rendered:
        row = json.loads(line)
        if row.get("statement_id") == "st-chp7-p180-n4-pair-location":
            pair = row
            break
    if not pair or pair.get("subject_candidate_id") is not None or pair.get("object_candidate_id") is not None:
        raise SystemExit("the pair-level location candidate is missing or its open endpoints changed")
    endpoint_sets = pair.get("qualifiers", {}).get("candidate_endpoint_sets", {})
    if endpoint_sets.get("subject_candidate_ids") != ["cand-6773", "cand-6774"]:
        raise SystemExit("the Poussin work endpoint set changed")
    if endpoint_sets.get("object_candidate_ids") != ["cand-4589", "cand-7072"]:
        raise SystemExit("the museum endpoint set changed")
    return rendered, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed qualifier changes")
    args = parser.parse_args()

    rendered, changes = make_plan(STATEMENTS.read_text(encoding="utf-8").splitlines(keepends=True))
    print(f"mode={'apply' if args.apply else 'dry-run'} changed_qualifiers={len(changes)}")
    for statement_id, old, new in changes:
        print(f"{statement_id}\n  - {old}\n  + {new}")
    if not args.apply:
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp7-p180-note-status-"))
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
    print(f"new_sha256={digest(STATEMENTS)}")


if __name__ == "__main__":
    main()
