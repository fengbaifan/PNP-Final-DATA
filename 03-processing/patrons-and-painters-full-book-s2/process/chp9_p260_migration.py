"""Controlled S2 migration for printed p.260; defaults to a read-only dry run."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
VISUAL = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro_notes_p260_visual-transcription.md"
P259 = "chp-9:09_CHP-9_intro:l188-200"
P260 = "chp-9:09_CHP-9_intro:l202-210"
P261 = "chp-9:09_CHP-9_intro:l212-216"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
VISUAL_ID = "chp-9:09_CHP-9_intro_notes_p260_visual-transcription:l1-1"
EXPECTED_P260_HASH = "ffbd53ac783c55a991bc4629b6bde3328e0708acce1819a1412f55607387ce6d"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p260-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {r["segment_id"]: r for r in segments}
for sid in (P259, P260, P261, NOTES, VISUAL_ID):
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
if segment_by_id[P260]["sha256"] != EXPECTED_P260_HASH or segment_by_id[P260]["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.260 source segment or source asset fingerprint changed")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("S0 OCR asset changed")
visual_meta = segment_by_id[VISUAL_ID]
visual_asset_hash = hashlib.sha256(VISUAL.read_bytes()).hexdigest()
if visual_asset_hash != visual_meta["asset_sha256"]:
    raise SystemExit("p.260 visual transcription asset hash changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
visual_lines = VISUAL.read_text(encoding="utf-8-sig").splitlines()
sources = {P260: source_lines, NOTES: source_lines, VISUAL_ID: visual_lines}


def line_offsets(segment_id):
    meta = segment_by_id[segment_id]
    rows = sources[segment_id]
    offsets, offset = {}, 0
    for n in range(meta["line_start"], meta["line_end"] + 1):
        offsets[n] = offset
        offset += len(rows[n - 1]) + 1
    return offsets


offsets = {sid: line_offsets(sid) for sid in sources}


def quote(segment_id, first, last):
    return "\n".join(sources[segment_id][n - 1] for n in range(first, last + 1))


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {r["segment_id"]: r for r in coverage}
expected_states = {
    P259: ("reviewed", "partial", "L189-200"),
    P260: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-394; p.255 L155 continuation"),
}
for sid, expected in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage for {sid}: {row}")
if VISUAL_ID in coverage_by_id:
    raise SystemExit("p.260 visual coverage already exists; inspect before retry")
candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8490:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")

C = {
    "rooms_group": "cand-8491",
    "novelli_s_marco": "cand-8492",
    "novelli_history": "cand-8493",
    "guarana_frescoes": "cand-8494",
    "nogari_portrait": "cand-8495",
    "pisani_academy": "cand-8496",
    "tiepolo_prints": "cand-8497",
    "past_figures_images": "cand-8498",
    "muses": "cand-8499",
    "pisani_family": "cand-8500",
    "miani_family": "cand-8501",
    "baglione_family": "cand-8502",
    "arnaldi": "cand-8503",
    "arnaldi_book": "cand-8504",
    "brosses_citation": "cand-8505",
    "moschini_1808": "cand-8506",
    "gradenigo": "cand-8507",
    "gradenigo_citation": "cand-8508",
    "molino": "cand-8509",
    "molino_book": "cand-8510",
    "moschini_1806": "cand-8511",
    "mauroner": "cand-8512",
    "mauroner_citation": "cand-8513",
    "gallo": "cand-8514",
    "gallo_citation": "cand-8515",
    "ceiling_fresco": "cand-8516",
    "patrician_glorification": "cand-8517",
    "drawing_lessons": "cand-8518",
    "foscarini_rooms": "cand-8519",
    "venetian_painters_group": "cand-8520",
    "tiepolo_drawings": "cand-8521",
}
candidate_specs = [
    (8491, "Portraits and busts of distinguished men described in Foscarini's rooms", "", P260, 207,
     "Unidentified group in the contemporary description of Marco Foscarini's rooms; no individual portraits or sitters are named."),
    (8492, "Saint Mark painting by Pietro Antonio Novelli made for Marco Pitteri", "work", P260, 205,
     "Painting described in Novelli's recollection as made for engraver Marco Pitteri; no title, date, or present location is supplied."),
    (8493, "Unidentified history picture requested by Marco Foscarini from Pietro Antonio Novelli", "work", P260, 205,
     "Novelli says Foscarini wanted a history picture after admiring his Saint Mark; no subject or evidence of completion is given."),
    (8494, "Frescoes by Giacomo Guarana in the Foscarini palace", "work", P260, 205,
     "Plural frescoes attributed in Haskell's account; no subject, date, or present condition is supplied."),
    (8495, "Unidentified portrait of Marco Foscarini by Giuseppe Nogari", "work", P260, 206,
     "Portrait is named without title, date, or location; kept distinct from Batoni's portrait candidate."),
    (8496, "Private academy organized by the Pisani with Pietro Longhi in charge", "institution", P260, 208,
     "A source-described private academy; Haskell says it seems to have provided drawing lessons to the Pisani's son and ended with his death."),
    (8497, "Prints from Tiepolo drawings of Oriental heads dedicated to Marco Foscarini", "work", NOTES, 399,
     "Plural prints described only in p.260 note 5; no individual print titles or publication details are supplied."),
    (8498, "Sculpted images of great figures of the past made for Marco Foscarini", "work", P260, 205,
     "Source-described group of sculptural images in marble, ivory, and metal; the figures and artists are not named."),
    (8499, "Muses invoked in the contemporary description of Foscarini's rooms", "term", P260, 207,
     "Rhetorical/mythological collective in the contemporary quotation, not a claim that identifiable figures literally lived in the rooms."),
    (8500, "Pisani family in Haskell's account of a private academy", "family", P260, 208,
     "Family named collectively as organizing an academy and providing drawing lessons to their son; members other than the son are not specified."),
    (8501, "Miani of Camerata (household-employment example in Haskell's note 8)", "family", VISUAL_ID, 1,
     "Source-named group in a list of examples; retain the place qualifier and do not expand to individual members."),
    (8502, "Baglione of Polazzo (household-employment example in Haskell's note 8)", "family", VISUAL_ID, 1,
     "Source-named group in a list of examples; retain the place qualifier and do not expand to individual members."),
    (8503, "Lodovico Arnaldi", "person", NOTES, 395,
     "Person named as author of an oration cited by Haskell; identity beyond the citation form is not resolved."),
    (8504, "Lodovico Arnaldi, Orazione in lode di Marco Foscarini Doge di Venezia", "archive", NOTES, 395,
     "Work title as cited in p.260 note 1; not independently consulted."),
    (8505, "De Brosses, volume II, page 39 (citation locator)", "archive", NOTES, 395,
     "Citation locator in note 1 for the quoted description of Marco Foscarini; the cited page was not independently consulted."),
    (8506, "G. A. Moschini, 1808, page 139 (citation locator)", "archive", NOTES, 397,
     "Bibliographic locator in p.260 note 3; title is not supplied and the cited page was not independently consulted."),
    (8507, "Gradenigo", "person", NOTES, 398,
     "Surname-only author cited in p.260 note 4; identity is unresolved."),
    (8508, "Gradenigo, page 91 (citation locator)", "archive", NOTES, 398,
     "Citation locator in p.260 note 4; the work and cited page were not independently consulted."),
    (8509, "Sebastiano Molino", "person", NOTES, 400,
     "Person named as author of an oration cited in p.260 note 6; identity is limited to the citation form."),
    (8510, "Sebastiano Molino, Orazione in lode di Marco Foscarini Procurator di S. Marco", "archive", NOTES, 400,
     "Work title as cited in p.260 note 6; not independently consulted."),
    (8511, "G. A. Moschini, 1806, volume III, pages 49 and 70 (citation locators)", "archive", NOTES, 401,
     "Notes 7 and 8 cite this bibliographic form at pages 49 and 70; the cited pages were not independently consulted."),
    (8512, "Mauroner", "person", VISUAL_ID, 1,
     "Surname-only author cited in p.260 note 8; identity is unresolved."),
    (8513, "Mauroner, page 15 (citation locator)", "archive", VISUAL_ID, 1,
     "Citation locator in p.260 note 8; title and cited page are not supplied beyond the locator and were not independently consulted."),
    (8514, "Gallo", "person", NOTES, 403,
     "Surname-only author cited in p.260 note 9; identity is unresolved."),
    (8515, "Gallo, 1945, page 53 (citation locator)", "archive", NOTES, 403,
     "Citation locator in p.260 note 9; title and cited page were not independently consulted."),
    (8516, "Ceiling fresco as a prevalent form of patrician glorification", "term", P260, 209,
     "Art form and patronage tendency identified in Haskell's argument; the claim is not quantified beyond the passage."),
    (8517, "Patrician self-glorification in Haskell's account", "term", P260, 209,
     "Explanatory concept in Haskell's account of Venetian patronage; not an independently measured motive."),
    (8518, "Drawing lessons given to the Pisani's son", "procedure", P260, 208,
     "Activity attributed to the private academy; Haskell says it seems to have done little more than provide these lessons."),
    (8519, "Rooms in the Foscarini palace for books, portraits, and busts", "place", P260, 203,
     "Interior rooms described across pp.260; kept distinct from the palace as a whole, but no individual room is named."),
    (8520, "Great names of Venetian painting (unnamed group in Haskell's account)", "", P260, 207,
     "Collective wording without individual names; retain as an untyped candidate rather than inventing a roster."),
    (8521, "Tiepolo drawings of Oriental heads", "work", NOTES, 399,
     "Drawings from which the prints mentioned in note 5 were taken; individual drawing titles are not supplied."),
]
natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    cid = f"cand-{n:04d}"
    if cid in candidate_ids or (name, kind) in natural_keys:
        raise SystemExit(f"candidate ID/natural-key collision: {cid} {name} / {kind}")
    candidates.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                       "index_page_range": "", "suggested_type": kind, "status": "open",
                       "index_source_file": "", "sub_entry": "", "detail": detail,
                       "exclude_reason": "", "candidate_origin": "body-mention",
                       "candidate_source_ref": f"{source_segment}#L{line_no}"})
    candidate_ids.add(cid)
    natural_keys.add((name, kind))

# p.258-259 already introduced the unnamed picture group; p.260 resolves its description.
existing_group = [r for r in candidates if r["candidate_id"] == "cand-8485"]
if len(existing_group) != 1:
    raise SystemExit("expected one p.259 unnamed picture-group candidate")
existing_group[0]["detail"] = "Haskell's continuation on p.260 says these pictures represented great writers of Venice and hung in the rooms where Foscarini kept their books; many seem to have been painted in Rome. Still unnamed, so retain an untyped source-described group."

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(segment_id, line, suffix, cid, surface, note="", last_line=None, occurrence=0):
    mid = f"m-chp9-p260-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    last_line = line if last_line is None else last_line
    text = "\n".join(sources[segment_id][n - 1] for n in range(line, last_line + 1))
    start_at, pos = 0, -1
    for _ in range(occurrence + 1):
        pos = text.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found in {segment_id} L{line}-{last_line}: {surface!r}")
        start_at = pos + len(surface)
    start = offsets[segment_id][line] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    (P260,203,"writers-venice","cand-8485","great writers of Venice","Describes the still-unnamed picture group introduced on p.259."),
    (P260,203,"venice-writers","cand-2719","Venice","City whose writers are represented; distinguish from the Venetian State."),
    (P260,203,"rooms-books","cand-8519","the rooms","Rooms in the Foscarini family palace; the text does not name individual rooms."),
    (P260,203,"books-in-rooms","cand-8462","their books","Anaphoric to the books and manuscripts in Foscarini's library described on p.259."),
    (P260,204,"paintings-rome","cand-8485","Many of them","Anaphoric to the pictures representing Venetian writers; Haskell says many seem to have been painted in Rome."),
    (P260,204,"rome-painted","cand-4490","Rome","City in Haskell's qualified account of where many pictures seem to have been painted."),
    (P260,204,"marco-foscarini","cand-1053","Marco Foscarini","Existing candidate reused."),
    (P260,205,"de-brosses","cand-0455","President de Brosses","Existing surname-form candidate reused; preserve the source title and quotation layer."),
    (P260,205,"native-city","cand-2719","his native city","Anaphoric to Venice in the preceding sentence."),
    (P260,205,"rome-acquired","cand-4490","in Rome","Place where Haskell says Foscarini acquired the books and manuscripts."),
    (P260,205,"books-and-manuscripts","cand-8462","books and manuscripts","Part of Foscarini's source-described collection; no titles are given."),
    (P260,205,"family-palace","cand-1059","the-family palace","OCR hyphen retained in the surface; the referent is the Foscarini family palace."),
    (P260,205,"novelli-room","cand-8519","his room","Room in the Foscarini palace where Novelli says the Saint Mark picture was kept for four days."),
    (P260,205,"sculpted-images","cand-8498","images","Anaphoric to the sculpted records of past figures, not to the later paintings by Novelli."),
    (P260,205,"novelli","cand-1758","Pietro Antonio Novelli","Existing person candidate reused; the quotation is nested within Haskell's report."),
    (P260,205,"saint-mark-painting","cand-8492","a S. Marco","Title/subject wording for the unidentified painting made for Marco Pitteri."),
    (P260,205,"pitteri","cand-1948","Marco Pitteri","Existing artist/engraver candidate reused."),
    (P260,205,"history-picture","cand-8493","a history picture","Requested in Novelli's recollection; no subject or completion status is stated."),
    (P260,205,"guarana","cand-1237","Giacomo Guarana","Existing candidate reused."),
    (P260,205,"tiepolo","cand-2569","Tiepolo","Haskell describes Guarana as a follower of Tiepolo."),
    (P260,205,"guarana-frescoes","cand-8494","frescoes","Plural frescoes attributed to Guarana in the palace; no subjects are named."),
    (P260,205,"palace-guarana","cand-1059","the palace","Foscarini palace from the preceding context."),
    (P260,206,"nogari","cand-1743","Giuseppe Nogari","Existing candidate reused."),
    (P260,206,"portrait-nogari","cand-8495","his portrait","Portrait of Marco Foscarini by Nogari; distinct from the Batoni portrait noted on p.259."),
    (P260,207,"leading-venetian-painters","cand-8520","The great names of Venetian painting","General art-historical grouping; no names are listed here."),
    (P260,207,"life-marco","cand-1053","his life","Anaphoric to Marco Foscarini."),
    (P260,207,"rooms-contemporary","cand-8519","lais rooms","OCR surface; CHP-9.pdf physical p.22 reads 'his rooms'."),
    (P260,207,"portraits-busts","cand-8491","the portraits and busts of great men","Unnamed group in the contemporary description."),
    (P260,207,"muses","cand-8499","the very Muses themselves","Rhetorical figures in the quoted description."),
    (P260,208,"moschini-body","cand-1709","the Abate Moschini","Existing candidate reused."),
    (P260,208,"pisani-family","cand-8500","the Pisani","Family as the subject of the academy and household-employment account."),
    (P260,208,"private-academy","cand-8496","a private academy","Source-described institution; no formal name or location is supplied."),
    (P260,208,"pietro-longhi","cand-1429","Pietro Longhi","Existing artist candidate reused."),
    (P260,208,"pisani-son","cand-1941","their son Almord","Existing indexed candidate reused; scan reads Almorò, recorded in S2 without changing S0."),
    (P260,208,"drawing-lessons","cand-8518","drawing lessons","Only function attributed to the academy in Haskell's qualified account."),
    (P260,208,"son-death","cand-1941","his death","The son's death as the reported end point; no date is given."),
    (P260,209,"restricted-patronage","cand-1053","this patronage","Anaphoric to Venetian artistic patronage, including Foscarini's context."),
    (P260,209,"moschini-objection","cand-1709","Moschini","The critic whose rebuttal Haskell describes."),
    (P260,209,"venetian-support","cand-2719","Venetian support","Refers to support from Venice; the institutional/civic reading is not resolved beyond Haskell's wording."),
    (P260,209,"patrician-class","cand-8517","the patrician","The social group in Haskell's explanation of self-glorification."),
    (P260,209,"ceiling-fresco","cand-8516","the ceiling fresco","Art form Haskell says became concentrated under patrician self-glorification."),
    (NOTES,395,"arnaldi-note","cand-8503","Lodovico Arnaldi","Author named in footnote 1."),
    (NOTES,395,"arnaldi-orazione","cand-8504","Orazione in lode di Marco Foscarini Doge di Venezia","Work cited in footnote 1."),
    (NOTES,395,"de-brosses-note","cand-0455","De Brosses","Existing candidate reused for the footnote citation."),
    (NOTES,395,"de-brosses-page","cand-8505","II, p. 39","Volume and page locator in footnote 1."),
    (NOTES,396,"novelli-citation","cand-1758","Novelli","Surname citation for note 2; identity is linked to the preceding quotation by context."),
    (NOTES,396,"novelli-memoirs","cand-8363","p. 16","Page locator for the Novelli citation; reuse the existing memoir candidate."),
    (NOTES,397,"moschini-1808-author","cand-1709","G. A. Moschini","Existing author candidate reused."),
    (NOTES,397,"moschini-1808-page","cand-8506","1808, p. 139","Year and page locator in note 3."),
    (NOTES,398,"gradenigo-author","cand-8507","Gradenigo","Surname-only author citation in note 4."),
    (NOTES,398,"gradenigo-page","cand-8508","p. 91","Page locator in note 4."),
    (NOTES,399,"tiepolo-notes","cand-2569","Tiepolo","Existing artist candidate reused in the note about prints from his drawings."),
    (NOTES,399,"oriental-prints","cand-8497","prints","Plural prints from Tiepolo's drawings; individual works are unnamed."),
    (NOTES,399,"oriental-drawings","cand-8521","drawings","Tiepolo drawings from which the prints were taken."),
    (NOTES,399,"oriental-heads","cand-8521","Oriental heads","Subject of Tiepolo's drawings from which the prints were taken."),
    (NOTES,399,"foscarini-print-dedication","cand-1053","him","Anaphoric to Marco Foscarini, to whom the prints were dedicated."),
    (NOTES,400,"molino-author","cand-8509","Sebastiano Molino","Author named in note 6."),
    (NOTES,400,"molino-orazione","cand-8510","Orazione in lode di Marco Foscarini Procurator di S. Marco","Work cited in note 6."),
    (NOTES,400,"molino-foscarini","cand-1053","Marco Foscarini","Person named in the cited oration's title."),
    (NOTES,401,"moschini-1806-author","cand-1709","G. A. Moschini","Existing author candidate reused."),
    (NOTES,401,"moschini-volume","cand-8511","1806, III, p. 49","Volume and page locator in note 7."),
    (VISUAL_ID,1,"zenobio-family","cand-2870","Zenobio","Existing family candidate reused."),
    (VISUAL_ID,1,"carlevarijs","cand-0554","Carlevarijs","Existing artist candidate reused."),
    (VISUAL_ID,1,"mauroner","cand-8512","Mauroner","Surname-only author named in the parenthetical citation."),
    (VISUAL_ID,1,"mauroner-page","cand-8513","p. 15","Page locator for Mauroner."),
    (VISUAL_ID,1,"miani-family","cand-8501","Miani of Camerata","Source-named family/group; do not expand to individuals."),
    (VISUAL_ID,1,"baglione-family","cand-8502","Baglione of Polazzo","Source-named family/group; do not expand to individuals."),
    (VISUAL_ID,1,"alessandro-longhi","cand-1424","Alessandro Longhi","Existing artist candidate reused; exact assignment in the list is not expanded."),
    (VISUAL_ID,1,"zambelli-family","cand-2832","Zambelli","Existing family candidate reused."),
    (VISUAL_ID,1,"pittoni","cand-1950","Pittoni","Existing artist candidate reused."),
    (VISUAL_ID,1,"moschini-note8","cand-1709","G. A. Moschini","Existing author candidate reused for the note 8 continuation."),
    (VISUAL_ID,1,"moschini-page70","cand-8511","p. 70","Second page locator to the same volume cited in note 7."),
    (NOTES,403,"gallo-author","cand-8514","Gallo","Surname-only author named in note 9."),
    (NOTES,403,"gallo-page","cand-8515","1945, p. 53","Year and page locator in note 9."),
]
for sid, line, suffix, cid, surface, note in M:
    mention(sid, line, suffix, cid, surface, note)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="body", extras=None):
    sid = f"st-chp9-p260-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement span out of segment: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 260,
         "pdf_physical_page": 22, "claim": claim, "speaker": speaker, "text_layer": text_layer,
         "qualification": qualification,
         "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": meta["source_file"]})


statement("writers-pictures", P260,203,203,"cand-8485","cand-2719",
          "pictures_represent_great_writers_of_venice",
          "Haskell says Foscarini's other pictures represented the great writers of Venice and hung in the rooms where he kept their books.",
          "Continuation of p.259's unnamed group; no titles or individual writers are identified.",
          ["cand-8485","cand-2719","cand-8519","cand-8462"])
statement("pictures-seem-painted-rome", P260,204,204,"cand-8485","cand-4490",
          "many_pictures_seem_painted_in_rome",
          "Haskell says many of the pictures seem to have been painted in Rome.",
          "Preserve 'seem'; this is the author's qualified account, not an externally verified production location.",
          ["cand-8485","cand-4490","cand-1053"])
statement("foscarini-prestige-native-city", P260,204,204,"cand-1053","cand-2719",
          "foscarini_worked_to_maintain_native_city_prestige",
          "Haskell says Foscarini did everything he could to maintain the prestige of his native city.",
          "The city is anaphorically Venice; the de Brosses phrase is a nested quotation within Haskell's narrative.",
          ["cand-1053","cand-2719","cand-0455"])
statement("books-and-manuscripts-returned", P260,205,205,"cand-1053","cand-8462",
          "acquired_books_and_manuscripts_in_rome_and_brought_them_home",
          "Haskell says Foscarini acquired large numbers of books and manuscripts in Rome and brought them back to the family palace.",
          "Preserve the source's quantity wording and the quoted Italian 'quasi trionfando'; no individual books or manuscripts are named.",
          ["cand-1053","cand-8462","cand-4490","cand-1059"])
statement("sculptors-and-past-images", P260,205,205,"cand-1053","cand-8498",
          "employed_sculptors_in_two_cities_to_record_figures_of_the_past",
          "Haskell says Foscarini employed sculptors in Rome and Venice, working in marble, ivory, and metal, to record great figures of the past.",
          "The artists and depicted figures are unnamed; retain the source-described group of sculptural images without assigning authorship.",
          ["cand-1053","cand-4490","cand-2719","cand-8498"])
statement("sculptural-images-now-gone", P260,205,205,"cand-8498",None,
          "all_images_gone_and_artists_unknown",
          "Haskell says all these images were gone and that there was no indication of the artists who made them.",
          "This is Haskell's statement about the surviving evidence at the time of writing, not a current condition check.",
          ["cand-8498"])
statement("novelli-description-foscarini", P260,205,205,"cand-1758","cand-1053",
          "novelli_described_foscarini_as_learned_patron_and_lover_of_arts",
          "In the passage Haskell attributes to Pietro Antonio Novelli, Foscarini is described as extremely learned and a great patron and lover of the fine arts.",
          "Nested recollection/quotation reported by Haskell; do not treat the quoted wording as independently verified testimony.",
          ["cand-1758","cand-1053"],marker=2,speaker="Pietro Antonio Novelli, as quoted by Haskell",text_layer="nested quotation")
statement("novelli-s-marco-kept-four-days", P260,205,205,"cand-1053","cand-8492",
          "kept_novelli_saint_mark_painting_in_room_for_four_days",
          "Novelli says Foscarini liked the Saint Mark painting made for engraver Marco Pitteri so much that he insisted on keeping it in his room for four days.",
          "Nested recollection reported by Haskell. The painting is unnamed and no ownership transfer is stated.",
          ["cand-1758","cand-1053","cand-1948","cand-8492"],marker=2,speaker="Pietro Antonio Novelli, as quoted by Haskell",text_layer="nested quotation")
statement("novelli-history-picture-request", P260,205,205,"cand-1053","cand-8493",
          "requested_history_picture_from_novelli",
          "Novelli says Foscarini then wanted a history picture from him.",
          "Nested recollection; the source does not name the subject or say that the requested picture was completed.",
          ["cand-1758","cand-1053","cand-8493"],marker=2,speaker="Pietro Antonio Novelli, as quoted by Haskell",text_layer="nested quotation")
statement("guarana-frescoes", P260,205,205,"cand-1237","cand-8494",
          "guarana_painted_frescoes_in_foscarini_palace",
          "Haskell says Giacomo Guarana, a follower of Tiepolo, painted frescoes in the palace.",
          "The palace is identified by context as the Foscarini family palace; no subjects, dates, or surviving condition are supplied.",
          ["cand-1237","cand-2569","cand-8494","cand-1059"],marker=3)
statement("nogari-portrait", P260,206,206,"cand-1743","cand-8495",
          "nogari_painted_foscarini_portrait",
          "Haskell names Giuseppe Nogari as the painter of Foscarini's portrait.",
          "No title, date, or location is supplied; distinct from Batoni's portrait candidate.",
          ["cand-1743","cand-1053","cand-8495"],marker=4)
statement("venetian-painters-limited-role", P260,207,207,"cand-1053","cand-8489",
          "leading_venetian_painters_little_part_in_foscarini_life",
          "Haskell says the great names of Venetian painting seem to have played little part in Foscarini's life, while his patronage impressed fellow citizens.",
          "Preserve 'do not seem' and Haskell's comparative assessment; no individual artist or quantified reception is inferred.",
          ["cand-1053","cand-8520"],marker=5)
statement("contemporary-rooms-description", P260,207,207,None,"cand-8491",
          "contemporary_described_rooms_as_venerable_sanctuary_of_writers_and_muses",
          "An unnamed contemporary describes Foscarini's rooms, portraits, and busts as a venerable sanctuary where famous writers and the Muses seemed at home.",
          "Quotation nested within Haskell's account; retain its rhetorical language and unnamed speaker.",
          ["cand-1053","cand-8519","cand-8491","cand-8499"],marker=6,
          speaker="Unnamed contemporary, as quoted by Haskell",text_layer="nested quotation",
          extras={"ocr_corrections":[{"source_line":207,"ocr":"lais rooms","print":"his rooms","basis":"CHP-9.pdf physical page 22."}]})
statement("first-half-patronage-moschini", P260,208,208,None,None,
          "artists_received_considerable_patronage_and_moschini_claimed_no_lack_of_support",
          "Haskell says some artists received considerable patronage in the first half of the eighteenth century and reports Moschini's claim that the arts had suffered from no lack of support.",
          "The passage reports Haskell's framing and Moschini's attributed claim; the claim is not independently tested here.",
          ["cand-1709"],marker=7)
statement("household-employment-general", P260,208,208,None,None,
          "families_employed_established_artists_as_household_members",
          "Haskell says other sources show families employing established artists as members of their households.",
          "General claim attributed to Haskell; specific examples and their source locators are handled separately.",
          ["cand-8500"],marker=8)
statement("pisani-private-academy", P260,208,208,"cand-8500","cand-8496",
          "pisani_organized_private_academy_with_longhi_in_charge",
          "Haskell says the Pisani organized a private academy with Pietro Longhi in charge.",
          "No academy name or location is supplied; the citation and examples are in the footnotes.",
          ["cand-8500","cand-8496","cand-1429"],marker=9,extras={"relation_candidate":True})
statement("academy-lessons-end", P260,208,208,"cand-8496","cand-1941",
          "academy_limited_to_drawing_lessons_and_ended_at_sons_death",
          "Haskell says the academy seems to have done little more than provide drawing lessons to the Pisani's son Almorò and ended with his death.",
          "Preserve 'seems' and the print reading Almorò; S0 OCR has Almord. No date or additional academy activity is supplied.",
          ["cand-8496","cand-1941"],marker=9,
          extras={"ocr_corrections":[{"source_line":208,"ocr":"Almord","print":"Almorò","basis":"CHP-9.pdf physical page 22."}]})
statement("narrower-patronage-scope", P260,209,209,"cand-1053",None,
          "venetian_patronage_more_restricted_than_it_first_appears",
          "Haskell argues that Venetian patronage was more restricted in nature and scope than it first appears, while acknowledging that the arts did receive Venetian support.",
          "Preserve Haskell's concession and contrast with Moschini's rebuttal; no general measure of support is inferred.",
          ["cand-1053","cand-1709","cand-2719"])
statement("patrician-glorification-ceiling-fresco", P260,209,209,"cand-8517","cand-8516",
          "patrician_self_glorification_concentrated_art_on_ceiling_fresco",
          "Haskell says patrician insistence on self-glorification led to a great concentration on ceiling frescoes.",
          "Authorial explanation and tendency, not an exclusive rule; the following sentence continues on p.261.",
          ["cand-8517","cand-8516"])

def note_statement(suffix, first, last, subject, obj, predicate, claim, qualification,
                   mentioned, marker, extras=None, segment_id=NOTES, speaker="Haskell's footnote"):
    statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=marker, speaker=speaker, text_layer="footnote citation", extras=extras)


note_statement("note1-arnaldi-and-de-brosses",395,395,None,"cand-8504",
               "citation_locators_for_foscarini_description",
               "Haskell's note 1 cites Lodovico Arnaldi's Orazione in lode di Marco Foscarini Doge di Venezia and De Brosses, volume II, page 39.",
               "Citation locators only; neither cited work/page was independently consulted.",
               ["cand-8503","cand-8504","cand-0455","cand-8505"],1)
note_statement("note2-novelli-page",396,396,None,"cand-8363",
               "citation_locator_novelli_page_16",
               "Haskell's note 2 cites Novelli, page 16, for the preceding recollection.",
               "The existing Novelli memoir candidate is reused; the cited page was not independently consulted.",
               ["cand-1758","cand-8363"],2)
note_statement("note3-moschini-1808",397,397,None,"cand-8506",
               "citation_locator_moschini_1808_page_139",
               "Haskell's note 3 cites G. A. Moschini, 1808, page 139.",
               "Citation locator only; title and cited page were not independently consulted.",
               ["cand-1709","cand-8506"],3)
note_statement("note4-gradenigo",398,398,None,"cand-8508",
               "citation_locator_gradenigo_page_91",
               "Haskell's note 4 cites Gradenigo, page 91.",
               "Citation locator only; author identity, work, and cited page remain unresolved/unread.",
               ["cand-8507","cand-8508"],4)
note_statement("note5-tiepolo-dedicated-prints",399,399,"cand-2569","cand-8497",
               "tiepolo_prints_of_oriental_heads_dedicated_to_foscarini",
               "Haskell's note 5 says prints taken from Tiepolo's drawings of Oriental heads were dedicated to Foscarini.",
               "The prints are not individually identified. The scan shows printed note marker 5; S0 OCR duplicates marker 6 at the start of this note.",
               ["cand-2569","cand-8497","cand-1053"],5,
               extras={"ocr_corrections":[{"source_file":"02-sources/02-Markdown/09_CHP-9_intro.md","source_line":399,"ocr":"6 Though","print":"5 Though","basis":"CHP-9.pdf physical page 22."}]},
               speaker="Haskell's footnote")
note_statement("note6-molino-orazione",400,400,"cand-8509","cand-8510",
               "citation_locator_molino_oration",
               "Haskell's note 6 cites Sebastiano Molino's Orazione in lode di Marco Foscarini Procurator di S. Marco.",
               "Citation locator only; the oration was not independently consulted.",
               ["cand-8509","cand-8510","cand-1053"],6)
note_statement("note7-moschini-volume-iii-page-49",401,401,None,"cand-8511",
               "citation_locator_moschini_1806_volume_iii_page_49",
               "Haskell's note 7 cites G. A. Moschini, 1806, volume III, page 49.",
               "Citation locator only; the cited page was not independently consulted.",
               ["cand-1709","cand-8511"],7)
statement("note8-zenobio-carlevarijs",VISUAL_ID,1,1,"cand-2870","cand-0554",
          "zenobio_employed_carlevarijs",
          "Haskell's note 8 gives the Zenobio employment of Carlevarijs as an example of established artists employed in households.",
          "S2 relationship candidate only; Mauroner page 15 is a locator and was not independently read.",
          ["cand-2870","cand-0554","cand-8512","cand-8513"],marker=8,
          speaker="Haskell's footnote",text_layer="footnote claim",
          extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":402,"source_line_end":402}]})
statement("note8-miani-baglione-list",VISUAL_ID,1,1,None,None,
          "miani_and_baglione_named_in_household_artist_examples",
          "Haskell's note 8 lists the Miani of Camerata and the Baglione of Polazzo, with an Alessandro Longhi citation, among household-employment examples.",
          "The note's compressed wording does not specify an individual member or assign a precise artist-family pairing; keep that mapping unresolved.",
          ["cand-8501","cand-8502","cand-1424"],marker=8,
          speaker="Haskell's footnote",text_layer="footnote claim",
          extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":402,"source_line_end":402}]})
statement("note8-zambelli-pittoni",VISUAL_ID,1,1,"cand-2832","cand-1950",
          "zambelli_employed_pittoni_late_in_his_life",
          "Haskell's note 8 names the Zambelli employment of Pittoni at the end of his life as a household-employment example.",
          "S2 relationship candidate only; no date or identified Zambelli family member is specified, and Moschini page 70 was not consulted.",
          ["cand-2832","cand-1950","cand-1709","cand-8511"],marker=8,
          speaker="Haskell's footnote",text_layer="footnote claim",
          extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":402,"source_line_end":402}]})
note_statement("note9-gallo-page-53",403,403,None,"cand-8515",
               "citation_locator_gallo_1945_page_53",
               "Haskell's note 9 cites Gallo, 1945, page 53, for the Pisani academy account.",
               "Citation locator only; the cited publication and page were not independently consulted.",
               ["cand-8514","cand-8515","cand-8496","cand-1429"],9)

all_candidate_ids = {r["candidate_id"] for r in candidates}
statement_ids = {r["statement_id"] for r in statements}
if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")
for row in new_statements:
    q = row["qualifiers"]
    refs = set(q.get("mentioned_candidate_ids", []))
    refs.update(x for x in [row.get("subject_candidate_id"), row.get("object_candidate_id")] if x)
    if not refs <= all_candidate_ids:
        raise SystemExit(f"statement foreign key error {row['statement_id']}: {refs-all_candidate_ids}")
    if row["original_quote"] != quote(row["segment_id"], q["source_line_start"], q["source_line_end"]):
        raise SystemExit(f"quote mismatch: {row['statement_id']}")

coverage_by_id[P259].update({
    "disposition":"reviewed","migration_status":"complete","source_line_ranges":"L189-200",
    "note":"Printed p.259 (CHP-9.pdf physical p.21) reviewed against scan. L200's unfinished 'other pictures' sentence is closed by p.260 L202-203. Notes 1-6 are migrated at consolidated L389-394; the Kress Foundation location statement remains discrepant with the Plate 45 caption and is preserved for later reconciliation."})
coverage_by_id[P260].update({
    "disposition":"reviewed","migration_status":"partial","source_line_ranges":"L202-210",
    "note":"Printed p.260 (CHP-9.pdf physical p.22) reviewed against scan. S0 line 202 says [Page 200], corrected in S2 metadata to printed p.260. L203 closes p.259 L200. L210 'We know too' begins an unfinished sentence continuing in p.261 L212; p.260 footnotes 1-9 are at consolidated L395-403, with note 8 also anchored by the full derived visual transcription."})
coverage_by_id[NOTES].update({
    "disposition":"reviewed","migration_status":"partial","source_line_ranges":"L349-403; p.255 L155 continuation",
    "note":"Consolidated p.258-260 notes through p.260 notes 1-9 have been migrated at L387-403; p.255 note 1 continuation at L155 remains cross-linked to L370. P.260 note 8 uses the full-page-image-derived visual segment as its canonical exact span, with no duplicate S2 rows from overlapping OCR L402. Later notes from L404 remain queued; citations are locators, not independent verification."})
coverage_by_id[VISUAL_ID] = {"chapter":"chp-9","segment_id":VISUAL_ID,"disposition":"reviewed","migration_status":"complete",
                             "source_line_ranges":"L1-1","note":"Derived transcription of the complete printed p.260 note 8 from CHP-9.pdf physical p.22. It restores the S0 OCR truncation after '(G. A.)' and gives the exact text anchor for the note; overlapping OCR L402 is not duplicated in S2 mentions/statements. Citation locators were not independently checked."}

summary = {"new_candidates":len(candidate_specs),"new_mentions":len(new_mentions),"new_statements":len(new_statements),
           "coverage":{sid:[coverage_by_id[sid]["disposition"],coverage_by_id[sid]["migration_status"],coverage_by_id[sid]["source_line_ranges"]] for sid in (P259,P260,NOTES,VISUAL_ID)},
           "next_body_segment":P261+"#L212-216 closes p.260 L210"}
print(json.dumps(summary,ensure_ascii=False,indent=2))
parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true",help="write the preflighted migration")
args=parser.parse_args()
if args.apply:
    paths=[candidate_path,mention_path,statement_path,coverage_path]
    backups=[p.with_name(p.name+BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for src,bak in zip(paths,backups):
        shutil.copy2(src,bak)
    try:
        write_csv(candidate_path,candidate_fields,candidates)
        write_csv(mention_path,mention_fields,mentions+new_mentions)
        write_jsonl(statement_path,statements+new_statements)
        write_csv(coverage_path,coverage_fields,list(coverage_by_id.values()))
    except Exception:
        for dst,bak in zip(paths,backups):
            shutil.copy2(bak,dst)
        raise
    print("APPLIED; recovery backups retained: "+", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
