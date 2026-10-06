"""Controlled S2 migration for printed p.277 footnote 5; dry-run unless --apply."""
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
EXPECTED_LINE_SHA = "682f6872df2400dc0729c645b5c103b5a298afb3096f72f3d2c1425387170d77"
BACKUP = ".bak-s2-chp10-p277-note5-20261002"


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
if hashlib.sha256(src[498].encode("utf-8")).hexdigest() != EXPECTED_LINE_SHA:
    raise SystemExit("p.277 note 5 changed")
if "the Entry of the Count of Colloredo" not in src[498] or "Count of Bolagno" not in src[498]:
    raise SystemExit("p.277 note 5 content mismatch")

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
if maximum != 9291:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-498":
    raise SystemExit("notes coverage pre-state changed")

index_work_rows = {cid: next((r for r in candidates if r["candidate_id"] == cid), None)
                   for cid in ("cand-0556", "cand-0504", "cand-0505")}
expected_subentries = {
    "cand-0556": "Entry of the Count of Colloredo",
    "cand-0504": "Entry of the Comte de Gergy",
    "cand-0505": "Entry of the Count of Bolagno",
}
for cid, row in index_work_rows.items():
    if not row or row.get("sub_entry") != expected_subentries[cid] or row.get("suggested_type"):
        raise SystemExit(f"index work candidate changed: {cid}: {row}")

body_targets = [row for row in statements if row["segment_id"] == BODY
                and row.get("qualifiers", {}).get("footnote_marker") == 5]
if len(body_targets) != 2 or any(not row["qualifiers"].get("footnote_text_pending") for row in body_targets):
    raise SystemExit("p.277 note 5 body links changed")

NEW_CANDIDATES = [
    ("cand-9292", "Count of Colloredo (Imperial ambassador named in p.277 note 5; identity unresolved)", "person",
     "The footnote supplies a title and surname but no first name; keep the person distinct from the Entry work and do not infer commission."),
    ("cand-9293", "Comte de Gergy (French ambassador named in p.277 note 5; identity unresolved)", "person",
     "The footnote supplies a title and surname but no first name; keep the person distinct from the Entry work and do not infer commission."),
    ("cand-9294", "Count of Bolagno (Imperial ambassador named in p.277 note 5; identity unresolved)", "person",
     "The footnote supplies a title and surname but no first name; preserve the printed spelling and do not infer commission."),
    ("cand-9295", "V. Moschini, 1954, p.29 (citation locator; title unresolved)", "archive",
     "Short-form citation in p.277 note 5 for the reported Hermitage location of the Count of Bolagno entry. The cited page was not independently consulted; align with the existing V. Moschini author candidate at S3."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L499",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []

def add_mention(local, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p277n5-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[498]
    positions, at = [], 0
    while True:
        at = line.find(surface, at)
        if at < 0:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L499: {surface!r}")
    start = offsets[499] + positions[occurrence]
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })

add_mention("manchester-entry", "Lord Manchester’s Entry into Venice (1707)", "cand-8839",
            "The footnote restates the work introduced in p.276; OCR replacement characters are corrected in S2 notes.")
add_mention("manchester-person", "Lord Manchester", "cand-1504")
add_mention("frederick-regatta", "Regatta in honour of Frederick IV of Denmark (1709)", "cand-8845")
add_mention("frederick-person", "Frederick IV of Denmark", "cand-1078")
add_mention("carlevarijs", "Carlevarijs", "cand-0554")
add_mention("colloredo-entry", "Entry of the Count of Colloredo", "cand-0556")
add_mention("colloredo-person", "Count of Colloredo", "cand-9292")
add_mention("dresden", "Dresden", "cand-0947")
add_mention("mauroner-citation", "Mauroner, 1945, p. 3 7, note 17", "cand-9289")
add_mention("mauroner-person", "Mauroner", "cand-8512")
add_mention("canaletto", "Canaletto", "cand-0498")
add_mention("gergy-entry", "Entry of the Comte de Gergy", "cand-0504")
add_mention("gergy-person", "Comte de Gergy", "cand-9293")
add_mention("hermitage-gergy", "Hermitage", "cand-5795", occurrence=0)
add_mention("haskell-citation", "Haskell, 1956, p. 298", "cand-8642")
add_mention("bolagno-entry", "that of the Count of Bolagno", "cand-0505")
add_mention("bolagno-person", "Count of Bolagno", "cand-9294")
add_mention("hermitage-bolagno", "Hermitage", "cand-5795", occurrence=1)
add_mention("moschini-citation", "V. Moschini, 1954, p. 29", "cand-9295")
add_mention("moschini-person", "V. Moschini", "cand-8658")

def make_statement(statement_id, subject, object_, predicate, quote, claim, qualification, mentioned, relation=False):
    if statement_id in sids:
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in src[498]:
        raise SystemExit(f"quote is not anchored: {statement_id}")
    return {
        "statement_id": statement_id, "segment_id": NOTES,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 499, "source_line_end": 499, "printed_page": 277, "pdf_physical_page": 2,
            "claim": claim, "speaker": "Haskell, footnote", "text_layer": "authorial note",
            "qualification": qualification, "mentioned_candidate_ids": mentioned,
            "footnote_number": 5,
            "related_body_statement_ids": [r["statement_id"] for r in body_targets],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": relation,
        },
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    }

newstatements = [
    make_statement(
        "st-chp10-notes-p277n5-colloredo-entry", "cand-0554", "cand-0556",
        "artist_painted_named_ambassador_entry_work_in_1726",
        "Carlevarijs painted the Entry of the Count of Colloredo, the Imperial ambassador (1726)",
        "Haskell's note says Carlevarijs painted the Entry of the Count of Colloredo, identified as an Imperial ambassador, in 1726.",
        "The footnote does not name the Count's first name or explicitly say he commissioned the painting. Its cited catalogue page was not independently consulted.",
        ["cand-0554", "cand-0556", "cand-9292", "cand-9289"], True,
    ),
    make_statement(
        "st-chp10-notes-p277n5-colloredo-location", "cand-0556", "cand-0947",
        "book_note_reports_work_location_at_publication",
        "this picture is now in Dresden (Mauroner, 1945, p. 3 7, note 17)",
        "Haskell's note reports the Count of Colloredo entry painting in Dresden.",
        "The word 'now' is relative to Haskell's publication, not a present-day location verification. Mauroner 1945, p.37 note 17 is cited but was not independently consulted; S0 OCR spaces the page number as '3 7'.",
        ["cand-0556", "cand-0947", "cand-9289", "cand-8512"], True,
    ),
    make_statement(
        "st-chp10-notes-p277n5-gergy-entry", "cand-0498", "cand-0504",
        "artist_painted_named_ambassador_entry_work_in_1725",
        "Canaletto painted the Entry of the Comte de Gergy, the French ambassador (1725)",
        "Haskell's note says Canaletto painted the Entry of the Comte de Gergy, identified as the French ambassador, in 1725.",
        "The footnote does not name the Comte's first name or explicitly say he commissioned the painting. The artist/work distinction follows the index heading and subentry.",
        ["cand-0498", "cand-0504", "cand-9293", "cand-8642"], True,
    ),
    make_statement(
        "st-chp10-notes-p277n5-gergy-location", "cand-0504", "cand-5795",
        "book_note_reports_work_location_at_publication",
        "now in the Hermitage (Haskell, 1956, p. 298)",
        "Haskell's note reports the Comte de Gergy entry painting in the Hermitage.",
        "The word 'now' is relative to Haskell's publication and is not a present-day location verification. Haskell 1956 p.298 is cited but was not independently consulted.",
        ["cand-0504", "cand-5795", "cand-8642"], True,
    ),
    make_statement(
        "st-chp10-notes-p277n5-bolagno-entry", "cand-0498", "cand-0505",
        "artist_painted_named_ambassador_entry_work_in_1729",
        "and that of the Count of Bolagno, the Imperial ambassador (1729)",
        "Haskell's note says Canaletto painted an entry picture of the Count of Bolagno, identified as an Imperial ambassador, in 1729.",
        "The antecedent of 'that' is the entry painting in the preceding clause. The footnote gives no first name and does not explicitly say the Count commissioned the picture.",
        ["cand-0498", "cand-0505", "cand-9294", "cand-9295"], True,
    ),
    make_statement(
        "st-chp10-notes-p277n5-bolagno-location", "cand-0505", "cand-5795",
        "book_note_reports_work_location_at_publication",
        "now in the Hermitage (V. Moschini, 1954, p. 29)",
        "Haskell's note reports the Count of Bolagno entry painting in the Hermitage.",
        "The word 'now' is relative to Haskell's publication, not a present-day location verification. V. Moschini 1954 p.29 is cited but was not independently consulted.",
        ["cand-0505", "cand-5795", "cand-9295", "cand-8658"], True,
    ),
]

body_by_id = {row["statement_id"]: row for row in body_targets}
for row in body_targets:
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = 499
    q["footnote_note_statement_ids"] = [
        "st-chp10-notes-p277n5-colloredo-entry", "st-chp10-notes-p277n5-colloredo-location",
        "st-chp10-notes-p277n5-gergy-entry", "st-chp10-notes-p277n5-gergy-location",
        "st-chp10-notes-p277n5-bolagno-entry", "st-chp10-notes-p277n5-bolagno-location",
    ]
    q["qualification"] = (
        "Footnote 5 supplies examples and book-era repository reports for the named-entry pictures. "
        "It does not establish that each ambassador commissioned the picture; cited publications were not independently consulted."
    )

candidate_by_id = {row["candidate_id"]: row for row in candidates}
for cid, detail in {
    "cand-0556": "Index subentry identifies the Entry of the Count of Colloredo as a work. P.277 note 5 dates it to 1726, describes the Count as Imperial ambassador, and reports it in Dresden at the time of Haskell's note; do not infer a commission or the Count's personal identity.",
    "cand-0504": "Index subentry identifies the Entry of the Comte de Gergy as a work. P.277 note 5 dates it to 1725, describes him as French ambassador, and reports the picture in the Hermitage at the time of Haskell's note; do not infer a commission or personal identity.",
    "cand-0505": "Index subentry identifies the Entry of the Count of Bolagno as a work. P.277 note 5 dates it to 1729, describes the Count as Imperial ambassador, and reports the picture in the Hermitage at the time of Haskell's note; do not infer a commission or personal identity.",
}.items():
    candidate_by_id[cid]["suggested_type"] = "work"
    candidate_by_id[cid]["detail"] = detail
candidate_by_id["cand-8839"]["detail"] = (
    "The source supplies no full title. P.276 note 2 reports the picture in Birmingham City Art Gallery at the time of Haskell's note; "
    "p.277 note 5 restates the Entry into Venice (1707). Do not treat the book-era location as current or infer further identity."
)
candidate_by_id["cand-8845"]["detail"] += (
    " P.277 note 5 also lists the work as the Regatta in honour of Frederick IV of Denmark (1709); keep the printed Fredericksborg spelling."
)

body_cov = cov[BODY]
body_cov["note"] += " Printed p.277 note 5 at L499 is now migrated: it identifies three entry pictures and reports their book-era locations. The citations remain unverified; do not infer ambassador commissions."
notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-499"
notes_cov["note"] = (
    "Processed p.276 notes 1-3 at L492-L494 and p.277 notes 1-5 at L495-L499. L500-L634 remains pending in the merged note segment."
)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p277 note5 hash verified; planned new candidates=4, mentions=20, statements=6")
print("existing index subentries will be typed as work and linked to note 5; ambassador commissions remain unasserted")
print("book-era repository statements remain distinct from present-day verification")
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
statements.extend(newstatements)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
