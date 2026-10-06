"""Controlled S2 migration for printed p.359; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY_PREV = "chp-14:14_CHP-14_intro:l118-124"
BODY = "chp-14:14_CHP-14_intro:l126-137"
BODY_NEXT = "chp-14:14_CHP-14_intro:l139-146"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-chp14-p359-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.359 S2 migration")
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
        temp_path = Path(handle.name)
    temp_path.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (127, "his favourite Tiepolo to insert figures into their backgrounds"),
    (128, "a landscape ‘derived from Titian’ and a boat and white horse"),
    (129, "commissions to Tiepolo were now mainly confmed"),
    (131, "compelled to go to Spain"),
    (132, "with Tesi and his wife he established extremely intimate relations"),
    (133, "collected works"),
    (135, "a number of theoretical works"),
    (137, "the two styles that were just beginning to clash in a"),
    (214, "Baudi di Vesme, 1912, pp. 309-29"),
    (215, "Opéré, VIII, p. 101"),
    (216, "Annamaria Gabbrielli, 1938 and 1939"),
    (217, "Annamaria Gabbrielli, 1938 and 1939"),
]:
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")

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
    or coverage_by_id[NOTES]["source_line_ranges"] != "L169-213"
):
    raise SystemExit("S2 coverage preconditions changed")
previous_statement_id = "st-chp14-p358-limits-of-picturesque-invention-partial"
if previous_statement_id not in statement_by_id:
    raise SystemExit("missing open p.358 cross-page statement")
if not statement_by_id[previous_statement_id]["predicate"].endswith("_partial"):
    raise SystemExit("p.358 continuation was already revised")

new_candidates = [
    ("cand-10397", "Tiepolo’s figures inserted into architectural-painting backgrounds (p.359)", "work", BODY, 127,
     "A descriptive group of figures Giambattista Tiepolo was asked to insert into backgrounds in architectural paintings by other artists; individual paintings and dates are not identified."),
    ("cand-10398", "Tiepolo’s landscape, boat, and white horse added to a Pesci architectural setting (p.359)", "work", BODY, 128,
     "Haskell reports that Tiepolo added a Titian-derived landscape and a boat and white horse described as worthy of Wouwermans to Prospero Pesci’s dry architectural setting; no title or present location is supplied."),
    ("cand-10399", "Tiepolo’s small-scale copies after Veronese (p.359)", "work", BODY, 129,
     "A descriptive group of copies after Paolo Veronese listed among Algarotti’s later small-scale commissions to Tiepolo; no titles or count are given."),
    ("cand-10400", "Mauro Tesi’s copies of works admired by Algarotti in central Italy (p.359)", "work", BODY, 132,
     "An unidentified group of copies Tesi made while travelling through central Italy with Algarotti; the admired source works are not named."),
    ("cand-10401", "Landscapes by Dietrich copied by Mauro Tesi (p.359)", "work", BODY, 132,
     "A group of unidentified landscapes by the source-named Dietrich that Algarotti employed Tesi to copy; no titles, dates, or attribution details are supplied."),
    ("cand-10402", "Vignettes engraved by Mauro Tesi for Algarotti’s planned collected works (p.359)", "work", BODY, 132,
     "A group of vignettes Tesi was employed to engrave for an edition Algarotti was preparing; the individual designs and publication status are not specified here."),
    ("cand-10403", "Algarotti’s edition of his collected works in preparation (p.359)", "archive", BODY, 132,
     "An edition of Algarotti’s collected works that Haskell says he was preparing; keep distinct from the later seventeen-volume edition described by candidate cand-10229 until S3/source review resolves the relationship."),
    ("cand-10404", "Algarotti’s theoretical works on the arts (p.359)", "archive", BODY, 135,
     "An unidentified plurality of theoretical works in which Algarotti tried to formulate views on the arts; this descriptive candidate does not assign titles or editions."),
    ("cand-10405", "Dietrich (source form, p.359)", "person", BODY, 132,
     "Only the surname Dietrich is supplied for the painter whose landscapes Tesi copied; do not equate automatically with the index candidate cand-0920 before S3."),
    ("cand-10406", "Mauro Tesi’s unnamed wife (p.359)", "person", BODY, 132,
     "An unnamed person identified only as Mauro Tesi’s wife; preserve the source’s wording and do not infer her identity or the nature of Algarotti’s relationship with her."),
    ("cand-10407", "Unnamed daughter of Mauro Tesi and his wife (p.359)", "person", BODY, 132,
     "An unnamed daughter described as belonging to Tesi and his wife; Algarotti is reported to have been her godfather. No personal identity is supplied."),
    ("cand-10408", "Unnamed room in Pisa where Algarotti lay dying (p.359)", "place", BODY, 133,
     "The room in Pisa that Tesi was summoned to decorate in 1764, where Algarotti lay dying; the building and room are not identified."),
    ("cand-10409", "Spain as the destination of Tiepolo’s compelled departure (p.359)", "place", BODY, 131,
     "Haskell says Tiepolo was compelled to go to Spain; the passage does not identify a city, employer, or exact travel date."),
    ("cand-10410", "Baudi di Vesme, 1912, pages 309–329 (citation in p.359 n.1)", "archive", NOTES, 214,
     "Citation locator supplied in Haskell’s note 1; the cited work and pages were not independently consulted."),
    ("cand-10411", "Opere, volume VIII, page 101 (citation in p.359 n.2)", "archive", NOTES, 215,
     "Citation locator supplied in Haskell’s note 2; the volume and cited page were not independently consulted."),
    ("cand-10412", "Annamaria Gabbrielli (author cited in p.359 notes 3–4)", "person", NOTES, 216,
     "Author named in two identical general-reference notes; identity is retained in the source form and not externally aligned here."),
    ("cand-10413", "Gabbrielli, 1938 (citation in p.359 notes 3–4)", "archive", NOTES, 216,
     "Unidentified Gabbrielli publication dated 1938, cited for a general discussion; title, edition, and pages are not supplied in these notes."),
    ("cand-10414", "Gabbrielli, 1939 (citation in p.359 notes 3–4)", "archive", NOTES, 216,
     "Unidentified Gabbrielli publication dated 1939, cited for a general discussion; title, edition, and pages are not supplied in these notes."),
]
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10396:
    raise SystemExit("candidate sequence changed; expected max cand-10396")
for cid, name, suggested_type, segment_id, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment_id}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_bounds = {BODY: (126, 137), NOTES: (168, 220)}
segment_texts = {sid: "\n".join(source_lines[first - 1:last]) for sid, (first, last) in segment_bounds.items()}
planned_mentions = []
mention_counter = 1


def add_mention(segment_id, candidate_id, surface, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    text = segment_texts[segment_id]
    occupied = [(int(r["start_char"]), int(r["end_char"])) for r in mentions + planned_mentions if r["segment_id"] == segment_id]
    start = 0
    while True:
        pos = text.find(surface, start)
        if pos < 0:
            original = text.find(surface)
            collisions = [r for r in mentions + planned_mentions if r["segment_id"] == segment_id
                          and int(r["start_char"]) < original + len(surface)
                          and original < int(r["end_char"])]
            raise SystemExit(f"surface not found in {segment_id}: {surface!r}; overlaps={collisions}")
        end = pos + len(surface)
        if not any(pos < old_end and old_start < end for old_start, old_end in occupied):
            break
        start = pos + 1
    mention_id = f"m-chp14-p359-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(pos), "end_char": str(end), "note": note,
    })
    mention_counter += 1


# Explicit names, source-relative referents, and descriptive works in the p.359 body.
add_mention(BODY, "cand-2569", "Tiepolo")
add_mention(BODY, "cand-0052", "Algarotti")
add_mention(BODY, "cand-10397", "figures")
add_mention(BODY, "cand-2569", "the great Venetian artist", "Appositional reference to Tiepolo.")
add_mention(BODY, "cand-10398", "a landscape")
add_mention(BODY, "cand-2630", "Titian")
add_mention(BODY, "cand-10398", "a boat and white horse")
add_mention(BODY, "cand-2820", "Wouwermans")
add_mention(BODY, "cand-1887", "Pesci")
add_mention(BODY, "cand-0054", "Algarotti’s commissions")
add_mention(BODY, "cand-2569", "Tiepolo")
add_mention(BODY, "cand-10397", "figures to be added in architectural paintings")
add_mention(BODY, "cand-10399", "copies after")
add_mention(BODY, "cand-2755", "Veronese")
add_mention(BODY, "cand-0054", "He", "Pronoun referring to Algarotti.")
add_mention(BODY, "cand-2569", "Tiepolo")
add_mention(BODY, "cand-10409", "Spain")
add_mention(BODY, "cand-0054", "Algarotti’s requests")
add_mention(BODY, "cand-0050", "Algarotti himself")
add_mention(BODY, "cand-2551", "Mauro Tesi")
add_mention(BODY, "cand-2551", "Tesi")
add_mention(BODY, "cand-10406", "his wife")
add_mention(BODY, "cand-10407", "their daughter")
add_mention(BODY, "cand-7392", "central Italy")
add_mention(BODY, "cand-10400", "the works he especially admired")
add_mention(BODY, "cand-10405", "Dietrich")
add_mention(BODY, "cand-10401", "landscapes")
add_mention(BODY, "cand-10402", "vignettes")
add_mention(BODY, "cand-10403", "the edition")
add_mention(BODY, "cand-2551", "Tesi")
add_mention(BODY, "cand-10408", "the very room")
add_mention(BODY, "cand-5628", "Pisa")
add_mention(BODY, "cand-0050", "Algarotti")
add_mention(BODY, "cand-10404", "theoretical works")
add_mention(BODY, "cand-0079", "his views on the arts")
add_mention(BODY, "cand-6439", "neo-classicism")
add_mention(BODY, "cand-0079", "Algarotti")
add_mention(BODY, "cand-0079", "Algarotti")
add_mention(BODY, "cand-0059", "Algarotti")
add_mention(BODY, "cand-0076", "the picturesque")

# Printed notes 1-4 at L214-217; note 4's body marker occurs on p.360 and is linked there.
add_mention(NOTES, "cand-3419", "Baudi di Vesme")
add_mention(NOTES, "cand-10410", "1912, pp. 309-29")
add_mention(NOTES, "cand-10411", "Opéré, VIII, p. 101", "Print reads Opere; record correction in S2 without changing S0.")
add_mention(NOTES, "cand-10412", "Annamaria Gabbrielli")
add_mention(NOTES, "cand-10413", "1938")
add_mention(NOTES, "cand-10414", "1939")
add_mention(NOTES, "cand-10412", "Annamaria Gabbrielli")
add_mention(NOTES, "cand-10413", "1938")
add_mention(NOTES, "cand-10414", "1939")

unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")


def quote(segment_id, line_start, line_end):
    return "\n".join(source_lines[line_start - 1:line_end])


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 359 if segment_id == BODY else 359,
        "pdf_physical_page": 13 if segment_id == BODY else 13,
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


def footnote(marker, note_lines, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": note_lines, "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_note_statement_ids": list(statement_ids),
    }


# Close the p.358 limit clause using its p.359 continuation; preserve the original anchor.
previous = statement_by_id[previous_statement_id]
previous["predicate"] = previous["predicate"].removesuffix("_partial")
previous["qualifiers"]["claim"] = (
    "Haskell says Algarotti recognized limits to the picturesque invention he could expect from "
    "architectural painters such as Tesi and Pesci; at p.359 he reports that Algarotti asked "
    "Tiepolo to supplement their efforts by inserting figures into their backgrounds."
)
previous["qualifiers"]["qualification"] = (
    "The p.358 sentence is closed by p.359 L127. The continuation is separately recorded as "
    "st-chp14-p359-asked-tiepolo-to-insert-figures; this does not identify every background "
    "painting or imply that all requested additions were completed."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = "p.358 L124 continues at p.359 L127 and is closed there."
previous["qualifiers"]["cross_reference_statement_ids"] = ["st-chp14-p359-asked-tiepolo-to-insert-figures"]

# Body statements preserve distinctions between requests, completed additions, and Haskell's analysis.
add_statement(
    "st-chp14-p359-asked-tiepolo-to-insert-figures", BODY, "cand-0054", "cand-2569",
    "asked_tiepolo_to_insert_figures_into_architectural_painting_backgrounds", 127, 127,
    "Haskell reports that Algarotti asked his favourite Tiepolo to insert figures into backgrounds in the architectural painters’ works.",
    qualification="The request supplements the limits described at p.358 L124. The passage does not identify every background painting or say that every requested addition was completed.",
    mentioned=["cand-0054", "cand-2569", "cand-10397", "cand-2551", "cand-1887"],
    relation_candidate=True, **footnote(1, "L214", ["st-chp14-p359-note1-baudi-di-vesme-locator"]))

add_statement(
    "st-chp14-p359-classical-framework-and-pictorial-variety", BODY, "cand-0076", None,
    "classical_framework_limited_tiepolo_fantasy_while_adding_life_and_variety", 127, 128,
    "Haskell says that within a classical framework devised by Algarotti and his executants, Tiepolo’s fantasy was limited yet added the life and variety Algarotti wanted.",
    qualification="This is Haskell’s characterization of the balance; it is not a claim that every resulting picture achieved it.",
    mentioned=["cand-0059", "cand-2569", "cand-0076"])

add_statement(
    "st-chp14-p359-tiepolo-additions-to-pesci-setting", BODY, "cand-2569", "cand-10398",
    "added_landscape_boat_and_white_horse_to_pesci_architectural_setting", 128, 128,
    "Haskell quotes Algarotti describing a landscape ‘derived from Titian’ and a boat and white horse ‘worthy of Wouwermans’ that Tiepolo had added to Pesci’s dry architectural setting.",
    text_layer="letter quotation reproduced by Haskell", speaker="Algarotti, as quoted by Haskell",
    qualification="The wording is quoted through Haskell; the cited letter was not independently consulted. ‘Derived from Titian’ and ‘worthy of Wouwermans’ are source comparisons, not authorship claims.",
    mentioned=["cand-2569", "cand-10398", "cand-2630", "cand-2820", "cand-1887"],
    relation_candidate=True, **footnote(2, "L215", ["st-chp14-p359-note2-opere-locator"]))

add_statement(
    "st-chp14-p359-small-scale-tiepolo-commissions", BODY, "cand-0054", "cand-2569",
    "later_tiepolo_commissions_mainly_figural_inserts_and_veronese_copies", 129, 130,
    "Haskell says Algarotti’s later commissions to Tiepolo were mainly small-scale works: figures added to other artists’ architectural paintings and copies after Veronese.",
    qualification="The passage describes the main character of the later commissions, not an exhaustive list or identified individual works.",
    mentioned=["cand-0054", "cand-2569", "cand-10397", "cand-10399", "cand-2755"],
    relation_candidate=True)

add_statement(
    "st-chp14-p359-no-position-for-great-pictures", BODY, "cand-0050", None,
    "no_longer_in_position_to_order_great_pictures_as_when_serving_ambitious_patrons", 130, 130,
    "Haskell says Algarotti was no longer in a position to order the great pictures he had enjoyed commissioning when he served ambitious patrons.",
    qualification="The text gives a contrast in Algarotti’s circumstances but does not identify the earlier patrons or specify a single cause.",
    mentioned=["cand-0050"])

add_statement(
    "st-chp14-p359-tiepolo-requests-sacrificed", BODY, "cand-2569", "cand-0054",
    "could_not_fulfil_even_modest_algarotti_requests_and_requests_were_sacrificed", 130, 131,
    "Haskell says Tiepolo could not fulfil even these modest requirements: he was overwhelmingly in demand, compelled to go to Spain, and Algarotti’s requests had to be sacrificed.",
    qualification="This is Haskell’s explanation; the passage supplies no exact departure date, Spanish destination, or named competing commissions.",
    mentioned=["cand-2569", "cand-0054", "cand-10409"], relation_candidate=True)

add_statement(
    "st-chp14-p359-algarotti-relied-on-tesi", BODY, "cand-0050", "cand-2551",
    "increasing_ill_health_led_algarotti_to_rely_almost_exclusively_on_tesi", 131, 131,
    "Haskell reports that Algarotti, increasingly stricken with ill-health, had to rely almost exclusively on Mauro Tesi.",
    qualification="‘Almost exclusively’ is retained; no diagnosis or exact onset is supplied.",
    mentioned=["cand-0050", "cand-2551"], relation_candidate=True)

for object_id, label in [("cand-2551", "Tesi"), ("cand-10406", "his wife")]:
    add_statement(
        f"st-chp14-p359-intimate-relations-{label.replace(' ', '-')}", BODY, "cand-0050", object_id,
        "established_extremely_intimate_relations_with", 132, 132,
        f"Haskell characterizes Algarotti’s relations with {label} as ‘extremely intimate’." if object_id == "cand-2551" else
        "Haskell says Algarotti established ‘extremely intimate relations’ with Tesi and his unnamed wife.",
        qualification="Preserve Haskell’s characterization without inferring a specific romantic, sexual, legal, or household relationship.",
        mentioned=["cand-0050", object_id, "cand-2551"], relation_candidate=True)

add_statement(
    "st-chp14-p359-godfather-to-tesi-daughter", BODY, "cand-0050", "cand-10407",
    "was_godfather_to_tesi_and_his_wifes_daughter", 132, 132,
    "Haskell says Algarotti became godfather to the daughter of Tesi and his wife.",
    qualification="The daughter is unnamed; the passage does not provide a date or further family details.",
    mentioned=["cand-0050", "cand-2551", "cand-10406", "cand-10407"], relation_candidate=True)

add_statement(
    "st-chp14-p359-took-tesi-through-central-italy", BODY, "cand-0050", "cand-2551",
    "took_tesi_through_central_italy_to_copy_admired_works", 132, 132,
    "Haskell says Algarotti took Tesi throughout central Italy to make copies of works he especially admired.",
    qualification="The source does not identify the copied works or give dates for the journey.",
    mentioned=["cand-0050", "cand-2551", "cand-7392", "cand-10400"], relation_candidate=True)

add_statement(
    "st-chp14-p359-employed-tesi-to-copy-dietrich-landscapes", BODY, "cand-0050", "cand-2551",
    "employed_tesi_to_copy_landscapes_by_dietrich", 132, 132,
    "Haskell says Algarotti also employed Tesi to copy landscapes by Dietrich.",
    qualification="The painter is identified only by the surname Dietrich here; identity remains for S3. No landscape titles or dates are supplied.",
    mentioned=["cand-0050", "cand-2551", "cand-10405", "cand-10401"], relation_candidate=True)

add_statement(
    "st-chp14-p359-employed-tesi-to-engrave-vignettes", BODY, "cand-0050", "cand-2551",
    "employed_tesi_to_engrave_vignettes_for_planned_edition", 132, 133,
    "Haskell says Algarotti employed Tesi to engrave vignettes for the edition of collected works he was preparing.",
    qualification="The edition is described as in preparation; do not treat it as already published or identify it automatically with the later seventeen-volume Opere edition.",
    mentioned=["cand-0050", "cand-2551", "cand-10402", "cand-10403"], relation_candidate=True)

add_statement(
    "st-chp14-p359-tesi-summoned-to-decorate-pisa-room", BODY, "cand-0050", "cand-2551",
    "summoned_tesi_in_1764_to_decorate_room_in_pisa", 133, 134,
    "Haskell says that in 1764 Algarotti summoned Tesi to decorate the room in Pisa where he lay dying.",
    qualification="The building and room are unnamed; ‘where he lay dying’ is Haskell’s description and does not establish the exact date or circumstances of death.",
    mentioned=["cand-0050", "cand-2551", "cand-10408", "cand-5628"], relation_candidate=True)

add_statement(
    "st-chp14-p359-theoretical-works-on-arts", BODY, "cand-0079", "cand-10404",
    "produced_theoretical_works_to_formulate_views_on_the_arts", 135, 135,
    "Haskell says that in these final years Algarotti produced a number of theoretical works in which he tried to formulate his views on the arts.",
    qualification="The works are not titled in this passage; do not infer a count or edition.",
    mentioned=["cand-0079", "cand-0050", "cand-10404"],
    **footnote(3, "L216", ["st-chp14-p359-note3-gabbrielli-general-discussion"]))

add_statement(
    "st-chp14-p359-evaluation-of-theoretical-works", BODY, "cand-0079", None,
    "works_add_little_to_informal_expressions_but_make_him_sympathetic_and_helpful_critic", 135, 135,
    "Haskell judges that the theoretical works add little to Algarotti’s more casual expressions in letters, commissions, and projects, repeating confusions and contradictions that weakened his position as a theorist but made him a sympathetic and helpful critic to artists.",
    text_layer="authorial evaluation", qualification="This is Haskell’s evaluative interpretation, not a neutral bibliographic description.",
    mentioned=["cand-0079", "cand-0050"])

add_statement(
    "st-chp14-p359-algarotti-moved-toward-neo-classicism", BODY, "cand-0059", "cand-6439",
    "moved_somewhat_toward_neo_classicism_with_drawing_sculpture_idealism_and_hierarchy", 135, 135,
    "Haskell says Algarotti had moved somewhat further toward neo-classicism, citing his categorical priority of drawing over colour, insistence on studying Greek sculpture, idealistic theory of art, and rigid hierarchy of values.",
    qualification="‘Somewhat further’ and the listed tendencies are Haskell’s characterization; this does not erase the passage’s continuing qualifications or prove a complete conversion.",
    mentioned=["cand-0059", "cand-6439", "cand-0079"])

add_statement(
    "st-chp14-p359-qualified-theoretical-approach", BODY, "cand-0079", None,
    "qualified_theoretical_positions_and_warned_against_excessive_sculpture_or_severity", 136, 136,
    "Haskell says that even in a purely theoretical approach Algarotti was careful not to commit himself too far: he qualified each point, warning that too much study of sculpture might lead to dryness and too much severity was harmful.",
    qualification="Retain ‘might’ for the possible effect of excessive sculpture study; these are reported cautions, not claims that dryness necessarily followed.",
    mentioned=["cand-0079", "cand-0059"])

add_statement(
    "st-chp14-p359-reconciliation-demand-in-every-commission", BODY, "cand-0059", None,
    "demanded_reconciliation_of_contrasting_styles_in_every_commission", 137, 137,
    "Haskell says Algarotti demanded a reconciliation in every commissioned work between Roman and Venetian, learned and fantastic, classical and picturesque styles.",
    qualification="This is Haskell’s generalized account of Algarotti’s demands, not proof that each work achieved the synthesis.",
    mentioned=["cand-0059", "cand-0076", "cand-0054"])

add_statement(
    "st-chp14-p359-algarotti-synthesis-styles-partial", BODY, "cand-0059", None,
    "was_always_trying_to_synthesize_two_styles_just_beginning_to_clash_partial", 137, 137,
    "Haskell says Algarotti was always trying to effect a synthesis between the two styles that were just beginning to clash in a battle.",
    qualification="The sentence continues at p.360 L140 with the battle’s resolution after Algarotti’s death; keep this statement partial until that continuation is read.",
    mentioned=["cand-0059", "cand-0076"], cross_reference_segments=[BODY_NEXT],
    cross_reference_text="p.359 L137 continues at p.360 L140; closure is pending.")

# Notes 1-4 are transcribed as Haskell's citation trail, not independent source verification.
add_statement(
    "st-chp14-p359-note1-baudi-di-vesme-locator", NOTES, "cand-3419", "cand-10410",
    "cites_baudi_di_vesme_1912_pages_309_329", 214, 214,
    "P.359 note 1 cites Baudi di Vesme, 1912, pages 309–329.",
    qualification="The cited work and pages were not independently consulted.", mentioned=["cand-3419", "cand-10410"])

add_statement(
    "st-chp14-p359-note2-opere-locator", NOTES, None, "cand-10411",
    "cites_opere_viii_page_101", 215, 215,
    "P.359 note 2 cites Opere, volume VIII, page 101.",
    qualification="Print reads Opere; S0 OCR reads ‘Opéré’. The volume and page were not independently consulted.",
    mentioned=["cand-10411"])

for marker, line_number in [(3, 216), (4, 217)]:
    add_statement(
        f"st-chp14-p359-note{marker}-gabbrielli-general-discussion", NOTES, None, "cand-10412",
        "cites_gabbrielli_1938_and_1939_for_general_discussion", line_number, line_number,
        f"P.359 note {marker} points to Annamaria Gabbrielli, 1938 and 1939, for a general discussion of the cited subject.",
        qualification="The two publications are unidentified in these notes and were not independently consulted; the same citation appears in notes 3 and 4.",
        mentioned=["cand-10412", "cand-10413", "cand-10414"])

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp14-p359-")}
expected_statement_count = 24
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.359 statements, got {len(new_statement_ids)}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L119-124",
    "note": "Printed p.358 read against CHP-14.pdf physical p.12. L124 is closed by p.359 L127, where Algarotti asks Tiepolo to supplement the architectural painters’ efforts; the continuation is cross-linked. Notes 1–6 at L208–213 remain linked; S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L127-137",
    "note": "Printed p.359 read against CHP-14.pdf physical p.13. Recorded commissions, Tesi relationships and work groups, Algarotti’s theoretical positions and Haskell’s evaluation. L137 continues at p.360 L140, so this segment remains partial; body footnotes 1–3 are linked and note 4's marker is on the continuation. S2-only print corrections recorded; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-217",
    "note": "Printed p.359 notes 1–4 at L214–217 read against CHP-14.pdf physical p.13 and recorded. Note 4 repeats the Gabbrielli 1938/1939 citation and its body marker occurs on p.360; link when that continuation is migrated. Remaining notes in the consolidated segment are pending; S0 unchanged.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "updated_statements": [previous_statement_id],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
}

if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in touched:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + planned_mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
