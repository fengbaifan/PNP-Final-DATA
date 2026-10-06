"""Controlled S2 migration for printed p.352 body and notes 1-3; dry-run by default."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BODY_PREV = "chp-14:14_CHP-14_intro:l46-53"
BODY = "chp-14:14_CHP-14_intro:l55-61"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
PLATES = "front-matter:00_05_List_of_Plates:l140-172"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p352-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.352 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    56: "The episode of The Banquet of Cleopatra gives us our first indication",
    57: "The two men took to each other at once",
    58: "The picture was The Banquet of Cleopatra and the original patron",
    59: "Two very similar versions of the composition",
    60: "the large picture itself which is in Melbourne (Plate 61b)",
    61: "Cleopatra’s gesture is correspondingly more imperious",
    182: "For the complicated history of this picture see especially Levey",
    183: "Despite Morassi’s claim (1955, p. 21)",
    184: "Letter of 26 October 1743 published by G. Fogolari",
}.items():
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
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, NOTES, PLATES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if coverage_by_id[BODY_PREV]["disposition"] != "reviewed" or coverage_by_id[BODY_PREV]["migration_status"] != "partial":
    raise SystemExit("p.351 body segment is not in the expected partial state")
if coverage_by_id[BODY]["disposition"] != "queued":
    raise SystemExit("p.352 body segment is not queued; refusing to overwrite")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated chapter 14 notes segment is not in the expected partial state")
if coverage_by_id[PLATES]["disposition"] != "reviewed" or coverage_by_id[PLATES]["migration_status"] != "complete":
    raise SystemExit("plate-list segment is not already reviewed; refusing to assume its caption data")

new_candidates = [
    ("cand-10279", "Villa Cordellina named as the site Tiepolo was decorating in 1743", "place", 57,
     "p.352 names Villa Cordellina. Existing cand-8376 describes an unnamed Cordellina country house at Montecchio and Tiepolo’s decoration; possible cross-chapter identity is left for S3 rather than merged here."),
    ("cand-10280", "Giambattista Tiepolo’s letter to Francesco Algarotti, 26 October 1743 (Fogolari 1942, p.34)", "archive", 184,
     "The body and note identify the writer, recipient, date, and secondary publication locator; the letter itself was not consulted."),
    ("cand-10281", "Levey, 1955, pp.193–203 (citation in p.352 note 1)", "archive", 182,
     "Short citation as printed by Haskell. The local bibliography entry is to be checked during the separate S2 bibliography pass; cited pages were not independently consulted."),
    ("cand-10283", "Palazzo Clerici, Milan (site named in p.352 note 2)", "place", 183,
     "Named as the site where Tiepolo may have been painting in 1737. No building history or independent identity is added here."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES if source_line >= 168 else BODY}#L{source_line}",
    })
    candidate_by_id[cid] = candidates[-1]

segment_bounds = {BODY: (55, 61), NOTES: (168, 220)}
segment_offsets = {}
for segment_id, (line_start, line_end) in segment_bounds.items():
    offset = 0
    for number in range(line_start, line_end + 1):
        segment_offsets[(segment_id, number)] = offset
        offset += len(source_lines[number - 1]) + (1 if number < line_end else 0)
occupied_same_candidate = set()
mention_counter = 1


def _add_mention(segment_id, candidate_id, surface, number, pos, note=""):
    global mention_counter
    start = segment_offsets[(segment_id, number)] + pos
    end = start + len(surface)
    if any(seg == segment_id and cid == candidate_id and s == start and e == end
           for seg, cid, s, e in occupied_same_candidate):
        return
    mention_id = f"m-chp14-p352-{mention_counter:04d}"
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    row = {"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
           "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note}
    mentions.append(row)
    mention_by_id[mention_id] = row
    occupied_same_candidate.add((segment_id, candidate_id, start, end))
    mention_counter += 1


def add_surface(segment_id, candidate_id, surface, line_numbers, note=""):
    matched = False
    for number in line_numbers:
        line = source_lines[number - 1]
        search_from = 0
        while True:
            pos = line.find(surface, search_from)
            if pos < 0:
                break
            matched = True
            _add_mention(segment_id, candidate_id, surface, number, pos, note)
            search_from = pos + 1
    if not matched:
        raise SystemExit(f"surface not found in requested lines: {segment_id} {surface!r} {line_numbers}")


def add_surface_occurrence(segment_id, candidate_id, surface, line_number, occurrence=0, note=""):
    line = source_lines[line_number - 1]
    positions = []
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            break
        positions.append(pos)
        search_from = pos + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface occurrence not found: L{line_number} {surface!r} #{occurrence}")
    _add_mention(segment_id, candidate_id, surface, line_number, positions[occurrence], note)


def add_pronoun_occurrence(segment_id, candidate_id, form, line_number, occurrence=0, note="Coreference resolved from the immediate passage context."):
    matches = list(re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", source_lines[line_number - 1]))
    if occurrence >= len(matches):
        raise SystemExit(f"pronoun occurrence not found: L{line_number} {form!r} #{occurrence}")
    _add_mention(segment_id, candidate_id, form, line_number, matches[occurrence].start(), note)


# Reuse the already reviewed caption objects for plates 61a and 61b.
for item in [
    ("Tiepolo", "cand-2577", [56, 57, 58, 59, 60]),
    ("King", "cand-0151", [56]),
    ("Venice", "cand-2719", [56, 57]),
    ("Dresden", "cand-0947", [56, 57, 58]),
    ("The Banquet of Cleopatra", "cand-2577", [56, 58]),
    ("original series", "cand-10273", [56]),
    ("gallery", "cand-9091", [56]),
    ("pittore di macchia e spiritoso", "cand-10272", [56]),
    ("Briihl", "cand-0458", [57, 58], "The printed p.352 image reads Brühl; S0 OCR retained unchanged."),
    ("Villa Cordellina", "cand-10279", [57]),
    ("Consul Smith", "cand-2440", [58]),
    ("large picture", "cand-4101", [58, 60]),
    ("modello", "cand-4100", [59]),
    ("Musée Cognacq-", "cand-3659", [59], "OCR line break; print reads Musée Cognacq-Jay."),
    ("Jay", "cand-3659", [60], "OCR begins this wrapped museum name with a stray apostrophe; print reads Musée Cognacq-Jay."),
    ("Paris", "cand-3955", [60]),
    ("Melbourne", "cand-3937", [60]),
    ("Plate 61a", "cand-4100", [60]),
    ("Plate 61b", "cand-4101", [60]),
    ("the sketch", "cand-4100", [60]),
    ("Cleopatra", "cand-4157", [61]),
    ("Levey, 1955", "cand-10281", [182]),
    ("pp. 193-203", "cand-10281", [182]),
    ("Haskell, 1958", "cand-9559", [182]),
    ("pp. 212-3", "cand-9559", [182]),
    ("Morassi", "cand-8257", [183]),
    ("Palazzo Clerici", "cand-10283", [183]),
    ("Milan", "cand-3418", [183]),
    ("Newtonianismo", "cand-10258", [183]),
    ("Tiepolo", "cand-2577", [183, 184]),
    ("Algarotti", "cand-0052", [183, 184]),
    ("Letter of 26 October 1743", "cand-10280", [184]),
    ("G. Fogolari, 1942, p. 34", "cand-8381", [184]),
]:
    surface, cid, lines, *note = item
    segment_id = NOTES if lines[0] >= 168 else BODY
    add_surface(segment_id, cid, surface, lines, note=note[0] if note else "")

# The line's final Algarotti mention is specifically indexed with Count Brühl;
# earlier Algarotti mentions belong to the same person but have different index context.
add_surface(BODY, "cand-0052", "Algarotti", [56])
add_surface_occurrence(BODY, "cand-0052", "Algarotti", 57, 0)
add_surface_occurrence(BODY, "cand-0052", "Algarotti", 57, 1)
add_surface_occurrence(BODY, "cand-0045", "Algarotti", 57, 2)

# Resolve page-local pronouns carefully rather than assigning every token to one person.
for cid, form, line, occurrence in [
    ("cand-0054", "him", 56, 0),
    ("cand-0054", "his", 56, 0),
    ("cand-0052", "his", 56, 1),
    ("cand-0071", "he", 56, 0),
    ("cand-0071", "his", 56, 2),
    ("cand-0071", "he", 56, 1),
    ("cand-0052", "his", 56, 3),
    ("cand-0052", "he", 56, 2),
    ("cand-2577", "his", 56, 4),
    ("cand-2577", "he", 56, 3),
    ("cand-0052", "his", 57, 0),
    ("cand-0052", "himself", 57, 0),
    ("cand-0052", "he", 57, 0),
    ("cand-0052", "he", 57, 1),
    ("cand-2577", "him", 57, 0),
    ("cand-2577", "he", 57, 2),
    ("cand-2577", "he", 57, 3),
    ("cand-0052", "him", 57, 1),
    ("cand-0052", "he", 58, 0),
    ("cand-2440", "his", 58, 0),
]:
    add_pronoun_occurrence(BODY, cid, form, line, occurrence)
add_surface(BODY, "cand-0052", "the two men", [56, 57])
add_surface(BODY, "cand-2577", "the artist", [56])


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:90]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 352,
        "pdf_physical_page": 6, "claim": claim, "speaker": "Haskell",
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start, end = qualifiers["source_line_start"], qualifiers["source_line_end"]
    bounds = (55, 61) if segment_id == BODY else (168, 220)
    if not (bounds[0] <= start <= end <= bounds[1]):
        raise SystemExit(f"statement span escapes source segment: {statement_id}")
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers, "original_quote": original_quote,
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


def add_note_statement(statement_id, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    row = {
        "statement_id": statement_id, "segment_id": NOTES,
        "subject_candidate_id": None, "object_candidate_id": None,
        "predicate": "bibliographic_note", "qualifiers": qualifiers,
        "original_quote": original_quote, "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


link1 = {"footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L182",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p352-note1-picture-history"]}
link2 = {"footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L183",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p352-note2-prior-contact"]}
link3 = {"footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L184",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": ["st-chp14-p352-note3-tiepolo-letter"]}

add_statement("st-chp14-p352-banquet-ordered-for-king", BODY, "cand-0054", "cand-4101", "ordered_painting_for_king",
    q(56, 56, "The page completes the p.351 sentence by identifying the painting as a Tiepolo work outside the original series, ordered by Algarotti for the King on his own initiative.",
      "authorial narrative", "Completes the p.351 L53 sentence. Plate 61b is the separate large Melbourne picture in the already-reviewed plate list; keep it distinct from the Cognacq-Jay modello and from cand-9162 pending S3.",
      ["cand-0054", "cand-2577", "cand-4101", "cand-0151", "cand-10273"],
      candidate_identity_questions=[{"candidate_id": "cand-9162", "question": "Potential cross-chapter identity with the Melbourne Banquet version; keep distinct until S3 identity alignment."}],
      relation_candidate=True, cross_reference_segments=[BODY_PREV, PLATES],
      cross_reference_text="closes p.351 L53 and connects the text’s Plate 61b reference to the reviewed plate-list object"),
    quote(56, 56, "by Tiepolo which did not form part of the original series, but which was ordered by him for the King on his own initiative."))
add_statement("st-chp14-p352-first-indication-of-relations", BODY, "cand-0052", "cand-2577", "episode_indicates_relations_between_algarotti_and_tiepolo",
    q(56, 56, "Haskell presents the Banquet of Cleopatra episode as the first indication of the nature of the relations between Algarotti and Tiepolo.",
      "authorial interpretation", "This is Haskell’s framing of the episode, not an independent claim about the relationship’s full history.",
      ["cand-0052", "cand-2577", "cand-4101", "cand-9559"],
      cross_reference_segments=[PLATES], cross_reference_text="the captioned 61a and 61b objects are recorded separately in the plate-list segment",
      **link1),
    quote(56, 56, "The episode of The Banquet of Cleopatra gives us our first indication as to the nature of the relations between Algarotti and Tiepolo,1"))
add_statement("st-chp14-p352-no-evidence-prior-venice-contact", BODY, "cand-0052", None, "no_evidence_of_contact_during_1737_venice_stay",
    q(56, 56, "Haskell says there was no evidence that Algarotti and Tiepolo had been in contact during Algarotti’s previous Venice stay in 1737.",
      "authorial evidence qualification", "The OCR reads ‘1757?’; the printed page reads 1737 with footnote marker 2. This statement is limited to the Venice stay and preserves ‘no evidence’ rather than asserting no contact occurred.",
      ["cand-0052", "cand-2577", "cand-2719"],
      ocr_corrections=[{"source_line": 56, "ocr": "1757?", "print": "1737.²", "basis": "CHP-14.pdf physical page 6."}],
      cross_reference_segments=["chp-14:14_CHP-14_intro:l35-44", NOTES],
      cross_reference_text="p.350 likewise limits the absence of evidence to the Venice visit; note 2 discusses a possible Milan meeting, without evidence of contact before 1743",
      **link2),
    quote(56, 56, "for we have seen that there is no evidence that the two men had been in contact at all during his previous stay in Venice in 1757?"))
add_statement("st-chp14-p352-tiepolo-appraisal-and-reservation", BODY, "cand-0071", "cand-2577", "referred_to_tiepolo_without_special_distinction_in_plan",
    q(56, 56, "When Algarotti drew up the gallery projects, he described Tiepolo as ‘pittore di macchia e spiritoso’ but did not suggest that he was remarkable.",
      "authorial report of proposal and appraisal", "The description is attributed to Algarotti through Haskell; it does not establish a formal movement affiliation or negate later recognition.",
      ["cand-0071", "cand-2577", "cand-10272", "cand-9091"]),
    quote(56, 56, "When he drew up his projects for the royal gallery he referred to Tiepolo as ‘pittore di macchia e spiritoso’ but did not suggest that he was in any way remarkable."))
add_statement("st-chp14-p352-contact-and-purchase-advice", BODY, "cand-0052", "cand-2577", "contacted_and_sought_advice_about_dresden_pictures",
    q(56, 56, "Within a few days of arriving in Venice, Algarotti contacted Tiepolo and asked his advice about pictures to buy for the Dresden gallery.",
      "authorial narrative", "The page reports contact and advice-seeking; it does not identify which pictures were purchased as a result of this conversation.",
      ["cand-0052", "cand-2577", "cand-2719", "cand-0947", "cand-9091"], relation_candidate=True),
    quote(56, 56, "However, within a few days of his arrival in Venice he was in touch with the artist and asking his advice about the pictures to be bought for the Dresden gallery."))
add_statement("st-chp14-p352-tiepolo-recognition", BODY, "cand-2577", None, "described_as_greatest_painter_in_venice",
    q(56, 56, "Haskell says Tiepolo was then unanimously recognized as Venice’s greatest painter and had been so for perceptive critics for several years.",
      "authorial assessment", "This is Haskell’s report of contemporary critical recognition, not an independently measured ranking.",
      ["cand-2577", "cand-2719"]),
    quote(56, 56, "Tiepolo was by now unanimously recognised as being the greatest painter in Venice, as he had been to perceptive critics for a number of years."))
add_statement("st-chp14-p352-algarotti-position-and-mission", BODY, "cand-0052", None, "position_changed_to_official_buying_mission",
    q(57, 57, "Haskell contrasts Algarotti’s earlier status as a brilliant young dilettante of 25 with his changed position on an official mission to buy pictures for a leading European collector.",
      "authorial biographical interpretation", "The comparison is Haskell’s characterization; the collector is not named in this sentence.",
      ["cand-0052", "cand-0151"]),
    quote(57, 57, "Algarotti’s own position had considerably changed since his last visit. The brilliant young dilettante of 25 now found himself on an official mission to buy pictures for the greatest of European collectors."))
add_statement("st-chp14-p352-mutual-rapport", BODY, "cand-0052", "cand-2577", "formed_immediate_mutual_rapport",
    q(57, 57, "Haskell says the two men took to each other at once.",
      "authorial narrative", "This is Haskell’s characterization of their rapport, not a quoted self-description by either man.",
      ["cand-0052", "cand-2577"], relation_candidate=True),
    quote(57, 57, "The two men took to each other at once,"))
add_statement("st-chp14-p352-friendly-letter-from-villa-cordellina", BODY, "cand-2577", "cand-10280", "wrote_friendly_letter_to_algarotti",
    q(57, 57, "In October 1743, Tiepolo wrote Algarotti an exceedingly friendly letter from Villa Cordellina, which he was then decorating; the letter says he would enjoy discussing painting with Algarotti.",
      "authorial report of correspondence", "The letter is known here through Haskell and the citation to Fogolari; it was not independently consulted. ‘He’ decorating the villa refers to Tiepolo.",
      ["cand-2577", "cand-0052", "cand-10279", "cand-10280", "cand-8381"], relation_candidate=True,
      **link3),
    quote(57, 57, "and in October Tiepolo wrote Algarotti an exceedingly friendly letter from the Villa Cordellina, which he was then decorating, saying how much he would enjoy having a discussion with him about painting.3"))
add_statement("st-chp14-p352-january-1744-proposed-picture-to-bruhl", BODY, "cand-0045", "cand-4101", "planned_to_send_tiepolo_picture_to_bruhl",
    q(57, 58, "In January 1744, Algarotti first told Count Brühl in Dresden that he planned to send a large picture by Tiepolo, already begun for another patron.",
      "authorial report", "The note preserves the planned transfer and the source’s ‘already been begun’ wording; it does not say the transfer had yet occurred.",
      ["cand-0045", "cand-0458", "cand-0947", "cand-2577", "cand-4101"], relation_candidate=True),
    quote(57, 58, "It was a few months after this, in January 1744, that Algarotti mentioned for the first time to Count Briihl in\nDresden that he was planning to send a large picture by Tiepolo that had already been begun for another patron."))
add_statement("st-chp14-p352-smith-original-patron-qualified", BODY, "cand-2440", "cand-4101", "identified_as_probable_original_patron",
    q(58, 58, "Haskell says the original patron of the Banquet was almost certainly Consul Smith, who had agreed to waive his claims, probably for financial reasons.",
      "authorial inference and qualification", "‘Almost certainly’ and ‘probably’ are both preserved; the passage does not state the precise agreement or independently identify the legal parties.",
      ["cand-2440", "cand-4101", "cand-2577"]),
    quote(58, 58, "The picture was The Banquet of Cleopatra and the original patron was almost certainly Consul Smith, who for some reason (probably financial) had agreed to waive his claims."))
add_statement("st-chp14-p352-two-versions-related-to-double-commission", BODY, "cand-4100", "cand-4101", "versions_related_to_double_commission_with_qualification",
    q(59, 59, "Haskell says the two very similar versions can with some certainty be related to the double commission.",
      "authorial attribution assessment", "‘Can with some certainty’ remains qualified; no external provenance or object identity is asserted beyond Haskell’s account.",
      ["cand-2577", "cand-4100", "cand-4101", "cand-2440", "cand-0151"], relation_candidate=True,
      cross_reference_segments=[PLATES], cross_reference_text="plate-list S2 has distinct caption candidates for the 61a and 61b versions"),
    quote(59, 59, "Two very similar versions of the composition can with some certainty be related to this double commission."))
add_statement("st-chp14-p352-modello-paris-version", BODY, "cand-4100", None, "modello_located_at_cognacq_jay_in_paris",
    q(59, 60, "The first version is a small modello, shown as now in Musée Cognacq-Jay in Paris, and Haskell says it shows Tiepolo’s original intentions.",
      "authorial description with plate cross-reference", "The OCR wraps and corrupts the museum name across lines; the reviewed plate list independently records a captioned 61a object at Musée Cognacq-Jay, Paris. ‘Now in’ is Haskell’s edition-era statement, not a present-day custody claim.",
      ["cand-4100", "cand-3659", "cand-3955", "cand-2577"],
      ocr_corrections=[{"source_line": 59, "source_line_end": 60, "ocr": "Cognacq-\n‘Jay", "print": "Cognacq-Jay", "basis": "CHP-14.pdf physical page 6."}],
      cross_reference_segments=[PLATES], cross_reference_text="Plate 61a caption is already reviewed at lines 142-143"),
    quote(59, 60, "The first is the small modello (now in the Musée Cognacq-\n‘Jay in Paris) which shows what were Tiepolo’s original intentions (Plate 61a);"))
add_statement("st-chp14-p352-large-melbourne-version", BODY, "cand-4101", None, "large_version_located_in_melbourne",
    q(60, 60, "The second version is the large picture in Melbourne, identified as Plate 61b.",
      "authorial description with plate cross-reference", "The reviewed plate list identifies 61b as the National Gallery of Victoria, Felton Bequest, Melbourne; the paragraph itself gives Melbourne only.",
      ["cand-4101", "cand-3937", "cand-2577"],
      cross_reference_segments=[PLATES], cross_reference_text="Plate 61b caption is already reviewed at lines 144-145"),
    quote(60, 60, "the second is the large picture itself which is in Melbourne (Plate 61b)."))
add_statement("st-chp14-p352-versions-painterly-quality-differ", BODY, "cand-4100", "cand-4101", "compared_for_quality_and_significant_differences",
    q(60, 60, "Haskell praises the brilliance and subtle colors of both versions while saying there are highly significant differences between them.",
      "authorial visual assessment", "OCR reads ‘fight’; the printed page reads ‘light’. The comparison is limited to Haskell’s description.",
      ["cand-4100", "cand-4101"], relation_candidate=True,
      ocr_corrections=[{"source_line": 60, "ocr": "fight", "print": "light", "basis": "CHP-14.pdf physical page 6."}]),
    quote(60, 60, "Both are painted with dazzling brilliance in fight, rich and subtle colours; yet between them there are a number of highly significant differences."))
add_statement("st-chp14-p352-sketch-outdoor-setting", BODY, "cand-4100", None, "depicted_open_garden_banquet_setting",
    q(60, 60, "In the sketch, Haskell describes a small pedimented entrance to an Italian garden, cypresses above its walls, and the banquet taking place in the open with an informal quality.",
      "authorial visual description", "This describes the sketch/modello only; do not transfer these details to the large Melbourne version.",
      ["cand-4100", "cand-2577"]),
    quote(60, 60, "In the sketch we see in the distance a small, but nobly pedimented, entrance into an Italian garden, with cypresses rising high above the walls as Tiepolo so frequently painted them. The banquet, in fact, takes place in the open, and though it is fully as sumptuous as required by the story, there is about it an air almost of informality and eager, delightful casualness."))
add_statement("st-chp14-p352-large-version-loggia-and-capital", BODY, "cand-4101", None, "depicted_enclosed_capital_setting",
    q(60, 61, "The large version is enclosed by a huge loggia, with the garden and most of the cloud-streaked sky gone; Haskell says the setting is definitely a great capital.",
      "authorial visual description", "OCR reads ‘fight’; print reads ‘light’. The page’s next comparative clause about Cleopatra and her servants continues beyond L61 onto p.353 and remains partial.",
      ["cand-4101", "cand-4157"],
      cross_reference_segments=["chp-14:14_CHP-14_intro:l63-71"], cross_reference_text="the comparative description continues on p.353"),
    quote(60, 61, "In the second version all this changes. The scene is now powerfully enclosed by a huge loggia from the balcony of\n' which the crowds look down. The garden has disappeared, and so too has most of the blue, cloud-streaked sky. We are definitely in some great capital."))
add_statement("st-chp14-p352-cleopatra-description-continuation", BODY, "cand-4101", "cand-4157", "visual_description_continues_across_page",
    q(61, 61, "The page begins to contrast Cleopatra’s more imperious, theatrical gesture and her more awestruck servants; the comparison continues on p.353.",
      "authorial visual description", "Keep this boundary statement partial: OCR ends after ‘and’ and the sentence continues on the next page; no missing comparison is inferred.",
      ["cand-4101", "cand-4157"],
      ocr_corrections=[{"source_line": 61, "ocr": "theatrical;her", "print": "theatrical; her", "basis": "CHP-14.pdf physical page 6."}],
      cross_reference_segments=["chp-14:14_CHP-14_intro:l63-71"],
      cross_reference_text="continuation of the unfinished sentence at p.353 L63"),
    quote(61, 61, "Cleopatra’s gesture is correspondingly more imperious, more theatrical;her servants more awestruck and"))

# The three p.352 notes are statement evidence, not independent verification.
note1 = {
    "source_line_start": 182, "source_line_end": 182, "printed_page": 352,
    "pdf_physical_page": 6, "claim": "Note 1 refers the reader to Levey (1955), pages 193–203, and Haskell (1958), pages 212–213, for the complicated history of the Banquet.",
    "speaker": "Haskell", "text_layer": "authorial bibliographic note",
    "qualification": "The cited works were not independently consulted. The canonical bibliography is a separate S2 source and will be reconciled in its own pass.",
    "mentioned_candidate_ids": ["cand-4100", "cand-4101", "cand-10281", "cand-9559"],
    "cross_reference_segments": [BODY], "cross_reference_text": "footnote 1 marker after the Banquet episode and relation sentence",
}
note2 = {
    "source_line_start": 183, "source_line_end": 183, "printed_page": 352,
    "pdf_physical_page": 6, "claim": "Note 2 reports Morassi’s claim that the friendship was long-standing by 1743; Haskell says it is just possible they met in Milan in 1737 while Tiepolo painted at Palazzo Clerici and Algarotti prepared Newtonianismo, but there is no real evidence of contact before 1743.",
    "speaker": "Haskell", "text_layer": "authorial bibliographic note and evidence qualification",
    "qualification": "Preserves Morassi’s claim, Haskell’s possibility language, and Haskell’s explicit lack of evidence. Do not state that a Milan meeting occurred. The note complements, rather than overrides, p.350’s narrower lack-of-evidence statement about the Venice visit.",
    "mentioned_candidate_ids": ["cand-8257", "cand-8258", "cand-0052", "cand-2577", "cand-3418", "cand-10283", "cand-10258"],
    "cross_reference_segments": [BODY, "chp-14:14_CHP-14_intro:l35-44"],
    "cross_reference_text": "footnote 2 marker after 1737 in the prior-Venice-contact sentence; p.350 confines its claim to the Venice visit",
}
note3 = {
    "source_line_start": 184, "source_line_end": 184, "printed_page": 352,
    "pdf_physical_page": 6, "claim": "Note 3 identifies the Tiepolo letter as dated 26 October 1743 and published by G. Fogolari in 1942, page 34.",
    "speaker": "Haskell", "text_layer": "authorial bibliographic note",
    "qualification": "The note is a publication locator; the manuscript/letter and cited publication were not independently consulted.",
    "mentioned_candidate_ids": ["cand-2577", "cand-0052", "cand-10280", "cand-8381"],
    "cross_reference_segments": [BODY], "cross_reference_text": "footnote 3 marker after Tiepolo’s friendly letter report",
}
add_note_statement("st-chp14-p352-note1-picture-history", note1,
    quote(182, 182, "1 For the complicated history of this picture see especially Levey, 1955, pp. 193-203, and Haskell, 1958, pp. 212-3."))
add_note_statement("st-chp14-p352-note2-prior-contact", note2,
    quote(183, 183, "2 Despite Morassi’s claim (1955, p. 21) that by 1743 ‘the friendship between them was of long standing’. It is in fact just possible that they may have met in Milan in 1737 when Tiepolo was painting in the Palazzo Clerici and Algarotti preparing the publication of his Newtonianismo, but there is no real evidence of any contact before 1743."))
add_note_statement("st-chp14-p352-note3-tiepolo-letter", note3,
    quote(184, 184, "3 Letter of 26 October 1743 published by G. Fogolari, 1942, p. 34."))

# p.351's unfinished sentence is closed by p.352 L56; p.352 ends mid-description.
coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L46-53",
    "note": "Printed p.351 read against CHP-14.pdf physical p.5. Its L53 sentence (‘in a painting’) is completed by p.352 L56 (‘by Tiepolo…ordered by him for the King’); cross-linked to st-chp14-p352-banquet-ordered-for-king. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L56-61",
    "note": "Printed p.352 read against CHP-14.pdf physical p.6. L56 closes p.351 L53. L61 ends mid-comparison (‘her servants more awestruck and’) and continues on p.353 L63; keep partial. Print corrections are recorded in S2 qualifiers; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-184",
    "note": "Printed notes p.347-p.352 read against CHP-14.pdf physical pages 1-6. Notes 1-3 on p.352 link to the Banquet history, prior-contact evidence note, and Tiepolo’s 1743 letter. Later-page notes remain pending.",
})

# Preflight foreign keys and exact character anchors for this batch.
known_ids = set(candidate_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p352-"):
        seg = row["segment_id"]
        bounds = segment_bounds[seg]
        text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']} {row['surface_form']!r}")
        if row["candidate_id"] not in known_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p352-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in known_ids:
                raise SystemExit(f"statement mentioned candidate missing: {row['statement_id']} -> {cid}")

new_mentions = [r for r in mentions if r["mention_id"].startswith("m-chp14-p352-")]
new_statements = [r for r in statements if r["statement_id"].startswith("st-chp14-p352-")]
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
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
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
