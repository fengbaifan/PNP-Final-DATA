"""Controlled S2 migration for printed p.361; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
INTRO = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_intro.md"
BODY_SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
INTRO_SHA = "015d35e467ad4cca8a4029d62aeb9469e49b4619e8c0c6916f46b0e0e019830b"
BODY_SHA = "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
INTRO_HEADING = "chp-15:15_CHP-15_intro:l1-1"
CHAPTER_HEADING = "chp-15:15_CHP-15_intro:l3-5"
NOTES = "chp-15:15_CHP-15_intro:l7-9"
SECTION_HEADING = "chp-15:15_CHP-15_sec_i:l1-1"
BODY = "chp-15:15_CHP-15_sec_i:l3-14"
BODY_NEXT = "chp-15:15_CHP-15_sec_i:l16-25"
INTRO_FILE = "02-sources/02-Markdown/15_CHP-15_intro.md"
BODY_FILE = "02-sources/02-Markdown/15_CHP-15_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp15-p362-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.361 S2 migration")
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


for path, expected, label in [
    (INTRO, INTRO_SHA, "chapter 15 introductory/notes source"),
    (BODY_SOURCE, BODY_SHA, "chapter 15 body source"),
    (PDF, PDF_SHA, "registered CHP-15 PDF asset"),
]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"{label} changed")

intro_lines = INTRO.read_text(encoding="utf-8-sig").splitlines()
body_lines = BODY_SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (8, "For a vivid account of the deplorable state of Venetian painting"),
    (9, "Letter from Mariette to Temanza of 15 April 1768"),
]:
    if required not in intro_lines[line_number - 1]:
        raise SystemExit(f"required citation text changed at intro L{line_number}")
for line_number, required in [
    (4, "Y 1764, the year of Algarotti’s death"),
    (5, "Piazzetta had been dead for ten years"),
    (6, "Guaraña (born in 1720)"),
    (7, "Canaletto went on mechanically repeating himself"),
    (9, "Republic.1"),
    (10, "The Sagredo pictures were being dispersed"),
    (11, "Smith’s best paintings had been acquired for George III"),
    (12, "When Zanetti died in 1767"),
    (14, "Algarotti, suggested new possibilities for a different kind of patronage"),
]:
    if required not in body_lines[line_number - 1]:
        raise SystemExit(f"required body text changed at L{line_number}")

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

for segment_id in (INTRO_HEADING, CHAPTER_HEADING, NOTES, SECTION_HEADING, BODY, BODY_NEXT):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
for segment_id in (INTRO_HEADING, CHAPTER_HEADING, NOTES, SECTION_HEADING, BODY):
    if coverage_by_id[segment_id]["migration_status"] != "pending":
        raise SystemExit(f"S2 coverage precondition changed: {segment_id}")
if coverage_by_id[BODY_NEXT]["migration_status"] != "pending":
    raise SystemExit("p.362 continuation coverage precondition changed")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10422:
    raise SystemExit("candidate sequence changed; expected max cand-10422")
if "st-chp15-p361-enlightenment-different-patronage-partial" in statement_by_id:
    raise SystemExit("p.361 partial statement ID already exists")

new_candidates = [
    ("cand-10423", "Unnamed widow of Joseph Smith who sold the remainder of his gallery (p.361)", "person", BODY, 11,
     "Source-relative person: Haskell says Smith’s widow sold the remainder of his gallery a few years after the 1762 acquisition. Her name and identity are not supplied."),
    ("cand-10424", "E. Müntz (editor named in p.361 note 2)", "person", NOTES, 9,
     "Editor named in the source form E. Müntz for the 1890 publication of a 1768 letter; no further identity is inferred."),
    ("cand-10425", "G. A. Moschini, 1810 citation in p.361 note 1", "archive", NOTES, 8,
     "Citation to G. A. Moschini (1810) for an account of the state of Venetian painting; title and pages are not supplied in the note and the cited work was not independently consulted."),
    ("cand-10426", "Letter from Mariette to Temanza, 15 April 1768 (published by E. Müntz, 1890, p.116)", "archive", NOTES, 9,
     "Letter identified by correspondent, date, editor/publication year and page in Haskell’s note; the letter and publication were not independently consulted."),
    ("cand-10427", "Joseph Smith’s gallery whose remainder was sold by his widow (p.361)", "", BODY, 11,
     "Source-relative picture collection described as Smith’s gallery. Keep type unresolved and distinct from the other Smith collection candidates pending S3 identity alignment."),
    ("cand-10428", "A. M. Zanetti’s pictures presumed by Mariette to be leaving Venice (p.361)", "", BODY, 12,
     "Unspecified group of Zanetti’s pictures referred to in Haskell’s report of Mariette’s 1768 assumption. No individual works or collection identity are supplied; keep type unresolved."),
    ("cand-10429", "Revival of Venetian painting in the first half of the eighteenth century (p.361)", "term", BODY, 12,
     "Historical process described as encouraged by ‘these men’; the source does not enumerate the phrase’s full referent, so no roster is inferred."),
    ("cand-10430", "Different kind of patronage suggested by the Enlightenment in Venice (p.361)", "term", BODY, 14,
     "Source-described possibility associated with the Enlightenment as it reached Venice; the following sentence continues on p.362, so preserve the unfinished qualification."),
]
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

body_first, body_last = 3, 14
note_first, note_last = 7, 9
segment_bounds = {BODY: (body_first, body_last), NOTES: (note_first, note_last)}
segment_lines = {
    BODY: {number: body_lines[number - 1] for number in range(body_first, body_last + 1)},
    NOTES: {number: intro_lines[number - 1] for number in range(note_first, note_last + 1)},
}
segment_texts = {
    sid: "\n".join(segment_lines[sid][number] for number in range(first, last + 1))
    for sid, (first, last) in segment_bounds.items()
}
segment_offsets = {}
for sid, (first, last) in segment_bounds.items():
    offset = 0
    segment_offsets[sid] = {}
    for number in range(first, last + 1):
        segment_offsets[sid][number] = offset
        offset += len(segment_lines[sid][number]) + 1

planned_mentions = []
mention_counter = 1


def add_mention(segment_id, candidate_id, surface, source_line, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[segment_id][source_line]
    existing_on_line = [
        (int(row["start_char"]), int(row["end_char"]))
        for row in mentions + planned_mentions
        if row["segment_id"] == segment_id
        and segment_offsets[segment_id][source_line] <= int(row["start_char"]) <
            segment_offsets[segment_id][source_line] + len(line)
    ]
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            raise SystemExit(f"surface not found on {segment_id} L{source_line}: {surface!r}")
        start = segment_offsets[segment_id][source_line] + pos
        end = start + len(surface)
        if not any(start < old_end and old_start < end for old_start, old_end in existing_on_line):
            break
        search_from = pos + 1
    mention_id = f"m-chp15-p361-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


# Printed p.361 body, with occurrences anchored to their actual source lines.
add_mention(BODY, "cand-0050", "Algarotti", 4)
add_mention(BODY, "cand-1901", "Piazzetta", 5)
add_mention(BODY, "cand-2569", "Tiepolo", 5)
add_mention(BODY, "cand-10409", "Spain", 5)
add_mention(BODY, "cand-3461", "Italy", 5)
add_mention(BODY, "cand-1950", "Pittoni", 5)
add_mention(BODY, "cand-0005", "Accademia", 5)
add_mention(BODY, "cand-1047", "Fontebasso", 5)
add_mention(BODY, "cand-2888", "Zugno", 5)
add_mention(BODY, "cand-1237", "Guaraña", 6, "S0 OCR spelling; the printed name is Guarana, recorded as an S2-only correction.")
add_mention(BODY, "cand-0498", "Canaletto", 7)
add_mention(BODY, "cand-1239", "Francesco Guardi", 7)
add_mention(BODY, "cand-2879", "Zuccarelli", 8)
add_mention(BODY, "cand-3401", "Venice", 8, "OCR joins ‘of Venice’ as ‘ofVenice’; print spacing correction is recorded in S2.")
add_mention(BODY, "cand-2830", "Zais", 8)
add_mention(BODY, "cand-1429", "Pietro Longhi", 8)
add_mention(BODY, "cand-1424", "Alessandro", 8, "The text identifies him as Pietro Longhi’s son.")
add_mention(BODY, "cand-8520", "great names", 8, "Collective phrase for the great names of the first half of the century; no roster is inferred.")
add_mention(BODY, "cand-8572", "Republic", 9, "‘Dying Republic’ refers to the political community in the book’s usage; candidate identity remains subject to S3.")
add_mention(BODY, "cand-2336", "Sagredo pictures", 10, "Index sub-entry for dispersal of Zaccaria Sagredo’s collection; do not identify individual pictures.")
add_mention(BODY, "cand-9622", "Schulenburg collection", 10)
add_mention(BODY, "cand-5529", "Germany", 11)
add_mention(BODY, "cand-2440", "Smith’s", 11)
add_mention(BODY, "cand-9178", "best paintings", 11, "The source says Smith’s best paintings; retain that scope and do not broaden to all holdings.")
add_mention(BODY, "cand-1141", "George III", 11)
add_mention(BODY, "cand-10427", "gallery", 11)
add_mention(BODY, "cand-2440", "his", 11, "Pronoun refers to Joseph Smith.")
add_mention(BODY, "cand-10423", "widow", 11, "Unnamed source-relative person; no identity is inferred.")
add_mention(BODY, "cand-0050", "Algarotti", 11)
add_mention(BODY, "cand-10223", "own pictures", 11, "Keep distinct from the joint Algarotti–Bonomo and family collections already represented elsewhere.")
add_mention(BODY, "cand-0040", "Bonomo", 11)
add_mention(BODY, "cand-2838", "Zanetti", 12, "The body gives surname only; the index crosswalk is retained without an additional identity inference.")
add_mention(BODY, "cand-1547", "Mariette", 12)
add_mention(BODY, "cand-10428", "his pictures", 12, "Pronoun refers to Zanetti; the unspecified picture group remains separate from other Zanetti holdings.")
add_mention(BODY, "cand-3401", "Venice", 12)
add_mention(BODY, "cand-3401", "there", 12, "Pronoun refers to Venice as the location from which the pictures were assumed to leave.")
add_mention(BODY, "cand-10429", "revival of Venetian painting", 12)
add_mention(BODY, "cand-8124", "great patrician families", 12)
add_mention(BODY, "cand-3563", "hordes of agents", 12, "Generic agency group; no individual agents are named.")
add_mention(BODY, "cand-3401", "Venice", 12)
add_mention(BODY, "cand-0976", "Enlightenment", 13)
add_mention(BODY, "cand-3401", "Venice", 13)
add_mention(BODY, "cand-2068", "publishers", 13)
add_mention(BODY, "cand-3562", "travellers", 13)
add_mention(BODY, "cand-1411", "Lodoli", 13)
add_mention(BODY, "cand-0050", "Algarotti", 14)
add_mention(BODY, "cand-10430", "different kind of patronage", 14)

# Footnote 1–2 citation trail; person and source mentions do not overlap.
add_mention(NOTES, "cand-1709", "G. A. Moschini", 8)
add_mention(NOTES, "cand-10425", "1810", 8, "Year locator for the cited Moschini source.")
add_mention(NOTES, "cand-1547", "Mariette", 9)
add_mention(NOTES, "cand-2546", "Temanza", 9)
add_mention(NOTES, "cand-10426", "15 April 1768", 9, "Date anchor for the source-relative letter candidate.")
add_mention(NOTES, "cand-10424", "E. Müntz", 9)

unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")


def quote(segment_id, line_start, line_end):
    first, last = segment_bounds[segment_id]
    lines = segment_lines[segment_id]
    if not first <= line_start <= line_end <= last:
        raise SystemExit(f"quote span outside segment {segment_id}: L{line_start}-{line_end}")
    return "\n".join(lines[number] for number in range(line_start, line_end + 1))


def footnote(marker, note_line, statement_ids, body_marker_line):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{note_line}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_marker_line}",
        "footnote_note_statement_ids": list(statement_ids),
    }


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), original_quote_override=None, **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 361, "pdf_physical_page": 1,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": original_quote_override if original_quote_override is not None else quote(segment_id, line_start, line_end),
        "origin": "book", "source_file": INTRO_FILE if segment_id == NOTES else BODY_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


add_statement(
    "st-chp15-p361-flowering-nearly-ended-1764", BODY, None, None,
    "venetian_art_flowering_nearly_ended_by_1764", 4, 5,
    "Haskell dates the near end of the great flowering of Venetian art to 1764, the year Francesco Algarotti died.",
    qualification="The drop capital splits ‘By’ across OCR lines (‘Y’ / ‘Bnearly’); print reading is ‘By 1764 … very nearly’. This is Haskell’s periodization, not an independently established endpoint for Venetian art.",
    mentioned=["cand-0050"],
    ocr_corrections=[{"source_lines": "L4-L5", "ocr": "Y 1764 … very / Bnearly at an end", "print": "By 1764 … very nearly at an end"}])
add_statement(
    "st-chp15-p361-piazzetta-dead-ten-years", BODY, "cand-1901", None,
    "had_been_dead_for_ten_years_by_1764", 5, 5,
    "Haskell says Piazzetta had been dead for ten years by 1764.",
    mentioned=["cand-1901", "cand-0050"])
add_statement(
    "st-chp15-p361-tiepolo-in-spain-no-desire-return", BODY, "cand-2569", "cand-10409",
    "was_in_spain_and_showed_no_desire_to_return_to_italy", 5, 5,
    "Haskell says Tiepolo was in Spain and showed no desire to return to Italy.",
    qualification="The print has ‘to return’; OCR inserts a period in ‘to.return’. The sentence does not specify an exact date of departure or an intended return date.",
    mentioned=["cand-2569", "cand-10409", "cand-3461"],
    ocr_corrections=[{"source_line": 5, "ocr": "to.return", "print": "to return"}])
add_statement(
    "st-chp15-p361-pittoni-president-neglected", BODY, "cand-1950", "cand-0005",
    "was_accademia_president_but_increasingly_neglected_as_powers_declined", 5, 5,
    "Haskell says Pittoni was president of the Accademia but increasingly neglected as his powers declined.",
    mentioned=["cand-1950", "cand-0005"])
add_statement(
    "st-chp15-p361-new-history-painters-imitation", BODY, "cand-1047", "cand-2888",
    "new_generation_history_painters_added_little_beyond_imitation", 5, 6,
    "Haskell says the new generation of history painters, including Fontebasso, Zugno (born 1709) and Guarana (born 1720), added little beyond imitation to the heritage of the past.",
    qualification="This is the author’s evaluative generalization. S0 OCR reads ‘Guaraña’; the printed name is Guarana. The text names examples, not a complete roster of the generation.",
    mentioned=["cand-1047", "cand-2888", "cand-1237"],
    ocr_corrections=[{"source_line": 6, "ocr": "Guaraña", "print": "Guarana"}])
add_statement(
    "st-chp15-p361-canaletto-repeated-himself-died-1769", BODY, "cand-0498", None,
    "mechanically_repeated_himself_until_death_in_1769", 7, 7,
    "Haskell says Canaletto went on mechanically repeating himself until his death in 1769.",
    qualification="‘Mechanically repeating himself’ is Haskell’s critical characterization.",
    mentioned=["cand-0498"])
add_statement(
    "st-chp15-p361-guardi-unknown-to-great-patrons-different-public", BODY, "cand-1239", None,
    "virtually_unknown_to_great_patrons_worked_for_different_public", 7, 7,
    "Haskell says Francesco Guardi was virtually unknown to the great patrons and worked for an altogether different public, as would become clear in a later chapter.",
    qualification="Retain ‘virtually’ and the author’s forward reference; the passage does not identify this public here.",
    mentioned=["cand-1239"])
add_statement(
    "st-chp15-p361-zuccarelli-mostly-out-of-venice", BODY, "cand-2879", "cand-3401",
    "was_mostly_out_of_venice", 8, 8,
    "Haskell says Zuccarelli was mostly out of Venice.",
    qualification="OCR joins ‘of Venice’ as ‘ofVenice’; the print includes a space. ‘Mostly’ is retained.",
    mentioned=["cand-2879", "cand-3401"],
    ocr_corrections=[{"source_line": 8, "ocr": "out ofVenice", "print": "out of Venice"}])
add_statement(
    "st-chp15-p361-zais-poverty-neglected", BODY, "cand-2830", None,
    "lived_in_poverty_and_was_almost_completely_neglected", 8, 8,
    "Haskell says Zais was living in poverty and was almost completely neglected.",
    qualification="Preserve ‘almost completely’ rather than converting the author’s qualification into an absolute.",
    mentioned=["cand-2830"])
add_statement(
    "st-chp15-p361-pietro-longhi-carried-on-twenty-years", BODY, "cand-1429", None,
    "continued_for_another_twenty_years", 8, 8,
    "Haskell says Pietro Longhi was the only great name of the first half of the century to carry on for another twenty years.",
    qualification="The duration is approximate wording from the source; it is not converted into a precise end year.",
    mentioned=["cand-1429", "cand-8520"])
add_statement(
    "st-chp15-p361-alessandro-son-of-pietro-longhi", BODY, "cand-1424", "cand-1429",
    "son_of", 8, 8,
    "The source identifies Alessandro as Pietro Longhi’s son.",
    qualification="The source names Alessandro by first name only; the candidate crosswalk to Alessandro Longhi is retained for later identity alignment.",
    mentioned=["cand-1424", "cand-1429"], relation_candidate=True)
add_statement(
    "st-chp15-p361-alessandro-longhi-detached-observation", BODY, "cand-1424", None,
    "introduced_detached_observation_into_portraits_of_grandees_and_intellectuals", 8, 9,
    "Haskell says Alessandro Longhi was bringing a new spirit of detached observation into portraits of grandees and intellectuals of the dying Republic.",
    qualification="The source names Alessandro by first name only; the candidate crosswalk to Alessandro Longhi is retained for later identity alignment.",
    mentioned=["cand-1424", "cand-8572"])
add_statement(
    "st-chp15-p361-artists-patrons-collections-vanishing", BODY, None, None,
    "artists_patrons_and_their_collections_were_vanishing", 10, 10,
    "Haskell generalizes that artists, patrons, and even the great collections they had amassed were vanishing.",
    qualification="This is the author’s transition into specific collection dispersals; it is not itself a quantified claim.",
    mentioned=[])
add_statement(
    "st-chp15-p361-sagredo-pictures-dispersing", BODY, "cand-2336", None,
    "pictures_were_being_dispersed", 10, 10,
    "Haskell says the Sagredo pictures were being dispersed.",
    qualification="No individual pictures, exact dispersal date, or sale event is specified in this sentence.",
    mentioned=["cand-2329", "cand-2336"])
add_statement(
    "st-chp15-p361-schulenburg-collection-broken-up-1775", BODY, "cand-9622", None,
    "collection_broken_up_in_1775", 10, 10,
    "Haskell says the Schulenburg collection was broken up in 1775.",
    qualification="Keep the collection distinct from Schulenburg as a person and from any individual works.",
    mentioned=["cand-2401", "cand-9622"])
add_statement(
    "st-chp15-p361-most-schulenburg-collection-sent-to-germany", BODY, "cand-9622", "cand-5529",
    "most_of_collection_had_long_since_been_sent_to_germany", 10, 11,
    "Haskell says most of the Schulenburg collection had already been sent to Germany long before it was broken up in 1775.",
    qualification="‘Most’ and ‘long since’ are retained; this does not mean the whole collection had left or establish a precise transfer date.",
    mentioned=["cand-9622", "cand-5529"])
add_statement(
    "st-chp15-p361-smith-best-paintings-acquired-george-iii-1762", BODY, "cand-9178", "cand-1141",
    "best_paintings_acquired_for_george_iii_in_1762", 11, 11,
    "Haskell says Joseph Smith’s best paintings had been acquired for George III in 1762.",
    qualification="The claim concerns Smith’s ‘best paintings’; do not expand it to all holdings or merge it with the later sale of the remainder by his widow.",
    mentioned=["cand-2440", "cand-9178", "cand-1141"], relation_candidate=True)
add_statement(
    "st-chp15-p361-widow-sold-remainder-smith-gallery", BODY, "cand-10423", "cand-10427",
    "sold_remainder_of_smith_gallery_a_few_years_later", 11, 11,
    "Haskell says Smith’s unnamed widow sold the remainder of his gallery a few years after the 1762 acquisition.",
    qualification="The widow’s name, exact sale date, and the identities of the remaining works are not supplied. This is distinct from the 1762 acquisition of Smith’s best paintings.",
    mentioned=["cand-2440", "cand-10423", "cand-10427"], relation_candidate=True)
add_statement(
    "st-chp15-p361-algarotti-pictures-dispersed-after-bonomo-death", BODY, "cand-0050", "cand-10223",
    "own_pictures_began_to_be_dispersed_after_bonomos_death_in_1776", 11, 11,
    "Haskell says Algarotti’s own pictures began to be dispersed soon after his brother Bonomo’s death in 1776.",
    qualification="‘Began’ and ‘soon after’ are retained. Keep this personal collection distinct from the joint Algarotti–Bonomo and Algarotti family collections.",
    mentioned=["cand-0050", "cand-10223", "cand-0040"], relation_candidate=True)
add_statement(
    "st-chp15-p361-bonomo-brother-of-algarotti", BODY, "cand-0040", "cand-0050",
    "brother_of", 11, 11,
    "The source identifies Bonomo as Francesco Algarotti’s brother.",
    qualification="Kinship is stated in the source; this source-level candidate relation is not yet a formal S6 edge.",
    mentioned=["cand-0040", "cand-0050"], relation_candidate=True)
add_statement(
    "st-chp15-p361-zanetti-died-1767", BODY, "cand-2838", None,
    "died_in_1767", 12, 12,
    "Haskell says Zanetti died in 1767.",
    qualification="The body uses the surname only. The index crosswalk to A. M. Zanetti the Elder is not supplemented with external identity evidence here.",
    mentioned=["cand-2838"])
add_statement(
    "st-chp15-p361-mariette-assumed-zanetti-pictures-leaving-venice", BODY, "cand-1547", "cand-10428",
    "assumed_zanetti_pictures_would_soon_leave_venice_because_collection_building_interest_had_faded", 12, 12,
    "Haskell reports that Mariette assumed Zanetti’s pictures would soon leave Venice because no one seemed interested any longer in forming a collection there.",
    speaker="Pierre-Jean Mariette, as reported by Haskell",
    qualification="This is Mariette’s reported assumption, not evidence that the pictures actually left Venice. The surname-only Zanetti crosswalk and the unspecified picture group remain distinct from identity verification.",
    mentioned=["cand-1547", "cand-2838", "cand-10428", "cand-3401"],
    **footnote(2, 9, ["st-chp15-p361-note2-mariette-letter"], 12))
add_statement(
    "st-chp15-p361-men-encouraged-revival-venetian-painting", BODY, None, "cand-10429",
    "unnamed_referents_encouraged_revival_during_first_half_of_century", 12, 12,
    "Haskell says ‘these men’ had encouraged the revival of Venetian painting during the first half of the century.",
    qualification="The phrase ‘these men’ has no complete roster in this sentence; no particular people are assigned to the collective without evidence. The OCR apostrophe after ‘during’ is not present in the print.",
    mentioned=["cand-10429"],
    ocr_corrections=[{"source_line": 12, "ocr": "during' the first half", "print": "during the first half"}])
add_statement(
    "st-chp15-p361-patrician-families-sold-possessions-to-agents", BODY, "cand-8124", "cand-3563",
    "were_more_concerned_to_sell_possessions_to_agents_descending_on_venice", 12, 12,
    "Haskell says the great patrician families were even more concerned to sell their possessions to the agents descending on Venice.",
    qualification="‘Like vultures’ is Haskell’s simile. The passage does not identify the families, agents, or the individual objects sold.",
    mentioned=["cand-8124", "cand-3563", "cand-3401"], relation_candidate=True,
    ocr_corrections=[{"source_line": 12, "ocr": "Venice. -", "print": "Venice."}])
add_statement(
    "st-chp15-p361-enlightenment-different-patronage-partial", BODY, "cand-0976", "cand-10430",
    "enlightenment_reached_venice_through_publishers_travellers_and_men_of_letters_suggested_new_patronage_partial", 13, 14,
    "Haskell says a few distinguished men showed that the Enlightenment, as it reached Venice through publishers, travellers and men of letters such as Lodoli and Algarotti, suggested new possibilities for a different kind of patronage.",
    qualification="The sentence ends mid-thought at ‘though it is’ and continues at p.362 L17; its qualification is not supplied here.",
    mentioned=["cand-0976", "cand-2068", "cand-3562", "cand-1411", "cand-0050", "cand-10430"],
    cross_reference_segments=[BODY_NEXT], cross_reference_text="P.361 L14 ends ‘though it is’; continuation begins at p.362 L17.",
    cross_reference_text_pending=True)

# Footnote 1 is attached at the end of the first paragraph; note 2 is attached to the Mariette/Zanetti passage.
add_statement(
    "st-chp15-p361-note1-moschini-1810", NOTES, "cand-1709", "cand-10425",
    "cites_moschini_1810_for_state_of_venetian_painting", 8, 8,
    "P.361 note 1 cites G. A. Moschini (1810) for a vivid account of the state of Venetian painting during the last quarter of the century.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The title and page locator are not supplied; Moschini’s work was not independently consulted.",
    mentioned=["cand-1709", "cand-10425"], cited_source_independently_consulted=False,
    **footnote(1, 8, ["st-chp15-p361-flowering-nearly-ended-1764"], 9))
add_statement(
    "st-chp15-p361-note2-mariette-letter", NOTES, "cand-1547", "cand-10426",
    "cites_letter_to_temanza_15_april_1768_published_by_muntz_1890", 9, 9,
    "P.361 note 2 cites a letter from Mariette to Temanza dated 15 April 1768, published by E. Müntz in 1890, page 116.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="E. Müntz is preserved in the source form without expanding the initials. The letter and cited publication were not independently consulted.",
    mentioned=["cand-1547", "cand-2546", "cand-10424", "cand-10426"], cited_source_independently_consulted=False,
    **footnote(2, 9, ["st-chp15-p361-mariette-assumed-zanetti-pictures-leaving-venice"], 12))

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p361-")}
expected_statement_count = 27
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.361 statements, got {len(new_statement_ids)}")

coverage_by_id[INTRO_HEADING].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "L1-1",
    "note": "Generated Markdown filename heading only; not printed book content and contains no claim or entity mention.",
})
coverage_by_id[CHAPTER_HEADING].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-5",
    "note": "no_semantic_content: printed p.361 chapter title and chapter heading checked against CHP-15.pdf physical p.1; no semantic content to migrate.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L7-9",
    "note": "Printed p.361 notes 1–2 read against CHP-15.pdf physical p.1. Both citation trails are recorded; note 1 links to the first paragraph, note 2 links to the Mariette/Zanetti passage. Cited works were not independently consulted.",
})
coverage_by_id[SECTION_HEADING].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "L1-1",
    "note": "Generated Markdown filename heading only; not printed book content and contains no claim or entity mention.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L3-14",
    "note": "Printed p.361, CHP-15.pdf physical p.1, read and semantically migrated. Covers the Farsetti section heading and p.361 text through the unfinished sentence ending ‘though it is’; continuation is p.362 L17 in the next segment. Footnotes 1–2 are migrated in the chapter-intro note segment. S2-only print/OCR corrections recorded; S0 unchanged.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": {INTRO_FILE: INTRO_SHA, BODY_FILE: BODY_SHA},
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (INTRO_HEADING, CHAPTER_HEADING, NOTES, SECTION_HEADING, BODY)},
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
