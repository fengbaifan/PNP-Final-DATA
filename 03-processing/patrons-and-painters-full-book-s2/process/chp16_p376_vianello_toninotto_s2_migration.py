"""Controlled S2 migration for chapter 16 p.376 and footnotes 1-3."""
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
BODY_PREV = "chp-16:16_CHP-16_intro:l24-36"
BODY = "chp-16:16_CHP-16_intro:l38-46"
BODY_NEXT = "chp-16:16_CHP-16_intro:l48-64"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
BACKUP_SUFFIX = ".bak-s2-chp16-p376-vianello-toninotto-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
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
    raise SystemExit("chapter 16 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-16 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    38: "[Page 376]", 39: "canon ofChioggia Cathedral, Dr GiovanniVianello",
    41: "Pietrp della Vecchia", 42: "Rosalba, Ricci, Piazzetta and Tiepolo",
    43: "Dominican Padre", 44: "Giovanni del Pian of Carpaccio’s famous scenes",
    46: "Amadeo Swajer (Plate 59a)", 82: "catalogue of his pictures published in. 1790",
    83: "Haskell, in Journal os Warburg Institute, i960, pp. 263-4",
    84: "Swajer’s correspondence is in the Seminario Patriarcale in Venice",
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
if (coverage_by_id[BODY_PREV]["migration_status"] != "complete"
        or coverage_by_id[BODY]["disposition"] != "queued"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L70-81"):
    raise SystemExit("S2 coverage preconditions changed")
if any(row["segment_id"] == BODY for row in mentions):
    raise SystemExit("p.376 body already has mention rows")
if any(row.get("statement_id", "").startswith("st-chp16-p376-") for row in statements):
    raise SystemExit("p.376 statements already exist")
if "cand-10629" not in candidate_by_id:
    raise SystemExit("p.375 Haskell article candidate is missing")

body_lines = {number: source_lines[number - 1] for number in range(38, 47)}
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
    ("cand-10630", "Catalogue of Giovanni Vianello's pictures (1790; title unspecified)", "archive", BODY, 41,
     "Haskell says its publication in 1790 strongly suggests Vianello was willing to dispose of his pictures; the catalogue was not consulted."),
    ("cand-10631", "Giovanni Vianello's 1793 edition of Rosalba Carriera's journal (title unspecified)", "archive", BODY, 41,
     "The passage describes an edition Vianello brought out; it gives no title, edition details, or repository."),
    ("cand-10632", "Alla Giorgionesca manner (Haskell's phrase for Vianello's fantasy heads)", "term", BODY, 41,
     "The Italian phrase describes the manner of some fantasy heads in Vianello's collection; S0 reads 'alia' and the printed form is 'alla'."),
    ("cand-10633", "Twenty-five pictures by Pietro della Vecchia in Giovanni Vianello's collection", "work", BODY, 41,
     "Haskell gives the count and artist but no titles, dates, or present locations."),
    ("cand-10634", "Three works by Francesco Guardi in Giovanni Vianello's collection (two paintings and one drawing)", "work", BODY, 42,
     "The source gives the count and media but no individual titles, dates, or locations."),
    ("cand-10635", "Scenes from the Life of St Ursula by Vittore Carpaccio (cycle cited by Haskell)", "work", BODY, 44,
     "The passage refers to Carpaccio's famous scenes as the subject of a print series; no title or present location is supplied here."),
    ("cand-10636", "Nine large prints by Giovanni del Pian after Carpaccio's Life of St Ursula scenes (1785)", "work", BODY, 44,
     "Haskell gives the maker, number, subject, and year; individual print titles and publication details are not supplied."),
    ("cand-10637", "Twelve paintings and four drawings by Giuseppe Zais in Toninotto's collection", "work", BODY, 44,
     "The source gives counts and artist but no individual titles or locations."),
    ("cand-10638", "Eight paintings by Francesco Guardi in Toninotto's collection", "work", BODY, 44,
     "The source gives the count and artist; the following sentence describes subsets without individual titles."),
    ("cand-10639", "Four Guardi capricci described as 'caprizi copiosi di figure' in Toninotto's collection", "work", BODY, 45,
     "Haskell identifies four of the described paintings by this phrase; titles and locations are not supplied."),
    ("cand-10640", "Four unnamed Venetian views by Francesco Guardi in Toninotto's collection", "work", BODY, 45,
     "The views are expressly unnamed in the source; no individual titles or locations are supplied."),
    ("cand-10641", "Chioggia Cathedral (source does not distinguish building from chapter institution)", "", BODY, 39,
     "Named as the cathedral of which Vianello was a canon; the text does not distinguish the building from its institutional chapter."),
    ("cand-10642", "The Frari (church visited with tourists by Giuseppe Toninotto)", "place", BODY, 44,
     "Haskell names the Frari as the place where Toninotto showed foreign tourists around; no fuller site name is supplied here."),
    ("cand-10643", "Unidentified 'secret' manuscripts collected by Amadeo Swajer (as described by Haskell)", "archive", BODY, 46,
     "Haskell begins a cross-page account of manuscripts whose possible posthumous dispersal alarmed the Inquisitors; their contents remain unidentified."),
    ("cand-10644", "Amadeo Swajer's correspondence cited as held at Seminario Patriarcale", "archive", NOTES, 84,
     "Haskell's footnote begins a locator for Swajer's correspondence; its details continue on p.377 and the papers were not consulted."),
    ("cand-10645", "Ricci (surname-only artist reference on p.376; identity unresolved)", "person", BODY, 42,
     "The source gives only 'Ricci'; the index has both Marco Ricci and Sebastiano Ricci at p.376, so this mention remains unresolved."),
    ("cand-10646", "Two unidentified works by Pietro della Vecchia in Toninotto's collection, described as 'sulla maniera di Zorzone'", "work", BODY, 44,
     "The source says a couple of works but gives no titles or medium; the identity behind 'Zorzone' is not resolved."),
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

# This is the same unidentified 1960 journal article cited on p.374 and p.375.
haskell_article = candidate_by_id["cand-10629"]
if haskell_article["canonical_name"] != "Haskell, Journal of Warburg Institute, 1960 (article title unspecified)":
    if haskell_article["canonical_name"] != "Haskell, Journal of Warburg Institute, 1960, pp. 261-2 (article title unspecified)":
        raise SystemExit("unexpected p.375 Haskell article candidate label")
haskell_article["canonical_name"] = "Haskell, Journal of Warburg Institute, 1960 (article title unspecified)"
haskell_article["detail"] = (
    "Haskell's p.374 note cites pp.256-76; p.375 cites pp.261-2 and p.376 cites pp.263-4. "
    "The article title and full publication details are not supplied in these notes; the cited pages were not consulted."
)

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
    mention_id = f"m-chp16-p376-vianello-toninotto-{len(planned_mentions) + 1:04d}"
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


mention_specs = [
    ("cand-2764", "GiovanniVianello", BODY, 39, "S0 joins the forename and surname; retain the exact source span.", 0),
    ("cand-10641", "Chioggia Cathedral", BODY, 39, "Institutional/building referent remains unresolved.", 0),
    ("cand-2364", "Sasso", BODY, 39, "", 0),
    ("cand-1387", "della Lena", BODY, 39, "", 0),
    ("cand-10631", "edition he brought out in 1793 of Rosalba’s journal", BODY, 41, "Edition described by Haskell; title unspecified.", 0),
    ("cand-0581", "Rosalba", BODY, 41, "Person named within the edition description.", 0),
    ("cand-10630", "catalogue of his paintings in 1790", BODY, 41, "The catalogue is described, not consulted.", 0),
    ("cand-2707", "Pietrp della Vecchia", BODY, 41, "S0 OCR form; print reading is Pietro della Vecchia.", 0),
    ("cand-10633", "twenty-five pictures", BODY, 41, "Count of works by Pietro della Vecchia.", 0),
    ("cand-10632", "‘alia Giorgionesca’", BODY, 41, "S0 spelling; print reading is alla Giorgionesca.", 0),
    ("cand-0581", "Rosalba", BODY, 42, "", 0),
    ("cand-10645", "Ricci", BODY, 42, "Surname-only mention; both Marco and Sebastiano Ricci are indexed at p.376.", 0),
    ("cand-1901", "Piazzetta", BODY, 42, "", 0),
    ("cand-2569", "Tiepolo", BODY, 42, "The source gives surname only; mapped to the main index candidate for S3 review.", 0),
    ("cand-2764", "Vianello", BODY, 42, "Named again as the collector in this sentence.", 0),
    ("cand-1239", "Francesco Guardi", BODY, 42, "", 0),
    ("cand-1239", "Guardi", BODY, 42, "Repeated direct reference after the full name.", 1),
    ("cand-1239", "Guardi", BODY, 42, "Repeated direct reference in the same sentence.", 2),
    ("cand-10634", "three works", BODY, 42, "Two paintings and one drawing, as specified in the same sentence.", 0),
    ("cand-0498", "Canaletto", BODY, 42, "", 0),
    ("cand-0941", "Dominican", BODY, 43, "Religious-order reference; existing index candidate retained.", 0),
    ("cand-2643", "Giuseppe Toninotto", BODY, 44, "", 0),
    ("cand-10642", "Frari", BODY, 44, "Named church/place in the source.", 0),
    ("cand-10524", "State Inquisition", BODY, 44, "Reuses the existing institution candidate; no legal finding is inferred.", 0),
    ("cand-8838", "Republic", BODY, 44, "Venetian political entity in context; distinct from the city.", 0),
    ("cand-10636", "series of nine large prints", BODY, 44, "Work group, distinct from Carpaccio's source cycle.", 0),
    ("cand-1899", "Giovanni del Pian", BODY, 44, "", 0),
    ("cand-0566", "Carpaccio", BODY, 44, "Person indexed with the Life of St Ursula subentry at p.376.", 0),
    ("cand-10635", "Carpaccio’s famous scenes of the Life of St Ursula", BODY, 44, "Source cycle; separate from del Pian's nine prints.", 0),
    ("cand-2630", "Titian", BODY, 44, "", 0),
    ("cand-0257", "Bassano", BODY, 44, "", 0),
    ("cand-2707", "Pietro della Vecchias", BODY, 44, "Source possessive form retained.", 0),
    ("cand-10646", "a couple of Pietro della Vecchias ‘sulla maniera di Zorzone’", BODY, 44, "Unnamed work group; medium and the identity behind Zorzone remain unresolved.", 0),
    ("cand-0554", "Carlevarijs", BODY, 44, "", 0),
    ("cand-2149", "Marco Ricci", BODY, 44, "", 0),
    ("cand-1546", "Marieschi", BODY, 44, "", 0),
    ("cand-2830", "Giuseppe Zais", BODY, 44, "", 0),
    ("cand-1239", "Francesco Guardi", BODY, 44, "", 0),
    ("cand-10637", "twelve paintings and four drawings", BODY, 44, "Counted works by Zais.", 0),
    ("cand-10638", "eight paintings", BODY, 44, "Counted works by Guardi.", 0),
    ("cand-10639", "'caprizi copiosi di figure’", BODY, 45, "Source's opening quote is an ASCII apostrophe; retain the exact span.", 0),
    ("cand-10640", "four were unnamed Venetian views", BODY, 45, "The views are expressly unnamed in Haskell's text.", 0),
    ("cand-2534", "Amadeo Swajer", BODY, 46, "", 0),
    ("cand-4016", "Plate 59a", BODY, 46, "Cross-reference to the already indexed Canova portrait of Swajer.", 0),
    ("cand-2719", "Venice", BODY, 46, "", 0),
    ("cand-10643", "manuscripts", BODY, 46, "The later phrase 'the secret' refers to an unidentified subset; p.377 continuation pending.", 0),
    ("cand-10643", "secret", BODY, 46, "Implicit object continues on p.377; preserve as partial.", 0),
    ("cand-10630", "catalogue of his pictures", NOTES, 82, "Footnote 1 source locator for Vianello's 1790 catalogue.", 0),
    ("cand-10629", "Haskell, in Journal os Warburg Institute, i960, pp. 263-4", NOTES, 83,
     "Reuses the 1960 article candidate cited on pp.374-375; printed year is 1960.", 0),
    ("cand-3770", "Haskell", NOTES, 83, "Author within the bibliographic locator.", 0),
    ("cand-6004", "Journal os Warburg Institute", NOTES, 83, "S0 OCR form; print title reads Journal of Warburg Institute.", 0),
    ("cand-10644", "Swajer’s correspondence", NOTES, 84, "Footnote 3 locator; continuation on p.377 remains pending.", 0),
    ("cand-6589", "Seminario Patriarcale", NOTES, 84, "Existing manuscript repository candidate.", 0),
    ("cand-2534", "Swajer", NOTES, 84, "Person named within the correspondence locator.", 0),
    ("cand-2719", "Venice", NOTES, 84, "Place in the repository locator.", 0),
]
for candidate_id, surface, segment_id, source_line, note, occurrence in mention_specs:
    add_mention(candidate_id, surface, segment_id, source_line, note, occurrence)

body38, body39, body40, body41 = [source_lines[n - 1] for n in range(38, 42)]
body42, body43, body44, body45, body46 = [source_lines[n - 1] for n in range(42, 47)]
note82, note83, note84 = [source_lines[n - 1] for n in range(82, 85)]

corrections_l39 = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 39,
     "ocr": "ofChioggia", "print": "of Chioggia", "basis": "CHP-16.pdf physical page 4."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 39,
     "ocr": "GiovanniVianello", "print": "Giovanni Vianello", "basis": "CHP-16.pdf physical page 4."},
]
corrections_l41 = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 41,
     "ocr": "Pietrp", "print": "Pietro", "basis": "CHP-16.pdf physical page 4."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 41,
     "ocr": "‘alia Giorgionesca’", "print": "‘alla Giorgionesca’", "basis": "CHP-16.pdf physical page 4."},
]
corrections_l44 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 44,
    "ocr": "tnodelli", "print": "modelli", "basis": "CHP-16.pdf physical page 4."},
]
corrections_note82 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 82,
    "ocr": "in. 1790", "print": "in 1790", "basis": "CHP-16.pdf physical page 4."},
]
corrections_note83 = [{
    "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 83,
    "ocr": "i960", "print": "1960", "basis": "CHP-16.pdf physical page 4."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 83,
     "ocr": "Journal os", "print": "Journal of", "basis": "CHP-16.pdf physical page 4."},
]

note1_id = "st-chp16-p376-note1-vianello-catalogue"
note2_id = "st-chp16-p376-note2-haskell-journal"
note3_id = "st-chp16-p376-note3-swajer-correspondence-partial"


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, speaker, text_layer, qualification, mentioned_ids, quote,
                   relation_candidate=False, **extra_qualifiers):
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 376 if segment_id == BODY or start_line <= 84 else 377,
        "pdf_physical_page": 4 if segment_id == BODY or start_line <= 84 else 5,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
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


note1_link = {
    "footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L82-L82",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L39-L41", "footnote_note_statement_ids": [note1_id],
    "footnote_link_note": "Note 1 identifies the 1790 catalogue mentioned in Vianello's biography.",
}
note2_link = {
    "footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L83-L83",
    "footnote_text_pending": False, "footnote_body_link_status": "linked",
    "footnote_body_line_range": "L43-L45", "footnote_note_statement_ids": [note2_id],
    "footnote_link_note": "Note 2 points to Haskell's pages 263-4 for references connected with this p.376 discussion.",
}
note3_link = {
    "footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L84-L84",
    "footnote_text_pending": True, "footnote_body_link_status": "partial",
    "footnote_body_line_range": "L46", "footnote_note_statement_ids": [note3_id],
    "footnote_link_note": "The footnote continues in the p.377 source segment; its full locator is pending.",
}

make_statement(
    "st-chp16-p376-vianello-circle-membership", BODY, "cand-2764", None,
    "may_have_belonged_to_circle_of_sasso_and_della_lena", 39, 39,
    "Haskell says Dr Giovanni Vianello may well have belonged to the circle of Sasso and della Lena.",
    "Haskell", "qualified authorial report", "Membership is explicitly probable; the passage does not define the circle's membership or boundaries.",
    ["cand-2764", "cand-2364", "cand-1387"], body39,
    relation_candidate=True, ocr_corrections=corrections_l39,
)
make_statement(
    "st-chp16-p376-vianello-canon-of-chioggia-cathedral", BODY, "cand-2764", "cand-10641",
    "was_canon_of_chioggia_cathedral", 39, 39,
    "Haskell identifies Dr Giovanni Vianello as a canon of Chioggia Cathedral.",
    "Haskell", "authorial report", "The candidate's institutional/building referent is unresolved.",
    ["cand-2764", "cand-10641"], body39,
    relation_candidate=True, ocr_corrections=corrections_l39,
)
make_statement(
    "st-chp16-p376-vianello-scholarship-and-rosalba-journal-edition", BODY, "cand-2764", "cand-10631",
    "brought_out_1793_edition_of_rosalba_journal", 40, 41,
    "Haskell characterizes Vianello as having pretensions to scholarship, illustrated—though hardly justified—by his 1793 edition of Rosalba's journal.",
    "Haskell", "authorial interpretation and report", "The journal and edition are not titled or independently consulted.",
    ["cand-2764", "cand-10631", "cand-0581"], body40 + "\n" + body41,
    relation_candidate=True, ocr_corrections=corrections_l41,
)
make_statement(
    "st-chp16-p376-vianello-dealer-and-picture-catalogue", BODY, "cand-2764", "cand-10630",
    "catalogue_publication_suggested_willingness_to_sell_pictures", 41, 41,
    "Haskell says it is uncertain whether Vianello was a dealer, but the publication of his picture catalogue in 1790 strongly suggests he was then willing to dispose of pictures.",
    "Haskell", "authorial report and qualified inference", "The catalogue supports a strong suggestion, not a confirmed dealer identity or sale.",
    ["cand-2764", "cand-10630"], body41, relation_candidate=True, **note1_link,
)
make_statement(
    "st-chp16-p376-vianello-large-venetian-collection", BODY, "cand-2764", None,
    "owned_over_two_hundred_pictures_mostly_venetian_seventeenth_and_eighteenth_century", 41, 41,
    "Haskell says Vianello owned more than 200 pictures, the vast majority Venetian works of the seventeenth and eighteenth centuries.",
    "Haskell", "authorial report", "The passage gives no inventory or individual titles.",
    ["cand-2764"], body41,
)
make_statement(
    "st-chp16-p376-vianello-vecchia-pictures", BODY, "cand-2764", "cand-10633",
    "owned_twenty_five_pictures_by_pietro_della_vecchia", 41, 41,
    "Haskell says Pietro della Vecchia was Vianello's special favourite and that Vianello owned 25 pictures by him, many fantasy heads described as alla Giorgionesca.",
    "Haskell", "authorial report", "Individual pictures are unidentified; the stylistic phrase is retained as printed after OCR correction.",
    ["cand-2764", "cand-2707", "cand-10633", "cand-10632"], body41,
    relation_candidate=True, ocr_corrections=corrections_l41,
)
make_statement(
    "st-chp16-p376-vianello-artists-and-preferred-works", BODY, "cand-2764", None,
    "collection_included_many_works_by_named_venetian_artists_and_he_preferred_sketches_and_bust_portraits", 42, 42,
    "Haskell says Vianello's collection included many drawings and paintings by Rosalba, Ricci, Piazzetta, and Tiepolo; Vianello seems to have preferred sketches and capricious bust portraits.",
    "Haskell", "authorial report", "The source gives Ricci by surname only; the index lists both Marco and Sebastiano Ricci at p.376, so identity remains unresolved.",
    ["cand-2764", "cand-0581", "cand-10645", "cand-1901", "cand-2569"], body42,
)
make_statement(
    "st-chp16-p376-vianello-guardi-works", BODY, "cand-2764", "cand-10634",
    "owned_three_guardi_works_two_paintings_and_one_drawing", 42, 42,
    "Haskell says Vianello owned three works by Francesco Guardi—two paintings and one drawing—while his appreciation of Guardi exceeded what that small number alone would suggest.",
    "Haskell", "authorial report and interpretation", "No individual Guardi work is titled or located.",
    ["cand-2764", "cand-10634", "cand-1239"], body42, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-vianello-defends-guardi", BODY, "cand-2764", "cand-1239",
    "deplored_guardis_absence_from_reference_books_and_defended_him_from_perspective_criticism", 42, 42,
    "Haskell says Vianello deplored Guardi's absence from standard reference books and, unlike other writers, did not make the usual unfavourable comparison with Canaletto; by implication he defended Guardi against perspective criticisms.",
    "Haskell", "authorial report and interpretation", "Haskell's 'by implication' framing is retained; no particular reference book or critic is named.",
    ["cand-2764", "cand-1239", "cand-0498"], body42,
)
make_statement(
    "st-chp16-p376-vianello-guardi-aesthetic-qualities", BODY, "cand-2764", "cand-1239",
    "admired_guardis_movement_colour_vivacity_lights_and_macchiette", 42, 42,
    "Haskell says Vianello especially admired Guardi's movement, colour, vivacity, sparkling lights, and macchiette, with the Italian phrase 'secondo si dice dalli Pittori'.",
    "Haskell", "authorial report", "The aesthetic evaluation and quoted Italian remain Haskell's account.",
    ["cand-2764", "cand-1239"], body42,
)
make_statement(
    "st-chp16-p376-toninotto-introduction", BODY, "cand-2643", None,
    "introduced_as_dominican_with_similar_tastes_and_more_modest_than_preceding_collectors", 43, 44,
    "Haskell introduces Dominican Padre Giuseppe Toninotto as more modest than the preceding collectors but similar in taste.",
    "Haskell", "authorial characterization", "'More modest' is Haskell's comparison, not an independent social ranking.",
    ["cand-2643", "cand-0941"], body43 + "\n" + body44,
    **note2_link,
)
make_statement(
    "st-chp16-p376-toninotto-showed-tourists-around-frari", BODY, "cand-2643", "cand-10642",
    "showed_foreign_tourists_around_frari_while_begging_from_them", 44, 44,
    "Haskell says Toninotto begged from foreign tourists while showing them around the Frari.",
    "Haskell", "authorial report with evaluative wording", "The phrase 'rather pathetically' is Haskell's tone; the passage does not specify a paid guide role.",
    ["cand-2643", "cand-10642"], body44, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-toninotto-disgrace-with-state-inquisition", BODY, "cand-2643", "cand-10524",
    "was_in_disgrace_with_state_inquisition_for_selling_improper_prints", 44, 44,
    "Haskell says Toninotto was in disgrace with the State Inquisition for selling improper prints.",
    "Haskell", "authorial report", "The source does not specify a formal proceeding or outcome.",
    ["cand-2643", "cand-10524"], body44, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-toninotto-recording-venetian-art", BODY, "cand-2643", None,
    "helped_record_and_collect_venetian_art_before_republic_collapsed", 44, 44,
    "Haskell says Toninotto helped record and collect Venetian art before the Republic finally collapsed.",
    "Haskell", "authorial report", "The Republic is treated as the Venetian political entity, not the city; no exact collapse date is added.",
    ["cand-2643", "cand-8838"], body44,
)
make_statement(
    "st-chp16-p376-toninotto-del-pian-prints-after-carpaccio", BODY, "cand-2643", "cand-10636",
    "responsible_in_1785_for_nine_large_del_pian_prints_after_carpaccio_st_ursula_scenes", 44, 44,
    "Haskell says Toninotto was responsible in 1785 for publishing nine large prints by Giovanni del Pian of Carpaccio's famous Life of St Ursula scenes.",
    "Haskell", "authorial report", "The print series is distinct from Carpaccio's source cycle; individual print titles and the publication imprint are not given.",
    ["cand-2643", "cand-1899", "cand-10636", "cand-10635", "cand-0566"], body44,
    relation_candidate=True, ocr_corrections=corrections_l44,
)
make_statement(
    "st-chp16-p376-del-pian-maker-of-print-series", BODY, "cand-10636", "cand-1899",
    "prints_by_giovanni_del_pian", 44, 44,
    "Haskell describes the nine-print series as prints by Giovanni del Pian.",
    "Haskell", "authorial report", "The work group is not individually titled.",
    ["cand-10636", "cand-1899"], body44, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-del-pian-prints-of-carpaccio-cycle", BODY, "cand-10636", "cand-10635",
    "prints_of_carpaccios_life_of_st_ursula_scenes", 44, 44,
    "Haskell identifies Carpaccio's Life of St Ursula scenes as the subject of the nine-print series.",
    "Haskell", "authorial report", "The print series is distinct from the source cycle; no individual print titles are supplied.",
    ["cand-10636", "cand-10635"], body44, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-toninotto-attributed-old-masters", BODY, "cand-2643", None,
    "collection_included_old_masters_with_ambitious_attributions", 44, 44,
    "Haskell says Toninotto's collection included old masters with ambitious attributions to Titian, Bassano, and others.",
    "Haskell", "authorial report", "No individual picture or attribution is specified or independently assessed.",
    ["cand-2643", "cand-2630", "cand-0257"], body44, ocr_corrections=corrections_l44,
)
make_statement(
    "st-chp16-p376-toninotto-mixed-collection", BODY, "cand-2643", None,
    "collection_included_modelli_della_vecchia_flemish_paintings_and_venetian_views", 44, 44,
    "Haskell lists modelli, works by Pietro della Vecchia described as 'sulla maniera di Zorzone', Flemish paintings, and small Venetian views and landscapes by Carlevarijs, Marco Ricci, and Marieschi.",
    "Haskell", "authorial report", "The identity behind 'Zorzone' and the titles of the works are not resolved; S0's 'tnodelli' is corrected from the page image.",
    ["cand-2643", "cand-2707", "cand-10646", "cand-0554", "cand-2149", "cand-1546"], body44,
    ocr_corrections=corrections_l44,
)
make_statement(
    "st-chp16-p376-toninotto-vecchia-works", BODY, "cand-2643", "cand-10646",
    "owned_two_works_by_pietro_della_vecchia_described_as_sulla_maniera_di_zorzone", 44, 44,
    "Haskell says Toninotto had a couple of works by Pietro della Vecchia described as 'sulla maniera di Zorzone'.",
    "Haskell", "authorial report", "The two works are unnamed and their medium is not specified; the identity behind 'Zorzone' remains unresolved.",
    ["cand-2643", "cand-2707", "cand-10646"], body44, relation_candidate=True,
    ocr_corrections=corrections_l44,
)
make_statement(
    "st-chp16-p376-toninotto-zais-works", BODY, "cand-2643", "cand-10637",
    "owned_twelve_zais_paintings_and_four_drawings", 44, 44,
    "Haskell says Toninotto owned twelve paintings and four drawings by Giuseppe Zais.",
    "Haskell", "authorial report", "The individual works are not titled or located.",
    ["cand-2643", "cand-2830", "cand-10637"], body44, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-toninotto-guardi-works", BODY, "cand-2643", "cand-10638",
    "owned_eight_guardi_paintings", 44, 45,
    "Haskell says Toninotto owned eight paintings by Francesco Guardi; four were capricci described as 'caprizi copiosi di figure' and four were unnamed Venetian views.",
    "Haskell", "authorial report", "The source does not provide individual titles; the four-plus-four division follows the immediate antecedent 'eight paintings'.",
    ["cand-2643", "cand-1239", "cand-10638", "cand-10639", "cand-10640"], body44 + "\n" + body45,
    relation_candidate=True,
)
make_statement(
    "st-chp16-p376-toninotto-guardi-capricci", BODY, "cand-2643", "cand-10639",
    "owned_four_guardi_capricci_described_as_caprizi_copiosi_di_figure", 44, 45,
    "Haskell describes four of Toninotto's Guardi paintings as 'caprizi copiosi di figure'.",
    "Haskell", "authorial report", "The Italian phrase is retained as printed; the individual paintings are unnamed.",
    ["cand-2643", "cand-1239", "cand-10639"], body44 + "\n" + body45, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-toninotto-unnamed-venetian-views", BODY, "cand-2643", "cand-10640",
    "owned_four_unnamed_venetian_views_by_guardi", 44, 45,
    "Haskell says four of Toninotto's Guardi paintings were unnamed Venetian views.",
    "Haskell", "authorial report", "The views remain unidentified, as Haskell states.",
    ["cand-2643", "cand-1239", "cand-10640"], body44 + "\n" + body45, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-swajer-biography-and-manuscripts", BODY, "cand-2534", "cand-10643",
    "german_businessman_lived_in_venice_died_1792_and_collected_manuscripts", 46, 46,
    "Haskell describes Amadeo Swajer as a wealthy German businessman who lived most of his life in Venice, died there in 1792, and principally collected manuscripts.",
    "Haskell", "authorial report", "The source supplies no further biography or individual manuscript titles.",
    ["cand-2534", "cand-2719", "cand-10643"], body46, relation_candidate=True,
)
make_statement(
    "st-chp16-p376-swajer-secret-manuscripts-partial", BODY, "cand-2534", "cand-10643",
    "possible_posthumous_dispersal_of_secret_manuscripts_alarm_inquisitors_and_they_acquired_them", 46, 46,
    "Haskell begins a sentence saying possible posthumous dispersal of Swajer's 'secret' manuscripts caused concern; the sentence continues on p.377.",
    "Haskell", "authorial report", "The descriptor 'secret' and the manuscripts' contents remain unexplained; acquisition by the Inquisitors is pending p.377.",
    ["cand-2534", "cand-10643"], body46,
    relation_candidate=True, predicate_status="partial", cross_reference_segments=[BODY_NEXT],
    cross_reference_text="P.377 L49 begins 'ones caused some anxiety to the Inquisitors of State, who acquired them all.'",
    cross_reference_text_pending=True,
    **note3_link,
)
make_statement(
    note1_id, NOTES, "cand-10630", "cand-2764", "note_cites_vianello_picture_catalogue_published_1790", 82, 82,
    "Haskell's note points to the catalogue of Vianello's pictures published in 1790.",
    "Haskell's note", "bibliographic locator", "The catalogue was not independently consulted; OCR punctuation is corrected only in S2.",
    ["cand-10630", "cand-2764"], note82, cited_source_independently_consulted=False,
    ocr_corrections=corrections_note82, **note1_link,
)
make_statement(
    note2_id, NOTES, "cand-10629", "cand-6004", "note_cites_haskell_1960_journal_pages263_264", 83, 83,
    "Haskell's note cites his Journal of Warburg Institute article, 1960, pages 263-4, for references.",
    "Haskell's note", "bibliographic citation", "The article title and full publication details are not supplied; the cited pages were not consulted.",
    ["cand-10629", "cand-6004", "cand-3770"], note83, cited_source_independently_consulted=False,
    ocr_corrections=corrections_note83, **note2_link,
)
make_statement(
    note3_id, NOTES, "cand-10644", "cand-6589", "note_locates_swajer_correspondence_at_seminario_patriarcale", 84, 84,
    "Haskell's note locates much of Swajer's correspondence at Seminario Patriarcale in Venice and begins describing a volume of letters from the 1750s and 1760s.",
    "Haskell's note", "archival locator", "The note continues on p.377 with correspondence details; the papers were not consulted.",
    ["cand-10644", "cand-2534", "cand-6589", "cand-2719"], note84,
    cited_source_independently_consulted=False, predicate_status="partial",
    cross_reference_segments=[BODY_NEXT],
    cross_reference_text="P.377 source lines 60-64 continue note 3 with additional correspondence and archive details.",
    cross_reference_text_pending=True, **note3_link,
)

for statement in statements:
    if statement["statement_id"] == "st-chp16-p376-swajer-secret-manuscripts-partial":
        statement["qualifiers"]["cross_reference_statement_ids"] = []

coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L39-46",
    "note": "P.376 body L46's sentence about the possible dispersal of Swajer's 'secret' manuscripts continues at p.377 L49; the passage is recorded as partial.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L70-84",
    "note": "P.373 notes L70-71, p.374 notes L72-75, p.375 notes L76-81, and p.376 notes 1-2 at L82-83 are migrated; p.376 note 3 at L84 is partial and continues in the p.377 source segment.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp16-p376-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidates),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "coverage": {BODY: "reviewed/partial", NOTES: "reviewed/partial"},
        "next_body_segment": BODY_NEXT,
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
    "mode": "applied", "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
    "partial_segments": [BODY, NOTES],
    "article_candidate_updated": "cand-10629",
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
