"""Controlled S2 migration for Andrea Memmo's printed p.366 passage and note 1."""
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
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l6-12"
BODY = "chp-15:15_CHP-15_sec_ii:l14-28"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l30-36"
P365_NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
P365_PARTIAL = "st-chp15-p365-memmo-representation-eligibility-partial"
P366_PARTIAL = "st-chp15-p366-memmo-expert-patron-reputation-partial"
BACKUP_SUFFIX = ".bak-s2-chp15-p366-memmo-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.366 Andrea Memmo S2 migration")
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
for line_number, required in [
    (15, "city could be represented; moreover, only certain classes of people could present statues"),
    (16, "135 zecchini or, for something rather better, 150"),
    (17, "Memmo himself inaugurated the scheme by offering a statue"),
    (18, "Francesco Andreosi, of Antenor"),
    (18, "the city of Padua, which chose one of"),
    (19, "Memmo’s ancestors, a fourteenth century podestà"),
    (20, "with 19 statues in place, Memmo left for four years as Ambassador in Constantinople"),
    (21, "Giuseppe Subleyras, son of the French painter"),
    (22, "Francesco Piranesi engraved Subleyras’s drawing"),
    (23, "only eight out of the original eighty-eight"),
    (24, "Memmo’s reputation as an expert and patron was by now very great, and dining"),
    (25, "The Duke of Gloucester was in Padua"),
    (27, "No. 80 is from Memmo in Padua, dated 18 October [1775]"),
    (28, "Duca —see p. 373, note 2."),
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

for segment_id in (BODY_PREV, BODY, BODY_NEXT, P365_NOTES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if (
    coverage_by_id[BODY_PREV]["migration_status"] != "partial"
    or coverage_by_id[BODY]["migration_status"] != "pending"
    or coverage_by_id[BODY_NEXT]["migration_status"] != "pending"
    or coverage_by_id[P365_NOTES]["migration_status"] != "partial"
    or coverage_by_id[P365_NOTES]["source_line_ranges"] != "L91-92"
):
    raise SystemExit("S2 coverage preconditions changed")
if P365_PARTIAL not in statement_by_id:
    raise SystemExit(f"missing p.365 partial statement: {P365_PARTIAL}")
if statement_by_id[P365_PARTIAL]["qualifiers"].get("predicate_status") != "partial":
    raise SystemExit("p.365 cross-page statement is no longer partial")
if any(row["segment_id"] == BODY for row in mentions):
    raise SystemExit("p.366 mention rows already exist")
if any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.366 statement rows already exist")

new_candidates = [
    ("cand-10483", "Antenor, legendary founder of Padua in Haskell’s p.366 account", "person", 18,
     "The source calls him the legendary founder of Padua; this source-level description is not independently verified."),
    ("cand-10484", "Statue of Antenor offered by Andrea Memmo for the Prà della Valle scheme", "work", 17,
     "Haskell says it was to be made by Francesco Andreosi. The passage does not confirm completion or installation."),
    ("cand-10485", "House of Brunswick named in Haskell’s account of Azzo d’Este", "family", 18,
     "Haskell describes Azzo as the originator of the house; no wider genealogy is inferred here."),
    ("cand-10486", "Statue of Azzo, Marchese d’Este, erected at Prà della Valle by the Duke of Gloucester", "work", 18,
     "Haskell says the Duke erected the statue; page 366 note 1 gives a qualified chronology. Do not infer present survival or exact installation day."),
    ("cand-10487", "Unidentified fourteenth-century podestà, an ancestor of Andrea Memmo", "person", 19,
     "No personal name is supplied. Haskell says Padua selected him as the subject of a statue."),
    ("cand-10488", "Statue of an unnamed fourteenth-century ancestor of Andrea Memmo offered by Padua", "work", 19,
     "The subject is described as a fourteenth-century podestà; completion or installation is not stated here."),
    ("cand-10489", "Important churchmen as eligible statue presenters in Memmo’s scheme", "term", 15,
     "A class named in Haskell’s account of who could present statues in their own names."),
    ("cand-10490", "University teachers as eligible statue presenters in Memmo’s scheme", "term", 15,
     "A class named among old and distinguished professions; no specific university teacher is identified."),
    ("cand-10491", "Constantinople, destination of Andrea Memmo’s ambassadorship in 1777", "place", 20,
     "The name is retained as printed; no modern place-name normalization is needed for S2."),
    ("cand-10492", "Andrea Memmo’s ambassadorship in Constantinople, described as lasting four years", "event", 20,
     "Haskell dates the departure to 1777 and gives a four-year duration; the passage does not specify exact start/end dates."),
    ("cand-10493", "Unidentified Pope whose example was followed by statue contributors in Haskell’s p.366 account", "person", 21,
     "The Pope is unnamed in this passage; no identity is inferred from the chronology."),
    ("cand-10494", "Giuseppe Subleyras’s drawings of Andrea Memmo’s Prà della Valle plan", "work", 21,
     "Haskell says Subleyras drew the plans and that they were hung in Memmo’s apartments. The passage does not specify a title or number of sheets."),
    ("cand-10495", "Francesco Piranesi’s 1786 engraving after Subleyras’s Prà della Valle drawing", "work", 22,
     "Haskell says the engraving was accompanied by an account from Don Vincenzo Radicchio; edition details are not supplied here."),
    ("cand-10496", "Statue of Petrarch paid for by the Grand Duke of Tuscany for Memmo’s scheme", "work", 21,
     "Haskell identifies the subject and payer but gives no sculptor, precise installation date, or current location in this passage."),
    ("cand-10497", "Statue of Galileo paid for by the Grand Duke of Tuscany for Memmo’s scheme", "work", 21,
     "Haskell identifies the subject and payer but gives no sculptor, precise installation date, or current location in this passage."),
    ("cand-10498", "Six additional statues in Rome mentioned in Haskell’s account of Memmo’s scheme", "work", 20,
     "The phrase ‘another six in Rome’ is syntactically compressed; preserve the count and place without deciding how the group relates to the 19 statues at Prà."),
    ("cand-10499", "Memmo to John Strange, 18 October 1775, British Museum Egerton MSS. 1969, no. 80", "archive", 27,
     "Locator and content are reported in Haskell’s note; the manuscript has not been independently consulted."),
    ("cand-10500", "John Strange to G. M. Sasso, 8 October 1777, concerning a drawing of the Duke’s statue", "archive", 27,
     "Letter reported in Haskell’s note; repository and shelfmark are not supplied in this passage and the letter has not been consulted."),
    ("cand-10501", "Requested drawing of the Duke of Gloucester’s statue at Prà della Valle", "work", 27,
     "Haskell reports that Strange asked Sasso to have Mingardi make a drawing. The passage does not establish that the drawing was completed."),
    ("cand-10502", "‘New Athens’ as the poets’ comparison for the Prà della Valle scheme", "term", 20,
     "A rhetorical comparison reported by Haskell; no literal transformation or institutional identity is inferred."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{source_line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row

segment_lines = {BODY: {number: source_lines[number - 1] for number in range(14, 29)}}
segment_offsets = {}
offset = 0
segment_offsets[BODY] = {}
for number in range(14, 29):
    segment_offsets[BODY][number] = offset
    offset += len(segment_lines[BODY][number]) + 1

planned_mentions = []
mention_counter = 1


def add_mention(candidate_id, surface, source_line, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    line = segment_lines[BODY][source_line]
    line_offset = segment_offsets[BODY][source_line]
    occupied = [
        (int(row["start_char"]), int(row["end_char"]))
        for row in mentions + planned_mentions
        if row["segment_id"] == BODY and line_offset <= int(row["start_char"]) < line_offset + len(line)
    ]
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            raise SystemExit(f"surface not found on {BODY} L{source_line}: {surface!r}")
        start = line_offset + pos
        end = start + len(surface)
        if not any(start < old_end and old_start < end for old_start, old_end in occupied):
            break
        search_from = pos + 1
    mention_id = f"m-chp15-p366-memmo-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": BODY, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


def quote(line_start, line_end):
    if not 14 <= line_start <= line_end <= 28:
        raise SystemExit(f"quote span outside {BODY}: L{line_start}-{line_end}")
    return "\n".join(segment_lines[BODY][n] for n in range(line_start, line_end + 1))


def footnote(marker, note_start, note_end, body_line, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": BODY,
        "footnote_line_range": f"L{note_start}-L{note_end}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(statement_ids),
    }


def add_statement(statement_id, subject, obj, predicate, line_start, line_end, claim,
                  speaker="Haskell", text_layer="authorial report", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 366, "pdf_physical_page": 6,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": BODY,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(line_start, line_end),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


previous = statement_by_id[P365_PARTIAL]
previous["predicate"] = previous["predicate"].removesuffix("_partial")
previous["qualifiers"]["predicate_status"] = "complete"
previous["qualifiers"]["claim"] = "Haskell says only nobles or men who had brought particular glory to the city could be represented."
previous["qualifiers"]["qualification"] = (
    "P.366 L15 completes p.365 L11. Haskell then gives a separate rule about who could present statues in their own names; "
    "being represented and presenting a statue are not conflated."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = (
    "P.365 L11 ends ‘particular glory to the’; p.366 L15 continues ‘city could be represented’."
)
previous["qualifiers"]["cross_reference_text_pending"] = False
previous["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
    previous["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-3944"]
))

# S2 mentions follow the OCR source spans; verified print corrections stay in the notes.
add_mention("cand-3944", "city", 15, "Closes the p.365 partial clause; printed p.366 reads city.")
add_mention("cand-10489", "important churchmen", 15)
add_mention("cand-10490", "university teachers", 15)
add_mention("cand-8108", "nobles", 15)
add_mention("cand-1650", "opportunity to raise a statue", 15)
add_mention("cand-1650", "the rich", 15, "Eligibility/accessibility language for the statue scheme.")
add_mention("cand-1650", "precious marbles", 16)
add_mention("cand-1650", "famous sculptors", 16)
add_mention("cand-1650", "135 zecchini", 16)
add_mention("cand-1650", "150", 16)
add_mention("cand-1650", "standard of quality", 16)
add_mention("cand-1650", "a committee", 16, "Unnamed quality-control committee; no independent institution candidate is inferred.")
add_mention("cand-1650", "The same kind of stone", 16)
add_mention("cand-1650", "inscriptions", 16)
add_mention("cand-1650", "Latin", 16)
add_mention("cand-1650", "pedestals", 16)
add_mention("cand-1650", "the scheme", 17)
add_mention("cand-10484", "a statue", 17, "The proposed work offered to inaugurate the scheme.")
add_mention("cand-1642", "Memmo himself", 17)
add_mention("cand-0104", "Francesco Andreosi", 18, "The p.366 index subentry identifies this candidate with the statue of Antenor; S3 alignment remains pending.")
add_mention("cand-10483", "Antenor", 18)
add_mention("cand-3944", "Padua", 18)
add_mention("cand-1204", "Duke of Gloucester", 18)
add_mention("cand-10486", "a statue", 18)
add_mention("cand-0981", "Azzo, Marchese d’Este", 18)
add_mention("cand-10485", "house of Brunswick", 18)
add_mention("cand-10488", "a third", 18)
add_mention("cand-8406", "city of Padua", 18, "Civic-body candidate; exact institutional continuity is for S3.")
add_mention("cand-1642", "Memmo’s ancestors", 19)
add_mention("cand-10487", "a fourteenth century podestà", 19)
add_mention("cand-1642", "he had turned down their proposal", 19, "‘he’ is Andrea Memmo; the proposal was that he himself be represented.")
add_mention("cand-1642", "he himself", 19)
add_mention("cand-10502", "new Athens", 20, "Poetic comparison reported by Haskell; not a literal place identity.")
add_mention("cand-1650", "19 statues", 20)
add_mention("cand-1642", "Memmo left", 20)
add_mention("cand-10492", "Ambassador", 20)
add_mention("cand-10491", "Constantinople", 20)
add_mention("cand-10498", "another six", 20, "The source’s syntactic relation to the preceding 19 statues is retained as uncertain.")
add_mention("cand-4490", "Rome", 20)
add_mention("cand-3960", "Prato della Valle", 20, "OCR reads Prato; p.366 print reads Prà della Valle.")
add_mention("cand-1650", "Debts", 20)
add_mention("cand-8406", "the councillors", 20, "Unnamed civic actors; do not resolve their exact body here.")
add_mention("cand-1650", "work", 20)
add_mention("cand-1642", "Memmo remained", 20)
add_mention("cand-1650", "put up statues", 20)
add_mention("cand-1642", "his friends", 20, "Friends are unnamed; this mention records the reported relationship context only.")
add_mention("cand-1642", "his plans", 20)
add_mention("cand-2532", "Giuseppe Subleyras", 21)
add_mention("cand-8108", "the nobility", 21)
add_mention("cand-10493", "the Pope", 21, "The passage does not name the Pope.")
add_mention("cand-1650", "a statue", 21, "A general contribution to the scheme, not an identified individual work.")
add_mention("cand-1397", "Grand Duke of Tuscany", 21, "The p.366 index names Leopold I; the passage itself gives only the title, to be checked at S3.")
add_mention("cand-1893", "Petrarch", 21)
add_mention("cand-1105", "Galileo", 21)
add_mention("cand-2505", "Kings of Poland", 21, "The p.366 index names Stanislas Poniatowski; the passage itself gives only the title, to be checked at S3.")
add_mention("cand-1283", "Sweden", 21, "The p.366 index names Gustavus III; the passage itself gives only the title, to be checked at S3.")
add_mention("cand-1937", "Francesco Piranesi", 22)
add_mention("cand-10495", "engraved", 22)
add_mention("cand-10494", "Subleyras’s drawing", 22)
add_mention("cand-2089", "Don Vincenzo Radicchio", 22)
add_mention("cand-10495", "the engraving", 22)
add_mention("cand-1650", "the original eighty-eight", 23)
add_mention("cand-1650", "fifty-three", 23)
add_mention("cand-1650", "in situ", 23)
add_mention("cand-1642", "Memmo’s reputation", 24)
add_mention("cand-1650", "expert and patron", 24)
add_mention("cand-1204", "The Duke of Gloucester", 25)
add_mention("cand-3944", "Padua", 25)
add_mention("cand-1204", "he fell ill", 25)
add_mention("cand-1642", "Memmo", 26)
add_mention("cand-1204", "him", 26)
add_mention("cand-2516", "John Strange", 26)
add_mention("cand-5986", "British Museum", 26)
add_mention("cand-10499", "Egerton MSS. 1969", 26)
add_mention("cand-10499", "No. 80", 27)
add_mention("cand-1642", "Memmo", 27)
add_mention("cand-3944", "Padua", 27)
add_mention("cand-1204", "the Duke’s ill-health", 27)
add_mention("cand-10486", "the statue", 27)
add_mention("cand-2516", "Strange", 27)
add_mention("cand-2364", "G. M. Sasso", 27, "The source abbreviates the name; the index candidate supplies Giuseppe Maria, pending S3.")
add_mention("cand-1669", "Mingardi", 27, "The source gives only the surname; the p.366n index candidate is Francesco Mingardi, pending S3.")
add_mention("cand-10501", "a drawing of the statue", 27)
add_mention("cand-3960", "Prato della Valle", 27, "OCR reads Prato; p.366 print reads Prà della Valle. The source text is unchanged.")
add_mention("cand-1204", "Duca", 28, "Completes the Italian quotation split at the source line break: ‘donata dal nostro Duca’." )

N1A = "st-chp15-p366-note1-duke-visits"
N1B = "st-chp15-p366-note1-memmo-contact-and-order-date"
N1C = "st-chp15-p366-note1-egerton-ms-1969-no80"
N1D = "st-chp15-p366-note1-statue-and-strange-letter-1777"

add_statement(
    "st-chp15-p366-eligible-presenters", "cand-1650", None,
    "only_certain_classes_could_present_statues_in_own_names", 15, 15,
    "Haskell says only certain classes could present statues in their own names: nobles, important churchmen, or a few old and distinguished professions such as university teachers.",
    qualification="The text distinguishes eligibility to be represented from eligibility to present a statue; no named individual presenter is inferred.",
    mentioned=["cand-1650", "cand-8108", "cand-10489", "cand-10490"])
add_statement(
    "st-chp15-p366-memmo-not-only-rich", "cand-1642", "cand-1650",
    "wanted_statue_opportunity_not_limited_to_rich", 15, 15,
    "Haskell says Memmo was especially anxious that the opportunity to raise a statue should not be available only to the rich.",
    qualification="This records the stated aim, not proof that all social groups could participate equally.",
    mentioned=["cand-1642", "cand-1650"])
add_statement(
    "st-chp15-p366-price-and-appearance", "cand-1650", None,
    "avoiding_precious_marble_and_famous_sculptors_kept_price_low", 16, 16,
    "Haskell says that if precious marbles and famous sculptors were avoided, general appearance could matter more and prices could be kept to 135 zecchini or 150 for something rather better.",
    qualification="The conditional design choice and two price levels are retained; no modern currency conversion or realized cost is inferred.",
    mentioned=["cand-1650"])
add_statement(
    "st-chp15-p366-quality-committee-and-stone", "cand-1650", None,
    "quality_standard_and_committee_and_uniform_stone_required", 16, 16,
    "Haskell says a quality standard was required, a committee was appointed to enforce it, and the same kind of stone had to be used for every statue.",
    qualification="The committee is unnamed and its membership or formal institutional identity is not supplied.",
    mentioned=["cand-1650"])
add_statement(
    "st-chp15-p366-latin-inscriptions-pedestals", "cand-1650", None,
    "brief_latin_inscriptions_enforced_by_limited_pedestal_space", 16, 16,
    "Haskell says inscriptions had to be brief and in Latin, with limited pedestal space enforcing the restriction.",
    qualification="This records the design rule as described; no individual inscription is identified.",
    mentioned=["cand-1650"])
add_statement(
    "st-chp15-p366-memmo-offers-antenor-statue", "cand-1642", "cand-10484",
    "offered_statue_of_antenor_to_inaugurate_scheme", 17, 18,
    "Haskell says Memmo inaugurated the scheme by offering a statue of Antenor, the legendary founder of Padua, to be made by Francesco Andreosi.",
    qualification="The work is described as offered and to be made; the passage does not confirm completion. ‘Legendary founder’ is Haskell’s description.",
    mentioned=["cand-1642", "cand-10484", "cand-10483", "cand-0104", "cand-3944"], relation_candidate=True)
add_statement(
    "st-chp15-p366-duke-gloucester-azzo-statue", "cand-1204", "cand-10486",
    "duke_of_gloucester_erected_statue_of_azzo", 18, 18,
    "Haskell says the Duke of Gloucester, passing through Padua, erected a statue of Azzo, Marchese d’Este, a Paduan citizen described as originator of the house of Brunswick.",
    qualification="The statement reflects Haskell’s account; the page text does not provide an installation date. Footnote 1 qualifies when the statue order was arranged and reports a 1777 status.",
    mentioned=["cand-1204", "cand-10486", "cand-0981", "cand-10485", "cand-3944"], relation_candidate=True,
    **footnote(1, 25, 28, 18, [N1A, N1B, N1C, N1D]))
add_statement(
    "st-chp15-p366-azzo-statue-subject", "cand-10486", "cand-0981",
    "statue_depicted_azzo_marchese_deste", 18, 18,
    "Haskell identifies Azzo, Marchese d’Este, as the subject of the Duke of Gloucester’s statue.",
    qualification="Azzo’s description as a Paduan citizen and originator of the House of Brunswick remains attributed to Haskell.",
    mentioned=["cand-10486", "cand-0981"], relation_candidate=True)
add_statement(
    "st-chp15-p366-padua-offers-memmo-ancestor-statue", "cand-8406", "cand-10488",
    "city_of_padua_offered_statue_of_memmo_ancestor", 18, 19,
    "Haskell says the city of Padua offered a third statue and chose one of Memmo’s ancestors, a fourteenth-century podestà, after Memmo declined the proposal that he himself be represented.",
    qualification="The ancestor is unnamed. The city-body candidate reuses a prior Padua civic-body candidate provisionally; institutional identity remains for S3.",
    mentioned=["cand-8406", "cand-10488", "cand-1642", "cand-10487"], relation_candidate=True)
add_statement(
    "st-chp15-p366-poets-new-athens", "cand-1650", "cand-10502",
    "poets_compared_progress_to_new_athens", 20, 20,
    "Haskell reports that poets asked whether they were dreaming or had found themselves in a new Athens as the scheme made progress.",
    speaker="Poets as reported by Haskell", text_layer="reported poetic response",
    qualification="The phrase is rhetorical; the poets are unnamed and the comparison does not identify Padua as the ancient city of Athens.",
    mentioned=["cand-1650", "cand-10502"])
add_statement(
    "st-chp15-p366-1777-progress-and-ambassadorship", "cand-1642", "cand-10492",
    "nineteen_statues_in_place_and_memmo_left_as_ambassador_in_1777", 20, 20,
    "Haskell says that in 1777, with 19 statues in place, Memmo left for four years as Ambassador in Constantinople.",
    qualification="The text gives the year and duration but not exact dates. Its following phrase ‘to be followed immediately by another six in Rome’ is recorded separately because its referent is compressed.",
    mentioned=["cand-1642", "cand-1650", "cand-10492", "cand-10491"], relation_candidate=True)
add_statement(
    "st-chp15-p366-another-six-in-rome-ambiguous", "cand-1650", "cand-10498",
    "another_six_in_rome_followed_1777_progress_ambiguous", 20, 20,
    "Haskell adds that the 1777 progress was ‘to be followed immediately by another six in Rome’.",
    qualification="The wording does not unambiguously specify whether the six are additional scheme statues or how they relate spatially to the 19 in place; keep the count and Rome reference without resolving the syntax.",
    mentioned=["cand-1650", "cand-10498", "cand-4490"], relation_candidate=True,
    predicate_status="qualified")
add_statement(
    "st-chp15-p366-difficulties-at-pra-while-memmo-away", "cand-1650", "cand-3960",
    "debts_councillors_objections_slowed_work_during_memmo_absence", 20, 20,
    "Haskell says that while Memmo was away, Prà della Valle encountered serious difficulties: debts rose, councillors objected to the expense, and work slowed alarmingly.",
    qualification="OCR reads ‘Prato’; the p.366 print reads ‘Prà’. The councillors are unnamed.",
    mentioned=["cand-1650", "cand-3960", "cand-8406"])
add_statement(
    "st-chp15-p366-memmo-urges-friends-for-statues", "cand-1642", "cand-1650",
    "in_rome_memmo_urged_friends_to_contribute_statues_and_spread_ideas", 20, 21,
    "Haskell says Memmo remained enthusiastic in Rome, repeatedly pressed friends to provide statues, proposed subjects, and spread his ideas.",
    qualification="Friends are unnamed; this is Haskell’s account of Memmo’s activity, not a complete list of contributors.",
    mentioned=["cand-1642", "cand-4490", "cand-1650"])
add_statement(
    "st-chp15-p366-subleyras-plans-displayed", "cand-1642", "cand-10494",
    "subleyras_drew_prà_plans_hung_in_memmo_apartments", 20, 21,
    "Haskell says Memmo had his plans drawn by Giuseppe Subleyras, son of the French painter, and hung in his apartments, where nobles and distinguished visitors admired them.",
    qualification="No title, exact number of drawings, or precise apartment location is supplied.",
    mentioned=["cand-1642", "cand-10494", "cand-2532", "cand-8108"])
add_statement(
    "st-chp15-p366-pope-and-visitors-contribute", "cand-10493", "cand-1650",
    "visitors_followed_pope_example_and_contributed_statues", 21, 21,
    "Haskell says many distinguished visitors followed the Pope’s example and contributed a statue.",
    qualification="The Pope and visitors are unnamed; the source does not identify each statue or contributor.",
    mentioned=["cand-10493", "cand-8108", "cand-1650"], relation_candidate=True)
add_statement(
    "st-chp15-p366-grandduke-funds-petrarch-galileo-statues", "cand-1397", None,
    "grand_duke_of_tuscany_paid_for_petrarch_and_galileo_statues", 21, 21,
    "Haskell says the Grand Duke of Tuscany paid for two statues, Petrarch and Galileo.",
    qualification="The page text gives only the title; the page 366 index names Leopold I. The two subject-to-work links are recorded as candidates and await S3 alignment.",
    mentioned=["cand-1397", "cand-1893", "cand-1105", "cand-10496", "cand-10497"], relation_candidate=True)
add_statement(
    "st-chp15-p366-poland-sweden-subscriptions", "cand-2505", "cand-1650",
    "kings_of_poland_and_sweden_subscribed", 21, 21,
    "Haskell says the Kings of Poland and Sweden both subscribed to the scheme.",
    qualification="The page text supplies titles only; page 366 index candidates name Stanislas Poniatowski and Gustavus III. Identity alignment remains for S3.",
    mentioned=["cand-2505", "cand-1283", "cand-1650"], relation_candidate=True)
add_statement(
    "st-chp15-p366-piranesi-engraves-subleyras-drawing", "cand-1937", "cand-10495",
    "piranesi_engraved_subleyras_drawing", 22, 22,
    "Haskell says Francesco Piranesi engraved Subleyras’s drawing.",
    qualification="The drawing and engraving are recorded as separate work candidates; no surviving copy, title, or exact edition is identified here.",
    mentioned=["cand-1937", "cand-10494", "cand-10495"], relation_candidate=True)
add_statement(
    "st-chp15-p366-radicchio-account-accompanies-engraving", "cand-2089", "cand-10495",
    "radicchio_wrote_account_to_accompany_engraving_in_1786", 22, 22,
    "Haskell says that in 1786 Don Vincenzo Radicchio, one of Memmo’s secretaries, wrote an account to accompany the engraving.",
    qualification="The p.365 note 2 short citation Radicchio, 1786 may refer to this account, but the title and identity of the citation are not confirmed here; do not merge the locators yet.",
    mentioned=["cand-2089", "cand-1642", "cand-10495"], relation_candidate=True,
    cross_reference_segments=[P365_NOTES],
    cross_reference_text="Possible connection to the Radicchio 1786 short citation in p.365 note 2; identity remains unverified.",
    cross_reference_text_pending=True)
add_statement(
    "st-chp15-p366-statues-promised-and-in-situ-1786", "cand-1650", None,
    "by_1786_eight_of_eighty_eight_unpromised_and_fifty_three_in_situ", 23, 23,
    "Haskell says that by 1786 only eight of the original eighty-eight statues had not been promised and fifty-three were already in situ.",
    qualification="The two counts refer to different progress states; the text does not provide a list of the statues or define the exact survey date beyond ‘by that year’.",
    mentioned=["cand-1650"])
add_statement(
    P366_PARTIAL, "cand-1642", None,
    "memmo_reputation_expert_patron_great_and_during_partial", 24, 24,
    "Haskell says Memmo’s reputation as an expert and patron was by then very great, and the sentence continues after ‘and during’.",
    qualification="The OCR reads ‘dining’; p.366 print reads ‘during’. Continuation is pending at p.367.",
    mentioned=["cand-1642"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT],
    cross_reference_text="P.366 L24 ends ‘and during’; continuation begins in the next source segment.",
    cross_reference_text_pending=True)

N1A = "st-chp15-p366-note1-duke-visits"
N1B = "st-chp15-p366-note1-memmo-contact-and-order-date"
N1C = "st-chp15-p366-note1-egerton-ms-1969-no80"
N1D = "st-chp15-p366-note1-statue-and-strange-letter-1777"
add_statement(
    N1A, None, "cand-1204", "note_reports_duke_gloucester_padua_visits_and_illness", 25, 25,
    "P.366 note 1 says the Duke of Gloucester was in Padua and fell ill in September 1775 and again in May 1777.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The visits and illness are reported by the note; the cited letters have not been independently consulted.",
    mentioned=["cand-1204", "cand-3944"], cited_source_independently_consulted=False)
add_statement(
    N1B, "cand-1642", "cand-1204", "memmo_contacted_duke_first_visit_order_date_uncertain", 26, 26,
    "P.366 note 1 says Memmo was certainly in touch with the Duke during his first visit, but the date when Memmo persuaded him to order the statue is uncertain.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="Preserves the note’s distinction between certain contact and uncertain timing of the order.",
    mentioned=["cand-1642", "cand-1204"], cited_source_independently_consulted=False)
add_statement(
    N1C, "cand-1642", "cand-10499", "note_cites_egerton_mss_1969_no80", 26, 27,
    "P.366 note 1 points to letters to John Strange in the British Museum and identifies Egerton MSS. 1969, no. 80 as a letter from Memmo in Padua dated 18 October [1775] concerning the Duke’s ill-health.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The shelfmark and letter description are transcribed from Haskell; the manuscript has not been independently consulted.",
    mentioned=["cand-2516", "cand-5986", "cand-10499", "cand-1642", "cand-1204", "cand-3944"],
    cited_source_independently_consulted=False)
add_statement(
    N1D, "cand-10500", "cand-10501", "strange_letter_reports_erection_and_requests_drawing", 27, 28,
    "P.366 note 1 says the statue had been erected by October 1777 and reports that on 8 October Strange wrote to G. M. Sasso asking him to get Mingardi to make a drawing of the statue in the Prà della Valle, quoting ‘donata dal nostro Duca’.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The Strange letter and requested drawing have not been independently consulted; the passage does not establish that the drawing was completed. The note directs readers to p.373 note 2, not yet processed.",
    mentioned=["cand-10500", "cand-10501", "cand-2516", "cand-2364", "cand-1669", "cand-10486", "cand-3960", "cand-1204"],
    cited_source_independently_consulted=False,
    cross_reference_text="P.366 note 1 says ‘see p. 373, note 2’; that later note remains to be processed in source order.",
    cross_reference_text_pending=True)

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p366-")}
expected_statement_count = 26
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.366 statements, got {len(new_statement_ids)}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L7-12",
    "note": "P.366 L15 closes the p.365 representation-eligibility statement; p.365 body is fully migrated. S0 remains unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L15-28",
    "note": "Printed p.366 checked against CHP-15.pdf physical p.6. Processes the p.365 eligibility continuation, statue scheme rules and subjects, 1777–1786 progress, Subleyras/Piranesi/Radicchio sequence, and note 1. Note 1 is linked to the Duke of Gloucester statue statement. Printed page ends with ‘and during’; continuation is pending. OCR corrections are recorded in S2 only; S0 unchanged.",
})
coverage_by_id[P365_NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L91-92",
    "note": "P.365 notes 1–2 remain migrated at L91–92. The remaining consolidated notes L93–113 are later page notes and remain pending; p.366 note 1 is located in the p.366 body segment L25–28.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA, "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids), "updated_statements": [P365_PARTIAL],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, P365_NOTES)},
    "printed_page": 366, "pdf_physical_page": 6,
    "open_cross_page_statement": P366_PARTIAL,
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
