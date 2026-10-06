"""Controlled S2 migration for printed p.339 footnotes; dry-run by default."""
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
BODY = "chp-13:13_CHP-13_intro:l70-77"
PREVIOUS_BODY = "chp-13:13_CHP-13_intro:l61-68"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
NOTES_SHA = "f592d5913122cf2c4c2e7db9a39b8016c82dbc232a869018793ef11096faacb9"
BACKUP_SUFFIX = ".bak-s2-chp13-p339-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.339 footnote migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for number, prefix in {
    211: "1 Archi vio di Stato, Venice—Inquisitori di Stato, 535, p. 173, 18 Giugno 1759, and 536, p. 4IV,",
    212: "19 Novembre 17Ó0.",
    213: "2 ‘. . . terziario, a quel die pare, dei Gesuiti,’ wrote Giovanni de Cattaneo",
    214: "3 Lettera del Magnifico Signor Antonio Zatta",
    215: "4 Catalogo di Libri latini c italiani",
    216: "8 Catalogo di quadri raccolti dal fu Signor Maffeo Pinelli",
}.items():
    if not source_lines[number - 1].startswith(prefix):
        raise SystemExit(f"canonical source changed at L{number}")

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
    len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions), len(statements),
)
if table_state != (10166, 10179, 21985, 9823):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
if hashlib.sha256("\n".join(source_lines[178:251]).encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("consolidated notes segment L179-L251 changed")
for segment_id in (BODY, PREVIOUS_BODY, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f"required coverage row missing: {segment_id}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.339 body is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes segment is not reviewed/partial")
if coverage[NOTES]["source_line_ranges"] != "L180-210":
    raise SystemExit("consolidated notes coverage cursor changed")

candidate_specs = [
    ("cand-10180", "Archivio di Stato, Venice, Inquisitori di Stato 535, p.173 (18 June 1759)", "archive",
     "Archival citation printed in p.339 note 1. The record itself has not been independently consulted.", 211),
    ("cand-10181", "Archivio di Stato, Venice, Inquisitori di Stato 536, p.41v (19 November 1760)", "archive",
     "Archival citation printed in p.339 note 1. The printed page reads 41v; the record itself has not been independently consulted.", 211),
    ("cand-10182", "Nouvelles Ecclésiastiques (periodical cited in p.339 note 2)", "archive",
     "Cited as the source of a description of Antonio Zatta; no issue, date, or article title is supplied in this note.", 213),
    ("cand-10183", "Neri, 1899, pp.109 and 114 (work title unspecified in p.339 note 2)", "archive",
     "Short-form citation used for two quotations concerning Zatta. The work title and cited pages have not been independently established here.", 213),
    ("cand-10184", "Catalogo di Libri latini e italiani che trovansi vendibili nel negozio di Antonio Zatta e figli Libraj Stampatori in Venezia (1790)", "archive",
     "Catalogue cited in p.339 note 4. Title normalized against the scan; the catalogue itself has not been consulted.", 215),
    ("cand-10185", "G. da Venezia, 1934, pp.25-34 (title unspecified in p.339 note 5)", "archive",
     "Short-form citation printed in p.339 note 5. Do not expand the author initials or invent a title from this citation alone.", 215),
    ("cand-10186", "Catalogo di quadri raccolti dal fu Signor Maffeo Pinelli ed ora posti in vendita in Venezia (1785)", "archive",
     "Sale catalogue cited in p.339 note 6 for Pinelli's picture collection. The catalogue itself has not been consulted.", 216),
    ("cand-10187", "G. A. Moschini, 1806, volume II, p.64 (title unresolved)", "archive",
     "Short-form bibliographic citation printed in p.339 note 6; reuse the existing Moschini author candidate only if later bibliography processing identifies it.", 216),
]
new_candidates = []
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
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
all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
for candidate_id in ("cand-0610", "cand-1321", "cand-1932", "cand-2865", "cand-3401", "cand-10178", "cand-10024"):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"required candidate is missing: {candidate_id}")

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
    positions = []
    cursor = 0
    while True:
        position = line_text.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
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
        "mention_id": f"m-s2-ch13-p339-notes-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    })
    new_mentions.append(row)


def add_cross_line_mention(first_line, last_line, start_text, end_text, candidate_id, note=""):
    local_text = "\n".join(source_lines[first_line - 1:last_line])
    start = local_text.find(start_text)
    end_start = local_text.find(end_text, start)
    if start < 0 or end_start < 0:
        raise SystemExit(f"cross-line mention boundary missing: {start_text!r}/{end_text!r}")
    surface = local_text[start:end_start + len(end_text)]
    absolute_start = line_offsets[first_line] + start
    absolute_end = absolute_start + len(surface)
    if notes_text[absolute_start:absolute_end] != surface:
        raise SystemExit(f"cross-line mention offset mismatch: {surface!r}")
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for cross-line mention: {candidate_id}")
    key = (NOTES, candidate_id, str(absolute_start), str(absolute_end))
    if key in existing_mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate cross-line mention: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p339-notes-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": absolute_start,
        "end_char": absolute_end,
        "note": note,
    })
    new_mentions.append(row)


add_mention(211, "Archi vio di Stato, Venice—Inquisitori di Stato, 535, p. 173, 18 Giugno 1759", "cand-10180",
            "S0 OCR splits Archivio; the scan reads Archivio. The archival record remains unconsulted.")
add_mention(211, "Venice", "cand-3401", "Repository location in the printed citation.")
add_cross_line_mention(211, 212, "536, p. 4IV,", "19 Novembre 17Ó0", "cand-10181",
                       "The citation continues on L212; scan reads p.41V and 1760.")
add_mention(213, "terziario, a quel die pare, dei Gesuiti", "cand-1321",
            "The scan reads che where OCR has die; preserve the source span.")
add_mention(213, "Giovanni de Cattaneo", "cand-0610", "Named as the first quoted reporter; the quotation is mediated by Neri, 1899.")
add_mention(213, "Zatta", "cand-2865", "Named in the second quoted description.")
add_mention(213, "Nouvelles Ecclésiastiques", "cand-10182", "Periodical named as the source of the second description.")
add_mention(213, "Neri, 1899, pp. 109 and 114", "cand-10183", "Intermediate bibliographic citation for both quotations; title unspecified here.")
add_mention(214, "Lettera del Magnifico Signor Antonio Zatta", "cand-10178",
            "Same cited title is cross-referenced to p.338 note 2; p.23 is the locator for the p.339 vignette passage.")
add_mention(214, "Antonio Zatta", "cand-2865", "Author named in the cited letter title.")
add_mention(215, "Catalogo di Libri latini c italiani che trovansi vendibili nel negozio di Antonio Zatta efigli Libraj Stampatori in Venezia, 1790", "cand-10184",
            "S0 OCR has c/efigli; scan reads e/e figli. Preserve OCR surface and record print readings in qualifiers.")
add_mention(215, "Antonio Zatta", "cand-2865", "Publisher named in the catalogue title.")
add_mention(215, "G. da Venezia, 1934, pp. 25-34", "cand-10185",
            "The scan reads pp.25-34. The short form does not supply a title or expanded author name.")
add_mention(216, "Catalogo di quadri raccolti dal fu Signor Maffeo Pinelli ed ora posti in vendita in Venezia, 1785", "cand-10186",
            "Sale catalogue title normalized from the scan; the publication itself has not been consulted.")
add_mention(216, "Maffeo Pinelli", "cand-1932", "Person named in the sale-catalogue title.")
add_mention(216, "Venezia", "cand-3401", "Publication place in the sale-catalogue title.")
add_mention(216, "G. A. Moschini, 1806, II, p. 64", "cand-10187",
            "Short-form citation; the scan reads See where OCR has Sec.")


note_links = {
    "1": ["st-chp13-p338-zatta-proposed-jesuit-polemical-publications"],
    "2": ["st-chp13-p339-zatta-reported-lay-member-jesuits"],
    "3": ["st-chp13-p339-satirical-secretary-reads-vignette-as-jesuit-attack"],
    "4": ["st-chp13-p339-zatta-most-prolific-in-eighteenth-century-venice"],
    "5": [
        "st-chp13-p339-novelli-metastasio-illustrations-from-1781",
        "st-chp13-p339-haskell-metastasio-illustrations-herald-romantic",
    ],
    "6": ["st-chp13-p339-pinelli-owned-many-hundred-pictures"],
}

for marker, body_ids in note_links.items():
    for body_id in body_ids:
        if body_id not in statement_by_id:
            raise SystemExit(f"footnote {marker} target statement missing: {body_id}")

previous_statement_id = "st-chp13-p338-zatta-proposed-jesuit-polemical-publications"
previous_qualifiers = statement_by_id[previous_statement_id]["qualifiers"]
if not any(ref.get("footnote_marker") == "1" and ref.get("footnote_text_pending") for ref in previous_qualifiers.get("continuation_footnote_refs", [])):
    raise SystemExit("p.338 cross-page statement no longer has pending p.339 footnote 1")

wrong_marker_scope = {
    "st-chp13-p339-zatta-prefaces-characterization": ("3", "Printed note 3 follows the later vignette satire, not the preceding general characterization of Zatta’s prefaces."),
    "st-chp13-p339-zatta-classical-editions": ("4", "Printed note 4 follows the preceding catalogue-based superlative sentence; it is not attached to this later sentence about Zatta’s Italian-classics editions."),
    "st-chp13-p339-zatta-sponsored-first-illustrated-dante-edition-in-two-centuries": ("4", "Printed note 4 follows the earlier catalogue-based superlative sentence, not this later Dante-edition claim."),
    "st-chp13-p339-novelli-second-goldoni-drawing-set": ("5", "Printed note 5 follows the preceding sentence about Novelli’s Metastasio illustrations, not the next sentence about the Goldoni drawings."),
}
for statement_id, (marker, _) in wrong_marker_scope.items():
    if statement_id not in statement_by_id:
        raise SystemExit(f"statement requiring note-scope correction is missing: {statement_id}")
    refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
    if not any(ref.get("footnote_marker") == marker and ref.get("footnote_printed_page") == 339 for ref in refs):
        raise SystemExit(f"expected same-line OCR footnote {marker} missing from {statement_id}")


corrections = {
    211: [
        {"source_line": 211, "ocr": "Archi vio", "print": "Archivio", "basis": "CHP-13.pdf physical page 8."},
        {"source_line": 211, "ocr": "4IV", "print": "41V", "basis": "CHP-13.pdf physical page 8; archive folio recto/verso locator."},
        {"source_line": 212, "ocr": "17Ó0", "print": "1760", "basis": "CHP-13.pdf physical page 8."},
    ],
    213: [{"source_line": 213, "ocr": "quel die pare", "print": "quel che pare", "basis": "CHP-13.pdf physical page 8."}],
    215: [
        {"source_line": 215, "ocr": "c italiani", "print": "e italiani", "basis": "CHP-13.pdf physical page 8."},
        {"source_line": 215, "ocr": "efigli", "print": "e figli", "basis": "CHP-13.pdf physical page 8."},
        {"source_line": 215, "ocr": "p. 25-34", "print": "pp. 25-34", "basis": "CHP-13.pdf physical page 8."},
    ],
    216: [{"source_line": 216, "ocr": "Sec also", "print": "See also", "basis": "CHP-13.pdf physical page 8."}],
}


def source_quote(first_line, last_line, start_text=None, end_text=None):
    block = "\n".join(source_lines[first_line - 1:last_line])
    start = block.find(start_text) if start_text else 0
    end_start = block.find(end_text, start) if end_text else len(block)
    if start < 0 or end_start < 0:
        raise SystemExit(f"quote boundary missing in L{first_line}-L{last_line}: {start_text!r}/{end_text!r}")
    quote = block[start:end_start + (len(end_text) if end_text else 0)]
    if quote not in notes_text:
        raise SystemExit(f"quote is not anchored in the notes segment: {quote!r}")
    return quote


note_specs = [
    {
        "id": "st-chp13-p339-note1-inquisitori-records",
        "marker": "1", "line_start": 211, "line_end": 212,
        "subject": "cand-2865", "object": "cand-10180",
        "predicate": "footnote_cites_two_inquisitori_records_for_zatta_episodes",
        "claim": "Printed p.339 note 1 cites two Inquisitori di Stato records dated 18 June 1759 and 19 November 1760.",
        "qualification": "The dates and locators are transcribed from Haskell’s note and checked against the scan; the archival records themselves have not been consulted.",
        "quote": source_quote(211, 212),
        "mentioned": ["cand-10180", "cand-10181", "cand-3401"],
        "linked": note_links["1"],
        "citations": [
            {"source_candidate_id": "cand-10180", "repository": "Archivio di Stato, Venice", "series": "Inquisitori di Stato", "record_number": "535", "page": "173", "date_as_printed": "18 Giugno 1759"},
            {"source_candidate_id": "cand-10181", "repository": "Archivio di Stato, Venice", "series": "Inquisitori di Stato", "record_number": "536", "page_as_printed": "4IV", "page_print_reading": "41V", "date_as_printed": "19 Novembre 17Ó0", "date_print_reading": "1760"},
        ],
    },
    {
        "id": "st-chp13-p339-note2-cattaneo-testimony",
        "marker": "2", "line_start": 213, "line_end": 213,
        "subject": "cand-2865", "object": "cand-1321",
        "predicate": "cites_cattaneo_report_of_zatta_as_jesuit_tertiary",
        "claim": "Printed p.339 note 2 attributes to Giovanni de Cattaneo a qualified description of Zatta as a Jesuit tertiary.",
        "qualification": "Haskell quotes the wording through the Neri 1899 citation; retain a quel che pare (‘as it seems’) qualification and do not treat the report as independently verified.",
        "quote": source_quote(213, 213),
        "mentioned": ["cand-2865", "cand-0610", "cand-1321", "cand-10183"],
        "linked": note_links["2"],
        "citations": [{"source_candidate_id": "cand-10183", "reported_author_candidate_id": "cand-0610", "pages": "109", "quoted_source": "Giovanni de Cattaneo"}],
        "speaker": "Haskell quoting Giovanni de Cattaneo as cited by Neri",
        "layer": "nested quotation in bibliographic note",
        "ocr_corrections": corrections[213],
        "relation_candidate": True,
    },
    {
        "id": "st-chp13-p339-note2-nouvelles-testimony",
        "marker": "2", "line_start": 213, "line_end": 213,
        "subject": "cand-2865", "object": "cand-1321",
        "predicate": "cites_nouvelles_description_of_zatta_as_jesuit_tertiary",
        "claim": "Printed p.339 note 2 cites Nouvelles Ecclésiastiques describing Zatta as a printer for the Society and a Jesuit of the Third Order.",
        "qualification": "Haskell gives this quotation through Neri 1899, page 114; the periodical issue and original text have not been independently consulted.",
        "quote": source_quote(213, 213),
        "mentioned": ["cand-2865", "cand-1321", "cand-10182", "cand-10183"],
        "linked": note_links["2"],
        "citations": [{"source_candidate_id": "cand-10182", "intermediate_source_candidate_id": "cand-10183", "page": "114"}],
        "speaker": "Haskell quoting Nouvelles Ecclésiastiques as cited by Neri",
        "layer": "nested quotation in bibliographic note",
        "ocr_corrections": corrections[213],
        "relation_candidate": True,
    },
    {
        "id": "st-chp13-p339-note3-zatta-letter-page23",
        "marker": "3", "line_start": 214, "line_end": 214,
        "subject": "cand-2865", "object": "cand-10178",
        "predicate": "cites_zatta_letter_page_23_for_vignette_passage",
        "claim": "Printed p.339 note 3 cites page 23 of Zatta’s 1761 letter, explicitly cross-referencing p.338 note 2, for the vignette passage.",
        "qualification": "The letter itself has not been consulted. The in-book cross-reference identifies the cited title; candidate-level consolidation with the p.339 carrier-book candidate is deferred to S3.",
        "quote": source_quote(214, 214),
        "mentioned": ["cand-2865", "cand-10178"],
        "linked": note_links["3"],
        "citations": [{"source_candidate_id": "cand-10178", "year": "1761", "page": "23", "cross_reference": "p.338, note 2"}],
    },
    {
        "id": "st-chp13-p339-note4-zatta-1790-catalogue",
        "marker": "4", "line_start": 215, "line_end": 215,
        "subject": "cand-2865", "object": "cand-10184",
        "predicate": "cites_zatta_1790_catalogue_for_publisher_claim",
        "claim": "Printed p.339 note 4 cites Antonio Zatta’s 1790 catalogue of Latin and Italian books available from his Venetian bookselling and printing business.",
        "qualification": "The catalogue is cited by Haskell but has not been independently consulted; title wording follows the scan while S0 OCR is preserved.",
        "quote": source_quote(215, 215, "4 Catalogo", "1790."),
        "mentioned": ["cand-2865", "cand-10184", "cand-3401"],
        "linked": note_links["4"],
        "citations": [{"source_candidate_id": "cand-10184", "publisher_candidate_id": "cand-2865", "year": "1790", "place_candidate_id": "cand-3401"}],
        "ocr_corrections": corrections[215][:2],
    },
    {
        "id": "st-chp13-p339-note5-da-venezia-1934",
        "marker": "5", "line_start": 215, "line_end": 215,
        "subject": "cand-10029", "object": "cand-10185",
        "predicate": "cites_da_venezia_1934_for_novelli_metastasio_illustrations",
        "claim": "Printed p.339 note 5 cites G. da Venezia (1934), pages 25–34, after the sentence on Novelli’s Metastasio illustrations.",
        "qualification": "The note supplies no title or expanded author name; the cited pages have not been independently consulted.",
        "quote": source_quote(215, 215, "5 G. da Venezia", None),
        "mentioned": ["cand-10185"],
        "linked": note_links["5"],
        "citations": [{"source_candidate_id": "cand-10185", "author_as_printed": "G. da Venezia", "year": "1934", "pages_as_printed": "25-34"}],
        "ocr_corrections": [corrections[215][2]],
    },
    {
        "id": "st-chp13-p339-note6-pinelli-catalogues",
        "marker": "6", "line_start": 216, "line_end": 216,
        "subject": "cand-1932", "object": "cand-10186",
        "predicate": "cites_pinelli_sale_catalogue_and_moschini_reference_for_picture_collection",
        "claim": "Printed p.339 note 6 cites Pinelli’s 1785 sale catalogue and G. A. Moschini (1806), volume II, page 64.",
        "qualification": "These are bibliographic references printed beneath Haskell’s approximate statement that Pinelli owned many hundred pictures; neither source has been independently consulted.",
        "quote": source_quote(216, 216),
        "mentioned": ["cand-1932", "cand-10186", "cand-10187", "cand-3401"],
        "linked": note_links["6"],
        "citations": [
            {"source_candidate_id": "cand-10186", "year": "1785", "place_candidate_id": "cand-3401"},
            {"source_candidate_id": "cand-10187", "author_as_printed": "G. A. Moschini", "year": "1806", "volume": "II", "page": "64"},
        ],
        "ocr_corrections": corrections[216],
    },
]

new_statements = []
note_statement_ids_by_marker = {}
for spec in note_specs:
    if spec["id"] in statement_by_id:
        raise SystemExit(f"note statement already exists: {spec['id']}")
    missing = [candidate_id for candidate_id in spec["mentioned"] if candidate_id not in all_candidate_ids]
    if missing:
        raise SystemExit(f"missing candidate FK in {spec['id']}: {missing}")
    qualifiers = {
        "source_line_start": spec["line_start"],
        "source_line_end": spec["line_end"],
        "printed_page": 339,
        "pdf_physical_page": 8,
        "claim": spec["claim"],
        "speaker": spec.get("speaker", "Haskell, printed footnote"),
        "text_layer": spec.get("layer", "bibliographic citation"),
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "footnote_number": spec["marker"],
        "linked_body_statement_ids": spec["linked"],
        "citations": spec["citations"],
    }
    if spec.get("ocr_corrections"):
        qualifiers["ocr_corrections"] = spec["ocr_corrections"]
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    new_statements.append({
        "statement_id": spec["id"],
        "segment_id": NOTES,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec["object"],
        "predicate": spec["predicate"],
        "qualifiers": qualifiers,
        "original_quote": spec["quote"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })
    note_statement_ids_by_marker.setdefault(spec["marker"], []).append(spec["id"])


def link_body_statement(statement_id, marker, note_ids, continuation=False):
    statement = statement_by_id[statement_id]
    qualifiers = statement.setdefault("qualifiers", {})
    ref_field = "continuation_footnote_refs" if continuation else "footnote_refs"
    refs = qualifiers.get(ref_field, [])
    matching = [ref for ref in refs if ref.get("footnote_marker") == marker and ref.get("footnote_printed_page") == 339]
    if not matching:
        raise SystemExit(f"pending note {marker} reference missing from {statement_id}")
    for ref in matching:
        ref["footnote_text_pending"] = False
        ref["footnote_body_link_status"] = "linked"
        ref["footnote_note_statement_ids"] = note_ids
    id_field = "continuation_footnote_note_statement_ids" if continuation else "footnote_note_statement_ids"
    qualifiers[id_field] = sorted(set(qualifiers.get(id_field, [])) | set(note_ids))
    if continuation:
        qualifiers["continuation_footnote_text_pending"] = False
        qualifiers["continuation_footnote_body_link_status"] = "linked"
        qualifiers["continuation_closed_note"] = "The p.338 sentence closes with “Portuguese government” at p.339 L71; its printed p.339 note 1 at L211-L212 is migrated and linked to the two cited archival records."
        qualifiers["qualification"] = "“Two or three” is approximate. The Portuguese target is completed as “Portuguese government” at p.339 L71. Note 1 cites two Inquisitori di Stato records; neither archival record has been independently consulted."
    else:
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"


for marker, body_ids in note_links.items():
    note_ids = note_statement_ids_by_marker[marker]
    for body_id in body_ids:
        link_body_statement(body_id, marker, note_ids, continuation=(marker == "1"))

# Correct same-line OCR carryover from the p.339 body: only printed marker positions
# determine the scope of each note; ordinary proximity is insufficient.
for statement_id, (marker, explanation) in wrong_marker_scope.items():
    qualifiers = statement_by_id[statement_id].setdefault("qualifiers", {})
    qualifiers["footnote_refs"] = [
        ref for ref in qualifiers.get("footnote_refs", [])
        if not (ref.get("footnote_marker") == marker and ref.get("footnote_printed_page") == 339)
    ]
    if not qualifiers["footnote_refs"]:
        qualifiers.pop("footnote_refs", None)
        for field in (
            "footnote_marker", "footnote_printed_page", "footnote_text_pending", "footnote_segment",
            "footnote_body_link_status", "footnote_note_statement_ids",
        ):
            qualifiers.pop(field, None)
        if qualifiers.get("cross_reference_segments") == [NOTES]:
            qualifiers.pop("cross_reference_segments", None)
    qualifiers["footnote_scope_exclusion"] = explanation + " Confirmed against CHP-13.pdf physical page 8."

# The general phrase “His own prefaces” was incorrectly attached to the single
# unidentified carrier-book candidate. It is a general characterization, not a
# separately identified work. Keep the named carrier-book candidate for the vignette.
preface_mention_id = "m-s2-ch13-p339-007"
preface_rows = [row for row in mentions if row["mention_id"] == preface_mention_id]
if len(preface_rows) != 1 or preface_rows[0]["surface_form"] != "His own prefaces" or preface_rows[0]["candidate_id"] != "cand-10024":
    raise SystemExit("unexpected p.339 preface mention mapping")
mentions.remove(preface_rows[0])

preface_statement = statement_by_id["st-chp13-p339-zatta-prefaces-characterization"]
preface_qualifiers = preface_statement["qualifiers"]
if preface_statement.get("object_candidate_id") != "cand-10024":
    raise SystemExit("unexpected p.339 general-preface statement object")
preface_statement["object_candidate_id"] = None
preface_qualifiers["mentioned_candidate_ids"] = [
    candidate_id for candidate_id in preface_qualifiers.get("mentioned_candidate_ids", [])
    if candidate_id != "cand-10024"
]
preface_qualifiers["qualification"] = "This is Haskell’s general characterization of Zatta’s prefaces, not a claim about one identified book; note 3 follows the later vignette discussion."

carrier_book = candidate_by_id["cand-10024"]
carrier_book["detail"] = (
    "Printed p.339 note 3 (L214) cites page 23 of Lettera del Magnifico Signor Antonio Zatta and explicitly cross-references p.338 note 2. "
    "This identifies the cited source for the fountain-and-dolphin vignette; candidate cand-10178 names that cited title. "
    "Keep the existing S2 candidates distinct and send candidate-level consolidation to S3."
)

coverage[NOTES]["source_line_ranges"] = "L180-216"
coverage[NOTES]["note"] = (
    "Notes L180-210 (pp.332-338) and p.339 notes 1-6 at L211-216 are migrated. "
    "L217-246 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."
)
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["source_line_ranges"] = "L70-77"
coverage[BODY]["note"] = (
    "Printed p.339 body and notes 1-6 were checked against CHP-13.pdf physical page 8. "
    "The p.338 continuation closes at L71; all six printed note markers now link to their exact body statements and citation records. "
    "False same-line note 3/4/5 carryovers were removed. OCR corrections are recorded in S2 only; the referenced archival and printed works were not independently consulted."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = statements + new_statements

if len({row["candidate_id"] for row in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique after migration")
if len({row["mention_id"] for row in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique after migration")
if len({row["statement_id"] for row in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique after migration")
for row in new_mentions:
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"final mention span failed: {row['mention_id']}")
for statement in new_statements:
    if statement["original_quote"] not in notes_text:
        raise SystemExit(f"final statement quote failed: {statement['statement_id']}")

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions) + 1} -> {len(mention_out)} (+{len(new_mentions)} added, 1 mis-mapped mention removed)")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage: p.339 body partial -> complete; consolidated notes range L180-210 -> L180-216, still partial")
print("footnote links: 1 -> p.338 continuation; 2-6 -> exact p.339 statements")
print("scope corrections: remove p.339 notes 3, 4 and 5 from adjacent but unmarked statements")
print("citation scan: physical p.8 confirms Archivio, folio 41V, 1760, che, catalogue title, pp.25-34, See also")

if not args.apply:
    print("dry-run only; rerun with --apply after reviewing this delta")
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
