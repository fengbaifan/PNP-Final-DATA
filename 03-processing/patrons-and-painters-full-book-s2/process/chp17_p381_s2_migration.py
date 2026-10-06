"""Controlled semantic migration for chapter 17, printed p.381."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_I = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
SOURCE_II = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-17.pdf"
EXPECTED_HASHES = {
    SOURCE_I: "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4",
    SOURCE_II: "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3",
    PDF: "fa9c9a4ebc484c481d13b0afb46f96bf94fe0631c65f0b742d0b0b9d9e0b7465",
}

BODY_I = "chp-17:17_CHP-17_sec_i:l22-24"
NOTES_I = "chp-17:17_CHP-17_sec_i:l26-35"
BODY_II = "chp-17:17_CHP-17_sec_ii:l3-5"
HEADING_II = "chp-17:17_CHP-17_sec_ii:l1-1"
BACKUP_SUFFIX = ".bak-s2-chp17-p381-20261004"

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


for path, expected in EXPECTED_HASHES.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

source_i_lines = SOURCE_I.read_text(encoding="utf-8-sig").splitlines()
source_ii_lines = SOURCE_II.read_text(encoding="utf-8-sig").splitlines()
required = [
    (source_i_lines, 22, "[Page 381]"),
    (source_i_lines, 23, "huge collection of over 400 pictures"),
    (source_i_lines, 24, "Joseph and Potiphars Wife"),
    (source_i_lines, 32, "Moschini, 1806, U, p. 107"),
    (source_i_lines, 33, "V. Lazari"),
    (source_i_lines, 34, "By Bernardo Castelli"),
    (source_i_lines, 35, "Archivio Correr"),
    (source_ii_lines, 3, "The other great collector who survived the downfall of the Republic"),
    (source_ii_lines, 3, "‘The Sacrifices of the Ancients’"),
    (source_ii_lines, 3, "fatherland... . .’6"),
    (source_ii_lines, 4, "ibid.,  (5)."),
    (source_ii_lines, 5, "IO ' '"),
]
for lines, line_number, fragment in required:
    if fragment.casefold() not in lines[line_number - 1].casefold():
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

for segment_id in (BODY_I, NOTES_I, BODY_II, HEADING_II):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing coverage row: {segment_id}")
if coverage_by_id[BODY_I]["disposition"] != "queued" or coverage_by_id[BODY_I]["migration_status"] != "pending":
    raise SystemExit("p.381 Manfrin body coverage precondition changed")
if coverage_by_id[NOTES_I]["disposition"] != "reviewed" or coverage_by_id[NOTES_I]["migration_status"] != "partial":
    raise SystemExit("p.380–381 note segment coverage precondition changed")
if coverage_by_id[NOTES_I]["source_line_ranges"] != "L27-31":
    raise SystemExit("p.380 note coverage no longer ends at L31")
for segment_id in (BODY_II, HEADING_II):
    if coverage_by_id[segment_id]["disposition"] != "queued" or coverage_by_id[segment_id]["migration_status"] != "pending":
        raise SystemExit(f"p.381 Correr coverage precondition changed: {segment_id}")
if any(row.get("statement_id", "").startswith("st-chp17-p381-") for row in statements):
    raise SystemExit("p.381 statements already exist")

new_candidate_specs = [
    ("cand-10695", "Giorgione’s Tempesta", "work", BODY_I, 23,
     "A specific painting named as a treasure in the Manfrin gallery; no external identity check is made here."),
    ("cand-10696", "Bernardo Castelli (artist named in p.381 note 3)", "person", NOTES_I, 34,
     "The note names Bernardo Castelli as painter of Teodoro Correr’s portrait; the List of Plates gives Bernardino Castelli for Plate 59b. Preserve the name variation for S3."),
    ("cand-10697", "Paper titled The Sacrifices of the Ancients (read by Teodoro Correr in 1768)", "archive", BODY_II, 3,
     "An elaborate paper read by Correr to a club in 1768; the passage does not explicitly establish authorship. The note supplies related Archivio Correr material; the paper and manuscript were not independently consulted."),
    ("cand-10698", "Teodoro Correr’s 1787 letter to the Doge about the Treviso governorship (Archivio Correr 1468/10, item 5)", "archive", BODY_II, 3,
     "The letter is quoted by Haskell and the page note gives an archival locator whose shelfmark is omitted in S0 OCR; the manuscript was not consulted."),
    ("cand-10699", "Archivio Correr, Biblioteca Correr, 1468/10", "archive", NOTES_I, 35,
     "P.381 notes 4–5 cite items 6a–d and 5 in this archival unit. The printed shelfmark is 1468/10; the OCR drops it."),
    ("cand-10700", "Moschini, 1806, volume II, p.107 (p.381 note 1 citation)", "archive", NOTES_I, 32,
     "The printed note spells the author Moschini. P.380 note 4 spells a citation at the same volume and page Meschini; retain both source forms pending identity review."),
    ("cand-10701", "Moschini, 1810 (p.381 note 1 citation)", "archive", NOTES_I, 32,
     "The title and page are not supplied; this is a source citation locator, not an independently consulted publication."),
    ("cand-10702", "V. Lazari (author cited for Teodoro Correr and his collections)", "person", NOTES_I, 33,
     "The note gives only an initial and surname; no fuller identity or specific work is inferred."),
    ("cand-10703", "G. Mariacher (author of the 1957 Museo Correr catalogue)", "person", NOTES_I, 33,
     "The note gives an initial and surname; identity is not externally aligned."),
    ("cand-10704", "G. Mariacher, 1957, Museo Correr catalogue through the Renaissance", "archive", NOTES_I, 33,
     "Bibliographic reference named in Haskell’s note; the catalogue was not independently consulted."),
    ("cand-10705", "T. Pignatti, 1960, Museo Correr catalogue of seventeenth- and eighteenth-century holdings (p.62 cited)", "archive", NOTES_I, 33,
     "The note identifies the catalogue scope and note 3 cites p.62 for the Castelli portrait; title and catalogue were not independently checked."),
    ("cand-10706", "Minerva (named as a subject of the friends’ odes and sonnets)", "person", BODY_II, 3,
     "Mythological figure named in the literary subject of Correr’s friends’ poems; type and identity remain open for S3."),
]
if any(spec[0] in candidate_by_id for spec in new_candidate_specs):
    raise SystemExit("one or more p.381 candidate IDs already exist")
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
    BODY_I: {number: source_i_lines[number - 1] for number in range(22, 25)},
    NOTES_I: {number: source_i_lines[number - 1] for number in range(26, 36)},
    BODY_II: {number: source_ii_lines[number - 1] for number in range(3, 6)},
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


def add_mention(candidate_id, surface, segment_id, line_start, note="", occurrence=0):
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    text = segment_lines[segment_id][line_start]
    positions = []
    cursor = 0
    while True:
        position = text.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface not found in {segment_id} L{line_start}: {surface!r} #{occurrence + 1}")
    start = line_offsets[segment_id][line_start] + positions[occurrence]
    end = start + len(surface)
    occupied = [(int(row["start_char"]), int(row["end_char"])) for row in mentions + planned_mentions if row["segment_id"] == segment_id]
    for other_start, other_end in occupied:
        if start < other_end and other_start < end:
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not nested or (start, end) == (other_start, other_end):
                raise SystemExit(f"overlapping mention span: {surface!r} at {segment_id} L{line_start}")
    planned_mentions.append({
        "mention_id": f"m-chp17-p381-{len(planned_mentions) + 1:04d}",
        "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# Manfrin’s p.381 gallery and patronage account.
add_mention("cand-1512", "Manfrin’s", BODY_I, 23, "Collection owner; the possessive is retained as the source form.")
add_mention("cand-1513", "huge collection of over 400 pictures", BODY_I, 23, "Manfrin collection; the count is Haskell’s report.")
add_mention("cand-0262", "Batoni", BODY_I, 23, "Pompeo Batoni, from the index entry covering p.381.")
add_mention("cand-4085", "Triumph of Venice", BODY_I, 23, "Specific painting already represented by the accepted-work candidate and named in the plate list.")
add_mention("cand-1053", "Marco Foscarini", BODY_I, 23, "Patron named in the sentence; the index entry covers p.381.")
add_mention("cand-1513", "the gallery", BODY_I, 23, "The Manfrin collection/gallery; physical-space versus collection scope remains contextual.")
add_mention("cand-2719", "Venice", BODY_I, 23, "City in which the gallery is described as one of the finest.")
add_mention("cand-2719", "the city", BODY_I, 23, "Anaphoric reference to Venice.")
add_mention("cand-1189", "Giorgione", BODY_I, 23, "Painter indexed with a p.381 Tempest subentry.")
add_mention("cand-10695", "Tempesta", BODY_I, 23, "Specific painting named among the gallery’s treasures.")
add_mention("cand-1512", "Manfrin’s", BODY_I, 24, "Subject of the account of his patronage ventures.")
add_mention("cand-1514", "competitions", BODY_I, 24, "Index subentry identifies Manfrin’s competitions for painters.")

# Notes 1–4 on p.381 are printed in the section-I note block.
add_mention("cand-1709", "Moschini", NOTES_I, 32, "Printed author form; keep distinct from p.380’s Meschini spelling until S3.")
add_mention("cand-10700", "Moschini, 1806, U, p. 107", NOTES_I, 32, "Exact OCR citation span; the page image reads volume II.")
add_mention("cand-10701", "the same author, 1810", NOTES_I, 32, "Citation locator by anaphora to Moschini; title and page are absent.")
add_mention("cand-0857", "Correr", NOTES_I, 33, "Teodoro Correr, for whom the note points to literature on his collections.")
add_mention("cand-0858", "his collections", NOTES_I, 33, "Teodoro Correr’s collections; use the index subentry for that topic.")
add_mention("cand-10702", "V. Lazari", NOTES_I, 33, "Author form exactly as printed/transcribed; identity unresolved.")
add_mention("cand-3661", "the museum", NOTES_I, 33, "Museo Correr, distinct from Biblioteca Correr.")
add_mention("cand-10703", "G. Mariacher", NOTES_I, 33, "Catalogue author named in the note.")
add_mention("cand-10704", "G. Mariacher, 1957", NOTES_I, 33, "Bibliographic locator for the catalogue through the Renaissance.")
add_mention("cand-3578", "the Renaissance", NOTES_I, 33, "Catalogue’s stated chronological coverage.")
add_mention("cand-9891", "T. Pignatti", NOTES_I, 33, "Author mention; existing open Pignatti candidate reused pending identity review.")
add_mention("cand-10705", "T. Pignatti, i960", NOTES_I, 33, "Exact OCR citation span; page image reads 1960.")
add_mention("cand-10696", "Bernardo Castelli", NOTES_I, 34, "P.381 note 3 artist form; Plate 59b caption uses Bernardino Castelli.")
add_mention("cand-9891", "Pignatti", NOTES_I, 34, "Author in the p.62 citation; source identity remains for S3.")
add_mention("cand-10705", "Pignatti, i960, p. 62", NOTES_I, 34, "Exact OCR citation span; page image reads 1960.")
add_mention("cand-8262", "Biblioteca Correr", NOTES_I, 35, "Repository named in the p.381 note.")
add_mention("cand-10699", "Archivio Correr", NOTES_I, 35, "The printed locator includes shelfmark 1468/10, omitted by S0 OCR.")
add_mention("cand-10699", "6 a-d", NOTES_I, 35, "Item range in the archival locator.")

# Teodoro Correr’s p.381 account and the page-5 note continuation.
add_mention("cand-8572", "the Republic", BODY_II, 3, "Political entity in the Venetian context, distinguished from the city; identity remains in the S3 alignment stage.")
add_mention("cand-0857", "Teodoro Correr", BODY_II, 3, "Index candidate covering printed pp.381–383.")
add_mention("cand-1512", "Manfrin", BODY_II, 3, "Comparator for Correr’s character and interests.")
add_mention("cand-4007", "portrait", BODY_II, 3, "The text points to Plate 59b, the already represented Teodoro Correr portrait.")
add_mention("cand-4007", "Plate 59b", BODY_II, 3, "Cross-reference to the portrait identified in the List of Plates.")
add_mention("cand-10697", "The Sacrifices of the Ancients", BODY_II, 3, "Title of Correr’s 1768 paper as printed.")
add_mention("cand-3432", "juno", BODY_II, 3, "Exact S0 OCR form; the page image reads Juno and inserts the missing space after ‘of’.")
add_mention("cand-8195", "Ceres", BODY_II, 3, "Named subject of the friends’ poems.")
add_mention("cand-10706", "Minerva", BODY_II, 3, "Named subject of the friends’ poems.")
add_mention("cand-8110", "Council of Ten", BODY_II, 3, "Venetian governing body named in the account.")
add_mention("cand-8450", "Doge", BODY_II, 3, "Unidentified officeholder; do not infer the individual’s identity.")
add_mention("cand-9209", "Treviso", BODY_II, 3, "Place named in the governor post Correr could not accept.")
add_mention("cand-8450", "Most Serene Prince", BODY_II, 3, "Form of address to the unidentified Doge in Correr’s quoted letter.")
add_mention("cand-10699", "ibid.", BODY_II, 4, "Footnote 5 refers back to the same Archivio Correr locator as note 4.")
add_mention("cand-10698", "(5)", BODY_II, 4, "Item number for the letter’s archival locator in the printed note.")


def quote_for(segment_id, start_line, end_line):
    return "\n".join(segment_lines[segment_id][number] for number in range(start_line, end_line + 1))


def footnote(marker, note_segment, note_range, body_segment, body_range, note_ids, explanation):
    return {
        "footnote_marker": marker,
        "footnote_segment": note_segment,
        "footnote_line_range": note_range,
        "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_body_segment_id": body_segment,
        "footnote_body_line_range": body_range,
        "footnote_note_statement_ids": note_ids,
        "footnote_link_note": explanation,
    }


def make_statement(statement_id, segment_id, subject_id, object_id, predicate, start_line, end_line,
                   claim, text_layer, qualification, mentioned_ids, speaker="Haskell",
                   relation_candidate=False, extra=None, footnote_data=None, quote=None):
    physical = 3
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 381, "pdf_physical_page": physical,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": mentioned_ids,
    }
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if footnote_data:
        qualifiers.update(footnote_data)
    if extra:
        qualifiers.update(extra)
    statements.append({
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject_id, "object_candidate_id": object_id,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote or quote_for(segment_id, start_line, end_line),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md" if segment_id == BODY_II else "02-sources/02-Markdown/17_CHP-17_sec_i.md",
    })


note_statement_ids = {
    "1": ["st-chp17-p381-note1-moschini-1806", "st-chp17-p381-note1-moschini-1810"],
    "2": ["st-chp17-p381-note2-catalogue-references"],
    "3": ["st-chp17-p381-note3-castelli-portrait", "st-chp17-p381-note3-portrait-date"],
    "4": ["st-chp17-p381-note4-archival-locator"],
    "5": ["st-chp17-p381-note5-letter-locator"],
}

statements = list(statements)

# The p.381 Manfrin page.
make_statement(
    "st-chp17-p381-manfrin-collection-over400", BODY_I, "cand-1512", "cand-1513",
    "assembled_gallery_collection_with_advisers_and_own_wealth", 23, 23,
    "Haskell says Manfrin’s advisers’ expertise and his own wealth assembled a gallery collection of more than 400 pictures.",
    "authorial report", "The count and causal framing are Haskell’s account, not independently verified.",
    ["cand-1512", "cand-1513"], relation_candidate=True,
)
make_statement(
    "st-chp17-p381-triumph-painted-for-foscarini", BODY_I, "cand-4085", "cand-1053",
    "painted_for", 23, 23,
    "Haskell identifies Batoni’s Triumph of Venice as a picture painted for Marco Foscarini.",
    "authorial report", "The wording ‘painted for’ is retained; this passage alone does not establish a commission contract.",
    ["cand-0262", "cand-4085", "cand-1053"], relation_candidate=True,
)
make_statement(
    "st-chp17-p381-triumph-in-manfrin-gallery", BODY_I, "cand-4085", "cand-1513",
    "included_in_collection", 23, 23,
    "The passage gives Batoni’s painting as an example among works in Manfrin’s gallery collection.",
    "authorial report", "The passage does not establish the painting’s later location or the exact acquisition history.",
    ["cand-1513", "cand-4085"], relation_candidate=True,
)
make_statement(
    "st-chp17-p381-gallery-evaluation", BODY_I, "cand-1513", "cand-2719",
    "described_as_among_finest_galleries_in_city", 23, 23,
    "Haskell evaluates the gallery as eventually among the finest in Venice.",
    "authorial evaluation", "This is Haskell’s comparative judgment, not an objective ranking.",
    ["cand-1513", "cand-2719"],
)
make_statement(
    "st-chp17-p381-gallery-tourist-attraction", BODY_I, "cand-1513", "cand-2719",
    "long_remained_chief_tourist_attraction", 23, 23,
    "Haskell says the gallery long remained one of the city’s chief tourist attractions.",
    "authorial report", "‘Long’ and ‘one of’ are retained; the passage gives no exact date range or ranking.",
    ["cand-1513", "cand-2719"],
)
make_statement(
    "st-chp17-p381-tempesta-in-gallery", BODY_I, "cand-1513", "cand-10695",
    "included_named_painting", 23, 23,
    "Haskell lists Giorgione’s Tempesta among the treasures of Manfrin’s gallery.",
    "authorial report", "The work is recorded as named in the source; no external title or attribution verification is made.",
    ["cand-1513", "cand-1189", "cand-10695"], relation_candidate=True,
)
make_statement(
    "st-chp17-p381-manfrin-patronage-evaluation", BODY_I, "cand-1512", None,
    "patronage_ventures_judged_unsatisfactory_and_vulgarian", 24, 24,
    "Haskell judges Manfrin’s patronage ventures less satisfactory and says they seemed characteristic of the vulgarian his enemies mocked, while adding that lack of available talented painters made this hardly Manfrin’s fault.",
    "authorial evaluation", "The evaluative terms and Haskell’s qualification are preserved as his judgment.",
    ["cand-1512"],
)
make_statement(
    "st-chp17-p381-manfrin-competitions", BODY_I, "cand-1512", "cand-1514",
    "organised_painters_competitions_on_self_devised_erotic_themes", 24, 24,
    "Haskell says Manfrin organised competitions in which painters produced pictures on erotic themes he devised, listing four narrative subjects.",
    "authorial report", "The listed subjects are retained as competition themes, not asserted as identified surviving paintings.",
    ["cand-1512", "cand-1514"], relation_candidate=True,
    footnote_data=footnote("1", NOTES_I, "L32-L32", BODY_I, "L24-L24", note_statement_ids["1"], "P.381 note 1 cites Moschini after the list of competition themes; the citation is recorded without assuming that the cited works were consulted."),
)
make_statement(
    "st-chp17-p381-history-painters-response", BODY_I, "cand-1512", None,
    "competitions_stirred_starved_history_painters_but_not_posterity_gratitude", 24, 24,
    "Haskell says the competitions aroused enthusiasm among history painters starved of commissions, but that this was hardly what entitled Manfrin to posterity’s gratitude.",
    "authorial evaluation", "The closing judgment is Haskell’s retrospective assessment.",
    ["cand-1512"],
)

# Teodoro Correr’s p.381 section-II account. The final clause remains open to p.382.
make_statement(
    "st-chp17-p381-correr-republic-context", BODY_II, "cand-0857", "cand-8572",
    "collector_survived_republic_downfall_and_linked_to_its_history", 3, 3,
    "Haskell introduces Teodoro Correr as a major collector who survived the Republic’s downfall and whose name remained linked to Venice’s history.",
    "authorial framing", "The Republic is treated as Venice’s political entity, distinct from the city; identity alignment remains S3 work.",
    ["cand-0857", "cand-8572"],
    footnote_data=footnote("2", NOTES_I, "L33-L33", BODY_II, "L3-L3", note_statement_ids["2"], "P.381 note 2 points readers to literature on Correr and his collections."),
)
make_statement(
    "st-chp17-p381-correr-born-1750", BODY_II, "cand-0857", None,
    "born_in_1750", 3, 3,
    "Haskell gives Teodoro Correr’s birth year as 1750.",
    "authorial report", "The date is retained as a book-reported claim; no external verification is made.",
    ["cand-0857"],
)
make_statement(
    "st-chp17-p381-correr-different-from-manfrin", BODY_II, "cand-0857", "cand-1512",
    "shared_love_of_art_but_different_life_and_character", 3, 3,
    "Haskell contrasts Correr with Manfrin, saying they shared a love of art but differed in life and character in every other way.",
    "authorial characterization", "The comparison is Haskell’s characterization, not a quantified or independently tested claim.",
    ["cand-0857", "cand-1512"],
)
make_statement(
    "st-chp17-p381-correr-portrait-traits", BODY_II, "cand-0857", "cand-4007",
    "portrait_described_as_showing_elegance_and_withdrawn_character", 3, 3,
    "Haskell says the Plate 59b portrait shows Correr as elegant and rather withdrawn.",
    "authorial interpretation of portrait", "These are Haskell’s inferences from the portrait, not externally verified personality facts.",
    ["cand-0857", "cand-4007"],
    footnote_data=footnote("3", NOTES_I, "L34-L34", BODY_II, "L3-L3", note_statement_ids["3"], "P.381 note 3 names the portrait painter and gives its painting/engraving chronology."),
)
make_statement(
    "st-chp17-p381-correr-descent", BODY_II, "cand-0857", None,
    "descended_from_one_of_oldest_venetian_aristocratic_families", 3, 3,
    "Haskell says Correr descended from one of the oldest Venetian aristocratic families.",
    "authorial report", "The family is unnamed and is not inferred from later family references.",
    ["cand-0857"],
)
make_statement(
    "st-chp17-p381-correr-paper-read-1768", BODY_II, "cand-0857", "cand-10697",
    "read_paper_to_club_in_1768", 3, 3,
    "Haskell says Correr read an elaborate and rather strained paper titled The Sacrifices of the Ancients to a club he belonged to in 1768.",
    "authorial report", "The club is not named. ‘Elaborate’ and ‘rather strained’ are Haskell’s characterization of the paper.",
    ["cand-0857", "cand-10697"], relation_candidate=True,
    footnote_data=footnote("4", NOTES_I, "L35-L35", BODY_II, "L3-L3", note_statement_ids["4"], "P.381 note 4 provides an Archivio Correr locator for the meeting material."),
)
make_statement(
    "st-chp17-p381-correr-meeting-poems", BODY_II, "cand-0857", None,
    "meeting_followed_by_fencing_and_friends_poems_on_three_deities", 3, 3,
    "Haskell says the evening ended with fencing and friends’ odes and sonnets on the sacrifices of Juno, Ceres, and Minerva.",
    "authorial report", "The individual poems and friends are unnamed; the OCR’s merged ‘ofjuno’ is read as ‘of Juno’ from the page image.",
    ["cand-0857", "cand-3432", "cand-8195", "cand-10706"],
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 3, "ocr": "ofjuno", "print": "of Juno", "basis": "CHP-17.pdf physical page 3, printed page 381."}]},
)
make_statement(
    "st-chp17-p381-correr-political-career-1776", BODY_II, "cand-0857", None,
    "began_traditional_political_career_in_1776", 3, 3,
    "Haskell says Correr began the expected traditional political career in 1776.",
    "authorial report", "The account does not identify a particular office at the start of 1776.",
    ["cand-0857"],
)
make_statement(
    "st-chp17-p381-correr-council-ten", BODY_II, "cand-0857", "cand-8110",
    "became_member_within_three_years_of_1776", 3, 3,
    "Haskell says that within three years of beginning his political career Correr was a member of the Council of Ten.",
    "authorial report", "The source gives a relative limit, not an exact membership year; no exact date is calculated.",
    ["cand-0857", "cand-8110"], relation_candidate=True,
)
make_statement(
    "st-chp17-p381-correr-became-abate", BODY_II, "cand-0857", None,
    "tired_of_politics_and_became_an_abate", 3, 3,
    "Haskell says Correr soon tired of politics and became an abate to avoid further responsibilities.",
    "authorial report", "The source gives no precise date for this change or further definition of the role.",
    ["cand-0857"],
)
make_statement(
    "st-chp17-p381-correr-letter-about-treviso-post", BODY_II, "cand-0857", "cand-10698",
    "wrote_to_doge_in_1787_unable_to_take_treviso_governorship_for_lack_of_means", 3, 3,
    "Haskell reports that in 1787 Correr wrote to the Doge that lack of means made it impossible to take up his post as governor of Treviso, and quotes the letter’s appeal.",
    "authorial report with a letter quoted by Haskell", "The Doge is unidentified; the statement preserves Haskell’s quoted wording and does not infer the addressee’s personal identity.",
    ["cand-0857", "cand-8450", "cand-9209", "cand-10698"], relation_candidate=True,
    footnote_data=footnote("5", BODY_II, "L4-L5", BODY_II, "L3-L3", note_statement_ids["5"], "The page image shows printed note 5 after the quotation; OCR reads marker 6 and omits the repeated 1468/10 shelfmark."),
    extra={"ocr_corrections": [
        {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 3, "ocr": "printed marker 6", "print": "marker 5", "basis": "CHP-17.pdf physical page 3, printed page 381."},
        {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 4, "ocr": "ibid., (5); shelfmark OCR appears as IO on L5", "print": "ibid., 1468/10 (5)", "basis": "CHP-17.pdf physical page 3, printed page 381."},
    ]},
)
make_statement(
    "st-chp17-p381-correr-repeated-applications", BODY_II, "cand-0857", None,
    "repeatedly_applied_to_escape_official_duties_across_regime_changes", 3, 3,
    "Haskell says Correr grew accustomed to the situation and made many applications to escape official duties, renewing them with each subsequent regime change.",
    "authorial summary", "This is Haskell’s account. The next sentence begins ‘However, there’ and continues on p.382; that unfinished tail remains partial.",
    ["cand-0857"],
)

# Footnote records on the p.381 page. Their cited works and manuscripts were not independently consulted.
make_statement(
    "st-chp17-p381-note1-moschini-1806", NOTES_I, "cand-1709", "cand-10700",
    "cited_for_manfrin_patronage_passage", 32, 32,
    "P.381 note 1 cites Moschini, 1806, volume II, p.107.",
    "bibliographic citation", "The cited work was not independently consulted. The printed author form differs from p.380’s Meschini citation at the same volume/page and is retained as a source discrepancy.",
    ["cand-1709", "cand-10700"],
    extra={"ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 32, "ocr": "U", "print": "II", "basis": "CHP-17.pdf physical page 3, printed page 381."}],
           "footnote_marker": "1", "footnote_body_segment_id": BODY_I, "footnote_body_line_range": "L24-L24", "footnote_body_link_status": "linked", "footnote_text_pending": False},
)
make_statement(
    "st-chp17-p381-note1-moschini-1810", NOTES_I, "cand-1709", "cand-10701",
    "additional_citation_by_same_author_for_manfrin_patronage_passage", 32, 32,
    "P.381 note 1 adds a 1810 citation by the same author.",
    "bibliographic citation", "No title or page is supplied and the work was not independently consulted.",
    ["cand-1709", "cand-10701"],
    extra={"footnote_marker": "1", "footnote_body_segment_id": BODY_I, "footnote_body_line_range": "L24-L24", "footnote_body_link_status": "linked", "footnote_text_pending": False},
)
make_statement(
    "st-chp17-p381-note2-catalogue-references", NOTES_I, "cand-3661", None,
    "bibliography_referenced_for_correr_and_collections", 33, 33,
    "P.381 note 2 directs readers to V. Lazari and to Museo Correr catalogues by G. Mariacher (1957, through the Renaissance) and T. Pignatti (1960, seventeenth and eighteenth centuries).",
    "bibliographic citation", "The note gives citation leads only; none of the cited works was independently consulted. ‘of-the’ and year OCR forms are retained unless the page image establishes a correction.",
    ["cand-0857", "cand-0858", "cand-10702", "cand-10703", "cand-10704", "cand-10705"],
    extra={"footnote_marker": "2", "footnote_body_segment_id": BODY_II, "footnote_body_line_range": "L3-L3", "footnote_body_link_status": "linked", "footnote_text_pending": False},
)
make_statement(
    "st-chp17-p381-note3-castelli-portrait", NOTES_I, "cand-4007", "cand-10696",
    "painted_by", 34, 34,
    "P.381 note 3 attributes the Plate 59b Teodoro Correr portrait to Bernardo Castelli.",
    "attribution in Haskell’s note", "The List of Plates names Bernardino Castelli for the same portrait; preserve this source-name variation for S3 rather than silently normalizing it.",
    ["cand-4007", "cand-10696"], relation_candidate=True,
    extra={"footnote_marker": "3", "footnote_body_segment_id": BODY_II, "footnote_body_line_range": "L3-L3", "footnote_body_link_status": "linked", "footnote_text_pending": False},
)
make_statement(
    "st-chp17-p381-note3-portrait-date", NOTES_I, "cand-4007", None,
    "painted_before_1795_and_engraved_in_1795", 34, 34,
    "P.381 note 3 says the portrait was painted before 1795 and engraved in 1795.",
    "bibliographic/artwork note", "The chronology is reported by Haskell’s note and is not independently checked against the print or catalogue.",
    ["cand-4007", "cand-10696", "cand-10705"],
    extra={"footnote_marker": "3", "footnote_body_segment_id": BODY_II, "footnote_body_line_range": "L3-L3", "footnote_body_link_status": "linked", "footnote_text_pending": False,
           "ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 34, "ocr": "i960", "print": "1960", "basis": "CHP-17.pdf physical page 3, printed page 381."}]},
)
make_statement(
    "st-chp17-p381-note4-archival-locator", NOTES_I, "cand-10697", "cand-10699",
    "cited_archival_locator", 35, 35,
    "P.381 note 4 gives Biblioteca Correr, Archivio Correr, 1468/10, items 6a–d, as a locator for material relating to the 1768 meeting and paper.",
    "archival citation", "The physical manuscript was not consulted. The printed shelfmark 1468/10 is absent from S0 OCR and is recorded from the page image.",
    ["cand-10697", "cand-8262", "cand-10699"], relation_candidate=True,
    extra={"footnote_marker": "4", "footnote_body_segment_id": BODY_II, "footnote_body_line_range": "L3-L3", "footnote_body_link_status": "linked", "footnote_text_pending": False,
           "ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 35, "ocr": "shelfmark omitted", "print": "1468/10", "basis": "CHP-17.pdf physical page 3, printed page 381."}]},
)
make_statement(
    "st-chp17-p381-note5-letter-locator", BODY_II, "cand-10698", "cand-10699",
    "archival_locator_for_1787_correr_letter", 4, 5,
    "P.381 note 5 refers back to Archivio Correr and gives shelfmark 1468/10, item 5, for the letter quoted in the preceding paragraph.",
    "archival citation", "The S0 OCR places ‘ibid.’ and ‘(5)’ at L4 and corrupts the shelfmark on L5; the physical page supplies 1468/10. The manuscript was not consulted.",
    ["cand-10698", "cand-10699"], relation_candidate=True,
    extra={"footnote_marker": "5", "footnote_body_segment_id": BODY_II, "footnote_body_line_range": "L3-L3", "footnote_body_link_status": "linked", "footnote_text_pending": False,
           "ocr_corrections": [{"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 3, "ocr": "marker 6", "print": "marker 5", "basis": "CHP-17.pdf physical page 3, printed page 381."},
                                {"source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 4, "ocr": "ibid., (5); shelfmark OCR appears as IO on L5", "print": "ibid., 1468/10 (5)", "basis": "CHP-17.pdf physical page 3, printed page 381."}]},
)

new_statement_ids = [row["statement_id"] for row in statements if row.get("statement_id", "").startswith("st-chp17-p381-")]
if any(row["mention_id"] in {item["mention_id"] for item in mentions} for row in planned_mentions):
    raise SystemExit("one or more p.381 mention IDs already exist")
for row in planned_mentions:
    candidate_by_id[row["candidate_id"]]
    segment = segment_texts[row["segment_id"]]
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span failed exact-source check: {row['mention_id']}")
for row in statements:
    if row.get("statement_id", "").startswith("st-chp17-p381-"):
        if row["subject_candidate_id"] and row["subject_candidate_id"] not in candidate_by_id:
            raise SystemExit(f"missing subject candidate in {row['statement_id']}")
        if row["object_candidate_id"] and row["object_candidate_id"] not in candidate_by_id:
            raise SystemExit(f"missing object candidate in {row['statement_id']}")

coverage_by_id[BODY_I].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L22-24",
    "note": "Printed p.381 Manfrin body checked against CHP-17.pdf physical page 3. The page’s Correr section begins in sec_ii and is processed there; page-image OCR corrections remain in S2, S0 is unchanged.",
})
coverage_by_id[NOTES_I].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L27-35",
    "note": "P.380 notes L27-31 remain as previously migrated; p.381 notes 1-4 at L32-35 were added and linked to sec_i L24 and sec_ii L3. The printed 1468/10 shelfmark omitted from L35 OCR is recorded in S2 from the page image. P.381 note 5 continues in sec_ii L4-5.",
})
coverage_by_id[BODY_II].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L3-5",
    "note": "Printed p.381 Teodoro Correr section and footnote 5 checked against CHP-17.pdf physical page 3. Printed note marker 5 is OCR 6; note shelfmark 1468/10 is lost/corrupt in S0. The final body phrase ‘However, there’ continues on p.382 and remains unclosed.",
})
coverage_by_id[HEADING_II].update({
    "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "L1-L1",
    "note": "Generated Markdown heading ‘# 17 CHP-17 sec ii’; it is not source-book content.",
})

if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_candidates": len(new_candidate_specs),
        "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
        "coverage_updates": {BODY_I: "complete", NOTES_I: "complete", BODY_II: "partial", HEADING_II: "excluded"},
        "next_source_segment": "chp-17:17_CHP-17_sec_ii:l7-17",
        "new_candidate_ids": [item[0] for item in new_candidate_specs],
        "new_statement_ids": new_statement_ids,
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
    shutil.copy2(path, backup)

write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, mentions + planned_mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({
    "mode": "applied", "new_candidates": len(new_candidate_specs),
    "new_mentions": len(planned_mentions), "new_statements": len(new_statement_ids),
    "backups": [path.name + BACKUP_SUFFIX for path in (candidate_path, mention_path, statement_path, coverage_path)],
    "next_source_segment": "chp-17:17_CHP-17_sec_ii:l7-17",
}, ensure_ascii=False))
