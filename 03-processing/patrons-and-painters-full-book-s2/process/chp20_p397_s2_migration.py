#!/usr/bin/env python3
"""Controlled S2 migration for printed p.397 and closure of p.396's open quote."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
EXPECTED = {
    SOURCE: "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90",
    PDF: "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788",
}
P396 = "chp-20:20_CHP-20Postscript:l3-12"
P397 = "chp-20:20_CHP-20Postscript:l14-24"
P398 = "chp-20:20_CHP-20Postscript:l26-36"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
OPEN_396 = "st-chp20-p396-lavin-bernini-crossing-open"
CLOSE_397 = "st-chp20-p397-lavin-quote-closure"
BACKUP_SUFFIX = ".bak-s2-chp20-p397-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


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


for path, expected in EXPECTED.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)} ({actual})")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(x) for x in statement_path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
coverage_fields, coverage = read_csv(coverage_path)
segments = [json.loads(x) for x in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
segment_by_id = {r["segment_id"]: r for r in segments}
candidate_by_id = {r["candidate_id"]: r for r in candidates}
coverage_by_id = {r["segment_id"]: r for r in coverage}
statement_by_id = {r["statement_id"]: r for r in statements}

for sid in (P396, P397, P398, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if (coverage_by_id[P396]["disposition"], coverage_by_id[P396]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"p.396 must be reviewed/partial before closure: {coverage_by_id[P396]}")
if (coverage_by_id[P397]["disposition"], coverage_by_id[P397]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.397 should be queued/pending: {coverage_by_id[P397]}")
if segment_by_id[P397]["sha256"] != "201c57b2a02bdec4aa20893568ecc58d42cdd22877f13fbfd89df1512e3bab0e":
    raise SystemExit("registered p.397 S0 hash changed")
if segment_by_id[P397]["asset_sha256"] != EXPECTED[SOURCE]:
    raise SystemExit("p.397 source asset hash is inconsistent")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text397 = "\n".join(source_lines[segment_by_id[P397]["line_start"] - 1 : segment_by_id[P397]["line_end"]])
if hashlib.sha256(text397.encode("utf-8")).hexdigest() != segment_by_id[P397]["sha256"]:
    raise SystemExit("p.397 S0 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P397]["line_start"], segment_by_id[P397]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1


def quote(first, last):
    return "\n".join(source_lines[first - 1 : last])


candidate_specs = [
    ("cand-10864", "Tapestries given by the French to Cardinal Francesco Barberini (group unspecified)", "work", 16,
     "The postscript identifies a group given by the French and says David Dubon described them; no count or individual titles are supplied."),
    ("cand-10865", "David Dubon", "person", 16, "Named as the author who described tapestries given to Cardinal Francesco Barberini."),
    ("cand-10866", "David Dubon’s publication describing the French tapestries given to Cardinal Francesco Barberini (title unspecified)", "archive", 16,
     "The publication is cited by Haskell but is not titled in this passage and was not independently consulted."),
    ("cand-10867", "Don Urbano Barberini", "person", 16,
     "The page image reads Don Urbano Barberini; the规范 OCR inserts a stray quotation mark before the surname."),
    ("cand-10868", "Don Urbano Barberini’s article on tapestries celebrating Urban VIII’s papacy (title unspecified)", "archive", 16,
     "Haskell says this article replaces previous literature and changes some attributions repeated in the first edition; title and specific attributions are not given here."),
    ("cand-10869", "Ann Sutherland Harris", "person", 18, "Named as the author of a monograph on Andrea Sacchi."),
    ("cand-10870", "Ann Sutherland Harris’s monograph on Andrea Sacchi (title unspecified)", "archive", 18,
     "Haskell says the monograph modifies his statements about the Palazzo Barberini ceiling and interprets its iconography; it was not independently consulted."),
    ("cand-10871", "Poirier (scholar cited in the second-edition postscript; identity unresolved)", "person", 20,
     "The source supplies only the surname and says Poirier reaffirmed a qualification about the classical/baroque debate."),
    ("cand-10872", "Poirier’s publication on the classical/baroque debate (title unspecified)", "archive", 20,
     "Citation is supplied only by surname in the page footnote; title and edition remain for bibliography review."),
    ("cand-10873", "Garas, 1967 publication of an inventory of Cardinal Ludovico’s pictures (title unspecified)", "archive", 21,
     "Haskell says Garas published the inventory; the cited publication was not consulted. Keep distinct from the existing Garas 1962 citation candidate."),
    ("cand-10874", "Heikamp (scholar cited in the second-edition postscript; identity unresolved)", "person", 21,
     "The postscript supplies only the surname and year 1966 in this passage."),
    ("cand-10875", "Heikamp, 1966 study of Cardinal Del Monte and the Tuscan court (title unspecified)", "archive", 21,
     "Haskell says the study used published and unpublished sources; it was not independently consulted."),
    ("cand-10876", "Tuscan court mentioned in Heikamp’s study (specific body unresolved)", "institution", 21,
     "The postscript names a court but does not identify the ruler, government, or institutional scope involved."),
    ("cand-10877", "Christoph Frommel", "person", 21, "Named as the publisher of important inventories of Cardinal Del Monte’s collection."),
    ("cand-10878", "Christoph Frommel’s publication of Cardinal Del Monte collection inventories and Caravaggio inquiry (title unspecified)", "archive", 21,
     "Haskell associates the inventories with an inquiry into the Cardinal’s influence on Caravaggio; exact title and cited pages are not supplied here."),
    ("cand-10879", "W. Chandler Kirwin", "person", 22, "Named as another scholar who published important inventories of Del Monte’s collection."),
    ("cand-10880", "W. Chandler Kirwin’s publication of Cardinal Del Monte collection inventories (title unspecified)", "archive", 22,
     "The postscript provides the author name but no title; publication was not independently consulted."),
    ("cand-10881", "Luigi Spezzaferro", "person", 22, "Named as a scholar of Cardinal Del Monte’s patronage and cultural formation."),
    ("cand-10882", "Luigi Spezzaferro’s study of Del Monte’s cultural formation and Caravaggio patronage (title unspecified)", "archive", 22,
     "Haskell says the study stresses Del Monte’s interest in scientific investigation; the publication was not independently consulted."),
    ("cand-10883", "Posner (scholar cited in the second-edition postscript; identity unresolved)", "person", 22,
     "The source supplies only the surname; no given name is inferred."),
    ("cand-10884", "Posner’s study of Del Monte and the early works of Caravaggio (title unspecified)", "archive", 22,
     "Haskell attributes an interpretive argument to Posner; title and edition are not given in this passage."),
    ("cand-10885", "Hibbard, 1973 publication discussing Lavin and recent Borromini literature (title unspecified)", "archive", 15,
     "The p.397 footnote identifies Hibbard, 1973; this is distinct from the p.396 Hibbard 1971 Maderno monograph candidate."),
    ("cand-10886", "Garas’s inventory of Cardinal Ludovico’s pictures dating from 1633 (publication locator unspecified)", "archive", 21,
     "A historical inventory of pictures, reported by Haskell as published by Garas; the inventory and its publication were not consulted."),
    ("cand-10887", "Cardinal Del Monte’s picture collection covered by later inventories (extent/type unresolved)", "", 21,
     "The postscript refers to inventories of his collection but does not define its boundaries, location, or exact contents."),
    ("cand-10888", "Andrea Sacchi’s ceiling in Palazzo Barberini (work identity/title unspecified)", "work", 18,
     "Haskell discusses his earlier comments on the ceiling’s style and iconography; Harris’s monograph supplies a different interpretation."),
    ("cand-10889", "French donor collective for tapestries given to Cardinal Francesco Barberini (identity unresolved)", "institution", 16,
     "The source says ‘the French’ but names no ruler, government, or individual donors; do not equate the group with France as a place."),
    ("cand-10890", "Unidentified early works of Caravaggio discussed by Posner (individual works unspecified)", "work", 22,
     "Posner’s interpretation concerns Caravaggio’s early works generally; no individual work is identified, and the group is not equated with other Del Monte-related canvases."),
]
existing_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
for cid, name, kind, line_number, detail in candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P397}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-10861", "the crossing", 15, 15, "Lavin’s quote continuation describes this interior space; closes p.396.", 0),
    ("cand-3806", "Hibbard", 15, 15, "Reuse the existing Howard Hibbard candidate.", 0),
    ("cand-10860", "Lavin’s book", 15, 15, "The p.396 candidate study is referenced in Hibbard’s discussion.", 0),
    ("cand-0404", "Borromini", 15, 15, "Recent literature on Borromini is cited as qualifying the baldacchino attribution.", 0),
    ("cand-4234", "thebaldacchino", 15, 15, "Raw OCR; the page image reads ‘the baldacchino’.", 0),
    ("cand-0295", "Bernini", 15, 15, "Haskell says his straightforward attribution needs qualification.", 0),
    ("cand-0198", "Barberini patrons", 15, 15, "Collective patronage attribution remains qualified.", 0),
    ("cand-0199", "Cardinal Francesco Barberini", 16, 16, "Reuse the indexed person candidate.", 0),
    ("cand-10864", "tapestries given to Cardinal Francesco Barberini by the French", 16, 16, "Work group; no count or individual tapestry is identified.", 0),
    ("cand-10889", "the French", 16, 16, "Collective donor reference; no state or individual is named.", 0),
    ("cand-10865", "David Dubon", 16, 16, "Named as author of the description.", 0),
    ("cand-10866", "fully described by David Dubon", 16, 16, "Cited publication is not titled here.", 0),
    ("cand-4935", "those that were woven much later to celebrate the papacy of Urban VIII", 16, 16, "Reuse the existing Urban VIII tapestry group; this passage does not restate its count.", 0),
    ("cand-0209", "Urban VIII", 16, 16, "Reuse the Maffeo Barberini/Pope Urban VIII candidate.", 0),
    ("cand-10867", "Don Urbano \"Barberini", 16, 16, "Raw OCR includes a stray quote; the page image reads Don Urbano Barberini.", 0),
    ("cand-10868", "article by Don Urbano \"Barberini", 16, 16, "The cited article replaces earlier literature and changes some attributions; title unspecified.", 0),
    ("cand-0187", "Cardinal Antonio Barberini", 17, 17, "Reuse the nephew-to-Urban-VIII candidate.", 0),
    ("cand-2318", "Sacchi", 17, 17, "Andrea Sacchi candidate from the index.", 0),
    ("cand-10869", "Ann Sutherland Harris", 18, 18, "Named as the author of Sacchi’s monograph.", 0),
    ("cand-10870", "Her monograph on the artist", 18, 18, "Harris’s monograph; source not independently consulted.", 0),
    ("cand-2318", "the artist", 18, 18, "Anaphoric reference to Andrea Sacchi.", 0),
    ("cand-10888", "his ceiling", 18, 18, "Sacchi’s ceiling in Palazzo Barberini; identity remains unspecified.", 0),
    ("cand-4957", "Palazzo Barberini", 18, 18, "Reuse the place candidate for the palace.", 0),
    ("cand-1810", "Sforza\nPallavicino", 18, 19, "Name crosses an OCR line break; Haskell reports only Harris’s suggested possible inspiration.", 0),
    ("cand-4490", "Rome", 20, 20, "Place in Haskell’s account of mid-century artistic categories.", 0),
    ("cand-10871", "Poirier", 20, 20, "Surname-only scholar reference.", 0),
    ("cand-4348", "the Ludovisi", 21, 21, "Reuse the collective family candidate.", 0),
    ("cand-9342", "Garas", 21, 21, "Reuse surname-only candidate; do not resolve identity from this passage.", 0),
    ("cand-10886", "inventory of Cardinal Ludovico’s pictures", 21, 21, "Inventory publication cited as dating from 1633; preserve OCR superscript correction.", 0),
    ("cand-1456", "Cardinal Ludovico", 21, 21, "Reuse the indexed Ludovico Ludovisi candidate.", 0),
    ("cand-1691", "Cardinal Del Monte", 21, 21, "Reuse the indexed Francesco Maria del Monte candidate.", 0),
    ("cand-10874", "Heikamp", 21, 21, "Surname-only source mention.", 0),
    ("cand-10875", "investigated his relations with the Tuscan court", 21, 21, "Heikamp’s 1966 study; the court’s identity remains unresolved.", 0),
    ("cand-10876", "the Tuscan court", 21, 21, "Specific court and political scope are not named.", 0),
    ("cand-10877", "Christoph Frommel", 21, 21, "Named as a publisher of the inventories.", 0),
    ("cand-10878", "important inventories of his collection", 21, 21, "Del Monte collection records; collection extent is unresolved.", 0),
    ("cand-10887", "his collection", 21, 21, "Anaphoric reference to Cardinal Del Monte’s collection.", 0),
    ("cand-10878", "the Cardinal’s influence on Caravaggio", 21, 21, "Frommel’s inquiry; this does not settle the nature or extent of influence.", 0),
    ("cand-0544", "Caravaggio", 21, 21, "Caravaggio named as the subject of Frommel’s inquiry.", 0),
    ("cand-10879", "W. Chandler Kirwin", 22, 22, "Named as another publisher of inventories.", 0),
    ("cand-10881", "Luigi Spezzaferro", 22, 22, "Named as a scholar of Del Monte.", 0),
    ("cand-1691", "the Cardinal’s patronage", 22, 22, "Anaphoric reference to Cardinal Del Monte.", 0),
    ("cand-0544", "young Caravaggio", 22, 22, "The patronage reference is Haskell’s account of Spezzaferro’s approach.", 0),
    ("cand-10883", "Posner", 22, 22, "Surname-only scholar reference.", 0),
    ("cand-10884", "following up a suggestion made in the first edition of this book", 22, 22, "Posner’s cited study; title is not given here.", 0),
    ("cand-10890", "Caravaggio’s early works", 22, 22, "Unidentified group; no individual artwork is named.", 0),
    ("cand-1691", "the Cardinal", 22, 22, "Anaphoric reference to Cardinal Del Monte.", 0),
    ("cand-0018", "Giambattista Agucchi", 24, 24, "Reuse the indexed person candidate; the sentence continues beyond this segment.", 0),
]

new_mentions = []
mention_ids = {r["mention_id"] for r in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mid = f"m-chp20-p397-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or closed: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text397.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on p.397 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mid, "segment_id": P397, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    mention_ids.add(mid)

intervals = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"])
                   for r in [*mentions, *new_mentions] if r["segment_id"] == P397)
for index, left in enumerate(intervals):
    for right in intervals[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing p.397 mention spans: {left[2]} / {right[2]}")


def make_statement(sid, first, last, subject, obj, predicate, claim, speaker, layer, qualification,
                   candidate_ids, relation=False, extra=None):
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": 397, "pdf_physical_page": 2,
        "claim": claim, "speaker": speaker,
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation,
        "cited_material_not_independently_consulted": True,
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid, "segment_id": P397,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(first, last),
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement(CLOSE_397, 15, 15, "cand-10859", "cand-10861",
        "lavin_described_the_crossing_as_an_unplanned_evolutionary_process",
        "The continuation of Lavin’s quotation says the crossing’s transformation took place over a considerable period and was never fully realised; it says there is no evidence that every detail was worked out in advance as a general scheme.",
        "Irving Lavin, quoted by Haskell", "quoted architectural interpretation",
        "This closes the quotation opened in p.396 statement st-chp20-p396-lavin-bernini-crossing-open. Lavin’s publication was not independently consulted.",
        ["cand-10859", "cand-10860", "cand-10861"], relation=False,
        extra={"cross_reference_segments": [P396], "closes_statement_ids": [OPEN_396]}),
    make_statement("st-chp20-p397-hibbard-qualifies-baldacchino-attribution", 15, 15, None, "cand-4234",
        "hibbard_discussion_and_borromini_literature_require_qualification_of_baldacchino_attribution",
        "Haskell says Hibbard’s discussion of Lavin’s book and recent literature on Borromini show that his straightforward attribution of the baldacchino to Bernini and his Barberini patrons needs qualification.",
        "Haskell assessing later scholarship", "authorial revision of an earlier attribution",
        "This is a qualification, not a new attribution decision. The Hibbard 1973 publication and cited literature were not read here.",
        ["cand-3806", "cand-10860", "cand-0404", "cand-10885", "cand-4234", "cand-0295", "cand-0198"], relation=True,
        extra={"cross_reference_segments": [NOTES], "ocr_corrections": [{"source_line": 15, "ocr": "thebaldacchino", "print": "the baldacchino", "basis": "CHP-20Postscript.pdf physical page 2"}]}),
    make_statement("st-chp20-p397-french-tapestries-dubon", 16, 16, None, "cand-10864",
        "french_tapestries_given_to_francesco_barberini_were_described_by_dubon",
        "Haskell says tapestries given by the French to Cardinal Francesco Barberini were fully described by David Dubon.",
        "Haskell reporting later scholarship", "scholarly description of a group of tapestries",
        "The passage gives no count, individual subjects, donor identity, or title for Dubon’s publication; neither the tapestries nor the publication were independently consulted.",
        ["cand-10864", "cand-0199", "cand-10889", "cand-10865", "cand-10866"], relation=True,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-urban-viii-tapestries-don-urbano", 16, 16, None, "cand-4935",
        "don_urbano_barberini_article_revised_attributions_of_urban_viii_tapestries",
        "Haskell says later tapestries woven to celebrate Urban VIII’s papacy were discussed in an article by Don Urbano Barberini, which replaced previous literature and altered some attributions repeated in the first edition.",
        "Haskell assessing later scholarship", "authorial report of revised art-historical attribution",
        "The source does not specify which attributions changed. Reuse the existing Urban VIII tapestry candidate without restating a count; the cited article was not consulted.",
        ["cand-4935", "cand-0209", "cand-10867", "cand-10868"], relation=True,
        extra={"cross_reference_segments": [NOTES], "ocr_corrections": [{"source_line": 16, "ocr": "Don Urbano \"Barberini", "print": "Don Urbano Barberini", "basis": "CHP-20Postscript.pdf physical page 2"}]}),
    make_statement("st-chp20-p397-harris-sacchi-palazzo-ceiling", 17, 18, None, "cand-10870",
        "harris_monograph_revised_haskells_assessment_of_sacchi_and_palazzo_barberini_ceiling",
        "Haskell says Cardinal Antonio Barberini’s patronage of Sacchi has been fully discussed by Ann Sutherland Harris. Her monograph modifies Haskell’s statements about the style of Sacchi’s Palazzo Barberini ceiling, while he retains only half-hearted praise, and offers a balanced interpretation of its iconography; Harris suggests Sforza Pallavicino could have inspired it.",
        "Haskell assessing Harris’s scholarship", "qualified art-historical interpretation",
        "Harris’s proposed inspiration is explicitly a suggestion, not a documented commission or proven source. Her monograph and the ceiling were not independently consulted.",
        ["cand-0187", "cand-2318", "cand-10869", "cand-10870", "cand-10888", "cand-4957", "cand-1810"], relation=True,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-classical-baroque-debate-poirier", 20, 20, None, "cand-10872",
        "poirier_reaffirmed_the_classical_baroque_debate_was_not_about_colour_and_drawing",
        "Haskell says Harris qualifies a traditional sharp division between classical and baroque artists in mid-century Rome, and Poirier reaffirmed that the so-called debate was not, as sometimes claimed, about the merits of colour and drawing.",
        "Haskell reporting Harris and Poirier", "historiographical interpretation",
        "This records Haskell’s account of two scholars’ arguments; it is not an independent conclusion about the debate. Neither cited publication was read here.",
        ["cand-10869", "cand-10871", "cand-10872", "cand-4490"], relation=False,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-ludovisi-garas-inventory", 21, 21, None, "cand-10886",
        "garas_published_inventory_of_cardinal_ludovicos_pictures_dating_from_1633",
        "Haskell says the Ludovisi have been discussed by Garas, who published an inventory of Cardinal Ludovico’s pictures dating from 1633.",
        "Haskell reporting published scholarship", "source-reported inventory publication",
        "The inventory and Garas’s publication were not consulted. The OCR’s ‘16335’ combines the printed year 1633 with superscript footnote 7.",
        ["cand-4348", "cand-9342", "cand-10873", "cand-10886", "cand-1456"], relation=True,
        extra={"cross_reference_segments": [NOTES], "ocr_corrections": [{"source_line": 21, "ocr": "16335", "print": "1633" , "basis": "CHP-20Postscript.pdf physical page 2; superscript 7 is footnote marker"}]}),
    make_statement("st-chp20-p397-del-monte-recent-attention", 21, 21, None, "cand-1691",
        "del_monte_received_the_most_attention_from_recent_writers",
        "Haskell says Cardinal Del Monte had received by far the most attention from recent writers among the patrons other than the Barberini discussed in the chapter.",
        "Haskell’s assessment of recent literature", "authorial summary",
        "This is Haskell’s characterization of the literature, not a quantitative survey independently checked here.",
        ["cand-1691", "cand-0198"], relation=False),
    make_statement("st-chp20-p397-heikamp-del-monte-tuscan-court", 21, 21, None, "cand-10875",
        "heikamp_1966_study_used_sources_to_examine_del_monte_and_tuscan_court_relations",
        "Haskell says Heikamp’s 1966 study investigated Del Monte’s relations with the Tuscan court and used published and unpublished sources to illustrate the range and depth of his artistic tastes.",
        "Haskell reporting later scholarship", "source-reported research scope",
        "The specific Tuscan court and sources are not identified in this passage; Heikamp’s study was not independently consulted.",
        ["cand-10874", "cand-10875", "cand-10876", "cand-1691"], relation=True,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-frommel-del-monte-inventories", 21, 21, None, "cand-10878",
        "frommel_published_del_monte_collection_inventories_in_an_inquiry_on_caravaggio",
        "Haskell says that five years after Heikamp, important inventories of Del Monte’s collection were published by Christoph Frommel during an inquiry into the nature of the Cardinal’s influence on Caravaggio.",
        "Haskell reporting later scholarship", "source-reported publication and research context",
        "The inventories and Frommel’s inquiry are not independently checked; no specific picture or causal influence is established.",
        ["cand-10877", "cand-10878", "cand-10887", "cand-1691", "cand-0544"], relation=True,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-kirwin-del-monte-inventories", 21, 22, None, "cand-10880",
        "kirwin_also_published_del_monte_collection_inventories",
        "Haskell says W. Chandler Kirwin also published important inventories of Del Monte’s collection.",
        "Haskell reporting later scholarship", "source-reported inventory publication",
        "The publication title and exact relationship between the sets of inventories are not stated; the publication was not consulted.",
        ["cand-10879", "cand-10880", "cand-10887", "cand-1691"], relation=True,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-spezzaferro-del-monte-caravaggio", 22, 22, None, "cand-10882",
        "spezzaferro_examined_del_montes_cultural_formation_and_scientific_interests",
        "Haskell says Luigi Spezzaferro, emphasizing Del Monte’s patronage of the young Caravaggio, examined the Cardinal’s cultural formation in detail and stressed his interest in scientific investigation.",
        "Haskell reporting later scholarship", "source-reported interpretation",
        "This describes Haskell’s reading of Spezzaferro, not independent evidence of a patronage relationship or a complete account of Del Monte’s interests.",
        ["cand-10881", "cand-10882", "cand-1691", "cand-0544"], relation=True,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-posner-caravaggio-early-works", 22, 22, None, "cand-10884",
        "posner_interpreted_del_monte_circle_as_encouraging_homoerotic_character_in_caravaggios_early_works",
        "Haskell says Posner, following a suggestion in the first edition, drew attention to the ‘homo-erotic’ nature of Caravaggio’s early works, which was probably encouraged by Cardinal Del Monte and members of his circle.",
        "Haskell reporting Posner’s interpretation", "qualified interpretation of artworks and patronal influence",
        "‘Probably’ is preserved: this is an attributed interpretation, not proof about individual works or the Cardinal’s circle. No members or specific paintings are identified.",
        ["cand-10883", "cand-10884", "cand-10890", "cand-0544", "cand-1691"], relation=True,
        extra={"cross_reference_segments": [NOTES]}),
    make_statement("st-chp20-p397-agucchi-career-open", 23, 24, "cand-0018", None,
        "haskell_opened_a_qualified_update_on_agucchis_early_career",
        "Haskell introduces Giambattista Agucchi as another patron whose early career has been much illuminated in recent years, adding that readers may only feel they know it; the sentence continues beyond this segment.",
        "Haskell", "authorial transition with explicit uncertainty",
        "The wording ‘probably know (or feel we know)’ is not a settled conclusion. The continuation is on p.398 and remains open.",
        ["cand-0018"], relation=False,
        extra={"cross_reference_segments": [P398], "open_across_segment": True}),
]

if OPEN_396 not in statement_by_id:
    raise SystemExit(f"missing open p.396 statement: {OPEN_396}")
open_statement = statement_by_id[OPEN_396]
open_qualifiers = open_statement.get("qualifiers", {})
if not open_qualifiers.get("open_across_segment"):
    raise SystemExit("p.396 Lavin quotation is not marked open")
if CLOSE_397 in statement_by_id:
    raise SystemExit(f"closure statement already exists: {CLOSE_397}")

existing_statement_ids = {r["statement_id"] for r in statements}
for row in new_statements:
    sid = row["statement_id"]
    if sid in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {sid}")
    existing_statement_ids.add(sid)
    if row["original_quote"] not in text397:
        raise SystemExit(f"statement quote not contained in p.397 segment: {sid}")
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {cid}")
    for ref_id in row["qualifiers"].get("cross_reference_segments", []):
        if ref_id not in segment_by_id:
            raise SystemExit(f"statement references missing segment {ref_id}")

open_qualifiers["open_across_segment"] = False
open_qualifiers["closed_by_segment"] = P397
open_qualifiers["closed_by_statement_id"] = CLOSE_397
open_qualifiers["cross_page_quote_continuation"] = (
    "evolutionary process that took place over a considerable period and that was never fully realised. "
    "There is no evidence to suppose that all the details of the crossing were worked out in advance as a general scheme"
)
open_qualifiers["qualification"] = (
    "The p.396 sentence and its quoted passage are now closed by the text on p.397, which says the crossing evolved over time, "
    "was never fully realised, and was not shown to have been planned in full in advance. Lavin’s publication was not independently consulted."
)
open_statement["predicate"] = "lavin_analysis_of_bernini_st_peters_crossing_confirms_haskells_impression_closed"
mentions.extend(new_mentions)
statements.extend(new_statements)

coverage_by_id[P396]["migration_status"] = "complete"
coverage_by_id[P396]["note"] = coverage_by_id[P396]["note"] + " The cross-page Lavin quotation was closed against p.397 statement `" + CLOSE_397 + "`."
coverage_by_id[P397]["disposition"] = "reviewed"
coverage_by_id[P397]["migration_status"] = "partial"
coverage_by_id[P397]["source_line_ranges"] = "L15-24"
coverage_by_id[P397]["note"] = (
    "Printed p.397 (PDF physical page 2) read against the page image. Closes p.396’s Lavin quotation; processes Hibbard’s "
    "qualification of the baldacchino attribution, tapestry scholarship, Harris/Sacchi, the classical/baroque debate, "
    "Ludovisi and Del Monte research, and the opening on Agucchi. The Agucchi sentence continues on p.398, so this segment remains partial. "
    "Page-image corrections are recorded on statements; cited publications were not independently consulted."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.397 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print(f"closed p.396 statement {OPEN_396} using {CLOSE_397}")
    print("p.397 remains partial because the Agucchi sentence continues on p.398")
