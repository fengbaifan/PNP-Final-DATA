#!/usr/bin/env python3
"""Controlled S2 migration for printed p.408 (PDF physical p.17)."""
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
P407 = "chp-20:20_CHP-20Postscript:l164-172"
P408 = "chp-20:20_CHP-20Postscript:l174-185"
P409 = "chp-20:20_CHP-20Postscript:l187-199"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP = ".bak-s2-chp20-p408-20261004"

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
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
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
body = "\n".join(source_lines[173:185])
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
if P408 not in segment_by_id or sha(body.encode("utf-8")) != segment_by_id[P408]["sha256"]:
    raise SystemExit("p.408 S0 segment hash mismatch")
if segment_by_id[P408]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.408 source registration changed")

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
for segment_id in (P407, P408, P409, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing segment: {segment_id}")
if (coverage_by_id[P407]["disposition"], coverage_by_id[P407]["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.407 must be complete before p.408")
if (coverage_by_id[P408]["disposition"], coverage_by_id[P408]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.408 is not queued/pending")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("postscript notes must remain queued")

# New candidates are limited to entities and work/source groups named in this page.
candidate_specs = [
    ("cand-11108", "Venetian Enlightenment as Haskell's term for an intellectual movement", "term", "Haskell says his own use of the term is very vague. Keep the label as a term under discussion, not as a settled historical periodization.", 176),
    ("cand-11109", "Franco Venturi's studies on the Venetian Enlightenment and Carlo Lodoli", "archive", "Works by Venturi are cited in p.408 notes 1-2; exact publication identity and relation to the bibliography remain pending.", 176),
    ("cand-11110", "Gianfranco Torcellan's 1969 publication cited on the Venetian Enlightenment", "archive", "The body credits Torcellan with recent scholarship; note 3 gives 1969. Title and bibliography match remain pending.", 177),
    ("cand-11112", "Le Blon's new colour-printing method", "term", "The invention is described as a new method of colour printing related by Antonio Conti to Newton's theories; the exact technical method is not identified here.", 179),
    ("cand-11113", "James Byam Shaw's 1967 study of Le Blon's invention", "archive", "The body describes Byam Shaw's identification; note 4 cites a 1967 publication, pp.21-6. Exact title and bibliography match remain pending.", 178),
    ("cand-11114", "Thomas J. McCormick", "person", "Full name as printed in the body; align identity during S3.", 180),
    ("cand-11115", "Vassar College Art Gallery", "institution", "Institution named as the source of the catalogue selections; do not treat it as the catalogue itself.", 181),
    ("cand-11116", "Thomas J. McCormick's catalogue of selections from Vassar College Art Gallery", "archive", "The body gives no catalogue title. Footnote 5 cites Vassar College Art Gallery, p.24; reconcile against bibliography after S2 notes review.", 180),
    ("cand-11117", "Unidentified Boscarati allegorical canvas linked to Giorgio Pisani's processional route", "work", "McCormick's catalogue includes another canvas; title and relation to the four Riviera-commissioned pictures or other p.326 groups remain unresolved.", 181),
    ("cand-11118", "Loredana Olivato", "person", "Full name as printed; align identity during S3.", 181),
    ("cand-11119", "Loredana Olivato's 1977 article on Boscarati and Pisani", "archive", "The body reports Olivato's interpretation; footnote 6 cites 1977. Exact title and bibliography match remain pending.", 181),
    ("cand-11120", "Trial of Giorgio Pisani at which Felice Boscarati gave evidence", "event", "The body identifies a trial and testimony but gives no date or further event detail. Do not merge with Pisani's arrest or political downfall without evidence.", 181),
    ("cand-11121", "Fondazione Giorgio Cini", "institution", "Named as recipient of the Zanetti caricature album; align the institution during S3.", 183),
    ("cand-11122", "Album containing 350 caricatures by A. M. Zanetti the Elder", "work", "The album is reported as discovered and presented to Fondazione Giorgio Cini. Its title, date, and current catalogue identity are not supplied.", 183),
    ("cand-11123", "Alessandro Bettagno's catalogue for the exhibition marking the Zanetti album gift", "archive", "The exhibition catalogue is described but untitled. Footnote 7 cites Bettagno; reconcile against bibliography after S2.", 183),
    ("cand-11124", "Engravings in Matina's volume probably used as models for Pinelli's Doge portraits", "work", "Parker's explanation is tentative and the sentence continues on p.409. Keep the source group unidentified until the continuation is reviewed.", 185),
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
           "candidate_source_ref": f"{P408}#L{line_number}"}
    candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# Candidate ID, exact S0 surface, first line, last line, occurrence, note.
mention_specs = [
    ("cand-11108", "Venetian Enlightenment", 176, 176, 0, "The label whose use Haskell explicitly calls vague."),
    ("cand-2751", "Franco Venturi", 177, 177, 0, "Reuse the indexed Professor Franco Venturi candidate."),
    ("cand-1411", "Lodoli", 177, 177, 0, "Reuse a Carlo Lodoli index candidate; duplicated index entries await S3 alignment."),
    ("cand-2644", "Gianfranco\nTorcellan", 177, 178, 0, "Full name crosses the OCR line boundary; reuse the indexed Torcellan candidate."),
    ("cand-8432", "James Byam Shaw", 178, 178, 0, "Reuse the indexed Byam Shaw person candidate; full-name form appears here."),
    ("cand-0826", "Antonio Conti", 178, 178, 0, "Reuse an existing Antonio Conti candidate; duplicate entries await S3 alignment."),
    ("cand-1739", "Sir Isaac Newton", 178, 178, 0, "Reuse the indexed Newton candidate."),
    ("cand-1375", "the German painter", 178, 178, 0, "Reuse the indexed LeBlon candidate; the sentence identifies this painter as Le Blon below."),
    ("cand-1375", "Jakob Christoffel\nLe Bion", 178, 179, 0, "Reuse the indexed LeBlon candidate; S0 OCR reads Le Bion but p.408 image reads Le Blon."),
    ("cand-11112", "a new method of colour printing", 178, 178, 0, "The method is described but not technically specified."),
    ("cand-8983", "England", 179, 179, 0, "Reuse the England place candidate."),
    ("cand-3461", "Italy", 179, 179, 0, "Reuse the Italy place candidate."),
    ("cand-11114", "Thomas J. McCormick", 180, 180, 0, "Full author name as printed."),
    ("cand-11115", "Vassar\nCollege Art Gallery", 180, 181, 0, "Institution name crosses the OCR line boundary."),
    ("cand-11116", "his catalogue of selections from the Vassar\nCollege Art Gallery", 180, 181, 0, "Untitled catalogue described by Haskell; the Vassar phrase is nested in this source mention."),
    ("cand-0411", "Felice Boscarati", 181, 181, 0, "Reuse the indexed artist candidate."),
    ("cand-11117", "another of the very bizarre allegorical canvases", 181, 181, 0, "Untitled individual canvas; keep distinct from the previously recorded group pending alignment."),
    ("cand-1942", "Giorgio Pisani", 181, 181, 0, "Reuse the indexed Pisani candidate."),
    ("cand-9792", "as he took up his appointment", 181, 181, 0, "Refers to Pisani's 1780 public entry/appointment; do not treat the pictures as specially commissioned."),
    ("cand-8449", "Procuratore di S. Marco", 181, 181, 0, "Reuse the Venetian office candidate."),
    ("cand-11118", "Loredana Olivato", 181, 181, 0, "Full name as printed."),
    ("cand-11117", "these abstruse pictures", 181, 181, 0, "Anaphoric reference to the previously described Boscarati canvases."),
    ("cand-11120", "the trial of Pisani", 181, 181, 0, "Trial event named in Olivato's account; date and relation to Pisani's downfall remain unresolved."),
    ("cand-0411", "Boscarati’s evidence", 181, 181, 0, "Reuse Felice Boscarati as the witness in the cited testimony."),
    ("cand-1942", "his patron", 181, 181, 0, "The patron in Boscarati's reported trial testimony is Giorgio Pisani."),
    ("cand-11118", "Dr Olivato", 181, 181, 0, "Reuse Loredana Olivato candidate."),
    ("cand-0411", "Boscarati himself", 181, 181, 0, "Reuse Felice Boscarati; the continued views are reported through Olivato."),
    ("cand-1942", "Pisani’s downfall", 181, 181, 0, "Reuse Pisani; do not equate this phrase with a particular arrest date."),
    ("cand-2838", "Anton Maria Zanetti (the Elder)", 183, 183, 0, "Reuse an A. M. Zanetti the Elder index candidate; duplicated index entries await S3 alignment."),
    ("cand-11122", "an album containing 350 of his caricatures", 183, 183, 0, "Newly reported album; the possessive refers to Zanetti the Elder."),
    ("cand-11121", "Fondazione Giorgio Cini", 183, 183, 0, "Institution receiving the album."),
    ("cand-3401", "Venice", 183, 183, 0, "Reuse the typed Venice place candidate."),
    ("cand-9321", "Alessandro Bettagno", 183, 183, 0, "Reuse the existing Bettagno person candidate."),
    ("cand-11123", "catalogue by Alessandro Bettagno of the exhibition held there to mark the gift", 183, 183, 0, "Untitled exhibition catalogue; Bettagno person mention is contained in this span."),
    ("cand-1932", "Maffeo Pinelli", 184, 184, 0, "Reuse the indexed Pinelli person candidate."),
    ("cand-10042", "At least six of the little oval portraits on copper of the Doges", 184, 184, 0, "Reuse the previously recorded Maggiotto series; p.408 reports that at least six have surfaced."),
    ("cand-1489", "Francesco Maggiotto", 184, 184, 0, "Reuse a Francesco Maggiotto index candidate."),
    ("cand-4190", "Plate 68", 184, 184, 0, "Plate 68a illustrates three portraits from the wider series; do not equate the illustration with all six newly surfaced portraits."),
    ("cand-9538", "Sir Karl Parker", 185, 185, 0, "Reuse the K. T. Parker candidate; identity alignment remains pending."),
    ("cand-10042", "their reappearance", 185, 185, 0, "Anaphoric reference to the portraits for Pinelli."),
    ("cand-11124", "adapted from engravings", 185, 185, 0, "Parker's explanation begins here and continues on p.409."),
    ("cand-1926", "those by Piccino", 185, 185, 0, "Reuse the indexed Piccino candidate; Parker's identification is tentative."),
    ("cand-1578", "Matina’s volume", 185, 185, 0, "Reuse the indexed Matina candidate; exact title/source remains pending."),
]

line_offsets = {}
cursor = 0
for line_number in range(174, 186):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p408-{index:03d}"
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
    new_mentions.append({"mention_id": mention_id, "segment_id": P408, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(position),
                         "end_char": str(position + len(surface)), "note": note})
    mention_ids.add(mention_id)

note_lines = {1: 267, 2: 267, 3: 268, 4: 268, 5: 269, 6: 269, 7: 270}
candidate_ids = set(candidate_by_id)
statement_ids = {row["statement_id"] for row in statements}
source_file = "02-sources/02-Markdown/20_CHP-20Postscript.md"

def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer,
                   qualification, mentioned, markers=(), relation=False, extra=None):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID exists: {statement_id}")
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 408,
                  "pdf_physical_page": 17, "claim": claim, "speaker": speaker,
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
    return {"statement_id": statement_id, "segment_id": P408,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[first - 1:last]),
            "source_file": source_file, "origin": "book"}

cross_pisani = ["st-chp10-p326-election-1780", "st-chp10-p326-picture-display-agency-alternatives",
                "st-chp10-p326-riviera-commission"]
cross_pinelli = ["st-chp13-p340-maggiotto-painted-doge-portrait-series-for-pinelli",
                 "st-chp20-plate68a-maggiotto-three-doge-portraits"]
existing_ids = {row["statement_id"] for row in statements}
for sid in cross_pisani + cross_pinelli:
    if sid not in existing_ids:
        raise SystemExit(f"missing cross-reference statement: {sid}")

new_statements = [
    make_statement("st-chp20-p408-venetian-enlightenment-recent-scholarship", 176, 178, "cand-11108", None,
                   "receives_recent_scholarly_attention",
                   "Haskell says the Venetian Enlightenment has received serious recent attention from Franco Venturi and Gianfranco Torcellan; he notes Venturi's attention to Lodoli and Torcellan's death at twenty-eight.",
                   "Haskell", "authorial retrospective and report of scholarship",
                   "The citations are footnotes 1-3 and remain queued; the precise publication identities await note and bibliography review. This sentence does not identify the two figures whose ideas and art patronage he later says are now clearer.",
                   ["cand-11108", "cand-2751", "cand-1411", "cand-2644", "cand-11109", "cand-11110"], [1, 2, 3],
                   extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p408-haskell-qualifies-enlightenment-term", 178, 178, "cand-11108", None,
                   "use_of_term_characterized_as_vague",
                   "Haskell says his own use of the term 'Venetian Enlightenment' can only be regarded as very vague, while ideas and art patronage of two varied figures discussed in this context have been clarified since 1963.",
                   "Haskell", "authorial qualification and summary of later scholarship",
                   "The passage does not name the pair in this sentence; do not assign the reference to specific candidates by inference.",
                   ["cand-11108"], [1, 2, 3]),
    make_statement("st-chp20-p408-byam-shaw-identifies-le-blon", 178, 179, "cand-11113", "cand-1375",
                   "identifies_contis_german_painter_as_le_blon",
                   "Haskell reports that James Byam Shaw identified the German painter in whom Antonio Conti was interested as Jakob Christoffel Le Blon; Conti connected Le Blon's new colour-printing method with Newton's theories, and the invention made a notable impact in England and Italy.",
                   "Haskell reporting James Byam Shaw", "authorial report of scholarship",
                   "The printed page reads Le Blon; S0 OCR reads Le Bion. The technical process and the claimed impact are not independently verified here. Footnote 4 remains queued.",
                   ["cand-11113", "cand-8432", "cand-1375", "cand-0826", "cand-11112", "cand-1739", "cand-8983", "cand-3461"], [4],
                   extra={"cited_material_not_independently_consulted": True,
                          "ocr_corrections": [{"source_line": 178, "ocr": "begji", "print": "been", "basis": "CHP-20Postscript.pdf physical page 17 image"},
                                              {"source_line": 179, "ocr": "Le Bion", "print": "Le Blon", "basis": "CHP-20Postscript.pdf physical page 17 image"}]}),
    make_statement("st-chp20-p408-mccormick-boscarati-canvas", 180, 181, "cand-11116", "cand-11117",
                   "catalogue_includes_boscarati_canvas_linked_to_pisani_procession",
                   "Haskell says Thomas J. McCormick's Vassar College Art Gallery catalogue published another unusual allegorical canvas by Felice Boscarati, connected with the political uproar around Giorgio Pisani's processional route as he took office as Procuratore di S. Marco.",
                   "Haskell", "authorial report of a catalogue and historical context",
                   "The canvas is unnamed. Its identity within or outside the four pictures previously connected with Pisani's route remains unresolved; footnote 5 is queued.",
                   ["cand-11114", "cand-11115", "cand-11116", "cand-0411", "cand-11117", "cand-1942", "cand-9792", "cand-8449"], [5], True,
                   {"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_sec_ii:l210-222", "source_line_start": 210, "source_line_end": 222}],
                    "cross_reference_statement_ids": cross_pisani,
                    "related_candidate_ids_pending_alignment": ["cand-9803", "cand-9807"],
                    "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p408-olivato-casual-picture-selection", 181, 181, "cand-11119", "cand-11117",
                   "supports_casual_rather_than_deliberately_provocative_selection",
                   "Haskell says Loredana Olivato accepts his tentative suggestion that the Boscarati pictures, painted years earlier for someone else, were probably selected for Pisani's processional route casually rather than to provoke deliberately.",
                   "Haskell reporting Olivato's article", "authorial report of attributed interpretation",
                   "This is explicitly probabilistic and attributed. Footnote 6 remains queued; the pictures' commission and display history should not be collapsed into one event.",
                   ["cand-11118", "cand-11119", "cand-11117", "cand-9792"], [6], True,
                   {"cross_reference_statement_ids": cross_pisani,
                    "related_candidate_ids_pending_alignment": ["cand-9803", "cand-9807"],
                    "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p408-olivato-boscarati-trial-testimony", 181, 181, "cand-11119", "cand-0411",
                   "quotes_boscarati_claim_about_pisani_interest_in_subjects",
                   "Haskell says Olivato quotes Boscarati's trial testimony that his patron, Giorgio Pisani, showed little interest in the subject matter of the pictures he commissioned.",
                   "Boscarati as quoted by Olivato and reported by Haskell", "nested report of testimony",
                   "The claim is attributed to Boscarati's testimony, quoted through Olivato; the trial record and article have not been independently consulted. The cited article is footnote 6.",
                   ["cand-11119", "cand-0411", "cand-1942", "cand-11120"], [6], True,
                   {"related_candidate_ids_pending_alignment": ["cand-9803", "cand-9807"],
                    "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p408-olivato-boscarati-subversive-opinions", 181, 181, "cand-0411", "cand-1942",
                   "continued_to_hold_subversive_opinions_after_pisani_downfall",
                   "Haskell says Olivato makes clear that Boscarati continued to hold subversive opinions long after Pisani's downfall.",
                   "Haskell reporting Olivato", "authorial report of scholarship",
                   "This is Olivato's reported finding; 'downfall' is not equated here with a specific trial, arrest, or date. Footnote 6 remains queued.",
                   ["cand-11118", "cand-11119", "cand-0411", "cand-1942"], [6], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p408-zanetti-caricature-album-presented-to-cini", 183, 183, "cand-11122", "cand-11121",
                   "album_of_350_caricatures_presented_to_fondazione_giorgio_cini",
                   "Haskell reports discovery of an album containing 350 caricatures by Anton Maria Zanetti the Elder and says it was presented to the Fondazione Giorgio Cini in Venice.",
                   "Haskell", "authorial report of a discovery and gift",
                   "The album title and date are not stated. Footnote 7 remains queued; no further provenance is inferred.",
                   ["cand-2838", "cand-11122", "cand-11121", "cand-3401"], [7], True),
    make_statement("st-chp20-p408-bettagno-zanetti-exhibition-catalogue", 183, 183, "cand-11123", "cand-11122",
                   "catalogues_exhibition_marking_gift_of_zanetti_album",
                   "Haskell says Alessandro Bettagno's catalogue of the exhibition marking the album's gift gives a useful summary of Zanetti's life and activities, while its illustrations show the circles in which he moved.",
                   "Haskell", "authorial assessment of a catalogue",
                   "The catalogue title and the exact exhibition details are not given. Footnote 7 remains queued and the cited catalogue has not been independently consulted.",
                   ["cand-9321", "cand-11123", "cand-11122", "cand-2838"], [7], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p408-six-maggiotto-doge-portraits-surface", 184, 184, "cand-10042", "cand-1932",
                   "at_least_six_portraits_have_surfaced",
                   "Haskell reports that at least six small oval portraits on copper of the Doges, painted by Francesco Maggiotto for Maffeo Pinelli, had come to light after the first edition; Plate 68 illustrates three from the series.",
                   "Haskell, crediting Sir Karl Parker for telling him of the reappearance", "authorial update linked to prior documentation",
                   "The number is a lower bound, not a count of the full series. Plate 68a shows three portraits and is not identical with the six newly surfaced objects. Link to the earlier p.340 statement without treating it as independent evidence.",
                   ["cand-10042", "cand-1932", "cand-1489", "cand-4190", "cand-9538"], (), True,
                   {"cross_reference_statement_ids": cross_pinelli}),
    make_statement("st-chp20-p408-parker-piccinio-engraving-models-partial", 185, 185, "cand-10042", "cand-11124",
                   "portraits_adapted_from_probable_piccino_engravings",
                   "Haskell says Sir Karl Parker pointed out that the Pinelli Doge portraits were adapted from engravings, probably those by Piccino in Matina's volume.",
                   "Haskell reporting Sir Karl Parker", "authorial report of a tentative source identification",
                   "The word 'probably' is retained. The sentence continues on p.409, so this statement remains partial until that segment is reviewed; Matina's volume and the engravings are not identified more precisely.",
                   ["cand-10042", "cand-9538", "cand-11124", "cand-1926", "cand-1578"], (), True,
                   {"cross_reference_segments": [{"segment_id": P409, "source_line_start": 187, "source_line_end": 199}],
                    "cross_reference_statement_ids": cross_pinelli,
                    "related_candidate_ids_pending_alignment": ["cand-4190"]}),
]

for statement in new_statements:
    if statement["statement_id"] in statement_ids:
        raise SystemExit(f"duplicate statement ID: {statement['statement_id']}")
    statement_ids.add(statement["statement_id"])
    for cid in statement["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate: {cid}")
    if statement["original_quote"] != "\n".join(source_lines[statement["qualifiers"]["source_line_start"]-1:statement["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"statement source quote mismatch: {statement['statement_id']}")

all_mentions = mentions + new_mentions
spans = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"])
               for r in all_mentions if r["segment_id"] == P408)
for i, left in enumerate(spans):
    for right in spans[i+1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"crossing/duplicate mention spans: {left[2]} / {right[2]}")

coverage_by_id[P408]["disposition"] = "reviewed"
coverage_by_id[P408]["migration_status"] = "partial"
coverage_by_id[P408]["source_line_ranges"] = "L174-185"
coverage_by_id[P408]["note"] = "Printed p.408 (PDF physical page 17) checked against page image. Footnotes 1-7 link to queued notes L267-270. Corrected OCR 'oiLodoli' to 'of Lodoli', 'begji' to 'been', and 'Le Bion' to printed 'Le Blon' in statement qualifiers only. The final Parker sentence continues on p.409; p.408 remains partial."

paths = [candidate_path, mention_path, statement_path, coverage_path]
if ARGS.apply:
    backups = [path.with_name(path.name + BACKUP) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("p.408 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"APPLIED p.408: candidates+={len(candidate_specs)}, mentions+={len(new_mentions)}, statements+={len(new_statements)}; backup={BACKUP}")
else:
    print(f"DRY RUN p.408: candidates+={len(candidate_specs)}, mentions+={len(new_mentions)}, statements+={len(new_statements)}; p.408 remains partial pending p.409")
