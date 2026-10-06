"""Controlled S2 migration for printed p.276 footnotes 2-3; dry-run unless --apply."""
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
BODY = "chp-10:10_CHP-10_intro:l3-13"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINE_HASHES = {
    493: "265c1a56bcb9aa80350d51c0db373c39a74901818db10ae8165291243d180f56",
    494: "8bde006bb09fbd7b44d4d837c92a8668820420c452ea4d6f99f4270ff4b2367d",
}
BACKUP = ".bak-s2-chp10-p276-notes2-3-20261002"


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
if "Birmingham City Art Gallery" not in src[492] or "Mostra di Pellegrini, 1959, p. 15." not in src[493]:
    raise SystemExit("p.276 notes 2-3 content mismatch")

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
if maximum != 9282:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-492":
    raise SystemExit("notes coverage pre-state changed")

body_entry = next((row for row in statements if row["statement_id"] == "st-chp10-p276-manchester-carlevarijs-entry"), None)
body_departure = next((row for row in statements if row["statement_id"] == "st-chp10-p276-manchester-departure-with-artists"), None)
for row, marker in ((body_entry, 2), (body_departure, 3)):
    if not row or row["qualifiers"].get("footnote_marker") != marker or not row["qualifiers"].get("footnote_text_pending"):
        raise SystemExit(f"p.276 body statement marker {marker} changed")

NEW_CANDIDATES = [
    ("cand-9283", "Birmingham City Art Gallery", "institution",
     "Named in p.276 note 2 as the holding place of the Lord Manchester entry painting at the time of Haskell's note. Do not treat this as a verified present-day location."),
    ("cand-9284", "Nisser, 1937 (citation locator; title and page not supplied)", "archive",
     "Short-form citation attached to the p.276 note 2 holding statement. Author is supplied only by surname; cited material has not been independently consulted."),
    ("cand-9285", "Mostra di Pellegrini, 1959, p.15 (citation locator)", "archive",
     "Short-form citation in p.276 note 3 for Manchester's departure with Pellegrini and Marco Ricci. The cited material has not been independently consulted."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L{493 if cid != 'cand-9285' else 494}",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []

def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p276n23-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    at = line.find(surface)
    if at < 0 or line.find(surface, at + len(surface)) >= 0:
        raise SystemExit(f"surface missing or repeated at L{line_no}: {surface!r}")
    start = offsets[line_no] + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })

add_mention("entry-picture", 493, "The picture", "cand-8839", "Corefers to Lord Manchester's Entry into Venice in p.276 body.")
add_mention("birmingham-gallery", 493, "Birmingham City Art Gallery", "cand-9283")
add_mention("nisser-citation", 493, "Nisser, 1937", "cand-9284")
add_mention("mostra-citation", 494, "Mostra di Pellegrini, 1959, p. 15", "cand-9285")

new_statement = {
    "statement_id": "st-chp10-notes-p276n2-manchester-entry-location",
    "segment_id": NOTES,
    "subject_candidate_id": "cand-8839",
    "object_candidate_id": "cand-9283",
    "predicate": "book_note_reports_painting_location_at_publication",
    "qualifiers": {
        "source_line_start": 493, "source_line_end": 493, "printed_page": 276, "pdf_physical_page": 1,
        "claim": "Haskell's note says the Lord Manchester entry painting is now in Birmingham City Art Gallery.",
        "speaker": "Haskell, footnote", "text_layer": "authorial note",
        "qualification": "The word 'now' is relative to Haskell's publication and is not a present-day location verification. Nisser 1937 is cited but was not independently consulted.",
        "mentioned_candidate_ids": ["cand-8839", "cand-9283", "cand-9284"],
        "parent_body_statement_ids": ["st-chp10-p276-manchester-carlevarijs-entry"],
        "footnote_number": 2, "relation_candidate": True, "cited_material_not_independently_consulted": True,
        "ocr_corrections": [{
            "source_file": SOURCE_FILE, "source_line": 493, "ocr": "��", "print": "—",
            "basis": "CHP-10.pdf physical page 1.",
        }],
    },
    "original_quote": src[492],
    "origin": "book",
    "source_file": SOURCE_FILE,
}
if new_statement["statement_id"] in sids:
    raise SystemExit("p.276 note 2 statement already exists")
if new_statement["original_quote"] not in notes_body:
    raise SystemExit("p.276 note 2 statement quote is not anchored")

body_entry["qualifiers"]["footnote_text_pending"] = False
body_entry["qualifiers"]["footnote_link_status"] = "resolved_source_migration"
body_entry["qualifiers"]["footnote_segment"] = NOTES
body_entry["qualifiers"]["footnote_source_line"] = 493
body_entry["qualifiers"]["qualification"] = (
    "The p.276 note identifies the painting as Lord Manchester's Entry into Venice and reports it at Birmingham City Art Gallery "
    "at the time of Haskell's note, citing Nisser 1937; this is not a present-day location verification."
)
body_departure["qualifiers"]["footnote_text_pending"] = False
body_departure["qualifiers"]["footnote_link_status"] = "resolved_source_migration"
body_departure["qualifiers"]["footnote_segment"] = NOTES
body_departure["qualifiers"]["footnote_source_line"] = 494
body_departure["qualifiers"]["qualification"] += " Note 3 is citation-only (Mostra di Pellegrini, 1959, p.15); the cited material was not independently consulted."

body_cov = cov[BODY]
body_cov["note"] += " Notes 2-3 at L493-L494 are now migrated: note 2 supplies a book-era holding report and note 3 is citation-only. The L13 scan discrepancy remains for handoff audit."
notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-494"
notes_cov["note"] = (
    "Processed printed p.276 notes 1-3 at L492-L494. Note 1 records layered attribution/date discussion; note 2 reports the "
    "Manchester-entry painting's book-era location; note 3 is a citation locator. Remaining L495-L634 is pending."
)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p276 notes2-3 hashes verified; planned candidates=3 mentions=4 statements=1")
print("body footnote links: p276 statements 2 and 3 -> canonical L493 and L494")
print("print reading at L493: replacement glyph -> em dash; note 3 remains citation-only")
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
