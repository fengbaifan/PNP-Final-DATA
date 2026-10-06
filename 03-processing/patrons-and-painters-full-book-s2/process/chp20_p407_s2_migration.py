#!/usr/bin/env python3
"""Controlled S2 migration for printed p.407 (PDF physical p.16)."""
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
P406 = "chp-20:20_CHP-20Postscript:l150-162"
P407 = "chp-20:20_CHP-20Postscript:l164-172"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP = ".bak-s2-chp20-p407-20261004"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P407_SHA = "b9b3ba9f777bdcf5d0af79db02511e032f706f6927605ead0717e7c7180e92f0"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
ARGS = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


if sha(SOURCE) != SOURCE_SHA or sha(PDF) != PDF_SHA:
    raise SystemExit("source or PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(source_lines[163:172])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != P407_SHA:
    raise SystemExit("p.407 S0 segment hash mismatch")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
for segment_id in (P406, P407, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing segment: {segment_id}")
if segment_by_id[P407]["sha256"] != P407_SHA or segment_by_id[P407]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.407 S0 registration changed")
if (coverage_by_id[P406]["disposition"], coverage_by_id[P406]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.406 must be reviewed/partial before its continuation is closed")
if (coverage_by_id[P407]["disposition"], coverage_by_id[P407]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.407 is not queued/pending")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("postscript notes segment must remain queued")

candidate_specs = [
    ("cand-11094", "Joseph Smith's large paintings by Sebastiano Ricci (unnamed group)", "work", "P.407 calls these Smith's large paintings by Sebastiano Ricci and reports disagreement about whether they originated in another failed commission. No individual titles are given; keep this group distinct from the paintings in Smith's 1770 'second collection' problem pending evidence.", 165),
    ("cand-11095", "Possible Canaletto and/or Joseph Smith visit to Rome in the early 1740s", "event", "A disputed possibility, not an established journey: Haskell says Constable, supported implicitly by Links, was unconvinced that both men or Canaletto alone visited Rome.", 167),
    ("cand-11096", "Unidentified Canaletto view of Venice made for Joseph Smith and altered in 1751", "work", "Haskell reports that the view had been made sixteen years before 1751 and was altered to include the newly added façade of Smith's Grand Canal palace. No title or more precise identification is supplied; do not merge with other Canaletto Venice views without evidence.", 168),
    ("cand-11097", "Michael Levey's 1962 study of Canaletto's altered Venice view for Joseph Smith", "archive", "The body describes Levey's contribution but gives no article title. Footnote 3 and bibliography reconciliation remain pending; not independently consulted.", 168),
    ("cand-11098", "William Barcham", "person", "Full author name in the body; identity alignment remains for S3.", 168),
    ("cand-11099", "William Barcham's analysis of Joseph Smith's Palladian overdoor commission", "archive", "Publication described in the body without a title. Footnote 4 and bibliography reconciliation remain pending; not independently consulted.", 168),
    ("cand-11100", "Alice Binion", "person", "Full name in the body; identity alignment remains for S3.", 169),
    ("cand-11101", "Alice Binion's article on Marshal Schulenburg's collection and patronage", "archive", "Article described in the body; footnote 5 and bibliography details remain pending. Not independently consulted.", 169),
    ("cand-11102", "Elizabetta Antoniazzi Rossi", "person", "Name as printed in the body; identity alignment remains for S3.", 171),
    ("cand-11103", "Elizabetta Antoniazzi Rossi's article on minor genres in Schulenburg's collection", "archive", "Article described in the body; footnote 6 and bibliography details remain pending. Not independently consulted.", 172),
    ("cand-11104", "Links (scholar cited with W. G. Constable; identity unresolved)", "person", "Surname-only scholar in the body. Do not infer identity from the brief citation until note and bibliography review/S3.", 166),
    ("cand-11105", "Constable's assessment of the possible Canaletto-Rome visit, revised by Links", "archive", "Work described by the body and footnote 2 as Constable revised by Links, p.32. Its exact title and publication identity await note and bibliography review.", 167),
    ("cand-11106", "Minor genres of painting discussed in Schulenburg's collection", "term", "A category in Rossi's discussion; examples in the body include small landscapes, battles, and animal pictures. Do not convert the examples into individually identified works.", 172),
    ("cand-11107", "Local school of painting in Rossi's interpretation of Schulenburg's collection", "term", "Descriptive concept in Rossi's quoted interpretation of the collection; retain as her attributed interpretation, not an independently established curatorial program.", 172),
]

natural_keys = {(row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()) for row in candidates}
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID exists: {candidate_id}")
    key = (name.strip().casefold(), kind.casefold())
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {name}")
    row = {
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P407}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# Candidate ID, exact S0 surface, first line, last line, occurrence, note.
mention_specs = [
    ("cand-11094", "Smith’s large paintings by Sebastiano Ricci", 165, 165, 0, "Unidentified group whose origin is disputed; do not identify its members or equate it with the 1770 second-collection group."),
    ("cand-2440", "Smith’s", 165, 165, 0, "Reuse Joseph Smith candidate; the stated paintings are from his holdings."),
    ("cand-2154", "Sebastiano Ricci", 165, 165, 0, "Reuse the indexed artist candidate."),
    ("cand-11094", "his set", 165, 165, 0, "Anaphoric reference to Smith's group of large Ricci paintings."),
    ("cand-2440", "Smith’s financial arrangements", 165, 165, 0, "Reuse Joseph Smith candidate."),
    ("cand-0498", "Canaletto", 166, 166, 0, "Reuse the indexed Canaletto candidate covering p.407."),
    ("cand-9913", "W. G. Constable", 166, 166, 0, "Reuse the surname/initials candidate from p.316 note; identity is not inferred from John Constable."),
    ("cand-11104", "Links", 167, 167, 0, "Surname-only scholar said to support Constable implicitly; identity remains unresolved."),
    ("cand-11095", "paid a visit to Rome in the early 1740s", 167, 167, 0, "The visit is expressly disputed; Haskell reports doubts about both men travelling or Canaletto alone."),
    ("cand-0498", "Canaletto", 167, 167, 0, "Reuse Canaletto candidate as one of the possible travellers."),
    ("cand-2440", "the two men", 167, 167, 0, "Refers to Joseph Smith and Canaletto; the stated visit remains uncertain."),
    ("cand-4490", "Rome", 167, 167, 0, "Reuse the existing city place candidate."),
    ("cand-10999", "Michael\nLevey", 167, 168, 0, "Full name crosses the OCR source line boundary; reuse the full-name person candidate introduced earlier in this postscript."),
    ("cand-0498", "Canaletto", 168, 168, 1, "Reuse Canaletto candidate."),
    ("cand-11096", "a view of Venice", 168, 168, 0, "Specific but untitled painting described on p.407; retain separate from other Venice views pending S3/source review."),
    ("cand-2719", "Venice", 168, 168, 0, "Reuse the broad indexed Venice place candidate provisionally."),
    ("cand-2440", "Smith", 168, 168, 0, "Reuse Joseph Smith candidate."),
    ("cand-9737", "his patron’s palace", 168, 168, 0, "Reuse the unidentified Joseph Smith palace on the Grand Canal; do not supply a formal building name."),
    ("cand-8178", "Grand Canal", 168, 168, 0, "Reuse the place/waterway candidate."),
    ("cand-2440", "this touch of vanity", 168, 168, 0, "The possessive context refers to Smith's reported request; 'vanity' is Haskell's interpretation."),
    ("cand-0498", "Another aspect of Smith’s patronage of Canaletto", 168, 168, 0, "Reuse both patron and artist within the described Palladian commission."),
    ("cand-1807", "Palladio", 168, 168, 0, "Reuse the indexed architect/artist candidate; the phrase names his architectural principles."),
    ("cand-9251", "commission for a series of fantasising overdoors depicting sixteenth-century buildings and monuments", 168, 168, 0, "Reuse the broader Smith overdoors work group; p.407 describes the commission and iconographic range, but exact member works remain unnamed."),
    ("cand-11098", "William Barcham", 168, 168, 0, "Full author name; identity alignment remains for S3."),
    ("cand-2401", "Marshal Schulenburg’s", 169, 169, 0, "Reuse Marshal Johann Matthias Schulenburg candidate."),
    ("cand-9622", "collection", 169, 169, 0, "Reuse the unresolved collection/gallery candidate; taxonomy has no collection class."),
    ("cand-11100", "Alice Binion", 169, 169, 0, "Full author name; her judgment is reported by Haskell."),
    ("cand-2838", "Zanetti", 169, 169, 0, "Reuse A. M. Zanetti the Elder candidate indexed for p.407."),
    ("cand-0041", "Algarotti", 169, 169, 0, "Reuse Francesco Algarotti candidate indexed for p.407."),
    ("cand-2440", "Joseph Smith", 169, 169, 0, "Reuse Joseph Smith candidate in Binion's comparison."),
    ("cand-11100", "Binion acknowledges", 170, 170, 0, "Alice Binion is the subject of the verb; Haskell reports her acknowledgment."),
    ("cand-2401", "the man", 170, 170, 0, "Refers to Schulenburg in Haskell's response to Binion."),
    ("cand-1901", "Piazzetta", 171, 171, 0, "Reuse the indexed artist candidate for p.407."),
    ("cand-9600", "the two great ‘pastorals’", 171, 171, 0, "Reuse the unresolved group of two Piazzetta pastorals; do not assign an individual to Chicago or Cologne."),
    ("cand-4624", "Chicago", 171, 171, 0, "Reuse existing city-place candidate."),
    ("cand-6300", "Cologne", 171, 171, 0, "Reuse existing city-place candidate."),
    ("cand-2719", "eighteenth-century Venice", 171, 171, 0, "Reuse Venice place candidate in a cultural comparison; the claim is Haskell's assessment."),
    ("cand-2401", "him", 171, 171, 0, "Anaphoric reference to Schulenburg."),
    ("cand-11102", "Elizabetta Antoniazzi Rossi", 171, 171, 0, "Name as printed; identity alignment remains for S3."),
    ("cand-9622", "Schulenburg’s collection", 172, 172, 0, "Reuse the collection candidate."),
    ("cand-11106", "minor genres", 172, 172, 0, "Rossi's phrase is quoted by Haskell; retain this as her attributed classification."),
    ("cand-11106", "small landscapes, battles, animal pictures", 172, 172, 0, "Examples of the minor genres discussed; not separate identified pictures."),
    ("cand-11100", "Alice Binion’s conclusion", 172, 172, 0, "Rossi's stated position is compared with Binion's conclusion."),
    ("cand-11107", "local school of painting", 172, 172, 0, "Quoted interpretation attributed to Rossi, not an independently established program."),
    ("cand-11102", "she", 172, 172, 0, "Anaphoric reference to Elizabetta Antoniazzi Rossi."),
]

line_offsets = {}
cursor = 0
for line_number in range(164, 173):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p407-{index:03d}"
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
    new_mentions.append({"mention_id": mention_id, "segment_id": P407, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(position),
                         "end_char": str(position + len(surface)), "note": note})
    mention_ids.add(mention_id)

note_lines = {1: 264, 2: 264, 3: 265, 4: 265, 5: 266, 6: 266}


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer, qualification, ids,
                   note_markers=(), relation=True, extra=None):
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 407,
                  "pdf_physical_page": 16, "claim": claim, "speaker": speaker, "text_layer": layer,
                  "qualification": qualification, "mentioned_candidate_ids": ids,
                  "relation_candidate": relation}
    if note_markers:
        qualifiers.update({"footnote_markers": list(note_markers), "footnote_text_pending": True,
                           "footnote_segment": NOTES,
                           "footnote_refs": [{"marker": n, "segment_id": NOTES, "source_line": note_lines[n]} for n in note_markers],
                           "footnote_statement_ids": [], "footnote_body_link_status": "pending"})
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": P407, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[first - 1:last]),
            "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "origin": "book"}


new_statements = [
    make_statement("st-chp20-p407-daniels-origin-of-smith-ricci-pictures", 165, 165, "cand-11093", "cand-11094",
                   "disputes_derivation_from_failed_commission",
                   "Jeffrey Daniels disagrees with writers including Haskell who think Smith's large Sebastiano Ricci paintings may have derived from another commission that fell through. Daniels writes that there is no reason to believe Smith was not the originator of his set.",
                   "Haskell reporting Jeffrey Daniels and his own earlier view", "authorial report of a scholar's contrary interpretation",
                   "The possibility and the attribution are presented as a scholarly disagreement. Keep the set-level paintings unidentified and distinct from the p.406 1770 second-collection problem; footnote 1 remains queued.",
                   ["cand-11093", "cand-11094", "cand-2440", "cand-2154"], [1], True,
                   {"cross_reference_segments": [{"segment_id": P406, "source_line_start": 162, "source_line_end": 162}],
                    "related_candidate_ids_pending_alignment": ["cand-11074"]}),
    make_statement("st-chp20-p407-smith-canaletto-financial-details-unclear", 165, 166, "cand-2440", "cand-0498",
                   "financial_arrangements_with_canaletto_remain_unclear",
                   "Haskell says the precise details of Smith's financial arrangements with Canaletto remain unclear.",
                   "Haskell", "authorial qualification of patronage evidence",
                   "This is an explicit limit on what can be said about Smith's financial arrangements; it does not imply a particular payment or contract.",
                   ["cand-2440", "cand-0498"], (), True),
    make_statement("st-chp20-p407-constable-links-rome-visit-doubt", 166, 167, "cand-9913", "cand-11095",
                   "questions_likelihood_of_early_1740s_rome_visit",
                   "W. G. Constable, supported implicitly by Links, was not convinced that Smith and Canaletto together—or Canaletto alone—visited Rome in the early 1740s, contrary to Haskell's first-edition view.",
                   "Haskell reporting Constable and Links, and correcting his earlier view", "authorial report of scholarship and retrospective qualification",
                   "The journey is a disputed likelihood, not a confirmed event. Footnote 2 remains queued; the cited assessment was not independently consulted.",
                   ["cand-2440", "cand-0498", "cand-9913", "cand-11104", "cand-11105", "cand-11095", "cand-4490"], [2], True,
                   {"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_intro:l445-454", "source_line_start": 445, "source_line_end": 454}],
                    "cross_reference_statement_ids": ["st-chp10-p307-possible-rome-visit-and-roman-series"],
                    "cited_material_not_independently_consulted": True,
                    "ocr_corrections": [{"source_line": 165, "ocr": "The precise, details", "print": "The precise details", "basis": "CHP-20Postscript.pdf physical page 16 image"}]}),
    make_statement("st-chp20-p407-levey-smith-view-alteration-1751", 168, 168, "cand-11097", "cand-11096",
                   "canaletto_view_altered_for_smith_in_1751",
                   "Haskell credits Michael Levey with showing that in 1751 Canaletto had to alter a view of Venice made for Smith sixteen years earlier, adding the grand new façade recently built at Smith's Grand Canal palace. Haskell calls this a touch of vanity and says no portrait had yet come to light, without specifying whose portrait.",
                   "Haskell reporting Levey and adding his own assessment", "authorial report of scholarship and commentary",
                   "The picture title, exact façade, and subject of the unlocated portrait are not specified. The sixteen-year interval is Haskell's wording; do not infer a more precise date or formal palace name. Footnote 3 remains queued.",
                   ["cand-10999", "cand-11097", "cand-0498", "cand-11096", "cand-2719", "cand-2440", "cand-9737", "cand-8178"], [3], True,
                   {"related_candidate_ids_pending_alignment": ["cand-9216", "cand-9648"],
                    "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p407-smith-palladian-overdoor-commission", 168, 168, "cand-2440", "cand-9251",
                   "commissioned_palladian_overdoors_analyzed_by_barcham",
                   "Haskell describes Smith's patronage of Canaletto as including a carefully devised commission for a series of imaginary overdoors depicting sixteenth-century buildings and monuments, expressing a glorification of Palladio and his architectural principles; William Barcham analyzed the series.",
                   "Haskell reporting William Barcham and characterizing Smith's patronage", "authorial summary of a commission and later analysis",
                   "The passage does not divide the larger overdoor series into individually titled paintings or specify which elements were made by Canaletto. The source publication and its evidence await footnote 4 and bibliography review.",
                   ["cand-2440", "cand-0498", "cand-1807", "cand-9251", "cand-11098", "cand-11099"], [4], True,
                   {"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_intro:l456-466", "source_line_start": 456, "source_line_end": 466}],
                    "cross_reference_statement_ids": ["st-chp10-p308-door-series-contrasting-scenes"],
                    "related_candidate_ids_pending_alignment": ["cand-9239"],
                    "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p407-binion-schulenburg-collection-assessment", 169, 170, "cand-11101", "cand-9622",
                   "binion_assesses_schulenburg_taste_and_collecting",
                   "Haskell says Alice Binion traced some of Marshal Schulenburg's pictures and judged him less discerning than Zanetti, Algarotti, or Joseph Smith, with collecting for a permanent gallery appearing to be much of the pleasure. Haskell adds that too little is known to be sure of Schulenburg's taste.",
                   "Haskell reporting Binion and adding a qualification", "authorial report of scholarship and explicit limitation",
                   "The negative assessment is Binion's as quoted by Haskell; Haskell explicitly limits confidence because evidence about Schulenburg's taste is insufficient. Footnote 5 is printed as Binion on the page image, while S0 notes L266 OCR labels it '8'; preserve the body marker 5 and recheck the note segment later.",
                   ["cand-11100", "cand-11101", "cand-2401", "cand-9622", "cand-2838", "cand-0041", "cand-2440"], [5], True,
                   {"cited_material_not_independently_consulted": True,
                    "ocr_corrections": [{"source_line": 169, "ocr": "Marshall Schulenburg", "print": "Marshal Schulenburg", "basis": "CHP-20Postscript.pdf physical page 16 image"}]}),
    make_statement("st-chp20-p407-haskell-schulenburg-piazzetta-counterargument", 170, 171, "cand-2401", "cand-9600",
                   "piazzetta_pastorals_counter_binion_assessment",
                   "Haskell finds Binion's assessment difficult to accept because Schulenburg commissioned two great Piazzetta pastorals now reported at Chicago and Cologne; he says their difference from other eighteenth-century Venetian painting makes it difficult to conclude Schulenburg lacked sensitivity or failed to influence painters who worked for him.",
                   "Haskell responding to Binion", "authorial disagreement supported by a work-group example",
                   "The two pictures remain a group-level reference: the body does not map either picture individually to Chicago or Cologne. Haskell's inference about taste and influence is his assessment, not an independently established conclusion.",
                   ["cand-2401", "cand-1901", "cand-9600", "cand-4624", "cand-6300", "cand-2719"], (), True,
                   {"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_sec_ii:l83-93", "source_line_start": 83, "source_line_end": 93}],
                    "cross_reference_statement_ids": ["st-chp10-p314-piazzetta-subject-pictures-for-schulenburg", "st-chp10-p314-naturalism-inferred-from-schulenburg-genre-gallery"],
                    "related_candidate_ids_pending_alignment": ["cand-9601", "cand-9602"]}),
    make_statement("st-chp20-p407-rossi-minor-genres-schulenburg", 171, 172, "cand-11103", "cand-9622",
                   "rossi_reframes_schulenburg_minor_genres_as_local_school_defense",
                   "Haskell says Elizabetta Antoniazzi Rossi focuses on the so-called minor genres in Schulenburg's collection. After detailed examination, she accepts Binion's conclusion only in a qualified way: Rossi interprets the collection as possibly illustrating the local school of painting on a grand scale and as reflecting a possible duty to defend and spread a taste for minor types of painting.",
                   "Haskell reporting Rossi's interpretation", "authorial report of an attributed scholarly interpretation",
                   "The quoted phrases are Rossi's interpretation as relayed by Haskell, not a confirmed statement of Schulenburg's intent. The source groups small landscapes, battles, and animal pictures as examples; it does not identify particular works. Footnote 6 is printed as Rossi on the page image and maps to notes L266, where OCR numbering remains to be checked.",
                   ["cand-11102", "cand-11103", "cand-9622", "cand-11106", "cand-11107", "cand-11100"], [6], True,
                   {"cited_material_not_independently_consulted": True,
                    "ocr_corrections": [{"source_line": 172, "ocr": "it seems.as if he conceived of. his collection", "print": "it seems as if he conceived of his collection", "basis": "CHP-20Postscript.pdf physical page 16 image"}]})
]

existing_statement_ids = {row["statement_id"] for row in statements}
for statement in new_statements:
    if statement["statement_id"] in existing_statement_ids:
        raise SystemExit(f"statement ID exists: {statement['statement_id']}")
    existing_statement_ids.add(statement["statement_id"])
    first = statement["qualifiers"]["source_line_start"]
    last = statement["qualifiers"]["source_line_end"]
    if statement["original_quote"] != "\n".join(source_lines[first - 1:last]):
        raise SystemExit(f"statement quote mismatch: {statement['statement_id']}")
    for candidate_id in statement["qualifiers"]["mentioned_candidate_ids"]:
        if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate: {candidate_id}")

all_mentions = mentions + new_mentions
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
               for row in all_mentions if row["segment_id"] == P407)
for index, left in enumerate(spans):
    for right in spans[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"crossing/duplicate mention spans: {left[2]} / {right[2]}")

coverage_by_id[P406]["disposition"] = "reviewed"
coverage_by_id[P406]["migration_status"] = "complete"
coverage_by_id[P406]["note"] = "Printed p.406 (PDF physical page 15) checked against page image; the Jeffrey Daniels sentence fragment at L162 is completed by p.407 L165. Footnotes 1-9 remain linked to queued notes L259-263."
coverage_by_id[P407]["disposition"] = "reviewed"
coverage_by_id[P407]["migration_status"] = "complete"
coverage_by_id[P407]["source_line_ranges"] = "L164-172"
coverage_by_id[P407]["note"] = "Printed p.407 (PDF physical page 16) checked against page image. Completes the p.406 Jeffrey Daniels sentence. Footnotes 1-6 link to queued notes L264-266; printed footnote 5 is Binion although S0 notes L266 OCR reads 8."

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP) for path in paths]
if ARGS.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("p.407 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied p.407 S2 migration; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates={len(candidate_specs)}; new mentions={len(new_mentions)}; new statements={len(new_statements)}")
    print("p.406 continuation, p.407 source/PDF/S0 hashes, source spans, note links, candidate foreign keys, and mention overlaps validated")
