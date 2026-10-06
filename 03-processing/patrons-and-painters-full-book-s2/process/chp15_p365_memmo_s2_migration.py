"""Controlled S2 migration for Andrea Memmo's printed p.365 passage and notes."""
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
BODY_PREV = "chp-15:15_CHP-15_sec_ii:l3-4"
BODY = "chp-15:15_CHP-15_sec_ii:l6-12"
BODY_NEXT = "chp-15:15_CHP-15_sec_ii:l14-28"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
PREVIOUS_PARTIAL = "st-chp15-p364-memmo-love-affairs-continuation-partial"
BACKUP_SUFFIX = ".bak-s2-chp15-p365-memmo-apply-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.365 Andrea Memmo S2 migration")
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
    (7, "continued to enjoy (and write about) a series of love affairs with great enthusiasm.1"),
    (7, "in 1775 he was made Proweditore at Padua"),
    (7, "themain concern of his Use"),
    (8, "annual agricultural fair, which had been inaugurated some two or three years earlier?"),
    (8, "In front of the church of S. Giustina lay a vast area of abandoned marsh land, the Pra della Valle (Plate 62)."),
    (8, "the Abate Cerate, to put it into effect (Plate 63)"),
    (10, "eighty-eight statues would be required"),
    (11, "Only nobles or men who had brought particular glory to the"),
    (12, "see Neu-Mayr, 1807."),
    (91, "1 Brunel Ji, 1923."),
    (92, "2 For the history of the Pri della Valle see Radicchio, 1786"),
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
    or coverage_by_id[NOTES]["migration_status"] != "pending"
):
    raise SystemExit("S2 coverage preconditions changed")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10477:
    raise SystemExit("candidate sequence changed; expected max cand-10477")
if PREVIOUS_PARTIAL not in statement_by_id or not statement_by_id[PREVIOUS_PARTIAL]["predicate"].endswith("_partial"):
    raise SystemExit("missing open p.364 love-affairs continuation statement")
for cid in (
    "cand-1642", "cand-1650", "cand-1643", "cand-1411", "cand-1804", "cand-3944",
    "cand-3960", "cand-4014", "cand-4031", "cand-5766", "cand-0623", "cand-9183",
    "cand-8406", "cand-8450", "cand-8108", "cand-8107", "cand-4490", "cand-3398",
    "cand-2769", "cand-3461", "cand-3462", "cand-9501", "cand-9502", "cand-2089",
):
    if cid not in candidate_by_id:
        raise SystemExit(f"required existing candidate missing: {cid}")

new_candidates = [
    ("cand-10478", "Radicchio, 1786, history of Prà della Valle (p.365 note 2 citation locator)", "archive", NOTES, 92,
     "Short-form citation to the history of Prà della Valle. The work title and full bibliographic identity were not independently checked; do not assume its author is the indexed Don Vincenzo Radicchio without later alignment."),
    ("cand-10479", "Neu-Mayr, 1807, figures and inscriptions of Prà della Valle (p.365 note 2 citation locator)", "archive", BODY, 12,
     "Short-form citation preserved from the continuation of p.365 note 2. Full name, work title and publication details are not supplied in this passage and were not independently checked."),
    ("cand-10480", "Annual agricultural fair at Padua mentioned in Andrea Memmo’s p.365 account", "event", BODY, 8,
     "Haskell says it had been inaugurated some two or three years before Memmo arrived in Padua in 1775; retain the approximate date and do not infer an exact founding year."),
    ("cand-10481", "Church of S. Giustina beside the Prà della Valle marshland in Haskell’s p.365 account", "place", BODY, 8,
     "Named as the landmark beside the marshland; this passage does not provide a fuller dedication or independent location record."),
    ("cand-10482", "Provveditore at Padua (office title as printed in Haskell, p.365)", "term", BODY, 7,
     "The printed spelling is retained as seen in CHP-15.pdf. Do not silently normalize or infer the precise legal remit from this passage."),
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

segment_bounds = {BODY: (6, 12), NOTES: (90, 113)}
segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(6, 13)},
    NOTES: {number: source_lines[number - 1] for number in range(90, 114)},
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
    line_offset = segment_offsets[segment_id][source_line]
    occupied = [
        (int(row["start_char"]), int(row["end_char"]))
        for row in mentions + planned_mentions
        if row["segment_id"] == segment_id and line_offset <= int(row["start_char"]) < line_offset + len(line)
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
    mention_id = f"m-chp15-p365-memmo-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions + planned_mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_counter += 1


def quote(segment_id, line_start, line_end):
    first, last = segment_bounds[segment_id]
    if not first <= line_start <= line_end <= last:
        raise SystemExit(f"quote span outside segment {segment_id}: L{line_start}-{line_end}")
    return "\n".join(segment_lines[segment_id][n] for n in range(line_start, line_end + 1))


def footnote(marker, note_line, body_line, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": NOTES,
        "footnote_line_range": f"L{note_line}", "footnote_text_pending": False,
        "footnote_body_link_status": "linked", "footnote_body_line_range": f"L{body_line}",
        "footnote_note_statement_ids": list(statement_ids),
    }


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer="authorial report", speaker="Haskell", qualification="",
                  mentioned=(), **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 365, "pdf_physical_page": 5,
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


# Close the love-affairs sentence opened on p.364; preserve the source-span boundary.
previous = statement_by_id[PREVIOUS_PARTIAL]
previous["predicate"] = previous["predicate"].removesuffix("_partial")
previous["qualifiers"]["predicate_status"] = "complete"
previous["qualifiers"]["qualification"] = (
    "P.365 L7 completes the clause: Memmo continued to enjoy and write about a series of love affairs. "
    "The p.364 source quote remains anchored to its original segment; note 1 is linked to this continuation."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = (
    "P.364 L4 ends ‘and he’; p.365 L7 continues ‘continued to enjoy (and write about) a series of love affairs with great enthusiasm.’"
)
previous["qualifiers"]["cross_reference_text_pending"] = False
previous["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(
    previous["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-9501", "cand-9502"]
))
previous["qualifiers"].update(footnote(1, 91, 7, ["st-chp15-p365-note1-brunelli-1923"]))

# Body mentions and contextual/index cross-references on printed p.365.
add_mention(BODY, "cand-1642", "continued to enjoy (and write about)", 7, "Closes the p.364 partial love-affairs statement.")
add_mention(BODY, "cand-1642", "a series of love affairs", 7)
add_mention(BODY, "cand-1642", "His political career", 7)
add_mention(BODY, "cand-8450", "Doge", 7, "Office/title candidate; Haskell says the chance of appointment was almost certain, not that Memmo held the office.")
add_mention(BODY, "cand-10482", "Proweditore", 7, "OCR surface ‘Proweditore’; p.365 print reads ‘Provveditore’. The S0 source is unchanged.")
add_mention(BODY, "cand-1642", "the patronage", 7)
add_mention(BODY, "cand-1642", "his Use", 7, "OCR reads ‘Use’; p.365 page image reads ‘life’.")
add_mention(BODY, "cand-1642", "Memmo’s ideas", 7)
add_mention(BODY, "cand-8107", "the Enlightenment", 7)
add_mention(BODY, "cand-1642", "he arrived", 8, "Pronoun refers to Andrea Memmo.")
add_mention(BODY, "cand-3944", "Padua", 8, "City candidate linked to the p.365 arrival and project context.")
add_mention(BODY, "cand-8406", "municipal authorities", 8, "Civic-body candidate; exact municipal office is not named in this passage.")
add_mention(BODY, "cand-10480", "annual agricultural fair", 8)
add_mention(BODY, "cand-8108", "The Venetian nobility", 8, "Social-estate candidate; keep distinct from the p.364 aristocracy candidate cand-10473 pending S3.")
add_mention(BODY, "cand-1650", "a suitable site must be found for the dealers", 8, "The index subentry cand-1650 covers Memmo’s Prà della Valle plan.")
add_mention(BODY, "cand-10481", "church of S. Giustina", 8)
add_mention(BODY, "cand-3960", "Pra della Valle", 8, "OCR omits the accent; print reads Prà. The index subentry cand-1804 and plate-caption place cand-3960 remain distinct candidates for S3.")
add_mention(BODY, "cand-4014", "Plate 62", 8, "Reuses the existing Canaletto/Prà della Valle plate candidate and caption.")
add_mention(BODY, "cand-1650", "Memmo decided to reclaim", 8)
add_mention(BODY, "cand-3960", "this land", 8)
add_mention(BODY, "cand-1650", "a canal", 8)
add_mention(BODY, "cand-1650", "an island", 8)
add_mention(BODY, "cand-1650", "the traders", 8)
add_mention(BODY, "cand-1650", "an oval plan", 8)
add_mention(BODY, "cand-5766", "Colosseum", 8, "Reuse the named monument candidate; no specific view or work is inferred.")
add_mention(BODY, "cand-9183", "Padua university", 8)
add_mention(BODY, "cand-0623", "Abate Cerate", 8, "The source OCR reads Cerate; p.365 page image reads Cerato.")
add_mention(BODY, "cand-4031", "Plate 63", 8, "Reuses the existing Cerato proposal drawing candidate.")
add_mention(BODY, "cand-3461", "Italy", 8)
add_mention(BODY, "cand-4490", "Rome", 8)
add_mention(BODY, "cand-1650", "Memmo designed the scheme", 9)
add_mention(BODY, "cand-3461", "Italy", 9)
add_mention(BODY, "cand-3462", "Europe", 9)
add_mention(BODY, "cand-1650", "a scries of statues", 9, "OCR reads ‘scries’; p.365 print reads ‘series’. The S0 source is unchanged.")
add_mention(BODY, "cand-1411", "Lodoli", 9)
add_mention(BODY, "cand-1650", "a plan devised by a pupil", 9)
add_mention(BODY, "cand-1650", "the foundations of the statues", 9)
add_mention(BODY, "cand-1650", "a public gallery", 9)
add_mention(BODY, "cand-8107", "the Enlightenment", 9)
add_mention(BODY, "cand-3398", "Bologna", 10)
add_mention(BODY, "cand-2769", "Vicenza", 10)
add_mention(BODY, "cand-1650", "Memmo’s plan", 10)
add_mention(BODY, "cand-1650", "eighty-eight statues", 10)
add_mention(BODY, "cand-8107", "Venetian Enlightenment", 11, "The phrase begins with ‘the’ at the p.365 page break; the content-bearing name is anchored on p.366 continuation line L11 in the Markdown segment.")
add_mention(BODY, "cand-8108", "Only nobles", 11, "The eligibility sentence continues on p.366; the represented-city clause is not completed here.")
add_mention(BODY, "cand-10479", "Neu-Mayr, 1807", 12, "Printed footnote 2 continues here; note 2’s opening citation is at consolidated L92.")

# Footnote mentions in the consolidated notes block; p.365 note 2 continues at body L12.
add_mention(NOTES, "cand-9502", "Brunel Ji", 91, "OCR corrupts the surname; p.365 page image reads Brunelli.")
add_mention(NOTES, "cand-9501", "1923", 91, "Short citation matches the existing Brunelli locator candidate; cited text was not consulted.")
add_mention(NOTES, "cand-2089", "Radicchio", 92, "Short citation may refer to indexed Don Vincenzo Radicchio (cand-2089); identity is not resolved here.")
add_mention(NOTES, "cand-10478", "1786", 92)

N1 = "st-chp15-p365-note1-brunelli-1923"
N2_RADICCHIO = "st-chp15-p365-note2-radicchio-1786"
N2_NEU_MAYR = "st-chp15-p365-note2-neu-mayr-1807"

add_statement(
    "st-chp15-p365-memmo-career-and-doge", BODY, "cand-1642", "cand-8450",
    "political_career_described_as_impressive_and_memmo_declined_almost_certain_dogeship", 7, 7,
    "Haskell describes Memmo’s political career as impressive and says he turned down an almost certain chance of becoming Doge.",
    qualification="The near certainty is Haskell’s wording; Memmo did not become Doge in this account.",
    mentioned=["cand-1642", "cand-8450"])
add_statement(
    "st-chp15-p365-memmo-appointed-provveditore", BODY, "cand-1642", "cand-10482",
    "appointed_provveditore_at_padua_in_1775", 7, 7,
    "Haskell says Memmo was made Provveditore at Padua in 1775.",
    qualification="The OCR reads ‘Proweditore’; the printed title is Provveditore. Its legal remit is not supplied here.",
    mentioned=["cand-1642", "cand-10482", "cand-3944"])
add_statement(
    "st-chp15-p365-memmo-patronage-main-concern", BODY, "cand-1642", None,
    "patronage_became_main_concern_and_significant_historical_contribution", 7, 7,
    "Haskell says patronage became the main concern of Memmo’s life and remained his one really significant contribution to history.",
    qualification="The claim is Haskell’s retrospective evaluation; the OCR ‘Use’ is corrected to printed ‘life’ only in this S2 reading.",
    mentioned=["cand-1642"])
add_statement(
    "st-chp15-p365-memmo-ideas-new-attitude-to-art", BODY, "cand-1642", "cand-8107",
    "ideas_reflected_new_attitude_to_art_characteristic_of_enlightenment", 7, 7,
    "Haskell says Memmo’s ideas reflected a new attitude to art characteristic of the Enlightenment.",
    qualification="This is Haskell’s framing; the passage does not define a formal program or identify its full scope.",
    mentioned=["cand-1642", "cand-8107"])
add_statement(
    "st-chp15-p365-padua-authorities-request-fair-assistance", BODY, "cand-8406", "cand-1642",
    "municipal_authorities_approached_memmo_for_help_with_annual_agricultural_fair", 8, 8,
    "Haskell says that when Memmo arrived in Padua in 1775, the municipal authorities asked him to take steps to help the annual agricultural fair.",
    qualification="The authorities are unnamed; cand-8406 is used as a civic-body candidate and its cross-chapter identity remains for S3.",
    mentioned=["cand-8406", "cand-1642", "cand-10480", "cand-3944"], relation_candidate=True)
add_statement(
    "st-chp15-p365-fair-inaugurated-two-or-three-years-earlier", BODY, "cand-10480", None,
    "inaugurated_about_two_or_three_years_before_memmos_1775_arrival", 8, 8,
    "Haskell says the annual agricultural fair had been inaugurated some two or three years before Memmo arrived in Padua in 1775.",
    qualification="Retain the approximate interval; no precise founding year is calculated. Printed marker 2 follows this clause, but the note cites sources for Prà della Valle history and figures; do not treat it as direct evidence for an exact fair inauguration date.",
    mentioned=["cand-10480", "cand-1642", "cand-3944"],
    **footnote(2, 92, 8, [N2_RADICCHIO, N2_NEU_MAYR]))
add_statement(
    "st-chp15-p365-first-suggestions-realistic-little-permanent-value", BODY, "cand-1642", None,
    "first_suggestions_realistic_but_of_little_permanent_value", 8, 8,
    "Haskell characterizes Memmo’s first suggestions as realistic enough but of little permanent value.",
    qualification="This is Haskell’s evaluation of the initial proposals.", mentioned=["cand-1642"])
add_statement(
    "st-chp15-p365-entertainment-proposed-for-venetian-nobility", BODY, "cand-1642", "cand-8108",
    "explained_nobility_needed_entertainment_and_proposed_theatres_operas_masked_balls", 8, 8,
    "Haskell says Memmo explained that the Venetian nobility would not come without entertainment and proposed theatres, operas and masked balls.",
    qualification="The statement reports Memmo’s explanation as rendered by Haskell, not an independently measured preference of every noble.",
    mentioned=["cand-1642", "cand-8108", "cand-10473"])
add_statement(
    "st-chp15-p365-dealers-needed-suitable-stall-site", BODY, "cand-1650", None,
    "plan_required_suitable_site_for_dealers_stalls", 8, 8,
    "Haskell says a suitable site also had to be found for dealers to set up their stalls.",
    qualification="No individual dealers or exact site boundaries are named in this statement.",
    mentioned=["cand-1650", "cand-10480"])
add_statement(
    "st-chp15-p365-pra-location-before-s-giustina", BODY, "cand-3960", "cand-10481",
    "abandoned_marshland_of_pra_lay_in_front_of_church_of_s_giustina", 8, 8,
    "Haskell locates the vast area of abandoned marshland called the Prà della Valle in front of the church of S. Giustina.",
    qualification="The place is linked to existing site candidate cand-3960 and Plate 62 candidate cand-4014; printed spelling Prà corrects OCR Pra. The index subentry cand-1804 remains a separate S3 alignment input.",
    mentioned=["cand-3960", "cand-10481", "cand-4014", "cand-1804", "cand-3944"])
add_statement(
    "st-chp15-p365-memmo-reclamation-canal-island", BODY, "cand-1650", "cand-3960",
    "planned_reclamation_to_reduce_flood_risk_with_canal_and_central_traders_island", 8, 8,
    "Haskell says Memmo decided to reclaim the flood-prone land by building a canal and constructing a central island for traders.",
    qualification="This records the proposed plan and purposes; it does not assert completion or a precise construction date.",
    mentioned=["cand-1650", "cand-3960", "cand-10480"], relation_candidate=True)
add_statement(
    "st-chp15-p365-memmo-oval-plan-colosseum", BODY, "cand-1650", "cand-5766",
    "drew_oval_plan_based_on_colosseum", 8, 8,
    "Haskell says Memmo drew an oval plan based on the Colosseum.",
    qualification="No claim is made that the proposed island itself reproduced the Colosseum.",
    mentioned=["cand-1650", "cand-5766", "cand-3960"])
add_statement(
    "st-chp15-p365-memmo-summoned-cerato-to-implement-plan", BODY, "cand-1650", "cand-0623",
    "summoned_padua_architecture_professor_cerato_to_implement_plan", 8, 8,
    "Haskell says Memmo summoned Abate Cerato, a professor of architecture at the University of Padua, to put the plan into effect.",
    qualification="The OCR reads Cerate; p.365 page image reads Cerato. Plate 63’s existing proposal candidate is linked, without asserting that its caption alone resolves every design stage.",
    mentioned=["cand-1650", "cand-0623", "cand-9183", "cand-4031", "cand-1804"], relation_candidate=True)
add_statement(
    "st-chp15-p365-pra-great-town-planning-evaluation", BODY, "cand-1650", None,
    "probably_greatest_italian_town_planning_since_papal_rome_schemes", 8, 8,
    "Haskell says that as a conception the project was probably the greatest example of town planning in Italy since the papal schemes in Rome about 150 years earlier.",
    qualification="Preserves ‘probably’ and records an authorial comparison rather than an independently established ranking or precise chronology.",
    mentioned=["cand-1650", "cand-3461", "cand-4490"])
add_statement(
    "st-chp15-p365-commercial-not-religious-or-family-glory-motive", BODY, "cand-1650", None,
    "commerce_not_religion_or_family_glory_was_mainspring", 8, 8,
    "Haskell contrasts the project’s commercial motive with religion or family glory, saying commerce had become the mainspring.",
    qualification="This is the author’s interpretation of motive, not a direct quotation from Memmo.", mentioned=["cand-1650"])
add_statement(
    "st-chp15-p365-memmo-resource-constraints-and-negotiation", BODY, "cand-1650", None,
    "not_sovereign_unlimited_funds_opposition_required_negotiation_and_fundraising", 9, 9,
    "Haskell says Memmo lacked unlimited sovereign funds, had to overcome opposition through negotiation and persuasion, and above all had to raise money.",
    qualification="No budget total, opponent or negotiation outcome is specified here.", mentioned=["cand-1650", "cand-1642"])
add_statement(
    "st-chp15-p365-subscriptions-for-statue-series", BODY, "cand-1650", None,
    "invited_public_in_italy_and_europe_to_subscribe_to_statue_series_with_limited_donor_choice", 9, 9,
    "Haskell says Memmo invited cooperation from the public across Italy and Europe by opening subscriptions for statues around the island; within limits, donors could choose the subject and artist.",
    qualification="The passage does not identify individual subscribers or say every donor choice was accepted.",
    mentioned=["cand-1650", "cand-3461", "cand-3462"], relation_candidate=True)
add_statement(
    "st-chp15-p365-lodoli-plan-functional-commercial", BODY, "cand-1650", "cand-1411",
    "pupil_of_lodoli_plan_strictly_functional_and_commercially_attractive", 9, 9,
    "Haskell says that, as a plan devised by Lodoli’s pupil, the scheme was strictly functional and a brilliant commercial idea for attracting international funds and support.",
    qualification="This is Haskell’s framing of the scheme and Lodoli relationship; no specific doctrinal proposition is supplied in the sentence.",
    mentioned=["cand-1650", "cand-1643", "cand-1411"], relation_candidate=True)
add_statement(
    "st-chp15-p365-statue-foundations-strengthen-canal-banks", BODY, "cand-1650", None,
    "statue_foundations_would_strengthen_canal_banks", 9, 9,
    "Haskell says the foundations of the statues would strengthen the banks of the canal surrounding the island.",
    qualification="The source describes the design’s intended function; it does not verify construction or structural performance.", mentioned=["cand-1650", "cand-3960"])
add_statement(
    "st-chp15-p365-statues-as-civic-virtue-gallery", BODY, "cand-1650", None,
    "statues_would_form_public_gallery_teaching_civic_virtue", 9, 9,
    "Haskell says the statues would act as a public gallery of exemplars teaching civic virtue, as required by Enlightenment opinion.",
    qualification="This records the stated civic purpose of the proposal, not evidence of its actual educational effect.",
    mentioned=["cand-1650", "cand-8107"])
add_statement(
    "st-chp15-p365-pra-plan-inspired-by-bologna-vicenza", BODY, "cand-1650", None,
    "plan_inspired_by_bologna_and_vicenza_porticoes_shrines_and_pilgrimage_churches", 10, 10,
    "Haskell says Memmo’s plan was inspired by Bologna and Vicenza, where citizens had cooperated in building porticoes with shrines leading to pilgrimage churches outside those towns.",
    qualification="No particular building or exact design element is singled out in this comparison.",
    mentioned=["cand-1650", "cand-3398", "cand-2769"])
add_statement(
    "st-chp15-p365-eighty-eight-statues-and-conditions", BODY, "cand-1650", None,
    "more_ambitious_plan_calculated_eighty_eight_statues_and_set_conditions", 10, 11,
    "Haskell says the proposal was more ambitious, that eighty-eight statues were calculated to be required, and that conditions were laid down which sometimes showed the limitations of the Venetian Enlightenment.",
    qualification="The conditions are not fully enumerated in this segment; eligibility continues on p.366 L15.",
    mentioned=["cand-1650", "cand-8107", "cand-8108"])
add_statement(
    "st-chp15-p365-memmo-representation-eligibility-partial", BODY, "cand-1650", "cand-8108",
    "only_nobles_or_people_with_particular_glory_to_city_could_be_represented_partial", 11, 11,
    "P.365 says only nobles or men who had brought particular glory to the—; the city and the remainder of the eligibility rules continue on p.366.",
    qualification="The sentence is intentionally left partial at the page break; no complete eligibility rule is inferred.",
    mentioned=["cand-1650", "cand-8108"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT],
    cross_reference_text="P.365 L11 ends ‘particular glory to the’; p.366 L15 begins ‘city could be represented; moreover…’.",
    cross_reference_text_pending=True)

add_statement(
    N1, NOTES, "cand-9502", "cand-9501", "note_cites_brunelli_1923", 91, 91,
    "P.365 note 1 cites Brunelli (1923) after Haskell’s account of Memmo’s continuing love affairs.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The print reads Brunelli; the OCR reads ‘Brunel Ji’. The citation matches the existing Brunelli locator candidate, but the work and cited content were not independently consulted.",
    mentioned=["cand-9502", "cand-9501"], cited_source_independently_consulted=False)
add_statement(
    N2_RADICCHIO, NOTES, None, "cand-10478", "footnote_cites_radicchio_1786_for_history_of_pra", 92, 92,
    "P.365 note 2 directs readers to Radicchio (1786) for the history of the Prà della Valle.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="Short-form citation only; the cited work was not independently consulted. The surname may match indexed Don Vincenzo Radicchio (cand-2089), but identity is not asserted.",
    mentioned=["cand-2089", "cand-10478", "cand-3960"],
    cited_source_independently_consulted=False)
add_statement(
    N2_NEU_MAYR, NOTES, None, "cand-10479", "footnote_cites_neu_mayr_1807_for_figures_and_inscriptions", 92, 92,
    "P.365 note 2 directs readers to Neu-Mayr (1807) for figures and inscriptions associated with the Prà della Valle.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="Short-form citation only; the sec_ii OCR splits the note, with its printed continuation at body-source L12. The p.365 image verifies the complete note; the cited work was not independently consulted.",
    mentioned=["cand-10479", "cand-3960"],
    cited_source_independently_consulted=False,
    cross_reference_segments=[BODY],
    cross_reference_text="Printed p.365 note 2 continues at sec_ii L12: ‘see Neu-Mayr, 1807.’",
    cross_reference_text_pending=False)

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p365-")}
expected_statement_count = 26
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.365 statements, got {len(new_statement_ids)}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-4",
    "note": "P.364 Andrea Memmo opening paragraph is now closed by printed p.365 L7: he continued to enjoy and write about a series of love affairs. Footnote 1 at p.365 L7 is linked to consolidated note L91. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L7-12",
    "note": "Printed p.365 checked against CHP-15.pdf physical p.5. Processes Memmo’s political career and Padua appointment, patronage, the agricultural fair request, Prà della Valle location and initial reclamation/statue-plan concepts; p.365 note 1 is at consolidated L91 and note 2 begins at L92 with its printed continuation at body-source L12. The final representation-eligibility sentence ends ‘to the’ and continues at p.366 L15, retained as a partial statement. S2 visual corrections are logged without changing S0.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L91-92",
    "note": "P.365 notes 1–2 are migrated: Brunelli 1923 at L91; Radicchio 1786 at L92 and the printed continuation ‘see Neu-Mayr, 1807’ at body-source L12. The remaining consolidated notes L93–113 belong to later p.367–372 passages and remain pending.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "updated_statements": [PREVIOUS_PARTIAL],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 365,
    "pdf_physical_page": 5,
    "open_cross_page_statement": "st-chp15-p365-memmo-representation-eligibility-partial",
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
