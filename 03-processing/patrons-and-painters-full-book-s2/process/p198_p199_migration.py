"""Controlled S2 migration for the reviewed p.198-199 body segments.

Run without --apply for a dry-run. OCR is retained as the quote anchor; scan
corrections are recorded in statement qualifiers.
"""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
base = root / "04-knowledge" / "tables"
source_rel = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
source_path = root / source_rel
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()

pages = {
    "chp-7:07_CHP-7_sec_iv:l77-87": {"page": 198, "physical": 36, "start": 77, "lo": 78, "hi": 87},
    "chp-7:07_CHP-7_sec_iv:l89-95": {"page": 199, "physical": 37, "start": 89, "lo": 90, "hi": 95},
}

new_candidates = [
    {"candidate_id": "cand-7237", "canonical_name": "Burghley, Lord Exeter's country house", "suggested_type": "place", "detail": "Named by Haskell as Exeter's country house where Verrio was employed to paint ceiling frescoes; no room or individual ceiling is identified.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L78"},
    {"candidate_id": "cand-7238", "canonical_name": "Holland as the political realm Shaftesbury supported", "suggested_type": "institution", "detail": "The passage contrasts Shaftesbury's sympathy for Holland with hostility to France; it does not name a specific policy or institution.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L82"},
    {"candidate_id": "cand-7239", "canonical_name": "Unidentified sculptor sought for Shaftesbury's proposed Virtues series", "suggested_type": "person", "detail": "Shaftesbury sent Closterman to Rome in 1699 to find a sculptor; no sculptor is named, and the project did not proceed.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7240", "canonical_name": "Proposed series of sculptures of the Virtues for Shaftesbury", "suggested_type": "work", "detail": "A proposed commission for an unnamed sculptor; the passage names no completed sculptures and says nothing came of the project.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7241", "canonical_name": "Drawings of Prudence and Justice by Domenico Guidi sent to Shaftesbury", "suggested_type": "work", "detail": "Closterman sent Shaftesbury some drawings by Guidi with a discouraging letter; the source does not establish that these were completed sculptures or that the proposed commission proceeded.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7242", "canonical_name": "Cambridge Platonists", "suggested_type": "term", "detail": "Named as the intellectual context of the Virtues subject choice; the passage does not identify individual members.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7243", "canonical_name": "Full-length classical portrait of Shaftesbury by John Closterman", "suggested_type": "work", "detail": "The source describes Shaftesbury in classical dress with volumes of Plato and Xenophon; it gives no title or present location.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7244", "canonical_name": "Plato", "suggested_type": "person", "detail": "Named as an author represented by a volume beside Shaftesbury in Closterman's portrait; no particular text is specified.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7245", "canonical_name": "Paolo de Matteis's Choice of Hercules (Plate 32b)", "suggested_type": "work", "detail": "The body calls it Hercules at the Crossroads between Vice and Virtue; the List of Plates identifies Plate 32b as Paolo de Matteis, The Choice of Hercules.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L85"},
    {"candidate_id": "cand-7246", "canonical_name": "Unidentified picture commissioned from Paolo de Matteis by Shaftesbury in 1713", "suggested_type": "work", "detail": "Haskell describes it as deeply moving and quotes Shaftesbury's French description; neither a title nor an independently verified identification is supplied.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l89-95#L90"},
    {"candidate_id": "cand-7247", "canonical_name": "Prudence as the subject of Guidi's drawings", "suggested_type": "term", "detail": "An allegorical subject named in the account of the drawings sent by Closterman; not treated as a historical person.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7248", "canonical_name": "Justice as the subject of Guidi's drawings", "suggested_type": "term", "detail": "An allegorical subject named in the account of the drawings sent by Closterman; not treated as a historical person.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L83"},
    {"candidate_id": "cand-7249", "canonical_name": "Vice and Virtue as the moral theme of the Choice of Hercules", "suggested_type": "term", "detail": "The two moral alternatives named in the title-like description of the painting; no independent iconographic interpretation is added.", "candidate_source_ref": "chp-7:07_CHP-7_sec_iv:l77-87#L85"},
]

# surface, candidate, note, optional line filter, optional occurrence indexes
mention_specs = {
    "chp-7:07_CHP-7_sec_iv:l77-87": [
        ("Burghley", "cand-7237", "Country house named in the continuation of p.197's open clause.", [78]),
        ("Verrio", "cand-2759", "Antonio Verrio; this closes the p.197 return-to-country-house clause.", [79]),
        ("Lord Exeter", "cand-0984", "Reuse the 5th Lord Exeter candidate; title identity remains for S3.", [80]),
        ("Carlo Maratta", "cand-1526", "Artist whom Exeter reportedly introduced to members of the nobility.", [81]),
        ("English milordi", "cand-0973", "General class of English visitors in the preceding tourist context; individual visitors are not identified.", [81]),
        ("the 3rd Earl of Shaftesbury", "cand-2426", "Index-seeded candidate; identity alignment remains for S3.", [81]),
        ("Italy", "cand-3461", "Place Shaftesbury visited in 1686.", [82]),
        ("Holland", "cand-7238", "Political realm named in Shaftesbury's sympathies.", [82]),
        ("France", "cand-7223", "France as a political power; hostile attitude is Haskell's account of Shaftesbury's stance.", [82]),
        ("Verrio’s frescoes", "cand-7213", "Unidentified Hampton Court allegorical fresco group reused from p.196.", [82]),
        ("Hampton Court", "cand-7212", "Named site of Verrio's frescoes.", [82]),
        ("William III", "cand-2814", "King whose policies are alluded to in the fresco programme.", [82]),
        ("John Closterman", "cand-0791", "Reuse the index-seeded painter candidate; spelling variant is not resolved here.", [82]),
        ("Rome", "cand-4490", "Destination of Closterman's 1699 search.", [83]),
        ("a sculptor capable of making for him a series of Virtues", "cand-7239", "Unnamed sculptor sought for the proposed project.", [83]),
        ("Virtues", "cand-7240", "The proposed series is a sculpture project, not a completed work.", [83]),
        ("Locke", "cand-1410", "John Locke, named in the description of Shaftesbury's intellectual context.", [83]),
        ("Cambridge Platonists", "cand-7242", "Named intellectual group; individual membership is not inferred.", [83]),
        ("Closterman", "cand-0791", "Painter named in the account of the drawings and portrait.", [83], [0, 1]),
        ("Prudence", "cand-7247", "Allegorical subject of one drawing.", [83]),
        ("Justice", "cand-7248", "Allegorical subject of one drawing.", [83]),
        ("Domenico Guidi", "cand-1277", "Reuse an existing Guidi person candidate; cross-chapter identity alignment remains for S3.", [83]),
        ("Shaftesbury", "cand-2426", "Named patron in the drawing and portrait account.", [83]),
        ("Plato", "cand-7244", "Author named on a volume depicted in the portrait.", [83]),
        ("Xenophon", "cand-4911", "Reuse the existing person candidate; the volume title is unspecified.", [83]),
        ("Naples", "cand-1722", "Destination of Shaftesbury's retirement.", [84]),
        ("Paolo de", "cand-1581", "First part of Paolo de Matteis split at the OCR line break; same artist candidate.", [84]),
        ("Matteis", "cand-1581", "Continuation of Paolo de Matteis across the OCR line break.", [85]),
        ("Hercules at the Crossroads between Vice and Virtue", "cand-7245", "Painting named descriptively in the body and identified as The Choice of Hercules in Plate 32b.", [85]),
        ("Vice and Virtue", "cand-7249", "Moral theme named in the painting description.", [85]),
    ],
    "chp-7:07_CHP-7_sec_iv:l89-95": [
        ("de Matteis", "cand-1581", "Paolo de Matteis; the artist is named by surname in this passage.", [90]),
        ("one further and deeply moving picture", "cand-7246", "Unidentified work commissioned in 1713; do not infer a portrait identity from the quoted description.", [90]),
        ("Shaftesbury", "cand-2426", "Named patron of the picture and subject of the final assessment.", [92, 93]),
    ],
}

statements = []

def add_statement(segment_id, sid, subj, obj, predicate, lo, hi, claim, qualification, mentioned, extra=None, speaker="Haskell"):
    page = pages[segment_id]
    qualifiers = {
        "source_line_start": lo,
        "source_line_end": hi,
        "printed_page": page["page"],
        "pdf_physical_page": page["physical"],
        "claim": claim,
        "speaker": speaker,
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        qualifiers.update(extra)
    statements.append({
        "statement_id": sid,
        "segment_id": segment_id,
        "subject_candidate_id": subj,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[lo - 1 : hi]),
        "origin": "book",
        "source_file": source_rel,
    })

add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-exeter-employs-verrio-burghley", "cand-0984", "cand-2759", "employed_to_paint_ceiling_frescoes_at", 78, 79, "Haskell says Exeter employed Verrio to paint ceiling frescoes at Burghley after circumstances compelled Verrio to leave court.", "The passage gives no room, individual ceiling, or precise date. This completes the open p.197 clause.", ["cand-0984", "cand-2759", "cand-7237"], {"continuation_of_statement_id": "st-chp7-p197-exeter-return-verrio-open", "continuation_status": "completed"})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-exeter-collecting-role", "cand-0984", None, "played_significant_role_in_english_collecting", 80, 80, "Haskell describes the 5th Lord Exeter as playing a highly significant role in the history of English collecting.", "This is Haskell's assessment, not a quantified comparison.", ["cand-0984"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-exeter-introduced-maratta", "cand-0984", "cand-1526", "introduced_artist_to_nobility", 81, 81, "Haskell reports that Exeter introduced Carlo Maratta to several members of the nobility.", "The individuals are unnamed, and the passage does not specify where or when the introductions occurred.", ["cand-0984", "cand-1526"], {"footnote_marker": 2})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-english-tourist-collecting", "cand-0973", None, "described_english_visitors_collecting_in_italy", 81, 81, "Haskell cites Italian biographies' accounts of English milordi visiting studios, paying high prices, and inviting artists from across the peninsula to settle in England.", "This is Haskell's characterization of vivid biographical accounts; no particular biography, visitor, transaction, or artist is identified here.", ["cand-0973", "cand-7200"], {"footnote_marker": 2})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-enthusiasm-and-shaftesbury-theory", "cand-2426", None, "theorised_english_art_patronage", 81, 81, "Haskell connects the indiscriminate enthusiasm for English collecting and patronage with the theorising of the 3rd Earl of Shaftesbury, whom he calls the most cultivated English aesthete of his day.", "The claim and superlative are Haskell's interpretation; retain the author's evaluative wording.", ["cand-2426", "cand-7200"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-welcomed-patronage", "cand-2426", "cand-7200", "welcomed_and_stimulated_english_patronage", 81, 81, "Haskell says Shaftesbury welcomed and stimulated English patronage of the arts while believing the subject needed much more consideration.", "This is Haskell's characterization of Shaftesbury's position, not a direct quotation.", ["cand-2426", "cand-7200"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-italy-visit", "cand-2426", "cand-3461", "visited_in_1686_at_age_fifteen", 82, 82, "Haskell says Shaftesbury visited Italy in 1686 at age fifteen and quotes that he acquired great knowledge of the polite arts.", "Haskell immediately says nothing is known of the results; do not infer particular acquisitions or outcomes.", ["cand-2426", "cand-3461"], {"footnote_marker": 3})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-political-sympathies", "cand-2426", None, "described_as_sympathetic_to_holland_and_hostile_to_france", 82, 82, "Haskell describes Shaftesbury as an eager Whig intellectual, deeply sympathetic to Holland and hostile to France.", "This is a characterization of political sympathy, not a specified office, policy, or formal affiliation.", ["cand-2426", "cand-7238", "cand-7223"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-verrio-programme", "cand-2426", "cand-7213", "probably_helped_draw_up_fresco_programme", 82, 82, "Haskell says Shaftesbury had in all probability helped draw up the programme for Verrio's Hampton Court frescoes, which alluded to William III's policies.", "In all probability marks the connection as Haskell's inference. The passage does not specify Shaftesbury's exact contribution.", ["cand-2426", "cand-7213", "cand-7212", "cand-2814"], {"footnote_marker": 4})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-closterman-search-sculptor", "cand-2426", "cand-7239", "sent_closterman_to_find_sculptor_in_rome", 82, 83, "Haskell says Shaftesbury sent portrait painter John Closterman to Rome in 1699 to find a sculptor capable of making a series of Virtues.", "The sculptor is unnamed; the proposed series was not completed. The line break after 'to' is preserved in the OCR quote.", ["cand-2426", "cand-0791", "cand-4490", "cand-7239", "cand-7240"], {"footnote_marker": 5})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-virtues-subject-choice", "cand-2426", "cand-7240", "selected_subject_for_project", 83, 83, "Haskell calls the choice of a series of Virtues characteristic of a pupil of Locke and the Cambridge Platonists.", "This is Haskell's interpretation of the subject choice; no completed sculpture series is claimed.", ["cand-2426", "cand-1410", "cand-7242", "cand-7240"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-guidi-drawings-project-failed", "cand-0791", "cand-7241", "sent_drawings_to_shaftesbury_project_abandoned", 83, 83, "Haskell says Closterman sent Shaftesbury drawings of Prudence and Justice by Domenico Guidi with a discouraging letter; nothing came of the project.", "The source does not establish that the drawings were commissioned sculptures or that the project advanced beyond this exchange.", ["cand-0791", "cand-2426", "cand-1277", "cand-7241", "cand-7247", "cand-7248", "cand-7240"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-endorsed-letter-inference", "cand-2426", None, "must_have_endorsed_discouraging_letter", 83, 83, "Haskell infers that Shaftesbury must have endorsed Closterman's discouraging letter.", "Must have marks an inference; the source does not report a direct reply or explicit endorsement.", ["cand-2426", "cand-0791"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-closterman-shaftesbury-portrait", "cand-0791", "cand-7243", "painted_full_length_portrait_of_patron", 83, 83, "Haskell says Closterman had already painted a full-length portrait of Shaftesbury in classical dress with volumes of Plato and Xenophon beside him.", "No title, date, or present location is supplied for the portrait.", ["cand-0791", "cand-2426", "cand-7243", "cand-7244", "cand-4911"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-closterman-instructions-advice", "cand-0791", "cand-2426", "recommended_patron_give_detailed_instructions", 83, 83, "Haskell says Closterman suggested Shaftesbury give detailed instructions to artists he proposed to employ in the future.", "OCR 'suture' is corrected to 'future' against the scan. This records advice, not evidence that every later commission followed it.", ["cand-0791", "cand-2426"], {"ocr_corrections": [{"source_line": 83, "ocr": "suture", "reading": "future", "basis": "PDF physical page 36."}]})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-retires-naples", "cand-2426", "cand-1722", "retired_to_naples_in_1711_due_to_ill_health", 84, 84, "Haskell says Shaftesbury was forced by ill-health to retire to Naples in 1711.", "The passage gives no diagnosis or exact date beyond the year.", ["cand-2426", "cand-1722"], {"footnote_marker": 6})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-buys-pictures-for-friends", "cand-2426", None, "mixed_in_intellectual_circles_and_bought_pictures_for_english_friends", 84, 84, "Haskell says Shaftesbury mixed in intellectual circles in Naples, bought pictures for his English friends, and decided to put his aesthetic ideas into practice.", "The friends, pictures, and intellectual circle are not identified; the passage does not name the individual purchases.", ["cand-2426", "cand-1722", "cand-7200"])
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-de-matteis-choice-hercules", "cand-2426", "cand-7245", "commissioned_choice_of_hercules_with_detailed_instructions", 84, 85, "Haskell says Shaftesbury chose Paolo de Matteis for an experiment and gave detailed instructions for a picture of Hercules at the Crossroads between Vice and Virtue.", "Plate 32b identifies the pictured work as de Matteis's The Choice of Hercules. The later publication of the instructions is stated by Haskell; the cited edition is not checked here.", ["cand-2426", "cand-1581", "cand-7245", "cand-7249"], {"cross_reference_segments": [{"segment_id": "front-matter:00_05_List_of_Plates:l83-118", "source_line_start": 92, "source_line_end": 93}]})
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-shaftesbury-quoted-aesthetic-instruction", "cand-2426", "cand-7249", "stated_historical_or_moral_should_govern_natural", 85, 86, "In Shaftesbury's quoted instruction, the merely natural must pay homage to the historical or moral; he criticizes a relish governed by immediate sensation rather than reflective thought and reason.", "This is a passage quoted in Haskell from Shaftesbury; preserve it as an attributed aesthetic argument, not a neutral rule adopted by this dataset.", ["cand-2426", "cand-7245", "cand-7249"], speaker="Shaftesbury (quoted by Haskell)")
add_statement("chp-7:07_CHP-7_sec_iv:l77-87", "st-chp7-p198-haskell-on-shaftesbury-executant", "cand-2426", None, "applied_artist_as_mechanical_executant_conception", 87, 87, "Haskell says Shaftesbury's elevated ideas and conception of the artist as a mechanical executant were not new but had rarely been applied so stringently to an actual creation.", "This is Haskell's historical evaluation; it refers to the Choice of Hercules discussed immediately before.", ["cand-2426", "cand-7245"])

add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-choice-hercules-failed-to-convey-thought", "cand-7245", None, "picture_did_not_betray_complex_thought", 90, 90, "Haskell says the resulting picture did not, or could not, betray the complex thought that had gone into making it.", "Haskell presents the relation between the concept and visible result as an evaluation, not a documented statement by the painter.", ["cand-7245"])
add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-shaftesbury-satisfied-with-picture", "cand-2426", "cand-7245", "more_interesting_to_theorists_but_satisfied_with_outcome", 90, 90, "Haskell says Shaftesbury's ideas were more interesting to theorists than artists, although Shaftesbury was satisfied with the outcome of the Choice of Hercules.", "The comparative judgment is Haskell's; the work's identity is linked to Plate 32b.", ["cand-2426", "cand-7245"], {"cross_reference_segments": [{"segment_id": "front-matter:00_05_List_of_Plates:l83-118", "source_line_start": 92, "source_line_end": 93}]})
add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-shaftesbury-1713-picture", "cand-2426", "cand-7246", "commissioned_further_picture_from_de_matteis_in_1713", 90, 91, "Haskell says Shaftesbury commissioned a further, deeply moving picture from de Matteis in 1713 and quotes its French description.", "The quoted description is retained in the source language. It does not supply a title or authorize an independent identification of the picture's subject.", ["cand-2426", "cand-1581", "cand-7246"], {"footnote_marker": 1, "ocr_corrections": [{"source_line": 90, "ocr": "Pliilosophe", "reading": "Philosophe", "basis": "PDF physical page 37."}, {"source_line": 91, "ocr": "retire", "reading": "retiré", "basis": "PDF physical page 37."}]})
add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-picture-as-history-instructions", "cand-2426", "cand-7246", "framed_picture_as_history_and_prescribed_execution", 92, 92, "Haskell says Shaftesbury treated the picture as a history, enclosed a rough drawing, prescribed details including the head's inclination, and insisted on examining preliminary sketches.", "The procedural details describe this commission; do not generalize them to all Shaftesbury commissions.", ["cand-2426", "cand-7246"], {"footnote_marker": 1})
add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-shaftesbury-died-before-order", "cand-2426", "cand-7246", "died_within_month_of_giving_order", 92, 92, "Haskell says Shaftesbury died within a month of giving the order.", "The source does not give an exact order or death date in this sentence, nor does it explicitly state the picture's completion status.", ["cand-2426", "cand-7246"], {"footnote_marker": 1})
add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-shaftesbury-civilising-role-of-art", "cand-2426", None, "stressed_role_of_art_in_civilising_society", 93, 94, "Haskell says Shaftesbury was among the first to stress art's role in civilising society, while extending the idea to the less acceptable concept that a good society would necessarily produce good art.", "Haskell's reservations are explicit; the proposition is attributed to Shaftesbury rather than endorsed as fact.", ["cand-2426"])
add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-shaftesbury-emotional-appeal", "cand-2426", None, "informal_writings_show_awareness_of_emotional_appeal", 94, 94, "Haskell says Shaftesbury's informal writings show that he was not blind to painting's more emotional appeal.", "This is Haskell's reading of the writings; the passage does not cite a particular text here.", ["cand-2426"])
add_statement("chp-7:07_CHP-7_sec_iv:l89-95", "st-chp7-p199-english-taste-and-patronage", "cand-2426", "cand-7200", "example_and_preaching_influenced_english_collecting", 94, 95, "Haskell says English taste soon favored portraiture, views, and landscape over serious history pictures Shaftesbury recommended, and that the extent of English collecting and patronage was in some measure due to his example and preaching.", "In some measure preserves Haskell's qualified causal claim; no proportions or additional causes are supplied here.", ["cand-2426", "cand-7200"])

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
if [c["candidate_id"] for c in new_candidates] != [f"cand-{i}" for i in range(7237, 7250)]:
    raise SystemExit("unexpected candidate sequence")
for c in new_candidates:
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
if any((s["subject_candidate_id"] and s["subject_candidate_id"] not in all_candidate_ids) or (s["object_candidate_id"] and s["object_candidate_id"] not in all_candidate_ids) for s in statements):
    raise SystemExit("statement endpoint FK missing")
if any(cid not in all_candidate_ids for s in statements for cid in s["qualifiers"]["mentioned_candidate_ids"]):
    raise SystemExit("statement mention FK missing")

coverage_rows = list(csv.DictReader(coverage_path.open(encoding="utf-8-sig", newline="")))
coverage_fields = list(coverage_rows[0].keys())
for segment_id in pages:
    matching = [r for r in coverage_rows if r["segment_id"] == segment_id]
    if len(matching) != 1 or matching[0]["disposition"] != "queued" or matching[0]["migration_status"] != "pending":
        raise SystemExit(f"segment absent, duplicate, or not queued: {segment_id}")

new_mentions = []
for segment_id, page in pages.items():
    # Mention offsets are relative to the full registered segment, including
    # its [Page N] marker; line bounds still refer to source-file lines.
    seg_text = "\n".join(source_lines[page["start"] - 1 : page["hi"]])
    found = {}
    for spec in mention_specs[segment_id]:
        surface, cid, note, *opt = spec
        lines = opt[0] if len(opt) else None
        occurrences = opt[1] if len(opt) > 1 else None
        if cid not in all_candidate_ids:
            raise SystemExit(f"mention candidate FK missing: {cid}")
        starts = []
        start = 0
        while True:
            pos = seg_text.find(surface, start)
            if pos < 0:
                break
            line = page["start"] + seg_text[:pos].count("\n")
            if lines is None or line in lines:
                starts.append((pos, pos + len(surface), line))
            start = pos + 1
        if occurrences is not None:
            starts = [m for i, m in enumerate(starts) if i in occurrences]
        if not starts:
            raise SystemExit(f"unmatched mention {surface!r} in {segment_id}")
        for lo, hi, line in starts:
            key = (lo, hi, cid)
            if key in found:
                found[key]["note"] = (found[key]["note"] + "; " + note).strip("; ")
            else:
                found[key] = {"mention_id": "", "segment_id": segment_id, "candidate_id": cid, "surface_form": surface, "start_char": str(lo), "end_char": str(hi), "note": note}
    rows = sorted(found.values(), key=lambda r: (int(r["start_char"]), int(r["end_char"]), r["candidate_id"]))
    span_owner = {}
    for row in rows:
        span = (row["start_char"], row["end_char"])
        if span in span_owner:
            raise SystemExit(f"duplicate span for {segment_id}: {span_owner[span]} and {row['candidate_id']}")
        span_owner[span] = row["candidate_id"]
    for i, row in enumerate(rows, 1):
        page_num = pages[segment_id]["page"]
        row["mention_id"] = f"m-chp7-p{page_num}-b{i:03d}"
        if row["mention_id"] in existing_mention_ids:
            raise SystemExit(f"mention id collision: {row['mention_id']}")
        if seg_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
            raise SystemExit(f"bad mention offset: {row}")
    new_mentions.extend(rows)

for s in statements:
    q = s["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1 : q["source_line_end"]])
    if s["original_quote"] not in excerpt or s["source_file"] != source_rel or s["origin"] != "book":
        raise SystemExit(f"quote/source mismatch: {s['statement_id']}")

p197_id = "st-chp7-p197-exeter-return-verrio-open"
p197 = next((s for s in statement_rows if s["statement_id"] == p197_id), None)
if p197 is None or p197["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("p.197 open clause missing or already closed")
p197_copy = json.loads(json.dumps(p197))
p197_copy["qualifiers"].update({
    "continuation_status": "completed",
    "continuation_to_segment_id": "chp-7:07_CHP-7_sec_iv:l77-87",
    "qualification": "The return-to-country-house clause is completed by p.198 L78-79, which names Burghley and Verrio's ceiling-fresco employment.",
    "claim": "Haskell says Exeter returned to his country house at Burghley and employed Verrio to paint ceiling frescoes after circumstances compelled Verrio to leave court.",
})

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == "chp-7:07_CHP-7_sec_iv:l63-75":
        row["note"] = "p.197 body migrated; its return-to-country-house clause is completed at p.198 L78-79. Notes 1-6 remain in composite L108-L112."
    if row["segment_id"] in pages:
        page = pages[row["segment_id"]]
        row.update({
            "disposition": "reviewed",
            "migration_status": "partial",
            "source_line_ranges": f"L{page['lo']}-{page['hi']}",
            "note": f"p.{page['page']} body read against PDF physical page {page['physical']} and migrated; page footnotes remain in the later composite note segment for source-order processing.",
        })
    updated_coverage.append(row)

backups = []
for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + ".bak-s2-chp7-p198-p199-20260930")
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    backups.append((path, backup))

preview = {"mode": "dry-run", "segments": list(pages), "new_candidates": len(new_candidates), "new_mentions": len(new_mentions), "new_statements": len(statements), "completed_cross_page_statement": p197_id, "coverage": "both reviewed/partial", "statement_ids": [statements[0]["statement_id"], statements[-1]["statement_id"]]}
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False))
    raise SystemExit(0)

for path, backup in backups:
    shutil.copy2(path, backup)

def atomic_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(f.name)
    temp.replace(path)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows = [p197_copy if s["statement_id"] == p197_id else s for s in statement_rows]
statement_rows.extend(statements)
atomic_csv(candidate_path, candidate_fields, candidate_rows)
atomic_csv(mention_path, mention_fields, mention_rows)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False, suffix=".tmp") as f:
    for row in statement_rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp = Path(f.name)
temp.replace(statement_path)
atomic_csv(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False))
