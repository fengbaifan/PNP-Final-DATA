#!/usr/bin/env python3
"""Complete the reused Northall archive candidate from bibliography p. 431."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
SEGMENT = "chp-21:21_CHP-21Bibliography:l846-881"
SEGMENT_SHA = "452e318c5db9d0281edb596dd0af17224ccd515db43cf082daf86a0adc35fb08"
BACKUP = ".bak-s2-chp21-bibliography-l846-881-northall-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[845:881])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text/hash changed")
if not source_lines[878].startswith("Northall, John: Travels through Italy, London 1767."):
    raise SystemExit("Northall bibliography entry changed")

candidate_path = TABLES / "entity-candidates.csv"
statement_path = TABLES / "book-statements.jsonl"
with candidate_path.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    candidate_fields = reader.fieldnames
    candidates = list(reader)
statements = [
    json.loads(line)
    for line in statement_path.read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if len(candidates) != 11388 or len(statements) != 11816:
    raise SystemExit("unexpected Northall follow-up pre-state")

candidate = next((row for row in candidates if row["candidate_id"] == "cand-10216"), None)
if not candidate or candidate["suggested_type"] != "archive":
    raise SystemExit("Northall archive candidate missing or wrong type")
if candidate["canonical_name"] != "John Northall, 1767, p.438 (short-form cited source; title unresolved)":
    raise SystemExit("Northall candidate pre-state changed")

statement = next(
    (
        row
        for row in statements
        if row.get("segment_id") == SEGMENT
        and row.get("object_candidate_id") == "cand-10216"
    ),
    None,
)
if not statement or statement.get("predicate") != "bibliography_lists_publication":
    raise SystemExit("Northall bibliography statement missing")
if statement.get("original_quote") != source_lines[878]:
    raise SystemExit("Northall bibliography statement quote changed")

candidate["canonical_name"] = "John Northall, Travels through Italy (London, 1767)"
candidate["detail"] = (
    "Printed p.431 identifies the title and publication data for the existing p.438 locator. "
    "The cited page and book were not independently consulted."
)

print(
    json.dumps(
        {
            "mode": "apply" if ARGS.apply else "dry-run",
            "candidate_id": "cand-10216",
            "segment_id": SEGMENT,
            "candidate_count": len(candidates),
        },
        ensure_ascii=False,
        indent=2,
    )
)

if ARGS.apply:
    backup = candidate_path.with_name(candidate_path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(candidate_path, backup)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=candidate_path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=candidate_fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(candidates)
        temporary = Path(handle.name)
    temporary.replace(candidate_path)
