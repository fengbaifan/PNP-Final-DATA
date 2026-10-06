"""Controlled S2 migration for printed p.357; dry-run by default."""
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
BODY_PREV = "chp-14:14_CHP-14_intro:l97-105"
BODY = "chp-14:14_CHP-14_intro:l107-116"
BODY_NEXT = "chp-14:14_CHP-14_intro:l118-124"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-chp14-p357-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.357 S2 migration")
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


source_bytes = SOURCE.read_bytes()
pdf_bytes = PDF.read_bytes()
source_hash = hashlib.sha256(source_bytes).hexdigest()
pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
if source_hash != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if pdf_hash != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    108: "prints of the palaces, churches and country houses of Genoa",
    109: "Triumph of Venice he had seen in Marco Foscarini’s palace",
    110: "Pantheon which he asked Bonomo to keep for him",
    111: "paintings by him in Dr Mead’s collection in London",
    113: "At the end of 1753 Algarotti left Germany",
    114: "Architectural capricci of the kind had long been familiar in Rome",
    115: "Nevertheless Algarotti was the first to draw up a theoretical scheme",
    116: "Letter to Bonomo from Berlin of 13 August 1750",
    201: "See letter to Girolamo Curli of 20 November 1751",
    202: "In 1748 he wrote from Potsdam to the Abate Scarselli",
    203: "Letter from Potsdam of 13 March 1751",
    204: "Letter from Berlin dated 21 November 1750 in Treviso, MSS. 1256",
    205: "For the dating before 1750 of these frescoes see Levey",
    206: "Letter to Prospero Pesci of 28 September 1759",
    207: "See Chapter 11.",
}.items():
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")
if "royal friend and master" not in source_lines[107] or "Canaletto from whom he commissioned" not in source_lines[112]:
    raise SystemExit("required p.357 context changed")

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
if (coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L169-200"):
    raise SystemExit("S2 coverage preconditions changed")
previous_statement_id = "st-chp14-p356-letter-to-acquaintances-for-supply-partial"
if previous_statement_id not in statement_by_id:
    raise SystemExit("missing p.356 open cross-page statement")
if statement_by_id[previous_statement_id]["predicate"] != "wrote_to_acquaintances_in_italy_asking_them_to_supply_partial":
    raise SystemExit("p.356 continuation was already revised")

new_candidates = [
    ("cand-10352", "Prints of Genoa palaces, churches, and country houses sought by Algarotti (p.356–357)", "work", 108,
     "Haskell reports that Algarotti asked acquaintances in Italy to supply prints of Genoese buildings; no print title, maker, or individual building is specified."),
    ("cand-10353", "Unidentified palace of Marco Foscarini where Batoni’s Triumph of Venice was seen (p.357)", "place", 109,
     "The palace is not named; retain it as a distinct setting and do not infer its identity from Marco Foscarini’s residence elsewhere."),
    ("cand-10354", "Algarotti’s proposal that Batoni paint a Cleopatra for the King, suitable for mosaic transfer (p.357)", "event", 109,
     "Haskell reports a suggestion, not a completed commission or an existing mosaic."),
    ("cand-10355", "Mira, location of the Contarini villa for Tiepolo’s Henri III fresco (p.357)", "place", 113,
     "Named as the location associated with the Contarini villa; no more precise site is supplied here."),
    ("cand-10356", "Modello of Tiepolo’s Reception of Henri III of France by the Contarini (p.357)", "work", 113,
     "Haskell says Algarotti obtained the modello of the fresco; keep it distinct from the fresco itself."),
    ("cand-10357", "Francesco Algarotti’s letter to Girolamo Curli dated 20 November 1751 (p.357 n.1)", "archive", 201,
     "Haskell cites the letter as published by A. Neri in 1885; neither the letter nor publication was independently consulted."),
    ("cand-10358", "A. Neri (citation form in p.357 n.1)", "person", 201,
     "Only initial and surname are supplied; do not identify this person with another Neri."),
    ("cand-10359", "A. Neri, 1885 (publication cited for the Curli letter; p.357 n.1)", "archive", 201,
     "Haskell gives author form and year but no title or page locator; the publication was not independently consulted."),
    ("cand-10360", "Francesco Algarotti’s 1748 letter from Potsdam to Abate Scarselli (p.357 n.2)", "archive", 202,
     "Haskell says the letter asked for details about leading Italian painters, sculptors, and architects in Rome; cited at Opere XIII, p.207."),
    ("cand-10361", "Opere XIII, p.207 (locator for the 1748 Scarselli letter; p.357 n.2)", "archive", 202,
     "Pinpoint locator cited by Haskell; the volume and letter were not independently consulted."),
    ("cand-10362", "Letter from Potsdam dated 13 March 1751 (Opere XIII, p.217; p.357 n.3)", "archive", 203,
     "Haskell cites a letter but does not name its addressee in this note; it is not independently consulted."),
    ("cand-10363", "Letter to Bonomo from Berlin dated 13 August 1750 (Campori, 1866, p.201; p.357 n.4)", "archive", 116,
     "Cited by Haskell for the Pannini Pantheon painting request; the letter and Campori publication were not independently consulted."),
    ("cand-10364", "Letter from Berlin dated 21 November 1750 (Treviso MSS. 1256; p.357 n.5)", "archive", 204,
     "The addressee is not named in the note; Haskell uses the letter within a source chain about Lazzarini paintings and observations."),
    ("cand-10365", "Fantuzzi (surname citation form in p.357 n.5)", "person", 204,
     "Only surname and a volume/page reference are supplied; identity is not resolved in S2."),
    ("cand-10366", "Fantuzzi I, p.xxxiii (citation locator in p.357 n.5)", "archive", 204,
     "Locator cited by Haskell; title and text were not independently consulted."),
    ("cand-10367", "Andrea Lazzarini, painter named in p.357 n.5", "person", 204,
     "The note names Andrea; do not merge with index candidates for Gregorio Lazzarini until the name conflict is resolved."),
    ("cand-10368", "Cincinnatus summoned from the Plough, attributed to Andrea Lazzarini in p.357 n.5", "work", 204,
     "The note reports Fantuzzi’s attribution and says the work was for Frederick; later evidence cited by Haskell suggests it was for Algarotti. Index candidate cand-1371 names Gregorio Lazzarini; identity/attribution remains unresolved."),
    ("cand-10369", "The Capture of Syracuse with the Death of Archimedes, attributed to Andrea Lazzarini in p.357 n.5", "work", 204,
     "The note reports Fantuzzi’s attribution and says the work was for Frederick; later evidence cited by Haskell suggests it was for Algarotti. Index candidate cand-1370 names Gregorio Lazzarini; identity/attribution remains unresolved."),
    ("cand-10370", "Unpublished observations on painting by Andrea Lazzarini cited in p.357 n.5", "archive", 204,
     "Haskell reports that Algarotti read and used these observations; no title, date, or repository is provided."),
    ("cand-10371", "Letters from Lazzarini, volume II, pp.174–181 (citation locator in p.357 n.5)", "archive", 204,
     "Haskell cites a later reference in these letters as evidence bearing on the works’ patron; author identity and text were not independently checked."),
    ("cand-10372", "Unidentified inventory of Francesco Algarotti cited in p.357 n.5", "archive", 204,
     "Haskell says its contents suggest the paintings were made for Algarotti rather than the King; title, date, and repository are not supplied."),
    ("cand-10373", "Byam Shaw, 1960, pp.529–530 (fresco dating locator in p.357 n.6)", "archive", 205,
     "Haskell cites the publication after ‘ibid.’; the exact title and cited pages were not independently consulted."),
    ("cand-10374", "Prospero Pesci (recipient named in p.357 n.7)", "person", 206,
     "Named as recipient of a letter; no additional identity details are supplied here."),
    ("cand-10375", "Francesco Algarotti’s letter to Prospero Pesci dated 28 September 1759 (Opere VIII, pp.89–100; p.357 n.7)", "archive", 206,
     "Haskell cites the letter for the Canaletto view and a version in Parma; neither letter nor volume was independently consulted."),
    ("cand-10376", "Parma gallery (institution not identified in p.357 n.7)", "institution", 206,
     "Haskell says a version of Canaletto’s picture, if not the original, is there; the gallery is not further identified."),
    ("cand-10377", "Palladio’s plans for the Rialto included in Joseph Smith’s earlier Palladian programme (p.357)", "work", 115,
     "Haskell reports the plans as part of Smith’s programme; the precise document, version, and scheme are not independently identified."),
    ("cand-10378", "Palazzo della Ragione in Vicenza (named in the proposed Canaletto architectural view; p.357)", "place", 114,
     "A specific Vicenza building is named; do not merge with Palazzo della Ragione in Bergamo."),
    ("cand-10379", "Unidentified Cleopatra painting proposed for Batoni and possible mosaic transfer (p.357)", "work", 109,
     "A proposed painting only; Haskell does not report that it was completed or transferred to mosaic."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    if candidate_by_id and int(cid.split("-")[1]) <= max(int(k.split("-")[1]) for k in candidate_by_id):
        raise SystemExit(f"candidate ID is not above the current maximum: {cid}")
    seg = NOTES if source_line >= 168 else BODY
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{seg}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_bounds = {BODY: (107, 116), NOTES: (168, 220)}
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
    mention_id = f"m-chp14-p357-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(pos), "end_char": str(end), "note": note,
    })
    mention_counter += 1


# P.357 body mentions, including the p.356 cross-page continuation.
add_mention(BODY, "cand-10352", "prints of the palaces, churches and country houses")
add_mention(BODY, "cand-1131", "Genoa")
add_mention(BODY, "cand-4490", "Rome")
add_mention(BODY, "cand-2719", "Venice")
add_mention(BODY, "cand-1080", "royal friend and master")
add_mention(BODY, "cand-0262", "Triumph of Venice")
add_mention(BODY, "cand-0261", "Batoni")
add_mention(BODY, "cand-1053", "Marco Foscarini")
add_mention(BODY, "cand-10353", "palace")
add_mention(BODY, "cand-10354", "should paint")
add_mention(BODY, "cand-10379", "a Cleopatra")
add_mention(BODY, "cand-1080", "the King")
add_mention(BODY, "cand-1827", "Pannini")
add_mention(BODY, "cand-1828", "Interior of the\nPantheon")
add_mention(BODY, "cand-0040", "Bonomo")
add_mention(BODY, "cand-1604", "Dr Mead")
add_mention(BODY, "cand-1422", "London")
add_mention(BODY, "cand-0498", "Canaletto")
add_mention(BODY, "cand-5529", "Germany")
add_mention(BODY, "cand-0083", "Algarotti")
add_mention(BODY, "cand-0083", "Venice")
add_mention(BODY, "cand-2572", "Tiepolo")
add_mention(BODY, "cand-2604", "The Reception of Henri III os France")
add_mention(BODY, "cand-0825", "villa of the Contarini")
add_mention(BODY, "cand-10355", "Mira")
add_mention(BODY, "cand-10356", "modello")
add_mention(BODY, "cand-0043", "Canaletto")
add_mention(BODY, "cand-8178", "Grand Canal")
add_mention(BODY, "cand-1807", "Palladio")
add_mention(BODY, "cand-9206", "the Rialto")
add_mention(BODY, "cand-1808", "Palazzo Chiericati")
add_mention(BODY, "cand-2769", "Vicenza")
add_mention(BODY, "cand-10378", "Palazzo della Ragione")
add_mention(BODY, "cand-2769", "Vicenza")
add_mention(BODY, "cand-4490", "Rome")
add_mention(BODY, "cand-1827", "Pannini")
add_mention(BODY, "cand-0498", "Canaletto")
add_mention(BODY, "cand-2440", "Consul Smith")
add_mention(BODY, "cand-1807", "Palladio")
add_mention(BODY, "cand-10377", "Palladio’s plans for the Rialto")
add_mention(BODY, "cand-0044", "Algarotti")

# Page notes, including note 4 at source line 116 within the p.357 body segment.
add_mention(BODY, "cand-10363", "13 August 1750")
add_mention(BODY, "cand-0040", "Bonomo")
add_mention(BODY, "cand-4847", "Campori")
add_mention(NOTES, "cand-10357", "20 November 1751")
add_mention(NOTES, "cand-0896", "Girolamo Curli")
add_mention(NOTES, "cand-10358", "A. Neri")
add_mention(NOTES, "cand-10359", "1885")
add_mention(NOTES, "cand-10360", "In 1748 he wrote from Potsdam")
add_mention(NOTES, "cand-2392", "Abate Scarselli")
add_mention(NOTES, "cand-3461", "Italian")
add_mention(NOTES, "cand-4490", "Rome")
add_mention(NOTES, "cand-10361", "Opere, XIII, p. 207")
add_mention(NOTES, "cand-10362", "13 March 1751")
add_mention(NOTES, "cand-10341", "Potsdam")
add_mention(NOTES, "cand-10229", "Opere, XIII, p. 217")
add_mention(NOTES, "cand-10364", "Letter from Berlin dated 21 November 1750")
add_mention(NOTES, "cand-9209", "Treviso")
add_mention(NOTES, "cand-10251", "MSS. 1256")
add_mention(NOTES, "cand-10365", "Fantuzzi")
add_mention(NOTES, "cand-10366", "I, p. xxxiii")
add_mention(NOTES, "cand-10367", "Andrea Lazzarini")
add_mention(NOTES, "cand-1080", "Frederick the Great")
add_mention(NOTES, "cand-10368", "Cincinnatus summoned from the Plough")
add_mention(NOTES, "cand-10369", "The Capture of Syracuse with the Death of Archimedes")
add_mention(NOTES, "cand-10370", "unpublished observations on painting")
add_mention(NOTES, "cand-10371", "II, pp. 174-81")
add_mention(NOTES, "cand-10372", "Algarotti’s inventory")
add_mention(NOTES, "cand-10302", "Levey")
add_mention(NOTES, "cand-8432", "Byam Shaw")
add_mention(NOTES, "cand-10373", "pp. 529-30")
add_mention(NOTES, "cand-10375", "28 September 1759")
add_mention(NOTES, "cand-10374", "Prospero Pesci")
add_mention(NOTES, "cand-10266", "Opere, VHI")
add_mention(NOTES, "cand-10376", "Parma gallery")

unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")


def quote(segment_id, line_start, line_end):
    return "\n".join(source_lines[line_start - 1:line_end])


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", qualification="", mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 357, "pdf_physical_page": 11,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
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


def footnote(marker, segment_id, note_lines, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": segment_id,
        "footnote_line_range": note_lines, "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_note_statement_ids": list(statement_ids),
    }


# Close the p.356 sentence with its p.357 continuation and printed footnote 1.
previous = statement_by_id[previous_statement_id]
previous["object_candidate_id"] = "cand-10352"
previous["predicate"] = "asked_acquaintances_in_italy_to_supply_prints_of_genoese_buildings"
previous["qualifiers"].update({
    "claim": "Haskell says Algarotti wrote to acquaintances in Italy asking them to supply prints of the palaces, churches, and country houses of Genoa.",
    "qualification": "The sentence starts on p.356 L105 and closes at p.357 L108. The prints and depicted buildings are not individually identified. P.357 note 1 cites a Curli letter published by A. Neri; neither source was independently consulted.",
    "mentioned_candidate_ids": ["cand-0049", "cand-10352", "cand-1131"],
    "cross_reference_segments": [BODY, NOTES],
    "cross_reference_text": "p.357 L108 completes p.356 L105 ‘asking them to supply’ with prints of Genoa buildings; p.357 n.1 is at L201.",
    **footnote(1, NOTES, "L201", ["st-chp14-p357-note1-curli-letter"]),
})

# Body statements.
add_statement(
    "st-chp14-p357-continued-commissioning-pictures", BODY, "cand-0047", None,
    "continued_commissioning_pictures", 108, 108,
    "Haskell says that Algarotti did not stop commissioning pictures when he shifted his attention from Venice toward Rome.",
    qualification="This is a general statement; no complete list of commissions is supplied here.",
    mentioned=["cand-0047", "cand-4490", "cand-2719"])

add_statement(
    "st-chp14-p357-rome-as-exemplar-for-frederick", BODY, "cand-0047", "cand-1080",
    "turned_to_rome_as_more_suitable_exemplar_than_venice", 108, 108,
    "Haskell says Algarotti evidently considered Rome more suitable than Venice as an exemplar for his royal friend and master, despite not returning there since his short visit in 1734.",
    qualification="‘Evidently thought’ remains Haskell’s inference; no return to Rome after 1734 is not generalized beyond the wording in this passage.",
    mentioned=["cand-0047", "cand-4490", "cand-2719", "cand-1080"], relation_candidate=True,
    **footnote(2, NOTES, "L202", ["st-chp14-p357-note2-scarselli-letter"]))

add_statement(
    "st-chp14-p357-batoni-triumph-seen-at-foscarini-palace", BODY, "cand-0262", "cand-1053",
    "triumph_of_venice_seen_in_foscarini_palace", 109, 109,
    "Haskell says Batoni’s Triumph of Venice had been seen in Marco Foscarini’s palace.",
    qualification="The palace is not identified and is not merged with any other Foscarini residence.",
    mentioned=["cand-0262", "cand-1053", "cand-10353"], relation_candidate=True)

add_statement(
    "st-chp14-p357-batoni-cleopatra-proposal-for-king", BODY, "cand-0047", "cand-0261",
    "proposed_batoni_paint_cleopatra_for_the_king_for_mosaic_transfer", 109, 109,
    "Haskell reports that Algarotti suggested Batoni paint a Cleopatra suitable for transfer to mosaic and appropriate for the King.",
    qualification="This is a proposal, not proof the painting was executed or transferred into mosaic; the King is identified from context as Frederick the Great.",
    mentioned=["cand-0047", "cand-0261", "cand-10354", "cand-10379", "cand-1080"],
    relation_candidate=True, **footnote(3, NOTES, "L203", ["st-chp14-p357-note3-potsdam-letter"]))

add_statement(
    "st-chp14-p357-pannini-interior-pantheon-commission", BODY, "cand-0047", "cand-1827",
    "commissioned_pannini_interior_of_the_pantheon_for_himself", 109, 110,
    "Haskell says Algarotti commissioned Pannini to paint an Interior of the Pantheon for himself and asked Bonomo to keep it for him in his rooms, possibly for exhibition.",
    qualification="The painting is distinct from the Pantheon building. ‘His rooms’ is left as the source’s wording; the room owner and whether the work was exhibited are not resolved.",
    mentioned=["cand-0047", "cand-1827", "cand-1828", "cand-0040"], relation_candidate=True,
    **footnote(4, BODY, "L116", ["st-chp14-p357-note4-bonomo-letter"]))

add_statement(
    "st-chp14-p357-pannini-colour-and-interior-strength", BODY, "cand-1827", "cand-0498",
    "colour_judged_languid_against_canaletto_and_best_at_interiors", 111, 112,
    "Haskell reports that Algarotti had admired Pannini in Dr Mead’s London collection, but later found his colour ‘languid’ compared with Canaletto’s and thought Pannini was best as a painter of interiors.",
    text_layer="authorial report with a quoted evaluative word",
    qualification="The wording is reported by Haskell; it is not treated as independent direct consultation of a letter. The printed footnote marker after ‘interiors’ is 5; the OCR line reads 6.",
    mentioned=["cand-1827", "cand-1604", "cand-1422", "cand-0498"],
    ocr_corrections=[{"source_line": 112, "ocr": "footnote marker 6", "print": "footnote marker 5", "basis": "CHP-14.pdf physical page 11."}],
    **footnote(5, NOTES, "L204", ["st-chp14-p357-note5-letter-and-source-chain"]))

add_statement(
    "st-chp14-p357-left-germany-and-returned-to-venice", BODY, "cand-0083", "cand-2719",
    "left_germany_end_1753_arrived_venice_early_following_year", 113, 113,
    "Haskell says Algarotti left Germany at the end of 1753 and reached Venice at the beginning of the following year.",
    qualification="The passage says ‘the next year’; 1754 follows from the stated 1753 date but is not substituted into the quotation.",
    mentioned=["cand-0083", "cand-5529", "cand-2719"])

add_statement(
    "st-chp14-p357-algarotti-no-longer-official-but-active", BODY, "cand-0083", None,
    "no_longer_in_official_position_remained_close_to_painters_and_probably_collected", 113, 113,
    "Haskell says Algarotti no longer held an official position as about ten years earlier, stayed close to painters, and probably continued collecting extensively for himself.",
    qualification="The collecting claim is explicitly probable; do not convert it to certainty.",
    mentioned=["cand-0083"])

add_statement(
    "st-chp14-p357-tiepolo-reception-fresco-and-modello", BODY, "cand-0052", "cand-2604",
    "admired_tiepolo_henri_iii_fresco_and_obtained_modello", 113, 113,
    "Haskell says Algarotti first saw and deeply admired Tiepolo’s Reception of Henri III of France fresco for the Contarini villa at Mira and obtained its modello.",
    qualification="Keep the modello distinct from the fresco and retain the villa/site as stated; footnote 6 addresses dating, not independent authorship verification.",
    mentioned=["cand-0052", "cand-2604", "cand-10356", "cand-0825", "cand-10355"],
    relation_candidate=True, ocr_corrections=[{"source_line": 113, "ocr": "os France", "print": "of France", "basis": "CHP-14.pdf physical page 11."},
                                             {"source_line": 113, "ocr": "his Use", "print": "his life", "basis": "CHP-14.pdf physical page 11."}],
    **footnote(6, NOTES, "L205", ["st-chp14-p357-note6-fresco-dating"]))

add_statement(
    "st-chp14-p357-turn-to-architectural-painting-and-views", BODY, "cand-0043", None,
    "turned_in_later_decade_toward_architectural_painting_and_views", 113, 113,
    "Haskell says that during his last decade Algarotti turned increasingly toward architectural painting and views.",
    qualification="This is a broad characterization, not a dated inventory of all later purchases.",
    mentioned=["cand-0043"])

add_statement(
    "st-chp14-p357-canaletto-grand-canal-view-commission", BODY, "cand-0044", "cand-0500",
    "commissioned_canaletto_view_of_grand_canal_after_palladian_design", 113, 113,
    "Haskell says Algarotti contacted Canaletto and commissioned a view of part of the Grand Canal as Palladio might have designed it.",
    qualification="Completion and whether a surviving Parma version is the original remain uncertain; compare candidate cand-9243 at later identity alignment.",
    mentioned=["cand-0044", "cand-0500", "cand-0499", "cand-8178", "cand-1807", "cand-9243"],
    relation_candidate=True,
    candidate_identity_questions=[{"candidate_id": "cand-9243", "issue": "A prior passage names a Canaletto view of the Rialto as planned by Palladio; compare with this p.357 index candidate without presuming identity."}],
    **footnote(7, NOTES, "L206", ["st-chp14-p357-note7-pesci-letter-and-parma-version"]))

add_statement(
    "st-chp14-p357-grand-canal-view-architectural-elements", BODY, "cand-0500", "cand-9206",
    "specified_rialto_and_two_vicenza_palaces_in_projected_view", 113, 114,
    "Haskell describes a proposed view in which the Rialto followed Palladio’s scheme, Palazzo Chiericati adjoined it, and Palazzo della Ragione stood across the Canal; both palaces are located in Vicenza in the text.",
    qualification="The source describes a projected pictorial composition, not a claim that the view was completed exactly as specified.",
    mentioned=["cand-0500", "cand-9206", "cand-1808", "cand-2769", "cand-10378", "cand-8178"],
    relation_candidate=True)

add_statement(
    "st-chp14-p357-architectural-capricci-in-rome", BODY, "cand-1827", "cand-0499",
    "pannini_specialized_in_roman_architectural_capricci_canaletto_also_used_fantasy", 114, 114,
    "Haskell says architectural capricci were long familiar in Rome, Pannini specialized in them, and Canaletto had often indulged in similar fantasy.",
    qualification="This is Haskell’s comparative account; no specific Pannini or Canaletto capriccio is identified here.",
    mentioned=["cand-1827", "cand-0499", "cand-4490"])

add_statement(
    "st-chp14-p357-smith-palladian-program-and-rialto-plans", BODY, "cand-2440", "cand-10377",
    "smith_earlier_palladian_program_included_palladio_plans_for_rialto", 114, 115,
    "Haskell says Consul Smith had launched a Palladian programme years earlier that included Palladio’s plans for the Rialto.",
    qualification="The plan is kept distinct from Canaletto’s projected painting; note 8 points to chapter 11, which is not re-read as part of this page migration.",
    mentioned=["cand-2440", "cand-1807", "cand-10377", "cand-9206"], relation_candidate=True,
    **footnote(8, NOTES, "L207", ["st-chp14-p357-note8-chapter-11-reference"]))

add_statement(
    "st-chp14-p357-theoretical-scheme-for-view-commission-partial", BODY, "cand-0044", "cand-0500",
    "first_to_draw_up_theoretical_scheme_for_such_commission_partial", 115, 115,
    "Haskell calls Algarotti the first to draw up a theoretical scheme for such a commission and begins to refer to letters describing it; the sentence continues on p.358.",
    qualification="Only the clause through ‘with their description of’ is present in this source segment. The letters’ described contents are not inferred before the next page is processed.",
    mentioned=["cand-0044", "cand-0500"], relation_candidate=True,
    cross_reference_segments=[BODY_NEXT], cross_reference_text="continues after ‘his letters, with their description of’ at p.358 L120")

# Notes 1-8: preserve the citation chain and source-status distinctions.
add_statement(
    "st-chp14-p357-note1-curli-letter", NOTES, None, "cand-10357",
    "cites_curli_letter_published_by_a_neri", 201, 201,
    "P.357 note 1 points to a letter to Girolamo Curli dated 20 November 1751, published by A. Neri in 1885.",
    text_layer="authorial bibliographic note",
    qualification="The note provides no title or locator for Neri’s publication; neither the letter nor the publication was independently consulted.",
    mentioned=["cand-10357", "cand-0896", "cand-10358", "cand-10359"],
    cross_reference_segments=[BODY_PREV, BODY], cross_reference_text="cited after the completed p.356–357 sentence about obtaining Genoa building prints")

add_statement(
    "st-chp14-p357-note2-scarselli-letter", NOTES, "cand-10360", "cand-2392",
    "1748_letter_from_potsdam_requests_details_about_rome_artists", 202, 202,
    "P.357 note 2 says that in 1748 Algarotti wrote from Potsdam to Abate Scarselli asking for details about leading Italian painters, sculptors, and architects in Rome; Haskell cites Opere XIII, p.207.",
    text_layer="authorial bibliographic note",
    qualification="The letter and published locator were not independently consulted.",
    mentioned=["cand-10360", "cand-2392", "cand-10341", "cand-4490", "cand-3461", "cand-10361"],
    cross_reference_segments=[BODY], cross_reference_text="supports the account of Algarotti turning toward Rome as an exemplar")

add_statement(
    "st-chp14-p357-note3-potsdam-letter", NOTES, None, "cand-10362",
    "cites_letter_from_potsdam_13_march_1751", 203, 203,
    "P.357 note 3 cites a letter from Potsdam dated 13 March 1751 in Opere XIII, p.217.",
    text_layer="authorial bibliographic note",
    qualification="The addressee is not given in this note; letter and locator were not independently consulted.",
    mentioned=["cand-10362", "cand-10341", "cand-10229"],
    cross_reference_segments=[BODY], cross_reference_text="appears after the proposal that Batoni paint a Cleopatra for the King")

add_statement(
    "st-chp14-p357-note4-bonomo-letter", BODY, None, "cand-10363",
    "cites_bonomo_letter_from_berlin_13_august_1750", 116, 116,
    "P.357 note 4 cites a letter to Bonomo from Berlin dated 13 August 1750, published by Campori in 1866, p.201.",
    text_layer="authorial bibliographic note",
    qualification="The letter and Campori publication were not independently consulted.",
    mentioned=["cand-10363", "cand-0040", "cand-4847"],
    cross_reference_segments=[BODY], cross_reference_text="attached to Algarotti’s request that Bonomo keep Pannini’s Pantheon painting for him")

add_statement(
    "st-chp14-p357-note5-letter-and-source-chain", NOTES, None, "cand-10364",
    "cites_1750_letter_and_reports_conflicting_patron_attributions_for_lazzarini_pictures", 204, 204,
    "P.357 note 5 cites a Berlin letter dated 21 November 1750 in Treviso MSS. 1256. Through Fantuzzi I, p.xxxiii, Haskell reports the two named pictures as Andrea Lazzarini works for Frederick the Great; he then says later Lazzarini letters and Algarotti’s inventory suggest that the pictures were for Algarotti, not the King.",
    text_layer="authorial bibliographic note quoting a secondary source and then giving Haskell’s later-source inference",
    qualification="Fantuzzi and the cited letters/inventory were not independently consulted. The index lists the two titles under Gregorio Lazzarini, while this note says Andrea; retain both candidate paths as unresolved rather than reconciling them here.",
    mentioned=["cand-10364", "cand-9209", "cand-10251", "cand-10365", "cand-10366", "cand-10367", "cand-1080", "cand-10368", "cand-10369", "cand-10371", "cand-10372", "cand-1371", "cand-1370"],
    candidate_identity_questions=[{"candidate_id": "cand-1371", "issue": "Index entry assigns Cincinnatus summoned from the Plough to Gregorio Lazzarini, but p.357 n.5 names Andrea Lazzarini."},
                                 {"candidate_id": "cand-1370", "issue": "Index entry assigns The Capture of Syracuse with the Death of Archimedes to Gregorio Lazzarini, but p.357 n.5 names Andrea Lazzarini."}],
    ocr_corrections=[{"source_line": 204, "ocr": "Mar-chigian", "print": "Marchigian", "basis": "CHP-14.pdf physical page 11."}])

add_statement(
    "st-chp14-p357-note5-algarotti-read-lazzarini-observations", NOTES, "cand-0065", "cand-10370",
    "read_and_used_lazzarini_unpublished_observations_on_painting", 204, 204,
    "The p.357 note reports that Algarotti read unpublished observations on painting by Andrea Lazzarini and used them in his own work.",
    text_layer="authorial bibliographic note reporting Fantuzzi",
    qualification="The observations are untitled and not independently located or consulted; identity conflict with the index’s Gregorio Lazzarini entry remains open.",
    mentioned=["cand-0065", "cand-10367", "cand-10370"], relation_candidate=True)

add_statement(
    "st-chp14-p357-note6-fresco-dating", NOTES, None, None,
    "cites_levey_and_byam_shaw_for_fresco_dating_before_1750", 205, 205,
    "P.357 note 6 cites Levey in Burlington Magazine (1960, p.257) and Byam Shaw (1960, pp.529–530) for dating the frescoes before 1750.",
    text_layer="authorial bibliographic note",
    qualification="The cited articles/pages were not independently consulted; p.357 note 6 uses ‘ibid.’ for the periodical reference.",
    mentioned=["cand-10302", "cand-8432", "cand-10373"],
    cross_reference_segments=[BODY], cross_reference_text="supports dating of Tiepolo’s Henri III frescoes before 1750",
    ocr_corrections=[{"source_line": 205, "ocr": "i960", "print": "1960", "basis": "CHP-14.pdf physical page 11."}])

add_statement(
    "st-chp14-p357-note7-pesci-letter-and-parma-version", NOTES, "cand-10374", "cand-10375",
    "cites_pesci_letter_and_reports_possible_parma_version_of_canaletto_picture", 206, 206,
    "P.357 note 7 cites a 28 September 1759 letter to Prospero Pesci in Opere VIII, pp.89–100, and says a version of Canaletto’s picture, if not the original, is in the Parma gallery.",
    text_layer="authorial bibliographic note",
    qualification="The wording explicitly leaves open whether the Parma object is a version or the original; the letter, book, picture, and institution were not independently checked.",
    mentioned=["cand-10374", "cand-10375", "cand-10266", "cand-0499", "cand-0500", "cand-10376", "cand-3417", "cand-9243"],
    candidate_identity_questions=[{"candidate_id": "cand-9243", "issue": "The p.357 view candidate may correspond to a previously mentioned Rialto view; the note does not identify the Parma object as original or version."}])

add_statement(
    "st-chp14-p357-note8-chapter-11-reference", NOTES, None, None,
    "cross_references_chapter_11", 207, 207,
    "P.357 note 8 directs the reader to Chapter 11.",
    text_layer="authorial cross-reference",
    qualification="This is a navigation pointer only; it is not treated as independent evidence or as a formal relation.",
    cross_reference_text="See Chapter 11")

new_statements = [row for row in statements if row["statement_id"].startswith("st-chp14-p357-")]
new_statement_ids = {row["statement_id"] for row in new_statements}
for row in statements:
    if row["statement_id"].startswith("st-chp14-p357-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        if row["original_quote"] not in segment_texts[row["segment_id"]]:
            raise SystemExit(f"statement quote missing from source: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in candidate_by_id:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in candidate_by_id:
                raise SystemExit(f"mentioned candidate missing: {row['statement_id']} -> {cid}")
        for note_id in row["qualifiers"].get("footnote_note_statement_ids", []):
            if note_id not in new_statement_ids:
                raise SystemExit(f"footnote statement missing: {row['statement_id']} -> {note_id}")

for row in planned_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_texts[row["segment_id"]][start:end] != row["surface_form"]:
        raise SystemExit(f"mention anchor mismatch: {row['mention_id']} {row['surface_form']!r}")
spans_by_segment = {}
for row in planned_mentions:
    spans_by_segment.setdefault(row["segment_id"], []).append(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"], row["surface_form"]))
for seg, spans in spans_by_segment.items():
    spans.sort()
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0]:
            raise SystemExit(f"overlapping mentions in {seg}: {left[2]} / {right[2]}")
unmentioned_new_candidates = {row[0] for row in new_candidates} - {row["candidate_id"] for row in planned_mentions}
if unmentioned_new_candidates:
    raise SystemExit(f"new candidates without an S2 mention anchor: {sorted(unmentioned_new_candidates)}")

previous["object_candidate_id"] = "cand-10352"
previous["predicate"] = "asked_acquaintances_in_italy_to_supply_prints_of_genoese_buildings"
previous["qualifiers"].update({
    "claim": "Haskell says Algarotti wrote to acquaintances in Italy asking them to supply prints of the palaces, churches, and country houses of Genoa.",
    "qualification": "The sentence starts on p.356 L105 and closes at p.357 L108. The prints and depicted buildings are not individually identified. P.357 note 1 cites a Curli letter published by A. Neri; neither source was independently consulted.",
    "mentioned_candidate_ids": ["cand-0049", "cand-10352", "cand-1131"],
    "cross_reference_segments": [BODY, NOTES],
    "cross_reference_text": "p.357 L108 completes p.356 L105 ‘asking them to supply’ with prints of Genoa buildings; p.357 n.1 is at L201.",
    **footnote(1, NOTES, "L201", ["st-chp14-p357-note1-curli-letter"]),
})

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L98-105",
    "note": "Printed p.356 read against CHP-14.pdf physical p.10. L98 closes the p.355 Canaletto sentence; L105’s ‘supply’ sentence closes at p.357 L108 with Genoa prints. Notes 1–7 at L194–200 are linked; S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L108-116",
    "note": "Printed p.357 read against CHP-14.pdf physical p.11. L108 closes p.356; page footnote 4 at L116 is linked. Body L115 ends mid-sentence after ‘description of’ and continues at p.358 L120; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-207",
    "note": "Printed notes p.347–p.357 read against CHP-14.pdf physical pages 1–11. P.357 notes 1–3 and 5–8 at L201–207 are migrated; note 4 is in the p.357 body segment at L116. Later notes remain pending.",
})

print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": source_hash, "pdf_sha256": pdf_hash,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statements), "updated_statements": [previous_statement_id],
    "coverage_updates": {BODY_PREV: coverage_by_id[BODY_PREV], BODY: coverage_by_id[BODY], NOTES: coverage_by_id[NOTES]},
}, ensure_ascii=False, indent=2))

if args.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if hashlib.sha256(backup.read_bytes()).digest() != hashlib.sha256(path.read_bytes()).digest():
                raise SystemExit(f"existing backup differs from current pre-write file: {backup.name}")
        else:
            shutil.copy2(path, backup)
    mentions.extend(planned_mentions)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
