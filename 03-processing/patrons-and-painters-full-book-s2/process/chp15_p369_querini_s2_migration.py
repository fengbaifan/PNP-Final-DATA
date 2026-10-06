"""Controlled S2 migration for printed p.369 and its notes 1-4."""
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
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l38-47"
BODY = "chp-15:15_CHP-15_sec_ii:l49-59"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l61-67"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
PREV_STATEMENT = "st-chp15-p368-querini-state-inquisition-dispute-partial"
BACKUP_SUFFIX = ".bak-s2-chp15-p369-querini-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.369 S2 migration")
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
    (47, "which Querini wished to"), (50, "reduce."), (50, "balance of power within the ruling class"),
    (51, "Marco Foscarini"), (51, "arrest and detention in a fortress"),
    (52, "In 1764 rumour credited him"), (52, "went to Switzerland and visited Voltaire"),
    (52, "text from Lucretius"), (53, "Girolamo Festari"), (53, "country house at Alticchiero"),
    (54, "Giustiniana Wynne"), (55, "Count Rosenberg"), (55, "rapturous account"),
    (57, "busts of ancient and modern philosophers"), (58, "unique in Italy"),
    (59, "plans of the great European cities"),
    (105, "anonymous author of Voyages"), (105, "The Hague in 1777"),
    (106, "Festari."), (107, "Cardinal de Bernis"),
    (108, "Alticchiero, Venezia 1787"), (108, "Heraclitus and Democritus"),
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
    or coverage_by_id[NOTES]["source_line_ranges"] != "L91-104"
):
    raise SystemExit("S2 coverage preconditions changed")
if PREV_STATEMENT not in statement_by_id or statement_by_id[PREV_STATEMENT]["qualifiers"].get("predicate_status") != "partial":
    raise SystemExit("expected p.368 cross-page statement is not partial")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.369 body rows already exist")
if any(row.get("statement_id", "").startswith("st-chp15-p369-") for row in statements):
    raise SystemExit("p.369 statements already exist")

new_candidates = [
    ("cand-10527", "Anonymous author of Voyages en differens pays de l'Europe en 1774, 1775, et 1776", "person", 105,
     "Haskell identifies the author as anonymous; this candidate records the attributed source role, not an inferred identity."),
    ("cand-10528", "Voyages en differens pays de l'Europe en 1774, 1775, et 1776 (The Hague, 1777), vol. I", "archive", 105,
     "Haskell cites this publication for the 1764 authorship rumour; exact edition and cited passage have not been independently checked."),
    ("cand-10529", "Switzerland (in Querini's reported 1777 journey)", "place", 52,
     "Place named in Haskell's account; identity reconciliation remains for S3."),
    ("cand-10530", "Medal specially coined by Angelo Querini for Voltaire, depicting Philosophy destroying Superstition", "work", 52,
     "The design and gift are reported by Haskell; no surviving object or independent catalogue record is identified here."),
    ("cand-10531", "Lucretius (source named for the medal inscription)", "person", 52,
     "Named as the source of the inscription EXAEQUAT VICTORIA COELO; the exact textual locus is not supplied."),
    ("cand-10532", "Angelo Querini's 1777 journey in Switzerland with Girolamo Festari", "event", 52,
     "Event candidate scoped to Haskell's brief account; itinerary beyond the named Switzerland visit is unspecified."),
    ("cand-10533", "Unidentified fortress where Angelo Querini was detained", "place", 51,
     "Haskell does not identify the fortress or its location."),
    ("cand-10534", "Giustiniana Wynne-Rosenberg, Alticchiero (Venezia, 1787)", "archive", 108,
     "Cited by Haskell as Wynne-Rosenberg's account of the villa; the edition has not been independently consulted."),
    ("cand-10535", "Bruno Brunelli, article on Alticchiero (1931), pp. 4-11", "archive", 108,
     "Haskell describes and cites the article; title and publication details beyond the note have not been verified."),
    ("cand-10536", "Mémoires et Lettres, vol. I, p. 166 (Cardinal de Bernis citation locator)", "archive", 107,
     "A citation locator in Haskell's note; cited text has not been independently consulted."),
    ("cand-10537", "Marquis de Prié (named in Cardinal de Bernis quotation)", "person", 107,
     "Historical identity is not resolved here; retain the title and spelling used in Haskell's note."),
    ("cand-10538", "Heraclitus (named in the p.369 note on busts at Casa Soster)", "person", 108,
     "Named by Haskell as represented by a bust reportedly at Casa Soster; identity is not further qualified."),
    ("cand-10539", "Democritus (named in the p.369 note on busts at Casa Soster)", "person", 108,
     "Named by Haskell as represented by a bust reportedly at Casa Soster; identity is not further qualified."),
    ("cand-10540", "Casa Soster, Padua", "place", 108,
     "Haskell says the Heraclitus and Democritus busts were there at the time of Brunelli's 1931 article; no present location is implied."),
    ("cand-10541", "Busts of Voltaire and Rousseau by Houdon at Alticchiero", "work", 57,
     "Haskell reports the busts among furnishings at the villa; individual titles, dates, and later locations are not supplied."),
    ("cand-10542", "Plans of major European cities displayed on the walls at Alticchiero", "work", 59,
     "Only the beginning of this sentence is present on p.369; the description remains partial pending p.370."),
    ("cand-10543", "Tahiti (in Giustiniana Wynne-Rosenberg's comparison with Alticchiero)", "place", 57,
     "Named in a reported comparison about trust in human nature; no geographic normalization is performed in S2."),
    ("cand-10544", "Busts of Heraclitus and Democritus reported at Casa Soster, Padua", "work", 108,
     "The 1931 location report is secondary and time-bound; no current location or object identity is independently verified."),
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
    BODY: {number: source_lines[number - 1] for number in range(49, 60)},
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
    mention_id = f"m-chp15-p369-querini-{mention_counter:04d}"
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
        "printed_page": 369 if segment_id == BODY else 369,
        "pdf_physical_page": 9,
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


# The p.368 sentence ends with the first word on p.369; preserve the original quote and close it by cross-reference.
previous = statement_by_id[PREV_STATEMENT]
previous["predicate"] = "querini_wished_to_reduce_state_inquisition_powers"
previous["qualifiers"]["predicate_status"] = "complete"
previous["qualifiers"]["claim"] = "Haskell says the dispute concerned State Inquisition powers that Querini wished to reduce."
previous["qualifiers"]["qualification"] = (
    "The p.368 clause ends after 'wished to'; p.369 L50 supplies 'reduce.' The page image reads 'reduce.'; "
    "the source does not specify the exact institutional power or the proposed legal mechanism."
)
previous["qualifiers"]["cross_reference_text"] = "P.368 L47 'wished to' continues at p.369 L50 'reduce.'"
previous["qualifiers"]["cross_reference_text_pending"] = False

# Body mentions are anchored to the OCR layer; print corrections remain in S2 notes below.
add_mention("cand-1053", "Marco Foscarini", BODY, 51)
add_mention("cand-2075", "Querini", BODY, 51)
add_mention("cand-10533", "a fortress", BODY, 51, "The source does not name the fortress.")
add_mention("cand-2075", "him", BODY, 52, "Querini remains the subject from the preceding page.")
add_mention("cand-8107", "Enlightenment", BODY, 52)
add_mention("cand-0265", "Beccaria", BODY, 52)
add_mention("cand-9707", "Dei delitti e dette pene", BODY, 52, "OCR reads 'dette'; the p.369 print reads 'delle'.")
add_mention("cand-10529", "Switzerland", BODY, 52)
add_mention("cand-2791", "Voltaire", BODY, 52)
add_mention("cand-10530", "a medal", BODY, 52, "Specially coined; the design is described in the same sentence.")
add_mention("cand-10531", "Lucretius", BODY, 52)
add_mention("cand-1032", "Girolamo Festari", BODY, 53)
add_mention("cand-0086", "Alticchiero", BODY, 53)
add_mention("cand-1803", "Padua", BODY, 53)
add_mention("cand-2824", "Giustiniana Wynne", BODY, 54)
add_mention("cand-2440", "Consul Smith", BODY, 54)
add_mention("cand-1642", "Andrea Memmo", BODY, 55)
add_mention("cand-2259", "Count Rosenberg", BODY, 55)
add_mention("cand-2824", "her", BODY, 55, "Pronoun refers to Giustiniana Wynne; her exact roles remain as described by Haskell.")
add_mention("cand-0086", "Alticchiero", BODY, 55)
add_mention("cand-2824", "her", BODY, 56, "Pronoun refers to Giustiniana Wynne.")
add_mention("cand-0086", "Alticchiero", BODY, 56)
add_mention("cand-10541", "busts of ancient and modern philosophers", BODY, 57)
add_mention("cand-2791", "Voltaire", BODY, 57)
add_mention("cand-2289", "Rousseau", BODY, 57)
add_mention("cand-1305", "Houdon", BODY, 57)
add_mention("cand-0086", "villa", BODY, 57)
add_mention("cand-0086", "gardens", BODY, 57)
add_mention("cand-10543", "Tahiti", BODY, 57)
add_mention("cand-2824", "Mme Rosenberg", BODY, 57)
add_mention("cand-3461", "Italy", BODY, 58)
add_mention("cand-10529", "Switzerland", BODY, 58)
add_mention("cand-10542", "plans of the great European cities", BODY, 59)

# Footnote mentions for the p.369 notes 1-4.
add_mention("cand-10527", "anonymous author", NOTES, 105)
add_mention("cand-10528", "Voyages en different pays de l’Europe en 1774, 1775, et 1776", NOTES, 105)
add_mention("cand-8959", "The Hague", NOTES, 105)
add_mention("cand-1032", "Festari", NOTES, 106)
add_mention("cand-8801", "Cardinal de Bernis", NOTES, 107)
add_mention("cand-2259", "Le Comte de Rosenberg", NOTES, 107)
add_mention("cand-10537", "the Marquis de Prié", NOTES, 107)
add_mention("cand-10536", "Mémoires et Lettres", NOTES, 107)
add_mention("cand-2824", "Giustiniana Wynne-Rosenberg", NOTES, 108)
add_mention("cand-10534", "Alticchiero", NOTES, 108)
add_mention("cand-2719", "Venezia", NOTES, 108)
add_mention("cand-9502", "Bruno Brunelh", NOTES, 108, "OCR form; the print reads Bruno Brunelli.")
add_mention("cand-10535", "article", NOTES, 108, "The article title is not supplied in this note.")
add_mention("cand-10538", "Heraclitus", NOTES, 108)
add_mention("cand-10539", "Democritus", NOTES, 108)
add_mention("cand-10540", "Casa Soster", NOTES, 108)
add_mention("cand-1803", "Padua", NOTES, 108)

N1 = "st-chp15-p369-note1-anonymous-voyages-rumour-source"
N2 = "st-chp15-p369-note2-festari-reference"
N3 = "st-chp15-p369-note3-bernis-rosenberg-quotation"
N4A = "st-chp15-p369-note4-alticchiero-wynne-publication"
N4B = "st-chp15-p369-note4-brunelli-article"
N4C = "st-chp15-p369-note4-heraclitus-democritus-busts"

FOOTNOTE_FIELDS = {
    "1": footnote_fields(1, 105, 105, 52, [N1], "The note identifies the source Haskell gives for the authorship rumour."),
    "2": footnote_fields(2, 106, 106, 52, [N2], "The printed marker follows the Voltaire visit; the note names Festari, introduced in the following sentence."),
    "3": footnote_fields(3, 107, 107, 55, [N3]),
    "4": footnote_fields(4, 108, 108, 55, [N4A, N4B, N4C]),
}

def link_footnote(statement_id, marker):
    statement_by_id[statement_id]["qualifiers"].update(FOOTNOTE_FIELDS[str(marker)])


# Body statements.
add_statement(
    "st-chp15-p369-querini-reform-within-ruling-class", "cand-2075", "cand-1053",
    "proposed_reforms_would_shift_power_within_ruling_class_without_fundamental_change", BODY, 50, 51,
    "Haskell doubts that Querini's proposal should be called progressive: he says it would shift power between ruling-class factions without fundamental change.",
    qualification="This is Haskell's political interpretation; the specific reform programme is not detailed here.",
    mentioned=["cand-2075", "cand-1053"],
)
add_statement(
    "st-chp15-p369-foscarini-victory-querini-arrest", "cand-1053", "cand-2075",
    "victory_of_foscarini_faction_followed_by_querini_arrest_and_detention", BODY, 50, 51,
    "Haskell says the conservatives' victory, led by Marco Foscarini, was followed by Querini's arrest and detention in an unnamed fortress for a couple of years.",
    qualification="The duration and sequence are reported by Haskell; the fortress is not identified.",
    mentioned=["cand-1053", "cand-2075", "cand-10533"], relation_candidate=True,
)
add_statement(
    "st-chp15-p369-querini-withdrawal-from-active-politics", "cand-2075", None,
    "after_release_left_active_politics_for_intellectual_and_cultural_pursuits", BODY, 51, 51,
    "Haskell says that after his release Querini took no further part in active politics and devoted himself to intellectual and cultural pursuits.",
    qualification="This summarizes Haskell's account; it does not establish that Querini held no public role of any kind thereafter.",
    mentioned=["cand-2075"],
)
add_statement(
    "st-chp15-p369-querini-enlightenment-involvement", "cand-2075", "cand-8107",
    "increasingly_involved_with_enlightenment", BODY, 52, 52,
    "Haskell says Querini became increasingly involved with Enlightenment currents.",
    qualification="Haskell's broad characterization; no specific organization or membership is named.", mentioned=["cand-2075", "cand-8107"],
)
RUMOUR = "st-chp15-p369-querini-beccaria-authorship-rumour"
add_statement(
    RUMOUR, "cand-2075", "cand-9707", "rumoured_to_be_author_of_beccaria_treatise", BODY, 52, 52,
    "Haskell reports a 1764 rumour crediting Querini as author of Beccaria's anonymously published Dei delitti e delle pene.",
    qualification="This is explicitly a rumour, not an authorship finding. OCR reads 'dette pene'; the p.369 print reads 'delle pene'.",
    mentioned=["cand-2075", "cand-0265", "cand-9707"], relation_candidate=True,
)
VISIT = "st-chp15-p369-querini-1777-switzerland-voltaire-visit"
add_statement(
    VISIT, "cand-2075", "cand-2791", "visited_voltaire_in_switzerland_1777", BODY, 52, 52,
    "Haskell says Querini went to Switzerland in 1777 and visited Voltaire.",
    qualification="The itinerary and date are given only at this level of detail in the passage.",
    mentioned=["cand-2075", "cand-10529", "cand-2791"], relation_candidate=True,
)
MEDAL = "st-chp15-p369-querini-medal-gift-to-voltaire"
add_statement(
    MEDAL, "cand-2075", "cand-2791", "presented_specially_coined_medal_to_voltaire", BODY, 52, 52,
    "Haskell says Querini presented Voltaire with a specially coined medal depicting Philosophy destroying Superstition and bearing EXAEQUAT VICTORIA COELO, a text he attributes to Lucretius.",
    qualification="No surviving medal, exact inscription source, or independent verification is supplied.",
    mentioned=["cand-2075", "cand-2791", "cand-10530", "cand-10531"], relation_candidate=True,
)
TRIP = "st-chp15-p369-querini-festari-companion-trip"
add_statement(
    TRIP, "cand-2075", "cand-1032", "travelled_with_festari_as_companion_in_1777", BODY, 53, 53,
    "Haskell identifies Girolamo Festari, described as a doctor and scientist, as Querini's companion on the trip; they admired pictures and architecture and commented on local trade and industry.",
    qualification="The places visited are not enumerated. The footnote marker appears after the Voltaire sentence and its note reads only 'Festari.'",
    mentioned=["cand-2075", "cand-1032", "cand-10532"], relation_candidate=True,
)
HOUSE = "st-chp15-p369-querini-alticchiero-building-decoration"
add_statement(
    HOUSE, "cand-2075", "cand-0086", "built_and_decorated_country_house_at_alticchiero", BODY, 53, 53,
    "Haskell says that thereafter much of Querini's life was devoted to building and decorating his country house at Alticchiero, a mile or two from Padua.",
    qualification="The source's approximate distance is retained; no precise location or construction chronology is inferred.",
    mentioned=["cand-2075", "cand-0086", "cand-1803"], relation_candidate=True,
)
FRIEND = "st-chp15-p369-querini-wynne-close-friendship"
add_statement(
    FRIEND, "cand-2075", "cand-2824", "described_as_one_of_querini_closest_friends", BODY, 54, 54,
    "Haskell describes Giustiniana Wynne as among Querini's closest friends.", qualification="This is Haskell's narrative characterization.",
    mentioned=["cand-2075", "cand-2824"], relation_candidate=True,
)
add_statement(
    "st-chp15-p369-wynne-earlier-flirtation-smith", "cand-2824", "cand-2440",
    "haskell_recalled_wynne_flirting_with_consul_smith", BODY, 54, 54,
    "Haskell recalls having previously encountered Wynne flirting with Consul Smith.",
    qualification="The statement is Haskell's retrospective, ironic narration; it is not an independently documented relationship.",
    mentioned=["cand-2824", "cand-2440"], relation_candidate=True,
)
add_statement(
    "st-chp15-p369-wynne-earlier-flirtation-memmo", "cand-2824", "cand-1642",
    "haskell_recalled_wynne_flirting_with_young_andrea_memmo", BODY, 54, 55,
    "Haskell recalls having previously encountered Wynne flirting with the young Andrea Memmo.",
    qualification="The statement is Haskell's retrospective, ironic narration; it is not an independently documented relationship.",
    mentioned=["cand-2824", "cand-1642"], relation_candidate=True,
)
add_statement(
    "st-chp15-p369-wynne-links-three-patrons", "cand-2824", "cand-2075",
    "haskell_says_wynne_links_querini_smith_and_memmo_as_significant_patrons", BODY, 54, 55,
    "Haskell says Wynne closely links three significant patrons: Querini, Consul Smith, and Andrea Memmo.",
    qualification="This is Haskell's interpretive grouping, not a claim that all three had the same relationship with Wynne.",
    mentioned=["cand-2824", "cand-2075", "cand-2440", "cand-1642"],
)
MARRIAGE = "st-chp15-p369-wynne-marriage-rosenberg-1762"
add_statement(
    MARRIAGE, "cand-2824", "cand-2259", "married_austrian_ambassador_count_rosenberg_in_1762", BODY, 55, 55,
    "Haskell says Giustiniana Wynne married the Austrian Ambassador, Count Rosenberg, in 1762.",
    qualification="The passage does not give Rosenberg's personal name.", mentioned=["cand-2824", "cand-2259"], relation_candidate=True,
)
LEARNED = "st-chp15-p369-wynne-interest-in-learned-company"
add_statement(
    LEARNED, "cand-2824", None, "continued_to_value_company_of_the_learned", BODY, 55, 55,
    "Haskell says Wynne's main interest remained the company of learned people.",
    qualification="This is Haskell's characterization, not Wynne's own statement in this passage.", mentioned=["cand-2824"],
)
add_statement(
    "st-chp15-p369-haskell-rosenberg-hardly-aspired-to-learned-company", "cand-2259", None,
    "haskell_says_rosenberg_hardly_aspired_to_learned_company", BODY, 55, 55,
    "Haskell adds that Wynne's husband 'hardly aspired' to the learned company she valued.",
    qualification="Retain as Haskell's pointed evaluation, not a neutral or independently corroborated assessment.",
    mentioned=["cand-2259"],
)
ACCOUNT = "st-chp15-p369-wynne-account-source-for-alticchiero"
add_statement(
    ACCOUNT, "cand-2824", "cand-0086", "account_is_source_for_most_description_of_alticchiero", BODY, 55, 55,
    "Haskell says most knowledge of Alticchiero comes from Wynne-Rosenberg's account and that the villa had long since been razed.",
    qualification="The source does not establish the date or circumstances of the villa's destruction.",
    mentioned=["cand-2824", "cand-0086"],
)
add_statement(
    "st-chp15-p369-wynne-philosophers-modest-retreats", "cand-2824", "cand-0086",
    "opening_remarks_contrast_philosophers_retreats_with_grand_palaces", BODY, 56, 56,
    "In the opening remarks quoted by Haskell, Wynne contrasts grand and luxurious residences with philosophers' modest retreats.",
    speaker="Giustiniana Wynne, quoted by Haskell", text_layer="quoted account",
    qualification="The French phrases are quoted in the source; their wording is not independently checked against the 1787 edition.",
    mentioned=["cand-2824", "cand-0086"],
)
SIMPLE = "st-chp15-p369-alticchiero-simple-convenient-furnishings"
add_statement(
    SIMPLE, "cand-0086", None, "building_and_furnishings_described_as_simple_and_convenient", BODY, 57, 57,
    "Wynne's quoted account describes the building as not sumptuous and its furnishings as neither lavish nor choice, but arranged as simply and conveniently as possible.",
    speaker="Giustiniana Wynne, quoted by Haskell", text_layer="quoted account",
    qualification="The source marks this as a quotation from Wynne; it is not a present-day condition report.",
    mentioned=["cand-0086"],
)
add_statement(
    "st-chp15-p369-alticchiero-houdon-philosopher-busts", "cand-0086", "cand-10541",
    "villa_reportedly_contained_voltaire_and_rousseau_busts_by_houdon", BODY, 57, 57,
    "Haskell says busts of Voltaire and Rousseau by Houdon stood on tables at Alticchiero.",
    qualification="The statement follows Haskell's account of Wynne's description; no individual bust titles or present locations are supplied.",
    mentioned=["cand-0086", "cand-10541", "cand-2791", "cand-2289", "cand-1305"], relation_candidate=True,
)
add_statement(
    "st-chp15-p369-voltaire-influence-alticchiero", "cand-2791", "cand-0086",
    "voltaire_influence_reported_throughout_villa_and_gardens", BODY, 57, 57,
    "Haskell says Voltaire's influence was felt throughout the villa and gardens.",
    qualification="This is Haskell's interpretation of the house and garden, not a direct quotation from Voltaire.",
    mentioned=["cand-2791", "cand-0086"],
)
add_statement(
    "st-chp15-p369-rousseau-influence-alticchiero", "cand-2289", "cand-0086",
    "rousseau_influence_reported_throughout_villa_and_gardens", BODY, 57, 57,
    "Haskell says Rousseau's influence was felt throughout the villa and gardens.",
    qualification="This is Haskell's interpretation of the house and garden, not a direct quotation from Rousseau.",
    mentioned=["cand-2289", "cand-0086"],
)
add_statement(
    "st-chp15-p369-alticchiero-no-theft-precautions", "cand-0086", None,
    "no_locks_or_guard_dogs_reported_at_alticchiero", BODY, 57, 57,
    "Haskell reports that no precautions were taken against theft at Alticchiero: nothing was locked up and no dogs roamed the grounds.",
    qualification="This is a historical description attributed to Wynne's account, not a security assessment beyond the passage.", mentioned=["cand-0086"],
)
add_statement(
    "st-chp15-p369-wynne-trust-human-nature-tahiti-alticchiero", "cand-2824", "cand-10543",
    "wynne_compared_trust_in_human_nature_at_tahiti_and_alticchiero", BODY, 57, 57,
    "Haskell reports Wynne's exclamation that such trust in human nature could be found only at Tahiti and Alticchiero.",
    qualification="This is a rhetorical comparison in the account, not an empirical generalization about either place.",
    mentioned=["cand-2824", "cand-10543", "cand-0086"],
)
add_statement(
    "st-chp15-p369-haskell-alticchiero-unique-and-edifying", "cand-0086", None,
    "haskell_calls_alticchiero_unique_in_italy_and_edifying_even_in_switzerland", BODY, 58, 58,
    "Haskell calls Alticchiero unique in Italy and says it would be edifying even in Switzerland.",
    qualification="Explicitly preserve this as the author's evaluation.", mentioned=["cand-0086", "cand-3461", "cand-10529"],
)
CITY_PLANS = "st-chp15-p369-alticchiero-european-city-plans-partial"
add_statement(
    CITY_PLANS, "cand-0086", "cand-10542", "rooms_reportedly_displayed_plans_of_major_european_cities_partial", BODY, 59, 59,
    "The sentence begins by saying that plans of major European cities were on the walls of rooms at Alticchiero.",
    qualification="The sentence continues on p.370; the purpose, remaining description, and predicate are not completed here.",
    mentioned=["cand-0086", "cand-10542"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT], cross_reference_text="P.369 L59 continues at p.370.", cross_reference_text_pending=True,
)

for sid, marker in [(RUMOUR, 1), (VISIT, 2), (TRIP, 2), (MARRIAGE, 3), (LEARNED, 3), (ACCOUNT, 4),
                    (SIMPLE, 4), ("st-chp15-p369-alticchiero-houdon-philosopher-busts", 4),
                    ("st-chp15-p369-voltaire-influence-alticchiero", 4),
                    ("st-chp15-p369-rousseau-influence-alticchiero", 4),
                    ("st-chp15-p369-alticchiero-no-theft-precautions", 4),
                    ("st-chp15-p369-wynne-trust-human-nature-tahiti-alticchiero", 4),
                    ("st-chp15-p369-haskell-alticchiero-unique-and-edifying", 4)]:
    link_footnote(sid, marker)

# Note statements retain the citation chain and the scope of Haskell's secondary reports.
add_statement(
    N1, None, "cand-10528", "note_attributes_authorship_rumour_to_anonymous_voyages_author", NOTES, 105, 105,
    "Haskell's note says the authorship rumour was reported by the anonymous author of Voyages en different pays de l'Europe en 1774, 1775, et 1776, published at The Hague in 1777, vol. I, p. 211.",
    speaker="Haskell's note", text_layer="bibliographic citation and source attribution",
    qualification="The cited book and passage were not independently consulted; OCR reads p. 2II and the print reads p. 211.",
    mentioned=["cand-10527", "cand-10528", "cand-8959"], cited_source_independently_consulted=False,
    **FOOTNOTE_FIELDS["1"],
)
add_statement(
    N2, None, "cand-1032", "note_names_festari", NOTES, 106, 106,
    "Haskell's note consists of the name 'Festari.'",
    speaker="Haskell's note", text_layer="name clarification",
    qualification="The note does not provide further biographical or bibliographic detail.", mentioned=["cand-1032"], **FOOTNOTE_FIELDS["2"],
)
add_statement(
    N3, "cand-8801", "cand-2259", "bernis_quotation_compares_rosenberg_with_marquis_de_prie", NOTES, 107, 107,
    "Haskell quotes Cardinal de Bernis describing Count Rosenberg as having more birth, wit, and intrigue than the Marquis de Prié, while saying Rosenberg had scarcely more merit than Prié, whom he called mediocre.",
    speaker="Cardinal de Bernis, quoted by Haskell", text_layer="quoted citation",
    qualification="Preserve the translated summary alongside the French quotation; neither the cited text nor identities are independently checked.",
    mentioned=["cand-8801", "cand-2259", "cand-10537", "cand-10536"], cited_source_independently_consulted=False,
    **FOOTNOTE_FIELDS["3"],
)
add_statement(
    N4A, None, "cand-10534", "note_cites_wynne_alticchiero_1787", NOTES, 108, 108,
    "Haskell cites Giustiniana Wynne-Rosenberg's Alticchiero, published in Venice in 1787.",
    speaker="Haskell's note", text_layer="bibliographic citation",
    qualification="The 1787 edition was not independently consulted.",
    mentioned=["cand-2824", "cand-10534", "cand-2719"], cited_source_independently_consulted=False,
    **FOOTNOTE_FIELDS["4"],
)
add_statement(
    N4B, "cand-9502", "cand-10535", "note_cites_brunelli_1931_article_on_alticchiero", NOTES, 108, 108,
    "Haskell says the remains of Alticchiero are discussed and illustrated in an article by Bruno Brunelli published in 1931, pages 4-11.",
    speaker="Haskell's note", text_layer="bibliographic citation and secondary report",
    qualification="The note calls it a 'sad little article'; the article title and edition were not independently checked. OCR reads Brunelh; the print reads Brunelli.",
    mentioned=["cand-0086", "cand-9502", "cand-10535"], cited_source_independently_consulted=False,
    **FOOTNOTE_FIELDS["4"],
)
add_statement(
    N4C, "cand-10544", "cand-10540", "brunelli_1931_reported_heraclitus_and_democritus_busts_at_casa_soster", NOTES, 108, 108,
    "Haskell reports that at the time of Brunelli's article, busts of Heraclitus and Democritus were in Casa Soster at Padua.",
    speaker="Haskell's note reporting Brunelli", text_layer="secondary location report",
    qualification="The location is explicitly time-bound to the article; it is not a present-day location claim.",
    mentioned=["cand-10538", "cand-10539", "cand-10544", "cand-10540", "cand-1803"],
    cited_source_independently_consulted=False, **FOOTNOTE_FIELDS["4"],
)

# Record print-vs-OCR corrections and the page heading missed by OCR without rewriting S0.
ocr_corrections = [
    {"source_file": SOURCE_FILE, "source_line": 51, "ocr": "accouple", "print": "a couple", "basis": "CHP-15.pdf physical page 9."},
    {"source_file": SOURCE_FILE, "source_line": 52, "ocr": "dette pene", "print": "delle pene", "basis": "CHP-15.pdf physical page 9."},
    {"source_file": SOURCE_FILE, "source_line": 105, "ocr": "different", "print": "differens", "basis": "CHP-15.pdf physical page 9; retain the older French spelling in the print."},
    {"source_file": SOURCE_FILE, "source_line": 105, "ocr": "2II", "print": "211", "basis": "CHP-15.pdf physical page 9."},
    {"source_file": SOURCE_FILE, "source_line": 108, "ocr": "Brunelh", "print": "Brunelli", "basis": "CHP-15.pdf physical page 9."},
]
for row in statements:
    if row["statement_id"].startswith("st-chp15-p369-"):
        row["qualifiers"].setdefault("ocr_corrections", []).extend(ocr_corrections if row["statement_id"] == RUMOUR else [])

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L39-47",
    "note": "Printed p.368 checked against CHP-15.pdf physical p.8; Querini's State Inquisition sentence closes with p.369 L50 'reduce'.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L50-59",
    "note": "Printed p.369 checked against CHP-15.pdf physical p.9. Processes Querini's reform dispute, arrest and post-release life, Enlightenment activity, 1777 Swiss journey, Wynne-Rosenberg and Alticchiero. The page image includes the centered heading 'A NEW DIRECTION', omitted from OCR; recorded here without changing S0. L59 city-plan sentence continues at p.370. Notes 1-4 at consolidated L105-108 are migrated. Print corrections are recorded in S2 only.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L91-108",
    "note": "P.365 notes 1-2 at L91-92, p.367 notes 1-4 at L93-96, p.368 notes 1-7 at L97-104, and p.369 notes 1-4 at L105-108 are migrated. Remaining notes L109-113 belong to later pages and remain pending.",
})

new_statement_ids = [row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p369-")]
result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA, "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids), "updated_statements": [PREV_STATEMENT],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 369, "pdf_physical_page": 9,
    "open_cross_page_statement": CITY_PLANS,
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
