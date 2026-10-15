"""Classify open p.279 S2 statements and atomize Sebastiano Ricci's profile.

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
SEGMENT = "chp-10:10_CHP-10_intro:l43-49"
NEW_IDS = {
    "generation": "st-chp10-p279-sebastiano-older-generation-than-pellegrini",
    "travel": "st-chp10-p279-sebastiano-travel-absorbed-styles",
}
BACKUP_SUFFIX = ".bak-s2-chp10-p279-semantic-reconciliation-20261014"

EXPECTED_SHA256 = {
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
    TABLES / "book-statements.jsonl": "3ce26a75a16cbf158bddb5e15c20ce087081f739c512c81ae9ecf9e93dd534a8",
    TABLES / "s2-coverage.csv": "f2fe07c68bd899afc9b4e7e82f7717241989c0ab9e338ec332947f89cf5fc6c9",
}
SEGMENT_SHA256 = "f311fdf054bf8adc8fe5bcab01d4a0458950b7f837b4da9af644e1ced09e283b"


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
if not source_lines[46].startswith("In England Pellegrini") or "His early patrons had mostly been" not in source_lines[48]:
    raise SystemExit("p.279 body anchors changed")
segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segment_rows}
if segment_by_id.get(SEGMENT, {}).get("sha256") != SEGMENT_SHA256:
    raise SystemExit("p.279 source segment hash changed")

statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
candidate_rows = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
candidate_ids = {row["candidate_id"] for row in candidate_rows}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

CLASSIFICATIONS = {
    "st-chp10-p279-drawing-anticipates-conversation-pieces": True,
    "st-chp10-p279-england-atmosphere-credit": True,
    "st-chp10-p279-fountaine-collector-traveller": False,
    "st-chp10-p279-marco-and-sebastiano-back-at-work": False,
    "st-chp10-p279-motteux-profile": False,
    "st-chp10-p279-pellegrini-new-style": True,
    "st-chp10-p279-pellegrini-palette-and-motifs": False,
    "st-chp10-p279-pellegrini-sheds-stolidity": False,
    "st-chp10-p279-sebastiano-contrasted-with-pellegrini": False,
    "st-chp10-p279-sebastiano-patronage-and-travel": True,
    "st-chp10-p279-van-dyck-portraits-influence-pellegrini": True,
}
if not set(CLASSIFICATIONS) <= statement_by_id.keys():
    raise SystemExit("one or more p.279 statements are missing")
for statement_id in CLASSIFICATIONS:
    row = statement_by_id[statement_id]
    if row.get("segment_id") != SEGMENT or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"target statement changed or is already classified: {statement_id}")
if any(statement_id in statement_by_id for statement_id in NEW_IDS.values()):
    raise SystemExit("one or more planned p.279 statements already exist")

patronage = statement_by_id["st-chp10-p279-sebastiano-patronage-and-travel"]
patronage["predicate"] = "sebastiano_ricci_early_patrons_were_autocratic_rulers_of_northern_and_central_italy"
patronage["qualifiers"]["claim"] = "Haskell says Sebastiano Ricci's early patrons were mostly the powerful autocratic rulers of northern and central Italy."
patronage["qualifiers"]["qualification"] = "The patrons remain an unnamed collective; preserve 'mostly' and the source's geographic scope. The generation and travel/style clauses are recorded separately."
patronage["qualifiers"]["mentioned_candidate_ids"] = ["cand-2154", "cand-3461", "cand-8904"]
patronage["original_quote"] = "His early patrons had mostly been the powerful autocratic rulers of northern and central Italy"

generation = {
    "statement_id": NEW_IDS["generation"],
    "segment_id": SEGMENT,
    "subject_candidate_id": "cand-2154",
    "object_candidate_id": "cand-1870",
    "predicate": "sebastiano_ricci_belonged_to_an_older_generation_than_pellegrini",
    "qualifiers": {
        "source_line_start": 49,
        "source_line_end": 49,
        "printed_page": 279,
        "pdf_physical_page": 4,
        "claim": "Haskell places Sebastiano Ricci in an older generation than Pellegrini.",
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": "Comparative generational characterization; no exact birth dates or age gap is inferred.",
        "mentioned_candidate_ids": ["cand-1870", "cand-2154"],
        "relation_candidate": False,
    },
    "original_quote": "Sebastiano belonged to an older generation than Pellegrini.",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "origin": "book",
}
travel = {
    "statement_id": NEW_IDS["travel"],
    "segment_id": SEGMENT,
    "subject_candidate_id": "cand-2154",
    "object_candidate_id": "cand-8905",
    "predicate": "sebastiano_ricci_absorbed_and_displayed_varied_styles_through_extensive_travel",
    "qualifiers": {
        "source_line_start": 49,
        "source_line_end": 49,
        "printed_page": 279,
        "pdf_physical_page": 4,
        "claim": "Haskell says Sebastiano's extensive travels exposed him to a wide variety of styles which he absorbed and could display with sometimes excessive facility.",
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": "'Sometimes excessive facility' is Haskell's evaluative phrasing, not an objective assessment.",
        "mentioned_candidate_ids": ["cand-2154", "cand-8905"],
        "relation_candidate": True,
    },
    "original_quote": "from his extensive travels he had absorbed a wide variety of styles which he was liable to display with a sometimes excessive facility.",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "origin": "book",
}

for statement_id, value in CLASSIFICATIONS.items():
    statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = value

needed_ids = {"cand-1870", "cand-2154", "cand-3461", "cand-8904", "cand-8905", "cand-8892", "cand-8900", "cand-8895", "cand-8897", "cand-8909"}
if not needed_ids <= candidate_ids:
    raise SystemExit(f"missing candidate endpoint(s): {sorted(needed_ids - candidate_ids)}")
for row in [patronage, generation, travel]:
    refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *row["qualifiers"].get("mentioned_candidate_ids", [])} - {None, ""}
    if not refs <= candidate_ids:
        raise SystemExit(f"unresolved candidate references in {row['statement_id']}: {sorted(refs - candidate_ids)}")

coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.279 coverage state changed")
coverage_row["note"] += " 2026-10-14 semantic reconciliation classified the eleven previously open p.279 body statements against physical page 4. The Sebastiano Ricci profile is separated into early patronage, generational context, and travel/style claims; the remaining aesthetic comparisons and biographical profile claims are retained as source statements without formal relation candidacy."

print(json.dumps({
    "source": "p.279, CHP-10.pdf physical page 4",
    "page_scan_sha256": EXPECTED_SHA256[PDF],
    "existing_statements_classified": len(CLASSIFICATIONS),
    "new_statements": list(NEW_IDS.values()),
    "p279_segment_open_statements": 0,
    "p279_reconciliation_true": sum(CLASSIFICATIONS.values()) + 1,
    "p279_reconciliation_false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values()) + 1,
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
        write_jsonl(statement_path, statements + [generation, travel])
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; backups=" + ", ".join(str(path.relative_to(ROOT)) for path in backups))
