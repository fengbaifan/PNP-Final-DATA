"""Controlled S2 migration for chapter 17, printed p.380 (physical PDF page 2)."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-17.pdf"
SOURCE_SHA = "CBCB4E8F0EB163564F0B0C8E060C79F1A48981DB45072A772C3EA16642AD3CA4".lower()
PDF_SHA = "FA9C9A4EBC484C481D13B0AFB46F96BF94FE0631C65F0B742D0B0B9D9E0B7465".lower()

PREVIOUS_BODY = "chp-17:17_CHP-17_sec_i:l3-6"
BODY = "chp-17:17_CHP-17_sec_i:l8-20"
NOTES = "chp-17:17_CHP-17_sec_i:l26-35"
NEXT_BODY = "chp-17:17_CHP-17_sec_i:l22-24"
BACKUP_SUFFIX = ".bak-s2-chp17-p380-manfrin-apply-20261004"

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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("chapter 17 section I source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-17 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    9: "when a false rumour of his death reached Bologna",
    10: "Venice who spends anything on the fine arts",
    11: "posthumous edition of Tiepolo’s etchings Varj Capriccj",
    12: "Flemish) painting4—but it is notable",
    14: "letter to Pietro Edwards, who acted as his adviser",
    15: "tribute to the achievement of Venetian painting",
    16: "A printed catalogue, made for the sale, was published in 1856",
    20: "Cicogna 3007/XIII.",
    27: "Seminario Patriarcale, Venice—MSS. 566",
    29: "Meschini, 1806, II, p. 107",
    30: "The first record of Manfrin’s gallery was made by Pietro Edwards",
    31: "Biblioteca Correr—Epistolario Meschini",
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
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (PREVIOUS_BODY, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if coverage_by_id[PREVIOUS_BODY]["migration_status"] != "partial":
    raise SystemExit("p.379 body is no longer partial")
for segment_id in (BODY, NOTES):
    if coverage_by_id[segment_id]["disposition"] != "queued" or coverage_by_id[segment_id]["migration_status"] != "pending":
        raise SystemExit(f"p.380 coverage preconditions changed: {segment_id}")
if any(row["segment_id"] in {BODY, NOTES} for row in mentions):
    raise SystemExit("p.380 source segments already have mention rows")
if any(row.get("statement_id", "").startswith("st-chp17-p380-") for row in statements):
    raise SystemExit("p.380 statements already exist")

previous_statement_id = "st-chp17-pi-manfrin-established-as-leading-venetian-patron"
if previous_statement_id not in statement_by_id:
    raise SystemExit("p.379 cross-page statement is missing")
shared_ids = (
    "cand-0119", "cand-0270", "cand-0381", "cand-0382", "cand-0965", "cand-1239",
    "cand-1512", "cand-1513", "cand-1522", "cand-1670", "cand-2364", "cand-2569",
    "cand-2612", "cand-2624", "cand-2719", "cand-3398", "cand-4129", "cand-6589",
    "cand-8262", "cand-8534", "cand-9448", "cand-10605", "cand-10614", "cand-10680", "cand-10681",
)
if any(cid not in candidate_by_id for cid in shared_ids):
    raise SystemExit("one or more p.380 shared candidates are missing")
new_ids = [f"cand-{number}" for number in range(10689, 10695)]
if any(cid in candidate_by_id for cid in new_ids):
    raise SystemExit("one or more p.380 candidate IDs already exist")

new_candidate_specs = [
    ("cand-10689", "G. A. Armanni letter to Giuseppe Maria Sasso, 20 July 1790 (Seminario Patriarcale, MSS. 566)", "archive", BODY, 9,
     "A dated letter identified by Haskell's note 1; the manuscript was not consulted. The page image reads the writer's surname as Armanni, while S0 OCR has Armarmi."),
    ("cand-10690", "Unidentified volume of painters’ portraits (Biblioteca Correr, Stampe D.30)", "work", BODY, 11,
     "The source names a volume of painters' portraits and gives a Biblioteca Correr shelfmark, but supplies no title or author in this passage."),
    ("cand-10691", "Printed sale catalogue of the Manfrin gallery (1856; photographic copy at Biblioteca Correr)", "archive", BODY, 16,
     "An unnamed catalogue made for the sale and published in 1856; the cited photographic copy was not consulted."),
    ("cand-10692", "Catalogue of pictures remaining in the Manfrin collection, published by Ab. G. Nicoletti (1872; Biblioteca Marciana, Misc. C. 11231)", "archive", BODY, 17,
     "The catalogue and repository record are cited by Haskell but were not independently consulted."),
    ("cand-10693", "Manuscript Catalogo delle Stampe della Collezione annessa alla Galleria Manfrin (Biblioteca Correr, Cod. Cicogna 3007/XIII)", "archive", BODY, 18,
     "Undated manuscript catalogue named in Haskell's text; the manuscript was not consulted."),
    ("cand-10694", "Ab. G. Nicoletti (author of the 1872 catalogue of pictures remaining in the Manfrin collection)", "person", NOTES, 30,
     "The source gives an abbreviated form of the author's name; no fuller identity is inferred."),
]
for cid, name, suggested_type, segment_id, source_line, detail in new_candidate_specs:
    candidate = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{source_line}",
    }
    candidates.append(candidate)
    candidate_by_id[cid] = candidate

segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(8, 21)},
    NOTES: {number: source_lines[number - 1] for number in range(26, 36)},
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


def add_mention(candidate_id, surface, segment_id, line_start, line_end=None, note="", occurrence=0):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    if line_end is None:
        line_end = line_start
    start_bound = line_offsets[segment_id][line_start]
    end_bound = line_offsets[segment_id][line_end] + len(segment_lines[segment_id][line_end])
    text = segment_texts[segment_id][start_bound:end_bound]
    positions = []
    search_from = 0
    while True:
        position = text.find(surface, search_from)
        if position < 0:
            break
        positions.append(position)
        search_from = position + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface not found at {segment_id} L{line_start}-{line_end}: {surface!r} #{occurrence + 1}")
    start = start_bound + positions[occurrence]
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == segment_id]
    for other_start, other_end in occupied:
        if start < other_end and other_start < end:
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not nested or (start, end) == (other_start, other_end):
                raise SystemExit(f"overlapping mention span: {surface!r} at {segment_id} L{line_start}")
    planned_mentions.append({
        "mention_id": f"m-chp17-p380-manfrin-{len(planned_mentions) + 1:04d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# p.380 body: close the p.379 sentence and preserve the reported letter and quotation.
add_mention("cand-1512", "his", BODY, 9, note="Anaphora to Girolamo Manfrin in the cross-page sentence.")
add_mention("cand-3398", "Bologna", BODY, 9, note="City reached by the reported false rumour.")
add_mention("cand-0119", "G. A. Armarmi", BODY, 9, note="Exact S0 OCR anchor; p.380 image reads the indexed surname Armanni.")
add_mention("cand-2364", "Giuseppe Maria Sasso", BODY, 9, note="The recipient named in the reported letter.")
add_mention("cand-1512", "he", BODY, 9, note="Quoted pronoun refers to Manfrin.")
add_mention("cand-2719", "Venice", BODY, 10, note="City in Armanni's quoted characterization.")
add_mention("cand-1512", "Manfrin", BODY, 11, note="Subject of the account of the 1785 dedication.")
add_mention("cand-2569", "Tiepolo", BODY, 11, note="Giambattista Tiepolo, identified by note 2.")
add_mention("cand-2612", "Varj Capriccj", BODY, 11, note="Index subentry for Tiepolo's etchings; note 2 gives the edition title and dedication.")
add_mention("cand-1512", "him", BODY, 11, note="Anaphora to Manfrin as dedicatee.")
add_mention("cand-10690", "volume of painters’ portraits", BODY, 11, note="Unidentified volume; note 3 gives Biblioteca Correr shelfmark Stampe D.30.")
add_mention("cand-1512", "he", BODY, 11, note="Anaphora to Manfrin's position in the Venetian art world.")
add_mention("cand-2719", "Venetian", BODY, 11, note="Geographic/cultural adjective in Haskell's description of the art world.")
add_mention("cand-1512", "his", BODY, 11, note="Possessive reference to Manfrin's death.")
add_mention("cand-1512", "he", BODY, 11, note="Anaphora to Manfrin as collector.", occurrence=1)
add_mention("cand-1513", "gallery", BODY, 11, note="Collection-specific Manfrin index subentry; the passage concerns its scope.")
add_mention("cand-1513", "Manfrin", BODY, 12, note="Collection owner in the sentence about pre-sixteenth-century art.")
add_mention("cand-1522", "Mantegna", BODY, 12, note="Andrea Mantegna, an indexed painter cited as an endpoint of the collection's Venetian pictures.")
add_mention("cand-0270", "Bellini", BODY, 12, note="Giovanni Bellini, as indexed at p.380.")
add_mention("cand-1239", "Francesco Guardi", BODY, 13, note="Named contemporary painter included in Haskell's account of the collection.")
add_mention("cand-2624", "Gian Domenico Tiepolo", BODY, 13, note="Named contemporary painter included in Haskell's account of the collection.")
add_mention("cand-1512", "Manfrin", BODY, 14, note="Private attitude to connoisseurship.")
add_mention("cand-1515", "a letter", BODY, 14, note="Manfrin-to-Edwards letter indexed under his gallery formation; note 6 gives its source and Appendix 7 cross-reference.")
add_mention("cand-0965", "Pietro Edwards", BODY, 14, note="Manfrin's adviser and letter recipient.")
add_mention("cand-1512", "his", BODY, 14, note="Possessive reference to Manfrin's adviser.")
add_mention("cand-1512", "he", BODY, 14, note="Anaphora to Manfrin as the letter's writer.")
add_mention("cand-0965", "yourself", BODY, 14, note="Second-person address to Pietro Edwards in the quoted letter.")
add_mention("cand-1670", "Sig. Gio.\nBattista Mingardi", BODY, 14, 15, note="Named expert in the letter; exact cross-line S0 span.")
add_mention("cand-1513", "my gallery", BODY, 14, note="Possessive reference to Manfrin's collection in his quoted letter.")
add_mention("cand-1513", "pictures", BODY, 14, note="Objects to be included in the Manfrin collection.")
add_mention("cand-1513", "my gallery", BODY, 15, note="Repeated reference to Manfrin's collection.")
add_mention("cand-1513", "pictures", BODY, 15, note="Pictures subject to expert selection and confidential rejection.")
add_mention("cand-1512", "my own guidance", BODY, 15, note="Manfrin's stated private purpose for keeping experts' objections confidential.")
add_mention("cand-1512", "Manfrin’s words", BODY, 15, note="Haskell's explicit attribution of the ensuing interpretation.")
add_mention("cand-1513", "the gallery", BODY, 15, note="Collection as historical choice and tribute.")
add_mention("cand-1513", "Venetian painting", BODY, 15, note="Artistic tradition described as the object of the gallery's tribute.")
add_mention("cand-10691", "A printed catalogue, made for the sale", BODY, 16, note="Unnamed catalogue of the sale of the Manfrin collection.")
add_mention("cand-10691", "this", BODY, 16, note="Anaphoric reference to the 1856 printed catalogue.")
add_mention("cand-8262", "Biblioteca Correr", BODY, 17, note="Repository of the photographic copy of the 1856 catalogue.")
add_mention("cand-10692", "A further catalogue", BODY, 17, note="Catalogue of pictures still remaining in the collection.")
add_mention("cand-1513", "the collection", BODY, 17, note="Manfrin collection whose remaining pictures were catalogued.")
add_mention("cand-10694", "Ab. G. Nicoletti", BODY, 18, note="Abbreviated author name as printed/transcribed by Haskell.")
add_mention("cand-9448", "Biblioteca Marciana", BODY, 18, note="Repository named for the 1872 catalogue.")
add_mention("cand-10692", "Misc. C. 11231", BODY, 18, note="Shelfmark for the 1872 catalogue.")
add_mention("cand-10693", "Catalogo delle\nStampe della Collezione annessa alla Galleria Manfrin, Venezia (n.d.)", BODY, 18, 19,
            note="Full manuscript catalogue title and undated status as transcribed in S0.")
add_mention("cand-8262", "Biblioteca Correr", BODY, 19, note="Repository named for the manuscript print catalogue.")
add_mention("cand-10693", "Cicogna 3007/XIII", BODY, 20, note="Manuscript shelfmark for the catalogue.")

# p.380 notes 1-6; source lines 32-35 are p.381 notes and remain pending.
add_mention("cand-6589", "Seminario Patriarcale", NOTES, 27, note="Repository named for the dated Armanni-Sasso letter.")
add_mention("cand-2719", "Venice", NOTES, 27, note="City in the manuscript repository locator.")
add_mention("cand-10614", "MSS. 566", NOTES, 27, note="Volume locator within the Armanni-Sasso letter collection.")
add_mention("cand-10689", "Letter of 20 July 1790", NOTES, 27, note="Dated letter identifier; the manuscript was not consulted.")
add_mention("cand-2612", "Varj capriccj inventati, ed incisi dal celebre Gio. Battista Tiepolo", NOTES, 28,
            note="Edition title as transcribed in S0; page image correction is recorded on the statement.")
add_mention("cand-2569", "Gio. Battista Tiepolo", NOTES, 28, note="Named etcher/author of the edition.")
add_mention("cand-1512", "S. Girolamo Manfrin", NOTES, 28, note="Dedicatee named in the edition title.")
add_mention("cand-8262", "Biblioteca Correr", NOTES, 28, note="Repository for the volume of painters' portraits.")
add_mention("cand-2719", "Venice", NOTES, 28, note="City in the repository locator.")
add_mention("cand-10690", "Stampe D.30", NOTES, 28, note="Shelfmark for the unidentified portrait volume.")
add_mention("cand-10680", "Meschini", NOTES, 29, note="Surname form in Haskell's citation.")
add_mention("cand-10681", "Meschini, 1806, II, p. 107", NOTES, 29, note="Bibliographic locator for the quoted description; work not independently consulted.")
add_mention("cand-1513", "Galleria", NOTES, 29, note="Manfrin gallery described in the Meschini quotation.")
add_mention("cand-10681", "quest’arte", NOTES, 29, note="The art whose development the quoted Meschini passage says the gallery could display.")
add_mention("cand-1512", "Manfrin’s gallery", NOTES, 30, note="The gallery for which Edwards made the first record.")
add_mention("cand-0965", "Pietro Edwards", NOTES, 30, note="Adviser and maker of the first record, as reported by Haskell.")
add_mention("cand-1512", "his adviser", NOTES, 30, note="Anaphoric reference to Manfrin's adviser Pietro Edwards.")
add_mention("cand-6589", "Seminario Patriarcale", NOTES, 30, note="Repository for MS. 788.13.")
add_mention("cand-2719", "Venice", NOTES, 30, note="City in the repository locator.")
add_mention("cand-8534", "MSS. 788.13", NOTES, 30, note="Existing archive candidate for Edwards's inventories in this manuscript.")
add_mention("cand-8262", "Biblioteca Correr", NOTES, 31, note="Repository named for the Manfrin-Edwards letter source.")
add_mention("cand-10605", "Epistolario Meschini", NOTES, 31, note="Exact S0 anchor; the page image reads 'Moschini', matching the existing collection candidate.")

corrections_body = [
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 9, "ocr": "Armarmi", "print": "Armanni", "basis": "CHP-17.pdf physical page 2, printed page 380."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 13, "ocr": "Gian Domenico Tiepolo.", "print": "Gian Domenico Tiepolo.5", "basis": "CHP-17.pdf physical page 2 shows printed note marker 5, omitted by S0 OCR."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 15, "ocr": "snobbishness óf", "print": "snobbishness of", "basis": "CHP-17.pdf physical page 2, printed page 380."},
]
corrections_notes = [
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 28, "ocr": "allTlLmo", "print": "all’Ill.mo", "basis": "CHP-17.pdf physical page 2, printed page 380."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 29, "ocr": "de’più spetti - - pennelli", "print": "de’ più esperti pennelli", "basis": "CHP-17.pdf physical page 2, printed page 380."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 31, "ocr": "8 Biblioteca Correr—Epistolario Meschini", "print": "6 Biblioteca Correr—Epistolario Moschini", "basis": "CHP-17.pdf physical page 2, printed page 380."},
]


def quote_for(segment_id, start_line, end_line):
    return "\n".join(segment_lines[segment_id][number] for number in range(start_line, end_line + 1))


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, text_layer, qualification, mentioned_ids, quote=None, speaker="Haskell",
                   relation_candidate=False, footnote=None, **extra):
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 380, "pdf_physical_page": 2,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if footnote:
        marker, note_range, body_range, note_ids, link_note = footnote
        qualifiers.update({
            "footnote_marker": marker, "footnote_segment": NOTES,
            "footnote_line_range": note_range, "footnote_text_pending": False,
            "footnote_body_link_status": "linked", "footnote_body_line_range": body_range,
            "footnote_note_statement_ids": note_ids, "footnote_link_note": link_note,
        })
    qualifiers.update(extra)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote or quote_for(segment_id, start_line, end_line),
        "origin": "book", "source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md",
    })


note_ids = {
    "1": ["st-chp17-p380-note1-armanni-sasso-letter-locator"],
    "2": ["st-chp17-p380-note2-varj-capriccj-edition-locator"],
    "3": ["st-chp17-p380-note3-portrait-volume-locator"],
    "4": ["st-chp17-p380-note4-meschini-gallery-description"],
    "5": ["st-chp17-p380-note5-edwards-record", "st-chp17-p380-note5-sale-catalogue",
          "st-chp17-p380-note5-nicoletti-catalogue", "st-chp17-p380-note5-print-catalogue"],
    "6": ["st-chp17-p380-note6-edwards-letter-source"],
}


def link(marker, footnote_range, body_range, explanation):
    return (marker, footnote_range, body_range, note_ids[marker], explanation)


make_statement(
    "st-chp17-p380-manfrin-death-rumour-reaches-bologna", BODY, "cand-1512", None,
    "false_report_of_death_reached_bologna", 9, 10,
    "Haskell says that within five years a false rumour of Manfrin's death reached Bologna.",
    "authorial report", "The event and timing are only as reported by Haskell; the rumour is explicitly described as false.",
    ["cand-1512", "cand-3398"],
)
make_statement(
    "st-chp17-p380-armanni-writes-sasso-after-rumour", BODY, "cand-0119", "cand-2364",
    "wrote_to_sasso_in_alarm_after_false_manfrin_death_rumour", 9, 10,
    "Haskell says painter and dealer G. A. Armanni wrote to Giuseppe Maria Sasso in alarm when the false rumour reached Bologna.",
    "authorial report", "The page image reads the surname Armanni; the source transcription is retained as the exact anchor. The manuscript is not independently checked.",
    ["cand-0119", "cand-2364", "cand-1512", "cand-3398", "cand-10689"], relation_candidate=True,
    footnote=link("1", "L27-L27", "L9-L10", "P.380 note 1 locates the dated Armanni-Sasso letter at Seminario Patriarcale MSS. 566."),
    ocr_corrections=corrections_body[:1],
)
make_statement(
    "st-chp17-p380-armanni-calls-manfrin-venices-only-art-spender", BODY, "cand-0119", "cand-1512",
    "described_as_almost_only_venetian_spending_on_fine_arts", 9, 10,
    "In the quoted letter, Armanni calls Manfrin almost the only man in Venice who spends anything on the fine arts.",
    "quoted letter", "This is Armanni's emphatic, comparative characterization as quoted by Haskell, not a census of Venetian art spending.",
    ["cand-0119", "cand-1512", "cand-2364", "cand-2719", "cand-10689"], speaker="G. A. Armanni, as quoted by Haskell",
    footnote=link("1", "L27-L27", "L9-L10", "P.380 note 1 identifies the cited letter as dated 20 July 1790."),
)
make_statement(
    "st-chp17-p380-varj-capriccj-dedicated-to-manfrin", BODY, "cand-2612", "cand-1512",
    "posthumous_1785_etching_edition_dedicated_to_manfrin", 11, 11,
    "Haskell says that Tiepolo's posthumous edition of the etchings Varj Capriccj was dedicated to Manfrin in 1785.",
    "authorial report", "The edition title and dedication are given in Haskell's note 2; the cited edition was not independently examined.",
    ["cand-2569", "cand-2612", "cand-1512"], relation_candidate=True,
    footnote=link("2", "L28-L28", "L11-L11", "P.380 note 2 supplies the edition's full title, dedicatee and 1785 imprint."),
)
make_statement(
    "st-chp17-p380-painters-portraits-volume-followed", BODY, "cand-1513", "cand-10690",
    "painters_portraits_volume_followed_two_years_after_1785_edition", 11, 11,
    "Haskell says a volume of painters' portraits followed two years after the 1785 etching edition.",
    "authorial report", "The relative interval is preserved; this passage does not name the volume's title or author.",
    ["cand-1513", "cand-10690", "cand-2569"], relation_candidate=True,
    footnote=link("3", "L28-L28", "L11-L11", "P.380 note 3 gives the Biblioteca Correr shelfmark Stampe D.30."),
)
make_statement(
    "st-chp17-p380-manfrin-forefront-until-1802", BODY, "cand-1512", "cand-2719",
    "remained_forefront_of_venetian_art_world_until_death_in_1802", 11, 11,
    "Haskell says Manfrin remained in the forefront of the Venetian art world until his death in 1802.",
    "authorial report", "'In the forefront' is Haskell's qualitative characterization; no ranking is implied.",
    ["cand-1512", "cand-2719"],
)
make_statement(
    "st-chp17-p380-gallery-apparent-historical-survey", BODY, "cand-1513", None,
    "apparently_intended_as_general_view_of_italian_and_some_flemish_painting", 11, 12,
    "Haskell says the vast gallery was apparently designed to give a general view of Italian painting and, to some extent, Flemish painting.",
    "authorial interpretation", "'Apparently' and 'to some extent' are retained; the passage does not define the precise scope of the holdings.",
    ["cand-1513"], footnote=link("4", "L29-L29", "L11-L12", "P.380 note 4 quotes Meschini on the gallery's intended historical survey."),
)
make_statement(
    "st-chp17-p380-manfrin-excluded-pre-sixteenth-century-art", BODY, "cand-1512", "cand-1513",
    "gallery_selection_did_not_follow_scholarly_opinion_on_pre_sixteenth_century_art", 12, 12,
    "Haskell says Manfrin took no account of a scholarly opinion then current that art had value before the sixteenth century.",
    "authorial interpretation", "The scholarly position is reported generally; no individual scholar or specific theory is identified.",
    ["cand-1512", "cand-1513"], relation_candidate=True,
)
make_statement(
    "st-chp17-p380-collection-venetian-painters-span", BODY, "cand-1513", None,
    "venetian_picture_sequence_from_mantegna_and_bellini_to_guardi_and_gian_domenico_tiepolo", 12, 13,
    "Haskell says the Venetian pictures began with Mantegna and Bellini and included great and lesser painters through Manfrin's contemporaries Francesco Guardi and Gian Domenico Tiepolo.",
    "authorial report", "The statement describes the collection's represented span; it does not identify individual pictures or settle attribution questions.",
    ["cand-1513", "cand-1522", "cand-0270", "cand-1239", "cand-2624"], relation_candidate=True,
    ocr_corrections=corrections_body[1:2],
)
make_statement(
    "st-chp17-p380-manfrin-few-connoisseurship-pretensions", BODY, "cand-1512", None,
    "made_few_private_pretensions_to_connoisseurship", 14, 14,
    "Haskell says Manfrin made few pretensions to connoisseurship in private.",
    "authorial characterization", "The qualifier 'in private, at least' limits the claim to the described private setting.",
    ["cand-1512"],
)
make_statement(
    "st-chp17-p380-edwards-advised-manfrin", BODY, "cand-0965", "cand-1512",
    "acted_as_manfrins_adviser", 14, 14,
    "Haskell identifies Pietro Edwards as an adviser to Manfrin.",
    "authorial report", "The adviser role is stated by Haskell; its scope is not further specified here.",
    ["cand-0965", "cand-1512"], relation_candidate=True,
)
make_statement(
    "st-chp17-p380-manfrin-delegated-picture-selection", BODY, "cand-1512", "cand-0965",
    "delegated_selection_identification_and_exclusion_of_pictures_to_edwards_and_mingardi", 14, 15,
    "In the quoted letter, Manfrin asks Edwards and Gio. Battista Mingardi to choose, identify and exclude pictures as they see fit, without regard to expense.",
    "quoted letter", "The first-person statement is Manfrin's as quoted by Haskell; the original letter is located in note 6 but not independently consulted.",
    ["cand-1512", "cand-0965", "cand-1670", "cand-1513"], speaker="Girolamo Manfrin, as quoted by Haskell",
    relation_candidate=True, footnote=link("6", "L31-L31", "L14-L15", "P.380 note 6 identifies the letter's Correr source and Appendix 7 publication."),
)
make_statement(
    "st-chp17-p380-manfrin-prioritized-highest-quality", BODY, "cand-1512", "cand-1513",
    "wanted_only_pictures_of_highest_quality_in_gallery", 14, 14,
    "In the quoted letter, Manfrin says he wanted only pictures of the highest quality in his gallery.",
    "quoted letter", "This is Manfrin's stated collecting criterion in a letter quoted by Haskell, not an objective quality assessment of the collection.",
    ["cand-1512", "cand-1513"], speaker="Girolamo Manfrin, as quoted by Haskell",
    footnote=link("6", "L31-L31", "L14-L15", "P.380 note 6 identifies the letter as published in Appendix 7."),
)
make_statement(
    "st-chp17-p380-manfrin-kept-experts-objections-private", BODY, "cand-1512", "cand-0965",
    "accepted_private_confidentiality_of_experts_rejections", 15, 15,
    "In the quoted letter, Manfrin says he accepts the experts' terms that objections to pictures remain private for his own guidance.",
    "quoted letter", "The quotation attributes this confidentiality arrangement to Manfrin; it does not show that every rejection was in fact recorded or concealed.",
    ["cand-1512", "cand-0965", "cand-1670", "cand-1513"], speaker="Girolamo Manfrin, as quoted by Haskell",
    relation_candidate=True, footnote=link("6", "L31-L31", "L14-L15", "P.380 note 6 identifies the letter's source."),
)
make_statement(
    "st-chp17-p380-haskell-snobbishness-characterization", BODY, "cand-1512", None,
    "letter_displays_snobbishness_of_self_made_millionaire_in_haskell_interpretation", 15, 15,
    "Haskell interprets Manfrin's words as showing the snobbishness of a self-made millionaire.",
    "authorial interpretation", "This is Haskell's evaluative characterization, not a neutral fact about Manfrin's psychology.",
    ["cand-1512"], ocr_corrections=corrections_body[2:3],
)
make_statement(
    "st-chp17-p380-gallery-choice-quasi-national-status", BODY, "cand-1513", None,
    "historical_choice_gave_gallery_some_definitive_status_of_national_institution", 15, 15,
    "Haskell says the gallery's historical choice of pictures gave it something of the definitive status of a national institution.",
    "authorial interpretation", "'Some of' and 'was to have' mark an analogy and intended status, not formal public or legal institutional status.",
    ["cand-1513"],
)
make_statement(
    "st-chp17-p380-gallery-tribute-to-venetian-painting", BODY, "cand-1513", "cand-2719",
    "intended_tribute_to_venetian_painting_when_it_seemed_near_its_end", 15, 15,
    "Haskell says the gallery was to be a tribute to Venetian painting at a time when it was felt that Venetian painting was virtually at an end.",
    "authorial interpretation", "This is Haskell's account of the gallery's intended meaning and contemporary perception, not proof that Venetian painting literally ceased.",
    ["cand-1513", "cand-2719"], relation_candidate=True,
)
make_statement(
    "st-chp17-p380-sale-catalogue-1856", BODY, "cand-10691", "cand-8262",
    "1856_sale_catalogue_photographic_copy_at_biblioteca_correr", 16, 17,
    "Haskell says a printed catalogue made for the sale was published in 1856 and that a photographic copy exists at Biblioteca Correr.",
    "authorial bibliographic report", "The catalogue and photographic copy are cited, not independently consulted.",
    ["cand-10691", "cand-8262", "cand-1513"], relation_candidate=True,
)
make_statement(
    "st-chp17-p380-nicoletti-catalogue-1872", BODY, "cand-10694", "cand-10692",
    "published_1872_catalogue_of_pictures_remaining_in_manfrin_collection", 17, 18,
    "Haskell says Ab. G. Nicoletti published a catalogue of pictures remaining in the collection in 1872, cited at Biblioteca Marciana, Misc. C. 11231.",
    "authorial bibliographic report", "The catalogue and repository record are cited, not independently consulted; the abbreviated author form remains unresolved.",
    ["cand-10694", "cand-10692", "cand-1513", "cand-9448"], relation_candidate=True,
)
make_statement(
    "st-chp17-p380-undated-print-catalogue", BODY, "cand-10693", "cand-8262",
    "undated_manuscript_catalogue_of_print_collection_at_biblioteca_correr", 18, 20,
    "Haskell identifies an undated manuscript Catalogo delle Stampe della Collezione annessa alla Galleria Manfrin at Biblioteca Correr, Cod. Cicogna 3007/XIII.",
    "authorial bibliographic report", "The manuscript was not consulted; title, repository and shelfmark follow the source transcription.",
    ["cand-10693", "cand-8262", "cand-1513"], relation_candidate=True,
)

# Notes are recorded as Haskell's citation trail; cited archives and publications were not consulted.
make_statement(
    "st-chp17-p380-note1-armanni-sasso-letter-locator", NOTES, "cand-6589", "cand-10689",
    "manuscript_locator_for_armanni_sasso_letter_of_20_july_1790", 27, 27,
    "Haskell locates the letter of 20 July 1790 in Seminario Patriarcale, Venice, MSS. 566.",
    "archival locator", "The manuscript was not consulted; the locator is preserved as cited.",
    ["cand-6589", "cand-2719", "cand-10614", "cand-10689"], quote=quote_for(NOTES, 27, 27),
)
make_statement(
    "st-chp17-p380-note2-varj-capriccj-edition-locator", NOTES, "cand-2612", "cand-1512",
    "edition_title_identifies_tiepolo_etchings_dedicated_to_manfrin_in_1785", 28, 28,
    "Haskell cites the 1785 edition Varj capriccj inventati, ed incisi dal celebre Gio. Battista Tiepolo, dedicated to Manfrin.",
    "bibliographic locator", "The edition was not independently consulted; the printed page corrects the S0 OCR form of all’Ill.mo.",
    ["cand-2612", "cand-2569", "cand-1512"], quote=quote_for(NOTES, 28, 28), relation_candidate=True,
    ocr_corrections=corrections_notes[:1],
)
make_statement(
    "st-chp17-p380-note3-portrait-volume-locator", NOTES, "cand-8262", "cand-10690",
    "correr_stampe_d30_locator_for_painters_portraits_volume", 28, 28,
    "Haskell gives Biblioteca Correr, Venice, Stampe D.30 as the locator for the volume of painters' portraits.",
    "repository locator", "The item itself and current shelfmark were not independently checked.",
    ["cand-8262", "cand-2719", "cand-10690"], quote=quote_for(NOTES, 28, 28),
)
make_statement(
    "st-chp17-p380-note4-meschini-gallery-description", NOTES, "cand-10680", "cand-1513",
    "quoted_meschini_description_of_gallery_as_historical_survey", 29, 29,
    "Haskell quotes Meschini describing a multi-room gallery that proceeded from the earliest painters to those of his day and was intended to show the gains and losses of art across different periods and schools.",
    "secondary quotation within Haskell's note", "The original Meschini work was not consulted; the S0 OCR wording is retained as the source anchor, with the page-image reading noted.",
    ["cand-10680", "cand-10681", "cand-1513"], quote=quote_for(NOTES, 29, 29),
    speaker="G. A. Meschini, as quoted by Haskell", ocr_corrections=[corrections_notes[1]],
)
make_statement(
    "st-chp17-p380-note5-edwards-record", NOTES, "cand-0965", "cand-8534",
    "identified_as_maker_of_first_record_of_manfrin_gallery", 30, 30,
    "Haskell says Pietro Edwards made the first record of Manfrin's gallery shortly before the end of the eighteenth century and locates it in Seminario Patriarcale MSS. 788.13.",
    "archival locator", "The manuscript was not consulted; existing Edwards inventories candidate is reused pending S3 identity and scope review.",
    ["cand-0965", "cand-1512", "cand-1513", "cand-6589", "cand-8534"], quote=quote_for(NOTES, 30, 30),
    footnote=link("5", "L30-L30", "L13-L20", "P.380 note 5 cites Edwards's first record; its repeated catalogue details in the printed note duplicate body L16-L20 and are represented by those body statements."),
)
make_statement(
    "st-chp17-p380-note6-edwards-letter-source", NOTES, "cand-8262", "cand-1515",
    "manfrin_edwards_letter_in_epistolario_moschini_published_in_appendix_7", 31, 31,
    "Haskell identifies Biblioteca Correr's Epistolario Moschini as the source for the Manfrin-Edwards letter published in full in Appendix 7.",
    "archival locator and internal cross-reference", "The letter is an existing index subentry; Appendix 7 is part of this book and remains to be semantically processed at its source-order position.",
    ["cand-8262", "cand-10605", "cand-1515"], quote=quote_for(NOTES, 31, 31), relation_candidate=True,
    ocr_corrections=corrections_notes[2:],
)

# Close the prior page's incomplete sentence with the cross-page event statement.
previous = statement_by_id[previous_statement_id]
old_quote = previous.get("original_quote", "")
continuation_phrase = "Indeed, within five years,"
if continuation_phrase not in old_quote:
    raise SystemExit("expected p.379 cross-page tail was not found in the prior quote")
previous["original_quote"] = old_quote.rsplit(continuation_phrase, 1)[0].rstrip()
previous["qualifiers"]["continuation"] = "The next sentence begins 'Indeed, within five years,' and continues in st-chp17-p380-manfrin-death-rumour-reaches-bologna at p.380 L9-L10; the p.379 statement itself is complete."

coverage_by_id[PREVIOUS_BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-6",
    "note": "Printed folio i body is complete; the trailing 'Indeed, within five years' begins the next sentence, migrated at p.380 L9-L10.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L9-20",
    "note": "Printed page 380 checked against CHP-17.pdf physical page 2; closes p.379 cross-page sentence. OCR corrections are recorded in statement qualifiers; S0 source is unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L27-31",
    "note": "P.380 footnotes 1-6 checked against physical page 2 and linked to body. The section OCR's note 5 stops after the Edwards manuscript record; the printed continuation repeats the catalogue details already present in body L16-20, crosschecked against the whole-chapter OCR and page image and represented by those body statements. The continuation segment also contains p.381 notes at L32-35, which remain pending for the next page.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp17-p380-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidate_specs),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "completed_segments": [PREVIOUS_BODY, BODY], "partial_segment": NOTES,
        "partial_line_ranges": "L27-31", "next_body": NEXT_BODY,
        "new_candidate_ids": [row[0] for row in new_candidate_specs],
        "new_statement_ids": new_statement_ids,
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
mentions.extend(planned_mentions)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({
    "mode": "applied", "new_candidates": len(new_candidate_specs),
    "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
    "completed_segments": [PREVIOUS_BODY, BODY], "partial_segment": NOTES,
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
