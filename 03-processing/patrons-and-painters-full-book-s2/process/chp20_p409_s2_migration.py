#!/usr/bin/env python3
"""Controlled S2 migration for printed p.409 (PDF physical p.18)."""
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
P408 = "chp-20:20_CHP-20Postscript:l174-185"
P409 = "chp-20:20_CHP-20Postscript:l187-199"
P410 = "chp-20:20_CHP-20Postscript:l201-209"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP = ".bak-s2-chp20-p409-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
ARGS = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows); temp = Path(handle.name)
    temp.replace(path)

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)

if sha(SOURCE.read_bytes()) != SOURCE_SHA or sha(PDF.read_bytes()) != PDF_SHA:
    raise SystemExit("source or PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(source_lines[186:199])
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
if P409 not in segment_by_id or sha(body.encode("utf-8")) != segment_by_id[P409]["sha256"]:
    raise SystemExit("p.409 S0 segment hash mismatch")
if segment_by_id[P409]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.409 source registration changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
for segment_id in (P408, P409, P410, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing segment: {segment_id}")
if (coverage_by_id[P408]["disposition"], coverage_by_id[P408]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.408 must remain partial until p.409 closes its sentence")
if (coverage_by_id[P409]["disposition"], coverage_by_id[P409]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.409 is not queued/pending")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("postscript notes must remain queued")

# Add only page-specific people, works, institutions, places, and described publications.
candidate_specs = [
    ("cand-11125", "Giovanni da Pozzo", "person", "Full name as printed; align identity during S3.", 191),
    ("cand-11126", "Giovanni da Pozzo's critical edition of Francesco Algarotti's essays", "archive", "The body describes a critical edition with bibliographical commentary; footnote 2 and bibliography reconciliation remain pending.", 191),
    ("cand-11127", "Giovanni da Pozzo's publication of the full text of Algarotti's will", "archive", "Publication of the will text, distinct from the 1764 will itself (existing candidate cand-10333); footnote 3 and bibliography reconciliation remain pending.", 191),
    ("cand-11128", "Posthumous catalogue of Francesco Algarotti's collection compiled twelve years after his death", "archive", "The catalogue is unnamed; Haskell uses its omission of the two Tiepolo subjects to explain the will evidence.", 193),
    ("cand-11129", "Tiepolo's Road to Calvary sketch reported in Berlin", "work", "Haskell says it is almost certainly a sketch for the larger S. Alvise painting; keep the identification probabilistic.", 193),
    ("cand-11130", "Large Tiepolo painting of Christ led to Calvary for S. Alvise, Venice", "work", "The church painting is the proposed destination work for the Berlin sketch; retain the relationship as Haskell's near-certain identification.", 193),
    ("cand-11131", "Church of S. Alvise in Venice", "place", "Church named as the location of the large Tiepolo painting; separate the building from its painting.", 193),
    ("cand-11132", "Unidentified Tiepolo sketch of the Banquet of Mark Antony and Cleopatra (Plate 61a)", "work", "Haskell says this may be the sketch in Paris's Musée Cognacq-Jay, while explicitly noting difficulties with the identification; keep distinct from Plate 61b and other Tiepolo Banquet versions.", 194),
    ("cand-11133", "Musée Cognacq-Jay", "institution", "Institution named as the possible location of the Plate 61a sketch.", 194),
    ("cand-11134", "Maria Santifaller", "person", "Full name as printed; align identity during S3.", 195),
    ("cand-11135", "Georg Friedrich Schmidt's classicising print portrait of Francesco Algarotti (Berlin, 1752)", "work", "Haskell reports this print as the source for the vast majority of Algarotti portraits discussed by Santifaller.", 197),
    ("cand-11136", "Georg Friedrich Schmidt's etching of Felice Salimbeni for Algarotti (1753)", "work", "The print is dated one year after the 1752 portrait; the source describes Salimbeni's features, not a sitter identity beyond the singer's name.", 197),
    ("cand-11137", "Maria Santifaller's 1976 article on portraits of Francesco Algarotti", "archive", "Article title is not stated; footnote 6 cites Santifaller 1976 and bibliography reconciliation remains pending.", 196),
    ("cand-11138", "Francesco Algarotti's etchings, sometimes made in collaboration with Tiepolo", "work", "A body-level group reference; do not enumerate or identify individual etchings beyond the separate known candidates.", 197),
    ("cand-11139", "Maria Santifaller's 1977 article on etchings by Algarotti", "archive", "Article title is not stated; footnote 7 cites Santifaller 1977 and bibliography reconciliation remains pending.", 197),
    ("cand-11140", "Michael Levey's 1978 article on the Tiepolo portrait theory", "archive", "The article is described but untitled; footnote 8 cites Levey 1978. Reconcile with bibliography and earlier portrait evidence.", 198),
    ("cand-11141", "Painting of Francesco Algarotti's tomb in Campo Santo, Pisa", "work", "Haskell reports its likely derivation from a Volpato engraving and changing locations; p.409's attribution discussion continues on p.410.", 199),
    ("cand-11142", "Giovanni Volpato engraving probably used as source for Algarotti's tomb painting", "work", "The derivation is explicitly probable, not certain.", 199),
    ("cand-11143", "John Bryson", "person", "Name attached to the collection that held the tomb painting in 1963; identity alignment remains for S3.", 199),
    ("cand-11144", "Oxford as the location of the John Bryson collection", "place", "The collection is located in Oxford in Haskell's 1963 account; no more precise institution is named.", 199),
    ("cand-11145", "Schloss Charlottenburg in Berlin", "place", "Named as the painting's later location; align with any authoritative institution/place record during S3/S5.", 199),
    ("cand-11146", "Maria Santifaller's 1978 article on Algarotti's tomb painting", "archive", "Article title is not stated; footnote 9 cites Santifaller 1978 and bibliography reconciliation remains pending.", 199),
]
natural_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID exists: {candidate_id}")
    key = (name.strip().casefold(), kind.casefold())
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {name}")
    row = {"candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
           "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
           "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
           "candidate_source_ref": f"{P409}#L{line_number}"}
    candidates.append(row); candidate_by_id[candidate_id] = row; natural_keys.add(key)

# Candidate ID, exact S0 surface, first line, last line, occurrence, note.
mention_specs = [
    ("cand-11124", "‘portraits’—in the form of medallions—of all the Doges", 188, 188, 0, "Continuation describes the contents of Matina's volume and publication date 1659."),
    ("cand-3401", "Venice", 188, 188, 0, "Reuse the Venice place candidate."),
    ("cand-10042", "Maggiotto’s paintings", 188, 188, 0, "Reuse the Pinelli Doge portrait series."),
    ("cand-0041", "Algarotti", 190, 190, 0, "Reuse Francesco Algarotti."),
    ("cand-11126", "a critical edition of the essays", 191, 191, 0, "Da Pozzo's edition with bibliographical commentary."),
    ("cand-11125", "Giovanni da Pozzo", 191, 191, 0, "Full author name."),
    ("cand-11127", "the full text of his will", 191, 191, 0, "Publication of the will text; the will artifact is cand-10333."),
    ("cand-10333", "his will", 191, 191, 0, "Reuse the 1764 will candidate; possessive refers to Algarotti."),
    ("cand-0919", "Diderot", 191, 191, 0, "Reuse Denis Diderot; Haskell characterizes his response as sarcastic amusement."),
    ("cand-1947", "the Elder Pitt", 192, 192, 0, "Reuse William Pitt the Elder."),
    ("cand-2551", "Mauro Tesi", 192, 192, 0, "Reuse the indexed Mauro Tesi candidate."),
    ("cand-0041", "Algarotti", 192, 192, 0, "Reuse Francesco Algarotti in the second bequest."),
    ("cand-1543", "Cosimo Mari", 192, 192, 0, "Reuse the indexed Cosimo Mari candidate."),
    ("cand-2569", "Tiepolo", 192, 192, 0, "Reuse Giambattista Tiepolo."),
    ("cand-11129", "Cristo condotto al Calvario", 192, 192, 0, "Original Italian subject title in the will as printed by Haskell."),
    ("cand-11132", "un convitto di Marco Antonio e Cleopatra", 192, 192, 0, "Original Italian subject title; keep distinct from other Banquet versions."),
    ("cand-10314", "Pictures by Tiepolo of these subjects", 192, 192, 0, "Reuse the broader Tiepolo-in-Algarotti-collection group; do not merge individual works."),
    ("cand-11128", "the catalogue of his collection", 193, 193, 0, "Posthumous catalogue compiled twelve years after Algarotti's death."),
    ("cand-0041", "Algarotti", 193, 193, 0, "Reuse Francesco Algarotti."),
    ("cand-11129", "The Road to Calvary", 193, 193, 0, "The identified sketch is only 'almost certainly' in Berlin."),
    ("cand-4623", "Berlin", 193, 193, 0, "Reuse an existing Berlin place candidate."),
    ("cand-11130", "the large painting", 193, 193, 0, "Anaphoric reference to the painting in S. Alvise."),
    ("cand-11131", "the church of S. Alvise", 193, 193, 0, "Church building is a location, distinct from the painting."),
    ("cand-3401", "Venice", 193, 193, 0, "Reuse Venice place candidate."),
    ("cand-11132", "The banquet of Mark Anthony and Cleopatra", 193, 193, 0, "Haskell's English title for the second Tiepolo subject."),
    ("cand-11133", "Musée Cognacq-Jay", 194, 194, 0, "Possible Paris location; retain Haskell's uncertainty."),
    ("cand-4653", "Paris", 194, 194, 0, "Reuse the Paris place candidate."),
    ("cand-11132", "Plate 61a", 194, 194, 0, "Plate reference for the possible Cognacq-Jay sketch; not the Plate 61b Banquet candidate."),
    ("cand-11134", "Dr Maria Santifaller", 195, 195, 0, "Full name as printed."),
    ("cand-0041", "Algarotti", 195, 195, 0, "Reuse Francesco Algarotti."),
    ("cand-11135", "the classicising print", 196, 196, 0, "Schmidt's 1752 print reported as the source for most Algarotti portraits."),
    ("cand-2396", "Georg Friedrich Schmidt", 197, 197, 0, "Reuse the indexed artist candidate."),
    ("cand-4623", "Berlin", 196, 196, 0, "Reuse Berlin as location of the print."),
    ("cand-2345", "Felice Salimbeni", 197, 197, 0, "Reuse the indexed singer/person candidate."),
    ("cand-11136", "the same artist", 197, 197, 0, "Refers to Georg Friedrich Schmidt."),
    ("cand-0041", "Algarotti", 197, 197, 1, "Reuse Francesco Algarotti as the print's commissioner/recipient."),
    ("cand-11134", "Dr Santifaller", 197, 197, 0, "Reuse Maria Santifaller."),
    ("cand-11138", "the etchings made by Algarotti himself", 197, 197, 0, "Reuse the work group of Algarotti's own etchings."),
    ("cand-2569", "Tiepolo", 197, 197, 0, "Reuse Giambattista Tiepolo as collaborator."),
    ("cand-10999", "Michael Levey", 197, 197, 0, "Reuse the existing full-name person candidate."),
    ("cand-10264", "a portrait of Algarotti", 197, 197, 0, "Reuse the previously recorded unidentified portrait candidate; identity with the 1741 letter portrait remains to be checked."),
    ("cand-2569", "Tiepolo", 197, 197, 1, "Reuse Tiepolo as the artist in the disputed portrait theory."),
    ("cand-0041", "Algarotti", 197, 197, 2, "Reuse the portrait's sitter."),
    ("cand-11134", "Dr Santifaller", 199, 199, 0, "Reuse Maria Santifaller in the tomb-painting discussion."),
    ("cand-11141", "the charming painting of Algarotti’s tomb", 199, 199, 0, "Newly discussed tomb painting; its attribution continues on p.410."),
    ("cand-5628", "Pisa", 199, 199, 0, "Reuse the Pisa place candidate."),
    ("cand-11142", "the Volpato engraving", 199, 199, 0, "Probable source for the tomb painting, not certain."),
    ("cand-2790", "Volpato", 199, 199, 0, "Reuse Giovanni Volpato."),
    ("cand-11143", "John Bryson collection", 199, 199, 0, "Reuse the named collector; the institution/collection itself is not given a separate type."),
    ("cand-11144", "Oxford", 199, 199, 0, "Reuse the newly recorded city location."),
    ("cand-11145", "Schloss Charlottenburg, Berlin", 199, 199, 0, "Current location named in Haskell's report."),
    ("cand-4623", "Berlin", 199, 199, 0, "Reuse Berlin as the location of Schloss Charlottenburg."),
]

line_offsets = {}
cursor = 0
for line_number in range(187, 200):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p409-{index:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"mention ID exists: {mention_id}")
    if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["status"] != "open":
        raise SystemExit(f"unavailable mention candidate: {candidate_id}")
    start = line_offsets[first_line]
    end = line_offsets[last_line] + len(source_lines[last_line - 1])
    position = start
    for _ in range(occurrence + 1):
        position = body.find(surface, position, end)
        if position < 0:
            raise SystemExit(f"exact source surface not found L{first_line}-{last_line}: {surface!r}")
        position += len(surface)
    position -= len(surface)
    new_mentions.append({"mention_id": mention_id, "segment_id": P409, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(position),
                         "end_char": str(position + len(surface)), "note": note})
    mention_ids.add(mention_id)

note_lines = {1: 271, 2: 271, 3: 271, 4: 272, 5: 273, 6: 273, 7: 274, 8: 274, 9: 275}
source_file = "02-sources/02-Markdown/20_CHP-20Postscript.md"
statement_ids = {row["statement_id"] for row in statements}
existing_statement_ids = set(statement_ids)

def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer,
                   qualification, mentioned, markers=(), relation=False, extra=None):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID exists: {statement_id}")
    statement_ids.add(statement_id)
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 409,
                  "pdf_physical_page": 18, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(mentioned)}
    if relation:
        qualifiers["relation_candidate"] = True
    if markers:
        qualifiers.update({"footnote_markers": list(markers), "footnote_text_pending": True,
                           "footnote_segment": NOTES,
                           "footnote_refs": [{"marker": n, "segment_id": NOTES, "source_line": note_lines[n]} for n in markers],
                           "footnote_statement_ids": [], "footnote_body_link_status": "pending"})
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": P409,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[first - 1:last]),
            "source_file": source_file, "origin": "book"}

cross_refs = [
    "st-chp14-p350-portrait-letter", "st-chp14-p355-tiepolo-paintings-in-collection",
    "st-chp14-p356-will-bequest-two-pictures-to-pitt", "st-chp14-p356-note5-treat-diderot-quotation",
]
existing_ids = {row["statement_id"] for row in statements}
for sid in cross_refs:
    if sid not in existing_ids:
        raise SystemExit(f"missing cross-reference statement: {sid}")

new_statements = [
    make_statement("st-chp20-p409-maggiotto-historical-portraiture", 188, 188, "cand-10042", None,
                   "offers_later_historical_portraiture_through_early_modern_view",
                   "Haskell describes Maggiotto's Doge portraits as an unusually revealing instance of medieval and later portraiture viewed through seventeenth- and eighteenth-century eyes.",
                   "Haskell", "authorial interpretation of the portrait series",
                   "This is Haskell's characterization of the series, not an independently established account of the artists' historical understanding. Footnote 1 identifies Matina's volume and remains queued.",
                   ["cand-10042", "cand-11124"], [1],
                   extra={"continuation_of_segment": P408,
                          "ocr_corrections": [{"source_line": 188, "ocr": "—in .the form", "print": "—in the form", "basis": "CHP-20Postscript.pdf physical page 18 image"}]}),
    make_statement("st-chp20-p409-da-pozzo-edition-and-will-publication", 190, 191, "cand-11125", "cand-0041",
                   "publishes_critical_edition_and_full_text_of_algarotti_will",
                   "Haskell says Giovanni da Pozzo published a critical edition of Algarotti's essays with bibliographical commentary and the full text of Algarotti's will, replacing earlier writers' reliance on inadequate summaries.",
                   "Haskell", "authorial report of recent scholarship",
                   "The critical edition and will publication are distinct archival/publication candidates; note 2 cites the edition and note 3 the will text. Neither publication has been independently consulted here.",
                   ["cand-11125", "cand-11126", "cand-11127", "cand-0041", "cand-10333"], [2, 3],
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p409-tesi-painted-pitt-bequests", 191, 192, "cand-10332", "cand-2551",
                   "two_pictures_bequeathed_to_pitt_attributed_to_mauro_tesi",
                   "Haskell reports that Da Pozzo's publication shows the two pictures Algarotti left to William Pitt the Elder were painted by Mauro Tesi; Haskell also remarks on Diderot's sarcastic amusement at the bequest.",
                   "Haskell reporting Da Pozzo and characterizing Diderot's response", "authorial report of documentary update",
                   "Reuse the earlier candidate and statement for the two Pitt bequests; p.409 adds the painter attribution. Diderot's response is reported by Haskell, not newly verified from Diderot. Footnote 3 remains queued.",
                   ["cand-10332", "cand-10333", "cand-0041", "cand-1947", "cand-2551", "cand-0919", "cand-11127"], [3], True,
                   {"cross_reference_statement_ids": ["st-chp14-p356-will-bequest-two-pictures-to-pitt", "st-chp14-p356-note5-treat-diderot-quotation"],
                    "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p409-tiepolo-pictures-bequeathed-to-cosimo-mari", 192, 193, "cand-0041", "cand-1543",
                   "bequeaths_two_tiepolo_pictures_with_named_subjects_to_cosimo_mari",
                   "Haskell says Algarotti bequeathed to Cosimo Mari two paintings by Tiepolo: one depicting Christ led to Calvary and another depicting a banquet of Mark Antony and Cleopatra.",
                   "Haskell reporting Da Pozzo's publication of the will", "authorial report of documentary evidence",
                   "Preserve the Italian titles as source formulations and keep the two works distinct from other paintings of the same subjects. The will text remains pending note 3 review.",
                   ["cand-0041", "cand-10333", "cand-1543", "cand-2569", "cand-11129", "cand-11132", "cand-11127"], [3], True,
                   {"related_candidate_ids_pending_alignment": ["cand-10314", "cand-11090"]}),
    make_statement("st-chp20-p409-tiepolo-subjects-explain-catalogue-absence", 193, 193, "cand-10332", "cand-11128",
                   "will_explains_absence_of_tiepolo_subjects_from_posthumous_collection_catalogue",
                   "Haskell says Tiepolo paintings of these subjects were independently known to have belonged to Algarotti, and their absence from the collection catalogue prepared twelve years after his death is explained by their bequest.",
                   "Haskell", "authorial reconciliation of documentary records",
                   "The statement concerns the two subjects and the named posthumous catalogue; it does not establish the catalogue's complete contents. Footnote 4 remains queued.",
                   ["cand-10332", "cand-0041", "cand-2569", "cand-11128", "cand-11129", "cand-11132"], [4],
                   {"cross_reference_statement_ids": ["st-chp14-p355-tiepolo-paintings-in-collection", "st-chp14-p356-will-bequest-two-pictures-to-pitt"]}),
    make_statement("st-chp20-p409-road-to-calvary-berlin-sketch-identification", 193, 193, "cand-11129", "cand-11130",
                   "almost_certainly_identifies_sketch_as_study_for_s_alvise_painting",
                   "Haskell says The Road to Calvary is almost certainly the sketch in Berlin for the large painting in the church of S. Alvise in Venice.",
                   "Haskell", "authorial identification with explicit high but nonabsolute confidence",
                   "Retain 'almost certainly'; the sketch and large painting remain distinct objects. Footnote 5 remains queued.",
                   ["cand-11129", "cand-11130", "cand-4623", "cand-11131", "cand-3401"], [5], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p409-banquet-sketch-cognacq-jay-possibility", 193, 194, "cand-11132", "cand-11133",
                   "possibly_identifies_banquet_sketch_with_cognacq_jay_version",
                   "Haskell says the sketch of The Banquet of Mark Anthony and Cleopatra may be the one in the Musée Cognacq-Jay in Paris, while acknowledging difficulties with accepting this identification.",
                   "Haskell", "authorial tentative identification with stated reservations",
                   "The location and identity are possible, not confirmed. Keep the Plate 61a sketch distinct from Plate 61b and other Tiepolo Banquet versions until S3/S5 evidence review. Footnote 5 remains queued.",
                   ["cand-11132", "cand-11133", "cand-4653", "cand-11129", "cand-11090"], [5],
                   {"related_candidate_ids_pending_alignment": ["cand-11090"],
                    "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p409-santifaller-algarotti-portraits-schmidt-print", 195, 197, "cand-11137", "cand-11135",
                   "reports_most_algarotti_portraits_derived_from_schmidt_1752_print",
                   "Haskell reports that Maria Santifaller showed that most portraits of Algarotti, including some previously unknown examples, derived from Georg Friedrich Schmidt's classicising print made in Berlin in 1752.",
                   "Haskell reporting Santifaller", "authorial report of scholarship",
                   "The article is footnote 6 (Santifaller 1976) and has not been independently consulted. 'Vast majority' remains Haskell's wording, not a quantified count.",
                   ["cand-11134", "cand-11137", "cand-0041", "cand-11135", "cand-2396", "cand-4623"], [6],
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p409-schmidt-salimbeni-etching", 197, 197, "cand-2396", "cand-2345",
                   "etches_salimbieni_for_algarotti_one_year_after_1752_print",
                   "Haskell says Georg Friedrich Schmidt etched for Algarotti the rather epicene features of the singer Felice Salimbeni in 1753, one year after the 1752 Algarotti print.",
                   "Haskell", "authorial report of a dated print and sitter description",
                   "The 1753 date is derived from Haskell's 'a year after' wording. Footnote 6 remains queued.",
                   ["cand-2396", "cand-11136", "cand-2345", "cand-0041"], [6]),
    make_statement("st-chp20-p409-santifaller-algarotti-etchings-collaboration", 197, 197, "cand-11139", "cand-11138",
                   "explores_algarotti_etchings_and_tiepolo_collaborations",
                   "Haskell says Santifaller also explored etchings made by Algarotti himself, sometimes in collaboration with Tiepolo.",
                   "Haskell reporting Santifaller", "authorial report of scholarship",
                   "The article is footnote 7 (Santifaller 1977); the specific prints and extent of collaboration are not enumerated here.",
                   ["cand-11134", "cand-11139", "cand-11138", "cand-2569"], [7], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p409-levey-corrects-tiepolo-algarotti-portrait-theory", 197, 198, "cand-11140", "cand-10264",
                   "attributes_portrait_theory_to_misreading_of_documents",
                   "Haskell says Michael Levey showed that the theory that Tiepolo projected or began a portrait of Algarotti, repeated by Haskell from earlier writers, rested on a misreading of documents; Haskell reluctantly agrees.",
                   "Haskell reporting Levey and revising his own earlier account", "authorial retrospective correction based on scholarship",
                   "Reuse the existing unidentified Algarotti portrait candidate from the 1741 letter as a related object, but do not assume the identities are settled. The Levey article is footnote 8 (1978) and has not been independently consulted.",
                   ["cand-11140", "cand-10999", "cand-2569", "cand-10264", "cand-0041"], [8],
                   {"cross_reference_statement_ids": ["st-chp14-p350-portrait-letter"],
                    "related_candidate_ids_pending_alignment": ["cand-10264"],
                    "cited_material_not_independently_consulted": True,
                    "ocr_corrections": [{"source_line": 198, "ocr": "a jnisreading", "print": "a misreading", "basis": "CHP-20Postscript.pdf physical page 18 image"}]}),
    make_statement("st-chp20-p409-santifaller-algarotti-tomb-painting-partial", 199, 199, "cand-11146", "cand-11141",
                   "discusses_tomb_painting_and_probable_volpato_source",
                   "Haskell says Santifaller discussed the painting of Algarotti's tomb in Pisa, probably derived from a Volpato engraving; it was in the John Bryson collection in Oxford in 1963 and was later in Schloss Charlottenburg, Berlin.",
                   "Haskell reporting Santifaller and his own location history", "authorial report of scholarship and object movement",
                   "The engraving derivation is probable. The article and source note remain pending. The sentence continues on p.410 with an attribution history, so this statement and p.409 remain partial until that page is reviewed.",
                   ["cand-11134", "cand-11146", "cand-11141", "cand-11142", "cand-2790", "cand-11143", "cand-11144", "cand-11145", "cand-5628"], [9], True,
                   {"cross_reference_segments": [{"segment_id": P410, "source_line_start": 201, "source_line_end": 202}],
                    "cited_material_not_independently_consulted": True})
]

for statement in new_statements:
    for cid in statement["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate: {cid}")
    if statement["original_quote"] != "\n".join(source_lines[statement["qualifiers"]["source_line_start"]-1:statement["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"statement source quote mismatch: {statement['statement_id']}")

# Close the cross-page sentence begun at p.408 using its p.409 continuation.
continued = next((row for row in statements if row["statement_id"] == "st-chp20-p408-parker-piccinio-engraving-models-partial"), None)
if not continued:
    raise SystemExit("p.408 Parker statement is missing")
q = continued["qualifiers"]
if (q.get("source_line_start"), q.get("source_line_end")) != (185, 185):
    raise SystemExit("p.408 Parker statement has unexpected span")
q["source_line_end"] = 188
q["continuation_printed_page"] = 409
q["continuation_pdf_physical_page"] = 18
q["qualification"] = "P.409 completes the sentence: Matina's volume consisted essentially of medallion portraits of the Doges through 1659. Preserve Parker's tentative 'probably' attribution to Piccino; notes and the precise volume identity remain pending."
q["footnote_markers"] = [1]
q["footnote_text_pending"] = True
q["footnote_segment"] = NOTES
q["footnote_refs"] = [{"marker": 1, "segment_id": NOTES, "source_line": 271}]
q["footnote_statement_ids"] = []
q["footnote_body_link_status"] = "pending"
continued["original_quote"] = source_lines[184] + "\n" + source_lines[187]
continued["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(q["mentioned_candidate_ids"] + ["cand-11124", "cand-10042"]))
candidate_by_id["cand-11124"]["detail"] = "Haskell reports the volume as consisting essentially of medallion portraits of all Doges who presided over Venice through 1659. Parker tentatively identifies its engravings as Piccino's; the volume title and note 1 remain pending."

coverage_by_id[P408]["disposition"] = "reviewed"
coverage_by_id[P408]["migration_status"] = "complete"
coverage_by_id[P408]["note"] = "Printed p.408 (PDF physical page 17) checked against page image. P.409 L188 completes the Parker sentence about Matina's volume and Doge medallions. Footnotes 1-7 link to queued notes L267-270."
coverage_by_id[P409]["disposition"] = "reviewed"
coverage_by_id[P409]["migration_status"] = "partial"
coverage_by_id[P409]["source_line_ranges"] = "L187-199"
coverage_by_id[P409]["note"] = "Printed p.409 (PDF physical page 18) checked against page image. Footnotes 1-9 link to queued notes L271-275; S0 note numbering at L271 is OCR-misaligned with the printed footer. The final Santifaller/tomb-painting attribution sentence continues on p.410 L201-202."

all_mentions = mentions + new_mentions
spans = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"])
               for r in all_mentions if r["segment_id"] == P409)
for i, left in enumerate(spans):
    for right in spans[i+1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"crossing/duplicate mention spans: {left[2]} / {right[2]}")

paths = [candidate_path, mention_path, statement_path, coverage_path]
if ARGS.apply:
    backups = [path.with_name(path.name + BACKUP) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("p.409 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"APPLIED p.409: candidates+={len(candidate_specs)}, mentions+={len(new_mentions)}, statements+={len(new_statements)}; p.408 complete, p.409 partial; backup={BACKUP}")
else:
    print(f"DRY RUN p.409: candidates+={len(candidate_specs)}, mentions+={len(new_mentions)}, statements+={len(new_statements)}; closes p.408 and leaves p.409 partial")
