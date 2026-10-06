"""Controlled S2 migration for chapter 17, first printed folio i."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INTRO = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_intro.md"
BODY_SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-17.pdf"
INTRO_SHA = "5252c5d3f0a9b52661b0e95d7a12c6f51aef46a6e7faa391794b356da7043e66"
BODY_SHA = "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4"
PDF_SHA = "fa9c9a4ebc484c481d13b0afb46f96bf94fe0631c65f0b742d0b0b9d9e0b7465"

INTRO_GENERATED = "chp-17:17_CHP-17_intro:l1-1"
TITLE = "chp-17:17_CHP-17_intro:l3-5"
NOTES = "chp-17:17_CHP-17_intro:l7-13"
BODY_GENERATED = "chp-17:17_CHP-17_sec_i:l1-1"
BODY = "chp-17:17_CHP-17_sec_i:l3-6"
BODY_NEXT = "chp-17:17_CHP-17_sec_i:l8-20"
BACKUP_SUFFIX = ".bak-s2-chp17-folio-i-manfrin-apply-20261004"

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


if hashlib.sha256(INTRO.read_bytes()).hexdigest() != INTRO_SHA:
    raise SystemExit("chapter 17 intro source changed")
if hashlib.sha256(BODY_SOURCE.read_bytes()).hexdigest() != BODY_SHA:
    raise SystemExit("chapter 17 section I source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-17 PDF asset changed")

intro_lines = INTRO.read_text(encoding="utf-8-sig").splitlines()
body_source_lines = BODY_SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    (INTRO, 3): "[Page 2]", (INTRO, 4): "Chapter 17", (INTRO, 5): "THE LAST PATRONS",
    (INTRO, 8): "Most of the available material about Manfrin is still unpublished",
    (INTRO, 10): "Risposta alla lettera apologetica impacciale",
    (INTRO, 11): "Inquisitori, 53 8, p. 43", (INTRO, 12): "6 ibid., 540, p. 6",
    (INTRO, 13): "8 Tassini: Curiosità Veneziane",
    (BODY_SOURCE, 3): "OR a full generation before the Republic finally collapsed",
    (BODY_SOURCE, 4): "Ffeeling that an epoch was drawing to a close",
    (BODY_SOURCE, 5): "Girolamo Manfrin was almost the caricature",
    (BODY_SOURCE, 6): "Venice4; but this was revoked",
}
for (path, line_number), fragment in required.items():
    lines = intro_lines if path == INTRO else body_source_lines
    if fragment.casefold() not in lines[line_number - 1].casefold():
        raise SystemExit(f"required source text changed at {path.name}:L{line_number}: {fragment}")

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

for segment_id in (INTRO_GENERATED, TITLE, NOTES, BODY_GENERATED, BODY):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
for segment_id in (TITLE, NOTES, BODY):
    if coverage_by_id[segment_id]["disposition"] != "queued" or coverage_by_id[segment_id]["migration_status"] != "pending":
        raise SystemExit(f"S2 coverage preconditions changed: {segment_id}")
for segment_id in (INTRO_GENERATED, BODY_GENERATED):
    if coverage_by_id[segment_id]["disposition"] != "queued" or coverage_by_id[segment_id]["migration_status"] != "pending":
        raise SystemExit(f"generated heading preconditions changed: {segment_id}")
if any(row["segment_id"] in {TITLE, NOTES, BODY} for row in mentions):
    raise SystemExit("p.379 source segments already have mention rows")
if any(row.get("statement_id", "").startswith("st-chp17-pi-") for row in statements):
    raise SystemExit("p.379 statements already exist")
existing_ids = ("cand-1512", "cand-2719", "cand-4129", "cand-8160", "cand-8262", "cand-8838", "cand-9209", "cand-9448", "cand-10172", "cand-10464")
if any(cid not in candidate_by_id for cid in existing_ids):
    raise SystemExit("one or more shared p.379 candidate references are missing")
new_ids = [f"cand-{number}" for number in range(10674, 10689)]
if any(cid in candidate_by_id for cid in new_ids):
    raise SystemExit("one or more p.379 candidate IDs already exist")

new_candidate_specs = [
    ("cand-10674", "Venier family referenced in Girolamo Manfrin's 1787 property purchase", "family", BODY, 6,
     "The text names an ancient family of Venier whose palace and country house Manfrin bought; do not merge this family with the indexed individual Leonardo Venier."),
    ("cand-10675", "Unidentified Venier-family palace on Cannaregio bought by Girolamo Manfrin in 1787", "place", BODY, 6,
     "The palace is described by former family ownership and location only; no formal name or current identity is supplied."),
    ("cand-10676", "Cannaregio (location of the unidentified Venier-family palace)", "place", BODY, 6,
     "The passage identifies the district but no street or exact building address."),
    ("cand-10677", "Unidentified Venier-family country house near Treviso bought by Girolamo Manfrin in 1787", "place", BODY, 6,
     "The house is not named; its former family ownership and approximate location are retained without guessing its identity."),
    ("cand-10678", "Dalmatia (location of Manfrin's tobacco-plantation monopoly)", "place", BODY, 5,
     "The source gives the historical regional name and supplies no narrower plantation location."),
    ("cand-10679", "1769 grant to Girolamo Manfrin of a monopoly over tobacco plantations in Dalmatia", "event", BODY, 5,
     "A reported concession; the granting authority, exact territory, terms, and underlying record are not independently established here."),
    ("cand-10680", "Girolamo A. Meschini (author named in Haskell's Manfrin note)", "person", NOTES, 8,
     "The source supplies initials and surname only; no fuller identity is inferred."),
    ("cand-10681", "G. A. Meschini, 1806, volume II, page 107 (general Manfrin account cited by Haskell)", "archive", NOTES, 8,
     "Haskell identifies this as the only general account of Manfrin and his gallery; the cited work and page were not consulted."),
    ("cand-10682", "Sonetti XVI ossiano Satire contro il Manfrin, Impressario di Tabacchi (Biblioteca Correr, Cod. Cicogna 2947/18)", "archive", NOTES, 9,
     "Haskell cites a manuscript locator for satirical sonnets; the manuscript was not consulted and the Roman numeral/title wording follows the page transcription."),
    ("cand-10683", "Risposta alla lettera apologetica imparziale per il Cittadino Gerolamo Manfrin (Venice, 1797; Biblioteca Marciana 183.C.89, p.321)", "archive", NOTES, 10,
     "Pamphlet cited by Haskell as one example of controversial material; the pamphlet and catalogue record were not consulted."),
    ("cand-10684", "Archivio di Stato, Venice, Inquisitori, register 538, p.43 (29 Genaro 1770)", "archive", NOTES, 11,
     "Archival locator cited in Haskell's note to the banishment account; the record was not consulted. The page image reads register 538, while S0 has '53 8'."),
    ("cand-10685", "Archivio di Stato, Venice, Inquisitori, register 540, p.6 (12 Giugno 1786)", "archive", NOTES, 12,
     "Haskell's 'ibid.' continues the prior Archivio di Stato/Inquisitori locator; the record was not consulted."),
    ("cand-10686", "Tassini (surname-only author form in Haskell's p.379 note 6)", "person", NOTES, 13,
     "The note supplies surname only; identity with other Tassini candidates remains for S3."),
    ("cand-10687", "Tassini, Curiosità Veneziane, 4th edition (1887)", "archive", NOTES, 13,
     "Haskell cites this edition for the Treviso country-house reference; title and edition were not independently consulted."),
    ("cand-10688", "Girolamo Manfrin's reported lifetime banishment from Venice and later revocation", "event", BODY, 5,
     "Haskell reports an exile for life and its later revocation; the cited 1770 archive locator was not independently checked."),
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
    TITLE: {number: intro_lines[number - 1] for number in range(3, 6)},
    NOTES: {number: intro_lines[number - 1] for number in range(7, 14)},
    BODY: {number: body_source_lines[number - 1] for number in range(3, 7)},
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
mention_counter = 0


def add_mention(candidate_id, surface, segment_id, line_start, line_end=None, note="", occurrence=0):
    global mention_counter
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
        raise SystemExit(f"surface occurrence not found at {segment_id} L{line_start}-{line_end}: {surface!r} #{occurrence + 1}")
    start = start_bound + positions[occurrence]
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == segment_id]
    for other_start, other_end in occupied:
        if start < other_end and other_start < end:
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not nested or (start, end) == (other_start, other_end):
                raise SystemExit(f"duplicate or crossing mention span: {surface!r} at {segment_id} L{line_start}")
    mention_counter += 1
    planned_mentions.append({
        "mention_id": f"m-chp17-pi-manfrin-{mention_counter:04d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# Body: named entities, places, and anaphoric references.
add_mention("cand-8838", "Republic", BODY, 3, note="The Venetian polity; distinct from Venice as a city.")
add_mention("cand-4129", "patrons", BODY, 4, note="Reuses the broad art-patronage term candidate; picture collectors remain a general role category here.")
add_mention("cand-2719", "Venice", BODY, 4, note="The city whose earlier independence is the object of memory.")
add_mention("cand-1512", "Girolamo Manfrin", BODY, 5, note="Full name; maps to the p.379 index candidate, with S3 identity review still pending.")
add_mention("cand-1512", "He", BODY, 5, note="Anaphoric reference to Girolamo Manfrin.", occurrence=0)
add_mention("cand-1512", "Manfrin", BODY, 5, note="Repeated named reference.", occurrence=1)
add_mention("cand-1512", "He", BODY, 5, note="Anaphoric reference to Girolamo Manfrin.", occurrence=1)
add_mention("cand-8160", "Zara", BODY, 5, note="Birthplace as named in the source.")
add_mention("cand-1512", "his", BODY, 5, note="Possessive reference to Manfrin in the phrase about an aristocratic denigrator.", occurrence=0)
add_mention("cand-1512", "he", BODY, 5, note="Anaphoric reference in Haskell's report of accusations.", occurrence=0)
add_mention("cand-1512", "he", BODY, 5, note="Anaphoric reference in the reported 1769 grant.", occurrence=1)
add_mention("cand-10679", "granted a monopoly of the tobacco plantations", BODY, 5, note="The reported concession; Dalmatia is anchored separately.")
add_mention("cand-10678", "Dalmatia", BODY, 5, note="Region named for the tobacco plantations.")
add_mention("cand-1512", "he", BODY, 5, note="Anaphoric reference in Haskell's account of the reaction and fortune.", occurrence=2)
add_mention("cand-1512", "himself", BODY, 5, note="Reflexive anaphor to Manfrin.")
add_mention("cand-1512", "his", BODY, 5, note="Possessive reference in the reported willingness to take bribes.", occurrence=1)
add_mention("cand-1512", "his", BODY, 5, note="Possessive reference in the reported financial trickery.", occurrence=2)
add_mention("cand-10688", "being banished for fife", BODY, 5, note="Exact S0 anchor for the reported lifetime banishment; the page image confirms OCR 'fife' should read 'life'.")
add_mention("cand-10688", "this", BODY, 6, note="Resolves to the reported banishment, which Haskell says was revoked.")
add_mention("cand-2719", "Venice", BODY, 6, note="City from which Haskell says Manfrin was banished.", occurrence=0)
add_mention("cand-1512", "him", BODY, 6, note="Anaphoric reference to Manfrin's return in 1786.")
add_mention("cand-1512", "his", BODY, 6, note="Possessive reference in 'attempts on his life'.")
add_mention("cand-1512", "he", BODY, 6, note="Anaphoric reference in the 1787 purchase account.", occurrence=0)
add_mention("cand-10675", "palace", BODY, 6, note="Unidentified building; described by prior Venier-family ownership and Cannaregio location.")
add_mention("cand-10674", "family of Venier", BODY, 6, note="A family, not the separately indexed individual Leonardo Venier.")
add_mention("cand-10676", "Cannaregio", BODY, 6, note="District named as the palace location.")
add_mention("cand-10674", "their", BODY, 6, note="Possessive reference to the Venier family in 'their country house'.")
add_mention("cand-10677", "country house", BODY, 6, note="Unidentified property near Treviso.")
add_mention("cand-9209", "Treviso", BODY, 6, note="Nearby town named in the property locator.")
add_mention("cand-1512", "he", BODY, 6, note="Anaphoric reference to Manfrin's status as patron and collector.", occurrence=1)
add_mention("cand-1512", "himself", BODY, 6, note="Reflexive anaphor to Manfrin.")
add_mention("cand-2719", "Venice", BODY, 6, note="City in which Haskell says Manfrin became a leading patron and collector.", occurrence=1)

# Footnotes: preserve citation objects separately from the claims they support.
add_mention("cand-1512", "Manfrin", NOTES, 8, note="Person named in the bibliographic note.")
add_mention("cand-1512", "him", NOTES, 8, note="Anaphoric reference to Manfrin.")
add_mention("cand-1512", "his", NOTES, 8, note="Possessive reference to Manfrin's gallery.")
add_mention("cand-10680", "G. A. Meschini", NOTES, 8, note="Author given by initials and surname only.")
add_mention("cand-8262", "Biblioteca Correr", NOTES, 9, note="Repository named in Haskell's manuscript locator.")
add_mention("cand-2719", "Venice", NOTES, 9, note="City in the repository locator.")
add_mention("cand-10682", "Sonetti XVIossiano Satire contro il Manfrin, Impressane di Tabacchi", NOTES, 9, note="Manuscript title transcription and locator as supplied in S0; exact manuscript wording not checked.")
add_mention("cand-1512", "Manfrin", NOTES, 9, note="Nested person reference in the manuscript title.")
add_mention("cand-10683", "Risposta alla lettera apologetica impacciale per il Cittadino Gerolamo Manfrin", NOTES, 10, note="Pamphlet title anchor follows S0; page image corrects 'impacciale' to 'imparziale'.")
add_mention("cand-1512", "Manfrin", NOTES, 10, note="Person named in Haskell's assessment after the citation title.", occurrence=1)
add_mention("cand-9448", "Biblioteca Marciana", NOTES, 10, note="Repository named for the pamphlet shelfmark.")
add_mention("cand-2719", "Venezia", NOTES, 10, note="Italian city name in the pamphlet imprint.")
add_mention("cand-10172", "Archivio di Stato", NOTES, 11, note="Repository named in the archival locator.")
add_mention("cand-2719", "Venice", NOTES, 11, note="City in the repository locator.")
add_mention("cand-10464", "Inquisitori", NOTES, 11, note="Institutional series named in the archival citation.")
add_mention("cand-10684", "53 8, p. 43—29 Genaro 1770", NOTES, 11, note="Exact S0 span; page image reads register 538.")
add_mention("cand-10172", "ibid.", NOTES, 12, note="Anaphoric citation to the Archivio di Stato/Inquisitori locator in note 4.")
add_mention("cand-10685", "540, p. 6—12 Giugno 1786", NOTES, 12, note="Locator as transcribed; not independently consulted.")
add_mention("cand-10686", "Tassini", NOTES, 13, note="Surname-only author reference; identity with other Tassini candidates remains unresolved.")
add_mention("cand-10687", "Curiosità Veneziane, 4th edition 1887", NOTES, 13, note="Title and edition as given by Haskell; work not independently consulted.")

correction_intro = [
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 3, "ocr": "OR a full generation", "print": "For a full generation", "basis": "CHP-17.pdf physical page 1, printed folio i."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 4, "ocr": "Ffeeling", "print": "feeling", "basis": "CHP-17.pdf physical page 1, printed folio i."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 4, "ocr": "turned to' the past", "print": "turned to the past", "basis": "CHP-17.pdf physical page 1, printed folio i."},
]
correction_body = [
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 5, "ocr": "fife from", "print": "life from", "basis": "CHP-17.pdf physical page 1, printed folio i."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 6, "ocr": "life.6", "print": "life.5", "basis": "Page image shows printed footnote marker 5 for the 1786 arms permit."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 6, "ocr": "Treviso,8", "print": "Treviso,6", "basis": "Page image shows printed footnote marker 6 for the country-house locator."},
]
correction_note3 = [
    {"source_file": "02-sources/02-Markdown/17_CHP-17_intro.md", "source_line": 10, "ocr": "8 See, for instance", "print": "3 See, for instance", "basis": "CHP-17.pdf physical page 1, printed folio i."},
    {"source_file": "02-sources/02-Markdown/17_CHP-17_intro.md", "source_line": 10, "ocr": "impacciale", "print": "imparziale", "basis": "CHP-17.pdf physical page 1, printed folio i."},
]
correction_note4 = [{"source_file": "02-sources/02-Markdown/17_CHP-17_intro.md", "source_line": 11, "ocr": "53 8", "print": "538", "basis": "CHP-17.pdf physical page 1, printed folio i."}]
correction_note5 = [{"source_file": "02-sources/02-Markdown/17_CHP-17_intro.md", "source_line": 12, "ocr": "6 ibid.", "print": "5 ibid.", "basis": "CHP-17.pdf physical page 1, printed folio i."}]
correction_note6 = [{"source_file": "02-sources/02-Markdown/17_CHP-17_intro.md", "source_line": 13, "ocr": "8 Tassini", "print": "6 Tassini", "basis": "CHP-17.pdf physical page 1, printed folio i."}]


def quote_for(segment_id, start_line, end_line):
    return "\n".join(segment_lines[segment_id][number] for number in range(start_line, end_line + 1))


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, text_layer, qualification, mentioned_ids, quote=None, speaker="Haskell",
                   relation_candidate=False, **extra):
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": None, "printed_folio": "i", "pdf_physical_page": 1,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    qualifiers.update(extra)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote or quote_for(segment_id, start_line, end_line),
        "origin": "book", "source_file": segment_file[segment_id],
    })


segment_file = {
    TITLE: "02-sources/02-Markdown/17_CHP-17_intro.md",
    NOTES: "02-sources/02-Markdown/17_CHP-17_intro.md",
    BODY: "02-sources/02-Markdown/17_CHP-17_sec_i.md",
}

note1_ids = ["st-chp17-pi-note1-manfrin-material-status", "st-chp17-pi-note1-meschini-account"]
note2_ids = ["st-chp17-pi-note2-correr-manuscript-locator"]
note3_ids = ["st-chp17-pi-note3-pamphlet-locator", "st-chp17-pi-note3-unpopularity-assessment"]
note4_ids = ["st-chp17-pi-note4-1770-archive-locator"]
note5_ids = ["st-chp17-pi-note5-1786-archive-locator"]
note6_ids = ["st-chp17-pi-note6-tassini-locator"]


def body_note_link(marker, line_range, body_line_range, note_ids, note):
    return {
        "footnote_marker": marker, "footnote_segment": NOTES, "footnote_line_range": line_range,
        "footnote_text_pending": False, "footnote_body_link_status": "linked",
        "footnote_body_line_range": body_line_range, "footnote_note_statement_ids": note_ids,
        "footnote_link_note": note,
    }


link1 = body_note_link("1", "L8-L8", "L5-L5", note1_ids, "P.379 note 1 describes the state of Manfrin materials in Haskell's edition and cites Meschini's general account.")
link2 = body_note_link("2", "L9-L9", "L5-L5", note2_ids, "P.379 note 2 gives a Biblioteca Correr manuscript locator associated with the quoted aristocratic denunciation.")
link3 = body_note_link("3", "L10-L10", "L5-L5", note3_ids, "P.379 note 3 cites a 1797 pamphlet and frames Haskell's caution about the degree of alleged dishonesty.")
link4 = body_note_link("4", "L11-L11", "L5-L6", note4_ids, "P.379 note 4 supplies Haskell's 1770 Inquisitori archival locator for the reported banishment.")
link5 = body_note_link("5", "L12-L12", "L6-L6", note5_ids, "P.379 note 5 continues the Archivio di Stato locator for the 1786 permit.")
link6 = body_note_link("6", "L13-L13", "L6-L6", note6_ids, "P.379 note 6 cites Tassini for the country-house reference.")

# Introductory synthesis: keep the authorial generalizations distinct from biography.
make_statement(
    "st-chp17-pi-epoch-of-venetian-republic-ending", BODY, None, "cand-8838",
    "generation_before_republic_collapse_marked_by_general_sense_of_an_ending", 3, 4,
    "Haskell says that for a full generation before the Republic's collapse there was a widespread feeling that an epoch was drawing to a close.",
    "authorial synthesis", "A general atmosphere attributed to the period; no individual speaker or text is identified.",
    ["cand-8838", "cand-2719"], ocr_corrections=correction_intro,
)
make_statement(
    "st-chp17-pi-feeling-reached-patrons-and-collectors", BODY, None, "cand-4129",
    "sense_of_ending_reflected_in_speeches_literature_and_art_collecting", 4, 4,
    "Haskell says political speeches and literature repeatedly expressed this feeling, which eventually affected patrons and picture collectors.",
    "authorial synthesis", "The cited speeches and literature are not individually named; the passage does not define a bounded collector group.",
    ["cand-4129", "cand-2719"],
)
make_statement(
    "st-chp17-pi-men-turned-to-the-venetian-past", BODY, None, "cand-2719",
    "men_turning_to_the_past_to_preserve_memory_of_venices_independence", 4, 4,
    "Haskell says a number of men turned toward the past rather than the present or future, seemingly to give later generations an impression of Venice in its independent heyday.",
    "authorial synthesis", "The phrase 'as if anxious' marks Haskell's interpretation of their motive, not a directly documented statement of intent.",
    ["cand-2719", "cand-4129"], ocr_corrections=correction_intro,
)

# Manfrin: attributed characterization, biography, reported allegations, and actions.
make_statement(
    "st-chp17-pi-manfrin-caricature-of-old-order-opponent", BODY, "cand-1512", None,
    "described_as_caricature_of_a_type_that_depressed_conservative_supporters_of_old_order", 5, 5,
    "Haskell characterizes Manfrin as almost a caricature of a type of figure that had long depressed conservative supporters of an old order.",
    "authorial characterization", "An attributed social characterization, not an independently established reaction of every conservative supporter.",
    ["cand-1512"], **link1,
)
make_statement(
    "st-chp17-pi-manfrin-nouveau-riche-rise", BODY, "cand-1512", None,
    "nouveau_riche_businessman_rose_in_status_through_unscrupulous_energy_and_talent", 5, 5,
    "Haskell describes Manfrin as a nouveau-riche businessman who rose to high social position through what he calls unscrupulous Balzacian energy and talent.",
    "authorial characterization", "'Balzacian' is retained as Haskell's literary comparison; the source does not name a separate work or make a biographical claim about Balzac.",
    ["cand-1512"],
)
make_statement(
    "st-chp17-pi-manfrin-success-as-symbolic-trend", BODY, "cand-1512", None,
    "success_presented_as_symbolic_of_a_historical_trend", 5, 5,
    "Haskell says that Manfrin's success was symbolic of a broader historical trend in which self-made figures could make their mark despite social disdain for their achievements.",
    "authorial interpretation", "This is Haskell's generalization about historical periods and social values.",
    ["cand-1512"],
)
make_statement(
    "st-chp17-pi-manfrin-born-in-zara", BODY, "cand-1512", "cand-8160",
    "born_in_zara_to_a_humble_family", 5, 5,
    "Haskell says Manfrin was born in Zara to a humble family.",
    "authorial report", "The Italian phrase that follows is attributed to an aristocratic denigrator, not independent confirmation of the family's circumstances.",
    ["cand-1512", "cand-8160"], relation_candidate=True,
)
make_statement(
    "st-chp17-pi-manfrin-aristocratic-denigrator-phrase", BODY, "cand-1512", None,
    "described_by_an_aristocratic_denigrator_as_born_in_mud_and_dung", 5, 5,
    "Haskell attributes the phrase 'in mezzo al fango, e dalla Merda nato' to one of Manfrin's aristocratic denigrators.",
    "reported speech", "The speaker is unnamed and the phrase is a hostile social description, not a verified statement of parentage.",
    ["cand-1512"], speaker="unnamed aristocratic denigrator as reported by Haskell", **link2,
)
make_statement(
    "st-chp17-pi-manfrin-accused-of-businessman-vices", BODY, "cand-1512", None,
    "accused_of_characteristic_vices_of_a_successful_businessman", 5, 5,
    "Haskell says Manfrin was accused of being iracondo, incivil, avaro, ingrato, sospettoso, and infedel.",
    "reported accusation", "These are reported accusations and quoted labels; they are not adopted as verified character facts.",
    ["cand-1512"], **link2,
)
make_statement(
    "st-chp17-pi-manfrin-tobacco-monopoly-1769", BODY, "cand-1512", "cand-10679",
    "granted_1769_tobacco_plantation_monopoly_in_dalmatia", 5, 5,
    "Haskell reports that Manfrin was granted a monopoly over tobacco plantations in Dalmatia in 1769.",
    "authorial report", "The granting authority and terms are not named; the source's report is not independently checked here.",
    ["cand-1512", "cand-10679", "cand-10678"], relation_candidate=True,
)
make_statement(
    "st-chp17-pi-manfrin-unpopular-and-acquired-fortune", BODY, "cand-1512", None,
    "became_hated_in_dalmatia_and_soon_acquired_an_enormous_fortune", 5, 5,
    "Haskell says Manfrin made himself hated in Dalmatia and soon acquired an enormous fortune.",
    "authorial report", "The sentence attributes the reaction and financial outcome to Haskell's account without naming particular people or transactions.",
    ["cand-1512", "cand-10678"],
)
make_statement(
    "st-chp17-pi-manfrin-fortune-discreditable-means", BODY, "cand-1512", None,
    "fortune_acquired_in_part_by_somewhat_discreditable_means", 5, 5,
    "Haskell says much of Manfrin's fortune came through means he calls somewhat discreditable.",
    "authorial characterization", "The qualification 'somewhat' is retained; note 3 says the extent of actual dishonesty is unclear.",
    ["cand-1512", "cand-10683"], **link3,
)
make_statement(
    "st-chp17-pi-manfrin-banished-and-returned", BODY, "cand-1512", "cand-10688",
    "reported_lifetime_banishment_from_venice_later_revoked", 5, 6,
    "Haskell says Manfrin's willingness to take bribes and general financial trickery led to a lifetime banishment from Venice, which was later revoked.",
    "authorial report", "The source frames the cause as willingness and reported trickery; the archival citation is not independently consulted.",
    ["cand-1512", "cand-10688", "cand-2719"], relation_candidate=True,
    **link4, ocr_corrections=correction_body,
)
make_statement(
    "st-chp17-pi-manfrin-1786-arms-permit", BODY, "cand-1512", None,
    "returned_to_venice_in_1786_with_permit_to_carry_arms", 6, 6,
    "Haskell says Manfrin was back in Venice in 1786 with a special permit to carry arms to discourage possible attempts on his life.",
    "authorial report", "The source states the stated purpose of the permit; it does not identify an actual attack or assailant.",
    ["cand-1512", "cand-2719", "cand-10685"], relation_candidate=True,
    **link5, ocr_corrections=correction_body,
)
make_statement(
    "st-chp17-pi-manfrin-bought-venier-palace-1787", BODY, "cand-1512", "cand-10675",
    "bought_venier_family_palace_on_cannaregio_in_1787", 6, 6,
    "Haskell says Manfrin was in a position in 1787 to buy the palace of the ancient Venier family on Cannaregio.",
    "authorial report", "The palace is not formally named; the source does not identify the individual Venier owners.",
    ["cand-1512", "cand-10675", "cand-10674", "cand-10676"], relation_candidate=True,
)
make_statement(
    "st-chp17-pi-manfrin-bought-venier-country-house-1787", BODY, "cand-1512", "cand-10677",
    "bought_venier_family_country_house_near_treviso_in_1787", 6, 6,
    "Haskell says Manfrin also bought the Venier family's country house near Treviso in 1787.",
    "authorial report", "The house is unnamed; note 6 cites Tassini but that work was not consulted.",
    ["cand-1512", "cand-10677", "cand-10674", "cand-9209"], relation_candidate=True,
    **link6,
)
make_statement(
    "st-chp17-pi-manfrin-established-as-leading-venetian-patron", BODY, "cand-1512", "cand-2719",
    "by_1787_established_as_one_of_venices_most_important_patrons_and_collectors", 6, 6,
    "Haskell says that by then Manfrin had established himself as one of the most important patrons and collectors in Venice.",
    "authorial evaluation", "'One of the most important' is Haskell's assessment, not a measured ranking.",
    ["cand-1512", "cand-2719", "cand-4129"], relation_candidate=True,
)

# The six notes are statements about Haskell's citation trail, not independent source verification.
make_statement(
    note1_ids[0], NOTES, None, None, "most_available_manfrin_material_described_as_unpublished_in_haskell", 8, 8,
    "Haskell says most material available to him about Manfrin remained unpublished and would be referred to as needed.",
    "authorial source comment", "This describes Haskell's source situation, not the present publication status of Manfrin materials.",
    ["cand-1512"], quote=quote_for(NOTES, 8, 8),
)
make_statement(
    note1_ids[1], NOTES, "cand-10680", "cand-10681", "cited_as_only_general_account_of_manfrin_and_his_gallery", 8, 8,
    "Haskell identifies G. A. Meschini's 1806 volume II, page 107 as the only general account of Manfrin and his gallery.",
    "bibliographic locator", "The cited work and page were not independently consulted; the author's initials are not expanded.",
    ["cand-1512", "cand-10680", "cand-10681"], quote=quote_for(NOTES, 8, 8),
)
make_statement(
    note2_ids[0], NOTES, "cand-8262", "cand-10682", "manuscript_locator_for_sonetti_satire_against_manfrin", 9, 9,
    "Haskell locates satirical sonnets against Manfrin at Biblioteca Correr, Cod. Cicogna 2947/18.",
    "archival locator", "The manuscript was not consulted; the OCR title is retained as the surface anchor.",
    ["cand-8262", "cand-2719", "cand-10682", "cand-1512"], quote=quote_for(NOTES, 9, 9),
)
make_statement(
    note3_ids[0], NOTES, "cand-10683", "cand-9448", "pamphlet_cited_at_biblioteca_marciana_183_c_89_page_321", 10, 10,
    "Haskell cites a 1797 pamphlet against Gerolamo Manfrin at Biblioteca Marciana shelfmark 183.C.89, page 321.",
    "bibliographic locator", "The pamphlet and repository record were not consulted; the page image corrects 'impacciale' to 'imparziale' and OCR note marker 8 to printed note 3.",
    ["cand-10683", "cand-9448", "cand-2719", "cand-1512"], quote=quote_for(NOTES, 10, 10),
    ocr_corrections=correction_note3,
)
make_statement(
    note3_ids[1], NOTES, None, "cand-1512", "controversial_material_indicates_unpopularity_but_dishonesty_extent_unclear", 10, 10,
    "Haskell infers from this pamphlet and similar controversial material that Manfrin made himself highly unpopular, while saying the extent of actual dishonesty is unclear.",
    "authorial inference", "This is Haskell's inference from cited material; it does not establish that Manfrin committed fraud.",
    ["cand-1512", "cand-10683", "cand-9448"], quote=quote_for(NOTES, 10, 10),
    ocr_corrections=correction_note3,
)
make_statement(
    note4_ids[0], NOTES, "cand-10172", "cand-10684", "archival_locator_for_29_january_1770_inquisitori_record", 11, 11,
    "Haskell cites Archivio di Stato, Venice, Inquisitori register 538, page 43, dated 29 Genaro 1770.",
    "archival locator", "The archive record was not consulted; the page image confirms register 538, and the source spelling 'Genaro' is retained.",
    ["cand-10172", "cand-2719", "cand-10464", "cand-10684"], quote=quote_for(NOTES, 11, 11),
    ocr_corrections=correction_note4,
)
make_statement(
    note5_ids[0], NOTES, "cand-10172", "cand-10685", "archival_locator_for_12_june_1786_inquisitori_record", 12, 12,
    "Haskell's 'ibid.' cites Archivio di Stato, Venice, Inquisitori register 540, page 6, dated 12 Giugno 1786.",
    "archival locator", "The record was not consulted; page image confirms printed note marker 5 rather than S0's 6.",
    ["cand-10172", "cand-2719", "cand-10464", "cand-10685"], quote=quote_for(NOTES, 12, 12),
    ocr_corrections=correction_note5,
)
make_statement(
    note6_ids[0], NOTES, "cand-10686", "cand-10687", "cited_tassini_curiosita_veneziane_fourth_edition_1887", 13, 13,
    "Haskell cites Tassini's fourth edition of Curiosità Veneziane from 1887.",
    "bibliographic locator", "The work was not consulted; S0 reads note marker 8 while the page image shows printed note 6.",
    ["cand-10686", "cand-10687"], quote=quote_for(NOTES, 13, 13),
    ocr_corrections=correction_note6,
)

# The page heading and generated filenames are handled as structural context, not knowledge objects.
coverage_by_id[INTRO_GENERATED].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
    "note": "Generated Markdown filename heading only; not printed book content.",
})
coverage_by_id[BODY_GENERATED].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
    "note": "Generated Markdown filename heading only; not printed book content.",
})
coverage_by_id[TITLE].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L4-5",
    "note": "no_semantic_content: Printed chapter number and title were checked against physical page 1 (folio i); '[Page 2]' is an OCR page marker and is not treated as the printed folio.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L8-13",
    "note": "P.379 footnotes 1-6 were checked against physical page 1 and linked to the body; OCR note markers 8/6/8 were corrected in S2 to printed 3/5/6.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L3-6",
    "note": "First printed folio i is semantically migrated; the final clause 'Indeed, within five years,' continues in the next body segment and remains pending.",
})

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp17-pi-")]
if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidate_specs),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "coverage": {INTRO_GENERATED: "excluded", TITLE: "complete", NOTES: "complete", BODY_GENERATED: "excluded", BODY: "partial"},
        "partial_continuation": BODY_NEXT,
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
    "partial_continuation": BODY_NEXT,
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
}, ensure_ascii=False))
