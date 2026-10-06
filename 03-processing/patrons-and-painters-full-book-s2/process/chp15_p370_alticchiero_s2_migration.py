"""Controlled S2 migration for printed p.370 and its notes 1-2."""
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
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l49-59"
BODY = "chp-15:15_CHP-15_sec_ii:l61-67"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l69-83"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
CITY_PLANS = "st-chp15-p369-alticchiero-european-city-plans-partial"
BACKUP_SUFFIX = ".bak-s2-chp15-p370-alticchiero-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.370 S2 migration")
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
    (59, "plans of the great European cities"), (62, "bathroom is lined with prints by Piranesi"),
    (62, "engravings by Picart"), (62, "a bust of Bacon"), (62, "Daphnis and Chloe"),
    (63, "garden was even more important than the house"), (63, "Young’s Wood"),
    (64, "Altar of Friendship"), (64, "busts of Epicurus"), (65, "Girolamo Ascanio Giustiniani"),
    (65, "Mme Rosenberg herself"), (66, "Fortune and Apollo"), (67, "cabane de la folie"),
    (67, "Montaigne’s dictum"), (67, "head of Voltaire"),
    (109, "inventory of Angelo Querini’s effects at Alticchiero"), (110, "G. A. Moschini"),
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
    coverage_by_id[BODY_PREV]["migration_status"] != "partial"
    or coverage_by_id[BODY]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
    or coverage_by_id[NOTES]["migration_status"] != "partial"
    or coverage_by_id[NOTES]["source_line_ranges"] != "L91-108"
):
    raise SystemExit("S2 coverage preconditions changed")
if CITY_PLANS not in statement_by_id or statement_by_id[CITY_PLANS]["qualifiers"].get("predicate_status") != "partial":
    raise SystemExit("expected p.369 city-plan continuation is not partial")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.370 body rows already exist")
if any(row.get("statement_id", "").startswith("st-chp15-p370-") for row in statements):
    raise SystemExit("p.370 statements already exist")

new_candidates = [
    ("cand-10545", "Piranesi prints displayed in the bathroom at Alticchiero", "work", 62,
     "Haskell reports the prints as part of the villa's decoration; no individual prints or present location are identified."),
    ("cand-10546", "Bernard Picart engravings of oriental customs displayed at Alticchiero", "work", 62,
     "The passage quotes a French caption-like description; individual print titles and editions are not supplied."),
    ("cand-10547", "Library at Alticchiero with classics and books on agriculture, philosophy, and theology", "archive", 62,
     "Haskell describes the contents at a high level; collection extent and surviving records are not identified."),
    ("cand-10548", "Bacon bust described as the 'idol of the temple' at Alticchiero", "work", 62,
     "Haskell reports a bust of Francis Bacon in the villa library; object identity and present location are not supplied."),
    ("cand-10549", "Daphnis and Chloe illustrations in Querini's study, drawn by the Regent and engraved by Audran", "work", 62,
     "A specific print group is described, but no edition, dates, or surviving impressions are identified."),
    ("cand-10550", "Young's Wood in the Alticchiero garden", "place", 63,
     "Named garden area whose trees framed columns and burial urns; precise layout is known only through Haskell's description."),
    ("cand-10551", "Edward Young, Night Thoughts", "archive", 63,
     "Named as the poem that had caught the romantic imagination of Europe; edition and exact citation are not supplied."),
    ("cand-10552", "Columns and burial urns arranged in Young's Wood", "work", 63,
     "The group is described as artfully casual garden scenery; individual objects are not identified."),
    ("cand-10553", "Philosopher's way of life as an allegory in Querini's garden", "term", 64,
     "An interpretive concept attributed to Haskell's account of the garden design."),
    ("cand-10554", "Shrines and antique or modern sculpture distributed through the Alticchiero garden", "work", 64,
     "A collective decorative programme described by Haskell; individual works are recorded separately where named."),
    ("cand-10555", "Altar of Friendship in the Alticchiero garden", "work", 64,
     "Haskell describes colossal busts of Epicurus and Phocion associated with this altar."),
    ("cand-10556", "Phocion (named in the account of the Altar of Friendship)", "person", 64,
     "The passage identifies him as Querini's particular hero; historical identity is deferred to S3."),
    ("cand-10557", "Colossal busts of Epicurus and Phocion at the Altar of Friendship", "work", 64,
     "Haskell reports the paired busts and their French epithets; no maker, date, or current location is supplied."),
    ("cand-10558", "Inscription below the Altar of Friendship dedicated to Girolamo Ascanio Giustiniani", "work", 65,
     "The inscription's wording is not transcribed; its dedicatee is named by Haskell."),
    ("cand-10559", "Tranquillity and Country Life as ideals represented by other Alticchiero altars", "term", 65,
     "Named ideals in Haskell's description; their exact iconographic objects are not individually identified."),
    ("cand-10560", "Apollo sculpture at Alticchiero, rendered in youthful repose", "work", 66,
     "The passage associates a modern sculpture of Apollo with a living sculptor but supplies no name or date."),
    ("cand-10561", "Unidentified modern sculptor described as still living in Haskell's account", "person", 66,
     "The sculptor's identity is not supplied; the candidate records only the reported role."),
    ("cand-10562", "Cabane de la folie, thatched hut in Querini's garden", "place", 67,
     "Haskell names and describes the structure; its exact location within the garden is not given."),
    ("cand-10563", "Montaigne's maxim inscribed at the cabane de la folie", "archive", 67,
     "The French dictum is transcribed by Haskell; edition and textual source are not cited here."),
    ("cand-10564", "Antique bust inside the cabane de la folie resembling an old woman", "work", 67,
     "Haskell reports an antique bust and a resemblance; no attribution or present location is supplied."),
    ("cand-10565", "Unidentified old woman remembered as roaming the streets of Venice", "person", 67,
     "She appears only as a reported resemblance for the antique bust; no name or independent source is given."),
    ("cand-10566", "Jean Huber engraving of Voltaire's head from multiple angles", "work", 67,
     "One of the engravings in the cabane de la folie; no title, date, or present location is supplied."),
    ("cand-10567", "Unclassified inventory of Angelo Querini's effects at Alticchiero, published by C. A. Levi, vol. II, p.255", "archive", 109,
     "Haskell cites the inventory through Levi; neither the inventory nor cited publication has been independently consulted."),
    ("cand-10568", "G. A. Moschini, 1806, vol. II, p.116 (citation locator)", "archive", 110,
     "Bibliographic locator in Haskell's note; the cited work and page have not been independently consulted."),
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
    BODY: {number: source_lines[number - 1] for number in range(61, 68)},
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
    mention_id = f"m-chp15-p370-alticchiero-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


def quote(segment_id, line_start, line_end):
    if line_start > line_end or line_start not in segment_lines[segment_id] or line_end not in segment_lines[segment_id]:
        raise SystemExit(f"quote span outside {segment_id}: L{line_start}-{line_end}")
    return "\n".join(segment_lines[segment_id][n] for n in range(line_start, line_end + 1))


def add_statement(statement_id, subject, obj, predicate, segment_id, line_start, line_end, claim,
                  speaker="Haskell", text_layer="authorial report", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 370, "pdf_physical_page": 10,
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


def footnote_fields(marker, line_start, line_end, body_line, linked_statement_ids, note=""):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{line_start}-L{line_end}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(linked_statement_ids), "footnote_link_note": note,
    }


# Close p.369's final city-plan sentence with the p.370 bathroom continuation.
city = statement_by_id[CITY_PLANS]
city["predicate"] = "alticchiero_rooms_had_city_plans_and_bathroom_piranesi_prints"
city["qualifiers"]["predicate_status"] = "complete"
city["qualifiers"]["claim"] = "Haskell says the rooms displayed plans of major European cities and that the bathroom was lined with Piranesi prints."
city["qualifiers"]["qualification"] = "The cross-page sentence is now closed at p.370 L62; no titles or present locations for the plans or prints are supplied."
city["qualifiers"]["cross_reference_text"] = "P.369 L59 'while the' continues at p.370 L62 'bathroom is lined with prints by Piranesi.'"
city["qualifiers"]["cross_reference_text_pending"] = False
city["qualifiers"]["mentioned_candidate_ids"] = ["cand-0086", "cand-10542", "cand-10545", "cand-1938"]

# Body mentions: preserve explicit source-language text and avoid overlapping spans.
add_mention("cand-1938", "Piranesi", BODY, 62)
add_mention("cand-10546", "engravings", BODY, 62)
add_mention("cand-1925", "Picart", BODY, 62)
add_mention("cand-10547", "library", BODY, 62)
add_mention("cand-0155", "Bacon", BODY, 62)
add_mention("cand-8107", "Enlightenment", BODY, 62)
add_mention("cand-1411", "Lodoli", BODY, 62)
add_mention("cand-2075", "Querini", BODY, 62)
add_mention("cand-10549", "series of prints", BODY, 62, "A print group described by purpose and subject; title and edition are not supplied.")
add_mention("cand-0901", "Daphnis and Chloe", BODY, 62)
add_mention("cand-1786", "Philippe d", BODY, 62, "OCR preserves the given name and start of surname; print reads Philippe d'Orléans, Regent.")
add_mention("cand-0145", "Audran", BODY, 62)
add_mention("cand-2081", "garden", BODY, 63)
add_mention("cand-2075", "Querini", BODY, 63)
add_mention("cand-2827", "Young’s", BODY, 63)
add_mention("cand-10550", "Wood", BODY, 63)
add_mention("cand-10551", "Night Thoughts", BODY, 63)
add_mention("cand-3462", "Europe", BODY, 63)
add_mention("cand-10552", "columns and burial urns", BODY, 63)
add_mention("cand-10553", "complete allegory", BODY, 64)
add_mention("cand-10554", "shrines", BODY, 64)
add_mention("cand-10555", "Altar of Friendship", BODY, 64)
add_mention("cand-0977", "Epicurus", BODY, 64)
add_mention("cand-10556", "Phocion", BODY, 64)
add_mention("cand-2075", "Querini’s", BODY, 65)
add_mention("cand-10558", "inscription", BODY, 65)
add_mention("cand-1198", "Girolamo Ascanio Giustiniani", BODY, 65)
add_mention("cand-10529", "Switzerland", BODY, 65)
add_mention("cand-2824", "Mme Rosenberg", BODY, 65)
add_mention("cand-10559", "Tranquillity", BODY, 65)
add_mention("cand-10559", "Country Life", BODY, 65)
add_mention("cand-10560", "Apollo", BODY, 66)
add_mention("cand-10561", "a modern and still living sculptor", BODY, 66)
add_mention("cand-10562", "cabane de la folie", BODY, 67)
add_mention("cand-1689", "Montaigne", BODY, 67)
add_mention("cand-10563", "dictum", BODY, 67)
add_mention("cand-10564", "an antique bust", BODY, 67)
add_mention("cand-10565", "old mad woman", BODY, 67)
add_mention("cand-2719", "Venice", BODY, 67)
add_mention("cand-2824", "Mme Rosenberg", BODY, 67)
add_mention("cand-1306", "Huber", BODY, 67)
add_mention("cand-2791", "Voltaire", BODY, 67)

# Page notes 1-2.
add_mention("cand-2075", "Angelo Querini’s", NOTES, 109)
add_mention("cand-0086", "Alticchiero", NOTES, 109)
add_mention("cand-8532", "Levi", NOTES, 109)
add_mention("cand-10567", "inventory", NOTES, 109)
add_mention("cand-1709", "G. A. Moschini", NOTES, 110)
add_mention("cand-10568", "1806, H, p. 116", NOTES, 110, "OCR reads H; p.370 print reads II, p.116.")

N1 = "st-chp15-p370-note1-querini-alticchiero-inventory"
N2 = "st-chp15-p370-note2-moschini-citation"
FN1 = footnote_fields(1, 109, 109, 62, [N1], "The inventory citation bears on the Alticchiero collection and material culture." )
FN2 = footnote_fields(2, 110, 110, 65, [N2])

def link_footnote(statement_id, fields):
    statement_by_id[statement_id]["qualifiers"].update(fields)

# Page-body statements.
add_statement(
    "st-chp15-p370-alticchiero-piranesi-bathroom-prints", "cand-0086", "cand-10545",
    "bathroom_lined_with_piranesi_prints", BODY, 62, 62,
    "Haskell says the bathroom was lined with prints by Piranesi.",
    qualification="No print titles, editions, or current locations are supplied.",
    mentioned=["cand-0086", "cand-10545", "cand-1938"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-alticchiero-decoration-combined-with-utility", "cand-0086", None,
    "decoration_combined_with_utility_throughout_villa", BODY, 62, 62,
    "Haskell says that throughout Alticchiero decoration was combined with utility.",
    qualification="This is the author's summary of the villa's design, not a general architectural rule.", mentioned=["cand-0086"],
)
add_statement(
    "st-chp15-p370-alticchiero-picart-oriental-engraving", "cand-0086", "cand-10546",
    "walls_lined_with_picart_oriental_customs_engravings", BODY, 62, 62,
    "Haskell says other walls were lined with Picart engravings of oriental customs, accompanied by a French description of how they amused passers-by and prompted reflection on the folly of purported sages.",
    qualification="The French wording is retained from the source and not independently checked against the print series.",
    mentioned=["cand-0086", "cand-10546", "cand-1925"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-alticchiero-library-contents", "cand-0086", "cand-10547",
    "library_contained_classics_and_books_on_agriculture_philosophy_theology", BODY, 62, 62,
    "Haskell says the library contained the great classics and a large collection of books on agriculture, philosophy, and even theology.",
    qualification="The subjects are listed by Haskell; no catalogue or book count is supplied.", mentioned=["cand-0086", "cand-10547"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-bacon-bust-at-alticchiero", "cand-0086", "cand-10548",
    "library_bust_of_bacon_called_idol_of_the_temple", BODY, 62, 62,
    "Haskell calls a bust of Bacon the 'idol of the temple' in the library.",
    qualification="The phrase is Haskell's metaphor; it is not a documented title for the bust.", mentioned=["cand-0086", "cand-10548", "cand-0155"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-bacon-as-enlightenment-and-lodoli-hero", "cand-0155", "cand-1411",
    "haskell_describes_bacon_as_enlightenment_founder_and_lodoli_hero", BODY, 62, 62,
    "Haskell describes Bacon as a founding father of the Enlightenment and as Lodoli's particular hero.",
    qualification="These are Haskell's historical and intellectual characterizations.", mentioned=["cand-0155", "cand-8107", "cand-1411"],
)
add_statement(
    "st-chp15-p370-querini-study-daphnis-chloe-print-series", "cand-2075", "cand-10549",
    "study_contained_daphnis_chloe_illustrations_drawn_by_regent_and_engraved_by_audran", BODY, 62, 62,
    "Haskell says Querini's study contained prints intended to lighten his overburdened mind: illustrations to Daphnis and Chloe drawn by Philippe d'Orléans, the Regent, and engraved by Audran.",
    qualification="The passage does not identify the edition or surviving impressions; artist and engraver attribution is reported as printed.",
    mentioned=["cand-2075", "cand-10549", "cand-0901", "cand-1786", "cand-0145"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-querini-garden-as-expression-of-taste", "cand-2075", "cand-2081",
    "garden_more_important_than_house_as_expression_of_querini_taste", BODY, 63, 63,
    "Haskell says the garden mattered even more than the house as an expression of Querini's taste.",
    qualification="This comparative judgment is attributed to Haskell.", mentioned=["cand-2075", "cand-2081"],
)
add_statement(
    "st-chp15-p370-alticchiero-garden-formal-and-agreeable-confusion", "cand-2081", None,
    "regular_outline_combined_with_agreeable_confusion_of_plants", BODY, 63, 63,
    "Haskell describes the garden's main outlines as severely regular, with an 'agreeable confusion' of bushes and plants within that framework.",
    qualification="The quoted phrase is Haskell's aesthetic description.", mentioned=["cand-2081"],
)
add_statement(
    "st-chp15-p370-youngs-wood-landscape-arrangement", "cand-2081", "cand-10550",
    "wild_area_named_youngs_wood_with_artfully_arranged_trees_columns_and_urns", BODY, 63, 63,
    "Haskell describes a wild area called Young's Wood, with cunningly sited trees framing columns and burial urns arranged with artful casualness.",
    qualification="The passage gives no exact plan or inventory for this garden area.",
    mentioned=["cand-2081", "cand-10550", "cand-10552"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-youngs-night-thoughts-romantic-influence", "cand-10551", "cand-10550",
    "night_thoughts_named_as_inspiration_for_youngs_wood", BODY, 63, 63,
    "Haskell says Young's Wood was named in honour of the poet whose Night Thoughts had caught Europe's romantic imagination.",
    qualification="This records Haskell's stated naming explanation, not a direct statement by Querini.",
    mentioned=["cand-2827", "cand-10551", "cand-10550", "cand-3462"],
)
add_statement(
    "st-chp15-p370-garden-allegory-philosophers-way-of-life", "cand-2081", "cand-10553",
    "garden_designed_as_allegory_of_philosophers_way_of_life", BODY, 64, 64,
    "Haskell describes the main garden as a complete allegory of the philosopher's way of life, with ideals expressed through shrines and selected sculpture.",
    qualification="The allegorical interpretation is Haskell's account.", mentioned=["cand-2081", "cand-10553", "cand-10554"],
)
add_statement(
    "st-chp15-p370-friendship-altar-epicurus-phocion-busts", "cand-10555", "cand-10557",
    "altar_of_friendship_associated_with_epicurus_and_phocion_busts", BODY, 64, 64,
    "Haskell says the Altar of Friendship had colossal busts of Epicurus and Phocion, glossed respectively as 'the philosopher of wise pleasure' and 'the citizen philosopher'.",
    speaker="Haskell, quoting French epithets", text_layer="authorial report with quoted labels",
    qualification="The French phrases and their punctuation are not independently checked against an external edition.",
    mentioned=["cand-10555", "cand-10557", "cand-0977", "cand-10556"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-phocion-described-as-querini-hero", "cand-2075", "cand-10556",
    "phocion_described_as_querini_particular_hero", BODY, 65, 65,
    "Haskell describes Phocion as the man who dared to stand against the ignorant mob and says he was Querini's particular hero.",
    qualification="The characterization and historical framing belong to Haskell's account.",
    mentioned=["cand-2075", "cand-10556"],
)
add_statement(
    "st-chp15-p370-querini-aristocratic-cast-and-1761-downfall", "cand-2075", None,
    "haskell_reads_phocion_choice_as_aristocratic_and_says_populace_rejoiced_at_1761_downfall", BODY, 65, 65,
    "Haskell says the choice showed Querini's aristocratic cast of mind and that the populace had long recognized his proposed reforms would do them no good and rejoiced at his downfall in 1761.",
    qualification="This is Haskell's social and political interpretation of the passage, not an independently verified account of popular opinion.",
    mentioned=["cand-2075", "cand-10556"],
)
add_statement(
    "st-chp15-p370-altar-inscription-dedicated-to-giustiniani", "cand-10555", "cand-10558",
    "inscription_below_altar_dedicated_to_girolamo_ascanio_giustiniani", BODY, 65, 65,
    "Haskell says an inscription below the Altar of Friendship was dedicated to Querini's closest friend, Girolamo Ascanio Giustiniani.",
    qualification="The inscription text is not given; the relationship is reported by Haskell.",
    mentioned=["cand-10555", "cand-10558", "cand-1198"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-other-altars-friendships-and-ideals", "cand-2081", None,
    "other_altars_celebrated_friendships_and_named_ideals", BODY, 65, 66,
    "Haskell says other altars, made from genuine antique sculpture or modern imitations, celebrated other friendships—including friendships formed in Switzerland and, after her death in 1791, Mme Rosenberg—and ideals including Tranquillity, Country Life, Fortune, and Apollo.",
    qualification="The syntax does not identify every friendship or map each ideal to a specific altar; keep the grouping unresolved.",
    mentioned=["cand-2081", "cand-10529", "cand-2824", "cand-10559", "cand-10560"],
)
APOLLO = "st-chp15-p370-apollo-sculpture-by-unidentified-living-artist"
add_statement(
    APOLLO, "cand-10560", "cand-10561", "apollo_rendered_in_youthful_repose_by_modern_living_sculptor", BODY, 66, 66,
    "Haskell quotes a description of Apollo rendered in noble repose and youthful beauty by a modern sculptor who was still living at the time of writing.",
    qualification="The sculptor is not named; the wording is Haskell's quoted description.",
    mentioned=["cand-10560", "cand-10561"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-cabane-de-la-folie-and-montaigne-inscription", "cand-10562", "cand-10563",
    "thatched_hut_displayed_montaigne_dictum_about_wisdom_and_folly", BODY, 67, 67,
    "Haskell describes the cabane de la folie as a thatched hut bearing Montaigne's dictum that only a half turn separates the greatest wisdom from folly.",
    qualification="The original French wording is retained in the source quote; the underlying text edition is not cited.",
    mentioned=["cand-10562", "cand-1689", "cand-10563"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-antique-bust-resembling-venetian-woman", "cand-10562", "cand-10564",
    "hut_contained_antique_bust_resembling_unidentified_old_venetian_woman", BODY, 67, 67,
    "Haskell says an antique bust inside the hut resembled an old mad woman who used to roam Venice's streets.",
    qualification="Both the woman's identity and the bust's attribution remain unknown in this account.",
    mentioned=["cand-10562", "cand-10564", "cand-10565", "cand-2719"], relation_candidate=True,
)
add_statement(
    "st-chp15-p370-wynne-reflection-on-madness-and-prophets", "cand-2824", "cand-10565",
    "sight_of_bust_prompted_wynne_reflection_on_eastern_veneration_of_mad_and_prophets", BODY, 67, 67,
    "Haskell says the bust's resemblance led Mme Rosenberg to reflect on veneration of the mad in the East and their proverbial relationship with prophets and poets.",
    qualification="This is Haskell's report of Wynne's thought; 'the East' is broad and undefined in the passage.",
    mentioned=["cand-2824", "cand-10564", "cand-10565"],
)
add_statement(
    "st-chp15-p370-huber-voltaire-angle-engraving", "cand-10562", "cand-10566",
    "hut_walls_displayed_huber_voltaire_head_engraving_from_multiple_angles", BODY, 67, 67,
    "Haskell says engravings were displayed on the hut's walls to make the point, including one by Huber showing Voltaire's head from multiple angles.",
    qualification="No title, date, or surviving print is identified.",
    mentioned=["cand-10562", "cand-10566", "cand-1306", "cand-2791"], relation_candidate=True,
)

link_footnote("st-chp15-p370-querini-study-daphnis-chloe-print-series", FN1)
link_footnote("st-chp15-p370-altar-inscription-dedicated-to-giustiniani", FN2)
link_footnote("st-chp15-p370-other-altars-friendships-and-ideals", FN2)

add_statement(
    N1, "cand-2075", "cand-10567", "note_cites_querini_effects_inventory_published_by_levi", NOTES, 109, 109,
    "Haskell cites a very unclassified inventory of Angelo Querini's effects at Alticchiero, published by Levi, volume II, page 255.",
    speaker="Haskell's note", text_layer="bibliographic citation and source trail",
    qualification="The inventory and Levi's cited publication were not independently consulted.",
    mentioned=["cand-2075", "cand-0086", "cand-8532", "cand-10567"], cited_source_independently_consulted=False,
    **FN1,
)
add_statement(
    N2, None, "cand-10568", "note_cites_moschini_1806_volume_ii_page_116", NOTES, 110, 110,
    "Haskell cites G. A. Moschini, 1806, volume II, page 116.",
    speaker="Haskell's note", text_layer="bibliographic citation",
    qualification="The print reads II; OCR reads H. The cited work and page were not independently consulted.",
    mentioned=["cand-1709", "cand-10568"], cited_source_independently_consulted=False,
    **FN2,
)

ocr_corrections = [
    {"source_file": SOURCE_FILE, "source_line": 62, "ocr": "R��gent Philippe d��Orl��ans", "print": "Régent Philippe d’Orléans", "basis": "CHP-15.pdf physical page 10."},
    {"source_file": SOURCE_FILE, "source_line": 63, "ocr": "wildarea", "print": "wild area", "basis": "CHP-15.pdf physical page 10."},
    {"source_file": SOURCE_FILE, "source_line": 65, "ocr": 'who "was Querini', "print": "who was Querini", "basis": "CHP-15.pdf physical page 10."},
    {"source_file": SOURCE_FILE, "source_line": 67, "ocr": "Montaigne's", "print": "Montaigne’s", "basis": "CHP-15.pdf physical page 10."},
    {"source_file": SOURCE_FILE, "source_line": 110, "ocr": "1806, H, p. 116", "print": "1806, II, p. 116", "basis": "CHP-15.pdf physical page 10."},
]
corrections_by_statement = {
    "st-chp15-p370-querini-study-daphnis-chloe-print-series": [ocr_corrections[0]],
    "st-chp15-p370-youngs-wood-landscape-arrangement": [ocr_corrections[1]],
    "st-chp15-p370-phocion-described-as-querini-hero": [ocr_corrections[2]],
    "st-chp15-p370-querini-aristocratic-cast-and-1761-downfall": [ocr_corrections[2]],
    "st-chp15-p370-cabane-de-la-folie-and-montaigne-inscription": [ocr_corrections[3]],
    N2: [ocr_corrections[4]],
}
for statement_id, corrections in corrections_by_statement.items():
    statement_by_id[statement_id]["qualifiers"]["ocr_corrections"] = corrections

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L50-59",
    "note": "Printed p.369 checked against CHP-15.pdf physical p.9; the final city-plan sentence closes at p.370 L62 with the bathroom's Piranesi prints.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L62-67",
    "note": "Printed p.370 checked against CHP-15.pdf physical p.10. Processes the villa's prints, library and Bacon bust; Querini's garden and Young's Wood; philosophical altars, sculpture, Montaigne's folly hut, the antique bust and Huber's Voltaire engraving. Notes 1-2 at consolidated L109-110 are migrated. Print corrections are recorded in S2 only; S0 is unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L91-110",
    "note": "P.365 notes 1-2 at L91-92, p.367 notes 1-4 at L93-96, p.368 notes 1-7 at L97-104, p.369 notes 1-4 at L105-108, and p.370 notes 1-2 at L109-110 are migrated. Remaining notes L111-113 belong to later pages and remain pending.",
})

new_statement_ids = [row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p370-")]
result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA, "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids), "updated_statements": [CITY_PLANS],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 370, "pdf_physical_page": 10,
    "open_cross_page_statement": None,
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
