"""Controlled S2 migration for printed p.371 and its notes 1-2."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l61-67"
BODY = "chp-15:15_CHP-15_sec_ii:l69-83"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l85-88"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
BACKUP_SUFFIX = ".bak-s2-chp15-p371-querini-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.371 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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
    raise SystemExit("chapter 15 sec_ii source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required_source = [
    (70, "Altar dedicated to"), (71, "his soul was"), (72, "these vices were depicted"),
    (74, "Grand Duke of Tuscany"), (74, "monument, crowned with a sphinx"),
    (76, "digne et malheureux"), (76, "Hercules by Algardi"), (76, "young Canova"),
    (76, "Egyptian figures"), (77, "Dominique De Non"), (78, "Zanetti"),
    (79, "portrait of Voltaire"), (80, "Voyage Pittoresque"),
    (80, "amico suavissimo"), (83, "Paolo Renier"), (83, "campaign"),
    (111, "Isidoro Bianchi"), (111, "Francesco Milizia"), (111, "Jacopo Morelli"),
    (112, "G. A. Moschini, 1924"), (112, "Mostra degli Incisori Veneti del Settecento"),
]
for line_number, required in required_source:
    if required.casefold() not in source_lines[line_number - 1].casefold():
        raise SystemExit(f"required source text changed at L{line_number}: {required}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, BODY_NEXT, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (
    coverage_by_id[BODY_PREV]["migration_status"] != "complete"
    or coverage_by_id[BODY]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
    or coverage_by_id[NOTES]["migration_status"] != "partial"
    or coverage_by_id[NOTES]["source_line_ranges"] != "L91-110"
):
    raise SystemExit("S2 coverage preconditions changed")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.371 body rows already exist")
if any(row.get("statement_id", "").startswith("st-chp15-p371-") for row in statements):
    raise SystemExit("p.371 statements already exist")

new_candidates = [
    ("cand-10569", "Altar dedicated to Ignorance, Envy, and Calumny at Alticchiero", "work", 70,
     "Haskell describes the altar and the personified vices; object details beyond the relief are not supplied."),
    ("cand-10570", "Bas-relief of Ignorance, Envy, and Calumny based on Apelles' composition", "work", 72,
     "Haskell links the relief to Apelles' famous composition as recorded by Pliny; no surviving object or copy history is identified."),
    ("cand-10571", "Pliny (named as the recorder of Apelles' composition)", "person", 73,
     "Named only by surname in the source; identity is deferred to S3."),
    ("cand-10572", "Querini's reportedly pagan or Manichean outlook as characterized by Mme Rosenberg", "term", 71,
     "A reported characterization in Mme Rosenberg's account, not an independently established statement of Querini's beliefs."),
    ("cand-10573", "Grand Duke of Tuscany's visit to Alticchiero", "event", 74,
     "Haskell reports the visit and a monument erected to record the occasion; the Grand Duke is not named in this passage."),
    ("cand-10574", "Monument at Alticchiero commemorating the Grand Duke's visit, with sphinx, inscription, and Apollo bas-relief", "work", 74,
     "Haskell describes its components and allegory; no date, inscription text, or surviving location is given."),
    ("cand-10575", "Unidentified quality and type of Querini's sculpture collection (Haskell's stated evidential limit)", "term", 76,
     "A methodological limitation stated by Haskell; it does not classify the collection itself."),
    ("cand-10576", "Hercules sculpture by Alessandro Algardi in Querini's collection", "work", 76,
     "Haskell names the subject and maker but gives no title, date, or current location."),
    ("cand-10577", "Unidentified sculpture by the young Antonio Canova in Querini's collection", "work", 76,
     "Haskell gives no subject, date, or current location."),
    ("cand-10578", "Ancient Etruscan phallic symbols owned by Querini", "work", 76,
     "A group of ancient objects described by Haskell; no count, catalogue, or present location is supplied."),
    ("cand-10579", "Egyptian figures owned by Querini", "work", 76,
     "Haskell says the group was large but gives no count, object identities, or current location."),
    ("cand-10580", "Zanetti prints bought by Dominique De Non, including Rembrandt prints", "work", 78,
     "Haskell gives a broad collecting claim; individual prints and transaction details are not identified."),
    ("cand-10581", "Ferney (site of De Non's reported Voltaire portrait engraving)", "place", 79,
     "Named as the place where De Non engraved a portrait of Voltaire; exact site is not identified."),
    ("cand-10582", "Portrait of Voltaire engraved by Dominique De Non at Ferney", "work", 79,
     "Haskell reports the engraving but gives no title, date, or surviving impression."),
    ("cand-10583", "Abbé de Saint-Non, Voyage Pittoresque de la Grèce et de la Sicile", "archive", 80,
     "Haskell says De Non worked on this publication in Naples; edition and precise contribution are not specified here."),
    ("cand-10584", "Portrait signed 'amico suavissimo' drawn by Dominique De Non (sitter reference unresolved)", "work", 80,
     "Haskell reports the portrait and inscription; no present location or date is supplied."),
    ("cand-10585", "Portrait of Mme Rosenberg drawn by Dominique De Non", "work", 81,
     "Haskell reports the portrait among her friends; no title, date, or present location is supplied."),
    ("cand-10586", "Bust of Paolo Renier commissioned by Querini from Canova", "work", 83,
     "The sentence continues beyond p.371; campaign context and completion details remain pending p.372."),
    ("cand-10587", "G. A. Moschini, 1924 (citation in Haskell's De Non note; title unspecified)", "archive", 112,
     "Citation trail only; title, edition, and cited passage have not been independently checked."),
    ("cand-10588", "Mostra degli Incisori Veneti del Settecento (1941), p.112", "archive", 112,
     "Citation trail only; the exhibition publication has not been independently consulted."),
    ("cand-10589", "Francesco Milizia (named in p.371 note 1)", "person", 111,
     "Named as one of several antiquarians/neoclassicists who dedicated books or monographs to Querini; identity resolution is deferred to S3."),
    ("cand-10590", "Jacopo Morelli (named in p.371 note 1)", "person", 111,
     "Named as one of several antiquarians/neoclassicists who dedicated books or monographs to Querini; identity resolution is deferred to S3."),
    ("cand-10591", "Napoleon (named in Haskell's description of De Non's later museum office)", "person", 77,
     "Named only in the context of De Non's later office; the identity is not resolved here."),
    ("cand-10592", "Ignorance (personified vice named in the Alticchiero altar programme)", "term", 71,
     "Named as a personified vice in Haskell's description; no individual allegorical figure is identified."),
    ("cand-10593", "Envy (personified vice named in the Alticchiero altar programme)", "term", 71,
     "Named as a personified vice in Haskell's description; no individual allegorical figure is identified."),
    ("cand-10594", "Calumny (personified vice named in the Alticchiero altar programme)", "term", 71,
     "Named as a personified vice in Haskell's description; no individual allegorical figure is identified."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{source_line}" if source_line < 90 else f"{NOTES}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(69, 84)},
    NOTES: {number: source_lines[number - 1] for number in range(90, 114)},
}
segment_offsets = {}
for segment_id, lines in segment_lines.items():
    offset = 0
    segment_offsets[segment_id] = {}
    for number, line in lines.items():
        segment_offsets[segment_id][number] = offset
        offset += len(line) + 1

planned_mentions = []
mention_counter = 1


def add_mention(candidate_id, surface, segment_id, source_line, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[segment_id][source_line]
    line_offset = segment_offsets[segment_id][source_line]
    occupied = [
        (int(row["start_char"]), int(row["end_char"]))
        for row in mentions + planned_mentions
        if row["segment_id"] == segment_id
        and line_offset <= int(row["start_char"]) < line_offset + len(line)
    ]
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            raise SystemExit(f"surface not found on {segment_id} L{source_line}: {surface!r}")
        start = line_offset + pos
        end = start + len(surface)
        if not any(start < old_end and old_start < end for old_start, old_end in occupied):
            break
        search_from = pos + 1
    mention_id = f"m-chp15-p371-querini-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


def quote(segment_id, line_start, line_end):
    if line_start > line_end or line_start not in segment_lines[segment_id] or line_end not in segment_lines[segment_id]:
        raise SystemExit(f"quote span outside {segment_id}: L{line_start}-L{line_end}")
    return "\n".join(segment_lines[segment_id][n] for n in range(line_start, line_end + 1))


def add_statement(statement_id, subject, obj, predicate, segment_id, line_start, line_end, claim,
                  speaker="Haskell", text_layer="authorial report", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 371 if segment_id == BODY else 371,
        "pdf_physical_page": 11,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(segment_id, line_start, line_end),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


def footnote_fields(marker, line_start, line_end, body_line, note_statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{line_start}-L{line_end}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(note_statement_ids), "footnote_link_note": "",
    }


# Body mentions. Exact OCR anchors are kept; print corrections are logged below, not written to S0.
add_mention("cand-2075", "Querini’s", BODY, 70)
add_mention("cand-10569", "Altar dedicated to", BODY, 70)
add_mention("cand-10592", "Ignorance", BODY, 71)
add_mention("cand-10593", "Envy", BODY, 71)
add_mention("cand-10594", "Calumny", BODY, 71)
add_mention("cand-2824", "Mme Rosenberg", BODY, 71)
add_mention("cand-10572", "Manichean", BODY, 71)
add_mention("cand-10570", "bas-relief", BODY, 72)
add_mention("cand-9945", "Apelles", BODY, 73)
add_mention("cand-10571", "Pliny", BODY, 73)
add_mention("cand-4302", "Grand Duke of Tuscany", BODY, 74)
add_mention("cand-2075", "Querini", BODY, 74)
add_mention("cand-10573", "the occasion", BODY, 74)
add_mention("cand-10574", "a monument", BODY, 74)
add_mention("cand-10575", "allegory", BODY, 74)
add_mention("cand-2824", "Mme Rosenberg", BODY, 74)
add_mention("cand-10575", "allegories", BODY, 74)
add_mention("cand-2075", "Querini’s", BODY, 75)
add_mention("cand-10575", "sculpture", BODY, 76)
add_mention("cand-2824", "Mme Rosenberg’s book", BODY, 76)
add_mention("cand-2816", "Winckelmann", BODY, 76)
add_mention("cand-10576", "Hercules", BODY, 76)
add_mention("cand-0034", "Algardi", BODY, 76)
add_mention("cand-0532", "Canova", BODY, 76)
add_mention("cand-10577", "sculpture by the young", BODY, 76)
add_mention("cand-10578", "ancient Etruscan phallic symbols", BODY, 76)
add_mention("cand-10579", "Egyptian figures", BODY, 76)
add_mention("cand-1752", "Dominique De Non", BODY, 77)
add_mention("cand-1752", "Dominique Vivant-Denon", BODY, 77)
add_mention("cand-10591", "Napoleon", BODY, 77)
add_mention("cand-2719", "Venice", BODY, 77)
add_mention("cand-10580", "Zanetti’s prints", BODY, 78)
add_mention("cand-10580", "the Rembrandts", BODY, 78)
add_mention("cand-1756", "Francesco Novelli", BODY, 78)
add_mention("cand-10581", "Ferney", BODY, 79)
add_mention("cand-10582", "portrait of", BODY, 79)
add_mention("cand-2791", "Voltaire", BODY, 79)
add_mention("cand-2341", "Abbé de Saint-Non", BODY, 80)
add_mention("cand-10583", "Voyage Pittoresque de la Grèce et de la Sicile", BODY, 80)
add_mention("cand-10584", "his portrait", BODY, 80, "The possessive sitter referent is ambiguous in the sentence; the signed portrait is not definitively identified with Querini.")
add_mention("cand-2824", "Mme Rosenberg", BODY, 81)
add_mention("cand-2075", "Querini’s", BODY, 82)
add_mention("cand-2133", "Paolo Renier", BODY, 83)
add_mention("cand-0532", "Canova", BODY, 83)
add_mention("cand-10586", "a bust", BODY, 83)

# Footnote mentions.
add_mention("cand-0372", "Isidoro Bianchi", NOTES, 111)
add_mention("cand-10589", "Francesco Milizia", NOTES, 111)
add_mention("cand-10590", "Jacopo Morelli", NOTES, 111)
add_mention("cand-2075", "him", NOTES, 111, "Pronoun refers to Querini in the linked p.371 note.")
add_mention("cand-10451", "de Tipaldo", NOTES, 112)
add_mention("cand-1709", "G. A. Moschini", NOTES, 112)
add_mention("cand-10319", "Pallucchini", NOTES, 112)
add_mention("cand-10588", "Mostra degli Incisori Veneti del Settecento", NOTES, 112)

N1 = "st-chp15-p371-note1-antiquarians-dedicated-books-to-querini"
N2 = "st-chp15-p371-note2-de-non-citation-chain"
FN1 = footnote_fields(1, 111, 111, 76, [N1])
FN2 = footnote_fields(2, 112, 112, 77, [N2])
FN1["footnote_note_statement_ids"] = [
    N1, "st-chp15-p371-note1-bianchi-dedication", "st-chp15-p371-note1-milizia-dedication",
    "st-chp15-p371-note1-morelli-dedication",
]

# Statements preserve attribution, uncertainty, and the p.372 continuation.
add_statement(
    "st-chp15-p371-querini-alter-spirits-and-mme-characterization", "cand-2075", "cand-10572",
    "mme_rosenberg_characterized_querini_as_somewhat_pagan_or_manichean", BODY, 70, 71,
    "Haskell reports Mme Rosenberg's view that Querini's soul was somewhat pagan or at least Manichean and that he believed one should sacrifice to evil as well as good spirits to hope for happiness.",
    speaker="Mme Rosenberg, quoted by Haskell", text_layer="reported account",
    qualification="This is a characterization attributed to Rosenberg, not an independently established statement of Querini's religious beliefs.",
    mentioned=["cand-2075", "cand-2824", "cand-10572"],
)
add_statement(
    "st-chp15-p371-vices-depicted-after-apelles-pliny", "cand-10569", "cand-10570",
    "vices_depicted_in_bas_relief_based_on_apelles_composition_recorded_by_pliny", BODY, 72, 73,
    "Haskell says Ignorance, Envy, and Calumny were shown in a bas-relief based on a famous composition by Apelles as recorded by Pliny.",
    qualification="Neither the ancient composition nor the Alticchiero relief is independently identified or examined here.",
    mentioned=["cand-10569", "cand-10570", "cand-10592", "cand-10593", "cand-10594", "cand-9945", "cand-10571"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-grand-duke-visit-and-monument", "cand-2075", "cand-4302",
    "grand_duke_of_tuscany_visited_villa_and_querini_erected_monument", BODY, 74, 74,
    "Haskell says the villa drew considerable attention; a Grand Duke of Tuscany visited, and Querini erected a monument to mark the occasion.",
    qualification="The Grand Duke is not named; the monument's date is not given.",
    mentioned=["cand-2075", "cand-4302", "cand-10573", "cand-10574"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-grand-duke-monument-sphinx-apollo-relief", "cand-10574", "cand-4302",
    "monument_crowned_with_sphinx_and_carried_flattering_inscription_and_apollo_bas_relief", BODY, 74, 74,
    "Haskell describes the monument as crowned by a sphinx, bearing a flattering inscription, and including a bas-relief allegorizing the reforming prince as Apollo.",
    qualification="The inscription text and monument's survival are not supplied.", mentioned=["cand-10574", "cand-4302"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-mme-rosenberg-distrust-of-allegory", "cand-2824", None,
    "mme_rosenberg_found_painted_ceilings_hard_to_understand_and_sculptural_allegory_easier", BODY, 74, 74,
    "Haskell says Mme Rosenberg distrusted allegory and found painted ceilings difficult to understand, while sculpture made allegory easier because it used fewer figures.",
    qualification="This is Haskell's summary of her view, not a direct quotation in this sentence.", mentioned=["cand-2824"],
)
add_statement(
    "st-chp15-p371-querini-garden-allegories-straightforward", "cand-2075", "cand-2081",
    "haskell_says_querini_garden_allegories_were_straightforward", BODY, 74, 75,
    "Haskell says that above all Mme Rosenberg found Querini's garden allegories absolutely straightforward.",
    qualification="Explicitly retain as the author's evaluation.", mentioned=["cand-2075", "cand-2081"],
)
LIMIT = "st-chp15-p371-sculpture-collection-assessment-limit"
add_statement(
    LIMIT, "cand-2075", "cand-10575", "haskell_cannot_assess_quality_or_type_of_querini_sculpture_collection", BODY, 76, 76,
    "Haskell says the illustrations in Mme Rosenberg's book do not make it possible to assess the quality or even type of Querini's sculpture collection.",
    qualification="This is an explicit source limitation and should constrain later claims about the collection.",
    mentioned=["cand-2075", "cand-2824", "cand-10575"],
)
WINCKELMANN = "st-chp15-p371-querini-antique-taste-winckelmann"
add_statement(
    WINCKELMANN, "cand-2075", "cand-2816", "haskell_attributes_querini_antique_taste_to_winckelmann_and_restraint", BODY, 76, 76,
    "Haskell says Querini's taste for antiquity was inspired by Winckelmann and that Querini saw restraint and lack of excess as its main character.",
    qualification="The interpretation is Haskell's; the note cites further antiquarian contacts and dedications.",
    mentioned=["cand-2075", "cand-2816"],
)
add_statement(
    "st-chp15-p371-querini-algardi-hercules", "cand-2075", "cand-10576",
    "collection_included_hercules_by_algardi", BODY, 76, 76,
    "Haskell says Querini's more modern sculpture included a Hercules by Algardi.",
    qualification="No title, date, or location is supplied.", mentioned=["cand-2075", "cand-10576", "cand-0034"],
)
add_statement(
    "st-chp15-p371-querini-young-canova-sculpture", "cand-2075", "cand-10577",
    "collection_included_sculpture_by_young_canova", BODY, 76, 76,
    "Haskell says Querini's more modern sculpture included work by the young Canova.",
    qualification="No subject, title, date, or location is supplied.", mentioned=["cand-2075", "cand-10577", "cand-0532"],
)
add_statement(
    "st-chp15-p371-querini-etruacan-and-egyptian-objects", "cand-2075", "cand-10578",
    "owned_ancient_etruscan_phallic_symbols_and_many_egyptian_figures", BODY, 76, 76,
    "Haskell says Querini owned ancient Etruscan phallic symbols and a large number of Egyptian figures; Mme Rosenberg had difficulty explaining the former.",
    qualification="The source gives no inventory or count; 'large number' remains qualitative.",
    mentioned=["cand-2075", "cand-10578", "cand-10579", "cand-2824"],
)
add_statement(
    "st-chp15-p371-de-non-close-contact-and-venice-period", "cand-2075", "cand-1752",
    "de_non_was_querini_only_close_artist_contact_and_lived_in_venice_about_five_years", BODY, 77, 77,
    "Haskell calls Dominique De Non the only artist, apart from sculptors, with whom Querini had close contacts and says De Non settled in Venice for about five years in the early 1790s.",
    qualification="The phrase 'about five years' and the decade are preserved as approximate source claims.",
    mentioned=["cand-2075", "cand-1752", "cand-2719"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-de-non-later-director-of-napoleon-museums", "cand-1752", "cand-1701",
    "later_became_napoleon_celebrated_director_of_museums", BODY, 77, 77,
    "Haskell says De Non later became Napoleon's celebrated director of museums.",
    qualification="The office and wording are reported by Haskell and are not independently verified in this stage.",
    mentioned=["cand-1752", "cand-10591"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-de-non-engraver-and-collector", "cand-1752", None,
    "described_as_busy_controversial_but_admired_engraver_and_collector", BODY, 77, 77,
    "Haskell describes De Non as a controversial but highly admired engraver and as a collector.",
    qualification="The characterization is Haskell's summary.", mentioned=["cand-1752"],
)
add_statement(
    "st-chp15-p371-de-non-bought-zanetti-rembrandt-prints", "cand-1752", "cand-10580",
    "bought_large_proportion_zanetti_prints_including_rembrandts", BODY, 78, 78,
    "Haskell says De Non bought a large proportion of Zanetti's prints, including the Rembrandts.",
    qualification="No count, transaction record, or individual Rembrandt prints are identified.",
    mentioned=["cand-1752", "cand-10580"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-rembrandt-prints-influenced-de-non-and-novelli", "cand-10580", "cand-1752",
    "rembrandt_prints_influenced_de_non_and_his_pupil_francesco_novelli", BODY, 78, 78,
    "Haskell says the Rembrandt prints profoundly affected De Non's style and that of his principal pupil Francesco Novelli.",
    qualification="This is Haskell's account of artistic influence; it is not independently assessed here.",
    mentioned=["cand-10580", "cand-1752", "cand-1756"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-de-non-voltaire-engraving-ferney", "cand-1752", "cand-10582",
    "engraved_voltaire_portrait_at_ferney", BODY, 79, 79,
    "Haskell says De Non engraved a portrait of Voltaire at Ferney.",
    qualification="No date, title, or surviving impression is specified.", mentioned=["cand-1752", "cand-10581", "cand-10582", "cand-2791"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-de-non-saint-non-travel-book-work", "cand-1752", "cand-10583",
    "worked_on_saint_non_voyage_pittoresque_in_naples", BODY, 80, 80,
    "Haskell says De Non worked in Naples on the Abbé de Saint-Non's Voyage Pittoresque de la Grèce et de la Sicile.",
    qualification="The precise nature and extent of De Non's contribution are not specified.",
    mentioned=["cand-1752", "cand-2341", "cand-10583"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-de-non-appealed-to-querini", "cand-1752", "cand-2075",
    "political_and_antiquarian_interests_made_de_non_well_qualified_to_appeal_to_querini", BODY, 80, 80,
    "Haskell says De Non's political and antiquarian interests made him well qualified to appeal to Querini.",
    qualification="This is Haskell's explanatory judgment, not a direct statement by Querini.",
    mentioned=["cand-1752", "cand-2075"],
)
add_statement(
    "st-chp15-p371-de-non-in-querini-circle-and-signed-portrait", "cand-1752", "cand-10584",
    "moved_in_querini_circle_and_drew_portrait_signed_amico_suavissimo", BODY, 80, 80,
    "Haskell says De Non moved in Querini's circle and drew a portrait signed 'amico suavissimo'.",
    qualification="The sitter of 'his portrait' is grammatically ambiguous in the source and is not identified here; the portrait's location and date are also not given.",
    mentioned=["cand-1752", "cand-2075", "cand-10584"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-de-non-drew-mme-rosenberg-portrait", "cand-1752", "cand-10585",
    "also_drew_mme_rosenberg_portrait_among_her_friends", BODY, 81, 81,
    "Haskell says De Non also drew Mme Rosenberg's portrait among her friends.",
    qualification="The source gives no date, title, or present location.",
    mentioned=["cand-1752", "cand-2824", "cand-10585"], relation_candidate=True,
)
add_statement(
    "st-chp15-p371-literary-inspiration-and-renaissance-art-life", "cand-2075", None,
    "literary_inspiration_shaped_querini_collecting_and_patronage_in_renaissance_spirit", BODY, 82, 83,
    "Haskell says literary inspiration in Querini's collecting and patronage encouraged him to live with art in a spirit largely absent since the early Renaissance.",
    qualification="This is Haskell's interpretive synthesis. OCR reads 'five with'; p.371 print reads 'live with'.",
    mentioned=["cand-2075"],
)
add_statement(
    "st-chp15-p371-querini-renier-canova-bust-commission-partial", "cand-2075", "cand-10586",
    "commissioned_canova_bust_of_paolo_renier_after_campaign_partial", BODY, 83, 83,
    "Haskell says Querini had been closely associated with the potential reformer Paolo Renier and commissioned Canova to make a bust of him after a successful, though exceedingly corrupt, campaign.",
    qualification="The sentence continues on p.372; the campaign, bust's completion, and further context remain pending.",
    mentioned=["cand-2075", "cand-2133", "cand-0532", "cand-10586"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT], cross_reference_text="P.371 L83 ends with 'campaign'; continue at p.372.", cross_reference_text_pending=True,
    relation_candidate=True,
)

link = {
    "st-chp15-p371-querini-antique-taste-winckelmann": FN1,
    LIMIT: FN1,
    "st-chp15-p371-de-non-close-contact-and-venice-period": FN2,
    "st-chp15-p371-de-non-later-director-of-napoleon-museums": FN2,
}
for statement_id, fields in link.items():
    statement_by_id[statement_id]["qualifiers"].update(fields)

add_statement(
    N1, None, None, "note_names_antiquarians_who_dedicated_books_or_monographs_to_querini", NOTES, 111, 111,
    "Haskell's note names Isidoro Bianchi, Francesco Milizia, and Jacopo Morelli as antiquarians and neo-classicists who dedicated books or monographs to Querini.",
    speaker="Haskell's note", text_layer="citation and relation report",
    qualification="The individual books or monographs are not named in this note and the claim has not been independently checked.",
    mentioned=["cand-0372", "cand-10589", "cand-10590", "cand-2075"], **FN1,
)
for sid, person in [
    ("st-chp15-p371-note1-bianchi-dedication", "cand-0372"),
    ("st-chp15-p371-note1-milizia-dedication", "cand-10589"),
    ("st-chp15-p371-note1-morelli-dedication", "cand-10590"),
]:
    add_statement(
        sid, person, "cand-2075", "note_reports_dedication_of_unspecified_book_or_monograph_to_querini", NOTES, 111, 111,
        f"Haskell's note says {candidate_by_id[person]['canonical_name']} dedicated a book or monograph to Querini.",
        speaker="Haskell's note", text_layer="relation report",
        qualification="The title, date, and specific item are not identified in the note.",
        mentioned=[person, "cand-2075"], relation_candidate=True, **FN1,
    )
add_statement(
    N2, "cand-1752", "cand-10587", "note_gives_citation_chain_for_de_non", NOTES, 112, 112,
    "Haskell's note directs readers to De Tipaldo for the relationship with De Non, and cites G. A. Moschini (1924) and Pallucchini's Mostra degli Incisori Veneti del Settecento (1941), page 112, for De Non.",
    speaker="Haskell's note", text_layer="bibliographic citation chain",
    qualification="The cited works were not independently consulted; OCR errors in this note are checked below against the print.",
    mentioned=["cand-1752", "cand-10451", "cand-1709", "cand-10587", "cand-10319", "cand-10588"],
    cited_source_independently_consulted=False, **FN2,
)

ocr_corrections = [
    {"source_file": SOURCE_FILE, "source_line": 74, "ocr": "above ail", "print": "above all", "basis": "CHP-15.pdf physical page 11."},
    {"source_file": SOURCE_FILE, "source_line": 77, "ocr": "contacts'was", "print": "contacts was", "basis": "CHP-15.pdf physical page 11."},
    {"source_file": SOURCE_FILE, "source_line": 80, "ocr": "he.was", "print": "he was", "basis": "CHP-15.pdf physical page 11."},
    {"source_file": SOURCE_FILE, "source_line": 83, "ocr": "five with", "print": "live with", "basis": "CHP-15.pdf physical page 11."},
]
correction_targets = {
    "st-chp15-p371-querini-garden-allegories-straightforward": [ocr_corrections[0]],
    "st-chp15-p371-de-non-close-contact-and-venice-period": [ocr_corrections[1]],
    "st-chp15-p371-de-non-saint-non-travel-book-work": [ocr_corrections[2]],
    "st-chp15-p371-literary-inspiration-and-renaissance-art-life": [ocr_corrections[3]],
}
for statement_id, corrections in correction_targets.items():
    statement_by_id[statement_id]["qualifiers"]["ocr_corrections"] = corrections

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L62-67",
    "note": "Printed p.370 checked against CHP-15.pdf physical p.10; p.369 cross-page sentence closed at L62. Notes 1-2 at consolidated L109-110 are migrated.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L70-83",
    "note": "Printed p.371 checked against CHP-15.pdf physical p.11. Processes the altar of Ignorance/Envy/Calumny, Grand Duke visit monument, Mme Rosenberg's allegory account, Querini's sculpture and collection, De Non's work and contacts, and Paolo Renier/Canova bust commission. The final sentence stops at 'campaign' and continues at p.372. Notes 1-2 at consolidated L111-112 are migrated. Print corrections are recorded in S2 only; S0 is unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L91-112",
    "note": "P.365 notes 1-2 at L91-92, p.367 notes 1-4 at L93-96, p.368 notes 1-7 at L97-104, p.369 notes 1-4 at L105-108, p.370 notes 1-2 at L109-110, and p.371 notes 1-2 at L111-112 are migrated. Remaining note L113 belongs to p.372 and remains pending.",
})

new_statement_ids = [row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p371-")]
result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA, "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 371, "pdf_physical_page": 11,
    "open_cross_page_statement": "st-chp15-p371-querini-renier-canova-bust-commission-partial",
}
if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + planned_mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
