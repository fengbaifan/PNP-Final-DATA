"""Controlled semantic migration for chapter 17, printed p.383 and its notes."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-17.pdf"
EXPECTED_HASHES = {
    SOURCE: "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3",
    PDF: "fa9c9a4ebc484c481d13b0afb46f96bf94fe0631c65f0b742d0b0b9d9e0b7465",
}
BODY = "chp-17:17_CHP-17_sec_ii:l19-22"
BODY_382 = "chp-17:17_CHP-17_sec_ii:l7-17"
NOTES = "chp-17:17_CHP-17_sec_ii:l24-33"
BACKUP_SUFFIX = ".bak-s2-chp17-p383-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
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


for path, expected in EXPECTED_HASHES.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = [
    (19, "[Page 383]"),
    (20, "to buy Gian Antonio Guardi’s excursions into Longhi’s manner"),
    (21, "Ridotto, the gambling room"),
    (22, "the revolution of 1797"),
    (22, "under the headings of Liberia and Eguaglianza"),
    (22, "He died at last in 1830"),
    (30, "they were catalogued as Longhis by Lazari in 1859"),
    (30, "Pignatti, i960, p. 96."),
    (31, "Biblioteca Correr"),
    (33, "Levi, I, p. cxix."),
]
for line_number, fragment in required:
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

for segment_id in (BODY, BODY_382, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if coverage_by_id[BODY]["disposition"] != "queued" or coverage_by_id[BODY]["migration_status"] != "pending":
    raise SystemExit("p.383 body coverage precondition changed")
if coverage_by_id[BODY_382]["disposition"] != "reviewed" or coverage_by_id[BODY_382]["migration_status"] != "partial":
    raise SystemExit("p.382 continuation coverage precondition changed")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "partial" or coverage_by_id[NOTES]["source_line_ranges"] != "L25-29":
    raise SystemExit("p.382–383 notes coverage precondition changed")
if any(row.get("statement_id", "").startswith("st-chp17-p383-") for row in statements):
    raise SystemExit("p.383 statements already exist")

new_candidate_specs = [
    ("cand-10723", "The Parlatorio (painting described by Haskell as Gian Antonio Guardi’s, in Teodoro Correr’s collection)", "work", BODY, 20,
     "Haskell describes it as a Guardi work; note 1 preserves a later Lazari catalogue attribution to Longhi. No present location or independent identification is supplied."),
    ("cand-10724", "The Ridotto (painting described by Haskell as Gian Antonio Guardi’s, in Teodoro Correr’s collection)", "work", BODY, 21,
     "Haskell describes it as a Guardi work; note 1 preserves a later Lazari catalogue attribution to Longhi. Distinguish the painting from the gambling room called the Ridotto."),
    ("cand-10725", "The Ridotto gambling room in Venice", "place", BODY, 21,
     "The passage identifies the Ridotto as a gambling room closed by the government; its precise historical site is not established here."),
    ("cand-10726", "Venetian revolution of 1797 and ensuing foreign occupation", "event", BODY, 22,
     "Haskell links the 1797 revolution and subsequent foreign occupation to the break-up of aristocratic life and a resulting picture market; no occupying power is named."),
    ("cand-10727", "Byron (surname form in Haskell’s account of Venice)", "person", BODY, 22,
     "The source names Byron as a cultural reference for the Venice in which Correr continued collecting; identity is left for S3."),
    ("cand-10728", "Bonington (surname form in Haskell’s account of Venice)", "person", BODY, 22,
     "The source names Bonington as a cultural reference for the Venice in which Correr continued collecting; identity is left for S3."),
    ("cand-10729", "Civic Guard to which Teodoro Correr sought exemption", "institution", BODY, 22,
     "The body is named in Correr's reported exemption request; no specific unit or formal jurisdiction is inferred."),
    ("cand-10730", "Teodoro Correr’s correspondence to democratic authorities requesting Civic Guard exemption", "archive", BODY, 22,
     "The passage describes correspondence under the headings Libertà and Eguaglianza and a request for exemption; the original document was not consulted."),
    ("cand-10731", "Medical certificates enclosed with Teodoro Correr’s Civic Guard exemption request", "archive", BODY, 22,
     "The source reports certificates from Correr's doctors and dentist but does not name them or identify separate document call numbers."),
    ("cand-10732", "Levi, volume I, p. cxix (citation locator in p.383 note 3)", "archive", NOTES, 33,
     "Surname, volume, and page only; title, edition, and identity relative to other Levi volume-I citations remain unresolved."),
]
if any(spec[0] in candidate_by_id for spec in new_candidate_specs):
    raise SystemExit("one or more p.383 candidate IDs already exist")
for cid, name, suggested_type, source_segment, source_line, detail in new_candidate_specs:
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

candidate_by_id["cand-10699"]["detail"] += " P.383 note 2 also cites item (9a) in the same 1468/10 archive series."
candidate_by_id["cand-10705"]["detail"] += " P.383 note 1 also cites p.96 for the Parlatorio/Ridotto attribution history."

segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(19, 23)},
    NOTES: {number: source_lines[number - 1] for number in range(24, 34)},
}
segment_texts = {sid: "\n".join(lines.values()) for sid, lines in segment_lines.items()}
line_offsets = {}
for sid, lines in segment_lines.items():
    line_offsets[sid] = {}
    offset = 0
    for number, text in lines.items():
        line_offsets[sid][number] = offset
        offset += len(text) + 1

planned_mentions = []


def add_mention(candidate_id, surface, segment_id, line_number, note="", occurrence=0):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    text = segment_lines[segment_id][line_number]
    positions = []
    cursor = 0
    while True:
        position = text.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface not found in {segment_id} L{line_number}: {surface!r} #{occurrence + 1}")
    start = line_offsets[segment_id][line_number] + positions[occurrence]
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == segment_id]
    for other_start, other_end in occupied:
        if start < other_end and other_start < end:
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not nested or (start, end) == (other_start, other_end):
                raise SystemExit(f"overlapping mention span: {surface!r} at {segment_id} L{line_number}")
    planned_mentions.append({
        "mention_id": f"m-chp17-p383-{len(planned_mentions) + 1:04d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# Close the p.382 sentence and identify the works and Ridotto venue separately.
add_mention("cand-1245", "Gian Antonio Guardi’s", BODY, 20, "Artist indexed for p.383.")
add_mention("cand-1433", "Longhi’s", BODY, 20, "Pietro Longhi; the phrase describes manner, not authorship of the two works.")
add_mention("cand-10723", "Parlatorio", BODY, 20, "Title of the first Guardi work named in the collection account.")
add_mention("cand-10724", "Ridotto", BODY, 21, "Title of the second Guardi work; the gambling room itself is separately represented as a place.")
add_mention("cand-10725", "the gambling room", BODY, 21, "The venue called the Ridotto, distinguished from the painting of that title.")
add_mention("cand-0857", "he", BODY, 21, "Anaphoric reference to Teodoro Correr in the p.382–383 continuation.")
add_mention("cand-0857", "his political career", BODY, 21, "Correr's political career, previously described on p.381.")

# Revolutionary market, Correr's exemption correspondence, collecting, and legacy.
add_mention("cand-10726", "the revolution of 1797", BODY, 22, "Historical event named by Haskell; the following occupation remains unnamed.")
add_mention("cand-10726", "foreign occupation", BODY, 22, "The occupation is not attributed to a specific foreign power.")
add_mention("cand-8572", "the Republic", BODY, 22, "Venetian political entity, distinct from the city.")
add_mention("cand-0857", "Correr", BODY, 22, "Collector who acquired many pictures after the Republic's collapse.")
add_mention("cand-0857", "he", BODY, 22, "Anaphoric reference to Teodoro Correr.")
add_mention("cand-10730", "Liberia", BODY, 22, "OCR form for the printed correspondence heading Libertà; correction is recorded in S2.")
add_mention("cand-10730", "Eguaglianza", BODY, 22, "Printed heading in the reported correspondence; original document was not consulted.")
add_mention("cand-10729", "Civic Guard", BODY, 22, "Institution from which Correr sought exemption.")
add_mention("cand-10730", "to resist the violent stimulus of patriotism", BODY, 22, "Quoted wording attributed by Haskell to Correr's correspondence.")
add_mention("cand-10731", "certificates", BODY, 22, "Medical and dental certificates reported as enclosed with the request.")
add_mention("cand-2719", "Venice", BODY, 22, "City in the phrase ‘the Venice of Byron and Bonington’.")
add_mention("cand-0857", "a crotchety old bachelor", BODY, 22, "Haskell's characterization of Correr in the late collecting narrative.")
add_mention("cand-10727", "Byron", BODY, 22, "Surname form in Haskell's cultural context; identity left for S3.")
add_mention("cand-10728", "Bonington", BODY, 22, "Surname form in Haskell's cultural context; identity left for S3.")
add_mention("cand-0858", "the fruits of more than half a century’s avid collecting", BODY, 22, "Correr's accumulated collections, now left to Venice.")
add_mention("cand-2719", "his native city", BODY, 22, "Venice by anaphora.")

# P.383 notes 1–3 and their archival/citation references.
add_mention("cand-10723", "these pictures", NOTES, 30, "Refers to the Parlatorio and Ridotto discussed in the preceding body passage.")
add_mention("cand-1433", "Longhis", NOTES, 30, "Recorded as the catalogue attribution made by Lazari in 1859.")
add_mention("cand-10702", "Lazari", NOTES, 30, "Author named in the attribution history; identity remains aligned only through the existing open candidate.")
add_mention("cand-1245", "Guardi", NOTES, 30, "Attribution reported for Correr's own day.")
add_mention("cand-10705", "Pignatti, i960, p. 96", NOTES, 30, "Citation as transcribed by S0; page image reads 1960.")
add_mention("cand-8262", "Biblioteca Correr", NOTES, 31, "Repository in the printed archival locator.")
add_mention("cand-10699", "Archivio Correr", NOTES, 31, "Archive identified by the p.383 note.")
add_mention("cand-10699", "Mal", NOTES, 31, "Corrupted OCR portion of the shelfmark; the page image reads 1468/10.")
add_mention("cand-10732", "Levi", NOTES, 33, "Surname-only citation; volume and page are preserved without inferring a title or identity match.")


def quote_for(segment_id, start_line, end_line):
    return "\n".join(segment_lines[segment_id][number] for number in range(start_line, end_line + 1))


def footnote(marker, note_segment, note_range, body_segment, body_range, note_statement_ids, explanation):
    return {
        "footnote_marker": marker,
        "footnote_segment": note_segment,
        "footnote_line_range": note_range,
        "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_body_segment_id": body_segment,
        "footnote_body_line_range": body_range,
        "footnote_note_statement_ids": note_statement_ids,
        "footnote_link_note": explanation,
    }


new_statement_ids = []


def make_statement(suffix, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, text_layer, qualification, mentioned_ids, relation_candidate=False,
                   footnote_data=None, extra=None):
    statement_id = f"st-chp17-p383-{suffix}"
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 383, "pdf_physical_page": 5,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if footnote_data:
        qualifiers.update(footnote_data)
    if extra:
        qualifiers.update(extra)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote_for(segment_id, start_line, end_line),
        "origin": "book", "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md",
    })
    new_statement_ids.append(statement_id)
    return statement_id


# The p.382 open clause is completed by this p.383 passage.
note1_ids = ["st-chp17-p383-note1-parlatorio-attribution", "st-chp17-p383-note1-ridotto-attribution"]
make_statement("correr-bought-parlatorio", BODY, "cand-0857", "cand-10723",
    "bought_guardis_parlatorio_in_longhi_manner", 20, 21,
    "The p.382–383 passage says Correr's love of recording Venetian life led him to buy Gian Antonio Guardi's Parlatorio, described as an excursion into Pietro Longhi's manner.",
    "authorial report", "This closes p.382 L15. Note 1 preserves an attribution history in which Lazari later catalogued the pictures as Longhis, while they were known as Guardi's in Correr's own day.",
    ["cand-0857", "cand-10723", "cand-1245", "cand-1433"], True,
    footnote_data=footnote("1", NOTES, "L30-L30", BODY, "L20-L21", note1_ids, "P.383 note 1 discusses attribution history for the two named works; cited sources were not independently consulted."),
    extra={"continuation_from_segment_id": BODY_382, "continuation_source_line_range": "L15-L15"})
make_statement("correr-bought-ridotto", BODY, "cand-0857", "cand-10724",
    "bought_guardis_ridotto_in_longhi_manner", 20, 21,
    "The p.382–383 passage says Correr's love of recording Venetian life led him to buy Gian Antonio Guardi's Ridotto, described as an excursion into Pietro Longhi's manner.",
    "authorial report", "The painting titled Ridotto is distinct from the gambling room named in the same sentence; note 1 records an attribution history.",
    ["cand-0857", "cand-10724", "cand-1245", "cand-1433"], True,
    footnote_data=footnote("1", NOTES, "L30-L30", BODY, "L20-L21", note1_ids, "P.383 note 1 discusses attribution history for the two named works; cited sources were not independently consulted."),
    extra={"continuation_from_segment_id": BODY_382, "continuation_source_line_range": "L15-L15"})
make_statement("ridotto-room-closed", BODY, "cand-10725", None,
    "gambling_room_closed_by_government_while_correr_began_political_career", 21, 21,
    "Haskell identifies the Ridotto as a gambling room closed by the government as Correr was beginning his political career.",
    "authorial report", "The government and closure date are not identified; Correr's career start is given as 1776 on p.381.",
    ["cand-10725", "cand-0857"])
make_statement("revolution-and-paintings-market", BODY, "cand-10726", None,
    "revolution_and_foreign_occupation_brought_pictures_to_market", 22, 22,
    "Haskell says the 1797 revolution and ensuing foreign occupation broke up aristocratic life and collections, bringing many pictures onto the market.",
    "authorial historical explanation", "The occupying power and individual collections are not named; this records Haskell's causal account.", ["cand-10726"])
make_statement("correr-acquired-after-republic-collapse", BODY, "cand-0857", "cand-8572",
    "obtained_many_pictures_after_republic_collapsed", 22, 22,
    "Haskell says Correr obtained a great many pictures after the Venetian Republic had collapsed.",
    "authorial report", "No individual pictures or precise acquisition dates are identified here.", ["cand-0857", "cand-8572"], True)
make_statement("correr-avoided-political-commitment", BODY, "cand-0857", None,
    "carefully_avoided_commitment_to_new_regime", 22, 22,
    "Haskell says Correr was once again careful to avoid committing himself to the new regime.",
    "authorial characterization", "This is Haskell's interpretation of Correr's conduct, not a statement by Correr about his motive.", ["cand-0857"])
make_statement("correr-exemption-correspondence", BODY, "cand-0857", "cand-10730",
    "wrote_to_democratic_authorities_seeking_civic_guard_exemption", 22, 22,
    "Haskell reports that Correr wrote to the new democratic rulers under the headings Libertà and Eguaglianza, saying ill-health compelled him to resist the stimulus of patriotism and seek exemption from the Civic Guard.",
    "authorial report with a quotation attributed to Correr", "The original correspondence was not consulted. S0 reads ‘Liberia’; the page image reads ‘Libertà’. The rulers are unnamed.", ["cand-0857", "cand-10726", "cand-10729", "cand-10730"], True,
    footnote_data=footnote("2", NOTES, "L31-L32", BODY, "L22-L22", ["st-chp17-p383-note2-archival-locator"], "P.383 note 2 gives an Archivio Correr locator; the manuscript was not consulted."),
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 22, "ocr": "Liberia", "print": "Libertà", "basis": "CHP-17.pdf physical page 5, printed page 383."}]})
make_statement("correr-enclosed-medical-certificates", BODY, "cand-0857", "cand-10731",
    "enclosed_doctor_and_dentist_certificates_with_exemption_request", 22, 22,
    "Haskell says Correr enclosed certificates from his doctors and dentist to support his Civic Guard exemption request.",
    "authorial report", "The practitioners and certificate count are not supplied; the documents were not independently consulted.", ["cand-0857", "cand-10729", "cand-10730", "cand-10731"], True,
    footnote_data=footnote("2", NOTES, "L31-L32", BODY, "L22-L22", ["st-chp17-p383-note2-archival-locator"], "P.383 note 2 gives an Archivio Correr locator; the manuscript was not consulted."))
make_statement("correr-kept-collecting-into-nineteenth-century", BODY, "cand-0857", None,
    "continued_buying_well_into_nineteenth_century", 22, 22,
    "Haskell says Correr continued buying well into the nineteenth century.",
    "authorial report", "The passage gives no exact end date for the collecting activity.", ["cand-0857"])
make_statement("correr-background-and-bachelor-characterization", BODY, "cand-0857", None,
    "safely_in_background_and_characterized_as_crotchety_bachelor", 22, 22,
    "Haskell characterizes Correr as safely in the background and as a crotchety old bachelor.",
    "authorial characterization", "These are Haskell's descriptions, not independently established personality facts.", ["cand-0857"])
make_statement("correr-unnoticed-in-byron-bonington-venice", BODY, "cand-0857", "cand-2719",
    "unnoticed_in_venice_of_byron_and_bonington", 22, 22,
    "Haskell characterizes Correr as unnoticed in the Venice of Byron and Bonington.",
    "authorial characterization", "Byron and Bonington are retained in the source's surname forms for later identity alignment; this is not a claim that either interacted with Correr.", ["cand-0857", "cand-2719", "cand-10727", "cand-10728"])
make_statement("correr-vulnerable-to-dealers", BODY, "cand-0857", None,
    "easy_prey_to_unscrupulous_second_hand_dealers", 22, 22,
    "Haskell says Correr was an easy prey to more unscrupulous second-hand dealers.",
    "authorial characterization", "This is Haskell's characterization; no dealer or transaction is identified.", ["cand-0857"],
    footnote_data=footnote("3", NOTES, "L33-L33", BODY, "L22-L22", ["st-chp17-p383-note3-levi"], "P.383 note 3 gives only a Levi volume-and-page citation; it was not independently consulted."))
make_statement("correr-died-in-1830", BODY, "cand-0857", None,
    "died_in_1830", 22, 22,
    "Haskell gives Correr's death year as 1830.",
    "authorial report", "The year is retained as a book-reported claim and is not externally verified.", ["cand-0857"])
make_statement("correr-bequest-after-half-century", BODY, "cand-0857", "cand-2719",
    "left_more_than_half_century_of_collecting_to_native_city", 22, 22,
    "Haskell says Correr left the fruits of more than half a century of collecting to his native city, Venice.",
    "authorial report", "The passage gives no legal instrument or exact start date for the collecting period.", ["cand-0857", "cand-0858", "cand-2719"], True)
make_statement("haskell-closes-aristocratic-art-tradition", BODY, "cand-0857", None,
    "ended_long_tradition_of_aristocratic_interest_in_arts", 22, 22,
    "Haskell presents Correr's bequest as a worthy ending to a tradition of aristocratic interest in the arts that began many centuries earlier.",
    "authorial interpretation", "The longue durée framing is Haskell's interpretation, not an independently established historical periodization.", ["cand-0857"])

# Endnotes for the attribution history, archival locator, and dealer claim.
make_statement("note1-parlatorio-attribution", NOTES, "cand-10723", "cand-1245",
    "known_as_guardis_in_correr_day_but_catalogued_as_longhi_by_lazari_1859", 30, 30,
    "P.383 note 1 says the Parlatorio was catalogued as a Longhi by Lazari in 1859 but was known as Guardi's in Correr's own day.",
    "attribution history in Haskell's note", "The cited Lazari and Pignatti works were not independently consulted; the differing attribution history is preserved.", ["cand-10723", "cand-10724", "cand-1433", "cand-10702", "cand-1245", "cand-10705"], True,
    footnote_data={"footnote_marker": "1", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L20-L21", "footnote_body_link_status": "linked", "footnote_text_pending": False},
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 30, "ocr": "i960", "print": "1960", "basis": "CHP-17.pdf physical page 5, printed page 383."}]})
make_statement("note1-ridotto-attribution", NOTES, "cand-10724", "cand-1245",
    "known_as_guardis_in_correr_day_but_catalogued_as_longhi_by_lazari_1859", 30, 30,
    "P.383 note 1 says the Ridotto was catalogued as a Longhi by Lazari in 1859 but was known as Guardi's in Correr's own day.",
    "attribution history in Haskell's note", "The cited Lazari and Pignatti works were not independently consulted; the differing attribution history is preserved.", ["cand-10723", "cand-10724", "cand-1433", "cand-10702", "cand-1245", "cand-10705"], True,
    footnote_data={"footnote_marker": "1", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L20-L21", "footnote_body_link_status": "linked", "footnote_text_pending": False},
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 30, "ocr": "i960", "print": "1960", "basis": "CHP-17.pdf physical page 5, printed page 383."}]})
make_statement("note2-archival-locator", NOTES, "cand-10730", "cand-10699",
    "archival_locator_for_correr_exemption_correspondence", 31, 32,
    "P.383 note 2 gives Biblioteca Correr, Archivio Correr, 1468/10 (9a) as a locator for the Correr exemption material.",
    "archival citation", "The original item was not consulted. The OCR fragments ‘Mal’ and ‘10’ are reconstructed from the printed page as the fraction 1468/10.", ["cand-10730", "cand-10731", "cand-8262", "cand-10699"], True,
    footnote_data={"footnote_marker": "2", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L22-L22", "footnote_body_link_status": "linked", "footnote_text_pending": False},
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 31, "ocr": "Mal", "print": "1468", "basis": "CHP-17.pdf physical page 5, printed page 383."}, {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 32, "ocr": "10 ' ", "print": "10 (9a)", "basis": "CHP-17.pdf physical page 5, printed page 383."}]})
make_statement("note3-levi", NOTES, "cand-10732", None,
    "cited_for_correr_dealer_account", 33, 33,
    "P.383 note 3 cites Levi, volume I, p. cxix.",
    "bibliographic citation", "The title and edition are not given; the cited page was not independently consulted.", ["cand-10732"],
    footnote_data={"footnote_marker": "3", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L22-L22", "footnote_body_link_status": "linked", "footnote_text_pending": False})

if len({row["mention_id"] for row in planned_mentions}) != len(planned_mentions):
    raise SystemExit("duplicate planned mention IDs")
if any(row["mention_id"] in {item["mention_id"] for item in mentions} for row in planned_mentions):
    raise SystemExit("one or more p.383 mention IDs already exist")
for row in planned_mentions:
    if row["candidate_id"] not in candidate_by_id:
        raise SystemExit(f"missing candidate for {row['mention_id']}")
    text = segment_texts[row["segment_id"]]
    start, end = int(row["start_char"]), int(row["end_char"])
    if text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span failed exact-source check: {row['mention_id']}")
for row in statements:
    if row.get("statement_id", "").startswith("st-chp17-p383-"):
        for key in ("subject_candidate_id", "object_candidate_id"):
            value = row.get(key)
            if value and value not in candidate_by_id:
                raise SystemExit(f"missing {key} in {row['statement_id']}: {value}")

coverage_by_id[BODY_382].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L7-17",
    "note": "Printed p.382 body checked against CHP-17.pdf physical page 4. The final clause at L15 is closed by p.383 L20-21; p.382 body and printed note 4 are fully migrated.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L20-22",
    "note": "Printed p.383 body checked against CHP-17.pdf physical page 5. L20-21 closes the p.382 cross-page sentence; body claims and printed notes 1-3 are migrated. OCR Libertà and shelfmark corrections are recorded in S2 only.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L25-33",
    "note": "P.382 notes 1-3, 5-6 at L25-29 were previously migrated; p.383 notes 1-3 at L30-33 are now migrated and linked to p.383 body claims. Printed note 2 shelfmark is 1468/10 (9a); S0 OCR is unchanged.",
})

if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidate_specs),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "coverage_updates": {BODY_382: "complete", BODY: "complete", NOTES: "complete"},
        "candidate_ids": [item[0] for item in new_candidate_specs],
        "open_cross_page_phrase": "p.382 L15 closed by p.383 L20-21",
        "chapter_17_stage": "S2 page coverage through p.383 complete",
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
    shutil.copy2(path, backup)

mentions.extend(planned_mentions)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({"mode": "applied", "candidates": len(new_candidate_specs), "mentions": len(planned_mentions), "statements": len(new_statement_ids)}, ensure_ascii=False))
