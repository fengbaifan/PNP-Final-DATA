"""Close the remaining printed-p.276 S2 classifications after page-image review."""
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
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
BODY = "chp-10:10_CHP-10_intro:l3-13"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_chp10_phys1.png"
EXPECTED_HASHES = {
    STATEMENTS: "33796b043c25320e206387599e63ceef3c81981b39a85e388391514da6d4f289",
    COVERAGE: "f8e8a76b8c7c2a9074dfd794c0362dcbb7820d3d71f155523d2b55b9e6c852e1",
    MENTIONS: "a2d657512d0a2219597001b8abb264f7b10d940735711c30d4fc1833257f8204",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
}
SEGMENT_HASHES = {
    BODY: "2b86f1b920d1aa7de55b2ba8f511e3c8ec71b8c546387f71da2113d40e197e92",
    NOTES: "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76",
}
BACKUP_SUFFIX = ".bak-s2-chp10-p276-classification-reconciliation-20261014"

CLASSIFICATIONS = {
    "st-chp10-notes-p276n1-biographical-attribution": True,
    "st-chp10-notes-p276n1-guido-manner-interpretation": True,
    "st-chp10-notes-p276n1-zanetti-date-correction": True,
    "st-chp10-p276-cosmopolitan-venice-and-new-art": False,
    "st-chp10-p276-counter-reformation-painting": True,
    "st-chp10-p276-traditional-patronage-sources": True,
    "st-chp10-p276-venetian-isolation": False,
    "st-chp10-p276-war-neutrality-and-visitors": True,
}
REASONS = {
    "st-chp10-notes-p276n1-biographical-attribution": (
        "S2: Haskell explicitly reports the biographers' attribution of pastel advice from the English signor "
        "Colle to Rosalba Carriera; retain the attributed advice relation without treating the reports as independently verified."
    ),
    "st-chp10-notes-p276n1-guido-manner-interpretation": (
        "S2: Haskell explicitly infers Crespi's reference to Guido Reni's manner and notes its reception among "
        "eighteenth-century connoisseurs; preserve the inference and do not upgrade it to documented intent."
    ),
    "st-chp10-notes-p276n1-zanetti-date-correction": (
        "S2: Haskell reports a dated comparison by Crespi between Carriera's pastel work and Guido Reni; "
        "keep the date and bibliographic qualification attached to the comparison."
    ),
    "st-chp10-p276-cosmopolitan-venice-and-new-art": (
        "S2: this is Haskell's broad contrast between cosmopolitan audiences, contemporary fashion and history painting; "
        "it does not identify a specific patron, commission or individual artwork relation."
    ),
    "st-chp10-p276-counter-reformation-painting": (
        "S2: Haskell explicitly connects the three named-by-type patron groups to a tendency toward conservative "
        "Counter-Reformation elements in Italian painting; retain the stated tendency, not a universal rule."
    ),
    "st-chp10-p276-traditional-patronage-sources": (
        "S2: the passage explicitly identifies the State, nobles and Church as traditional patronage sources "
        "in the first part of the eighteenth century; retain the time-limited patronage relation."
    ),
    "st-chp10-p276-venetian-isolation": (
        "S2: this is Haskell's interpretive synthesis about paintings reflecting a Venetian desire for isolation; "
        "the text does not specify a particular policy act or commission as a formal relation."
    ),
    "st-chp10-p276-war-neutrality-and-visitors": (
        "S2: the passage reports Venice's neutrality alongside foreign embassies' activity and foreign kings' "
        "visits for alliance or relief; keep the unnamed collective actors and wartime context unresolved."
    ),
}
EXPECTED_GLOBAL_BEFORE = {True: 9678, False: 4014, None: 1137}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(f.name)
    temp_path.replace(path)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(f.name)
    temp_path.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"fingerprint changed; inspect before continuing: {path.relative_to(ROOT)}")
if not PAGE_IMAGE.exists():
    raise SystemExit(f"reviewed printed-p.276 image is missing: {PAGE_IMAGE.relative_to(ROOT)}")

segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
for sid, expected in SEGMENT_HASHES.items():
    if sid not in segments or segments[sid]["sha256"] != expected:
        raise SystemExit(f"unexpected source segment: {sid}")
    if segments[sid]["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
        raise SystemExit(f"unexpected source asset reference: {sid}")

statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
unset_ids = {
    row["statement_id"] for row in statement_rows
    if row.get("qualifiers", {}).get("printed_page") == 276
    and row.get("qualifiers", {}).get("relation_candidate") is None
}
if unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.276 unset classifications: {sorted(unset_ids)}")
if set(CLASSIFICATIONS) != set(REASONS):
    raise SystemExit("classification reasons do not match the decision set")

_, mention_rows = read_csv(MENTIONS)
page_body_mentions = [row for row in mention_rows if row["segment_id"] == BODY and row["mention_id"].startswith("m-chp10-p276-")]
page_note_mentions = [row for row in mention_rows if row["segment_id"] == NOTES and row["mention_id"].startswith("m-chp10-p276n")]
if len(page_body_mentions) != 33 or len(page_note_mentions) != 15:
    raise SystemExit(f"p.276 mention baseline changed: body={len(page_body_mentions)}, notes={len(page_note_mentions)}")

coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
for sid in (BODY, NOTES):
    if sid not in coverage_by_id or coverage_by_id[sid]["migration_status"] != "complete":
        raise SystemExit(f"unexpected S2 coverage state for {sid}")

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
if after[True] != before[True] + 6 or after[False] != before[False] + 2 or after[None] != before[None] - 8:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

coverage_by_id[BODY]["note"] += (
    " 2026-10-14 S2 review against CHP-10.pdf physical p.1 confirmed the 33 existing body mentions; "
    "five unset body statements were classified (3 true, 2 false), retaining the page-276 footnote continuation at L13."
)
coverage_by_id[NOTES]["note"] += (
    " 2026-10-14 review confirmed the 15 existing p.276 note mentions against the page image; "
    "three note 1 statements at L492 were classified as relation candidates with their source and inference limits retained."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_page": 276,
    "pdf_physical_page": 1,
    "existing_mentions_confirmed": {"body": len(page_body_mentions), "notes": len(page_note_mentions)},
    "classified_statements": {"true": 6, "false": 2, "unset_closed": 8},
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write verified p.276 statement and coverage updates")
args = parser.parse_args()
if args.apply:
    paths = [STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.276 reconciliation backups already exist")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    try:
        write_jsonl(STATEMENTS, statement_rows)
        write_csv(COVERAGE, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(path.name for path in backups))
