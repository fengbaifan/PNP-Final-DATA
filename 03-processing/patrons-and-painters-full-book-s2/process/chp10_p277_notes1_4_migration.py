"""Controlled S2 migration for printed p.277 footnotes 1-4; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BODY = "chp-10:10_CHP-10_intro:l15-24"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINE_HASHES = {
    495: "0a837d56e74ece5dcb469542de4fb5d05dfa31ca2f9b8211d94825c215b67707",
    496: "b9f97de2f42878a702c4227bf8cdc9c78adccfc3a5def963dcd4c5fbbf3d32d5",
    497: "5831251a2affdc6f2ecd67d104a59f11122046e49a825e1bcf6394ae63e96aa8",
    498: "7908225ca3ab9e3d9a4884205ae1ee8b23b65d98ea0f2639ad36ef3eb37a1991",
}
BACKUP = ".bak-s2-chp10-p277-notes1-4-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_body = "\n".join(src[490:634])
if hashlib.sha256(notes_body.encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("merged note segment changed")
for line_no, expected_hash in EXPECTED_LINE_HASHES.items():
    if hashlib.sha256(src[line_no - 1].encode("utf-8")).hexdigest() != expected_hash:
        raise SystemExit(f"source L{line_no} changed")
if not src[495].startswith("2 The picture is now in the Fredericksborg, Copenhagen"):
    raise SystemExit("p.277 note 2 content mismatch")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9285:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-494":
    raise SystemExit("notes coverage pre-state changed")

targets = [row for row in statements if row["segment_id"] == BODY
           and row.get("qualifiers", {}).get("footnote_marker") in {1, 2, 3, 4}]
expected_markers = {1: 1, 2: 1, 3: 1, 4: 3}
counts = {marker: sum(row["qualifiers"].get("footnote_marker") == marker for row in targets) for marker in expected_markers}
if counts != expected_markers or any(not row["qualifiers"].get("footnote_text_pending") for row in targets):
    raise SystemExit(f"body footnote states changed: {counts}")

NEW_CANDIDATES = [
    ("cand-9286", "Fredericksborg (printed spelling; holding location in p.277 note)", "place",
     "The note says Frederick IV's regatta picture was then at 'the Fredericksborg, Copenhagen'. Preserve the print spelling and do not infer a specific castle, museum, or present-day repository."),
    ("cand-9287", "Copenhagen (geographic context for Fredericksborg in p.277 note)", "place",
     "Named as the city context for the work's reported location. This does not identify the holding institution."),
    ("cand-9288", "Malamani, 1899 (citation locator; pp.39, 42, 49 and 50; title unresolved)", "archive",
     "Short-form citations in p.277 notes 1, 3 and 4. The cited pages were not independently consulted; align with other Malamani 1899 locators at S3."),
    ("cand-9289", "Mauroner, 1945 (citation locator; pp.51 and 37 note 17; title unresolved)", "archive",
     "Short-form citations in p.277 notes 2 and 5. The cited pages were not independently consulted; S0 OCR spaces '37' as '3 7' at L499."),
    ("cand-9290", "Sensier (citation locator; pp.22 ff.; year and title unresolved)", "archive",
     "Short-form citation in p.277 note 4. The cited material was not independently consulted and is not identified more fully in this note."),
    ("cand-9291", "Sensier (surname-only author cited in p.277 note 4)", "person",
     "The source supplies only the surname in a short-form citation; do not infer an initial or identity before S3."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = []
for cid, name, kind, detail in NEW_CANDIDATES:
    line_no = 496 if cid in {"cand-9286", "cand-9287", "cand-9289"} else (495 if cid == "cand-9288" else 498)
    newc.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_no}",
    })

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []

def add_mention(local, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p277n14-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    positions, at = [], 0
    while True:
        at = line.find(surface, at)
        if at < 0:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })

add_mention("malamani-l495", 495, "Malamani, 1899, pp. 39 and 42", "cand-9288")
add_mention("malamani-author-l495", 495, "Malamani", "cand-8664", "Surname-only cited author.", occurrence=0)
add_mention("regatta-location-picture", 496, "The picture", "cand-8845", "Corefers to the regatta painting named in p.277 body.")
add_mention("fredericksborg", 496, "Fredericksborg", "cand-9286", "Spelling follows print.")
add_mention("copenhagen", 496, "Copenhagen", "cand-9287")
add_mention("mauroner-citation-l496", 496, "Mauroner, 1945, p. 51", "cand-9289")
add_mention("mauroner-author-l496", 496, "Mauroner", "cand-8512", "Surname-only author; identity remains open.")
add_mention("malamani-l497", 497, "Malamani, 1899, p. 49", "cand-9288")
add_mention("malamani-author-l497", 497, "Malamani", "cand-8664", "Surname-only cited author.")
add_mention("crozat-l498", 498, "Crozat", "cand-0894")
add_mention("rosalba-l498", 498, "Rosalba", "cand-0581")
add_mention("malamani-l498", 498, "Malamani, 1899, p. 50", "cand-9288")
add_mention("malamani-author-l498", 498, "Malamani", "cand-8664", "Surname-only cited author.")
add_mention("sensier-citation", 498, "Sensier, pp. 22 ff.", "cand-9290")
add_mention("sensier-author", 498, "Sensier", "cand-9291", "Surname-only author; identity remains open.")

for line_no, surface, expected in [
    (496, src[495], "Fredericksborg"), (495, src[494], "Malamani"),
    (497, src[496], "Malamani"), (498, src[497], "Sensier"),
]:
    if expected not in surface:
        raise SystemExit(f"source check failed at L{line_no}")

new_statement = {
    "statement_id": "st-chp10-notes-p277n2-regatta-location",
    "segment_id": NOTES,
    "subject_candidate_id": "cand-8845",
    "object_candidate_id": "cand-9286",
    "predicate": "book_note_reports_work_location_at_publication",
    "qualifiers": {
        "source_line_start": 496, "source_line_end": 496, "printed_page": 277, "pdf_physical_page": 2,
        "claim": "Haskell's note says the regatta picture was then in the Fredericksborg, Copenhagen.",
        "speaker": "Haskell, footnote", "text_layer": "authorial note",
        "qualification": "Preserve the printed spelling 'Fredericksborg'. 'Now' is relative to Haskell's publication, not a present-day repository verification. Mauroner 1945 p.51 is cited but was not independently consulted.",
        "mentioned_candidate_ids": ["cand-8845", "cand-9286", "cand-9287", "cand-9289", "cand-8512"],
        "footnote_number": 2, "cited_material_not_independently_consulted": True,
        "related_body_statement_ids": ["st-chp10-p277-carlevarijs-regatta"],
        "relation_candidate": True,
        "ocr_corrections": [{
            "source_file": SOURCE_FILE, "source_line": 496, "ocr": "��", "print": "—",
            "basis": "CHP-10.pdf physical page 2.",
        }],
    },
    "original_quote": src[495],
    "origin": "book",
    "source_file": SOURCE_FILE,
}
if new_statement["statement_id"] in sids or new_statement["original_quote"] not in notes_body:
    raise SystemExit("p.277 note 2 statement is already present or not anchored")

qualification_by_marker = {
    1: "Footnote 1 is citation-only (Malamani, 1899, pp.39 and 42); cited pages were not independently consulted. Individual sitters and pastel titles remain unnamed.",
    2: "Footnote 2 reports the regatta picture at Fredericksborg, Copenhagen at the time of Haskell's note, citing Mauroner 1945 p.51. This is not a current-location verification.",
    3: "Footnote 3 is citation-only (Malamani, 1899, p.49); the cited page was not independently consulted.",
    4: "Footnote 4 points to Malamani, 1899, p.50 and Sensier, pp.22 ff.; neither cited source was independently consulted. The body claims remain attributed to Haskell.",
}
for row in targets:
    marker = row["qualifiers"]["footnote_marker"]
    row["qualifiers"]["footnote_text_pending"] = False
    row["qualifiers"]["footnote_link_status"] = "resolved_source_migration"
    row["qualifiers"]["footnote_segment"] = NOTES
    row["qualifiers"]["footnote_source_line"] = {1: 495, 2: 496, 3: 497, 4: 498}[marker]
    row["qualifiers"]["qualification"] = qualification_by_marker[marker]

candidate_by_id = {row["candidate_id"]: row for row in candidates}
candidate_by_id["cand-8845"]["detail"] = (
    "The p.277 body says Carlevarijs painted the regatta for Frederick; note 2 reports it at the Fredericksborg, Copenhagen "
    "at the time of Haskell's note, citing Mauroner 1945 p.51. Preserve the print spelling; the cited source was not independently consulted."
)

body_cov = cov[BODY]
body_cov["note"] += " Printed p.277 footnotes 1-4 at canonical L495-L498 are now migrated; citations remain unverified, and the location in note 2 is book-era only. Note 5 at L499 remains pending."
notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-498"
notes_cov["note"] = (
    "Processed p.276 notes 1-3 (L492-L494) and p.277 notes 1-4 (L495-L498). P.277 notes 1, 3 and 4 are citation locators; "
    "note 2 adds the Frederick IV regatta's book-era location. L499 and L500-L634 remain pending."
)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p277 notes1-4 hashes verified; planned candidates=6 mentions=15 statements=1")
print("body p277 footnote markers 1-4: all matching statements will be linked; marker 5 remains pending")
print("location evidence is book-era; citations are not independently consulted")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
candidates.extend(newc)
mentions.extend(newm)
statements.append(new_statement)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
