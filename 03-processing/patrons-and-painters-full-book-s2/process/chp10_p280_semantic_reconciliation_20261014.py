"""Classify open p.280 S2 statements and split a multi-group patronage claim.

Dry-run by default. Apply only when source and table fingerprints match.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md"
PDF = ROOT / "02-sources/01-book/CHP-10.pdf"
TABLES = ROOT / "04-knowledge/tables"
SEGMENT = "chp-10:10_CHP-10_intro:l51-61"
NEW_STATEMENT = "st-chp10-p280-ricci-patrons-officials"
BACKUP_SUFFIX = ".bak-s2-chp10-p280-semantic-reconciliation-20261014"

EXPECTED_SHA256 = {
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
    TABLES / "book-statements.jsonl": "613a39b02b9eb617cc0a069660d0c5844c6dccbe6ec9fcd653d0be54f3d2d62a",
    TABLES / "s2-coverage.csv": "1cb51580958b01279620572013b077dc393646a4b3af8727ab529b3faee9bebb",
}
SEGMENT_SHA256 = "877f9ed4cdae9e0e1bc219c8e90b31521e82843d62c83877f5d7a6c2420722c6"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(handle.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(handle.name)
    tmp.replace(path)


for path, expected in EXPECTED_SHA256.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "When Vertue saw the paintings" not in source_lines[54] or not source_lines[60].startswith("Ricci had many enthusiastic patrons"):
    raise SystemExit("p.280 statement anchors changed")
segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segment_rows}
if segment_by_id.get(SEGMENT, {}).get("sha256") != SEGMENT_SHA256:
    raise SystemExit("p.280 source segment hash changed")

statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
candidate_rows = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
candidate_ids = {row["candidate_id"] for row in candidate_rows}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

CLASSIFICATIONS = {
    "st-chp10-p280-portland-contemporary-opinion": False,
    "st-chp10-p280-portland-title-and-biography": False,
    "st-chp10-p280-portland-programme-catholic-comparison": False,
    "st-chp10-p280-vertue-praises-portland-paintings": True,
    "st-chp10-p280-burlington-decorative-preference": False,
    "st-chp10-p280-gay-burlington-house-quotation": False,
    "st-chp10-p280-ricci-patrons-whig-and-officials": True,
    "st-chp10-p280-sheffield-acknowledged-monarchy": False,
}
if not set(CLASSIFICATIONS) <= statement_by_id.keys():
    raise SystemExit("one or more p.280 statements are missing")
for statement_id in CLASSIFICATIONS:
    row = statement_by_id[statement_id]
    if row.get("segment_id") != SEGMENT or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"target statement changed or is already classified: {statement_id}")
if NEW_STATEMENT in statement_by_id:
    raise SystemExit("planned p.280 patron statement already exists")

vertue = statement_by_id["st-chp10-p280-vertue-praises-portland-paintings"]
vertue["subject_candidate_id"] = "cand-8933"
vertue["object_candidate_id"] = "cand-8916"
vertue["qualifiers"]["mentioned_candidate_ids"] = ["cand-1979", "cand-8916", "cand-8933"]

whig = statement_by_id["st-chp10-p280-ricci-patrons-whig-and-officials"]
whig["predicate"] = "ricci_had_many_enthusiastic_patrons_among_the_whig_nobility"
whig["qualifiers"]["claim"] = "Haskell says Ricci had many enthusiastic patrons among the Whig nobility."
whig["qualifiers"]["qualification"] = "This is one of two unnamed patron groups named in the sentence; the other group is recorded separately."
whig["qualifiers"]["mentioned_candidate_ids"] = ["cand-2154", "cand-8926"]
whig["original_quote"] = "Ricci had many enthusiastic patrons among the Whig nobility"

officials = {
    "statement_id": NEW_STATEMENT,
    "segment_id": SEGMENT,
    "subject_candidate_id": "cand-2154",
    "object_candidate_id": "cand-8927",
    "predicate": "ricci_had_many_enthusiastic_patrons_among_important_officials",
    "qualifiers": {
        "source_line_start": 61,
        "source_line_end": 61,
        "printed_page": 280,
        "pdf_physical_page": 5,
        "claim": "Haskell says Ricci had many enthusiastic patrons among important officials.",
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": "The officials are unnamed; this statement preserves the second patron group separately from the Whig nobility.",
        "mentioned_candidate_ids": ["cand-2154", "cand-8927"],
        "relation_candidate": True,
    },
    "original_quote": "and important officials",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "origin": "book",
}

for statement_id, value in CLASSIFICATIONS.items():
    statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = value

needed_ids = {"cand-8933", "cand-8916", "cand-2154", "cand-8926", "cand-8927"}
if not needed_ids <= candidate_ids:
    raise SystemExit(f"missing candidate endpoint(s): {sorted(needed_ids - candidate_ids)}")
for row in [vertue, whig, officials]:
    refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *row["qualifiers"].get("mentioned_candidate_ids", [])} - {None, ""}
    if not refs <= candidate_ids:
        raise SystemExit(f"unresolved candidate references in {row['statement_id']}: {sorted(refs - candidate_ids)}")

coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.280 coverage state changed")
coverage_row["note"] += " 2026-10-14 semantic reconciliation classified the eight previously open p.280 body statements against physical page 5. Corrected the Vertue response endpoints to Vertue and the four-painting programme; split Ricci's two unnamed patron groups into separate claims."

print(json.dumps({
    "source": "p.280, CHP-10.pdf physical page 5",
    "page_scan_sha256": EXPECTED_SHA256[PDF],
    "existing_statements_classified": len(CLASSIFICATIONS),
    "new_statement": NEW_STATEMENT,
    "p280_open_statements": 0,
    "true": sum(CLASSIFICATIONS.values()) + 1,
    "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values()),
}, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_jsonl(statement_path, statements + [officials])
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; backups=" + ", ".join(str(path.relative_to(ROOT)) for path in backups))
