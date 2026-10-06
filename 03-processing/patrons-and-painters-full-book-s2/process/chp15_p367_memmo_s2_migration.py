"""Controlled S2 migration for printed p.367 body and notes 1–4."""
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
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l14-28"
BODY = "chp-15:15_CHP-15_sec_ii:l30-36"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l38-47"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
P366_PARTIAL = "st-chp15-p366-memmo-expert-patron-reputation-partial"
BACKUP_SUFFIX = ".bak-s2-chp15-p367-memmo-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.367 Andrea Memmo S2 migration")
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
    (31, "Elementi dell’Architettura lodolianaf"),
    (31, "He must - certainly have felt"),
    (32, "In 1787 he returned to Venice"),
    (32, "fifty-eight of Lodoli’s Apologhi"),
    (32, "The panegyric which greeted his return"),
    (33, "plans for an amphitheatre were rejected by the municipal authorities"),
    (33, 'Casanova and asked" whether his patron at Dux'),
    (34, "Giovanni Dubravio Skala, perhaps, from Pilsen"),
    (35, "Giovanni Adalbertho Veith, a student of some fame in 1709?4"),
    (36, "notable, variations in quality and style"),
    (36, "between some noble donor’s insignificant ancestor to Livy or Galileo"),
    (36, "dust robs the Prà della"),
    (93, "See della Valle, HI, p. 459"),
    (93, "P. Valloni"),
    (94, "Apologhi immaginati"),
    (94, "Procurala di S. Marco"),
    (95, "Venezia, Zana, 1787"),
    (96, "Molmenti: Un nobil huomo, pp. 143-4"),
]
for line_number, required in required_source:
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
    or coverage_by_id[NOTES]["source_line_ranges"] != "L91-92"
):
    raise SystemExit("S2 coverage preconditions changed")
if P366_PARTIAL not in statement_by_id:
    raise SystemExit(f"missing p.366 partial statement: {P366_PARTIAL}")
if statement_by_id[P366_PARTIAL]["qualifiers"].get("predicate_status") != "partial":
    raise SystemExit("p.366 cross-page statement is no longer partial")
if any(row["segment_id"] == BODY for row in mentions):
    raise SystemExit("p.367 body mention rows already exist")
if any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.367 body statements already exist")
if any(row.get("statement_id", "").startswith("st-chp15-p367-") for row in statements):
    raise SystemExit("p.367 footnote statements already exist")

new_candidates = [
    ("cand-10503", "Unidentified Della Valle citation, volume III, p.459, quoted in Haskell p.367 note 1", "archive", 93,
     "Citation locator as printed by Haskell; the cited source and the identity/title behind ‘Della Valle’ have not been independently resolved."),
    ("cand-10504", "P. Vallotti, person named in the p.367 note 1 quotation", "person", 93,
     "The note prints the abbreviation ‘P.’ and surname Vallotti; no identity is inferred from the quotation."),
    ("cand-10505", "Unidentified 1787 panegyric for Andrea Memmo’s solemn entry as Procurator di San Marco", "work", 95,
     "Haskell identifies an oration printed in Venice by Zatta in 1787; the source is not independently consulted."),
    ("cand-10506", "Unrealised amphitheatre proposal for the Prà della Valle, rejected by municipal authorities", "event", 33,
     "Haskell says the more grandiose plan was rejected; no design, architect, or exact authority is identified."),
    ("cand-10507", "Dux, place associated with the Count of Waldstein in Haskell’s p.367 account", "place", 33,
     "Retain the source name Dux; modern place identification is not established in this passage."),
    ("cand-10508", "Pilsen, place of origin named for Giovanni Dubravio Skala", "place", 34,
     "Source-level place mention; no additional geographic normalization is needed for S2."),
    ("cand-10509", "Unnamed municipal authorities who rejected the amphitheatre plan in Haskell’s p.367 account", "institution", 33,
     "The passage does not specify the exact body or its formal name."),
    ("cand-10510", "Rococo sculpture represented at the Prà della Valle in Haskell’s p.367 account", "term", 36,
     "A stylistic category in Haskell’s assessment of the surviving sculpture; not a claim about every statue."),
    ("cand-10511", "Middle Ages as the period assigned to many heroes represented at the Prà della Valle", "term", 36,
     "A periodization claim attributed to Haskell; individual statue dates are not supplied here."),
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
    BODY: {number: source_lines[number - 1] for number in range(30, 37)},
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
    mention_id = f"m-chp15-p367-memmo-{mention_counter:04d}"
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
        "printed_page": 367, "pdf_physical_page": 7,
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


def footnote(marker, note_line, body_line, statement_ids, body_link_note=""):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{note_line}-L{note_line}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(statement_ids),
        "footnote_link_note": body_link_note,
    }


# Anchor source mentions to the OCR text; print corrections stay in S2 notes.
add_mention("cand-1647", "Elementi dell’Architettura lodoliana", BODY, 31, "Print has a superscript note 1 after the title; OCR renders it as a trailing ‘f’.")
add_mention("cand-4490", "Rome", BODY, 31)
add_mention("cand-1411", "his master’s", BODY, 31, "The referent is Carlo Lodoli in the adjacent clause.")
add_mention("cand-1643", "teaching of", BODY, 31, "Index candidate for Memmo and Lodoli; source-level relation only.")
add_mention("cand-1411", "Lodoli", BODY, 31)
add_mention("cand-1804", "Prato della Valle", BODY, 31, "OCR reads Prato; p.367 print reads Prà della Valle.")
add_mention("cand-2719", "Venice", BODY, 32)
add_mention("cand-8449", "Procuratore di San Marco", BODY, 32)
add_mention("cand-1644", "appointed two years earlier", BODY, 32)
add_mention("cand-1642", "he published", BODY, 32, "Andrea Memmo is the continuing subject.")
add_mention("cand-1411", "Lodoli’s", BODY, 32)
add_mention("cand-1651", "Apologhi", BODY, 32)
add_mention("cand-10505", "panegyric", BODY, 32)
add_mention("cand-1804", "Prà della", BODY, 32, "The place-name is split across S0 lines 32–33; L33 begins ‘Valle’.")
add_mention("cand-1804", "Valle", BODY, 33, "Continuation of the p.367 L32 Prà della Valle mention; superscript note 3 follows.")
add_mention("cand-1642", "Memmo himself", BODY, 33)
add_mention("cand-10506", "plans for an amphitheatre", BODY, 33)
add_mention("cand-10509", "municipal authorities", BODY, 33)
add_mention("cand-1650", "further statues", BODY, 33)
add_mention("cand-0591", "Casanova", BODY, 33)
add_mention("cand-10507", "Dux", BODY, 33)
add_mention("cand-2797", "the Count of", BODY, 33, "The name continues across the source line break at L34.")
add_mention("cand-2436", "Giovanni Dubravio Skala", BODY, 34)
add_mention("cand-2797", "Waldstein", BODY, 34, "Continuation of the Count of Waldstein mention split at L33–34.")
add_mention("cand-10508", "Pilsen", BODY, 34)
add_mention("cand-1803", "Padua", BODY, 34)
add_mention("cand-8351", "League of Cambrai", BODY, 34)
add_mention("cand-2708", "Giovanni Adalbertho Veith", BODY, 35)
add_mention("cand-1804", "Prato della Valle", BODY, 36, "OCR reads Prato; p.367 print reads Prà della Valle.")
add_mention("cand-0532", "Canova", BODY, 36)
add_mention("cand-0536", "a statue of the", BODY, 36, "The statue candidate is linked to the adjacent Marchese Poleni mention.")
add_mention("cand-1968", "Marchese Poleni", BODY, 36)
add_mention("cand-2750", "Leonardo Venier", BODY, 36)
add_mention("cand-0534", "the sculptor’s own statue", BODY, 36, "The p.367 index identifies the statue of Canova; retain this identity for S3 alignment.")
add_mention("cand-0537", "Antonio Cappello", BODY, 36)
add_mention("cand-1020", "Giovanni Ferrari", BODY, 36)
add_mention("cand-1804", "Prato della Valle", BODY, 36, "OCR reads Prato; p.367 print reads Prà della Valle.")
add_mention("cand-10510", "rococo sculpture", BODY, 36)
add_mention("cand-6439", "neo-classicism", BODY, 36)
add_mention("cand-6836", "Livy", BODY, 36)
add_mention("cand-1105", "Galileo", BODY, 36)
add_mention("cand-10511", "Middle Ages", BODY, 36)
add_mention("cand-1804", "Prà della", BODY, 36, "The sentence continues on p.368 L39 with ‘Valle of the effect’." )

# Notes are in the consolidated source segment, not the body segment.
add_mention("cand-10503", "della Valle, HI, p. 459", NOTES, 93, "OCR reads HI; p.367 print reads III.")
add_mention("cand-1804", "prato della Valle", NOTES, 93)
add_mention("cand-10504", "P. Valloni", NOTES, 93, "OCR reads Valloni; p.367 print reads Vallotti.")
add_mention("cand-1411", "sistema Lodoliano", NOTES, 93, "Italian wording retained from Haskell’s quoted passage.")
add_mention("cand-1647", "Elementi", NOTES, 93)
add_mention("cand-1651", "Apologhi immaginati", NOTES, 94)
add_mention("cand-1411", "Carlo de’ Conti Lodoli", NOTES, 94)
add_mention("cand-9736", "Min. Osservante", NOTES, 94)
add_mention("cand-1642", "Andrea Memmo", NOTES, 94)
add_mention("cand-8449", "Procurala di S. Marco", NOTES, 94, "OCR reads Procurala; print reads Procuratia di S. Marco.")
add_mention("cand-10052", "Bassano", NOTES, 94)
add_mention("cand-2122", "Remondini", NOTES, 94)
add_mention("cand-10505", "A Sua Eccellenza", NOTES, 95, "Opening words of the unidentified oration title; the complete title is preserved in the note statement.")
add_mention("cand-1642", "Andrea Memmo", NOTES, 95)
add_mention("cand-8449", "Procurator di San Marco", NOTES, 95)
add_mention("cand-2719", "Venezia", NOTES, 95)
add_mention("cand-2865", "Zana", NOTES, 95, "OCR reads Zana; p.367 print reads Zatta.")
add_mention("cand-10474", "Molmenti", NOTES, 96)
add_mention("cand-10475", "Un nobil huomo", NOTES, 96)
add_mention("cand-1642", "Memmo", NOTES, 96)
add_mention("cand-10476", "Torcellan", NOTES, 96)

N1A = "st-chp15-p367-note1-della-valle-quotation"
N1B = "st-chp15-p367-note1-elementi-first-volume-1786"
N1C = "st-chp15-p367-note1-elementi-completion-1834"
N2A = "st-chp15-p367-note2-apologhi-publication-1787"
N3A = "st-chp15-p367-note3-memmo-panegyric-1787"
N4A = "st-chp15-p367-note4-memmo-friends-citations"

N1_LINK = footnote(1, 93, 31, [N1A, N1B, N1C], "The printed marker follows the Elementi title; the note also bears on the Prà/Lodoli claim.")
N2_LINK = footnote(2, 94, 32, [N2A])
N3_LINK = footnote(3, 95, 33, [N3A])
N4_LINK = footnote(4, 96, 35, [N4A], "Marker follows the Veith sentence; the note's second citation concerns Memmo writing to friends, including the immediately preceding letter context.")

add_statement(
    "st-chp15-p367-elementi-publication-in-rome", "cand-1642", "cand-1647",
    "published_elementi_in_rome_during_last_year", BODY, 31, 31,
    "Haskell says that during his last year in Rome Andrea Memmo published the Elementi dell’Architettura lodoliana.",
    qualification="The exact year is not stated in the body; p.367 note 1 gives the first volume as 1786. The work has not been independently consulted.",
    mentioned=["cand-1642", "cand-1647", "cand-4490"], **N1_LINK)
add_statement(
    "st-chp15-p367-elementi-account-of-lodoli-theories", "cand-1647", "cand-1411",
    "described_as_first_and_only_complete_account_of_lodoli_theories", BODY, 31, 31,
    "Haskell describes the Elementi as the first and only work to give a complete account of Carlo Lodoli’s architectural theories.",
    qualification="This is Haskell’s characterization, not an independently verified bibliographic conclusion.",
    mentioned=["cand-1647", "cand-1411"], **N1_LINK)
add_statement(
    "st-chp15-p367-prato-utilitarian-basis-tribute-to-lodoli", "cand-1650", "cand-1411",
    "haskell_inference_utilitarian_prato_as_tribute_to_lodoli", BODY, 31, 31,
    "Haskell says Memmo must certainly have felt that the essentially utilitarian basis of the Prà della Valle was as much a tribute to Lodoli’s teaching as the Elementi was a defence of his system.",
    qualification="Retain Haskell’s inference (‘must certainly have felt’); the printed page reads Prà where OCR has Prato.",
    mentioned=["cand-1642", "cand-1650", "cand-1411", "cand-1647"], **N1_LINK)
add_statement(
    "st-chp15-p367-memmo-return-procurator-1787", "cand-1642", "cand-8449",
    "returned_to_venice_and_assumed_procurator_office_1787", BODY, 32, 32,
    "Haskell says Memmo returned to Venice in 1787 to take up the post of Procuratore di San Marco.",
    mentioned=["cand-1642", "cand-2719", "cand-8449"])
add_statement(
    "st-chp15-p367-memmo-appointment-two-years-before-1787", "cand-1642", "cand-1644",
    "appointed_procurator_two_years_before_1787_return", BODY, 32, 32,
    "Haskell says Memmo had been appointed to the Procuratore di San Marco two years before his 1787 return.",
    qualification="The source gives a relative interval; no exact appointment date is inferred.",
    mentioned=["cand-1642", "cand-1644", "cand-8449"])
add_statement(
    "st-chp15-p367-apologhi-publication-and-content", "cand-1642", "cand-1651",
    "published_58_lodoli_apologhi_to_celebrate_official_entry", BODY, 32, 32,
    "Haskell says Memmo published fifty-eight of Lodoli’s Apologhi to celebrate his official assumption of office.",
    qualification="The precise publication title and imprint are transcribed in p.367 note 2; the edition has not been independently consulted.",
    mentioned=["cand-1642", "cand-1411", "cand-1651", "cand-8449"], **N2_LINK)
add_statement(
    "st-chp15-p367-apologhi-satirised-leading-figures", "cand-1651", None,
    "apologhi_satirised_leading_venetian_figures", BODY, 32, 32,
    "Haskell describes the Apologhi as incisive fables that satirised many leading figures of Venetian society.",
    mentioned=["cand-1651"], **N2_LINK)
add_statement(
    "st-chp15-p367-panegyric-praise-and-memmo-dissatisfaction", "cand-10505", "cand-1642",
    "panegyric_praises_prato_organisation_but_memmo_dissatisfied", BODY, 32, 33,
    "Haskell says the panegyric greeting Memmo’s return praised his achievement in organising the Prà della Valle.",
    qualification="The source for the panegyric is identified in note 3 but has not been independently consulted.",
    mentioned=["cand-10505", "cand-1642", "cand-1650", "cand-1804"], **N3_LINK)
add_statement(
    "st-chp15-p367-memmo-dissatisfied-with-progress", "cand-1642", "cand-1650",
    "memmo_far_from_satisfied_with_prato_progress", BODY, 33, 33,
    "Haskell says Memmo himself was far from satisfied with the progress made at the Prà della Valle.",
    mentioned=["cand-1642", "cand-1650", "cand-1804"])
add_statement(
    "st-chp15-p367-debts-amphitheatre-and-statue-progress", "cand-1642", "cand-10506",
    "huge_prato_debts_had_to_be_cleared", BODY, 33, 33,
    "Haskell says huge debts at the Prà della Valle had to be cleared.",
    mentioned=["cand-1642", "cand-1650", "cand-1804"],
    cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p367-amphitheatre-plan-rejected-further-statues-needed", "cand-10509", "cand-10506",
    "municipal_authorities_rejected_amphitheatre_plan_and_more_statues_needed", BODY, 33, 33,
    "Haskell says municipal authorities rejected the more grandiose amphitheatre plan and further statues still needed to be installed.",
    qualification="The municipal body is unnamed; the passage does not identify a design or completed amphitheatre project.",
    mentioned=["cand-1642", "cand-10506", "cand-10509", "cand-1650"],
    cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p367-letter-to-casanova-about-waldstein", "cand-1642", "cand-2797",
    "memmo_via_casanova_asks_waldstein_about_statue_funding", BODY, 33, 34,
    "Haskell says Memmo wrote to his old friend Casanova asking whether Casanova’s patron at Dux, the Count of Waldstein, might pay for one statue.",
    qualification="The passage reports a question/proposal, not an accepted commission or payment; the cited correspondence has not been consulted.",
    mentioned=["cand-1642", "cand-0591", "cand-2797", "cand-10507", "cand-1650"],
    cross_reference_segments=[NOTES], cross_reference_text="P.367 note 4 cites sources for Memmo writing to friends; note 4 is in the consolidated note segment L96.",
    cross_reference_text_pending=False)
add_statement(
    "st-chp15-p367-skala-possible-statue-subject", "cand-2436", "cand-2797",
    "skala_suggested_as_possible_subject_for_waldstein_statue", BODY, 34, 34,
    "Haskell tentatively suggests Giovanni Dubravio Skala, perhaps from Pilsen, as one possible subject for the statue; he describes him as the first German student to study at Padua after the League of Cambrai.",
    qualification="The question mark and ‘perhaps’ are retained; neither the identity claim nor the proposed commission is independently verified.",
    mentioned=["cand-2436", "cand-10508", "cand-1803", "cand-8351", "cand-2797"],
    cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p367-veith-alternative-statue-subject", "cand-2708", "cand-2797",
    "veith_alternative_possible_subject_and_1709_fame", BODY, 35, 35,
    "Haskell offers Giovanni Adalbertho Veith as an alternative possible subject and calls him a student of some fame in 1709.",
    qualification="This remains a suggestion in Memmo’s reported letter context; p.367 note 4 is linked at the printed marker but its citations are not independently consulted.",
    mentioned=["cand-2708", "cand-2797"], **N4_LINK)
add_statement(
    "st-chp15-p367-results-difficult-to-assess", "cand-1650", None,
    "haskell_says_final_results_difficult_to_assess", BODY, 36, 36,
    "Haskell says the final results of the Prà della Valle are difficult to assess.",
    mentioned=["cand-1650", "cand-1804"])
add_statement(
    "st-chp15-p367-patronage-and-speed-caused-variation", "cand-1650", None,
    "divided_patronage_and_low_cost_speed_led_to_variations", BODY, 36, 36,
    "Haskell attributes notable variations in quality and style to the division of patronage and anxiety to complete the work cheaply and quickly.",
    qualification="The OCR comma in ‘notable, variations’ is not supported by the print, which breaks ‘notable’ across a line with a hyphen.",
    mentioned=["cand-1650"])
add_statement(
    "st-chp15-p367-canova-poleni-statue-for-venier", "cand-0532", "cand-0536",
    "canova_commissioned_1781_for_poleni_statue_for_venier", BODY, 36, 36,
    "Haskell says Canova was commissioned in 1781 to make a statue of Marchese Poleni for Leonardo Venier.",
    mentioned=["cand-0532", "cand-0536", "cand-1968", "cand-2750"])
add_statement(
    "st-chp15-p367-canova-only-sculptor-survived-his-age", "cand-0532", None,
    "canova_only_sculptor_involved_to_survive_his_age", BODY, 36, 36,
    "Haskell says that among the sculptors involved only Canova had survived his age.",
    qualification="‘Survived his age’ is retained as Haskell’s wording/evaluation; it is not normalized into a precise survival or reputation claim.",
    mentioned=["cand-0532"])
add_statement(
    "st-chp15-p367-canova-statue-commissioned-by-cappello-from-ferrari", "cand-0534", "cand-0537",
    "canova_statue_commissioned_by_cappello_from_ferrari", BODY, 36, 36,
    "Haskell says that within fifteen years Canova’s own statue, commissioned by Antonio Cappello from Giovanni Ferrari, was to take its place among the Prà della Valle statues.",
    qualification="The relative interval is preserved; no exact installation date is inferred.",
    mentioned=["cand-0534", "cand-0532", "cand-0537", "cand-1020", "cand-1804"])
add_statement(
    "st-chp15-p367-canova-statue-only-contemporary-honoured", "cand-0534", None,
    "canova_only_contemporary_honoured_and_reputation_tribute", BODY, 36, 36,
    "Haskell calls Canova’s statue the only contemporary honoured among the great and legendary heroes and an astonishing tribute to the artist’s reputation.",
    qualification="This is Haskell’s assessment of the statue’s place in the scheme.", mentioned=["cand-0534", "cand-0532"])
add_statement(
    "st-chp15-p367-sculptural-quality-and-rococo-remains", "cand-1650", "cand-10510",
    "competence_elegance_and_rococo_remains_at_prato", BODY, 36, 36,
    "Haskell says many other statues show competence and sometimes graceful elegance, making the Prà della Valle one of the best places in Italy to see remaining rococo sculpture before neo-classicism swept it away.",
    qualification="Aesthetic evaluation attributed to Haskell; OCR ‘Prato’ is corrected to print ‘Prà’ in S2 only.",
    mentioned=["cand-1650", "cand-1804", "cand-10510", "cand-6439", "cand-3461"])
add_statement(
    "st-chp15-p367-hero-subjects-and-medieval-costumes", "cand-1650", None,
    "heroes_range_from_ancestors_to_livy_galileo_and_many_are_medieval", BODY, 36, 36,
    "Haskell says the celebrated heroes range in distinction from a noble donor’s insignificant ancestor to Livy or Galileo; many date from the Middle Ages, and their costumes vary in accuracy and seriousness.",
    qualification="No specific anonymous ancestor or unmentioned statue is identified.",
    mentioned=["cand-1650", "cand-6836", "cand-1105", "cand-10511"])
add_statement(
    "st-chp15-p367-climate-and-prato-impression-partial", "cand-1804", None,
    "time_climate_and_summer_conditions_modify_prato_impression_partial", BODY, 36, 36,
    "Haskell says time and the Italian climate have modified the original impression; in summer the vegetation withers and dust robs the Prà della Valle of its effect.",
    qualification="The sentence ends mid-name at ‘the Prà della’ and continues on p.368; its completion remains pending.",
    mentioned=["cand-1804"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT], cross_reference_text="P.367 L36 ends ‘dust robs the Prà della’; p.368 L39 continues ‘Valle of the effect…’.",
    cross_reference_text_pending=True)

add_statement(
    N1A, None, "cand-10503", "note_quotes_della_valle_on_prato_lodoli_and_patronage", NOTES, 93, 93,
    "Haskell’s note quotes a passage cited to Della Valle, volume III, p.459, praising the Prà della Valle statues, the partly published Lodolian system, and its addressee as among the first patrons.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The Italian passage is reproduced by Haskell; the cited source is not independently consulted. The second-person addressee is contextually associated with Memmo, without external verification.",
    mentioned=["cand-10503", "cand-1642", "cand-1804", "cand-10504", "cand-1411", "cand-1647"],
    cited_source_independently_consulted=False)
add_statement(
    N1B, "cand-1642", "cand-1647", "note_says_only_first_elementi_volume_published_1786", NOTES, 93, 93,
    "P.367 note 1 says that for some reason Memmo published only the first volume of the Elementi in 1786.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The note’s wording ‘for some reason’ signals that it does not explain why; the work has not been independently consulted.",
    mentioned=["cand-1642", "cand-1647"], cited_source_independently_consulted=False)
add_statement(
    N1C, "cand-1642", "cand-1647", "note_says_elementi_completed_before_death_full_edition_1834", NOTES, 93, 93,
    "P.367 note 1 says Memmo completed the whole work before his death, but the full two-volume edition did not appear until 1834.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="Recorded as Haskell’s note, not independently verified publication history.",
    mentioned=["cand-1642", "cand-1647"], cited_source_independently_consulted=False)
add_statement(
    N2A, "cand-1642", "cand-1651", "note_gives_apologhi_title_imprint_and_occasion_1787", NOTES, 94, 94,
    "P.367 note 2 supplies the full title of the Apologhi, attributes them to Carlo de’ Conti Lodoli, and gives Bassano [Remondini], 1787, as the imprint for publication on the occasion of Memmo’s solemn entry as Procurator di San Marco.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The title and imprint are transcribed from Haskell’s note; the edition has not been independently consulted. OCR ‘Procurala’ is corrected to the printed ‘Procuratia’ in S2 only.",
    mentioned=["cand-1651", "cand-1411", "cand-9736", "cand-1642", "cand-8449", "cand-10052", "cand-2122"],
    cited_source_independently_consulted=False)
add_statement(
    N3A, "cand-10505", "cand-1642", "note_identifies_1787_panegyric_oration_for_memmo_entry", NOTES, 95, 95,
    "P.367 note 3 identifies an oration for Andrea Memmo’s solemn entry as Procurator di San Marco, printed in Venice by Zatta in 1787.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The note is linked to the panegyric statement on the preceding body lines; the oration has not been independently consulted. OCR ‘Zana’ is corrected to print ‘Zatta’ in S2 only.",
    mentioned=["cand-10505", "cand-1642", "cand-8449", "cand-2719", "cand-2865"],
    cited_source_independently_consulted=False)
add_statement(
    N4A, "cand-1642", "cand-10475", "note_cites_molmenti_and_torcellan_on_memmo_letters", NOTES, 96, 96,
    "P.367 note 4 cites Molmenti’s Un nobil huomo, pages 143–144, and directs readers to Torcellan (1963) for other examples of Memmo writing to friends in this way.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="Neither cited work has been independently consulted. The printed marker follows the Veith sentence, while the second citation concerns Memmo’s letter-writing context on the same page.",
    mentioned=["cand-1642", "cand-10474", "cand-10475", "cand-10476"],
    cited_source_independently_consulted=False)

new_statement_ids = {
    row["statement_id"] for row in statements
    if row["statement_id"].startswith("st-chp15-p367-")
}
expected_statement_count = 29
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.367 statements, got {len(new_statement_ids)}")

previous = statement_by_id[P366_PARTIAL]
previous["predicate"] = "memmo_reputation_expert_patron_great_and_elementi_published_in_final_rome_year"
previous["qualifiers"]["predicate_status"] = "complete"
previous["qualifiers"]["claim"] = (
    "Haskell says Memmo’s reputation as an expert and patron was by then very great, and during his last year in Rome he published the Elementi dell’Architettura lodoliana."
)
previous["qualifiers"]["qualification"] = (
    "P.366 L24 ends ‘and during’; p.367 L31 continues the sentence. OCR reads ‘dining’ on p.366, while the print reads ‘during’."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = (
    "P.366 L24 ends ‘and during’; p.367 L31 continues ‘his last year in Rome he published the Elementi dell’Architettura lodoliana’."
)
previous["qualifiers"]["cross_reference_text_pending"] = False
previous["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
    previous["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-1647", "cand-4490"]
))

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L15-28",
    "note": "P.367 L31 closes the p.366 final sentence about Memmo’s reputation and publication of the Elementi. S0 remains unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L31-36",
    "note": "Printed p.367 checked against CHP-15.pdf physical p.7. Processes Memmo’s Elementi and Lodoli account, 1787 return and Apologhi, Prà progress, the Waldstein proposal, sculptural assessments, and notes 1–4 at consolidated L93–96. The final sentence ends mid-name ‘Prà della’ and continues at p.368 L39. Print corrections are recorded in S2 only; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L91-96",
    "note": "P.365 notes 1–2 at L91–92 and p.367 notes 1–4 at L93–96 are migrated. Remaining consolidated notes L97–113 belong to later pages and remain pending.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA, "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates), "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids), "updated_statements": [P366_PARTIAL],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 367, "pdf_physical_page": 7,
    "open_cross_page_statement": "st-chp15-p367-climate-and-prato-impression-partial",
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
