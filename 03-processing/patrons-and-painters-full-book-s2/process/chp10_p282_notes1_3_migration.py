"""Controlled S2 migration for p.282 notes 1-3 (merged source L520-L522)."""
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
BODY = "chp-10:10_CHP-10_intro:l141-149"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "858035c4f5eb3b102cff83d432e37169deb451a466e2d12f013d1e81d1a620d0"
BACKUP = ".bak-s2-chp10-p282-notes1-3-20261002"


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
if hashlib.sha256("\n".join(src[519:522]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.282 source lines 520-522 changed")
if not src[519].startswith("1 I am most grateful to Dr Alessandro Bettagno"):
    raise SystemExit("p.282 note 1 changed")
if src[520].strip() != "2 Nicolas de Pigage.":
    raise SystemExit("p.282 note 2 changed")
if not src[521].startswith("3 Cignani painted two pictures for him:"):
    raise SystemExit("p.282 note 3 changed")

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
if maximum != 9320:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-519":
    raise SystemExit("notes coverage pre-state changed")

body_targets = [row for row in statements if row["segment_id"] == BODY
                and row.get("qualifiers", {}).get("footnote_marker") in (1, 2, 3)]
if len(body_targets) != 3 or {row["qualifiers"]["footnote_marker"] for row in body_targets} != {1, 2, 3}:
    raise SystemExit("p.282 footnote body links changed")
if any(not row["qualifiers"].get("footnote_text_pending") for row in body_targets):
    raise SystemExit("one or more p.282 footnotes are already resolved")

required = {
    "cand-2107", "cand-2108", "cand-1325", "cand-1870", "cand-0955", "cand-0748",
    "cand-1069", "cand-2480", "cand-4834", "cand-7251", "cand-7115", "cand-7155",
}
if not required <= cids:
    raise SystemExit(f"existing S2 candidates missing: {required-cids}")

NEW_CANDIDATES = [
    ("cand-9321", "Dr Alessandro Bettagno (person named in p.282 note 1)", "person",
     "Haskell thanks him for indicating Rapparini manuscripts; the note supplies no further biography or identity evidence."),
    ("cand-9322", "Nicolas de Pigage (person named in p.282 note 2)", "person",
     "The note gives only the name; no role or relation is inferred from this fragment."),
    ("cand-9323", "St John the Baptist (Carlo Cignani; work cited in p.282 note 3)", "work",
     "One of two pictures Haskell says Cignani painted for Johann Wilhelm. The paired dates 1702 and 1715 are not individually assigned to either picture."),
    ("cand-9324", "Jupiter Giving Suck (Carlo Cignani; work cited in p.282 note 3)", "work",
     "One of two pictures Haskell says Cignani painted for Johann Wilhelm. The paired dates 1702 and 1715 are not individually assigned to either picture."),
    ("cand-9325", "Venus and The Three Graces (Marcantonio Franceschini; p.282 note 3)", "work",
     "Work Haskell says Franceschini painted for Johann Wilhelm; the title is retained as printed in the note."),
    ("cand-9326", "St Teresa Wounded by Christ (Giovan Gioseffo dal Sole; p.282 note 3)", "work",
     "Work Haskell says Dal Sole painted for Johann Wilhelm; no date or present location is supplied here."),
    ("cand-9327", "Rape of the Sabines (Giovan Gioseffo dal Sole; p.282 note 3)", "work",
     "Work Haskell says Dal Sole painted for Johann Wilhelm; distinct from other works with the same title in the candidate list."),
    ("cand-9328", "Augsburg (place named as one reported location for the Cignani pictures, p.282 note 3)", "place",
     "One of two locations reported by Haskell through Lavagnino for Cignani's two pictures; the note does not map an individual picture to Augsburg or Munich, and this is not current-location verification."),
    ("cand-9329", "Rapparini manuscripts published in Düsseldorf in 1958 (source set identified in p.282 note 1)", "archive",
     "Haskell says Alessandro Bettagno directed him to this published manuscript set. The note names Le Portrait du Vrai Mérite... as a Rapparini eulogy written in 1709; the edition and cited text were not independently consulted."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L{520 if cid in {'cand-9321', 'cand-9329'} else 521 if cid == 'cand-9322' else 522}",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p282notes-{local}"
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


title_line = src[519]
title_start = title_line.index("Le Portrait")
title_end = title_line.index(" gives", title_start)
title_surface = title_line[title_start:title_end]
add_mention("bettagno", 520, "Dr Alessandro Bettagno", "cand-9321")
add_mention("rapparini", 520, "Rapparini", "cand-2107")
add_mention("dusseldorf", 520, "Dusseldorf", "cand-0955", "The printed page has Düsseldorf; correction is recorded at S2 without changing S0.")
add_mention("eulogy-title", 520, title_surface, "cand-2108", "Index subentry is typed as archive; print reads Mérite, while S0 OCR reads Mérité. S0 is unchanged.")
add_mention("johann-wilhelm", 520, "Johann Wilhelm", "cand-1325")
add_mention("pellegrini", 520, "Pellegrini", "cand-1870")
add_mention("rapparini-manuscripts", 520, "manuscripts of Rapparini", "cand-9329",
            "Published source set is distinct from the named 1709 eulogy subentry cand-2108.")
add_mention("pigage", 521, "Nicolas de Pigage", "cand-9322")
add_mention("cignani", 522, "Cignani", "cand-0748")
add_mention("cignani-john", 522, "a St John the Baptist", "cand-9323")
add_mention("cignani-jupiter", 522, "a Jupiter giving Suck", "cand-9324")
add_mention("pascoli", 522, "Pascoli", "cand-4834", "Citation to vol. I, pp.165-168; cited pages not independently consulted.")
add_mention("augsburg", 522, "Augsburg", "cand-9328")
add_mention("munich", 522, "Munich", "cand-7155", "The source reports a city-level location and does not identify a specific institution.")
add_mention("lavagnino", 522, "Lavagnino", "cand-7251", "Citation to p.85; exact volume is not stated in this note and the cited page was not consulted.")
add_mention("franceschini", 522, "Franceschini", "cand-1069")
add_mention("venus-graces", 522, "Venus and The Three Graces", "cand-9325")
add_mention("dal-sole", 522, "Dal Sole", "cand-2480")
add_mention("st-teresa", 522, "a St Teresa wounded by Christ", "cand-9326")
add_mention("rape-sabines", 522, "a Rape of the Sabines", "cand-9327")
add_mention("zanotti", 522, "Zanotti", "cand-7115", "Citation to vol. I, pp.228 and 306-307; cited pages not independently consulted.")

targets = {row["qualifiers"]["footnote_marker"]: row for row in body_targets}
body_ids = {marker: [targets[marker]["statement_id"]] for marker in (1, 2, 3)}
statement_ids = [
    "st-chp10-notes-p282n1-bettagno-indicated-manuscripts",
    "st-chp10-notes-p282n1-portrait-patronage-account",
    "st-chp10-notes-p282n1-eulogy-1709-no-pellegrini",
    "st-chp10-notes-p282n3-cignani-john-the-baptist",
    "st-chp10-notes-p282n3-cignani-jupiter-giving-suck",
    "st-chp10-notes-p282n3-cignani-locations",
    "st-chp10-notes-p282n3-franceschini-venus-graces",
    "st-chp10-notes-p282n3-dal-sole-st-teresa",
    "st-chp10-notes-p282n3-dal-sole-rape-sabines",
]
if set(statement_ids) & sids:
    raise SystemExit("one or more planned statement IDs already exist")

quote_bettagno = "I am most grateful to Dr Alessandro Bettagno for indicating to me the manuscripts of Rapparini which were published in Dusseldorf in 1958."
quote_account = title_line[title_start:title_line.index(", but as the eulogy", title_start)]
quote_eulogy = "but as the eulogy was written in 1709 there are naturally no references to Pellegrini."
quote_cignani = "Cignani painted two pictures for him: a St John the Baptist and a Jupiter giving Suck in 1702 and 1715"
quote_cignani_locations = "These pictures are now at Augsburg and Munich"
quote_franceschini = "Franceschini painted for him a Venus and The Three Graces"
quote_dal_sole = "and Dal Sole a St Teresa wounded by Christ and a Rape of the Sabines"
for quote in (quote_bettagno, quote_account, quote_eulogy, quote_cignani, quote_cignani_locations,
              quote_franceschini, quote_dal_sole):
    if quote not in "\n".join(src[519:522]):
        raise SystemExit(f"statement quote not found in p.282 notes: {quote!r}")

def note_statement(sid, line_no, subject, obj, predicate, claim, quote, qualification,
                   mentioned, marker, relation_candidate=False, consulted=False, extras=None):
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no, "printed_page": 282, "pdf_physical_page": 11,
        "claim": claim, "speaker": "Haskell, footnote", "text_layer": "authorial note",
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "footnote_number": marker, "related_body_statement_ids": body_ids[marker],
        "cited_material_not_independently_consulted": consulted,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": sid, "segment_id": NOTES, "subject_candidate_id": subject,
        "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    }


newstatements = [
    note_statement(statement_ids[0], 520, "cand-9321", "cand-9329", "bettagno_indicated_rapparini_manuscripts_to_haskell",
        "Haskell thanks Dr Alessandro Bettagno for indicating Rapparini manuscripts published in Düsseldorf in 1958.",
        quote_bettagno, "The note does not identify the full edited collection; the named eulogy appears in the index subentry and is kept distinct from the person Rapparini.",
        ["cand-9321", "cand-2107", "cand-2108", "cand-9329", "cand-0955"], 1, True,
        extras={"ocr_corrections": [{"source_file": SOURCE_FILE, "source_line": 520, "ocr": "Dusseldorf", "print": "Düsseldorf", "basis": "CHP-10.pdf physical page 11."}]}),
    note_statement(statement_ids[1], 520, None, "cand-2108", "haskell_describes_rapparini_eulogy_as_account_of_wilhelm_patronage",
        "Haskell says the named Rapparini eulogy gives a fairly full account of Johann Wilhelm's patronage.",
        quote_account, "This is Haskell's description of the text. S0 reads 'hill'; the print reads 'full'. The cited eulogy was not independently consulted.",
        ["cand-2108", "cand-2107", "cand-1325"], 1, consulted=True,
        extras={"ocr_corrections": [
            {"source_file": SOURCE_FILE, "source_line": 520, "ocr": "Mérité", "print": "Mérite", "basis": "CHP-10.pdf physical page 11."},
            {"source_file": SOURCE_FILE, "source_line": 520, "ocr": "hill", "print": "full", "basis": "CHP-10.pdf physical page 11."},
        ]}),
    note_statement(statement_ids[2], 520, "cand-2107", "cand-2108", "rapparini_eulogy_written_in_1709_precedes_pellegrini",
        "Haskell says the Rapparini eulogy was written in 1709 and therefore contains no references to Pellegrini.",
        quote_eulogy, "The date and absence of references are Haskell's account of the eulogy; the manuscript/publication was not independently consulted.",
        ["cand-2107", "cand-2108", "cand-1870"], 1, True, consulted=True),
    note_statement(statement_ids[3], 522, "cand-0748", "cand-9323", "cignani_painted_st_john_the_baptist_for_johann_wilhelm",
        "Haskell says Carlo Cignani painted a St John the Baptist for Johann Wilhelm as one of two works dated 1702 and 1715.",
        quote_cignani, "The note names two works and two years but does not unambiguously assign an individual year to this title; no individual date is asserted. Pascoli, vol. I, pp.165-168, is cited but not consulted.",
        ["cand-0748", "cand-9323", "cand-9324", "cand-1325", "cand-4834"], 3, True, consulted=True,
        extras={"date_assignment": "The source gives 1702 and 1715 for the pair without an unambiguous title-to-year mapping."}),
    note_statement(statement_ids[4], 522, "cand-0748", "cand-9324", "cignani_painted_jupiter_giving_suck_for_johann_wilhelm",
        "Haskell says Carlo Cignani painted a Jupiter giving Suck for Johann Wilhelm as one of two works dated 1702 and 1715.",
        quote_cignani, "The note names two works and two years but does not unambiguously assign an individual year to this title; no individual date is asserted. Pascoli, vol. I, pp.165-168, is cited but not consulted.",
        ["cand-0748", "cand-9323", "cand-9324", "cand-1325", "cand-4834"], 3, True, consulted=True,
        extras={"date_assignment": "The source gives 1702 and 1715 for the pair without an unambiguous title-to-year mapping."}),
    note_statement(statement_ids[5], 522, None, None, "cignani_pair_reported_at_augsburg_and_munich",
        "Haskell reports the two Cignani pictures at Augsburg and Munich.", quote_cignani_locations,
        "The note does not assign either city to an individual picture. 'Now' is source-relative to Haskell's account, not current-location verification. Lavagnino, p.85, is cited but not consulted.",
        ["cand-9323", "cand-9324", "cand-9328", "cand-7155", "cand-7251"], 3, consulted=True,
        extras={"location_assignment": "Augsburg and Munich are reported for the pair; work-to-city mapping is unspecified."}),
    note_statement(statement_ids[6], 522, "cand-1069", "cand-9325", "franceschini_painted_venus_and_three_graces_for_johann_wilhelm",
        "Haskell says Marcantonio Franceschini painted Venus and The Three Graces for Johann Wilhelm.", quote_franceschini,
        "The note gives no date or location for the work. Zanotti, vol. I, pp.228 and 306-307, is cited but not consulted.",
        ["cand-1069", "cand-9325", "cand-1325", "cand-7115"], 3, True, consulted=True),
    note_statement(statement_ids[7], 522, "cand-2480", "cand-9326", "dal_sole_painted_st_teresa_wounded_by_christ_for_johann_wilhelm",
        "Haskell says Giovan Gioseffo dal Sole painted St Teresa Wounded by Christ for Johann Wilhelm.", quote_dal_sole,
        "The note gives no date or location for this work. Zanotti, vol. I, pp.228 and 306-307, is cited but not consulted.",
        ["cand-2480", "cand-9326", "cand-1325", "cand-7115"], 3, True, consulted=True),
    note_statement(statement_ids[8], 522, "cand-2480", "cand-9327", "dal_sole_painted_rape_of_the_sabines_for_johann_wilhelm",
        "Haskell says Giovan Gioseffo dal Sole painted a Rape of the Sabines for Johann Wilhelm.", quote_dal_sole,
        "This is distinct from other same-titled works in the candidate list. The note gives no date or location. Zanotti, vol. I, pp.228 and 306-307, is cited but not consulted.",
        ["cand-2480", "cand-9327", "cand-1325", "cand-7115"], 3, True, consulted=True),
]

for row in body_targets:
    marker = row["qualifiers"]["footnote_marker"]
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = 520 if marker == 1 else 521 if marker == 2 else 522
    q["footnote_note_statement_ids"] = [s["statement_id"] for s in newstatements if s["qualifiers"]["footnote_number"] == marker]
    q["qualification"] = (q.get("qualification", "") +
        (" P.282 note 1 cites the Rapparini eulogy; its statements are Haskell's account and the cited text was not independently consulted."
         if marker == 1 else
         " P.282 note 2 consists only of the name Nicolas de Pigage; no role or relation is inferred."
         if marker == 2 else
         " P.282 note 3 reports named Cignani, Franceschini, and dal Sole works; the paired dates and locations are not assigned to individual Cignani paintings, and cited sources were not consulted.")).strip()

cand_by_id = {row["candidate_id"]: row for row in candidates}
cand_by_id["cand-2108"]["suggested_type"] = "archive"
cand_by_id["cand-2108"]["detail"] = "Index subentry names Rapparini's Le Portrait du Vrai Mérite...; p.282 note 1 identifies it as a 1709 eulogy published among his manuscripts in Düsseldorf in 1958. The cited text was not independently consulted."
cand_by_id["cand-0955"]["suggested_type"] = "place"
cand_by_id["cand-0955"]["detail"] = "Düsseldorf city, indexed at pp.281-284; p.282 note 1 reports the 1958 publication location for Rapparini manuscripts. S0 spelling is preserved; print correction is recorded in S2."
cand_by_id["cand-4834"]["detail"] += " P.282 note 3 cites vol. I, pp.165-168; the cited pages were not independently consulted."
cand_by_id["cand-7251"]["detail"] += " P.282 note 3 cites Lavagnino, p.85 without volume; this citation has not been confirmed as vol. III and the page was not consulted."
cand_by_id["cand-7115"]["detail"] += " P.282 note 3 cites vol. I, pp.228 and 306-307; cited pages were not independently consulted."
cand_by_id["cand-7155"]["detail"] += " P.282 note 3 reports one of two Cignani works at Munich at the time of Haskell's account; no individual painting or institution is assigned."

notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-522"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.282 notes 1-3 at L520-L522 are migrated: note 1 records Bettagno's pointer and Haskell's claims about Rapparini's 1709 eulogy; note 2 names Nicolas de Pigage without further context; note 3 records Cignani, Franceschini, and dal Sole works with unassigned paired dates/locations. OCR corrections are recorded in S2 only. Cited pages were not independently consulted. L523 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p282 source L520-L522 hashes verified; planned new candidates=9, mentions=21, statements=9")
print("linked the three printed footnote markers; assigned no individual Cignani date or city")
print("reused indexed Rapparini title and existing Pascoli, Lavagnino, and Zanotti archive candidates")
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
