"""Classify and atomize p.278 S2 statements against the scanned page.

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
SEGMENT = "chp-10:10_CHP-10_intro:l26-41"
NEW_STATEMENT = "st-chp10-p278-duchess-music-french-air"
BACKUP_SUFFIX = ".bak-s2-chp10-p278-semantic-reconciliation-20261014"

EXPECTED_SHA256 = {
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
    TABLES / "book-statements.jsonl": "935dfd5203b4dfe59486a9c6abd786833298df7590afa515ed145fbd56b71763",
    TABLES / "s2-coverage.csv": "65e87c52a84785b5a681de6ff78a3932d20c0b4e4a6612b41b2db054ad144054",
}
SEGMENT_SHA256 = "11109dec2da0c22589297ae786772e434dfb0571e62cde36113512f37e6db0ab"


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
if not source_lines[26].startswith("commissions there was a divergence of taste"):
    raise SystemExit("p.278 opening continuation anchor changed")
if "Italian, which is the best master" not in source_lines[38] or "French air" not in source_lines[38]:
    raise SystemExit("p.278 Duchess quotation anchor changed")
segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segment_rows}
if segment_by_id.get(SEGMENT, {}).get("sha256") != SEGMENT_SHA256:
    raise SystemExit("p.278 source segment hash changed")

statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
candidate_rows = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
candidate_ids = {row["candidate_id"] for row in candidate_rows}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

CLASSIFICATIONS = {
    "st-chp10-p278-german-courts-art-from-italy-late-baroque": True,
    "st-chp10-p278-english-german-austrian-patronage-difference": True,
    "st-chp10-p278-whigs-venetian-oligarchy-analogy": False,
    "st-chp10-p278-whigs-borrow-from-continent": False,
    "st-chp10-p278-whigs-optimistic-about-england": False,
    "st-chp10-p278-duchess-music-italian-french-influence": True,
    "st-chp10-p278-duchess-music-nonage-and-encouragement": False,
    "st-chp10-p278-haskell-painting-analogy": False,
}
if not set(CLASSIFICATIONS) <= statement_by_id.keys():
    raise SystemExit("one or more p.278 statements are missing")
for statement_id in CLASSIFICATIONS:
    row = statement_by_id[statement_id]
    if row.get("segment_id") != SEGMENT or row.get("qualifiers", {}).get("relation_candidate") is not None:
        raise SystemExit(f"target statement changed or is already classified: {statement_id}")
if NEW_STATEMENT in statement_by_id:
    raise SystemExit("planned p.278 French-air statement already exists")

german = statement_by_id["st-chp10-p278-german-courts-art-from-italy-late-baroque"]
german["subject_candidate_id"] = "cand-8852"
german["qualifiers"]["qualification"] += " No individual court or painting is identified; retain this as a group-level source claim without inventing item endpoints."

italian = statement_by_id["st-chp10-p278-duchess-music-italian-french-influence"]
italian["object_candidate_id"] = "cand-8879"
italian["predicate"] = "duchess_described_english_music_as_learning_from_the_italian_musical_model"
italian["qualifiers"]["source_line_start"] = 39
italian["qualifiers"]["source_line_end"] = 39
italian["qualifiers"]["claim"] = "In the letter quotation Haskell attributes to the Duchess, music in England is learning the Italian model, which she calls the best master."
italian["qualifiers"]["qualification"] = "This is the Duchess's evaluation within a nested letter quotation; do not treat it as an independently established account of English music. The French-air clause is recorded separately."
italian["qualifiers"]["mentioned_candidate_ids"] = ["cand-8877", "cand-8878", "cand-8879"]
italian["original_quote"] = "Italian, which is the best master,"

french = {
    "statement_id": NEW_STATEMENT,
    "segment_id": SEGMENT,
    "subject_candidate_id": "cand-8878",
    "object_candidate_id": "cand-8880",
    "predicate": "duchess_described_english_music_as_studying_the_french_air_for_gaiety_and_fashion",
    "qualifiers": {
        "source_line_start": 39,
        "source_line_end": 39,
        "printed_page": 278,
        "pdf_physical_page": 3,
        "claim": "In the letter quotation Haskell attributes to the Duchess, music in England studies a little of the French air for gaiety and fashion.",
        "speaker": "Duchess of Marlborough",
        "text_layer": "nested letter quotation reported by Haskell",
        "qualification": "This is the Duchess's evaluation within a nested letter quotation; do not treat it as an independently established account of English music.",
        "mentioned_candidate_ids": ["cand-8877", "cand-8878", "cand-8880"],
        "relation_candidate": True,
    },
    "original_quote": "and studying a little of the French air to give it somewhat of gaiety and fashion.",
    "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "origin": "book",
}

for statement_id, value in CLASSIFICATIONS.items():
    statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = value

needed_ids = {"cand-8852", "cand-8877", "cand-8878", "cand-8879", "cand-8880"}
if not needed_ids <= candidate_ids:
    raise SystemExit(f"missing candidate endpoint(s): {sorted(needed_ids - candidate_ids)}")
for row in [italian, french, german]:
    refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *row["qualifiers"].get("mentioned_candidate_ids", [])} - {None, ""}
    if not refs <= candidate_ids:
        raise SystemExit(f"unresolved candidate references in {row['statement_id']}: {sorted(refs - candidate_ids)}")

coverage_row = coverage_by_id.get(SEGMENT)
if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.278 coverage state changed")
coverage_row["note"] += " 2026-10-14 semantic reconciliation classified all eight previously open p.278 body statements. German-court collecting and the explicit English/South-German-Austrian patron comparison remain relation candidates; the Duchess's Italian-model and French-air clauses are separate source-attributed statements. Interpretive analogy, unspecified cultural borrowing, the quoted forecast about music, and Haskell's transition to painting remain claims but are not formal relation candidates."

print(json.dumps({
    "source": "p.278, CHP-10.pdf physical page 3",
    "page_scan_sha256": EXPECTED_SHA256[PDF],
    "existing_statements_classified": len(CLASSIFICATIONS),
    "new_statement": NEW_STATEMENT,
    "p278_segment_totals": {
        "statements_after": sum(1 for row in statements if row["segment_id"] == SEGMENT) + 1,
        "true": sum(CLASSIFICATIONS.values()) + 1,
        "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values()),
        "unset": 0,
    },
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
        write_jsonl(statement_path, statements + [french])
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; backups=" + ", ".join(str(path.relative_to(ROOT)) for path in backups))
