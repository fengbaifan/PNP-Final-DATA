#!/usr/bin/env python3
"""Close the second OCR segment of the opening index leaf (inferred p.443)."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INDEX_MD = ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md"
INDEX_PDF = ROOT / "02-sources" / "01-book" / "CHP-22Index.pdf"
INDEX_CSV = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "A.csv"
SOURCE_FILE = "02-sources/02-Markdown/22_CHP-22Index.md"
SEGMENT_ID = "chp-22:22_CHP-22Index:l64-109"
SEGMENT_SHA = "63c4cdd642118aa4dfbe1bd9e67b0080fbec56373118aa58de9ef56975c4c09a"
INDEX_MD_SHA = "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081"
INDEX_PDF_SHA = "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5"
INDEX_CSV_SHA = "b44d3ac13df58464fab2aaa1d1fca0a819ab03b1abcc56f466a70d543c4a1133"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p443-l64-109-20261007"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
ARGS = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path, encoding="utf-8-sig"):
    with path.open(encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


for path, expected, label in (
    (INDEX_MD, INDEX_MD_SHA, "index Markdown"),
    (INDEX_PDF, INDEX_PDF_SHA, "index PDF"),
    (INDEX_CSV, INDEX_CSV_SHA, "A.csv"),
):
    if sha256(path) != expected:
        raise SystemExit(f"{label} changed")

source_lines = INDEX_MD.read_text(encoding="utf-8-sig").splitlines()
manifest = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
segment = manifest.get(SEGMENT_ID)
if not segment or (
    segment.get("source_file"),
    segment.get("line_start"),
    segment.get("line_end"),
    segment.get("sha256"),
    segment.get("asset_sha256"),
) != (SOURCE_FILE, 64, 109, SEGMENT_SHA, INDEX_MD_SHA):
    raise SystemExit("S0 segment manifest changed")
segment_text = "\n".join(source_lines[63:109])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("S0 segment text changed")

coverage_path = TABLES / "s2-coverage.csv"
candidate_path = TABLES / "entity-candidates.csv"
coverage_fields, coverage = read_csv(coverage_path)
_, candidates = read_csv(candidate_path)
mentions = read_csv(TABLES / "mentions.csv")[1]
statements = [
    json.loads(line)
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
if (len(coverage), len(candidates), len(mentions), len(statements)) != (832, 11436, 26829, 12102):
    raise SystemExit("unexpected S2 pre-state")

coverage_by_id = {row["segment_id"]: row for row in coverage}
row = coverage_by_id.get(SEGMENT_ID)
if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("target segment is not queued")
for segment_id, expected_state in (
    ("chp-22:22_CHP-22Index:l1-1", ("excluded", "complete")),
    ("chp-22:22_CHP-22Index:l3-3", ("excluded", "complete")),
    ("chp-22:22_CHP-22Index:l9-56", ("reviewed", "complete")),
):
    earlier = coverage_by_id.get(segment_id)
    if not earlier or (earlier["disposition"], earlier["migration_status"]) != expected_state:
        raise SystemExit(f"opening index segment is not complete: {segment_id}")

marker_row = coverage_by_id["chp-22:22_CHP-22Index:l3-3"]
left_column_row = coverage_by_id["chp-22:22_CHP-22Index:l9-56"]
if "[Page 24]" not in marker_row["note"] or "p.24" not in left_column_row["note"]:
    raise SystemExit("opening index page-note pre-state changed")
marker_row["note"] = (
    "OCR/source marker [Page 24] only; it is not printed in CHP-22Index.pdf physical p.1, which is the unnumbered "
    "opening index leaf preceding the visible p.444 folio. Treat the marker as a source locator, not a printed folio, "
    "index entry, or factual claim."
)
left_column_row["note"] = (
    "no_semantic_content: S0 L9-56 is the left-column OCR segment of the unnumbered opening index leaf in "
    "CHP-22Index.pdf physical p.1; the opening folio is inferred as p.443 from the following visible p.444. The full-page "
    "A.csv mapping spans this segment and the right-column continuation at L64-109, which is recorded separately. Index "
    "entries and locators are navigational, not book-fact claims; no mentions or statements were added."
)

candidate_by_index_id = {
    candidate["index_entry_id"]: candidate
    for candidate in candidates
    if candidate["index_entry_id"]
}
index_rows = read_csv(INDEX_CSV, encoding="cp1252")[1]
for row_number in range(33, 67):
    index_entry_id = f"A.csv#{row_number}"
    candidate = candidate_by_index_id.get(index_entry_id)
    index_row = index_rows[row_number]
    exact_mapping = candidate and (
        candidate["canonical_name"], candidate["sub_entry"]
    ) == (index_row["Main Entry"], index_row["Sub-entry"])
    page_verified_spelling = (
        row_number == 46
        and candidate
        and candidate["canonical_name"] == index_row["Main Entry"]
        and index_row["Sub-entry"] == "and Count Br¨¹hl"
        and candidate["sub_entry"] == "and Count Brühl"
    )
    if not exact_mapping and not page_verified_spelling:
        raise SystemExit(f"S1 candidate mapping changed: {index_entry_id}")
    if row_number == 33:
        expected = ("excluded", "cand-0665")
        if candidate["status"] != expected[0] or expected[1] not in candidate["exclude_reason"]:
            raise SystemExit("Alexander VII alias mapping changed")
    elif row_number == 34:
        expected = ("excluded", "cand-1794")
        if candidate["status"] != expected[0] or expected[1] not in candidate["exclude_reason"]:
            raise SystemExit("Alexander VIII alias mapping changed")
    elif candidate["status"] != "open" or candidate["suggested_type"] != "person":
        raise SystemExit(f"right-column index candidate is not classified: {index_entry_id}")

row.update(
    disposition="reviewed",
    migration_status="complete",
    source_line_ranges="L64-109",
    note=(
        "no_semantic_content: S0 L64-109 is the right-column continuation of the unnumbered opening index leaf in "
        "CHP-22Index.pdf physical p.1; the following page visibly bears p.444, so the opening folio is inferred as p.443. "
        "L64-67 are OCR fragments of the index Notes; L68-109 cover Alexander VII/VIII cross-references, Algardi and "
        "Algarotti headings and subentries. Their A.csv#33-66 candidates were classified against the full page in the "
        "preceding migration; no additional candidate, mention, book statement, or relation is created here. The OCR "
        "marker [Page 24] is not a printed folio."
    ),
)

after = {
    "candidate_count": len(candidates),
    "mention_count": len(mentions),
    "statement_count": len(statements),
    "coverage_complete": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "complete"
        for item in coverage
    ),
    "coverage_queued": sum(item["disposition"] == "queued" for item in coverage),
    "coverage_excluded": sum(item["disposition"] == "excluded" for item in coverage),
    "coverage_partial": sum(
        item["disposition"] == "reviewed" and item["migration_status"] == "partial"
        for item in coverage
    ),
}
expected_after = {
    "candidate_count": 11436,
    "mention_count": 26829,
    "statement_count": 12102,
    "coverage_complete": 619,
    "coverage_queued": 90,
    "coverage_excluded": 123,
    "coverage_partial": 0,
}
if after != expected_after:
    raise SystemExit(f"unexpected post-state: {after}")

result = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "source_segment": SEGMENT_ID,
    "printed_leaf": "p.443 inferred; folio not visible",
    "physical_pdf_page": 1,
    "candidate_updates": 0,
    "new_candidates": 0,
    "new_mentions": 0,
    "new_book_statements": 0,
    "corrected_opening_page_notes": 2,
    **after,
}
if ARGS.apply:
    backup = coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("coverage backup already exists; refusing to overwrite it")
    shutil.copy2(coverage_path, backup)
    write_csv(coverage_path, coverage_fields, coverage)
    result["backup"] = str(backup.relative_to(ROOT))

print(json.dumps(result, ensure_ascii=False, indent=2))
