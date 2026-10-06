"""Controlled S2 migration for chapter 16's opening page and notes 1-2."""
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
TITLE = "chp-16:16_CHP-16_intro:l1-1"
BODY = "chp-16:16_CHP-16_intro:l3-14"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
BODY_NEXT = "chp-16:16_CHP-16_intro:l16-22"
BACKUP_SUFFIX = ".bak-s2-chp16-p373-sasso-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.373 S2 migration")
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
    3: "[Page 2]", 4: "Chapter 16", 5: "DEALERS AND PETITS BOURGEOIS",
    6: "E have seen", 7: "Wof the eighteenth", 8: "tbe taste",
    9: "Giovan Maria Sasso", 10: "survived the Republic", 11: "1803.",
    12: "John Strange", 13: "nearly twenty years", 14: "and",
    70: "Cicogna", 71: "Epistolario Moschini",
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
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (TITLE, BODY, NOTES, BODY_NEXT):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if (coverage_by_id[TITLE]["migration_status"] != "pending"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "pending"
        or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"):
    raise SystemExit("S2 coverage preconditions changed")
if any(row["segment_id"] in (TITLE, BODY, NOTES) for row in mentions):
    raise SystemExit("p.373 body or notes already have mention rows")
if any(row.get("statement_id", "").startswith("st-chp16-p373-") for row in statements):
    raise SystemExit("p.373 statements already exist")

new_candidates = [
    ("cand-10598", "Sasso's own small picture collection", "work", BODY, 9,
     "Haskell describes Sasso setting aside a small private collection alongside his dealing; its contents and later fate are not yet processed here."),
    ("cand-10599", "Unidentified portrait of Sasso by Alessandro Longhi", "work", NOTES, 70,
     "Haskell's note cites a portrait by Longhi; title, date, medium, and present location are not supplied."),
    ("cand-10600", "Cicogna (editor or annotator named in Haskell's p.373 note; identity unresolved)", "person", NOTES, 70,
     "Surname-only bibliographic reference; full identity and exact editorial role are not established in this note."),
    ("cand-10601", "Sasso, Osservazioni sopra i lavori a niello (1856 edition cited by Cicogna)", "archive", NOTES, 70,
     "Cited through Cicogna's footnote; the edition and text have not been independently consulted."),
    ("cand-10602", "Lorenzetti, 1914 (short-form biography citation; title unspecified)", "archive", NOTES, 70,
     "Haskell cites this for a short biography of Sasso; full publication details and text were not independently checked."),
    ("cand-10603", "Bollettino dei Musei Civici Veneziani, 1959, no. 2 (portrait citation)", "archive", NOTES, 70,
     "Haskell directs readers here for Longhi's portrait of Sasso; article title and page are not given."),
    ("cand-10604", "Letters from John Strange to Sasso cited in the Epistolario Moschini", "archive", NOTES, 71,
     "Haskell locates the letters in the Epistolario Moschini but supplies no dates or manuscript shelfmark here."),
    ("cand-10605", "Epistolario Moschini (manuscript collection at Biblioteca Correr)", "archive", NOTES, 71,
     "Named as the repository for letters from Strange to Sasso; exact collection scope and locator are not supplied."),
    ("cand-10606", "Mauroner, 1947, pp. 48-50 (quotations from Strange-Sasso letters)", "archive", NOTES, 71,
     "Short-form reference cited by Haskell for quotations from the letters; title and text were not independently checked."),
    ("cand-10607", "Four letters from Sasso to John Strange, British Museum Add. MSS. 23,730, ff. 359-363", "archive", NOTES, 71,
     "Haskell reports four surviving letters at this shelfmark; the manuscripts were not independently consulted."),
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

body_lines = {number: source_lines[number - 1] for number in range(3, 15)}
note_lines = {number: source_lines[number - 1] for number in range(69, 90)}
segment_lines = {BODY: body_lines, NOTES: note_lines}
segment_offsets = {}
for segment_id, lines in segment_lines.items():
    offset = 0
    segment_offsets[segment_id] = {}
    for number, line in lines.items():
        segment_offsets[segment_id][number] = offset
        offset += len(line) + 1

planned_mentions = []


def add_mention(candidate_id, surface, segment_id, source_line, note=""):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[segment_id][source_line]
    pos = line.find(surface)
    if pos < 0:
        raise SystemExit(f"surface not found at L{source_line}: {surface}")
    start = segment_offsets[segment_id][source_line] + pos
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == segment_id]
    if any(start < other_end and other_start < end for other_start, other_end in occupied):
        raise SystemExit(f"mention overlaps an existing span: {surface} at L{source_line}")
    mention_id = f"m-chp16-p373-sasso-{len(planned_mentions) + 1:04d}"
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    return mention_id


mention_specs = [
    ("cand-1416", "Carlo Lodoli", BODY, 7, ""),
    ("cand-0041", "Francesco Algarotti", BODY, 8, ""),
    ("cand-2719", "Venice", BODY, 7, ""),
    ("cand-1239", "Guardi", BODY, 8, "The printed name is Francesco Guardi; the OCR has stray punctuation around the surname."),
    ("cand-1002", "Farsetti", BODY, 8, ""),
    ("cand-1642", "Memmo", BODY, 8, ""),
    ("cand-2075", "Querini", BODY, 8, ""),
    ("cand-2364", "Giovan Maria Sasso", BODY, 9, "The text says Giovan Maria; the index candidate is Sasso, Giuseppe Maria. Preserve the name discrepancy for S3."),
    ("cand-10598", "a small collection", BODY, 9, ""),
    ("cand-2364", "Sasso", BODY, 10, ""),
    ("cand-8838", "Republic", BODY, 10, "Context indicates the Venetian political entity; keep it distinct from Venice as a city."),
    ("cand-9174", "British Residency", BODY, 12, ""),
    ("cand-2517", "John Strange", BODY, 12, ""),
    ("cand-2517", "Strange", BODY, 13, ""),
    ("cand-2367", "Sasso", BODY, 13, "Index sub-entry candidate for purchases of Venetian paintings for Strange; identity awaits S3."),
    ("cand-2364", "Sasso", NOTES, 70, ""),
    ("cand-10600", "Cicogna", NOTES, 70, ""),
    ("cand-10601", "Osservazioni sopra i lavori A niello", NOTES, 70, ""),
    ("cand-10602", "Lorenzetti, 1914", NOTES, 70, ""),
    ("cand-10599", "bis portrait", NOTES, 70, "S0 OCR reads 'bis'; the printed reading is 'his'."),
    ("cand-1426", "Alessandro Longhi", NOTES, 70, ""),
    ("cand-10603", "Bollettino dei Musei Civici Veneziani, 1959, No. 2", NOTES, 70, ""),
    ("cand-10604", "letters from Strange to Sasso", NOTES, 71, ""),
    ("cand-10605", "Epistolario Moschini", NOTES, 71, ""),
    ("cand-8262", "Biblioteca Cotter", NOTES, 71, "S0 OCR reads 'Cotter'; the printed repository name is Biblioteca Correr."),
    ("cand-10606", "Mauroner, 1947, pp. 48-50", NOTES, 71, ""),
    ("cand-2364", "Sasso’s replies", NOTES, 71, ""),
    ("cand-10607", "four letters from him to Strange", NOTES, 71, ""),
    ("cand-5986", "British Museum", NOTES, 71, ""),
    ("cand-10607", "Add. MSS. 23,730", NOTES, 71, ""),
]
for candidate_id, surface, segment_id, source_line, note in mention_specs:
    add_mention(candidate_id, surface, segment_id, source_line, note)


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, speaker, text_layer, qualification, mentioned_ids, quote,
                   relation_candidate=False, **extra_qualifiers):
    qualifiers = {
        "source_line_start": start_line,
        "source_line_end": end_line,
        "printed_page": 373,
        "pdf_physical_page": 1,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
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


body6, body7, body8 = source_lines[5], source_lines[6], source_lines[7]
body9, body10, body12, body13, body14 = source_lines[8], source_lines[9], source_lines[11], source_lines[12], source_lines[13]
note70, note71 = source_lines[69], source_lines[70]

dropcap_corrections = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 6,
     "ocr": "E have seen", "print": "We have seen",
     "basis": "CHP-16.pdf physical page 1; the initial W is a drop capital misplaced by OCR."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 7,
     "ocr": "Wof the eighteenth", "print": "of the eighteenth",
     "basis": "CHP-16.pdf physical page 1; the W belongs at the start of L6."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 7,
     "ocr": "die new ideas", "print": "the new ideas", "basis": "CHP-16.pdf physical page 1."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 8,
     "ocr": "tbe taste", "print": "the taste", "basis": "CHP-16.pdf physical page 1."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 8,
     "ocr": "Francesco \"Guardi,'was", "print": "Francesco Guardi, was", "basis": "CHP-16.pdf physical page 1."},
]
note2_corrections = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 12,
     "ocr": "termswith", "print": "terms with", "basis": "CHP-16.pdf physical page 1."},
]
note3_corrections = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 13,
     "ocr": "' for nearly twenty years.2", "print": "for nearly twenty years.^2",
     "basis": "CHP-16.pdf physical page 1; the note marker follows the sentence and is not an opening apostrophe."},
]
note70_corrections = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 70,
     "ocr": "bis portrait", "print": "his portrait", "basis": "CHP-16.pdf physical page 1."},
]
note71_corrections = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 71,
     "ocr": "Biblioteca Cotter", "print": "Biblioteca Correr", "basis": "CHP-16.pdf physical page 1."},
]

note1_ids = [
    "st-chp16-p373-note1-sasso-biography-citations",
    "st-chp16-p373-note1-longhi-portrait-reference",
]
note2_ids = [
    "st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
    "st-chp16-p373-note2-mauroner-quotes-letters",
    "st-chp16-p373-note2-sasso-replies-mostly-missing",
    "st-chp16-p373-note2-four-sasso-letters-british-museum",
]
footnote1_link = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L70-L70",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L10", "footnote_note_statement_ids": note1_ids,
    "footnote_link_note": "Note 1 supplies short biographical and portrait references for Sasso.",
}
footnote2_link = {
    "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L71-L71",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L12-L13", "footnote_note_statement_ids": note2_ids,
    "footnote_link_note": "Note 2 identifies the correspondence sources for the account of Strange and Sasso.",
}

make_statement(
    "st-chp16-p373-patronage-tastes-and-venetian-tradition", BODY, None, None,
    "new_patron_taste_differed_from_venetian_tradition_carried_by_guardi_and_lower_status_men", 6, 8,
    "Haskell contrasts patrons influenced by Lodoli and Algarotti with the Venetian painting tradition, which he says was carried on by lower-status figures and had Francesco Guardi as its last great master.",
    "Haskell", "authorial interpretation",
    "This is Haskell's periodization and evaluation of artistic taste, not an independent ranking of artists or patrons.",
    ["cand-1416", "cand-0041", "cand-1239"], body6 + "\n" + body7 + "\n" + body8,
    ocr_corrections=dropcap_corrections,
)
make_statement(
    "st-chp16-p373-dealers-perceived-as-agents-and-collectors", BODY, None, None,
    "dealers_seen_as_embassy_agents_but_formed_private_collections_with_distinct_taste", 8, 8,
    "Haskell says the men were viewed as dealers or agents helping foreign embassies plunder Venice, while they also assembled small personal collections with a distinctive taste that might appeal more than the spectacular patronage of Farsetti, Memmo, or Querini.",
    "Haskell", "authorial interpretation",
    "The plunder description is Haskell's account of how the men were viewed; the comparison with major patrons is his present-day evaluation.",
    ["cand-1002", "cand-1642", "cand-2075", "cand-2719"], body8,
)
make_statement(
    "st-chp16-p373-sasso-dealing-collection-and-writing", BODY, "cand-2364", "cand-10598",
    "dealt_in_pictures_while_collecting_corresponding_and_planning_unfinished_book", 9, 10,
    "Haskell describes Sasso buying and selling pictures, keeping a small collection, corresponding with friends and dealers, producing occasional pamphlets, and planning an uncompleted book on Venetian painting history.",
    "Haskell", "authorial report",
    "The proposed book was never completed; the source gives no title. S0 OCR reads the name as Giovan Maria Sasso, while the index candidate is Giuseppe Maria Sasso; identity and name form remain for S3.",
    ["cand-2364", "cand-10598", "cand-2719"], body9 + "\n" + body10,
    relation_candidate=True, **footnote1_link,
)
make_statement(
    "st-chp16-p373-sasso-survived-republic-and-died-1803", BODY, "cand-2364", "cand-8838",
    "survived_venetian_republic_and_died_in_1803", 10, 11,
    "Haskell says Sasso only just survived the Republic and died in 1803.",
    "Haskell", "authorial report",
    "The passage does not date the Republic's end; no date is inferred from it.",
    ["cand-2364", "cand-8838"], body10 + "\n" + source_lines[10],
)
make_statement(
    "st-chp16-p373-sasso-born-to-poor-parents-and-studied-painting", BODY, "cand-2364", None,
    "born_to_poor_parents_and_studied_painting_briefly", 12, 12,
    "Haskell says Sasso was born some sixty years earlier to poor parents and studied painting for a short time.",
    "Haskell", "authorial report",
    "The approximate wording is retained; no birth year is calculated.",
    ["cand-2364"], body12,
)
make_statement(
    "st-chp16-p373-sasso-contacted-british-residency-in-1774", BODY, "cand-2364", "cand-9174",
    "first_made_contact_with_british_residency_in_1774", 12, 12,
    "Haskell says Sasso's career changed in 1774 when he first made contact with the British Residency.",
    "Haskell", "authorial report",
    "The exact office and nature of the contact are not further specified here.",
    ["cand-2364", "cand-9174"], body12, relation_candidate=True,
)
make_statement(
    "st-chp16-p373-strange-new-occupant-of-residency", BODY, "cand-2517", "cand-9174",
    "john_strange_was_new_occupant_of_british_residency_post", 12, 12,
    "Haskell identifies John Strange as the new occupant of the British Residency post when Sasso first made contact in 1774.",
    "Haskell", "authorial report",
    "This records the office named in the source; it does not independently establish appointment dates.",
    ["cand-2517", "cand-9174"], body12, relation_candidate=True,
    ocr_corrections=note2_corrections,
)
make_statement(
    "st-chp16-p373-strange-and-sasso-corresponded-nearly-twenty-years", BODY, "cand-2364", "cand-2517",
    "met_and_corresponded_for_nearly_twenty_years", 12, 13,
    "Haskell says Sasso and Strange soon became close, saw each other, and corresponded for nearly twenty years.",
    "Haskell", "authorial report",
    "The approximate duration is kept as stated; the footnote supplies archival references but was not independently checked.",
    ["cand-2364", "cand-2517"], body12 + "\n" + body13,
    relation_candidate=True, ocr_corrections=note3_corrections, **footnote2_link,
)
make_statement(
    "st-chp16-p373-strange-and-sasso-shared-complaints-and-business", BODY, "cand-2364", "cand-2517",
    "exchanged_complaints_condolences_gossip_and_lucrative_business", 13, 13,
    "Haskell reports that Sasso and Strange complained about social changes, consoled each other in losses and illness, exchanged gossip, and did lucrative business together.",
    "Haskell", "authorial report",
    "The quoted complaints are reported collectively; no individual letter or speaker is identified here.",
    ["cand-2364", "cand-2517"], body13, relation_candidate=True,
)
make_statement(
    "st-chp16-p373-strange-employed-sasso-to-buy-pictures-partial", BODY, "cand-2517", "cand-2367",
    "employed_sasso_to_buy_venetian_pictures_for_strange_partial", 13, 14,
    "Haskell says Strange employed Sasso to buy Venetian pictures for him; the list of painters continues onto p.374.",
    "Haskell", "authorial report",
    "The sentence is incomplete at p.373 L14 and continues in the next segment; retain the purchase role without inferring the complete list.",
    ["cand-2517", "cand-2367"], body13 + "\n" + body14,
    relation_candidate=True, predicate_status="partial", cross_reference_segments=[BODY_NEXT],
    cross_reference_text="P.373 L14 ends with 'and'; p.374 L17 continues the list of pictures Strange employed Sasso to buy.",
    cross_reference_text_pending=True,
)

note1_shared = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L70-L70",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L10", "footnote_note_statement_ids": note1_ids,
    "footnote_link_note": "The note gives biographical and portrait-source references for Sasso.",
}
note2_shared = {
    "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L71-L71",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L12-L13", "footnote_note_statement_ids": note2_ids,
    "footnote_link_note": "The note identifies the correspondence sources behind Haskell's account of Strange and Sasso.",
}
make_statement(
    note1_ids[0], NOTES, "cand-2364", "cand-10601", "note_cites_cicogna_and_lorenzetti_for_sasso_biography", 70, 70,
    "Haskell's note points to Cicogna's footnote to his 1856 edition of Sasso's Osservazioni sopra i lavori a niello and to Lorenzetti, 1914, for a short biography.",
    "Haskell's note", "bibliographic citation",
    "The cited edition and Lorenzetti reference were not independently consulted; the latter is short-form and its title is unspecified.",
    ["cand-2364", "cand-10600", "cand-10601", "cand-10602"], note70,
    cited_source_independently_consulted=False, **note1_shared,
)
make_statement(
    note1_ids[1], NOTES, "cand-2364", "cand-10599", "note_cites_longhi_portrait_in_bollettino", 70, 70,
    "Haskell's note identifies a portrait of Sasso by Alessandro Longhi and directs readers to Bollettino dei Musei Civici Veneziani, 1959, no. 2.",
    "Haskell's note", "bibliographic citation and artwork reference",
    "The portrait's title, date, medium, and present location are not supplied; the periodical reference was not independently checked.",
    ["cand-2364", "cand-10599", "cand-1426", "cand-10603"], note70,
    relation_candidate=True, cited_source_independently_consulted=False,
    ocr_corrections=note70_corrections, **note1_shared,
)
make_statement(
    note2_ids[0], NOTES, "cand-10604", "cand-10605", "letters_from_strange_to_sasso_preserved_in_epistolario_moschini", 71, 71,
    "Haskell says letters from Strange to Sasso are in the Epistolario Moschini at Biblioteca Correr in Venice.",
    "Haskell's note", "archival locator",
    "No letter dates or manuscript shelfmark are supplied in this note; the collection was not consulted.",
    ["cand-2517", "cand-2364", "cand-10604", "cand-10605", "cand-8262"], note71,
    relation_candidate=True, cited_source_independently_consulted=False,
    ocr_corrections=note71_corrections, **note2_shared,
)
make_statement(
    note2_ids[1], NOTES, "cand-10606", "cand-10604", "mauroner_quotes_strange_sasso_letters", 71, 71,
    "Haskell says quotations from the Strange-Sasso letters appear in Mauroner, 1947, pages 48-50.",
    "Haskell's note", "secondary citation",
    "Mauroner's publication and the quoted letters were not independently consulted.",
    ["cand-10606", "cand-10604", "cand-2517", "cand-2364"], note71,
    relation_candidate=True, cited_source_independently_consulted=False, **note2_shared,
)
make_statement(
    note2_ids[2], NOTES, "cand-2364", None, "sasso_replies_to_strange_mostly_missing", 71, 71,
    "Haskell says Sasso's replies are mostly missing.",
    "Haskell's note", "archival condition report",
    "The note does not say how many replies are missing or identify which survive beyond the four letters cited next.",
    ["cand-2364", "cand-2517"], note71, **note2_shared,
)
make_statement(
    note2_ids[3], NOTES, "cand-10607", "cand-5986", "four_sasso_letters_to_strange_at_british_museum_shelfmark", 71, 71,
    "Haskell says four letters from Sasso to Strange are at the British Museum, Add. MSS. 23,730, folios 359-363.",
    "Haskell's note", "archival locator",
    "The manuscripts were not independently consulted; the shelfmark and count are recorded as Haskell reports them.",
    ["cand-2364", "cand-2517", "cand-10607", "cand-5986"], note71,
    relation_candidate=True, cited_source_independently_consulted=False, **note2_shared,
)

coverage_by_id[TITLE].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "L1-1",
    "note": "Excluded: generated Markdown filename heading only; it is not printed book content. The chapter title and text appear in the next source segment.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L4-14",
    "note": "CHP-16.pdf physical page 1 is the chapter opening; continuous print order places it at p.373 because the preceding page is p.372 and the next page is printed p.374. S0 marker '[Page 2]' is retained without correction. OCR drop-cap and spacing corrections are recorded in S2 only. P.373 L14 continues to p.374 L17.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L70-71",
    "note": "P.373 footnotes 1-2 at L70-71 are migrated and linked to the opening-page statements; later notes in the merged segment remain pending.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp16-p373-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
        "new_statements": len(new_statement_ids),
        "coverage": {TITLE: "excluded/complete", BODY: "reviewed/partial", NOTES: "reviewed/partial"},
        "new_candidate_ids": [row[0] for row in new_candidates],
        "new_statement_ids": new_statement_ids,
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
    "new_statements": len(new_statement_ids),
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
