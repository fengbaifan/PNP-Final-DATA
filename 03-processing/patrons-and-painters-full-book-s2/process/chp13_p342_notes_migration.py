"""Controlled S2 migration for printed p.342 notes; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l98-105"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p342-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.342 note migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_fragments = {
    227: "The seven letters from Tessin are dated 23 September 1736",
    228: "The present quotation comes from the last of these letters.",
    229: "From the first and third letters. There is no indication who the painter was.",
    230: "From the third letter:",
    231: "Third letter—see also Chapter 10.",
    232: "Two of Zanetti’s Sebastiano Riccis",
    233: "Letter to A. F. Gori of 22 December 1752.",
    234: "all’esclusione della tazza d’Annibale",
}
for line_number, fragment in expected_fragments.items():
    if fragment not in source_lines[line_number - 1]:
        raise SystemExit(f"source line L{line_number} changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

table_state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if table_state != (10191, 10204, 22062, 9850):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
if BODY not in coverage or NOTES not in coverage:
    raise SystemExit("p.342 body or consolidated notes coverage row missing")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.342 body is not reviewed/partial with page notes pending")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated chapter 13 notes are not reviewed/partial")
if coverage[NOTES]["source_line_ranges"] != "L180-226":
    raise SystemExit("consolidated-notes cursor changed")
if any(row["segment_id"] == NOTES and row["mention_id"].startswith("m-s2-ch13-p342-notes-") for row in mentions):
    raise SystemExit("p.342 note mentions already exist")
if any(row["segment_id"] == NOTES and row["statement_id"].startswith("st-chp13-p342-notes-") for row in statements):
    raise SystemExit("p.342 note statements already exist")

body_note_targets = {
    "1": [
        "st-chp13-p342-tessin_used_zanetti_taste_and_scholarship",
        "st-chp13-p342-tessin_sent_protege_to_zanetti_for_instruction",
    ],
    "2": ["st-chp13-p342-young_protege_died"],
    "3": [
        "st-chp13-p342-tessin_sent_messages_to_tiepolo_through_zanetti",
        "st-chp13-p342-swedish_king_refused_tiepolo_sum",
    ],
    "4": [
        "st-chp13-p342-tessin_bought_zuccarelli_pictures",
        "st-chp13-p342-tessin_bought_nogari_pictures",
        "st-chp13-p342-tessin_bought_crespi_prints",
        "st-chp13-p342-zanetti_facilitated_gai_commission",
        "st-chp13-p342-tessin_assessed_gai_as_half_michelangelo",
        "st-chp13-p342-gai_figure_intended_to_pair_with_tessins_bathsheba",
        "st-chp13-p342-tessin_owned_giovanni_da_bologna_bathsheba",
    ],
    "5": [
        "st-chp13-p342-zanetti_owned_three_sebastiano_history_paintings",
        "st-chp13-p342-zanetti_brought_medals_and_gems_from_european_cities",
        "st-chp13-p342-zanetti_had_large_print_collection",
    ],
    "6": [
        "st-chp13-p342-zanetti_1752_described_print_collection",
        "st-chp13-p342-zanetti_was_proud_of_print_collection",
    ],
    "7": ["st-chp13-p342-zanetti_1752_rare_print_exception_fragment"],
}
for marker, ids in body_note_targets.items():
    for statement_id in ids:
        if statement_id not in statement_by_id:
            raise SystemExit(f"p.342 footnote {marker} target missing: {statement_id}")
        qualifiers = statement_by_id[statement_id].get("qualifiers", {})
        refs = qualifiers.get("footnote_refs", [])
        if not any(
            ref.get("footnote_marker") == marker
            and ref.get("footnote_printed_page") == 342
            and ref.get("footnote_text_pending")
            for ref in refs
        ):
            if marker == "5" and statement_id == "st-chp13-p342-zanetti_owned_three_sebastiano_history_paintings" and not refs:
                continue
            raise SystemExit(f"p.342 footnote {marker} is not pending on {statement_id}")

new_candidate_ids = {f"cand-{number}" for number in range(10205, 10214)}
if new_candidate_ids & set(candidate_by_id):
    raise SystemExit(f"candidate IDs already exist: {sorted(new_candidate_ids & set(candidate_by_id))}")
new_candidates = []


def add_candidate(candidate_id, name, kind, detail, line_number):
    if any(row["canonical_name"].casefold() == name.casefold() for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)


candidate_specs = [
    ("cand-10205", "Seven letters from Count Tessin recorded in Cod. CXVI, 7356 (1736–1748)", "archive",
     "P.342 notes 1–4 describe seven Tessin letters in the cited Biblioteca Marciana manuscript volume. Preserve the printed date discrepancy for the Copenhagen letter (26 October 1743, sic—but 1748) and the place spelling Strahlsund as printed. The letters and manuscript have not been consulted; do not create seven separately titled letter records from this summary alone.", 227),
    ("cand-10206", "Raccolta di Opere scelte (publication cited in p.342 note 5)", "archive",
     "P.342 note 5 says Pietro Monaco's engravings nos. 41 and 84 appeared in this titled publication. No publisher, date, edition, or copy locator is supplied in this note; the publication has not been consulted.", 232),
    ("cand-10207", "Pietro Monaco engraving no. 41 after Esther and Ahasuerus", "work",
     "P.342 note 5 identifies this as the engraving of Sebastiano Ricci's Esther and Ahasuerus included as no. 41 in Raccolta di Opere scelte. The print itself and publication were not consulted.", 232),
    ("cand-10208", "Pietro Monaco engraving no. 84 after The Presentation in the Temple", "work",
     "P.342 note 5 identifies this as the engraving of Sebastiano Ricci's The Presentation in the Temple included as no. 84 in Raccolta di Opere scelte. The print itself and publication were not consulted.", 232),
    ("cand-10209", "Portrait of A. M. Zanetti by Rosalba Carriera (frontispiece to the 1749 Dactyliotheca)", "work",
     "P.342 note 5 reports that a portrait of Zanetti by Rosalba Carriera served as the frontispiece to his Dactyliotheca in 1749. The note gives no medium, present location, or further portrait identification; the work was not consulted.", 232),
    ("cand-10210", "Letter to A. F. Gori, 22 December 1752 (Biblioteca Marucelliana, B. VIII, 13, p. 400)", "archive",
     "P.342 note 6 identifies the letter quoted in the body and gives its repository and shelfmark locator. The letter and catalogue were not independently consulted.", 233),
    ("cand-10211", "Kurz (author cited in 1955; full identity unspecified)", "person",
     "P.342 note 7 cites Kurz, 1955, pages 282–287. The note supplies no given name or title; author identity remains unresolved.", 234),
    ("cand-10212", "Kurz, 1955, pp. 282–287 (short-form cited publication; title unresolved)", "archive",
     "Short-form bibliographic reference in p.342 note 7. The title, edition, and full author identity are not supplied in the note; the cited pages have not been consulted.", 234),
    ("cand-10213", "Strahlsund (place name as printed in p.342 note 1; identity pending)", "place",
     "Printed spelling retained from the 1931 edition. Do not normalize it to another place-name before S3 identity alignment; the cited letter and place are not independently verified.", 227),
]
for spec in candidate_specs:
    add_candidate(*spec)

# Reuse previously indexed entities and extend their S2 context without making identity decisions.
candidate_by_id["cand-10192"]["canonical_name"] = "G. Lorenzetti, 1917 (short-form cited source; title unresolved)"
candidate_by_id["cand-10192"]["detail"] = (
    "Short-form citation used in p.341 notes 1–3 (pp.138, 145) and p.342 note 5 (p.75). "
    "No title or edition is supplied here and the cited work has not been consulted. "
    "Keep distinct from similarly abbreviated citations pending global S3 alignment."
)
candidate_by_id["cand-2163"]["suggested_type"] = "work"
candidate_by_id["cand-2163"]["detail"] = (
    "Index subentry Esther and Ahasuerus; p.342 note 5 identifies this as one of Zanetti's "
    "Sebastiano Ricci paintings and says Pietro Monaco engraved it as no. 41 in Raccolta di Opere scelte. "
    "The cited print and source pages were not independently consulted."
)
candidate_by_id["cand-2175"]["detail"] += (
    " P.342 note 5 also identifies it as one of Zanetti's Sebastiano Ricci paintings and says Pietro Monaco "
    "engraved it as no. 84 in Raccolta di Opere scelte; neither source was independently consulted."
)
candidate_by_id["cand-1682"]["suggested_type"] = "person"
candidate_by_id["cand-1682"]["detail"] = (
    "P.342 note 5 names Pietro Monaco as engraver of nos. 41 and 84 in Raccolta di Opere scelte. "
    "No further identity evidence is supplied here; compare other Monaco candidates and print references at S3."
)

all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
notes_text = "\n".join(source_lines[178:251])
line_offsets = {}
offset = 0
for line_number in range(179, 252):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

new_mentions = []
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}


def add_mention(line_number, surface, candidate_id, note="", occurrence=0):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line_text = source_lines[line_number - 1]
    positions, cursor = [], 0
    while True:
        at = line_text.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line_number}: {surface!r}")
    start = line_offsets[line_number] + positions[occurrence]
    end = start + len(surface)
    if notes_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (NOTES, candidate_id, str(start), str(end))
    if key in existing_mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p342-notes-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    })
    new_mentions.append(row)


mention_specs = [
    (227, "Biblioteca Marciana, Venice-—MSS. Italiani—Cl. XI, Cod. CXVI, 7356", "cand-10199", "Printed manuscript locator; no catalogue verification."),
    (227, "Biblioteca Marciana", "cand-9448", "Reuse the repository candidate; no catalogue verification."),
    (227, "The seven letters from Tessin", "cand-10205", "Aggregate description in the printed note; do not split into seven new records."),
    (227, "Tessin", "cand-2554"),
    (227, "23 September 1736", "cand-10205"),
    (227, "Vienna", "cand-2772"),
    (227, "9 November 1736", "cand-10205"),
    (227, "Strahlsund", "cand-10213", "Place spelling retained as printed; S3 identity pending."),
    (227, "12 March 1737", "cand-10205"),
    (228, "20 April 1744", "cand-10205"),
    (228, "5 April 1748", "cand-10205"),
    (228, "11 June 1748", "cand-10205"),
    (228, "Stockholm", "cand-4790"),
    (228, "26 October 1743 (—but 1748)", "cand-10205", "S0 omits printed sic; S2 records 1743 (sic—but 1748) from the scan without rewriting S0."),
    (228, "Copenhagen", "cand-9287"),
    (228, "the last of these letters", "cand-10205", "The note says the present quotation comes from this last letter."),
    (229, "ibid.", "cand-10199", "Reference to the manuscript volume in note 1."),
    (229, "first and third letters", "cand-10205"),
    (229, "the painter", "cand-10077", "The note says the letters do not identify the young painter."),
    (230, "ibid.", "cand-10199", "Reference to the manuscript volume in note 1."),
    (230, "third letter", "cand-10205"),
    (230, "Sr Tiepolo", "cand-2569"),
    (231, "ibid.", "cand-10199", "Reference to the manuscript volume in note 1."),
    (231, "Third letter", "cand-10205"),
    (232, "Lorenzetti, 1917, p. 75", "cand-10192", "Cited page not consulted."),
    (232, "Lorenzetti", "cand-9947", "Reuse surname-only cited-author candidate."),
    (232, "Bottari, II, pp. 129 and 179 ff.", "cand-7516", "Reuse cited volume candidate; pages not consulted."),
    (232, "Bottari", "cand-0417", "Reuse cited-author candidate."),
    (232, "Zanetti’s Sebastiano Riccis", "cand-10087", "The note identifies two members of the three-painting group."),
    (232, "Esther and Ahasuerus", "cand-2163"),
    (232, "The Presentation in the Temple", "cand-2175"),
    (232, "Pietro Monaco", "cand-1682", "Reuse the indexed person candidate; global identity alignment with other Monaco records is for S3."),
    (232, "Raccolta di Opere scelte", "cand-10206", "Title of the cited print publication; not independently consulted."),
    (232, "Nos. 41 and 84", "cand-10206", "The note maps no. 41 to Esther and Ahasuerus and no. 84 to The Presentation in the Temple."),
    (232, "Zanetti", "cand-2838", "First occurrence in note 5."),
    (232, "A portrait of Zanetti by Rosalba Carriera", "cand-10209", "Distinct portrait work; no medium or present location supplied."),
    (232, "Zanetti", "cand-2838", "Second occurrence in note 5; sitter of the portrait.", 1),
    (232, "Rosalba Carriera", "cand-0581"),
    (232, "Dactyliotheca", "cand-10012"),
    (233, "Biblioteca Marucelliana, Florence—MSS. B. VIII, 13, p. 400", "cand-9493", "Reuse repository candidate; do not treat this as a current catalogue check."),
    (233, "Florence", "cand-3397"),
    (233, "Letter to A. F. Gori of 22 December 1752", "cand-10210", "The archive item cited for the p.342 first-person quotation; not independently consulted."),
    (233, "A. F. Gori", "cand-1214"),
    (234, "all’esclusione della tazza d’Annibale, intagliata in una sottocoppa, rappresentante un Baccanale", "cand-10090", "Italian wording quoted in the note; retain without adding an unverified translation or medium."),
    (234, "tazza d’Annibale", "cand-10090"),
    (234, "Annibale", "cand-0576"),
    (234, "Kurz, 1955, pp. 282-7", "cand-10212", "Cited publication locator; cited pages not consulted."),
    (234, "Kurz", "cand-10211", "Surname only; full identity unresolved."),
]
for spec in mention_specs:
    add_mention(*spec)

ocr_corrections = [
    {"source_line": 227, "ocr": "Venice-—MSS.", "print": "Venice—MSS.", "basis": "CHP-13.pdf physical page 11."},
    {"source_line": 228, "ocr": "1748,11 June 1748", "print": "1748, 11 June 1748", "basis": "CHP-13.pdf physical page 11."},
    {"source_line": 228, "ocr": "26 October 1743 (—but 1748)", "print": "26 October 1743 (sic—but 1748)", "basis": "CHP-13.pdf physical page 11."},
    {"source_line": 230, "ocr": "éloigné", "print": "éloigne", "basis": "CHP-13.pdf physical page 11."},
]

new_statement_specs = [
    {
        "id": "st-chp13-p342-notes-note1-tessin-seven-letter-dates",
        "marker": "1", "line_start": 227, "line_end": 228,
        "subject": "cand-10199", "object": "cand-10205",
        "predicate": "manuscript_note_lists_seven_tessin_letter_dates_and_places",
        "claim": "P.342 note 1 lists seven Tessin letters in the cited Marciana volume: 23 September 1736 from Vienna; 9 November 1736 from Strahlsund; 12 March 1737; 20 April 1744; 5 April and 11 June 1748 from Stockholm; and 26 October 1743, explicitly corrected in print as 1748, from Copenhagen. It says the present quotation comes from the last letter.",
        "qualification": "This is Haskell's printed description of the cited manuscript. Preserve the printed sic correction and place spelling; the letters and manuscript were not consulted.",
        "mentioned": ["cand-10199", "cand-10205", "cand-2554", "cand-2772", "cand-10213", "cand-4790", "cand-9287"],
        "citations": [{"source_candidate_id": "cand-10199", "letters_group_candidate_id": "cand-10205", "date_list_as_printed": "1736-09-23; 1736-11-09; 1737-03-12; 1744-04-20; 1748-04-05; 1748-06-11; 1743 (sic—but 1748)-10-26", "places_as_printed": ["Vienna", "Strahlsund", "Stockholm", "Copenhagen"]}],
        "linked": body_note_targets["1"], "ocr_corrections": ocr_corrections[:3],
    },
    {
        "id": "st-chp13-p342-notes-note2-painter-unidentified",
        "marker": "2", "line_start": 229, "line_end": 229,
        "subject": "cand-10205", "object": "cand-10077",
        "predicate": "first_and_third_letters_do_not_identify_the_young_painter",
        "claim": "The note refers to the first and third Tessin letters and says they do not indicate who the young painter was.",
        "qualification": "Keep the protégé's identity unresolved; do not infer it from the painter's later death or from another passage.",
        "mentioned": ["cand-10205", "cand-10077"],
        "citations": [{"source_candidate_id": "cand-10205", "letter_order": [1, 3]}],
        "linked": body_note_targets["2"],
    },
    {
        "id": "st-chp13-p342-notes-note3-tessin-letter-about-tiepolo",
        "marker": "3", "line_start": 230, "line_end": 230,
        "subject": "cand-10205", "object": "cand-2569",
        "predicate": "third_letter_discusses_tiepolo_and_offers_hosting",
        "claim": "The note quotes the third Tessin letter asking Zanetti to report on Sr Tiepolo. The letter says price is the remaining obstacle, that Tiepolo would not regret accepting, and that Tessin would offer him room and board in his house in addition to the King's pension.",
        "qualification": "French quotation transcribed by Haskell; preserve its wording and old spelling. The letter was not independently consulted.",
        "mentioned": ["cand-10205", "cand-2554", "cand-2838", "cand-2569"],
        "citations": [{"source_candidate_id": "cand-10205", "letter_order": 3, "recipient_candidate_id": "cand-2838"}],
        "linked": body_note_targets["3"], "ocr_corrections": [ocr_corrections[3]],
    },
    {
        "id": "st-chp13-p342-notes-note4-third-letter-cross-reference",
        "marker": "4", "line_start": 231, "line_end": 231,
        "subject": "cand-10205", "object": "cand-10082",
        "predicate": "third_letter_cited_for_the_gai_figure_passage",
        "claim": "The note identifies the third Tessin letter as the source for the preceding figure passage and directs readers to Chapter 10 as well.",
        "qualification": "This preserves Haskell's cross-reference and source locator; Chapter 10 is not treated as a second independent source.",
        "mentioned": ["cand-10205", "cand-10082", "cand-10083"],
        "citations": [{"source_candidate_id": "cand-10205", "letter_order": 3}],
        "linked": body_note_targets["4"], "cross_reference_text": "Chapter 10",
    },
    {
        "id": "st-chp13-p342-notes-note5-zanetti-owned-esther-and-ahasuerus",
        "marker": "5", "line_start": 232, "line_end": 232,
        "subject": "cand-2838", "object": "cand-2163",
        "predicate": "owned_esther_and_ahasuerus_by_sebastiano_ricci",
        "claim": "P.342 note 5 identifies Esther and Ahasuerus as one of the Sebastiano Ricci paintings in Zanetti's collection.",
        "qualification": "The note supplies a title and attribution through Haskell's cited references; neither the cited pages nor the painting were independently consulted.",
        "mentioned": ["cand-2838", "cand-2163", "cand-2154", "cand-10192", "cand-9947", "cand-7516", "cand-0417"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917", "page": "75"}, {"source_candidate_id": "cand-7516", "author_candidate_id": "cand-0417", "volume": "II", "pages": ["129", "179 ff."]}],
        "linked": body_note_targets["5"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p342-notes-note5-zanetti-owned-presentation-in-temple",
        "marker": "5", "line_start": 232, "line_end": 232,
        "subject": "cand-2838", "object": "cand-2175",
        "predicate": "owned_presentation_in_the_temple_by_sebastiano_ricci",
        "claim": "P.342 note 5 identifies The Presentation in the Temple as another Sebastiano Ricci painting in Zanetti's collection.",
        "qualification": "The note supplies a title and attribution through Haskell's cited references; neither the cited pages nor the painting were independently consulted.",
        "mentioned": ["cand-2838", "cand-2175", "cand-2154", "cand-10192", "cand-9947", "cand-7516", "cand-0417"],
        "citations": [{"source_candidate_id": "cand-10192", "author_candidate_id": "cand-9947", "year": "1917", "page": "75"}, {"source_candidate_id": "cand-7516", "author_candidate_id": "cand-0417", "volume": "II", "pages": ["129", "179 ff."]}],
        "linked": body_note_targets["5"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p342-notes-note5-monaco-engraved-esther-no41",
        "marker": "5", "line_start": 232, "line_end": 232,
        "subject": "cand-1682", "object": "cand-10207",
        "predicate": "engraved_esther_and_ahasuerus_as_raccolta_no_41",
        "claim": "The note says Pietro Monaco engraved Esther and Ahasuerus as no. 41 in Raccolta di Opere scelte.",
        "qualification": "This is a reported print attribution; the print and publication were not consulted. Identity alignment among Monaco candidates remains for S3.",
        "mentioned": ["cand-1682", "cand-10207", "cand-2163", "cand-10206"],
        "citations": [{"source_candidate_id": "cand-10206", "print_number": 41, "after_work_candidate_id": "cand-2163"}],
        "linked": body_note_targets["5"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p342-notes-note5-monaco-engraved-presentation-no84",
        "marker": "5", "line_start": 232, "line_end": 232,
        "subject": "cand-1682", "object": "cand-10208",
        "predicate": "engraved_presentation_in_temple_as_raccolta_no_84",
        "claim": "The note says Pietro Monaco engraved The Presentation in the Temple as no. 84 in Raccolta di Opere scelte.",
        "qualification": "This is a reported print attribution; the print and publication were not consulted. Identity alignment among Monaco candidates remains for S3.",
        "mentioned": ["cand-1682", "cand-10208", "cand-2175", "cand-10206"],
        "citations": [{"source_candidate_id": "cand-10206", "print_number": 84, "after_work_candidate_id": "cand-2175"}],
        "linked": body_note_targets["5"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p342-notes-note5-carriera-portrait-frontispiece",
        "marker": "5", "line_start": 232, "line_end": 232,
        "subject": "cand-0581", "object": "cand-10209",
        "predicate": "portrait_of_zanetti_used_as_dactyliotheca_frontispiece_in_1749",
        "claim": "The note says a portrait of Zanetti by Rosalba Carriera was used as the frontispiece to his Dactyliotheca in 1749.",
        "qualification": "Do not equate this portrait with the pastels or miniatures mentioned in the p.342 body. Medium and present location are not supplied; portrait and book were not consulted.",
        "mentioned": ["cand-0581", "cand-10209", "cand-2838", "cand-10012"],
        "citations": [{"source_candidate_id": "cand-10012", "publication_year": 1749, "use": "frontispiece"}],
        "linked": body_note_targets["5"], "relation_candidate": True,
    },
    {
        "id": "st-chp13-p342-notes-note6-letter-to-gori-locator",
        "marker": "6", "line_start": 233, "line_end": 233,
        "subject": "cand-10210", "object": "cand-9493",
        "predicate": "letter_to_gori_located_in_marucelliana_b_viii_13_page_400",
        "claim": "P.342 note 6 locates the 22 December 1752 letter to A. F. Gori at Biblioteca Marucelliana, MSS. B. VIII, 13, page 400.",
        "qualification": "Repository and shelfmark are transcribed from Haskell's printed note; the letter and catalogue were not independently consulted.",
        "mentioned": ["cand-10210", "cand-9493", "cand-1214", "cand-3397"],
        "citations": [{"source_candidate_id": "cand-10210", "repository_candidate_id": "cand-9493", "recipient_candidate_id": "cand-1214", "shelfmark_as_printed": "MSS. B. VIII, 13, p. 400", "date": "1752-12-22"}],
        "linked": body_note_targets["6"],
    },
    {
        "id": "st-chp13-p342-notes-note7-zanetti-italian-exclusion-quote",
        "marker": "7", "line_start": 234, "line_end": 234,
        "subject": "cand-10090", "object": "cand-10212",
        "predicate": "note_quotes_italian_exclusion_phrase_and_cites_kurz_1955",
        "claim": "P.342 note 7 gives Zanetti's Italian wording for the Annibale dish exception and cites Kurz, 1955, pages 282–287.",
        "qualification": "The Italian quotation is preserved as printed. The cited pages were not consulted; do not extend this note's support to the Giulio Romano prints that follow in the open p.342 quotation.",
        "mentioned": ["cand-10090", "cand-2838", "cand-0576", "cand-10211", "cand-10212"],
        "citations": [{"source_candidate_id": "cand-10212", "author_candidate_id": "cand-10211", "year": "1955", "pages": "282–287"}],
        "linked": body_note_targets["7"],
    },
]

new_statements = []
note_statement_ids_by_marker = {str(n): [] for n in range(1, 8)}
for spec in new_statement_specs:
    for candidate_id in spec["mentioned"]:
        if candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement candidate missing: {spec['id']} -> {candidate_id}")
    quote = "\n".join(source_lines[spec["line_start"] - 1:spec["line_end"]])
    qualifiers = {
        "source_line_start": spec["line_start"],
        "source_line_end": spec["line_end"],
        "printed_page": 342,
        "pdf_physical_page": 11,
        "claim": spec["claim"],
        "speaker": "Haskell, printed footnote",
        "text_layer": "secondary source note and citation",
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "footnote_marker": spec["marker"],
        "footnote_printed_page": 342,
        "linked_body_statement_ids": spec["linked"],
        "citations": spec["citations"],
    }
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    if spec.get("ocr_corrections"):
        qualifiers["ocr_corrections"] = spec["ocr_corrections"]
    if spec.get("cross_reference_text"):
        qualifiers["cross_reference_text"] = spec["cross_reference_text"]
    new_statements.append({
        "statement_id": spec["id"],
        "segment_id": NOTES,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec["object"],
        "predicate": spec["predicate"],
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })
    note_statement_ids_by_marker[spec["marker"]].append(spec["id"])

# Link each printed note only to the body claims assigned to that marker.
for marker, body_ids in body_note_targets.items():
    note_ids = note_statement_ids_by_marker[marker]
    if not note_ids:
        raise SystemExit(f"no note statements for marker {marker}")
    for statement_id in body_ids:
        qualifiers = statement_by_id[statement_id].setdefault("qualifiers", {})
        refs = qualifiers.setdefault("footnote_refs", [])
        matching = [
            ref for ref in refs
            if ref.get("footnote_marker") == marker and ref.get("footnote_printed_page") == 342
        ]
        # Note 5's marker follows the collection paragraph and names two of its Ricci paintings;
        # add its explicit missing target without broadening it to the distinct Carriera portrait.
        if not matching and marker == "5" and statement_id == "st-chp13-p342-zanetti_owned_three_sebastiano_history_paintings":
            matching = [{
                "footnote_marker": marker,
                "footnote_printed_page": 342,
                "footnote_text_pending": True,
                "footnote_segment": NOTES,
                "footnote_line_range": "L232",
                "footnote_body_link_status": "pending",
            }]
            refs.extend(matching)
        if not matching:
            raise SystemExit(f"p.342 footnote {marker} missing from {statement_id}")
        for ref in matching:
            ref["footnote_text_pending"] = False
            ref["footnote_body_link_status"] = "linked"
            ref["footnote_note_statement_ids"] = note_ids
        qualifiers["footnote_note_statement_ids"] = sorted(set(qualifiers.get("footnote_note_statement_ids", [])) | set(note_ids))
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"

# The p.342 body sentence fragment carries only the first named exception, the Annibale dish.
# The following Giulio Romano item is separately recorded when p.343 closes the quotation.
rare = statement_by_id["st-chp13-p342-zanetti_1752_rare_print_exception_fragment"]
rare_q = rare.setdefault("qualifiers", {})
rare_q["claim"] = "In the 1752 quotation, Zanetti says he could hope to show any rare print requested except the dish engraved with a Bacchanal by Annibale."
rare_q["qualification"] = (
    "This p.342 statement covers only the first named exception; footnote 7 quotes the dish clause. "
    "The next Giulio Romano item begins in this source line and closes at p.343 L108, where it is recorded separately. "
    "Do not infer why either item was excepted."
)
rare_q["mentioned_candidate_ids"] = ["cand-2838", "cand-2850", "cand-10090", "cand-0576"]
rare["predicate"] = "said_any_rare_print_except_annibale_dish"

for marker, body_ids in body_note_targets.items():
    for statement_id in body_ids:
        refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
        if any(ref.get("footnote_marker") == marker and ref.get("footnote_text_pending") for ref in refs):
            raise SystemExit(f"footnote {marker} remains pending on {statement_id}")

for row in new_statements:
    if row["original_quote"] not in notes_text:
        raise SystemExit(f"statement quote not found in source segment: {row['statement_id']}")
for row in new_mentions:
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"final mention span failed: {row['mention_id']}")

coverage[NOTES]["source_line_ranges"] = "L180-234"
coverage[NOTES]["note"] = (
    "Notes L180-226 (pp.332-341) and p.342 notes 1-7 at L227-234 are migrated and linked to their marked body claims. "
    "The printed sic correction for the 1748 Copenhagen letter, note 3's French wording, and the p.342 Annibale dish clause "
    "are preserved with their source limits. L235-246 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."
)
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L98-105"
coverage[BODY]["note"] = (
    "Printed p.342 body and notes 1-7 were checked against CHP-13.pdf physical page 11 and linked to their marked claims. "
    "The open L105 quotation closes at p.343 L108; its Annibale dish and Giulio Romano prints are kept as separate items. "
    "OCR corrections are recorded in S2 only; cited letters, manuscripts, publications, and artworks were not independently consulted."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = [statement_by_id.get(row["statement_id"], row) for row in statements] + new_statements
if len({r["candidate_id"] for r in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique after migration")
if len({r["mention_id"] for r in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique after migration")
if len({r["statement_id"] for r in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique after migration")

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage: p.342 body partial -> complete; consolidated notes advance L180-226 -> L180-234 and remain partial")
print("footnotes 1-7 linked to the p.342 body; note 5 adds the titled Ricci painting target")
print("print corrections recorded only in S2: Venice dash; date spacing and sic; French éloigné -> éloigne")
print("cited letters, manuscripts, publications, and artworks were not independently consulted")
if not args.apply:
    print("dry-run only; review this delta before rerunning with --apply")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
if any(path.exists() for path in backups):
    raise SystemExit("one or more migration backup paths already exist")
for original, backup in zip(targets, backups):
    shutil.copy2(original, backup)
write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied with four table backups:")
for path in backups:
    print(f"  {path.relative_to(ROOT)}")
