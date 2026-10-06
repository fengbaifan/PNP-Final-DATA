"""Controlled S2 migration for printed p.355; dry-run by default."""
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
BODY_PREV = "chp-14:14_CHP-14_intro:l73-83"
BODY = "chp-14:14_CHP-14_intro:l85-95"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-chp14-p355-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.355 S2 migration")
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
if SOURCE_SHA and source_hash != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if PDF_SHA and pdf_hash != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    86: "‘correctness’, though both writer and artist died",
    87: "Algarotti’s own personal dilemma",
    88: "It was this conflicting attitude that led him always to admire Tiepolo",
    89: "Although the pictures that Algarotti commissioned for the King have been lost",
    90: "Caesar and the Corsairs of Cilicia for Augustus",
    91: "Parisian-style illustrations as frontispiece",
    92: "During this stay in Venice Algarotti was adding to the family collection",
    93: "And so, although he eventually built up the collection to nearly 200 paintings",
    94: "Tiepolo stands out among all his contemporaries with some 13 paintings and 116",
    95: "Canaletto at this stage was still intensively",
    191: "According to Michelessi (see Opere, I, p. Ixii)",
    192: "Mucius Scaevola at the Altar and The Death of Darius",
    193: "For Algarotti’s collection see [G. A. Selva]",
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
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (coverage_by_id[BODY_PREV]["migration_status"] != "partial"
        or coverage_by_id[BODY]["migration_status"] != "pending"
        or coverage_by_id[NOTES]["migration_status"] != "partial"
        or coverage_by_id[NOTES]["source_line_ranges"] != "L169-190"):
    raise SystemExit("S2 coverage preconditions changed")

new_candidates = [
    ("cand-10307", "Caesar and the Corsairs of Cilicia (Piazzetta painting commissioned by Algarotti for Augustus; p.355)", "work", 90,
     "The index subentry names the picture; Haskell describes an Algarotti commission for Augustus. No present location or version is stated."),
    ("cand-10308", "Mucius Scaevola at the Altar (Piazzetta painting named in p.355 note 2)", "work", 192,
     "Title and attribution follow the book index and p.355 note 2; location is listed in the note without an explicit one-to-one pairing."),
    ("cand-10309", "The Death of Darius (Piazzetta painting named in p.355 note 2)", "work", 192,
     "Title and attribution follow the book index and p.355 note 2; location is listed in the note without an explicit one-to-one pairing."),
    ("cand-10310", "Unidentified small painting by Piazzetta owned by Algarotti during the Venice visit", "work", 90,
     "Haskell reports one small painting owned by Algarotti; no title, date, or location is supplied."),
    ("cand-10311", "Piazzetta illustration used as the frontispiece in the first edition of Newtonianismo per le Dame", "work", 91,
     "Haskell describes a sophisticated Parisian-style illustration and attributes it to Piazzetta; the image and subject are not identified here."),
    ("cand-10312", "Algarotti family collection of pictures described on p.355", "", 92,
     "The source says the collection was formed by Algarotti’s father and greatly increased by his brother, then describes Algarotti’s additions. Keep its identity distinct from p.347 collection candidates until alignment; the taxonomy has no collection type."),
    ("cand-10313", "Paintings and canvases sent by Algarotti from Venice to Dresden (new and old works, p.355)", "work", 92,
     "A group of canvases sent to Dresden; Haskell does not enumerate them or equate them with the separately described five lost royal commissions."),
    ("cand-10314", "Tiepolo paintings in Algarotti’s collection (about 13, p.355)", "work", 94,
     "Haskell gives an approximate count of 13 paintings; the individual works are not identified."),
    ("cand-10315", "Tiepolo drawings in Algarotti’s collection (about 116, p.355)", "work", 94,
     "Haskell gives an approximate count of 116 drawings; the individual works are not identified."),
    ("cand-10316", "Canaletto pictures in Dresden discussed on p.355", "work", 95,
     "Haskell says none seems to have reached the gallery through Algarotti’s agency and that Algarotti wrote of no intention to send any; this wording is not proof that no contact or transfer occurred."),
    ("cand-10317", "Palazzo Barbaro Curtis (location listed in p.355 note 2)", "place", 192,
     "Named as one of two locations following two painting titles; the note does not explicitly say ‘respectively’."),
    ("cand-10318", "Cà Rezzonico (location listed in p.355 note 2)", "place", 192,
     "Named as one of two locations following two painting titles; the note does not explicitly say ‘respectively’."),
    ("cand-10319", "Pallucchini (author cited in p.355 note 2)", "person", 192,
     "Surname only in the note; author identity and publication details remain unaligned."),
    ("cand-10320", "Pallucchini, 1956, p.41 (citation locator in p.355 note 2)", "archive", 192,
     "Short citation only; title and cited text were not independently consulted."),
    ("cand-10321", "G. A. Selva (author cited in p.355 note 3)", "person", 193,
     "Initials and surname only; identity remains unresolved."),
    ("cand-10322", "Unidentified work by G. A. Selva on Algarotti’s collection (p.355 note 3 citation)", "archive", 193,
     "The note provides no title, date, or locator; the cited work was not independently consulted."),
    ("cand-10324", "Preliminary sketches or replicas retained by Algarotti of canvases sent to Dresden", "work", 92,
     "Haskell says Algarotti kept preliminary sketches or replicas of many canvases sent to Dresden; the wording does not identify which canvases or decide whether each retained item was a sketch or replica."),
    ("cand-10325", "Unidentified works kept by Algarotti when unsuitable for the Dresden royal collection", "work", 93,
     "Haskell describes a recurring practice of retaining some acquired works not suitable for the royal collection; no individual object is named."),
    ("cand-10326", "Unidentified pictures commissioned by Algarotti for the King and reported lost on p.355", "work", 89,
     "The passage does not enumerate these pictures. Compare with, but do not automatically merge into, the five commissions listed on p.351 (cand-10273)."),
    ("cand-10327", "Algarotti’s commission to Piazzetta for Caesar and the Corsairs of Cilicia for Augustus", "event", 89,
     "An event candidate grounded in the p.355 account; linked work candidate cand-10307. No date or documentary corroboration is supplied on this page."),
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

segment_bounds = {BODY: (85, 95), NOTES: (168, 220)}
segment_offsets = {}
for segment_id, (line_start, line_end) in segment_bounds.items():
    offset = 0
    for number in range(line_start, line_end + 1):
        segment_offsets[(segment_id, number)] = offset
        offset += len(source_lines[number - 1]) + (1 if number < line_end else 0)
mention_counter = 1
planned_mentions = []


def add_mention(segment_id, candidate_id, surface, line_number, pos, note=""):
    global mention_counter
    start = segment_offsets[(segment_id, line_number)] + pos
    end = start + len(surface)
    mention_id = f"m-chp14-p355-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    row = {"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
           "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note}
    mentions.append(row)
    planned_mentions.append(row)
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
            add_mention(segment_id, candidate_id, surface, number, pos, note)
            search_from = pos + len(surface)
    if not matched:
        raise SystemExit(f"surface not found in requested lines: {segment_id} {surface!r} {line_numbers}")


def add_occurrence(segment_id, candidate_id, surface, line_number, occurrence, note=""):
    starts = []
    search_from = 0
    line = source_lines[line_number - 1]
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            break
        starts.append(pos)
        search_from = pos + 1
    if occurrence >= len(starts):
        raise SystemExit(f"surface occurrence not found: L{line_number} {surface!r} #{occurrence}")
    add_mention(segment_id, candidate_id, surface, line_number, starts[occurrence], note)


def add_pronoun(segment_id, candidate_id, form, number, occurrence=0, note="Coreference resolved from the local passage context."):
    matches = list(re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", source_lines[number - 1]))
    if occurrence >= len(matches):
        raise SystemExit(f"pronoun not found: L{number} {form!r} #{occurrence}")
    add_mention(segment_id, candidate_id, form, number, matches[occurrence].start(), note)


for surface, cid, lines in [
    ("‘correctness’", "cand-6010", [86]),
    ("Algarotti", "cand-0052", [87, 88, 89, 90, 92, 93, 94, 95]),
    ("Tiepolo", "cand-3781", [86, 88, 89, 94]),
    ("Venetian", "cand-2719", [87, 88]),
    ("Venice", "cand-2719", [89, 92]),
    ("Piazzetta", "cand-1909", [89, 90]),
    ("pictures", "cand-10326", [89]),
    ("The commission", "cand-10327", [89]),
    ("the King", "cand-0149", [89]),
    ("Caesar and the Corsairs of Cilicia", "cand-10307", [90]),
    ("Augustus", "cand-0149", [90]),
    ("one small painting", "cand-10310", [90]),
    ("Newtonianismo", "cand-10258", [90]),
    ("frontispiece", "cand-10311", [91]),
    ("family collection", "cand-10312", [92]),
    ("his father", "cand-10225", [92]),
    ("his brother", "cand-0040", [92]),
    ("preliminary sketches or replicas", "cand-10324", [92]),
    ("canvases", "cand-10313", [92]),
    ("Dresden", "cand-0947", [93, 95]),
    ("royal collection", "cand-10222", [93]),
    ("some work", "cand-10325", [93]),
    ("the collection", "cand-10312", [93]),
    ("13 paintings", "cand-10314", [94]),
    ("116 drawings", "cand-10315", [94]),
    ("Canalettos", "cand-10316", [95]),
    ("gallery", "cand-10222", [95]),
    ("Mucius Scaevola at the Altar", "cand-10308", [192]),
    ("The Death of Darius", "cand-10309", [192]),
    ("Algarotti commission", "cand-10327", [192]),
    ("Michelessi", "cand-10227", [191]),
    ("Opere", "cand-10229", [191]),
    ("Palazzo Barbaro Curtis", "cand-10317", [192]),
    ("Cà Rezzonico", "cand-10318", [192]),
    ("Pallucchini", "cand-10319", [192]),
    ("1956, p. 41", "cand-10320", [192]),
    ("G. A. Selva", "cand-10321", [193]),
    ("Algarotti’s collection", "cand-10312", [193]),
    ("Tiepolos", "cand-10314", [193]),
    ("Levey", "cand-10297", [193]),
    ("Burlington Magazine, i960, pp. 250-7", "cand-10302", [193]),
]:
    add_surface(BODY if lines[0] < 168 else NOTES, cid, surface, lines)

add_occurrence(BODY, "cand-0498", "Canaletto", 95, 0)
add_occurrence(BODY, "cand-0498", "Canaletto", 95, 2)

for cid, form, number, occurrence in [
    ("cand-0052", "his", 87, 0), ("cand-0052", "his", 87, 1),
    ("cand-0052", "he", 88, 0), ("cand-0052", "he", 88, 1),
    ("cand-0052", "him", 88, 0), ("cand-3781", "him", 88, 1),
    ("cand-3781", "his", 88, 0), ("cand-0052", "he", 89, 0),
    ("cand-0052", "his", 89, 0), ("cand-1909", "his", 89, 1),
    ("cand-1909", "his", 89, 2), ("cand-1909", "his", 90, 0),
    ("cand-1909", "his", 90, 1), ("cand-0052", "he", 90, 0),
    ("cand-1909", "him", 90, 0), ("cand-1909", "his", 90, 2),
    ("cand-0052", "He", 92, 0), ("cand-0052", "he", 92, 0),
    ("cand-0052", "he", 93, 0), ("cand-0052", "he", 93, 1),
    ("cand-0052", "himself", 93, 0), ("cand-0052", "His", 93, 0),
    ("cand-0052", "he", 93, 2), ("cand-0052", "his", 93, 0),
    ("cand-0052", "his", 93, 1), ("cand-3781", "his", 94, 0),
    ("cand-0052", "his", 95, 0), ("cand-0052", "he", 95, 0),
]:
    add_pronoun(BODY, cid, form, number, occurrence)


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:100]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 355,
        "pdf_physical_page": 9, "claim": claim, "speaker": "Haskell",
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start, end = qualifiers["source_line_start"], qualifiers["source_line_end"]
    bounds = segment_bounds[segment_id]
    if not (bounds[0] <= start <= end <= bounds[1]):
        raise SystemExit(f"statement span escapes segment: {statement_id}")
    row = {"statement_id": statement_id, "segment_id": segment_id,
           "subject_candidate_id": subject, "object_candidate_id": obj,
           "predicate": predicate, "qualifiers": qualifiers,
           "original_quote": original_quote, "origin": "book", "source_file": SOURCE_FILE}
    statements.append(row)
    statement_by_id[statement_id] = row


def add_note_statement(statement_id, qualifiers, original_quote):
    add_statement(statement_id, NOTES, None, None, "bibliographic_note", qualifiers, original_quote)


# The p.354 fragment becomes readable as a complete sentence with this p.355 continuation.
prev_statement = statement_by_id.get("st-chp14-p354-reconcile-tiepolo-vision-with-neo-classical-demands")
if not prev_statement:
    raise SystemExit("p.354 continuation statement missing")
prev_statement["qualifiers"]["claim"] = "Haskell says Algarotti was constantly trying to reconcile his vision of Tiepolo with neo-classical correctness; both writer and artist died before the controversy reached a critical stage."
prev_statement["qualifiers"]["qualification"] = "The quoted phrase begins on p.354 L83 and is completed on p.355 L86; the continuation is recorded in st-chp14-p355-correctness-and-dilemma."
prev_statement["qualifiers"]["cross_reference_segments"] = [BODY]
prev_statement["qualifiers"]["cross_reference_text"] = "p.355 L86 completes ‘neo-classical correctness’ and the sentence"

add_statement("st-chp14-p355-correctness-and-dilemma", BODY, "cand-0052", "cand-6010",
    "sought_to_reconcile_tiepolo_vision_with_neo_classical_correctness",
    q(86, 87, "Haskell says Algarotti tried to reconcile his vision of Tiepolo with neo-classical correctness; both writer and artist died before the controversy reached a critical stage, and the clash crystallized Algarotti’s personal dilemma and that of his century.",
      "authorial interpretation", "This closes the sentence begun on p.354 L83. Haskell’s framing of the period-wide dilemma remains an interpretation.",
      ["cand-0052", "cand-3781", "cand-6010", "cand-0059"],
      cross_reference_segments=[BODY_PREV], cross_reference_text="completes p.354 L83 and records the cross-page clause"),
    quote(86, 87, "‘correctness’, though both writer and artist died before a really critical stage in the controversy had been reached. This clash between two sets of values crystallised\nAlgarotti’s own personal dilemma as well as that of his century."))

add_statement("st-chp14-p355-algarotti-venetian-heritage", BODY, "cand-0052", "cand-2719",
    "recognized_venetian_qualities_in_contemporaries",
    q(87, 88, "Haskell describes Algarotti as retaining his Venetian heritage, understanding and loving what made Venetian painting great, and recognizing those qualities in gifted contemporaries.",
      "authorial interpretation", "‘Venetian’ here describes cultural heritage and painting, not a claim about residence during this period.",
      ["cand-0052", "cand-2719"]),
    quote(87, 88, "As a Venetian who never renounced his Venetian heritage and who understood and loved what had made\nVenetian painting great, he was able to recognise these characteristic qualities in the most gifted of his contemporaries."))

add_statement("st-chp14-p355-algarotti-internationalist-dilemma", BODY, "cand-0052", "cand-3781",
    "balanced_venetian_attachment_against_international_new_standards",
    q(88, 88, "Haskell says Algarotti, as an internationalist in contact with scholars and princes, recognized the new standards and Tiepolo’s shortcomings measured against them; this conflicting stance led him to admire Tiepolo while urging him to moderate his poetic fantasy.",
      "authorial interpretation", "The new standards and the tension between them and Venetian painting are Haskell’s framing; the quoted request to moderate fantasy is attributed to Algarotti through Haskell and note 1.",
      ["cand-0052", "cand-3781", "cand-6010", "cand-10227", "cand-10229"], relation_candidate=True,
      footnote_marker="1", footnote_segment=NOTES, footnote_line_range="L191",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p355-note1-michelessi"]),
    quote(88, 88, "Yet as an internationalist, in touch with scholars and princes, he must have realised equally clearly the way the wind was blowing and the shortcomings of Tiepolo measured by the new standards that were everywhere being talked about. It was this conflicting attitude that led him always to admire Tiepolo as the greatest artist of the day and yet to try and induce him to ‘moderate somewhat his blazing poetic fantasy’.1"))

add_statement("st-chp14-p355-royal-commissions-lost", BODY, "cand-0052", "cand-10326",
    "commissioned_pictures_for_the_king_reported_lost",
    q(89, 89, "Haskell says the pictures Algarotti commissioned for the King were lost, while their impact on his Venetian visit can be traced in other works painted during or soon after the visit.",
      "authorial report", "The passage does not enumerate the lost pictures. The separate p.351 five-commission group is a candidate for comparison, not presumed identical.",
      ["cand-0052", "cand-0149", "cand-10273", "cand-2719"], relation_candidate=True,
      cross_reference_segments=["chp-14:14_CHP-14_intro:l46-53"],
      cross_reference_text="compare the five works described on p.351; identity of this plural remains open",
      candidate_identity_questions=[{"candidate_id": "cand-10273", "issue": "The five works listed on p.351 may be the lost commissions mentioned here, but p.355 does not enumerate them; confirm during S3/source reconciliation."}]),
    quote(89, 89, "Although the pictures that Algarotti commissioned for the King have been lost, the impact that he made on this visit to Venice can be noted in other works painted"))

add_statement("st-chp14-p355-piazzetta-isolated-classical-phase", BODY, "cand-1909", "cand-3781",
    "venice_visit_marked_an_important_isolated_phase_for_piazzetta",
    q(89, 89, "Haskell says the Venetian stay marked an important but isolated phase in Piazzetta’s career, as it did for Tiepolo.",
      "authorial assessment", "This is Haskell’s career-periodization, not an independently verified chronology.",
      ["cand-0052", "cand-1909", "cand-3781", "cand-2719"]),
    quote(89, 89, "For Piazzetta, as for Tiepolo, the period marked an important (though, in his case, isolated) phase in his career."))

add_statement("st-chp14-p355-piazzetta-caesar-commission", BODY, "cand-0052", "cand-10327",
    "commissioned_event_for_augustus",
    q(89, 90, "Haskell says Algarotti commissioned Piazzetta to paint Caesar and the Corsairs of Cilicia for Augustus after Piazzetta’s most successful genre and pastoral ventures.",
      "authorial report", "The index supplies the subject-based title; the passage gives no date, present location, or version. The commission remains a book-derived S2 relation candidate.",
      ["cand-0052", "cand-1909", "cand-10307", "cand-10327", "cand-0149"], relation_candidate=True),
    quote(89, 90, "The commission from\nAlgarotti to paint Caesar and the Corsairs of Cilicia for Augustus came after his most successful ventures into genre and pastoral painting."))

add_statement("st-chp14-p355-commission-event-work", BODY, "cand-10327", "cand-10307",
    "commissioned_work",
    q(89, 90, "The Algarotti commission event concerned Piazzetta’s painting Caesar and the Corsairs of Cilicia for Augustus.",
      "authorial report", "The event and painting are distinct candidates; the page gives no date or present location.",
      ["cand-0052", "cand-1909", "cand-10307", "cand-10327", "cand-0149"], relation_candidate=True),
    quote(89, 90, "The commission from\nAlgarotti to paint Caesar and the Corsairs of Cilicia for Augustus came after his most successful ventures into genre and pastoral painting."))

add_statement("st-chp14-p355-piazzetta-classical-works", BODY, "cand-1909", None,
    "described_only_three_classical_works_in_piazzetta_oeuvre",
    q(90, 90, "Haskell says large-scale classical history pictures were foreign to Piazzetta’s genius, but the Algarotti commission was followed by two further paintings of the same kind; together with the lost commissioned picture these were the only such classical works in Piazzetta’s oeuvre.",
      "authorial assessment", "The two additional titles are supplied by p.355 note 2; no location is assigned to an individual title because the note does not explicitly pair titles and places.",
      ["cand-1909", "cand-10307", "cand-10308", "cand-10309", "cand-10327"],
      footnote_marker="2", footnote_segment=NOTES, footnote_line_range="L192",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p355-note2-two-works-and-locations", "st-chp14-p355-note2-mucius-after-commission", "st-chp14-p355-note2-darius-after-commission"]),
    quote(90, 90, "Large-scale ‘historical’ pictures of classical themes were completely foreign to his genius, but Algarotti’s commission was followed by two further paintings of the same kind; and these (together with the lost picture) make up the only such classical works in Piazzetta’s œuvre."))

add_statement("st-chp14-p355-algarotti-piazzetta-ownership", BODY, "cand-0052", "cand-10310",
    "owned_one_small_piazzetta_painting",
    q(90, 90, "Haskell says Algarotti seems to have had no special admiration for Piazzetta, although he owned one small painting by him.",
      "authorial assessment and report", "The painting is not identified; Haskell’s inference about Algarotti’s admiration remains attributed rather than treated as a fact about private taste.",
      ["cand-0052", "cand-1909", "cand-10310"], relation_candidate=True),
    quote(90, 90, "In fact, Algarotti seems to have had no special admiration for Piazzetta: he only owned one small painting by him"))

add_statement("st-chp14-p355-piazzetta-newtonianismo-frontispiece", BODY, "cand-10311", "cand-10258",
    "frontispiece_illustration_in_first_edition",
    q(90, 91, "Haskell says the first edition of Newtonianismo had one of Piazzetta’s most sophisticated Parisian-style illustrations as its frontispiece.",
      "authorial report", "The passage attributes the illustration to Piazzetta but gives no subject, plate, edition date, or image location.",
      ["cand-0052", "cand-1909", "cand-10258", "cand-10311"], relation_candidate=True),
    quote(90, 91, "though the first edition of the Newtonianismo had one of his most sophisticated\nParisian-style illustrations as frontispiece."))

add_statement("st-chp14-p355-family-collection-formed-by-father", BODY, "cand-10312", "cand-10225",
    "formed_by",
    q(92, 92, "Haskell says the family picture collection had been formed by Algarotti’s unnamed father.",
      "authorial report", "The father remains unnamed; the family collection is kept distinct from the p.347 personal and joint-collection candidates pending alignment.",
      ["cand-0052", "cand-10225", "cand-10312", "cand-10223", "cand-10224"], relation_candidate=True,
      footnote_marker="3", footnote_segment=NOTES, footnote_line_range="L193",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p355-note3-collection-references"],
      candidate_identity_questions=[{"candidate_id": "cand-10223", "issue": "Compare this family collection with the p.347 candidate for Algarotti’s own collection; do not merge solely on wording."}, {"candidate_id": "cand-10224", "issue": "Compare with the separately described Algarotti-Bonomo joint collection; p.355 does not settle whether these are the same holding."}]),
    quote(92, 92, "the family collection of pictures which had been formed by his father"))

add_statement("st-chp14-p355-family-collection-increased-by-bonomo", BODY, "cand-10312", "cand-0040",
    "greatly_increased_by_brother",
    q(92, 92, "Haskell says Algarotti’s brother Bonomo greatly increased the family picture collection.",
      "authorial report", "The brother is identified as Bonomo from the chapter context; the collection’s identity relative to p.347 candidates remains unresolved.",
      ["cand-0052", "cand-0040", "cand-10312", "cand-10223", "cand-10224"], relation_candidate=True,
      footnote_marker="3", footnote_segment=NOTES, footnote_line_range="L193",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p355-note3-collection-references"],
      candidate_identity_questions=[{"candidate_id": "cand-10223", "issue": "Compare this family collection with the p.347 candidate for Algarotti’s own collection; do not merge solely on wording."}, {"candidate_id": "cand-10224", "issue": "Compare with the separately described Algarotti-Bonomo joint collection; p.355 does not settle whether these are the same holding."}]),
    quote(92, 92, "greatly increased by his brother"))

add_statement("st-chp14-p355-canvases-sent-to-dresden", BODY, "cand-0052", "cand-10313",
    "sent_new_and_old_canvases_to_dresden",
    q(92, 93, "Haskell says Algarotti sent many old and new canvases to Dresden.",
      "authorial report", "The sent canvases are an unidentified group and are not equated with the five lost royal commissions; the retained preparatory sketches or replicas are recorded separately.",
      ["cand-0052", "cand-10313", "cand-0947", "cand-10222"], relation_candidate=True),
    quote(92, 93, "He kept preliminary sketches or replicas of many of the canvases, new and old, that he sent to\nDresden"))

add_statement("st-chp14-p355-retained-sketches-or-replicas", BODY, "cand-0052", "cand-10324",
    "kept_preliminary_sketches_or_replicas_of_sent_canvases",
    q(92, 92, "Haskell says Algarotti kept preliminary sketches or replicas of many canvases that he sent to Dresden.",
      "authorial report", "The source leaves open whether each retained item was a preliminary sketch or a replica and does not identify individual works.",
      ["cand-0052", "cand-10313", "cand-10324", "cand-0947"], relation_candidate=True),
    quote(92, 92, "He kept preliminary sketches or replicas of many of the canvases, new and old, that he sent to"))

add_statement("st-chp14-p355-algarotti-collection-casual-disposals", BODY, "cand-10312", None,
    "acquired_pictures_casually_and_often_gave_or_sold_them",
    q(93, 93, "Haskell describes Algarotti’s pictures as acquired somewhat casually and often given away or sold when a suitable client became available.",
      "authorial report", "The passage does not name particular recipients or identify individual works.",
      ["cand-0052", "cand-10312"], relation_candidate=True),
    quote(93, 93, "His pictures were thus obtained in a somewhat casual way, and as often as not they were given away or sold when a suitable client became available."))

add_statement("st-chp14-p355-kept-unsuitable-works", BODY, "cand-0052", "cand-10325",
    "kept_acquired_works_unsuitable_for_royal_collection",
    q(93, 93, "Haskell says Algarotti often kept for himself works he acquired that were unsuitable for the royal collection.",
      "authorial report", "No individual work or destination is named.",
      ["cand-0052", "cand-10222", "cand-10325"], relation_candidate=True),
    quote(93, 93, "often when he acquired some work which was not suitable for the royal collection he kept it for himself"))

add_statement("st-chp14-p355-collection-size", BODY, "cand-0052", "cand-10312",
    "built_collection_to_nearly_two_hundred_paintings_and_many_drawings",
    q(93, 93, "Haskell says Algarotti eventually built the collection to nearly 200 paintings and a large number of drawings.",
      "authorial report", "‘Nearly’ and ‘a large number’ are approximate source wording.",
      ["cand-0052", "cand-10312"]),
    quote(93, 93, "although he eventually built up the collection to nearly 200 paintings and a large number of drawings"))

add_statement("st-chp14-p355-inventory-limit", BODY, "cand-0052", "cand-10312",
    "inventory_insufficient_to_gauge_taste_or_commission_extent",
    q(93, 93, "Haskell says the surviving inventory does not permit precise conclusions about Algarotti’s tastes or the extent of his commissions.",
      "authorial assessment", "This is a stated limit of the inventory-based inference, not a claim that no evidence exists elsewhere.",
      ["cand-0052", "cand-10312"]),
    quote(93, 93, "it is impossible to gauge anything very precise about his tastes or the extent of his commissions from the inventory as we have it."))

add_statement("st-chp14-p355-tiepolo-paintings-in-collection", BODY, "cand-10312", "cand-10314",
    "included_about_thirteen_tiepolo_paintings",
    q(94, 94, "Haskell says the collection included about 13 Tiepolo paintings, placing him above the other named contemporaries in Algarotti’s holdings.",
      "authorial report", "The painting count is expressly approximate (‘some 13’); no individual paintings are identified.",
      ["cand-0052", "cand-3781", "cand-10312", "cand-10314"], relation_candidate=True,
      footnote_marker="3", footnote_segment=NOTES, footnote_line_range="L193",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p355-note3-collection-references"]),
    quote(94, 94, "Tiepolo stands out among all his contemporaries with some 13 paintings and 116 drawings."))

add_statement("st-chp14-p355-tiepolo-drawings-in-collection", BODY, "cand-10312", "cand-10315",
    "included_one_hundred_sixteen_tiepolo_drawings",
    q(94, 94, "Haskell says the collection included 116 Tiepolo drawings.",
      "authorial report", "No individual drawings are identified.",
      ["cand-0052", "cand-3781", "cand-10312", "cand-10315"], relation_candidate=True,
      footnote_marker="3", footnote_segment=NOTES, footnote_line_range="L193",
      footnote_text_pending=False, footnote_body_link_status="linked",
      footnote_note_statement_ids=["st-chp14-p355-note3-collection-references"]),
    quote(94, 94, "Tiepolo stands out among all his contemporaries with some 13 paintings and 116 drawings."))

add_statement("st-chp14-p355-no-evidence-of-algarotti-canaletto-contact", BODY, "cand-0052", "cand-0498",
    "no_evidence_of_contact_during_venice_visit",
    q(94, 95, "Haskell says there is no evidence Algarotti contacted Canaletto during this Venice visit; he also says none of the Canalettos in Dresden seems to have reached the gallery through Algarotti’s agency and Algarotti wrote of no intention to send any.",
      "authorial report with negative-evidence qualification", "Retain ‘no evidence’ and ‘seems’; this is not an absolute claim that no contact or transfer ever occurred.",
      ["cand-0052", "cand-0498", "cand-10316", "cand-2719", "cand-0947", "cand-10222"], relation_candidate=True),
    quote(94, 95, "there is no evidence that\nAlgarotti made contact with Canaletto during this visit to Venice. None of the Canalettos in Dresden seems to have reached the gallery through his agency, nor did Algarotti write that he had any intention of sending any."))

add_statement("st-chp14-p355-canaletto-intensively-employed-partial", BODY, "cand-0498", None,
    "reported_as_intensively_employed_by_consul_smith_partial",
    q(95, 95, "Haskell begins to say Canaletto was still intensively employed by Consul Smith; the sentence continues on p.356.",
      "authorial report", "The sentence is incomplete at p.355 L95. The p.356 continuation and attached footnote must close this statement before the segment is complete.",
      ["cand-0498"],
      cross_reference_segments=["chp-14:14_CHP-14_intro:l97-107"], cross_reference_text="continues after ‘still intensively’ on p.356"),
    quote(95, 95, "Canaletto at this stage was still intensively"))

add_note_statement("st-chp14-p355-note1-michelessi",
    q(191, 191, "P.355 note 1 attributes the preceding report to Michelessi and locates the citation in Opere I, page lxii.",
      "authorial bibliographic note", "The cited passage was not independently consulted; OCR ‘Ixii’ is read as printed ‘lxii’. Reuses the chapter’s existing Michelessi and Opere candidates.",
      ["cand-10227", "cand-10229"], cross_reference_segments=[BODY],
      cross_reference_text="supports the p.355 sentence about urging Tiepolo to moderate his fantasy",
      ocr_corrections=[{"source_line": 191, "ocr": "Ixii", "print": "lxii", "basis": "CHP-14.pdf physical page 9."}]),
    quote(191, 191, "1 According to Michelessi (see Opere, I, p. Ixii)."))

add_note_statement("st-chp14-p355-note2-two-works-and-locations",
    q(192, 192, "P.355 note 2 names Mucius Scaevola at the Altar and The Death of Darius, lists Palazzo Barbaro Curtis and Cà Rezzonico in Venice, and cites Pallucchini (1956, p.41) for the claim that both paintings followed the Algarotti commission shortly afterward.",
      "authorial bibliographic note and report", "The note lists two works followed by two locations but does not explicitly say ‘respectively’; no one-to-one location assignment is asserted. Pallucchini’s cited text was not independently consulted.",
      ["cand-10307", "cand-10308", "cand-10309", "cand-10317", "cand-10318", "cand-2719", "cand-10319", "cand-10320", "cand-10327"],
      cross_reference_segments=[BODY], cross_reference_text="identifies the two further Piazzetta paintings and qualifies their chronology"),
    quote(192, 192, "2 Mucius Scaevola at the Altar and The Death of Darius—in the Palazzo Barbaro Curtis and Cà Rezzonico in Venice. According to Pallucchini (1956, p. 41) both were painted just after the Algarotti commission."))

for statement_id, work_id, title in [
    ("st-chp14-p355-note2-mucius-after-commission", "cand-10308", "Mucius Scaevola at the Altar"),
    ("st-chp14-p355-note2-darius-after-commission", "cand-10309", "The Death of Darius"),
]:
    add_statement(statement_id, NOTES, work_id, "cand-10327", "painted_shortly_after",
        q(192, 192, f"Pallucchini, as reported in Haskell’s note, places {title} shortly after the Algarotti commission.",
          "reported chronology", "The note says ‘both’ works and refers to the commission described in p.355 L90; the source itself was not consulted.",
          [work_id, "cand-10327", "cand-10307", "cand-10319", "cand-10320"],
          cross_reference_segments=[BODY], cross_reference_text="the p.355 commission event for Caesar and the Corsairs of Cilicia"),
        quote(192, 192, "According to Pallucchini (1956, p. 41) both were painted just after the Algarotti commission."))

add_note_statement("st-chp14-p355-note3-collection-references",
    q(193, 193, "P.355 note 3 cites G. A. Selva for Algarotti’s collection and Levey’s 1960 Burlington Magazine article, pages 250–257, for Tiepolo works in it.",
      "authorial bibliographic note", "The Selva reference has no title or locator; the Levey article is reused from p.354 note 2 and was not independently consulted.",
      ["cand-10312", "cand-10321", "cand-10322", "cand-10297", "cand-10302", "cand-10314", "cand-10315"],
      cross_reference_segments=[BODY], cross_reference_text="supports the p.355 collection description and Tiepolo counts",
      ocr_corrections=[{"source_line": 193, "ocr": "i960", "print": "1960", "basis": "CHP-14.pdf physical page 9."}],
      candidate_identity_questions=[{"candidate_id": "cand-10223", "issue": "The note does not settle whether the p.355 family collection equals the separate p.347 personal collection candidate."}, {"candidate_id": "cand-10224", "issue": "The note does not settle whether the p.355 family collection equals the p.347 Bonomo-Algarotti joint collection candidate."}]),
    quote(193, 193, "3 For Algarotti’s collection see [G. A. Selva] and for the Tiepolos in it Levey, in Burlington Magazine, i960, pp. 250-7."))

# Verify exact source anchors, foreign keys, and non-overlapping mention intervals before writing.
known_ids = set(candidate_by_id)
for row in planned_mentions:
    seg = row["segment_id"]
    start, end = int(row["start_char"]), int(row["end_char"])
    bounds = segment_bounds[seg]
    segment_text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention anchor mismatch: {row['mention_id']} {row['surface_form']!r}")
    if row["candidate_id"] not in known_ids:
        raise SystemExit(f"mention candidate missing: {row['mention_id']} -> {row['candidate_id']}")
for segment_id in (BODY, NOTES):
    spans = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"], r["surface_form"])
                   for r in planned_mentions if r["segment_id"] == segment_id)
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0]:
            raise SystemExit(f"overlapping mentions: {left[2]} {left[3]!r} / {right[2]} {right[3]!r}")
for row in statements:
    if row["statement_id"].startswith("st-chp14-p355-"):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        if row["original_quote"] not in "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]]):
            raise SystemExit(f"statement quote missing from source: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in known_ids:
                raise SystemExit(f"statement mentioned candidate missing: {row['statement_id']} -> {cid}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L74-83",
    "note": "Printed p.354 sentence ‘demands of neo-classical’ closes at p.355 L86 as ‘neo-classical correctness’; the joined claim is cross-linked. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L86-95",
    "note": "Printed p.355 read against CHP-14.pdf physical p.9. Body L86 closes p.354; L95 ends mid-sentence at ‘still intensively’ and continues on p.356. Notes 1-3 at L191-193 are linked; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-193",
    "note": "Printed notes p.347-p.355 read against CHP-14.pdf physical pages 1-9. P.355 notes 1-3 are linked to the fantasy quotation, two Piazzetta classical paintings, and collection/Tiepolo holdings; later notes remain pending.",
})

new_statements = [row for row in statements if row["statement_id"].startswith("st-chp14-p355-")]
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": source_hash,
    "pdf_sha256": pdf_hash,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statements),
    "updated_statements": ["st-chp14-p354-reconcile-tiepolo-vision-with-neo-classical-demands"],
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
