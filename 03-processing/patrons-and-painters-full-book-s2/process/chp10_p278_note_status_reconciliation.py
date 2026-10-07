"""Reconcile stale p.278 footnote status wording after the S2 migration."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"

EXPECTED_HASHES = {
    STATEMENTS: "f220ee8801cd609920573b17ef88133c4fd35d723b3d3bf53fd590b266507578",
    COVERAGE: "7e47da9f1457af7bf4043be694770b6941d24c1013d1dd919ba4e31c5bb46f3f",
    SOURCE: "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
}

BODY_SEGMENT = "chp-10:10_CHP-10_intro:l26-41"
NOTES_SEGMENT = "chp-10:10_CHP-10_intro:l491-634"
BODY_COVERAGE_STALE = (
    "Printed p.278 notes 1-6 remain pending at canonical L500-505."
)
BODY_COVERAGE_CURRENT = (
    "Printed p.278 notes 1-6 at canonical L500-505 are migrated: notes 1-3 and 5-6 "
    "are citation or cross-reference locators, and note 4 dates an unidentified "
    "Amigoni work group to 1716. See the notes-segment coverage for citation and "
    "consultation limits."
)
NOTES_COVERAGE_ADDENDUM = (
    "P.278 notes 1-6 at L500-505 were migrated as recorded in the S2 process log: "
    "notes 1-3 and 5-6 are citation or cross-reference locators, and note 4 dates "
    "an unidentified Amigoni work group to 1716; cited material was not independently "
    "consulted."
)

REPLACEMENTS = {
    "st-chp10-p278-german-courts-art-from-italy-late-baroque": (
        "This is Haskell's historical summary. 'At least a generation' is preserved as phrased; late Baroque names the pictures' style, not the purchased object. Note 1 is a source trail and remains pending.",
        "This is Haskell's historical summary. 'At least a generation' is preserved as phrased; late Baroque names the pictures' style, not the purchased object. Note 1 points back to Chapter 7 and to Lavagnino; it names no specific publication or page, and the Lavagnino reference was not independently consulted.",
    ),
    "st-chp10-p278-bencovich-followed-to-vienna": (
        "The place reference 'there' is Vienna. The plural antecedent of 'them' is not certain from this sentence; do not infer employment by the Hapsburgs or membership in a particular artist group. Printed note 2 remains pending.",
        "The place reference 'there' is Vienna. The plural antecedent of 'them' is not certain from this sentence; do not infer employment by the Hapsburgs or membership in a particular artist group. Note 2 cites Pallucchini, 1933-4, pp. 1491-1511; the article and pages were not independently consulted.",
    ),
    "st-chp10-p278-diziani-augustus-scene-painter": (
        "The page-278 index candidate is used provisionally for the title Augustus the Strong; global identity resolution remains S3. Note 3 is pending.",
        "The page-278 index candidate is used provisionally for the title Augustus the Strong; global identity resolution remains S3. Note 3 cites Donzelli, p. 82; the book and cited page were not independently consulted.",
    ),
    "st-chp10-p278-amigoni-french-craftsmen-nymphenburg": (
        "The source names no individual craftsman or pavilion. Note 4's date and cited works remain pending; the gardens and pavilions are separate place candidates.",
        "The source names no individual craftsman or pavilion. Note 4 dates the unidentified Amigoni works at Nymphenburg from 1716 and cites Lavagnino p. 121 (volume unspecified) and Powell pp. 68-70, 110, and 147; the cited pages were not independently consulted. The gardens and pavilions are separate place candidates.",
    ),
    "st-chp10-p278-manchester-profile-and-social-circle": (
        "The group is unnamed. The OCR footnote marker after 'poets' reads 6, but the scan prints 5; note 5 is pending. These descriptions are Haskell's account. Printed p.278 note marker is 5; S0 OCR misreads it as 6. The cited volume is not independently consulted.",
        "The group is unnamed. The OCR footnote marker after 'poets' reads 6, but the scan prints 5. Note 5 cites Duke of Manchester, vol. II, passim; the bibliography identifies Court and Society from Elizabeth to Anne (London, 1864), but the cited contents were not consulted. The author's identity remains for S3. These descriptions are Haskell's account.",
    ),
    "st-chp10-p278-duchess-wrote-manchester-music-letter": (
        "The letter is quoted through Haskell. Printed note 6 is pending and will be assessed with the canonical page-note segment. Printed p.278 note marker is 6; S0 OCR misreads it as 8. The cited volume is not independently consulted.",
        "The letter is quoted through Haskell. Printed note 6 uses ibid. to cite Duke of Manchester, vol. II, p. 140; the bibliography identifies Court and Society from Elizabeth to Anne (London, 1864), but the cited page was not consulted. The author's identity relative to person candidates remains for S3. Printed p.278 marker is 6; S0 OCR reads 8.",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames or [], list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"input hash changed: {path.relative_to(ROOT)}")

statements = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statements}
if len(statement_by_id) != len(statements):
    raise SystemExit("duplicate statement_id in book-statements.jsonl")

expected_markers = {
    "st-chp10-p278-german-courts-art-from-italy-late-baroque": 1,
    "st-chp10-p278-bencovich-followed-to-vienna": 2,
    "st-chp10-p278-diziani-augustus-scene-painter": 3,
    "st-chp10-p278-amigoni-french-craftsmen-nymphenburg": 4,
    "st-chp10-p278-manchester-profile-and-social-circle": 5,
    "st-chp10-p278-duchess-wrote-manchester-music-letter": 6,
}
for statement_id, (old, _) in REPLACEMENTS.items():
    row = statement_by_id.get(statement_id)
    if not row:
        raise SystemExit(f"missing statement: {statement_id}")
    q = row.get("qualifiers", {})
    marker = expected_markers[statement_id]
    if row.get("segment_id") != BODY_SEGMENT or q.get("printed_page") != 278:
        raise SystemExit(f"statement anchor changed: {statement_id}")
    if q.get("footnote_marker") != marker or q.get("footnote_text_pending") is not False:
        raise SystemExit(f"footnote state changed: {statement_id}")
    if q.get("footnote_link_status") != "resolved_source_migration":
        raise SystemExit(f"footnote migration status changed: {statement_id}")
    if q.get("footnote_source_line") != 499 + marker:
        raise SystemExit(f"footnote source line changed: {statement_id}")
    expected_note_ids = ["st-chp10-notes-p278n4-amigoni-nymphenburg-date"] if marker == 4 else []
    if q.get("footnote_note_statement_ids") != expected_note_ids:
        raise SystemExit(f"footnote statement links changed: {statement_id}")
    if q.get("qualification") != old:
        raise SystemExit(f"qualification changed: {statement_id}")

note4 = statement_by_id.get("st-chp10-notes-p278n4-amigoni-nymphenburg-date")
if not note4 or note4.get("segment_id") != NOTES_SEGMENT:
    raise SystemExit("p.278 note 4 statement is missing or moved")
if note4.get("qualifiers", {}).get("related_body_statement_ids") != [
    "st-chp10-p278-amigoni-french-craftsmen-nymphenburg"
]:
    raise SystemExit("p.278 note 4 body link changed")

coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
body_cov = coverage_by_id.get(BODY_SEGMENT)
notes_cov = coverage_by_id.get(NOTES_SEGMENT)
if not body_cov or not notes_cov:
    raise SystemExit("p.278 coverage rows are missing")
if body_cov["migration_status"] != "complete" or BODY_COVERAGE_STALE not in body_cov["note"]:
    raise SystemExit("p.278 body coverage state changed")
if notes_cov["migration_status"] != "complete" or notes_cov["source_line_ranges"] != "L492-634":
    raise SystemExit("merged notes coverage state changed")
if NOTES_COVERAGE_ADDENDUM in notes_cov["note"]:
    raise SystemExit("p.278 note status addendum already exists")

for row in statements:
    if row["statement_id"] in REPLACEMENTS:
        old, new = REPLACEMENTS[row["statement_id"]]
        row["qualifiers"]["qualification"] = new
body_cov["note"] = body_cov["note"].replace(BODY_COVERAGE_STALE, BODY_COVERAGE_CURRENT, 1)
notes_cov["note"] = f"{notes_cov['note'].rstrip()} {NOTES_COVERAGE_ADDENDUM}"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated reconciliation")
args = parser.parse_args()
print("verified six printed p.278 note anchors, migrated note links, source PDF, and current coverage states")
for statement_id, (_, new) in REPLACEMENTS.items():
    print(f"{statement_id}: {new}")
print("coverage: remove stale p.278 pending wording; record citation-only locators and consultation limits")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp10-p278-note-status-"))
shutil.copy2(STATEMENTS, backup_dir / STATEMENTS.name)
shutil.copy2(COVERAGE, backup_dir / COVERAGE.name)
write_jsonl(STATEMENTS, statements)
write_csv(COVERAGE, coverage_fields, coverage_rows)

written = read_jsonl(STATEMENTS)
written_by_id = {row["statement_id"]: row for row in written}
if any(written_by_id[sid]["qualifiers"]["qualification"] != new for sid, (_, new) in REPLACEMENTS.items()):
    raise SystemExit("post-write statement verification failed; recovery copies retained")
if sha256(STATEMENTS) == EXPECTED_HASHES[STATEMENTS] or sha256(COVERAGE) == EXPECTED_HASHES[COVERAGE]:
    raise SystemExit("post-write files did not change as expected; recovery copies retained")
print(f"applied six qualification updates and two coverage-note updates; recovery copies: {backup_dir}")
