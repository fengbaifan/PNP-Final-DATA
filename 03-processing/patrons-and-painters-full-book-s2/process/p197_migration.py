"""Controlled S2 table migration for the reviewed p.197 body segment.

The authored claims and candidate mappings below are the semantic payload.
Run without --apply for preflight; use --apply only after reviewing the diff.
"""
import argparse
import csv
import json
import re
import shutil
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
base = root / "04-knowledge" / "tables"
segment_id = "chp-7:07_CHP-7_sec_iv:l63-75"
source_rel = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
source_path = root / source_rel
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
seg_start, seg_end = 63, 75
seg_text = "\n".join(source_lines[seg_start - 1 : seg_end])

new_candidates = [
    {
        "candidate_id": "cand-7231",
        "canonical_name": "Valerio Castelli",
        "suggested_type": "person",
        "detail": "Artist named in Haskell's list of Lord Exeter's Genoese collecting. No identity match is made here.",
        "candidate_source_ref": f"{segment_id}#L74",
    },
    {
        "candidate_id": "cand-7232",
        "canonical_name": "Unidentified tutor accompanying Sir Thomas Isham on his Italian tour",
        "suggested_type": "person",
        "detail": "The source says Isham travelled with his tutor but gives no name or further biographical information.",
        "candidate_source_ref": f"{segment_id}#L68",
    },
    {
        "candidate_id": "cand-7233",
        "canonical_name": "Royal family not identified in John Finch gift account",
        "suggested_type": "",
        "detail": "Haskell says Finch gave some religious pictures to the royal family; the members and dynastic identification are not supplied.",
        "candidate_source_ref": f"{segment_id}#L66",
    },
    {
        "candidate_id": "cand-7234",
        "canonical_name": "Unidentified frescoes by Luca Giordano at Palazzo Riccardi",
        "suggested_type": "work",
        "detail": "Haskell says Giordano was engaged on his frescoes in Palazzo Riccardi; no individual fresco subject or title is given.",
        "candidate_source_ref": f"{segment_id}#L73",
    },
    {
        "candidate_id": "cand-7235",
        "canonical_name": "Tomb made by Pierre Monnot for the 5th Lord Exeter",
        "suggested_type": "work",
        "detail": "The source says Exeter persuaded Monnot to make a tomb for him; no location, design, or present status is specified on this page.",
        "candidate_source_ref": f"{segment_id}#L75",
    },
    {
        "candidate_id": "cand-7236",
        "canonical_name": "Northamptonshire",
        "suggested_type": "place",
        "detail": "Place used by Haskell to qualify Sir Thomas Isham's origin; no more precise location is supplied.",
        "candidate_source_ref": f"{segment_id}#L68",
    },
]

# (surface, candidate, note, optional line filter, optional occurrence indexes,
#  optional OCR footnote character immediately after the matched surface)
specs = [
    ("Niccol\u00f2 Cassana", "cand-0593", "Named Genoese artist; death-date note 1 remains to be migrated."),
    ("she", "cand-0110", "Pronoun refers to Queen Anne.", [64]),
    ("his", "cand-0593", "Pronoun refers to Niccol\u00f2 Cassana.", [64]),
    ("the patronage of English royalty", "cand-0970", "Haskell's comparison of English royal patronage with tourist patronage."),
    ("tourists who flocked to Italy", "cand-0973", "Collective tourist group named in the index."),
    ("Italy", "cand-3461", ""),
    ("these", "cand-0973", "Pronoun refers to the tourists who travelled to Italy.", [65]),
    ("their own likenesses", "cand-0973", "Possessive refers to the tourist majority; the sitter examples are separately named."),
    ("30a", "cand-4057", "Explicit plate cross-reference; plate list identifies Jerome Bankes, not Killigrew or Altham."),
    ("30b", "cand-4024", "Explicit plate cross-reference; plate list identifies Sir Thomas Baines."),
    ("31a", "cand-4026", "Explicit plate cross-reference; plate list identifies Charles Fox."),
    ("Thomas Killigrew", "cand-1342", "Named portrait sitter; do not map to a plate number from this sentence."),
    ("James Altham", "cand-0085", "Named portrait sitter; do not map to a plate number from this sentence."),
    ("Sir Thomas Baines", "cand-0162", "Named portrait sitter; index candidate retained pending S3."),
    ("Rome", "cand-4490", ""),
    ("Naples", "cand-1722", ""),
    ("Florence", "cand-3397", ""),
    ("The few men who were detained in Italy on business", "cand-0973", "The passage describes a more enterprising minority within the Italy-travelling visitor context; the individuals are unnamed."),
    ("Baines\u2019s", "cand-0162", "Possessive identifies Baines as Finch's friend."),
    ("John.", "cand-1037", "OCR punctuation after John is spurious; Finch continues at source line 66."),
    ("Finch", "cand-1037", "Continuation of the name John Finch from source line 65."),
    ("Carlo Dolci", "cand-0923", ""),
    ("the royal family", "cand-7233", "Unidentified family group; not resolved to a named dynasty."),
    ("Sir Thomas Isham", "cand-1315", "Index-seeded candidate; identity remains for S3."),
    ("Northamptonshire", "cand-7236", ""),
    ("England", "cand-7200", ""),
    ("his tutor", "cand-7232", "The unnamed tutor is a distinct person candidate; identity unknown."),
    ("he", "cand-1315", "Pronoun refers to Sir Thomas Isham.", [68]),
    ("his", "cand-1315", "Pronoun refers to Sir Thomas Isham.", [68]),
    ("Buno Talbot", "cand-2539", "Named priest who advised Isham; Haskell's adjective is preserved in the statement, not treated as an identity fact."),
    ("Raphael", "cand-2098", ""),
    ("Guido Reni", "cand-2124", ""),
    ("Poussin", "cand-1984", ""),
    ("Pietro da Cortona", "cand-0342", ""),
    ("Ludovico", "cand-1169", "Source line break separates Ludovico (L69) from Gimignani (L70); index form is Lodovico."),
    ("Gimignani", "cand-1169", "Continuation of the printed name Ludovico Gimignani across the OCR line break."),
    ("Giacinto Brandi", "cand-0446", ""),
    ("Filippo Lauri", "cand-1366", ""),
    ("his", "cand-1315", "Pronoun refers to Sir Thomas Isham.", [70]),
    ("his portrait by Carlo Maratta (Plate 31b)", "cand-4027", "Explicit in-text plate reference to the captioned Isham portrait; work candidate reused from the plate-list source."),
    ("Carlo Maratta", "cand-1526", ""),
    ("5th Lord Exeter", "cand-0984", "Index-seeded title candidate; personal identity is not resolved here."),
    ("He", "cand-0984", "Pronoun refers to the 5th Lord Exeter.", [71, 75]),
    ("he", "cand-0984", "Pronoun refers to the 5th Lord Exeter.", [72]),
    ("Italy", "cand-3461", ""),
    ("Florence", "cand-3397", ""),
    ("Luca", "cand-1172", "First part of Luca Giordano split at the OCR line break between L72 and L73."),
    ("Giordano", "cand-1172", "Continuation of Luca Giordano across the OCR line break; the same candidate is used."),
    ("his", "cand-1172", "Pronoun in 'his frescoes' refers to Luca Giordano.", [73], [0]),
    ("his frescoes in the Palazzo Riccardi", "cand-7234", "Identifiable but untitled work group; nested place mention is separate."),
    ("Palazzo Riccardi", "cand-2145", "Place; reuse the existing palace candidate."),
    ("he", "cand-0984", "Pronoun refers to the 5th Lord Exeter.", [72]),
    ("Carlo Dolci", "cand-0923", ""),
    ("he", "cand-0984", "Pronoun refers to the 5th Lord Exeter.", [72]),
    ("his", "cand-0984", "Pronoun refers to the 5th Lord Exeter.", [73], [1, 2]),
    ("Lord Exeter", "cand-0984", "Later short-form reference to the 5th Lord Exeter.", [73]),
    ("England", "cand-7200", ""),
    ("Venice", "cand-3401", ""),
    ("Liberis", "cand-1401", "Printed plural form; mapped to the p.197 Pietro Liberi index candidate without normalizing the quote."),
    ("Bologna", "cand-3398", ""),
    ("Lorenzo Pasinelli", "cand-1843", ""),
    ("Genoa", "cand-1131", ""),
    ("Piola", "cand-1935", ""),
    ("Assereto", "cand-0143", ""),
    ("Valerio Castelli", "cand-7231", ""),
    ("Rome", "cand-4490", ""),
    ("Maratta", "cand-1526", ""),
    ("Brandi", "cand-0446", ""),
    ("Gaulli", "cand-1117", ""),
    ("Calandrucci", "cand-0481", ""),
    ("Pierre Monnot", "cand-1686", ""),
    ("a tomb for him", "cand-7235", "Phrase identifies the work; OCR footnote marker 6 immediately follows 'him'.", [75], None, "6"),
    ("him", "cand-0984", "Pronoun refers to the 5th Lord Exeter; OCR footnote marker 6 immediately follows.", [75], None, "6"),
]

statements = []

def add_statement(sid, subj, obj, predicate, lo, hi, claim, qualification, mentioned, extra=None):
    qualifiers = {
        "source_line_start": lo,
        "source_line_end": hi,
        "printed_page": 197,
        "pdf_physical_page": 35,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        qualifiers.update(extra)
    statements.append(
        {
            "statement_id": sid,
            "segment_id": segment_id,
            "subject_candidate_id": subj,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[lo - 1 : hi]),
            "origin": "book",
            "source_file": source_rel,
        }
    )

add_statement("st-chp7-p197-verrio-doubtless-greeted-cassana", "cand-2759", "cand-0593", "doubtless_greeted_artist", 64, 64, "Haskell says Verrio was doubtless there to greet the Genoese artist Niccolo Cassana.", "This completes the p.196 sentence. 'Doubtless' marks Haskell's inference; 'there' is not specified in the continuation.", ["cand-2759", "cand-0593"], {"continuation_of_statement_id": "st-chp7-p196-verrio_pension_open", "continuation_status": "completed", "footnote_marker": 1, "ocr_corrections": [{"source_line": 64, "ocr": "1714?", "reading": "1714.", "basis": "PDF physical page 35 shows a period followed by superscript footnote 1."}]})
add_statement("st-chp7-p197-queen-anne-employs-cassana", "cand-0110", "cand-0593", "employed_as_portrait_painter_until_death", 64, 64, "Haskell says Queen Anne employed Cassana as her portrait painter until his death in 1714.", "This is Haskell's date; note 1 is pending migration and may qualify the date.", ["cand-0110", "cand-0593"], {"footnote_marker": 1})
add_statement("st-chp7-p197-tourist-patronage-comparison", "cand-0970", "cand-0973", "compared_patronage_of_royalty_and_tourists", 65, 65, "Haskell says English royal patronage mattered little in the long run compared with the expanding tourist patronage of Italy in the second half of the seventeenth century.", "This is Haskell's comparative argument, not a quantified measure of patronage.", ["cand-0970", "cand-0973", "cand-3461"], {"ocr_corrections": [{"source_line": 65, "ocr": "th\u00e8", "reading": "the", "basis": "PDF physical page 35."}]})
add_statement("st-chp7-p197-tourists-seek-portraits", "cand-0973", None, "majority_interested_in_own_portraits", 65, 65, "Haskell says that at first the majority of these tourists were interested only in their own likenesses.", "These refers to the tourists who travelled to Italy; this is Haskell's generalization about the early pattern.", ["cand-0973"])
add_statement("st-chp7-p197-tourist-portrait-examples", None, None, "tourist_portraits_by_leading_artists", 65, 65, "Haskell names Thomas Killigrew, James Altham and Sir Thomas Baines as visitors who had portraits painted by leading artists in Rome, Naples and Florence.", "The sentence does not map each sitter to an individual artist or city. Plate-list cross-reference: 30a is Jerome Bankes, 30b Sir Thomas Baines, and 31a Charles Fox; these are not a one-to-one key for the three names in the following clause. Footnote 2 remains to be migrated.", ["cand-0973", "cand-1342", "cand-0085", "cand-0162", "cand-4490", "cand-1722", "cand-3397", "cand-4057", "cand-4024", "cand-4026"], {"footnote_marker": 2, "cross_reference_segments": [{"segment_id": "front-matter:00_05_List_of_Plates:l83-118", "source_line_start": 87, "source_line_end": 90}]})
add_statement("st-chp7-p197-business-visitors-more-enterprising", "cand-0973", None, "business_detained_visitors_more_enterprising", 65, 65, "Haskell distinguishes a few men detained in Italy on business as more enterprising than the portrait-focused majority.", "The men are not named as a group; this describes a minority within the visitor context, not individually identified people.", ["cand-0973", "cand-3461"])
add_statement("st-chp7-p197-finch-resident-florence", "cand-1037", "cand-3397", "resident_at", 65, 66, "Haskell identifies John Finch as Resident in Florence from 1665 to 1670.", "The OCR splits John and Finch across lines and inserts a spurious period after John; the PDF reads John Finch. The diplomatic title is retained as printed.", ["cand-1037", "cand-3397"], {"ocr_corrections": [{"source_line": 65, "ocr": "John.", "reading": "John", "basis": "PDF physical page 35; surname begins on L66."}]})
add_statement("st-chp7-p197-finch-commissioned-dolci", "cand-1037", "cand-0923", "commissioned_religious_pictures_from", 65, 66, "Haskell says Finch commissioned a number of religious pictures from Carlo Dolci.", "The page gives no titles, count, or commission dates for the pictures.", ["cand-1037", "cand-0923"], {"footnote_marker": 3})
add_statement("st-chp7-p197-finch-gifted-royal-family", "cand-1037", "cand-7233", "gave_some_pictures_to", 66, 66, "Haskell says Finch gave some of the religious pictures to the royal family.", "Neither the works nor the royal family members are identified.", ["cand-1037", "cand-0923", "cand-7233"], {"footnote_marker": 3})
add_statement("st-chp7-p197-isham-italian-tour", "cand-1315", "cand-3461", "travelled_in_italy_with_tutor", 68, 68, "Haskell says Sir Thomas Isham left England in October 1676, spent nearly eighteen months in Italy, visited most important towns, and travelled with his tutor.", "The duration is approximate, the towns are not enumerated, and the tutor is unnamed. Footnote 4 remains to be migrated.", ["cand-1315", "cand-7200", "cand-3461", "cand-7232"], {"footnote_marker": 4})
add_statement("st-chp7-p197-isham-love-affairs-and-debt", "cand-1315", None, "described_as_having_love_affairs_and_debt", 68, 68, "Haskell says Isham had a series of extravagant love affairs and got heavily into debt.", "Extravagant and heavily are Haskell's characterizations; no amounts or individual affairs are specified.", ["cand-1315"])
add_statement("st-chp7-p197-isham-acquired-paintings-with-advice", "cand-1315", "cand-2539", "acquired_paintings_advised_by", 68, 68, "Haskell says Isham acquired a certain number of contemporary paintings, advised mainly by the priest Buno Talbot.", "The number and individual paintings are unspecified; dissolute is Haskell's description of Talbot, not an independently verified identity fact.", ["cand-1315", "cand-2539"])
add_statement("st-chp7-p197-isham-commissions-in-rome", "cand-1315", "cand-4490", "commissions_located_in", 68, 70, "Haskell says all Isham's commissions were given in Rome.", "This does not locate every acquisition or identify the individual works.", ["cand-1315", "cand-4490"])
add_statement("st-chp7-p197-isham-copies-after-famous-works", "cand-1315", None, "acquired_copies_after_famous_works", 68, 70, "Haskell distinguishes copies after famous works by Raphael, Guido Reni, Poussin, Pietro da Cortona and others within the account of Isham's acquisitions.", "No copied work titles or original versions are identified; preserve the distinction from the mythological pictures named next.", ["cand-1315", "cand-2098", "cand-2124", "cand-1984", "cand-0342"])
add_statement("st-chp7-p197-isham-mythological-pictures", "cand-1315", None, "commissioned_mythological_pictures_from_artists", 69, 70, "Haskell says Isham's Rome commissions included mythological pictures by Ludovico Gimignani, Giacinto Brandi and Filippo Lauri.", "No picture titles, dates, or number by artist are given. Ludovico in the text differs from the index form Lodovico; identity remains a candidate-level issue.", ["cand-1315", "cand-1169", "cand-0446", "cand-1366"])
add_statement("st-chp7-p197-isham-portrait-maratta", "cand-1315", "cand-4027", "portrait_by", 70, 70, "Haskell identifies Isham's portrait by Carlo Maratta as Plate 31b.", "The List of Plates independently labels the captioned work Carlo Maratta: Sir Thomas Isham; reuse the existing work candidate, while keeping person identity alignment for S3.", ["cand-1315", "cand-1526", "cand-4027"], {"cross_reference_segments": [{"segment_id": "front-matter:00_05_List_of_Plates:l83-118", "source_line_start": 90, "source_line_end": 91}]})
add_statement("st-chp7-p197-exeter-larger-patronage-scale", "cand-0984", "cand-1315", "patronage_larger_scale_than", 71, 71, "Haskell says the 5th Lord Exeter was a collector and patron on a far larger scale than Isham.", "This is a relative scale judgment by Haskell. PDF physical page 35 shows footnote 5; S0 OCR reads marker 8.", ["cand-0984", "cand-1315"], {"footnote_marker": 5, "ocr_corrections": [{"source_line": 71, "ocr": "Exeter'was", "reading": "Exeter was", "basis": "PDF physical page 35."}, {"source_line": 71, "ocr": "scale.8", "reading": "scale.5", "basis": "PDF physical page 35; marker is superscript footnote 5."}]})
add_statement("st-chp7-p197-exeter-italian-visits", "cand-0984", "cand-3461", "visited_italy_on_two_occasions", 71, 72, "Haskell says Exeter was in Italy on two occasions between 1680 and 1685.", "No exact dates for either visit are supplied.", ["cand-0984", "cand-3461"])
add_statement("st-chp7-p197-exeter-commissioned-across-visited-cities", "cand-0984", None, "commissioned_paintings_in_cities_visited", 72, 72, "Haskell says Exeter commissioned paintings in all the cities he visited.", "The page does not enumerate every city in this general statement; named examples follow.", ["cand-0984"])
add_statement("st-chp7-p197-exeter-ordered-nine-dolci", "cand-0984", "cand-0923", "ordered_nine_paintings_from_in", 72, 72, "Haskell says Exeter ordered nine paintings from Carlo Dolci in Florence.", "The works are not individually titled on this page.", ["cand-0984", "cand-0923", "cand-3397"])
add_statement("st-chp7-p197-exeter-ordered-fifteen-giordano", "cand-0984", "cand-1172", "ordered_fifteen_paintings_from_in", 72, 72, "Haskell says Exeter ordered fifteen paintings from Luca Giordano in Florence.", "The works are not individually titled on this page.", ["cand-0984", "cand-1172", "cand-3397"])
add_statement("st-chp7-p197-giordano-frescoes-riccardi", "cand-1172", "cand-7234", "engaged_on_frescoes_at", 72, 73, "Haskell says Luca Giordano was engaged on his frescoes in Palazzo Riccardi.", "The possessive refers to Giordano; the passage gives no fresco titles or subject matter. This fresco group is distinct from the paintings ordered by Exeter.", ["cand-1172", "cand-7234", "cand-2145"])
add_statement("st-chp7-p197-dolci-giordano-contrast", "cand-0984", None, "evaluated_taste_through_artist_contrast", 73, 73, "Haskell contrasts Dolci's gentle, sweet, primitive restraint with Giordano's dashing virtuosity and says the two seem to have been Exeter's favourites.", "These are Haskell's aesthetic judgments and his inference about preference, not neutral measurements.", ["cand-0984", "cand-0923", "cand-1172"])
add_statement("st-chp7-p197-exeter-taste-breadth", "cand-0984", None, "interpreted_as_broad_or_inconsistent_taste", 73, 73, "Haskell says this contrast indicates the breadth, or inconsistency, of Exeter's taste.", "The breadth-or-inconsistency phrase is explicitly evaluative.", ["cand-0984", "cand-0923", "cand-1172"])
add_statement("st-chp7-p197-england-lacks-italian-painting", "cand-7200", None, "described_as_largely_bereft_of_italian_painting", 73, 73, "Haskell describes England as still largely bereft of Italian painting in the context of Exeter's collecting.", "This is a contextual authorial characterization, not a measured inventory of all English collections.", ["cand-7200", "cand-0984"])
add_statement("st-chp7-p197-exeter-aesthetic-experience", "cand-0984", None, "characterized_as_glutton_for_aesthetic_experience", 73, 73, "Haskell characterizes Exeter as a glutton for every kind of aesthetic experience.", "Rhetorical authorial evaluation; not an independently verified personality trait.", ["cand-0984"])
add_statement("st-chp7-p197-exeter-collected-liberi-venice", "cand-0984", "cand-1401", "collector_artist_association_in_city", 73, 73, "Haskell says Exeter bought Liberi works in Venice.", "The printed form is Liberis; no individual work is titled. This is the only city-list clause with an explicit verb; see also the following elliptical entries.", ["cand-0984", "cand-1401", "cand-3401"])
add_statement("st-chp7-p197-exeter-collected-pasinelli-bologna", "cand-0984", "cand-1843", "collector_artist_association_in_city", 73, 73, "Haskell lists Lorenzo Pasinelli in the Bologna portion of Exeter's collecting.", "The sentence is elliptical after he bought at Venice; do not treat a purchase verb or individual work title as explicit for this entry.", ["cand-0984", "cand-1843", "cand-3398"])
add_statement("st-chp7-p197-exeter-collected-piola-genoa", "cand-0984", "cand-1935", "collector_artist_association_in_city", 73, 74, "Haskell lists Piola among the Genoese artists associated with Exeter's collecting.", "The list is elliptical; no specific work or transaction type is supplied.", ["cand-0984", "cand-1935", "cand-1131"])
add_statement("st-chp7-p197-exeter-collected-assereto-genoa", "cand-0984", "cand-0143", "collector_artist_association_in_city", 73, 74, "Haskell lists Assereto among the Genoese artists associated with Exeter's collecting.", "The list is elliptical; no specific work or transaction type is supplied.", ["cand-0984", "cand-0143", "cand-1131"])
add_statement("st-chp7-p197-exeter-collected-castelli-genoa", "cand-0984", "cand-7231", "collector_artist_association_in_city", 73, 74, "Haskell lists Valerio Castelli among the Genoese artists associated with Exeter's collecting.", "No index candidate or named work was present for this artist; a source-derived candidate is kept open for S3.", ["cand-0984", "cand-7231", "cand-1131"])
add_statement("st-chp7-p197-exeter-collected-maratta-rome", "cand-0984", "cand-1526", "collector_artist_association_in_city", 74, 74, "Haskell lists Maratta among the artists associated with Exeter's Roman collecting.", "The list is elliptical; no specific work or transaction type is supplied.", ["cand-0984", "cand-1526", "cand-4490"])
add_statement("st-chp7-p197-exeter-collected-brandi-rome", "cand-0984", "cand-0446", "collector_artist_association_in_city", 74, 74, "Haskell lists Brandi among the artists associated with Exeter's Roman collecting.", "The list is elliptical; no specific work or transaction type is supplied.", ["cand-0984", "cand-0446", "cand-4490"])
add_statement("st-chp7-p197-exeter-collected-gaulli-rome", "cand-0984", "cand-1117", "collector_artist_association_in_city", 74, 74, "Haskell lists Gaulli among the artists associated with Exeter's Roman collecting.", "The list is elliptical; no specific work or transaction type is supplied.", ["cand-0984", "cand-1117", "cand-4490"])
add_statement("st-chp7-p197-exeter-collected-calandrucci-rome", "cand-0984", "cand-0481", "collector_artist_association_in_city", 74, 74, "Haskell lists Calandrucci among the artists associated with Exeter's Roman collecting.", "The list is elliptical; no specific work or transaction type is supplied.", ["cand-0984", "cand-0481", "cand-4490"])
add_statement("st-chp7-p197-exeter-unique-commission-scale", "cand-0970", "cand-0984", "claimed_unprecedented_commission_scale", 75, 75, "Haskell says no Englishman had previously commissioned contemporary Italian painting on this scale and few would do so again.", "This is Haskell's historical superlative; such a scale refers to Exeter's patronage and is not independently tested here.", ["cand-0970", "cand-0984"])
add_statement("st-chp7-p197-monnot-tomb", "cand-0984", "cand-7235", "persuaded_monnot_to_make_tomb", 75, 75, "Haskell says Exeter persuaded the Franco-Italian sculptor Pierre Monnot to make a tomb for him.", "The tomb is identifiable as a work group, but this page does not give its location, design, or later history. Footnote 6 remains to be migrated.", ["cand-0984", "cand-1686", "cand-7235"], {"footnote_marker": 6, "ocr_corrections": [{"source_line": 75, "ocr": "FrancoItalian", "reading": "Franco-Italian", "basis": "PDF physical page 35."}]})
add_statement("st-chp7-p197-exeter-return-verrio-open", "cand-0984", None, "return_clause_open", 75, 75, "The source begins a return-to-country-house clause about Exeter, but the place and resulting employment are completed on p.198.", "Open cross-page clause; do not infer Burghley or Verrio until the next source segment is semantically processed.", ["cand-0984"], {"continuation_status": "open", "continuation_to_segment_id": "chp-7:07_CHP-7_sec_iv:l77-87"})

candidate_path = base / "entity-candidates.csv"
mention_path = base / "mentions.csv"
statement_path = base / "book-statements.jsonl"
coverage_path = base / "s2-coverage.csv"

with candidate_path.open(encoding="utf-8-sig", newline="") as f:
    candidate_rows = list(csv.DictReader(f))
    candidate_fields = list(candidate_rows[0].keys())
existing_candidate_ids = {r["candidate_id"] for r in candidate_rows}
if any(c["candidate_id"] in existing_candidate_ids for c in new_candidates):
    raise SystemExit("new candidate id collision")
if [c["candidate_id"] for c in new_candidates] != [f"cand-{i}" for i in range(7231, 7237)]:
    raise SystemExit("unexpected candidate sequence")
for c in new_candidates:
    c = c
    row = {field: "" for field in candidate_fields}
    row.update(c)
    row.update({"status": "open", "candidate_origin": "body-mention"})
    c.clear()
    c.update(row)
all_candidate_ids = existing_candidate_ids | {c["candidate_id"] for c in new_candidates}

with mention_path.open(encoding="utf-8-sig", newline="") as f:
    mention_rows = list(csv.DictReader(f))
    mention_fields = list(mention_rows[0].keys())
existing_mention_ids = {r["mention_id"] for r in mention_rows}
with statement_path.open(encoding="utf-8-sig") as f:
    statement_rows = [json.loads(x) for x in f if x.strip()]
existing_statement_ids = {s["statement_id"] for s in statement_rows}
if any(s["statement_id"] in existing_statement_ids for s in statements):
    raise SystemExit("statement id collision")
if any(
    (s["subject_candidate_id"] and s["subject_candidate_id"] not in all_candidate_ids)
    or (s["object_candidate_id"] and s["object_candidate_id"] not in all_candidate_ids)
    for s in statements
):
    raise SystemExit("statement endpoint FK missing")
if any(
    cid not in all_candidate_ids
    for s in statements
    for cid in s["qualifiers"]["mentioned_candidate_ids"]
):
    raise SystemExit("statement mentioned_candidate_id FK missing")

coverage_rows = list(csv.DictReader(coverage_path.open(encoding="utf-8-sig", newline="")))
coverage_fields = list(coverage_rows[0].keys())
matching = [r for r in coverage_rows if r["segment_id"] == segment_id]
if len(matching) != 1:
    raise SystemExit("coverage row absent/nonunique")
cover = matching[0]
if cover["disposition"] != "queued" or cover["migration_status"] != "pending":
    raise SystemExit("segment is not queued/pending")

new_mentions_by_span = {}
def add_mention_spec(spec):
    surface, cid, note, *opt = spec
    lines = opt[0] if len(opt) > 0 else None
    occurrences = opt[1] if len(opt) > 1 else None
    suffix = opt[2] if len(opt) > 2 else None
    if cid not in all_candidate_ids:
        raise ValueError(f"mention candidate FK: {cid}")
    end_pattern = r"(?=" + re.escape(suffix) + r")" if suffix else r"(?!\w)"
    pattern = re.compile(r"(?<!\w)" + re.escape(surface) + end_pattern)
    matches = []
    for m in pattern.finditer(seg_text):
        line = seg_start + seg_text[: m.start()].count("\n")
        if lines is not None and line not in lines:
            continue
        matches.append((m.start(), m.end(), line))
    if occurrences is not None:
        matches = [item for index, item in enumerate(matches) if index in occurrences]
    if not matches:
        raise ValueError(f"unmatched mention spec {surface!r} {cid}")
    for start, end, line in matches:
        if seg_text[start:end] != surface:
            raise ValueError(f"surface mismatch {surface!r} at {start}:{end}")
        key = (start, end, cid)
        if key in new_mentions_by_span:
            old = new_mentions_by_span[key]
            if note and note not in old["note"]:
                old["note"] = (old["note"] + "; " + note).strip("; ")
        else:
            new_mentions_by_span[key] = {
                "mention_id": "",
                "segment_id": segment_id,
                "candidate_id": cid,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(end),
                "note": note,
            }

for spec in specs:
    add_mention_spec(spec)
new_mentions = sorted(
    new_mentions_by_span.values(),
    key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["candidate_id"]),
)
span_candidates = {}
for row in new_mentions:
    span = (row["start_char"], row["end_char"])
    prior = span_candidates.get(span)
    if prior is not None:
        raise SystemExit(f"exact duplicate surface span ({prior}, {row['candidate_id']})")
    span_candidates[span] = row["candidate_id"]
for i, a in enumerate(new_mentions):
    for b in new_mentions[i + 1 :]:
        x1, x2 = int(a["start_char"]), int(a["end_char"])
        y1, y2 = int(b["start_char"]), int(b["end_char"])
        if x1 < y1 < x2 < y2 or y1 < x1 < y2 < x2:
            raise SystemExit(f"crossing mention spans: {a} / {b}")
for index, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-chp7-p197-b{index:03d}"
    if row["mention_id"] in existing_mention_ids:
        raise SystemExit("mention id collision")
    if seg_text[int(row["start_char"]) : int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"bad persisted offset: {row}")

for statement in statements:
    q = statement["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1 : q["source_line_end"]])
    if statement["original_quote"] not in excerpt:
        raise SystemExit(f"quote anchor failure: {statement['statement_id']}")
    if statement["segment_id"] != segment_id or statement["source_file"] != source_rel:
        raise SystemExit(f"segment/source mismatch: {statement['statement_id']}")
    if statement["origin"] != "book":
        raise SystemExit(f"bad origin: {statement['statement_id']}")

p196_id = "st-chp7-p196-verrio_pension_open"
p196 = next((s for s in statement_rows if s["statement_id"] == p196_id), None)
if p196 is None:
    raise SystemExit("p196 open statement missing")
if p196["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("p196 continuation is not open")
p196_copy = json.loads(json.dumps(p196))
p196_copy["qualifiers"]["continuation_status"] = "completed"
p196_copy["qualifiers"]["continuation_to_segment_id"] = segment_id
p196_copy["qualifiers"]["qualification"] = "The p.196 clause is completed by the next-page clause at p.197 L64; “there” remains unspecified."
p196_copy["qualifiers"]["claim"] = "Haskell says Verrio lived until 1707 and received a pension from Queen Anne; the next-page clause says he was doubtless there to greet Niccolo Cassana."

updated_coverage = []
for row in coverage_rows:
    if row["segment_id"] == "chp-7:07_CHP-7_sec_iv:l48-61":
        row = dict(row)
        row["note"] = "p.196 body and note 2 migrated; the final sentence now closes at p.197 L64. Note 1 at composite L107 remains pending."
    if row["segment_id"] == segment_id:
        row = dict(row)
        row.update(
            {
                "disposition": "reviewed",
                "migration_status": "partial",
                "source_line_ranges": "L64-75",
                "note": "p.197 body read against PDF physical page 35 and migrated. OCR corrections are recorded in linked statements. Footnotes 1-6 remain in composite source lines L108-L112 for later source-order migration; the last clause continues on p.198.",
            }
        )
    updated_coverage.append(row)

backups = []
for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + ".bak-s2-chp7-p197-20260930")
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    backups.append((path, backup))

preview = {
    "segment": segment_id,
    "candidates": len(new_candidates),
    "mentions": len(new_mentions),
    "statements": len(statements),
    "completed_cross_page_statement": p196_id,
    "coverage": "reviewed/partial",
    "mention_ids": [new_mentions[0]["mention_id"], new_mentions[-1]["mention_id"]],
    "statement_ids": [statements[0]["statement_id"], statements[-1]["statement_id"]],
}
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if not args.apply:
    print(json.dumps({"mode": "dry-run", **preview}, ensure_ascii=True))
    raise SystemExit(0)

for path, backup in backups:
    shutil.copy2(path, backup)

def atomic_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(f.name)
    temp_path.replace(path)

candidate_rows.extend(new_candidates)
atomic_csv(candidate_path, candidate_fields, candidate_rows)
mention_rows.extend(new_mentions)
atomic_csv(mention_path, mention_fields, mention_rows)
statement_rows = [p196_copy if row["statement_id"] == p196_id else row for row in statement_rows]
statement_rows.extend(statements)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False, suffix=".tmp") as f:
    for row in statement_rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp_path = Path(f.name)
temp_path.replace(statement_path)
atomic_csv(coverage_path, coverage_fields, updated_coverage)
print(json.dumps({"mode": "applied", **preview}, ensure_ascii=True))
