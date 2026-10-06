"""Controlled S2 migration for p.281 notes 1-2 and detached Plate 50 header tail."""
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
BODY = "chp-10:10_CHP-10_intro:l125-139"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
PLATE50 = "chp-10:10_CHP-10_intro_plates_visual-transcription:l6-7"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "ea91319b1b34472e706aa01e671f2b41e1499212db9206317efaae779faf4c8c"
BACKUP = ".bak-s2-chp10-p281-notes1-2-20261002"


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
if hashlib.sha256("\n".join(src[516:519]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.281 source lines 517-519 changed")
if src[516].strip() != "05 setalP ees( /" or not src[517].startswith("1 Collins Baker") or not src[518].startswith("2 After the demolition of Canons"):
    raise SystemExit("p.281 source fragment/notes changed")

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
if maximum != 9314:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in (
    (BODY, ("reviewed", "complete")),
    (NOTES, ("reviewed", "partial")),
    (PLATE50, ("reviewed", "complete")),
):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-516":
    raise SystemExit("notes coverage pre-state changed")
if cov[PLATE50]["source_line_ranges"] != "L6-7" or "no_semantic_content" not in cov[PLATE50]["note"]:
    raise SystemExit("Plate 50 visual coverage pre-state changed")

body_targets = [row for row in statements if row["segment_id"] == BODY
                and row.get("qualifiers", {}).get("footnote_marker") in (1, 2)]
if len(body_targets) != 3 or {row["qualifiers"]["footnote_marker"] for row in body_targets} != {1, 2}:
    raise SystemExit("p.281 footnote body links changed")
if any(not row["qualifiers"].get("footnote_text_pending") for row in body_targets):
    raise SystemExit("one or more p.281 footnotes are already resolved")

needed = {"cand-8942", "cand-0531", "cand-0647", "cand-2803"}
if not needed <= cids:
    raise SystemExit(f"existing S2 candidates missing: {needed-cids}")
body_cov = cov[BODY]
stale_body_note = ("L139's revolt sentence continues at p.282 L142, so this segment remains partial. "
                   "Closed the Johann Wilhelm accession/revolt sentence with p.282 L142; the revolt remains unnamed, "
                   "and the existing statement was completed in place with cross-page provenance retained.")
if stale_body_note not in body_cov["note"]:
    raise SystemExit("expected stale body coverage note changed")

NEW_CANDIDATES = [
    ("cand-9315", "Collins Baker and Muriel I. Baker (citation locator in p.281 note 1; work unresolved)", "archive",
     "Short-form source pointer for James Brydges's creation as Duke of Chandos at age 46; title and edition are not given and the reference was not independently consulted."),
    ("cand-9316", "Watson, Arte Veneta, 1954, pp.295-301 (citation locator; article title unresolved)", "archive",
     "Citation in Haskell's p.281 note 2 for the reported transfer and later use of the Canons chapel; cited pages not independently consulted."),
    ("cand-9317", "Lord Foley named in p.281 note 2 (personal identity unresolved)", "person",
     "Haskell identifies the owner only by title and surname; do not infer a first name or specific Foley identity."),
    ("cand-9318", "Unnamed country house of Lord Foley in Worcestershire (p.281 note 2)", "place",
     "Haskell says the Canons chapel was transferred there after Canons was demolished in 1747; the country house is not named."),
    ("cand-9319", "Great Witley (place named in p.281 note 2)", "place",
     "Haskell identifies the parish church location where the former Canons chapel reportedly survives; this is not present-day verification."),
    ("cand-9320", "Worcestershire (place named in p.281 note 2)", "place",
     "Named as the county location of Lord Foley's unnamed country house; no more precise location is supplied."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L{518 if cid == 'cand-9315' else 519}",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p281notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = offsets[line_no] + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("baker-citation", 518, "Collins Baker and Muriel I. Baker.", "cand-9315")
add_mention("canons", 519, "Canons", "cand-0531")
add_mention("chapel", 519, "the chapel", "cand-8942", "Same chapel candidate as the page text; the physical interpretation of 'transferred' is retained at source wording.")
add_mention("foley-country-house", 519, "country house", "cand-9318")
add_mention("lord-foley", 519, "Lord Foley", "cand-9317")
add_mention("worcestershire", 519, "Worcestershire", "cand-9320")
add_mention("great-witley", 519, "Great Witley", "cand-9319")
add_mention("watson-article", 519, "Watson, in Arte Veneta, 1954, pp. 295-301.", "cand-9316",
            "Citation only; cited pages not independently consulted.")
add_mention("watson-author", 519, "Watson", "cand-2803")

statements = list(statements)
targets = {row["qualifiers"]["footnote_marker"]: [] for row in body_targets}
for row in body_targets:
    targets[row["qualifiers"]["footnote_marker"]].append(row)
statement_ids = [
    "st-chp10-notes-p281n2-canons-chapel-transferred",
    "st-chp10-notes-p281n2-chapel-great-witley-use",
]
if set(statement_ids) & sids:
    raise SystemExit("one or more planned statement IDs already exist")
transfer_quote = "After the demolition of Canons in 1747 the chapel was transferred to the country house of Lord Foley in Worcestershire"
survival_quote = "and it survives intact to this day as the parish church of Great Witley"
line_note2 = src[518]
for q in (transfer_quote, survival_quote):
    if q not in line_note2:
        raise SystemExit("p.281 note 2 statement quote is not anchored")
body_note2_ids = [row["statement_id"] for row in targets[2]]
newstatements = [
    {
        "statement_id": statement_ids[0], "segment_id": NOTES,
        "subject_candidate_id": "cand-8942", "object_candidate_id": "cand-9318",
        "predicate": "haskell_reports_canons_chapel_transferred_to_foley_country_house_after_1747",
        "qualifiers": {
            "source_line_start": 519, "source_line_end": 519, "printed_page": 281, "pdf_physical_page": 10,
            "claim": "Haskell reports that after Canons was demolished in 1747, the chapel was transferred to Lord Foley's unnamed country house in Worcestershire.",
            "speaker": "Haskell, footnote", "text_layer": "authorial note",
            "qualification": "The transfer date is not supplied; the source states only that it followed the 1747 demolition. The country house is unnamed, Lord Foley's identity is unresolved, and the physical scope of 'the chapel was transferred' is not independently clarified. Watson, Arte Veneta 1954, pp.295-301, is cited but not consulted.",
            "mentioned_candidate_ids": ["cand-8942", "cand-0531", "cand-9318", "cand-9317", "cand-9320", "cand-9316", "cand-2803"],
            "footnote_number": 2, "related_body_statement_ids": body_note2_ids,
            "cited_material_not_independently_consulted": True, "relation_candidate": True,
            "time_qualifier": "after the demolition of Canons in 1747; transfer date unspecified",
        },
        "original_quote": transfer_quote, "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": statement_ids[1], "segment_id": NOTES,
        "subject_candidate_id": "cand-8942", "object_candidate_id": "cand-9319",
        "predicate": "haskell_reports_canons_chapel_surviving_as_parish_church_at_great_witley",
        "qualifiers": {
            "source_line_start": 519, "source_line_end": 519, "printed_page": 281, "pdf_physical_page": 10,
            "claim": "Haskell says the former Canons chapel survives intact as the parish church of Great Witley.",
            "speaker": "Haskell, footnote", "text_layer": "authorial note",
            "qualification": "'To this day' is the source's own time reference, not a present-day status check. The source report and cited Watson pages were not independently verified; the note is preserved as the same chapel candidate without resolving the moved structure's exact physical scope.",
            "mentioned_candidate_ids": ["cand-8942", "cand-9319", "cand-9320", "cand-9316", "cand-2803"],
            "footnote_number": 2, "related_body_statement_ids": body_note2_ids,
            "cited_material_not_independently_consulted": True, "relation_candidate": True,
        },
        "original_quote": survival_quote, "origin": "book", "source_file": SOURCE_FILE,
    },
]

for row in body_targets:
    marker = row["qualifiers"]["footnote_marker"]
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = 518 if marker == 1 else 519
    q["footnote_note_statement_ids"] = statement_ids if marker == 2 else []
    q["qualification"] = (q.get("qualification", "") +
        (" P.281 note 1 cites Collins Baker and Muriel I. Baker; the cited work is not identified or independently consulted."
         if marker == 1 else
         " P.281 note 2 reports the chapel's transfer and later Great Witley parish use; cited Watson pages were not independently consulted, and the current status is unverified.")).strip()

cand_by_id = {row["candidate_id"]: row for row in candidates}
cand_by_id["cand-8942"]["detail"] += " P.281 note 2 reports it transferred after Canons' 1747 demolition and surviving as Great Witley parish church; the exact physical scope moved is unresolved."
cand_by_id["cand-0531"]["suggested_type"] = "place"
cand_by_id["cand-0531"]["detail"] = "Canons manor/palace at Edgware, distinct from the chapel interior cand-8942; Haskell's p.281 note 2 reports its demolition in 1747."

notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-519"
notes_cov["note"] = (notes_cov.get("note", "") +
    " L517 is the rotated Plate 50 header tail '(see Plates 50 and 51)' and is reconciled to visual-transcription segment l6-7, already processed as editorial navigation with no new semantic content. P.281 notes 1-2 at L518-L519 are migrated; note 1 is a bibliographic pointer, note 2 reports the chapel transfer and later Great Witley use. L520 onward remains pending.").strip()
plate_cov = cov[PLATE50]
plate_cov["note"] = (plate_cov["note"] +
    " The reversed OCR tail at body-source L517 ('05 setalP ees( /') is the same rotated '(see Plates 50 and 51)' grouping header; reconciled from the merged note segment without duplicating a mention or statement.").strip()
body_cov["note"] = body_cov["note"].replace(stale_body_note,
    "L139's revolt sentence was closed using p.282 L142 in the existing statement; the revolt remains unnamed and cross-page provenance is retained. P.281 footnote 1 at L518 and footnote 2 at L519 are now linked to the consolidated notes segment.")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p281 source L517-519 hashes verified; planned new candidates=6, mentions=9, statements=2")
print("L517 is a repeated rotated Plate 50 navigation header; notes 1-2 close three p281 body footnote links")
print("the Canons chapel remains the same candidate; transfer scope and current status stay qualified")
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
