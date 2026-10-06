"""Controlled S2 migration for chapter 16 p.374 and footnotes 1-4."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-16.pdf"
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
PDF_SHA = "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f"
BODY_PREV = "chp-16:16_CHP-16_intro:l3-14"
BODY = "chp-16:16_CHP-16_intro:l16-22"
BODY_NEXT = "chp-16:16_CHP-16_intro:l24-36"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
BACKUP_SUFFIX = ".bak-s2-chp16-p374-sasso-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.374 S2 migration")
args = parser.parse_args()


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 16 source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-16 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    16: "[Page 374]", 17: "—less frequently—the moderns", 18: "citta di Venezia",
    19: "truth", 20: "hot just clear", 21: "G. A. Armanni", 22: "eighteenthcentury",
    72: "Journal of the Warburg Institute", 73: "Letter 8",
    74: "Lettere pittoriche", 75: "Journal of Warburg Institute",
}
for line_number, fragment in required.items():
    if fragment.casefold() not in source_lines[line_number - 1].casefold():
        raise SystemExit(f"required source text changed at L{line_number}: {fragment}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, BODY_NEXT, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if (coverage_by_id[BODY_PREV]["disposition"] != "reviewed"
        or coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L70-71"):
    raise SystemExit("S2 coverage preconditions changed")
if any(row["segment_id"] == BODY for row in mentions):
    raise SystemExit("p.374 body already has mention rows")
if any(row.get("statement_id", "").startswith("st-chp16-p374-") for row in statements):
    raise SystemExit("p.374 statements already exist")

body_lines = {number: source_lines[number - 1] for number in range(16, 23)}
note_lines = {number: source_lines[number - 1] for number in range(69, 90)}
segment_lines = {BODY: body_lines, NOTES: note_lines}
segment_offsets = {}
for segment_id, lines in segment_lines.items():
    offset = 0
    segment_offsets[segment_id] = {}
    for number, line in lines.items():
        segment_offsets[segment_id][number] = offset
        offset += len(line) + 1

new_candidates = [
    ("cand-10608", "Tiepolo (surname-only painter reference in p.374; identity unspecified)", "person", BODY, 17,
     "Haskell uses only the surname in references to Strange's purchases and the pigeon detail; this candidate does not decide which Tiepolo is meant."),
    ("cand-10609", "Unidentified Tiepolo picture detail of a pigeon on a twig, which Strange wanted cut out", "work", BODY, 20,
     "The passage identifies only a detail and a request; it does not name the painting or say that the detail was actually cut out."),
    ("cand-10610", "Unidentified Tiepolo modello sought by Antonio Canova", "work", BODY, 22,
     "The source reports Canova's request and explicitly says the story that Sasso had bought all such modelli was not true."),
    ("cand-10611", "Unidentified Guardi drawings Strange wanted clear, finished, paired, and accurately coloured", "work", BODY, 20,
     "The specifications are reported through Sasso; the passage does not identify the drawings or confirm completion."),
    ("cand-10612", "Sasso's unidentified copy after one picture in his Tiepolo collection", "work", BODY, 22,
     "Haskell says one of the collection pictures was copied by Sasso; neither the copied picture nor the copy is identified."),
    ("cand-10613", "Letter 8 in the Strange-Sasso correspondence, dated 22 December 1784", "archive", NOTES, 73,
     "The footnote gives a letter number and date but not author direction, repository, or shelfmark."),
    ("cand-10614", "Two volumes of Lettere pittoriche di G. A. Armanni a G. M. Sasso", "archive", NOTES, 74,
     "The note locates the volumes in the Archivio of the Seminario Patriarcale, Venice, MSS. 565 and 566; the manuscripts were not consulted."),
    ("cand-10615", "Armanni letter to Sasso dated 7 July 1789, in which Mr Poore is discussed", "archive", NOTES, 74,
     "The note supplies this date and topic but does not establish that this is the source of the full quotation on p.374."),
    ("cand-10616", "Richardson auctions of 4 and 19 April 1805 for Edward Poore's prints and drawings", "event", NOTES, 74,
     "Haskell's note says the sales included Poore's prints and drawings and no Tiepolo reference; auction catalogues were not independently checked."),
]
for cid, name, suggested_type, segment_id, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    candidate = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{source_line}",
    }
    candidates.append(candidate)
    candidate_by_id[cid] = candidate

planned_mentions = []


def add_mention(candidate_id, surface, segment_id, source_line, note="", occurrence=0):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[segment_id][source_line]
    positions = []
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            break
        positions.append(pos)
        search_from = pos + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface occurrence not found at L{source_line}: {surface} #{occurrence + 1}")
    pos = positions[occurrence]
    start = segment_offsets[segment_id][source_line] + pos
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions
                if row["segment_id"] == segment_id]
    if any(start < other_end and other_start < end for other_start, other_end in occupied):
        raise SystemExit(f"mention overlaps an existing span: {surface} at L{source_line}")
    mention_id = f"m-chp16-p374-sasso-{len(planned_mentions) + 1:04d}"
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


mention_specs = [
    ("cand-2517", "Strange", BODY, 17, "", 0),
    ("cand-0581", "Rosalba", BODY, 17, "Index identity is Rosalba Carriera.", 0),
    ("cand-0498", "Canaletto", BODY, 17, "", 0),
    ("cand-10608", "Tiepolo", BODY, 17, "Surname only in the source.", 0),
    ("cand-9209", "Treviso", BODY, 17, "", 0),
    ("cand-1422", "London", BODY, 17, "", 0),
    ("cand-2517", "Strange", BODY, 18, "", 0),
    ("cand-2874", "Zompini", BODY, 18, "Index candidate is Gaetano Zompini.", 0),
    ("cand-2876", "Le Arti che vanno per le vie nella citta di Venezia", BODY, 18,
     "S0 reads 'per le vie'; the index sub-entry reads 'per via'. Preserve the title variant for S3.", 0),
    ("cand-1239", "Francesco Guardi", BODY, 18, "", 0),
    ("cand-2517", "Strange", BODY, 20, "", 0),
    ("cand-2364", "Sasso", BODY, 20, "", 0),
    ("cand-1239", "Guardi", BODY, 20, "", 0),
    ("cand-2719", "Venice", BODY, 20, "", 0),
    ("cand-1422", "London", BODY, 20, "", 0),
    ("cand-4653", "Paris", BODY, 20, "", 0),
    ("cand-4490", "Rome", BODY, 20, "", 0),
    ("cand-10608", "Tiepolo", BODY, 20, "Surname only in the source.", 0),
    ("cand-10609", "a pigeon on a twig", BODY, 20, "The detail is described but not titled.", 0),
    ("cand-2364", "Sasso", BODY, 21, "", 0),
    ("cand-0119", "G. A. Armanni", BODY, 21, "Index gives Armanni, G. A.", 0),
    ("cand-0381", "Bologna", BODY, 21, "", 0),
    ("cand-4490", "Rome", BODY, 21, "", 0),
    ("cand-1973", "Mr Poore", BODY, 21, "The note names an Edward Poore; retain that as Haskell's identification.", 0),
    ("cand-10608", "Tiepolo", BODY, 22, "Surname-only reference in Armanni's quoted remark.", 0),
    ("cand-0618", "Celesti", BODY, 22, "", 0),
    ("cand-2719", "Venice", BODY, 22, "", 0),
    ("cand-2364", "Sasso", BODY, 22, "", 0),
    ("cand-0532", "Canova", BODY, 22, "Index candidate is Antonio Canova.", 0),
    ("cand-4490", "Rome", BODY, 22, "", 0),
    ("cand-10608", "Tiepolo", BODY, 22, "Surname-only reference in Canova's request.", 1),
    ("cand-10610", "modello", BODY, 22, "Unidentified work form; the source does not give a title.", 0),
    ("cand-2364", "Sasso", BODY, 22, "", 1),
    ("cand-10598", "collection he made for himself", BODY, 22,
     "Links the auctioned collection to Sasso's small private collection introduced on p.373; identity remains an S3 alignment decision.", 0),
    ("cand-2569", "Giambattista", BODY, 22, "Index candidate is Tiepolo, Giambattista.", 0),
    ("cand-2624", "Gian Domenico Tiepolo", BODY, 22, "", 0),
    ("cand-10612", "one of his own copies of one of them", BODY, 22, "The copied painting is unidentified.", 0),
    ("cand-2154", "Sebastiano Ricci", BODY, 22, "", 0),
    ("cand-1950", "Pittoni", BODY, 22, "Index candidate is Giovan Battista Pittoni.", 0),
    ("cand-1239", "Guardi", NOTES, 72, "", 0),
    ("cand-6004", "Journal of the Warburg Institute", NOTES, 72, "", 0),
    ("cand-10613", "Strange-Sasso correspondence", NOTES, 73, "", 0),
    ("cand-10613", "Letter 8", NOTES, 73, "", 0),
    ("cand-10614", "Lettere pittoriche di G. A. Armanni a G. M Sasso", NOTES, 74,
     "S0 omits the period after M; the print reads G. M. Sasso.", 0),
    ("cand-10614", "MSS. 565 and 566", NOTES, 74, "", 0),
    ("cand-6589", "Seminario Patriarcale, Venice", NOTES, 74, "", 0),
    ("cand-1973", "Mr Poore", NOTES, 74, "", 0),
    ("cand-10615", "letter of 7 July 1789", NOTES, 74, "", 0),
    ("cand-10616", "two auctions—4 and 19 April 1805", NOTES, 74, "", 0),
    ("cand-1973", "Edward Poore", NOTES, 74, "", 0),
    ("cand-10608", "Tiepolo", NOTES, 74, "Surname-only reference in the note.", 0),
    ("cand-6004", "Journal of Warburg Institute", NOTES, 75, "Journal title as transcribed in S0.", 0),
]
for candidate_id, surface, segment_id, source_line, note, occurrence in mention_specs:
    add_mention(candidate_id, surface, segment_id, source_line, note, occurrence)

body17, body18, body19, body20 = source_lines[16], source_lines[17], source_lines[18], source_lines[19]
body21, body22 = source_lines[20], source_lines[21]
note72, note73, note74, note75 = source_lines[71], source_lines[72], source_lines[73], source_lines[74]

corrections_l18 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 18,
    "ocr": "citta", "print": "città", "basis": "CHP-16.pdf physical page 2.",
}]
corrections_l20 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 20,
    "ocr": "hot just clear", "print": "not just clear", "basis": "CHP-16.pdf physical page 2.",
}]
corrections_l22 = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 22,
     "ocr": "with'whom", "print": "with whom", "basis": "CHP-16.pdf physical page 2."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 22,
     "ocr": "eighteenthcentury", "print": "eighteenth-century", "basis": "The print hyphenates at the line break on physical page 2."},
]
corrections_note72 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 72,
    "ocr": "i960", "print": "1960", "basis": "CHP-16.pdf physical page 2.",
}]
corrections_note74 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 74,
    "ocr": "G. M Sasso", "print": "G. M. Sasso", "basis": "CHP-16.pdf physical page 2.",
}]
corrections_note75 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 75,
    "ocr": "i960", "print": "1960", "basis": "CHP-16.pdf physical page 2.",
}]

note1_id = "st-chp16-p374-note1-guardi-patronage-reference"
note2_id = "st-chp16-p374-note2-strange-sasso-letter8"
note3_ids = [
    "st-chp16-p374-note3-armanni-sasso-letters-and-poore",
    "st-chp16-p374-note3-poore-auction-sales",
]
note4_id = "st-chp16-p374-note4-haskell-journal-276"


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, speaker, text_layer, qualification, mentioned_ids, quote,
                   relation_candidate=False, **extra_qualifiers):
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 374, "pdf_physical_page": 2, "claim": claim,
        "speaker": speaker, "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    qualifiers.update(extra_qualifiers)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    })


purchase_link = {
    "cross_reference_segments": [BODY_PREV],
    "cross_reference_statement_ids": ["st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial"],
    "cross_reference_text": "P.373 L14's final 'and' continues as the less-frequent moderns on p.374 L17.",
    "cross_reference_text_pending": False,
}
make_statement(
    "st-chp16-p374-strange-pictures-list-and-custody", BODY, "cand-2517", "cand-2367",
    "sasso_purchase_list_continues_with_moderns_and_pictures_are_stored_then_sold", 17, 17,
    "Haskell continues the p.373 list of pictures Sasso bought for Strange, adding Rosalba, Canaletto, and Tiepolo as less-frequent moderns; he says the pictures stayed temporarily at Strange's house near Treviso or London apartments and were sold, or would have been, to rich amateurs.",
    "Haskell", "authorial report", "The complaint that buyers wanted modern pictures is quoted without a named original speaker; the sentence does not identify who completed each sale.",
    ["cand-2517", "cand-2367", "cand-0581", "cand-0498", "cand-10608", "cand-9209", "cand-1422"], body17,
    relation_candidate=True, **purchase_link,
)
make_statement(
    "st-chp16-p374-dealer-trade-secrecy-transport-customs", BODY, None, None,
    "picture_dealing_required_secrecy_and_involved_high_transport_and_customs_costs", 18, 18,
    "Haskell says collections likely to be dispersed had to be examined secretly, transport was very expensive, and customs were troublesome and sometimes evaded.",
    "Haskell", "authorial report", "This is a general account of the trade process, not a claim about a named shipment or a particular collector.",
    [], body18,
)
make_statement(
    "st-chp16-p374-strange-modern-art-commissions", BODY, "cand-2517", None,
    "occasionally_commissioned_modern_works_for_himself_or_a_client", 18, 18,
    "Haskell says Strange occasionally commissioned modern works for himself or for a client.",
    "Haskell", "authorial report", "No particular work or client is identified.",
    ["cand-2517"], body18, relation_candidate=True,
)
make_statement(
    "st-chp16-p374-strange-zompini-publication-plan", BODY, "cand-2517", "cand-2876",
    "planned_to_publish_an_edition_of_zompini_le_arti", 18, 18,
    "Haskell says Strange planned to publish an edition of Zompini's Le Arti che vanno per le vie nella citta di Venezia.",
    "Haskell", "authorial report", "The passage records a plan and does not say the edition appeared. S0 wording differs from the index title variant 'per via'; retain both for S3.",
    ["cand-2517", "cand-2874", "cand-2876"], body18,
    ocr_corrections=corrections_l18,
)
make_statement(
    "st-chp16-p374-strange-employs-guardi", BODY, "cand-2517", "cand-1239",
    "employed_the_little_known_francesco_guardi", 18, 18,
    "Haskell says Strange employed the then little-known Francesco Guardi.",
    "Haskell", "authorial report", "The accompanying Plate 64 reference is not treated as an independent identification of a particular work.",
    ["cand-2517", "cand-1239"], body18, relation_candidate=True,
)
make_statement(
    "st-chp16-p374-strange-view-of-guardi-truth", BODY, "cand-2517", "cand-1239",
    "thought_guardi_was_spirited_but_missed_truth_in_his_views", 19, 19,
    "Haskell reports that Strange found Guardi spirited but thought his painted views often missed the truth.",
    "Haskell reporting Strange", "reported opinion", "The quoted terms are attributed to Strange through Haskell; they are an aesthetic judgement, not a neutral measurement.",
    ["cand-2517", "cand-1239"], body19, relation_candidate=True,
    **{
        "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L72-L72",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L19", "footnote_note_statement_ids": [note1_id],
        "footnote_link_note": "Footnote 1 directs readers to Haskell's fuller references on Guardi patronage.",
    },
)
make_statement(
    "st-chp16-p374-strange-drawing-instructions-via-sasso", BODY, "cand-2517", "cand-2364",
    "asked_sasso_to_convey_guardi_drawing_specifications", 20, 20,
    "Haskell says Strange asked Sasso to tell Guardi that his drawings should be clear, well finished, a pair, and accurately coloured.",
    "Haskell reporting Strange", "authorial report with quoted specifications", "The specifications are recorded as a request; the passage does not identify the drawings or confirm that Guardi completed them.",
    ["cand-2517", "cand-2364", "cand-1239", "cand-10611"], body20,
    relation_candidate=True, ocr_corrections=corrections_l20,
)
make_statement(
    "st-chp16-p374-strange-collects-guardi-and-venetian-colour", BODY, "cand-2517", "cand-1239",
    "admired_guardi_and_owned_many_works_while_preferring_venetian_colour", 20, 20,
    "Haskell says Strange admired Guardi and owned many of his works; he links Strange's love of Venetian painting's colour and brio to distance from newer London, Paris, and Rome fashions and dry neo-classical works.",
    "Haskell", "authorial interpretation and report", "The number and identity of the works are unspecified; the comparison between artistic climates is Haskell's explanation.",
    ["cand-2517", "cand-1239", "cand-2719", "cand-1422", "cand-4653", "cand-4490"], body20,
    relation_candidate=True,
)
make_statement(
    "st-chp16-p374-strange-tiepolo-pigeon-detail", BODY, "cand-2517", "cand-10609",
    "wanted_a_tiepolo_picture_detail_of_a_pigeon_cut_out_for_him", 20, 20,
    "Haskell says Strange spoke enthusiastically of Tiepolo and wanted a pigeon-on-a-twig detail from one of his pictures cut out for himself.",
    "Haskell", "authorial report", "The painting is unnamed and the request is not evidence that the detail was actually removed.",
    ["cand-2517", "cand-10608", "cand-10609"], body20, relation_candidate=True,
    **{
        "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L73-L73",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L20", "footnote_note_statement_ids": [note2_id],
        "footnote_link_note": "Footnote 2 gives a dated letter locator for the Strange-Sasso correspondence.",
    },
)
make_statement(
    "st-chp16-p374-armanni-introduces-poore", BODY, "cand-0119", "cand-1973",
    "armanni_wrote_derisively_of_english_visitor_mr_poore", 21, 21,
    "Haskell identifies G. A. Armanni as a painter and dealer travelling between Bologna and Rome and says he wrote derisively of an English visitor, Mr Poore.",
    "Haskell", "authorial report", "The note later names an Edward Poore; the identity is recorded as Haskell presents it, without external verification.",
    ["cand-0119", "cand-0381", "cand-4490", "cand-1973"], body21, relation_candidate=True,
    **{
        "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L74-L74",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L21-L22", "footnote_note_statement_ids": note3_ids,
        "footnote_link_note": "Footnote 3 gives Armanni-Sasso correspondence and Poore-sale source leads.",
    },
)
make_statement(
    "st-chp16-p374-armanni-quote-on-poore", BODY, "cand-0119", "cand-1973",
    "quoted_armanni_remark_contrasts_greek_subtlety_with_tiepolo_and_celesti", 22, 22,
    "Haskell quotes Armanni asking how a visitor who loves Greek subtlety could patiently look at Tiepolo's stranezze, Celesti's caricatures, and lesser painters' schiribizzi.",
    "Armanni, as quoted by Haskell", "embedded quotation", "Haskell attributes the remark to Armanni and links the context to Mr Poore; the archival letter itself was not consulted.",
    ["cand-0119", "cand-1973", "cand-10608", "cand-0618"], body22, relation_candidate=True,
    **{
        "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L74-L74",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L21-L22", "footnote_note_statement_ids": note3_ids,
        "footnote_link_note": "The note says Poore is discussed in an Armanni letter dated 7 July 1789, without proving that this is the quotation's exact manuscript source.",
    },
)
make_statement(
    "st-chp16-p374-venetian-dealers-retain-painting-heritage", BODY, None, None,
    "venetian_agents_dealers_clerics_and_doctors_kept_earlier_painting_heritage_alive", 22, 22,
    "Haskell contrasts Armanni's awareness of new fashions with Venice's agents, dealers, minor clerics, and doctors, who had not yet needed to reject recent Venetian painting; he says Sasso admired the rich virtuosity of earlier eighteenth-century painters.",
    "Haskell", "authorial interpretation and report", "The social contrast and assessment are Haskell's framing; OCR joins the printed line-break hyphen in 'eighteenth-century'.",
    ["cand-10608", "cand-2719", "cand-2364"], body22,
    ocr_corrections=corrections_l22,
)
make_statement(
    "st-chp16-p374-canova-tiepolo-modello-rumour", BODY, "cand-0532", "cand-10610",
    "canova_requested_a_tiepolo_modello_and_a_false_rumour_said_sasso_bought_them_all", 22, 22,
    "Haskell says Canova wrote from Rome seeking a Tiepolo modello and was told that Sasso had bought them all; Haskell immediately says this was not true and interprets the rumour as reflecting Sasso's known taste.",
    "Haskell", "authorial report with explicit correction", "The alleged purchase is expressly denied by Haskell; only the request and circulation of the rumour are recorded.",
    ["cand-0532", "cand-4490", "cand-10608", "cand-10610", "cand-2364"], body22,
    relation_candidate=True,
    **{
        "footnote_marker": "4", "footnote_segment": NOTES, "footnote_line_range": "L75-L75",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L22", "footnote_note_statement_ids": [note4_id],
        "footnote_link_note": "Footnote 4 supplies the Haskell journal citation locator.",
    },
)
make_statement(
    "st-chp16-p374-sasso-posthumous-collection-partial", BODY, "cand-2364", "cand-10598",
    "posthumous_collection_included_tiepolo_pictures_a_copy_drawings_and_modelli_partial", 22, 22,
    "Haskell says the collection Sasso made for himself was auctioned after his death in 1803 and included works by Giambattista and Gian Domenico Tiepolo, one of Sasso's copies after one of them, 100 drawings, and modelli by Sebastiano Ricci and Pittoni; the list continues on p.375.",
    "Haskell", "authorial report", "The collection is linked to the small private collection introduced on p.373, but that identity remains subject to S3 alignment. Its contents and the copied work are not individually identified.",
    ["cand-2364", "cand-10598", "cand-2569", "cand-2624", "cand-10612", "cand-2154", "cand-1950"], body22,
    relation_candidate=True, predicate_status="partial", cross_reference_segments=[BODY_NEXT],
    cross_reference_text="P.374 L22 ends the list with modelli by Pittoni; p.375 L25 continues 'and Piazzetta' and adds drawings and sketches.",
    cross_reference_text_pending=True,
)

note1_link = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L72-L72",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L19", "footnote_note_statement_ids": [note1_id],
    "footnote_link_note": "Reference to further documentation of Guardi patronage.",
}
note2_link = {
    "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L73-L73",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L20", "footnote_note_statement_ids": [note2_id],
    "footnote_link_note": "Dated Strange-Sasso correspondence cited for the anecdote about the Tiepolo detail.",
}
note3_link = {
    "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L74-L74",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L21-L22", "footnote_note_statement_ids": note3_ids,
    "footnote_link_note": "Archive and auction-source references associated with Haskell's Armanni-Poore passage.",
}
note4_link = {
    "footnote_marker": "4", "footnote_segment": NOTES, "footnote_line_range": "L75-L75",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L22", "footnote_note_statement_ids": [note4_id],
    "footnote_link_note": "Haskell journal citation attached to the Canova-Tiepolo report.",
}
make_statement(
    note1_id, NOTES, "cand-1239", "cand-6004", "note_cites_haskell_references_on_guardi_patronage", 72, 72,
    "Haskell's note directs readers to his fuller references on Guardi patronage in the Journal of the Warburg Institute, 1960, pages 256-276.",
    "Haskell's note", "bibliographic citation", "The cited article/pages were not independently consulted.",
    ["cand-1239", "cand-6004"], note72, cited_source_independently_consulted=False,
    ocr_corrections=corrections_note72, **note1_link,
)
make_statement(
    note2_id, NOTES, "cand-10613", None, "note_locates_strange_sasso_correspondence_letter8", 73, 73,
    "Haskell's note identifies Letter 8 in the Strange-Sasso correspondence and dates it 22 December 1784.",
    "Haskell's note", "archival locator", "The note gives no repository or manuscript shelfmark; the letter was not consulted.",
    ["cand-10613"], note73, cited_source_independently_consulted=False, **note2_link,
)
make_statement(
    note3_ids[0], NOTES, "cand-10614", "cand-6589", "note_locates_armanni_sasso_letter_volumes_and_poore_letter", 74, 74,
    "Haskell's note locates two volumes of Armanni-Sasso letters in the Archivio of the Seminario Patriarcale, Venice, MSS. 565 and 566, and says Mr Poore is discussed in a letter of 7 July 1789.",
    "Haskell's note", "archival locator", "The manuscripts were not consulted; the note does not establish that the dated letter is the exact source of the p.374 quotation.",
    ["cand-10614", "cand-6589", "cand-0119", "cand-2364", "cand-10615", "cand-1973", "cand-2719"], note74,
    cited_source_independently_consulted=False, ocr_corrections=corrections_note74, **note3_link,
)
make_statement(
    note3_ids[1], NOTES, "cand-10616", "cand-1973", "note_reports_poore_print_and_drawing_sales_without_tiepolo", 74, 74,
    "Haskell's note reports two Richardson auctions on 4 and 19 April 1805 that sold prints and drawings belonging to Edward Poore, with no Tiepolo reference among them.",
    "Haskell's note", "auction locator", "The sales catalogues were not independently consulted; 'Richardson' is retained as the source's abbreviated locator.",
    ["cand-10616", "cand-1973", "cand-10608"], note74,
    cited_source_independently_consulted=False, **note3_link,
)
make_statement(
    note4_id, NOTES, "cand-6004", None, "note_cites_haskell_in_journal_of_warburg_institute_page276", 75, 75,
    "Haskell's note cites his Journal of Warburg Institute publication, 1960, page 276.",
    "Haskell's note", "bibliographic citation", "The cited page was not independently consulted.",
    ["cand-6004"], note75, cited_source_independently_consulted=False,
    ocr_corrections=corrections_note75, **note4_link,
)

previous_statement = next((row for row in statements if row["statement_id"] == "st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial"), None)
if not previous_statement:
    raise SystemExit("missing p.373 cross-page statement")
previous_qualifiers = previous_statement["qualifiers"]
if previous_qualifiers.get("predicate_status") != "partial" or BODY not in previous_qualifiers.get("cross_reference_segments", []):
    raise SystemExit("p.373 cross-page statement is not in the expected partial state")
previous_qualifiers["predicate_status"] = "complete"
previous_qualifiers["qualification"] = "P.374 L17 completes the painter list with Rosalba, Canaletto, and Tiepolo as less-frequent moderns; the p.373 source quotation remains anchored within its own segment."
previous_qualifiers["claim"] = "Haskell says Strange employed Sasso to buy Venetian pictures for him; p.374 completes the list of painters."
previous_qualifiers["cross_reference_text_pending"] = False
previous_qualifiers["cross_reference_statement_ids"] = ["st-chp16-p374-strange-pictures-list-and-custody"]

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L4-14",
    "note": "P.373 L14's unfinished list is closed by p.374 L17; source marker '[Page 2]' remains as transcribed, with print-page mapping documented.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L17-22",
    "note": "CHP-16.pdf physical page 2 is printed p.374. The Sasso collection list at L22 continues to p.375 L25; source OCR corrections are recorded in S2 only.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L70-75",
    "note": "P.373 notes 1-2 at L70-71 and p.374 notes 1-4 at L72-75 are migrated and linked; later notes in the merged segment remain pending.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp16-p374-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
        "new_statements": len(new_statement_ids), "completed_prior_statement": previous_statement["statement_id"],
        "coverage": {BODY_PREV: "reviewed/complete", BODY: "reviewed/partial", NOTES: "reviewed/partial"},
        "new_candidate_ids": [row[0] for row in new_candidates], "new_statement_ids": new_statement_ids,
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)

mentions.extend(planned_mentions)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({
    "mode": "applied", "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids), "completed_prior_statement": previous_statement["statement_id"],
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
