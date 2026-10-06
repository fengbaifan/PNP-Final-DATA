"""Controlled semantic migration for chapter 17, printed p.382."""
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
BODY = "chp-17:17_CHP-17_sec_ii:l7-17"
NOTES = "chp-17:17_CHP-17_sec_ii:l24-33"
BACKUP_SUFFIX = ".bak-s2-chp17-p382-20261004"

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
required = {
    7: "[Page 382]",
    8: "the services which he rendered Venice",
    9: "when Correr began to assemble the vast collections",
    10: "especially the Molin, the Orsetti and the Pellegrini",
    10: "Antonello da Messina’s Deposition and Cosimo",
    11: "Tura’s Pietà",
    13: "Pietro Longhi",
    14: "Alessandro",
    15: "led him",
    16: "Zocchi’s double portrait",
    17: "Bollettino dei Musei Civici Veneziani",
    25: "Dandolo, p. 97.",
    26: "Pietro Longhi who died in 1782.",
    27: "Teodoro Correr e il suo museo",
    28: "Dandolo, p. 97.",
    29: "one view of Venice attributed to Canaletto",
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

for segment_id in (BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if coverage_by_id[BODY]["disposition"] != "queued" or coverage_by_id[BODY]["migration_status"] != "pending":
    raise SystemExit("p.382 body coverage precondition changed")
if coverage_by_id[NOTES]["disposition"] != "queued" or coverage_by_id[NOTES]["migration_status"] != "pending":
    raise SystemExit("p.382–383 notes coverage precondition changed")
if any(row.get("statement_id", "").startswith("st-chp17-p382-") for row in statements):
    raise SystemExit("p.382 statements already exist")

new_candidate_specs = [
    ("cand-10707", "Molin family named among sources of Teodoro Correr’s pictures", "family", BODY, 10,
     "The surname is used for a patrician family; no individual members or branch are identified."),
    ("cand-10708", "Orsetti family named among sources of Teodoro Correr’s pictures", "family", BODY, 10,
     "The surname is used for a patrician family; no individual members or branch are identified."),
    ("cand-10709", "Pellegrini family named among sources of Teodoro Correr’s pictures", "family", BODY, 10,
     "The surname is used for a patrician family; this is not identified with the painter Giovanni Antonio Pellegrini."),
    ("cand-10710", "Teodoro Correr’s unnamed palace near S. Giovanni Decollato", "place", BODY, 10,
     "The passage locates Correr’s palace near S. Giovanni Decollato but gives no palace name or address."),
    ("cand-10711", "S. Giovanni Decollato", "place", BODY, 10,
     "Named as a locator for Correr’s palace; no further identification is made in this S2 passage."),
    ("cand-10712", "Approximately twenty paintings by Pietro Longhi in Teodoro Correr’s collection", "work", BODY, 13,
     "A corpus described by Haskell as about twenty paintings; it is not a title-level inventory."),
    ("cand-10713", "Unidentified portrait by Alessandro Longhi owned by Teodoro Correr", "work", BODY, 14,
     "The passage says Correr owned one of Alessandro Longhi’s portraits but does not identify the sitter or portrait."),
    ("cand-10714", "Unidentified drawings by Pietro Longhi obtained by Teodoro Correr from Alessandro Longhi", "work", BODY, 14,
     "The passage describes drawings by Pietro Longhi obtained from his son Alessandro; no individual sheets are identified."),
    ("cand-10715", "Sasso sale of 1803 cited for the Zocchi double portrait", "event", BODY, 17,
     "The sale is named as the context in which Correr almost certainly bought the portrait; seller identity is not inferred."),
    ("cand-10716", "Unidentified Marchese Gerini portrayed with A. M. Zanetti the Elder", "person", BODY, 16,
     "The source gives only the title and surname; it is not equated with another Gerini candidate at S2."),
    ("cand-10717", "Haskell citation in Bollettino dei Musei Civici Veneziani, 1960, nos. 3/4, pp. 32–37", "archive", BODY, 17,
     "A citation locator for the p.382 note; the cited article was not independently consulted."),
    ("cand-10718", "Dandolo, p. 97 (citations in p.382 notes 1 and 5)", "archive", NOTES, 25,
     "The page gives author surname and page only; title and edition are not supplied or independently identified."),
    ("cand-10719", "Urbani de Ghelthof, Teodoro Correr e il suo museo", "archive", NOTES, 27,
     "The note gives an untitled/undated publication locator and a Biblioteca Correr shelfmark; the publication was not consulted."),
    ("cand-10720", "Unidentified view of Venice attributed to Canaletto and now thought to be from his studio", "work", NOTES, 29,
     "Haskell reports an attribution to Canaletto and a later studio-work assessment; the painting is not independently checked."),
    ("cand-10721", "Damaged view of Castel Cogolo, probably by Francesco Guardi", "work", NOTES, 29,
     "The attribution is explicitly probable and reported by Haskell; the painting is not independently checked."),
    ("cand-10722", "Unspecified archival papers in Teodoro Correr’s archive cited by Urbani de Ghelthof", "archive", NOTES, 27,
     "The note says archival papers corroborate the account but does not identify specific documents or call numbers."),
]
if any(spec[0] in candidate_by_id for spec in new_candidate_specs):
    raise SystemExit("one or more p.382 candidate IDs already exist")
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

segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(7, 18)},
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
        "mention_id": f"m-chp17-p382-{len(planned_mentions) + 1:04d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# The continuation from p.381 closes at the start of p.382.
add_mention("cand-0857", "he", BODY, 8, "Anaphoric reference to Teodoro Correr in the sentence continuing from printed p.381.")
add_mention("cand-2719", "Venice", BODY, 8, "City served by Correr; distinct from the Republic as a political entity.")

# Correr's collecting history, sources, method, and palace.
add_mention("cand-0857", "Correr", BODY, 9, "Subject of the account of when he began collecting.")
add_mention("cand-0858", "vast collections", BODY, 9, "Correr's collections, indexed as a separate topic candidate.")
add_mention("cand-0858", "which he later left to Venice", BODY, 9, "The collection was later left to Venice.")
add_mention("cand-2719", "Venice", BODY, 9, "Recipient city of Correr's bequest.")
add_mention("cand-0857", "he", BODY, 9, "Anaphoric reference to Teodoro Correr.")
add_mention("cand-0857", "he", BODY, 10, "Anaphoric reference to Teodoro Correr.")
add_mention("cand-10707", "Molin", BODY, 10, "Named patrician family; no branch or members specified.")
add_mention("cand-10708", "Orsetti", BODY, 10, "Named patrician family; no branch or members specified.")
add_mention("cand-10709", "Pellegrini", BODY, 10, "Named as a family, not identified with painter Giovanni Antonio Pellegrini.")
add_mention("cand-0857", "his contemporaries", BODY, 10, "Correr's contemporaries are an unnamed group, not separate person candidates.")
add_mention("cand-0857", "him", BODY, 10, "Anaphoric reference to Correr as a collector attending sales.")
add_mention("cand-0857", "His aim", BODY, 10, "Anaphoric reference to Correr's collecting aims.")
add_mention("cand-2719", "his city", BODY, 10, "Anaphoric reference to Venice.")
add_mention("cand-10710", "his palace", BODY, 10, "Correr's unnamed palace, described as near S. Giovanni Decollato.")
add_mention("cand-10711", "S. Giovanni Decollato", BODY, 10, "Named locator for the palace.")
add_mention("cand-0857", "Correr’s contemporaries", BODY, 10, "Contemporaries whose doubts about his taste Haskell reports.")
add_mention("cand-0857", "he", BODY, 11, "Anaphoric reference to Correr as collector.")
add_mention("cand-0857", "he", BODY, 11, "Anaphoric reference to Correr as collector.", occurrence=1)
add_mention("cand-1657", "Antonello da Messina’s Deposition", BODY, 10, "Specific work named as a high-quality acquisition.")
add_mention("cand-1657", "Deposition", BODY, 10, "Work title nested in the full artist/title mention.")
add_mention("cand-2659", "Cosimo", BODY, 10, "Artist's given name at the line end; surname and work title continue on the next line.")
add_mention("cand-2659", "Tura’s Pietà", BODY, 11, "Specific work named as a high-quality acquisition.")

# Longhi paintings, themes, Alessandro Longhi, and drawings.
add_mention("cand-0858", "the collection", BODY, 12, "Correr's collection, introduced in the preceding paragraph.")
add_mention("cand-1433", "Pietro Longhi", BODY, 13, "Painter indexed for paintings in Correr's collection.")
add_mention("cand-1433", "Longhi’s", BODY, 13, "Pietro Longhi, whose documentary scenes Correr collected.")
add_mention("cand-0859", "the physical aspect of the city", BODY, 13, "Connects to Correr's indexed interest in Venice's history; Haskell's speculation is retained as such.")
add_mention("cand-2719", "the city", BODY, 13, "Venice by anaphora.")
add_mention("cand-0857", "he collected", BODY, 13, "Correr is the collector; the object is the Longhi corpus.")
add_mention("cand-10712", "twenty-odd", BODY, 13, "Approximate number of paintings in the work group.")
add_mention("cand-10712", "Longhis", BODY, 14, "Continuation of the plural work-group reference across a source line break.")
add_mention("cand-0857", "he obtained", BODY, 14, "Subject is Correr, who obtained drawings from Alessandro Longhi.")
add_mention("cand-1424", "Alessandro", BODY, 14, "Alessandro Longhi, the artist's son; the index covers p.382.")
add_mention("cand-10713", "one of whose portraits he owned", BODY, 14, "An unidentified portrait by Alessandro Longhi owned by Correr.")
add_mention("cand-10714", "drawings by Pietro Longhi", BODY, 14, "Unidentified drawings obtained from Alessandro Longhi; no individual sheets named.")
add_mention("cand-1433", "Pietro Longhi", BODY, 14, "Painter of the drawings, nested within the work-group span.")

# Printed p.382 note 4 is set below the body and points back to the auction sentence.
add_mention("cand-2872", "Zocchi’s", BODY, 16, "Artist named for the double portrait.")
add_mention("cand-2873", "double portrait", BODY, 16, "Specific portrait indexed under Zocchi's double portrait of Zanetti and Gerini.")
add_mention("cand-2838", "A. M. Zanetti", BODY, 16, "The indexed Zanetti, the Elder; no new identity decision is made at S2.")
add_mention("cand-10716", "Marchese", BODY, 16, "The sitter is identified only by title and surname fragment on this line.")
add_mention("cand-10716", "Gerini", BODY, 17, "Continuation of the sitter's name across a source line break.")
add_mention("cand-10715", "Sasso sale", BODY, 17, "Named auction event; seller identity is not inferred.")
add_mention("cand-10715", "in 1803", BODY, 17, "Date attached to the Sasso sale.")
add_mention("cand-10717", "Haskell", BODY, 17, "Citation author named in the footnote.")
add_mention("cand-10717", "Bollettino dei Musei Civici Veneziani", BODY, 17, "Periodical locator; the cited pages were not independently consulted.")

# End-of-page footnotes 1–3, 5–6; note 4 is in BODY lines 16–17.
add_mention("cand-10718", "Dandolo", NOTES, 25, "Surname-only citation in note 1; title and edition are absent.")
add_mention("cand-1433", "Pietro Longhi", NOTES, 26, "Artist named in the conditional qualification about direct acquisition.")
add_mention("cand-10719", "Urbani de Ghelthof", NOTES, 27, "Author form as printed; not externally identified.")
add_mention("cand-10719", "Teodoro Correr e il suo museo", NOTES, 27, "Title of the cited work; not independently consulted.")
add_mention("cand-8262", "Biblioteca Correr", NOTES, 27, "Repository named in the publication locator.")
add_mention("cand-10699", "his archives", NOTES, 27, "Correr archival papers mentioned as confirmation; no specific manuscript is identified here.")
add_mention("cand-10718", "Dandolo", NOTES, 28, "Surname-only citation in note 5; same page reference as note 1.")
add_mention("cand-0498", "Canaletto", NOTES, 29, "Artist named in the reported attribution of the Venice view.")
add_mention("cand-10720", "one view of Venice", NOTES, 29, "Unidentified painting; source reports both former attribution and studio-work reassessment.")
add_mention("cand-2719", "Venice", NOTES, 29, "Place depicted in the unidentified view.")
add_mention("cand-0498", "his studio", NOTES, 29, "Anaphoric reference to Canaletto in the reported studio-work reassessment.")
add_mention("cand-10721", "view of Castel Cogolo", NOTES, 29, "Damaged unidentified painting with a probable Guardi attribution.")
add_mention("cand-1239", "Francesco Guardi", NOTES, 29, "Artist in Haskell's explicitly probable attribution.")


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
                   footnote_data=None, speaker="Haskell", extra=None):
    statement_id = f"st-chp17-p382-{suffix}"
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 382, "pdf_physical_page": 4,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
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


# The first sentence closes p.381; the remaining page is read in its original sequence.
s1 = make_statement("correr-services-to-venice", BODY, "cand-0857", "cand-2719",
    "rendered_services_to_venice_beyond_political_career", 8, 8,
    "Haskell says the services Correr rendered Venice in other ways exceeded what he could have achieved politically at that point in the city's history.",
    "authorial evaluation", "Comparative assessment by Haskell; no specific service is named in this sentence.", ["cand-0857", "cand-2719"])
s2 = make_statement("correr-collection-beginnings", BODY, "cand-0857", "cand-0858",
    "began_assembling_collections_when_young_probable", 9, 9,
    "Haskell says it is impossible to be certain when Correr began assembling the collections, but probable that he began while young.",
    "qualified authorial report", "Both the uncertainty and probability are preserved; the passage does not provide a date.", ["cand-0857", "cand-0858"],
    footnote_data=footnote("1", NOTES, "L25-L25", BODY, "L9-L9", ["st-chp17-p382-note1-dandolo"], "Printed note 1 cites Dandolo, p.97, for the collecting-history passage."))
s2b = make_statement("correr-bequeathed-collections-to-venice", BODY, "cand-0857", "cand-2719",
    "left_collections_to_venice", 9, 9,
    "Haskell says Correr later left his collections to Venice.",
    "authorial report", "The passage describes the bequest without specifying its legal instrument or the collection's later institutional status.", ["cand-0857", "cand-0858", "cand-2719"], True)
s3 = make_statement("correr-commissioning-living-artists", BODY, "cand-0857", None,
    "unlikely_to_have_commissioned_living_artists", 10, 10,
    "Haskell considers it unlikely that Correr commissioned work from living artists at any stage.",
    "qualified authorial inference", "Haskell says it seems unlikely, not impossible. Printed note 2 explicitly allows a possible occasional direct purchase from Pietro Longhi.", ["cand-0857", "cand-1433"],
    footnote_data=footnote("2", NOTES, "L26-L26", BODY, "L10-L10", ["st-chp17-p382-note2-longhi-qualification"], "Note 2 preserves an unlikely but possible exception concerning Pietro Longhi."))
s4 = make_statement("correr-pictures-from-molin-family", BODY, "cand-0857", "cand-10707",
    "obtained_pictures_from_family", 10, 10,
    "Haskell says Correr obtained many pictures from the Molin family.",
    "authorial report", "The family is named collectively; no individual seller or transaction is identified.", ["cand-0857", "cand-10707"], True)
s5 = make_statement("correr-pictures-from-orsetti-family", BODY, "cand-0857", "cand-10708",
    "obtained_pictures_from_family", 10, 10,
    "Haskell names the Orsetti family among the sources from which Correr obtained many pictures.",
    "authorial report", "No individual seller or transaction is identified.", ["cand-0857", "cand-10708"], True)
s6 = make_statement("correr-pictures-from-pellegrini-family", BODY, "cand-0857", "cand-10709",
    "obtained_pictures_from_family", 10, 10,
    "Haskell names the Pellegrini family among the sources from which Correr obtained many pictures.",
    "authorial report", "The family is not identified with the painter Giovanni Antonio Pellegrini; no individual seller or transaction is named.", ["cand-0857", "cand-10709"], True)
s7 = make_statement("correr-financial-weakness-exploitation", BODY, "cand-0857", None,
    "took_advantage_of_contemporaries_financial_weaknesses", 10, 10,
    "Haskell says Correr took ruthless advantage of his contemporaries' financial weaknesses.",
    "authorial report with evaluative language", "‘Ruthless’ is Haskell's characterization; no individual is named.", ["cand-0857"],
    footnote_data=footnote("3", NOTES, "L27-L27", BODY, "L10-L10", ["st-chp17-p382-note3-urbani-publication"], "Note 3 supplies a bibliographic lead and says archival papers confirmed the account; neither was independently consulted."))
s7b = make_statement("correr-attended-sales", BODY, "cand-0857", None,
    "attended_sales_and_public_auctions", 10, 10,
    "Haskell says Correr attended sales and public auctions.",
    "authorial report", "No individual transaction is identified in this sentence.", ["cand-0857"],
    footnote_data=footnote("4", BODY, "L16-L17", BODY, "L10-L10", ["st-chp17-p382-note4-zocchi-sale"], "Printed note 4 gives an example of a purchase at a sale; Haskell's cited pages were not independently consulted."))
s8 = make_statement("correr-collecting-aim-and-palace", BODY, "cand-0857", "cand-10710",
    "assembled_materials_for_city_history_and_palace_already_museum", 10, 10,
    "Haskell says Correr sought books, manuscripts, prints, coins, medals, bronzes and pictures that illuminated Venice's history and cultural achievements, and that his palace near S. Giovanni Decollato was already a museum before his death.",
    "authorial report", "The palace is unnamed. The museum description is Haskell's retrospective characterization; it does not establish a formal museum institution at that date.", ["cand-0857", "cand-2719", "cand-10710", "cand-10711"], True,
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 10, "ocr": "already-a museum", "print": "already a museum", "basis": "CHP-17.pdf physical page 4, printed page 382."}]})
s9 = make_statement("correr-taste-criticism", BODY, "cand-0857", None,
    "taste_criticized_by_contemporaries_and_nineteenth_century_writers", 10, 10,
    "Haskell reports doubts about Correr's taste among contemporaries and says nineteenth-century writers repeated the aspersions.",
    "authorial report", "The criticism is attributed to other writers, not asserted as an objective assessment by this dataset.", ["cand-0857"],
    footnote_data=footnote("5", NOTES, "L28-L28", BODY, "L10-L10", ["st-chp17-p382-note5-dandolo"], "Printed note 5 cites Dandolo, p.97, for the surrounding discussion."),
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 10, "ocr": "ofhis", "print": "of his", "occurrences": 2, "basis": "CHP-17.pdf physical page 4, printed page 382."}]})
s10 = make_statement("correr-collected-unfashionable-periods", BODY, "cand-0857", "cand-0858",
    "collected_fifteenth_and_eighteenth_century_works_when_unfashionable", 10, 11,
    "Haskell says Correr collected works of the fifteenth and eighteenth centuries when neither period was fashionable.",
    "authorial report", "The statement is limited to Haskell's account and does not name every work in either period.", ["cand-0857", "cand-0858"])
s11 = make_statement("correr-acquired-deposition", BODY, "cand-0857", "cand-1657",
    "acquired_antonello_da_messina_deposition", 10, 11,
    "Haskell names Antonello da Messina's Deposition as a high-quality work Correr acquired.",
    "authorial report", "The passage does not give the work's present location or an external catalogue identification.", ["cand-0857", "cand-1657"], True)
s12 = make_statement("correr-acquired-pieta", BODY, "cand-0857", "cand-2659",
    "acquired_cosimo_tura_pieta", 10, 11,
    "Haskell names Cosimo Tura's Pietà as a high-quality work Correr acquired.",
    "authorial report", "The passage does not give the work's present location or an external catalogue identification.", ["cand-0857", "cand-2659"], True)
s13 = make_statement("correr-owned-inferior-paintings", BODY, "cand-0857", "cand-0858",
    "collection_included_inferior_paintings_and_few_great_early_renaissance_pictures", 11, 11,
    "Haskell says Correr owned many inferior paintings and relatively few great early Renaissance pictures.",
    "authorial evaluation", "The qualitative terms and comparative framing belong to Haskell; no count is supplied.", ["cand-0857", "cand-0858"])
s14 = make_statement("correr-historical-curiosity", BODY, "cand-0857", None,
    "historical_curiosity_motivated_collecting_more_than_scholarship_or_aesthetic_appreciation", 11, 11,
    "Haskell says it is almost certain that historical curiosity motivated Correr more than scholarship or aesthetic appreciation.",
    "qualified authorial inference", "The phrase ‘almost certain’ is preserved as Haskell's degree of confidence.", ["cand-0857"])
s15 = make_statement("correr-longhi-dominates-collection", BODY, "cand-0857", "cand-1433",
    "pietro_longhi_paintings_dominate_eighteenth_century_collection", 12, 13,
    "Haskell says Pietro Longhi completely dominates the eighteenth-century artists in Correr's collection.",
    "authorial report", "The comparison is limited to the eighteenth-century artists in the collection.", ["cand-0857", "cand-1433", "cand-0858"], True)
s16 = make_statement("correr-longhi-and-view-painters", BODY, "cand-0857", "cand-1433",
    "collected_longhi_documentary_scenes_but_no_view_painters", 13, 13,
    "Haskell describes Correr's passion for Pietro Longhi's documentary scenes and says it is strange he paid no attention to view-painters.",
    "authorial report and interpretation", "‘Documentary’ and the characterization of Correr's motive are Haskell's framing; note 6 records two views in the collection.", ["cand-0857", "cand-1433"], True,
    footnote_data=footnote("6", NOTES, "L29-L29", BODY, "L13-L13", ["st-chp17-p382-note6-venice-view", "st-chp17-p382-note6-castel-cogolo-view"], "Printed note 6 qualifies the view-painters discussion with two collection examples and attributed works."))
s17 = make_statement("correr-awareness-of-venice-change", BODY, "cand-0857", "cand-2719",
    "possibly_collected_no_views_because_cityscape_remained_but_way_of_life_changed", 13, 13,
    "Haskell speculates that Correr may have thought Venice's physical aspect would remain while its ‘douceur de vivre’ had disappeared.",
    "authorial speculation", "The passage says ‘it almost seems’; this is not recorded as Correr's stated motive.", ["cand-0857", "cand-2719"])
s18 = make_statement("correr-longhi-paintings-corpus", BODY, "cand-0857", "cand-10712",
    "collected_about_twenty_longhi_paintings_to_record_venetian_life", 13, 14,
    "Haskell says Correr collected about twenty Longhi paintings depicting noble family life, street scenes, morning chocolate ceremonies, and clergy portraits.",
    "authorial report", "The count is approximate, and the named subjects describe a corpus rather than individual identified paintings.", ["cand-0857", "cand-10712", "cand-1433"], True)
s19 = make_statement("correr-owned-alessandro-longhi-portrait", BODY, "cand-0857", "cand-10713",
    "owned_one_portrait_by_alessandro_longhi", 14, 14,
    "Haskell says Correr owned one portrait by Alessandro Longhi.",
    "authorial report", "The portrait and sitter are not identified in this passage.", ["cand-0857", "cand-1424", "cand-10713"], True)
s20 = make_statement("correr-obtained-pietro-longhi-drawings", BODY, "cand-0857", "cand-10714",
    "obtained_as_many_pietro_longhi_drawings_as_possible_from_alessandro", 14, 14,
    "Haskell says Correr obtained from Alessandro Longhi as many drawings by Pietro Longhi as he could obtain.",
    "authorial report", "No individual drawing or precise count is supplied.", ["cand-0857", "cand-1424", "cand-1433", "cand-10714"], True)
# Footnote statements and the two reported view attributions.
make_statement("note1-dandolo", NOTES, "cand-10718", None,
    "cited_for_correr_collecting_history", 25, 25,
    "Printed p.382 note 1 cites Dandolo, p.97.", "bibliographic citation",
    "The cited work was not identified beyond surname and page and was not independently consulted.", ["cand-10718"],
    footnote_data={"footnote_marker": "1", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L9-L9", "footnote_body_link_status": "linked", "footnote_text_pending": False})
make_statement("note2-longhi-qualification", NOTES, "cand-0857", "cand-1433",
    "possible_occasional_direct_purchase_from_pietro_longhi", 26, 26,
    "Printed note 2 says it is just possible, though unlikely, that Correr occasionally obtained a painting directly from Pietro Longhi, who died in 1782.",
    "qualified authorial note", "Both possibility and low likelihood are retained; no individual painting is identified.", ["cand-0857", "cand-1433"], True,
    footnote_data={"footnote_marker": "2", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L10-L10", "footnote_body_link_status": "linked", "footnote_text_pending": False})
make_statement("note3-urbani-publication", NOTES, "cand-10719", "cand-8262",
    "cited_for_correr_collection_account_and_confirmed_by_archive_papers", 27, 27,
    "Printed note 3 points to Urbani de Ghelthof's Teodoro Correr e il suo museo and says the account is confirmed by papers in Correr's archives.",
    "bibliographic citation", "The publication and archival papers were not independently consulted; the note gives Biblioteca Correr Op. P.D. 18796.", ["cand-10719", "cand-8262", "cand-10722"],
    footnote_data={"footnote_marker": "3", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L10-L10", "footnote_body_link_status": "linked", "footnote_text_pending": False},
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 27, "ocr": "Sec the hints", "print": "See the hints", "basis": "CHP-17.pdf physical page 4, printed page 382."}]})
make_statement("note4-zocchi-sale", BODY, "cand-0857", "cand-2873",
    "almost_certain_purchase_at_sasso_sale_1803", 16, 17,
    "Printed note 4 says Correr almost certainly bought Zocchi's double portrait of A. M. Zanetti and Marchese Gerini at the Sasso sale in 1803.",
    "qualified authorial note", "The cited Haskell passage is a locator, not an independently consulted source.", ["cand-0857", "cand-2872", "cand-2873", "cand-2838", "cand-10716", "cand-10715"], True,
    footnote_data={"footnote_marker": "4", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L10-L10", "footnote_body_link_status": "linked", "footnote_text_pending": False},
    extra={"ocr_corrections": [
        {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 17, "ocr": "sec Haskell", "print": "see Haskell", "basis": "CHP-17.pdf physical page 4, printed page 382."},
        {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 17, "ocr": "i960", "print": "1960", "basis": "CHP-17.pdf physical page 4, printed page 382."},
    ]})
make_statement("note5-dandolo", NOTES, "cand-10718", None,
    "cited_for_correr_taste_discussion", 28, 28,
    "Printed p.382 note 5 cites Dandolo, p.97.", "bibliographic citation",
    "The cited work was not identified beyond surname and page and was not independently consulted.", ["cand-10718"],
    footnote_data={"footnote_marker": "5", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L10-L10", "footnote_body_link_status": "linked", "footnote_text_pending": False})
make_statement("note6-venice-view", NOTES, "cand-0857", "cand-10720",
    "owned_venice_view_attributed_to_canaletto_but_thought_studio_work", 29, 29,
    "Printed note 6 says Correr owned a view of Venice attributed to Canaletto but now thought to come from his studio.",
    "qualified attribution report", "Both the former attribution and revised studio-work assessment are reported by Haskell, not independently checked.", ["cand-0857", "cand-2719", "cand-0498", "cand-10720"], True,
    footnote_data={"footnote_marker": "6", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L13-L13", "footnote_body_link_status": "linked", "footnote_text_pending": False})
make_statement("note6-castel-cogolo-view", NOTES, "cand-0857", "cand-10721",
    "owned_damaged_castel_cogolo_view_probably_by_francesco_guardi", 29, 29,
    "Printed note 6 says Correr owned a damaged view of Castel Cogolo probably painted by Francesco Guardi.",
    "qualified attribution report", "The attribution remains explicitly probable and is not independently checked.", ["cand-0857", "cand-10721", "cand-1239"], True,
    footnote_data={"footnote_marker": "6", "footnote_body_segment_id": BODY, "footnote_body_line_range": "L13-L13", "footnote_body_link_status": "linked", "footnote_text_pending": False})

new_mentions = {row["mention_id"] for row in planned_mentions}
if len(new_mentions) != len(planned_mentions) or any(row["mention_id"] in {item["mention_id"] for item in mentions} for row in planned_mentions):
    raise SystemExit("one or more p.382 mention IDs already exist")
for row in planned_mentions:
    if row["candidate_id"] not in candidate_by_id:
        raise SystemExit(f"missing candidate for {row['mention_id']}")
    text = segment_texts[row["segment_id"]]
    start, end = int(row["start_char"]), int(row["end_char"])
    if text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span failed exact-source check: {row['mention_id']}")
for row in statements:
    if row.get("statement_id", "").startswith("st-chp17-p382-"):
        for key in ("subject_candidate_id", "object_candidate_id"):
            value = row.get(key)
            if value and value not in candidate_by_id:
                raise SystemExit(f"missing {key} in {row['statement_id']}: {value}")

coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L7-17",
    "note": "Printed p.382 body checked against CHP-17.pdf physical page 4. L8 closes the p.381 sentence; L9-14 and the p.382 printed note 4 at L16-17 are migrated. The final clause at L15 continues on p.383 and remains open.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L25-29",
    "note": "Printed p.382 notes 1-3, 5-6 at L25-29 are migrated and linked to body claims; printed note 4 is transcribed at body L16-17. Notes at L30-33 belong to p.383 and remain queued.",
})

if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidate_specs),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "coverage_updates": {BODY: "reviewed/partial", NOTES: "reviewed/partial"},
        "candidate_ids": [item[0] for item in new_candidate_specs],
        "statement_ids": new_statement_ids,
        "notes_remaining": "p.383 notes L30-33",
        "body_continuation": "p.383 closes L15",
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
