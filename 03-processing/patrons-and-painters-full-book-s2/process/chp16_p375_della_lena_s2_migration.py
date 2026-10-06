"""Controlled S2 migration for chapter 16 p.375 and footnotes 1-6."""
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
BODY_PREV = "chp-16:16_CHP-16_intro:l16-22"
BODY = "chp-16:16_CHP-16_intro:l24-36"
BODY_NEXT = "chp-16:16_CHP-16_intro:l38-46"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
BACKUP_SUFFIX = ".bak-s2-chp16-p375-della-lena-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.375 S2 migration")
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
    24: "[Page 375]", 25: "and Piazzetta; drawings and sketches",
    26: "letter of introduction to Sasso", 27: "Sir Richard Worsley",
    28: "no English dealer in Venice", 29: "-masterpieces",
    30: "Abate Giacomo della Lena", 31: "Medici to his own contemporaries",
    32: "-Spanish Ambassador’s doctor", 33: "thirty-two paintings by Francesco Guardi",
    34: "Maria Ortes.6", 35: ". while the value of the Sciences",
    36: "- It was only",
    76: "Catalog de quadri", 77: "Letter 57", 78: "A. Hume",
    79: "Journal of Warburg Institute", 80: "Raccolta Cicogna 3006/9",
    81: "14 January 1786",
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
        or coverage_by_id[NOTES]["source_line_ranges"] != "L70-75"):
    raise SystemExit("S2 coverage preconditions changed")
if any(row["segment_id"] == BODY for row in mentions):
    raise SystemExit("p.375 body already has mention rows")
if any(row.get("statement_id", "").startswith("st-chp16-p375-") for row in statements):
    raise SystemExit("p.375 statements already exist")

body_lines = {number: source_lines[number - 1] for number in range(24, 37)}
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
    ("cand-10618", "Catalogo de' quadri del q. Giammaria Sasso, che si mettono all'incanto nella sua casa al ponte di Cannareggio, n. 381", "archive", NOTES, 76,
     "Haskell says this sale catalogue documents Sasso's collection; cited copies are at Biblioteca Civica, Padua and Accademia Carrara, Bergamo. The catalogue was not consulted."),
    ("cand-10619", "Biblioteca Civica, Padua", "institution", NOTES, 76,
     "Named by Haskell as holding a copy of the Sasso sale catalogue; the institution's catalogue was not checked."),
    ("cand-10620", "Accademia Carrara, Bergamo", "institution", NOTES, 76,
     "Named by Haskell as holding a copy of the Sasso sale catalogue; the institution's catalogue was not checked."),
    ("cand-10621", "Lugt sales-catalogue reference cited for the Sasso collection catalogue (work unspecified)", "archive", NOTES, 76,
     "The note says the Sasso catalogue is not recorded by Lugt but gives no title, edition, or fuller bibliographic details."),
    ("cand-10622", "The Spoliation of Pictures from Venice (account by Giacomo della Lena; title as cited by Haskell)", "archive", BODY, 30,
     "Haskell reports that Della Lena wrote this account; the work itself and the exact title were not independently checked."),
    ("cand-10623", "Thirty-two paintings by Francesco Guardi in Giacomo della Lena's collection", "work", BODY, 33,
     "The source gives the count and artist but no individual titles or present locations."),
    ("cand-10624", "Letter from Giacomo della Lena to Giuseppe Maria Ortes, 14 January 1786 (Biblioteca Correr, Cod. Cicogna 3198)", "archive", NOTES, 81,
     "Haskell gives this date and shelfmark; the manuscript was not consulted."),
    ("cand-10625", "Biblioteca Correr, MSS. Raccolta Cicogna 3006/9 and other versions cited for Della Lena's account", "archive", NOTES, 80,
     "The shelfmark and alternative versions are reported by Haskell; they were not checked."),
    ("cand-10626", "Strange-Sasso correspondence, Letter 57, dated 3 October 1793", "archive", NOTES, 77,
     "Haskell gives the letter number and date but no repository or shelfmark here; the letter was not consulted."),
    ("cand-10627", "Unidentified Spanish Ambassador in Venice, whose doctor was Innocenzo della Lena", "person", BODY, 32,
     "The officeholder is unnamed. Do not merge with other unidentified Spanish ambassadors in the candidate table."),
    ("cand-10628", "One Guardi painting and seven Guardi drawings in Sasso's auctioned collection", "work", BODY, 25,
     "Haskell gives the artist and counts but no titles, dates, or present locations."),
    ("cand-10629", "Haskell, Journal of Warburg Institute, 1960, pp. 261-2 (article title unspecified)", "archive", NOTES, 79,
     "The note cites Haskell and pages 261-2 in the Journal of Warburg Institute; the article title and full publication details are not supplied here."),
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
    for other_start, other_end in occupied:
        overlaps = start < other_end and other_start < end
        nested = ((start <= other_start and other_end <= end)
                  or (other_start <= start and end <= other_end))
        if overlaps and (not nested or (start, end) == (other_start, other_end)):
            raise SystemExit(f"mention has duplicate or crossing span: {surface} at L{source_line}")
    mention_id = f"m-chp16-p375-della-lena-{len(planned_mentions) + 1:04d}"
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


mention_specs = [
    ("cand-1901", "Piazzetta", BODY, 25, "Index candidate is Giovanni Battista Piazzetta.", 0),
    ("cand-0498", "Canaletto", BODY, 25, "", 0),
    ("cand-0554", "Carlevarijs", BODY, 25, "Index candidate is Luca Carlevarijs.", 0),
    ("cand-1239", "Guardi", BODY, 25, "", 0),
    ("cand-2517", "Strange", BODY, 26, "", 0),
    ("cand-2364", "Sasso", BODY, 26, "", 0),
    ("cand-2819", "Richard Worsley", BODY, 27, "", 0),
    ("cand-2364", "Sasso", BODY, 27, "", 0),
    ("cand-2819", "Sir Richard Worsley", BODY, 27, "", 0),
    ("cand-1239", "Guardi", BODY, 27, "", 0),
    ("cand-1812", "Lady", BODY, 27, "Name split across source lines.", 0),
    ("cand-1812", "Palmerston", BODY, 28, "Continuation of the name across the OCR line break.", 0),
    ("cand-2719", "Venice", BODY, 28, "", 0),
    ("cand-2364", "Sasso", BODY, 28, "", 0),
    ("cand-2364", "Sasso", BODY, 30, "", 0),
    ("cand-1387", "Abate Giacomo della Lena", BODY, 30, "Uses the existing main S1 index entry; the Guardi subentry remains a separate index record.", 0),
    ("cand-1709", "Abate G. A. Moschini", BODY, 30, "", 0),
    ("cand-10622", "Spoliation of Pictures from Venice", BODY, 30, "The account's title and authorship are reported by Haskell.", 0),
    ("cand-1629", "Cardinal Leopold de’", BODY, 30, "Index candidate uses the Italian form 'Leopoldo'.", 0),
    ("cand-1629", "Medici", BODY, 31, "Continuation of the name across the OCR line break.", 0),
    ("cand-1387", "Della Lena", BODY, 31, "", 0),
    ("cand-1454", "Lucca", BODY, 31, "", 0),
    ("cand-2719", "Venice", BODY, 31, "", 0),
    ("cand-1389", "Innocenzo", BODY, 31, "Index candidate is Innocenzo della Lena.", 0),
    ("cand-10627", "Spanish Ambassador", BODY, 32, "Unnamed officeholder; not identified with other Spanish ambassadors.", 0),
    ("cand-1386", "Eusebio", BODY, 32, "Index candidate is Eusebio della Lena.", 0),
    ("cand-0591", "Casanova", BODY, 32, "", 0),
    ("cand-1387", "Della Lena", BODY, 33, "", 0),
    ("cand-2364", "Sasso", BODY, 33, "", 0),
    ("cand-0498", "Canalettos", BODY, 33, "Plural source form linked to the artist candidate.", 0),
    ("cand-10623", "thirty-two paintings", BODY, 33, "The source gives this count for Guardi's paintings in Della Lena's collection.", 0),
    ("cand-1239", "Francesco Guardi", BODY, 33, "", 0),
    ("cand-1387", "della Lena", BODY, 33, "", 0),
    ("cand-1789", "Giuseppe", BODY, 33, "First part of the name split across source lines.", 0),
    ("cand-1789", "Maria Ortes", BODY, 34, "Continuation of Giuseppe Maria Ortes across the OCR line break.", 0),
    ("cand-1239", "Francesco Guardi", BODY, 36, "", 0),
    ("cand-2364", "Sasso’s collection", NOTES, 76, "", 0),
    ("cand-10618", "Catalog de quadri del q. Giammaria Sasso, che si mettono all'incanto nella sua casa al ponte di Cannareggio, n.381", NOTES, 76,
     "S0 omits the printed 'o' and apostrophe in 'Catalogo de' quadri' and lacks the space in 'n. 381'.", 0),
    ("cand-10621", "Lugt", NOTES, 76, "The note does not identify which Lugt repertory is meant.", 0),
    ("cand-10619", "Biblioteca Civica", NOTES, 76, "", 0),
    ("cand-1803", "Padua", NOTES, 76, "", 0),
    ("cand-10620", "Accademia Carrara", NOTES, 76, "", 0),
    ("cand-7743", "Bergamo", NOTES, 76, "", 0),
    ("cand-10626", "Strange-Sasso correspondence", NOTES, 77, "", 0),
    ("cand-10626", "Letter 57", NOTES, 77, "", 0),
    ("cand-1308", "A. Hume", NOTES, 78, "", 0),
    ("cand-10602", "Lorenzetti, 1914", NOTES, 78, "Reuses the short-form 1914 bibliography candidate; publication not independently checked.", 0),
    ("cand-2437", "John Skippe", NOTES, 78, "", 0),
    ("cand-0946", "Hamilton, Marquis of Douglas", NOTES, 78, "", 0),
    ("cand-10605", "Epistolario Moschini", NOTES, 78, "", 0),
    ("cand-8262", "Biblioteca Correr", NOTES, 78, "", 0),
    ("cand-2719", "Venice", NOTES, 78, "", 0),
    ("cand-6004", "Journal of Warburg Institute", NOTES, 79, "Journal title as transcribed in S0.", 0),
    ("cand-10629", "Haskell, in Journal of Warburg Institute, i960, pp. 261-2", NOTES, 79,
     "Specific bibliographic locator; article title is not supplied by the note.", 0),
    ("cand-3770", "Haskell", NOTES, 79, "Author named within the bibliographic locator.", 0),
    ("cand-8262", "Biblioteca Correr", NOTES, 80, "", 0),
    ("cand-10625", "MSS. Raccolta Cicogna 3006/9", NOTES, 80, "", 0),
    ("cand-9424", "Haskell, 1967", NOTES, 80, "Reuses the unresolved Haskell 1967 citation candidate; exact work remains unspecified.", 0),
    ("cand-3770", "Haskell", NOTES, 80, "Author named within the bibliographic locator.", 0),
    ("cand-8262", "Biblioteca Correr", NOTES, 81, "", 0),
    ("cand-10624", "14 January 1786", NOTES, 81, "", 0),
    ("cand-10624", "MSS. Cod. Cicogna, 3198", NOTES, 81, "", 0),
]
for candidate_id, surface, segment_id, source_line, note, occurrence in mention_specs:
    add_mention(candidate_id, surface, segment_id, source_line, note, occurrence)

body25, body26, body27, body28 = source_lines[24], source_lines[25], source_lines[26], source_lines[27]
body29, body30, body31, body32 = source_lines[28], source_lines[29], source_lines[30], source_lines[31]
body33, body34, body35, body36 = source_lines[32], source_lines[33], source_lines[34], source_lines[35]
note76, note77, note78, note79, note80, note81 = [source_lines[n - 1] for n in range(76, 82)]

corrections_l29 = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 29,
     "ocr": "-masterpieces", "print": "masterpieces", "basis": "CHP-16.pdf physical page 3; the printed line begins 'masterpieces' without a lexical hyphen."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 29,
     "ocr": "3 '", "print": "3", "basis": "CHP-16.pdf physical page 3; the footnote marker is followed by no apostrophe."},
]
corrections_l32 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 32,
    "ocr": "-Spanish Ambassador’s doctor", "print": "Spanish Ambassador’s doctor",
    "basis": "CHP-16.pdf physical page 3; the leading mark is not sentence punctuation or a compound hyphen.",
}]
corrections_l35 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 35,
    "ocr": ". while", "print": "while", "basis": "CHP-16.pdf physical page 3; the semicolon at the end of L34 governs the continuation."},
]
corrections_l36 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 36,
    "ocr": "- It was", "print": "It was", "basis": "CHP-16.pdf physical page 3; the leading dash is an OCR artifact."},
]
corrections_note76 = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 76,
     "ocr": "Catalog de quadri", "print": "Catalogo de' quadri", "basis": "CHP-16.pdf physical page 3."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 76,
     "ocr": "n.381", "print": "n. 381", "basis": "CHP-16.pdf physical page 3."},
]
corrections_note79 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 79,
    "ocr": "i960", "print": "1960", "basis": "CHP-16.pdf physical page 3."},
]

note1_id = "st-chp16-p375-note1-sasso-sale-catalog"
note2_id = "st-chp16-p375-note2-strange-sasso-letter57"
note3_id = "st-chp16-p375-note3-sasso-correspondents"
note4_id = "st-chp16-p375-note4-haskell-journal"
note5_id = "st-chp16-p375-note5-della-lena-account-manuscript"
note6_id = "st-chp16-p375-note6-della-lena-ortes-letter"


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, speaker, text_layer, qualification, mentioned_ids, quote,
                   relation_candidate=False, **extra_qualifiers):
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 375, "pdf_physical_page": 3, "claim": claim,
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


collection_link = {
    "cross_reference_segments": [BODY_PREV],
    "cross_reference_statement_ids": ["st-chp16-p374-sasso-posthumous-collection-partial"],
    "cross_reference_text": "P.374 L22 leaves the Sasso collection list open; p.375 L25 adds Piazzetta, Canaletto, Carlevarijs, and Guardi.",
    "cross_reference_text_pending": False,
}
note1_body_link = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L76-L76",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L25", "footnote_note_statement_ids": [note1_id],
    "footnote_link_note": "The catalog note documents the collection whose p.374 list is completed here.",
}
make_statement(
    "st-chp16-p375-sasso-collection-list-completion", BODY, "cand-2364", "cand-10598",
    "auctioned_collection_list_continues_with_piazzetta_canaletto_carlevarijs_and_guardi", 25, 25,
    "Haskell completes the list of Sasso's auctioned collection: it included a modello by Piazzetta, drawings and sketches by Canaletto and Carlevarijs, and one painting plus seven drawings by Guardi.",
    "Haskell", "authorial report", "The specific works, their titles, and present locations are not given.",
    ["cand-2364", "cand-10598", "cand-1901", "cand-0498", "cand-0554", "cand-1239", "cand-10628"], body25,
    relation_candidate=True, **collection_link, **note1_body_link,
)
make_statement(
    "st-chp16-p375-strange-introduces-worsley-to-sasso", BODY, "cand-2517", "cand-2819",
    "provided_letter_introducing_successor_richard_worsley_to_sasso", 26, 27,
    "Haskell says that after leaving, Strange gave Sasso a letter introducing his successor Sir Richard Worsley, and quotes Strange praising Sasso's love of art and ability to find fine works.",
    "John Strange, as quoted by Haskell", "authorial report with embedded quotation", "The statement reports what the letter says through Haskell; the letter itself was not consulted.",
    ["cand-2517", "cand-2364", "cand-2819"], body26 + "\n" + body27,
    relation_candidate=True,
    **{
        "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L77-L77",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L26-L27", "footnote_note_statement_ids": [note2_id],
        "footnote_link_note": "Footnote 2 identifies the Strange-Sasso correspondence letter and date.",
    },
)
make_statement(
    "st-chp16-p375-sasso-finds-works-for-worsley", BODY, "cand-2364", "cand-2819",
    "found_more_artworks_for_worsley_after_stranges_introduction", 27, 28,
    "Haskell says Sasso found more works for Worsley, who soon presented a Guardi to Lady Palmerston.",
    "Haskell", "authorial report", "The Guardi work presented to Lady Palmerston is not identified by title or date.",
    ["cand-2364", "cand-2819", "cand-1239", "cand-1812"], body27 + "\n" + body28,
    relation_candidate=True,
)
make_statement(
    "st-chp16-p375-sasso-reputation-and-removal-of-masterpieces", BODY, "cand-2364", None,
    "english_dealers_relied_on_sasso_and_his_work_contributed_to_removal_of_venetian_masterpieces", 28, 29,
    "Haskell says English dealers in Venice relied on Sasso's trustworthiness and expertise, which he describes as responsible for removing many masterpieces from the city in the late eighteenth century.",
    "Haskell", "authorial interpretation and report", "The wording 'stripping the city' is Haskell's critical framing; no specific works or transactions are identified here.",
    ["cand-2719", "cand-2364"], body28 + "\n" + body29,
    relation_candidate=True, ocr_corrections=corrections_l29,
    **{
        "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L78-L78",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L28-L29", "footnote_note_statement_ids": [note3_id],
        "footnote_link_note": "Footnote 3 names several people in Sasso's network and gives related letter sources.",
    },
)
make_statement(
    "st-chp16-p375-della-lena-dealers-and-scholarship", BODY, None, "cand-1387",
    "venetian_dealers_kept_colour_and_fantasy_alive_and_della_lena_touched_scholarship", 30, 30,
    "Haskell says the tastes of Sasso and similar dealers helped keep colour and fantasy alive in Venetian art, and places Abate Giacomo della Lena on the fringes of scholarship.",
    "Haskell", "authorial interpretation", "This characterizes a group and Della Lena's scholarly position; it does not imply formal scholarly office.",
    ["cand-2364", "cand-1387", "cand-2719"], body30,
    **{
        "footnote_marker": "4", "footnote_segment": NOTES, "footnote_line_range": "L79-L79",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L30", "footnote_note_statement_ids": [note4_id],
        "footnote_link_note": "Footnote 4 provides a Haskell journal citation locator.",
    },
)
make_statement(
    "st-chp16-p375-della-lena-moschini-friendship-and-records", BODY, "cand-1387", "cand-1709",
    "close_friend_of_moschini_who_saved_venetian_records", 30, 30,
    "Haskell says Della Lena was a close friend of Abate G. A. Moschini, an antiquarian who saved many Venetian records from destruction.",
    "Haskell", "authorial report", "The passage does not name the records or identify particular acts of preservation.",
    ["cand-1387", "cand-1709", "cand-2719"], body30, relation_candidate=True,
)
make_statement(
    "st-chp16-p375-della-lena-spoliation-account", BODY, "cand-1387", "cand-10622",
    "wrote_account_on_spoliation_of_pictures_from_venice", 30, 31,
    "Haskell says Della Lena wrote an account titled 'Spoliation of Pictures from Venice' about collectors who removed pictures from Venice, from Cardinal Leopold de' Medici to Della Lena's contemporaries.",
    "Haskell", "authorial report", "The title and contents are recorded as Haskell reports them; the account was not independently consulted.",
    ["cand-1387", "cand-10622", "cand-1629", "cand-2719"], body30 + "\n" + body31,
    relation_candidate=True,
    **{
        "footnote_marker": "5", "footnote_segment": NOTES, "footnote_line_range": "L80-L80",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L30-L31", "footnote_note_statement_ids": [note5_id],
        "footnote_link_note": "Footnote 5 gives a Biblioteca Correr manuscript locator and a Haskell 1967 reference.",
    },
)
make_statement(
    "st-chp16-p375-historian-della-lena-german-dealings", BODY, "cand-1387", None,
    "nineteenth_century_historian_said_della_lena_was_well_placed_to_write_and_dealt_with_germans", 31, 31,
    "Haskell relays an unnamed nineteenth-century historian's comment that Della Lena was well qualified to write about picture removals because he was deeply involved in picture dealing, mainly with Germans.",
    "Unnamed nineteenth-century historian, as reported by Haskell", "reported commentary", "The historian and cited wording are not identified more fully.",
    ["cand-1387"], body31,
)
make_statement(
    "st-chp16-p375-della-lena-life-and-venice-office", BODY, "cand-1387", "cand-2719",
    "born_in_lucca_1732_lived_in_venice_and_acted_as_spanish_vice_consul_until_death_1807", 31, 31,
    "Haskell says Della Lena was born in Lucca in 1732, spent most of his life in Venice, acted there as Spanish vice-consul, and died in 1807.",
    "Haskell", "authorial report", "The appointment's dates and circumstances are not supplied; the Spanish vice-consul is recorded as a role, not as a separate officeholder.",
    ["cand-1387", "cand-1454", "cand-2719"], body31,
)
make_statement(
    "st-chp16-p375-della-lena-brothers-and-casanova", BODY, "cand-1387", None,
    "brother_innocenzo_served_spanish_ambassador_and_brother_eusebio_knew_casanova", 31, 32,
    "Haskell says Della Lena probably owed his vice-consular job to his brother Innocenzo, doctor to the Spanish Ambassador, while another brother Eusebio was a friend of Casanova.",
    "Haskell", "authorial report", "The causal wording is expressly probable; the ambassador is unnamed and is not identified with another Spanish ambassador candidate.",
    ["cand-1387", "cand-1389", "cand-10627", "cand-1386", "cand-0591"], body31 + "\n" + body32,
    ocr_corrections=corrections_l32, relation_candidate=True,
)
make_statement(
    "st-chp16-p375-della-lena-private-collection-and-guardi-paintings", BODY, "cand-1387", "cand-10623",
    "collected_pictures_including_thirty_two_guardi_paintings", 33, 33,
    "Haskell says Della Lena collected pictures on a modest scale, including a few Canaletto works, pieces by minor contemporaries, and thirty-two paintings by Francesco Guardi.",
    "Haskell", "authorial report", "The individual pictures and the other contemporaries are not named.",
    ["cand-1387", "cand-2364", "cand-0498", "cand-10623", "cand-1239"], body33,
    relation_candidate=True,
)
make_statement(
    "st-chp16-p375-della-lena-letter-to-ortes", BODY, "cand-1387", "cand-1789",
    "wrote_letter_to_economist_giuseppe_maria_ortes_about_guardi", 33, 34,
    "Haskell says Della Lena's enthusiasm for Guardi is explained in a letter he wrote to economist Giuseppe Maria Ortes.",
    "Haskell", "authorial report", "The letter is dated and located only in footnote 6; it was not independently consulted.",
    ["cand-1387", "cand-1239", "cand-1789"], body33 + "\n" + body34,
    relation_candidate=True,
    **{
        "footnote_marker": "6", "footnote_segment": NOTES, "footnote_line_range": "L81-L81",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L33-L34", "footnote_note_statement_ids": [note6_id],
        "footnote_link_note": "Footnote 6 dates and locates the letter mentioned here.",
    },
)
make_statement(
    "st-chp16-p375-della-lena-arts-and-sciences-theory", BODY, "cand-1387", None,
    "said_fantasy_precedes_intellect_and_artistic_truth_serves_falsehood", 34, 35,
    "In the passage Haskell attributes to Della Lena, the arts differ from sciences: fantasy should dominate intellect, truth serve falsehood, and artistic value remain indirect and unformulated, while scientific value is clear and complete.",
    "Della Lena, as quoted by Haskell", "embedded quotation", "The wording is a reported aesthetic theory, not a factual claim; OCR's leading period before 'while' is removed in the S2 print reading.",
    ["cand-1387"], body34 + "\n" + body35, ocr_corrections=corrections_l35,
    **{
        "footnote_marker": "6", "footnote_segment": NOTES, "footnote_line_range": "L81-L81",
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": "L34-L35", "footnote_note_statement_ids": [note6_id],
        "footnote_link_note": "Footnote 6 locates the 14 January 1786 letter in Biblioteca Correr, Cod. Cicogna 3198.",
    },
)
make_statement(
    "st-chp16-p375-guardi-flourishes-in-della-lena-world", BODY, "cand-1239", None,
    "flourished_in_atmosphere_that_tolerated_disregard_for_literal_truth", 36, 36,
    "Haskell concludes that an atmosphere receptive to fantasy allowed Guardi to flourish, in contrast with English viewers who demanded clear, literal renderings.",
    "Haskell", "authorial interpretation", "This is Haskell's aesthetic explanation; it does not attribute one uniform view to every English viewer.",
    ["cand-1239"], body36, ocr_corrections=corrections_l36,
)

note1_link = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L76-L76",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L25", "footnote_note_statement_ids": [note1_id],
    "footnote_link_note": "Sale-catalogue citation and copy locations for Sasso's collection.",
}
note2_link = {
    "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L77-L77",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L26-L27", "footnote_note_statement_ids": [note2_id],
    "footnote_link_note": "Dated correspondence locator for Strange's letter of introduction.",
}
note3_link = {
    "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L78-L78",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L28-L29", "footnote_note_statement_ids": [note3_id],
    "footnote_link_note": "Names several people in Sasso's circle and identifies letter sources.",
}
note4_link = {
    "footnote_marker": "4", "footnote_segment": NOTES, "footnote_line_range": "L79-L79",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L30", "footnote_note_statement_ids": [note4_id],
    "footnote_link_note": "Haskell journal reference attached to the scholarship characterization.",
}
note5_link = {
    "footnote_marker": "5", "footnote_segment": NOTES, "footnote_line_range": "L80-L80",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L30-L31", "footnote_note_statement_ids": [note5_id],
    "footnote_link_note": "Manuscript locator for Della Lena's account.",
}
note6_link = {
    "footnote_marker": "6", "footnote_segment": NOTES, "footnote_line_range": "L81-L81",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L34-L35", "footnote_note_statement_ids": [note6_id],
    "footnote_link_note": "Dated manuscript locator for the Della Lena-Ortes letter.",
}
make_statement(
    note1_id, NOTES, "cand-10618", "cand-10598", "note_cites_sasso_sale_catalogue_and_two_copy_locations", 76, 76,
    "Haskell says Sasso's collection is documented in the sale catalogue Catalogo de' quadri del q. Giammaria Sasso, n. 381, not recorded by Lugt, with copies at Biblioteca Civica, Padua and Accademia Carrara, Bergamo.",
    "Haskell's note", "catalogue citation and repository locator", "The catalogue and the cited copies were not independently checked; Lugt's reference is not fully identified.",
    ["cand-10618", "cand-10598", "cand-10621", "cand-10619", "cand-1803", "cand-10620", "cand-7743"], note76,
    cited_source_independently_consulted=False, ocr_corrections=corrections_note76, **note1_link,
)
make_statement(
    note2_id, NOTES, "cand-10626", None, "note_dates_strange_sasso_correspondence_letter57", 77, 77,
    "Haskell's note identifies Letter 57 in the Strange-Sasso correspondence and dates it 3 October 1793.",
    "Haskell's note", "archival locator", "The repository and shelfmark are not supplied; the letter was not consulted.",
    ["cand-10626"], note77, cited_source_independently_consulted=False, **note2_link,
)
make_statement(
    note3_id, NOTES, "cand-2364", None, "note_names_sasso_correspondents_and_letter_sources", 78, 78,
    "Haskell's note names A. Hume, John Skippe, and Hamilton, Marquis of Douglas, as people in touch with Sasso; it says Lorenzetti published three Hume letters from 1790-2 and points to letters in the Epistolario Moschini at Biblioteca Correr, Venice.",
    "Haskell's note", "archival and secondary-source locator", "The letters and Lorenzetti's publication were not independently consulted; the note does not map each named correspondent to a particular preserved letter.",
    ["cand-2364", "cand-1308", "cand-10602", "cand-2437", "cand-0946", "cand-10605", "cand-8262", "cand-2719"], note78,
    cited_source_independently_consulted=False, **note3_link,
)
make_statement(
    note4_id, NOTES, "cand-10629", "cand-6004", "note_cites_haskell_journal_article_pages261_262", 79, 79,
    "Haskell's note cites a publication in the Journal of Warburg Institute, 1960, pages 261-2; the article title is not given.",
    "Haskell's note", "bibliographic citation", "The cited pages were not independently consulted and the article title is unspecified.",
    ["cand-10629", "cand-6004", "cand-3770"], note79, cited_source_independently_consulted=False,
    ocr_corrections=corrections_note79, **note4_link,
)
make_statement(
    note5_id, NOTES, "cand-10625", "cand-8262", "note_locates_raccolta_cicogna_versions_at_biblioteca_correr", 80, 80,
    "Haskell's note gives Biblioteca Correr, Venice, MSS. Raccolta Cicogna 3006/9 and other versions as references for Della Lena's account, and cites Haskell 1967.",
    "Haskell's note", "archival locator and secondary citation", "The manuscripts and 1967 reference were not independently checked.",
    ["cand-10625", "cand-8262", "cand-2719", "cand-10622", "cand-9424", "cand-3770"], note80,
    cited_source_independently_consulted=False, **note5_link,
)
make_statement(
    note6_id, NOTES, "cand-10624", "cand-8262", "note_locates_14_january_1786_letter_in_cod_cicogna_3198", 81, 81,
    "Haskell's note locates the letter dated 14 January 1786 in Biblioteca Correr, MSS. Cod. Cicogna, 3198.",
    "Haskell's note", "archival locator", "The manuscript was not consulted.",
    ["cand-10624", "cand-8262"], note81, cited_source_independently_consulted=False, **note6_link,
)

previous_statement = next((row for row in statements if row["statement_id"] == "st-chp16-p374-sasso-posthumous-collection-partial"), None)
if not previous_statement:
    raise SystemExit("missing p.374 collection continuation statement")
previous_qualifiers = previous_statement["qualifiers"]
if previous_qualifiers.get("predicate_status") != "partial" or BODY not in previous_qualifiers.get("cross_reference_segments", []):
    raise SystemExit("p.374 collection statement is not in the expected partial state")
previous_qualifiers["predicate_status"] = "complete"
previous_qualifiers["qualification"] = "P.375 L25 completes the source's list with a Piazzetta modello, Canaletto/Carlevarijs drawings and sketches, and one Guardi painting plus seven drawings."
previous_qualifiers["cross_reference_text_pending"] = False
previous_qualifiers["cross_reference_statement_ids"] = ["st-chp16-p375-sasso-collection-list-completion"]

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L17-22",
    "note": "The Sasso collection list left partial on p.374 L22 is completed by p.375 L25.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L25-36",
    "note": "CHP-16.pdf physical page 3 is printed p.375; all body text is migrated. OCR layout hyphens and punctuation are recorded in S2 only.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L70-81",
    "note": "P.373 notes 1-2 at L70-71, p.374 notes 1-4 at L72-75, and p.375 notes 1-6 at L76-81 are migrated and linked; later notes remain pending.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp16-p375-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
        "new_statements": len(new_statement_ids), "completed_prior_statement": previous_statement["statement_id"],
        "coverage": {BODY_PREV: "reviewed/complete", BODY: "reviewed/complete", NOTES: "reviewed/partial"},
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
