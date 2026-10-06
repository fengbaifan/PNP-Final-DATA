"""Controlled S2 migration for printed p.344; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l116-122"
PREVIOUS = "chp-13:13_CHP-13_intro:l107-114"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BODY_SHA = "2eee99ac3f4b0588c8491bc9a2987eb8817d8e07774747df9d898967e4fcc16b"
BACKUP_SUFFIX = ".bak-s2-chp13-p344-20261003"
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.344 S2 migration")
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
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[115] != "[Page 344]":
    raise SystemExit("p.344 page anchor changed")
body_text = "\n".join(source_lines[115:122])
if hashlib.sha256(body_text.encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("p.344 source segment changed")
for line, required in {
    117: "Dactyliotheca Ant. M. Zanetti",
    118: "the Queen of Sweden, who was eventually chosen",
    119: "Rosalba Camera",
    120: "Le Arti che vanno per via nella Città di Venezia",
    121: "turn over each zecchino two",
    122: "Félicita Sartori as an engraver",
}.items():
    if required not in source_lines[line - 1]:
        raise SystemExit(f"required p.344 text missing at L{line}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (10090, 10103, 21763, 9695):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment_id in (BODY, PREVIOUS, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f"required coverage row missing: {segment_id}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.344 is not queued/pending")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.343 is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("chapter 13 notes are not queued/pending")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.344 rows already exist")

prior_catalogue = candidate_by_id.get("cand-10012")
if not prior_catalogue or prior_catalogue["canonical_name"] != "Unspecified Albrizzi publication of gems in A. M. Zanetti’s collection":
    raise SystemExit("p.337 descriptive Albrizzi catalogue candidate changed")
if prior_catalogue["suggested_type"] != "archive":
    raise SystemExit("p.337 Albrizzi catalogue candidate is not an archive")
previous_statement_id = "st-chp13-p343-delle_antiche_statue_publication_history"
previous_statement = statement_by_id.get(previous_statement_id)
if not previous_statement or previous_statement["object_candidate_id"] != "cand-2846":
    raise SystemExit("p.343 Delle Antiche publication statement changed")
previous_work_mention = next(
    (row for row in mentions
     if row["segment_id"] == PREVIOUS and row["surface_form"] == "Delle Antiche Statue Greche e Romane"),
    None,
)
if not previous_work_mention or previous_work_mention["candidate_id"] != "cand-2846":
    raise SystemExit("p.343 Delle Antiche title mention changed")

# The new page identifies the earlier p.337 description as the named Dactyliotheca.
prior_catalogue["canonical_name"] = "Dactyliotheca Ant. M. Zanetti"
prior_catalogue["detail"] = (
    "P.344 identifies this as the illustrated catalogue of A. M. Zanetti's collection of gems and medals, "
    "published in 1749 by Albrizzi. This is the earlier Albrizzi publication described on p.337; keep "
    "the indexed person entries and their subentries separate for S3 identity alignment."
)

candidate_specs = [
    ("cand-10104", "Delle Antiche Statue Greche e Romane", "archive",
     "A. M. Zanetti's book begun in 1725 and published fifteen years later by Albrizzi. The index records the title under Zanetti; this row represents the distinct documentary work.", PREVIOUS, 114),
    ("cand-10105", "Francesco Gori (Florentine antiquary; identity pending)", "person",
     "Named as the writer of a Latin commentary for the Dactyliotheca. Resolve identity in S3.", BODY, 118),
    ("cand-10106", "Unnamed King of Poland considered for dedication of the Dactyliotheca", "person",
     "Only the title is given; the text says he was considered before the Queen of Sweden. Do not infer identity.", BODY, 118),
    ("cand-10107", "Unnamed Queen of Sweden chosen as dedicatee of the Dactyliotheca", "person",
     "Only the title is given. The text says she was eventually chosen, but does not establish that a dedication was printed.", BODY, 118),
    ("cand-10108", "Unidentified operatic caricatures drawn by A. M. Zanetti", "work",
     "A group of caricatures of unnamed leading operatic figures; no individual titles or sitters are supplied.", BODY, 119),
    ("cand-10109", "Vari Capricci by Giambattista Tiepolo", "work",
     "The printed title is Vari Capricci. Haskell invokes the series in his interpretation of Zanetti's significance for Tiepolo.", BODY, 119),
    ("cand-10110", "Engravings by Gaetano Zompini after Castiglione drawings owned by A. M. Zanetti", "work",
     "The source describes a series but gives no individual titles or count. Keep distinct from Zanetti's twelve Castiglione drawings engraved in 1759.", BODY, 119),
    ("cand-10111", "Le Arti che vanno per via nella Città di Venezia", "work",
     "Zompini made drawings for this work in 1753. Retain Haskell's evaluative description as authorial interpretation.", BODY, 120),
    ("cand-10112", "Collection of Felicita Sartori’s works owned by A. M. Zanetti", "",
     "A personal art collection, distinct from the individual works. The current taxonomy has no personal collection type, so type remains undecided; no individual works or count are specified.", BODY, 122),
]
new_candidates = []
for cid, name, kind, detail, ref_segment, line in candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"p.344 candidate ID already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{ref_segment}#L{line}",
    })
    new_candidates.append(row)
all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}

# Split the p.343 compound publication claim and attach its exact title to a work candidate.
previous_work_mention["candidate_id"] = "cand-10104"
previous_statement["subject_candidate_id"] = "cand-10104"
previous_statement["object_candidate_id"] = None
previous_statement["predicate"] = "begun_in_1725"
previous_statement["qualifiers"].update({
    "claim": "Haskell says Delle Antiche Statue Greche e Romane was begun in 1725.",
    "mentioned_candidate_ids": ["cand-10104"],
    "relation_candidate": False,
    "qualification": "The p.343 source sentence records the start date; its separate publication statement follows below.",
})
publisher_statement = {
    "statement_id": "st-chp13-p343-delle_antiche_statue-published_by_albrizzi",
    "segment_id": PREVIOUS,
    "subject_candidate_id": "cand-10104",
    "object_candidate_id": "cand-0025",
    "predicate": "published_fifteen_years_after_1725_by",
    "qualifiers": {
        "source_line_start": 114,
        "source_line_end": 114,
        "printed_page": 343,
        "pdf_physical_page": 12,
        "claim": "Haskell says Delle Antiche Statue Greche e Romane was published fifteen years after 1725 by Albrizzi.",
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": "The source states the interval; the year 1740 is not substituted as a derived date.",
        "mentioned_candidate_ids": ["cand-10104", "cand-0025"],
        "relation_candidate": True,
        "cross_reference_segments": [BODY],
    },
    "original_quote": previous_statement["original_quote"],
    "origin": "book",
    "source_file": SOURCE_FILE,
}
new_statements = [publisher_statement]

body_lines = {number: source_lines[number - 1] for number in range(116, 123)}
line_offsets = {}
offset = 0
for number in range(116, 123):
    line_offsets[number] = offset
    offset += len(body_lines[number]) + 1
new_mentions = []


def add_mention(line, surface, candidate_id, note="", occurrence=0):
    raw_line = body_lines[line]
    positions, cursor = [], 0
    while True:
        at = raw_line.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line}: {surface!r} occurrence {occurrence}")
    start = line_offsets[line] + positions[occurrence]
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p344-{len(new_mentions) + 1:03d}",
        "segment_id": BODY,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"mention FK missing: {candidate_id}")
    new_mentions.append(row)


mention_specs = [
    (117, "Dactyliotheca Ant. M. Zanetti", "cand-10012", "The p.337 descriptive candidate is now identified by title in this passage."),
    (117, "Albrizzi", "cand-0025"),
    (118, "Francesco Gori", "cand-10105"),
    (118, "King of Poland", "cand-10106"),
    (118, "Queen of Sweden", "cand-10107"),
    (118, "Zanetti", "cand-2838", "", 0),
    (118, "Venice", "cand-2719"),
    (118, "Zanetti", "cand-2838", "", 1),
    (118, "Abbé Clement", "cand-0789"),
    (118, "the magnificent volume", "cand-10012", "Anaphoric reference to the Dactyliotheca."),
    (119, "Zanetti", "cand-2838", "", 0),
    (119, "some lively caricatures of the leading operatic figures of the day", "cand-10108"),
    (119, "Rosalba Camera", "cand-0581", "S2 reading corrected against the printed page: Rosalba Carriera; source transcription remains unchanged."),
    (119, "Tiepolo", "cand-2569"),
    (119, "Vari Capriccj", "cand-10109", "S2 reading corrected against the printed page: Vari Capricci; source transcription remains unchanged."),
    (119, "Zanetti", "cand-2838", "", 1),
    (119, "Gaetano Zompini", "cand-2877"),
    (119, "Zompini", "cand-2875", "", 1),
    (119, "Castiglione drawings belonging to Zanetti", "cand-10110"),
    (119, "Castiglione", "cand-0602"),
    (119, "Zanetti", "cand-2838", "", 2),
    (119, "he made the drawings", "cand-2876", "Anaphoric reference to Zompini, who made the drawings for Le Arti in 1753."),
    (120, "Le Arti che vanno per via nella Città di Venezia", "cand-10111"),
    (120, "Venezia", "cand-2719"),
    (121, "Zanetti’s", "cand-2838"),
    (121, "Paris", "cand-4653"),
    (121, "Italy", "cand-3461"),
    (122, "Zanetti", "cand-2838"),
    (122, "Rosalba’s", "cand-0581"),
    (122, "Félicita Sartori", "cand-2363", "Printed page spells Felicita Sartori; source transcription retains Félicita."),
    (122, "a large collection of her work", "cand-10112", "Anaphoric reference to Félicita Sartori."),
    (122, "Memorie", "cand-9279", "Abbreviated citation with 1843 date; candidate is the 1843 Memorie on Rosalba Carriera."),
]
for spec in mention_specs:
    add_mention(*spec)


def make_statement(statement_id, subject, object_id, predicate, line, claim, quote=None, end_line=None,
                   speaker="Haskell", text_layer="authorial narrative", qualification="",
                   relation=False, printed_page=344, note_refs=None, extra=None):
    line_end = end_line if end_line is not None else line
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line_end,
        "printed_page": printed_page,
        "pdf_physical_page": 13 if printed_page == 344 else 12,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": [x for x in (subject, object_id) if x],
        "relation_candidate": relation,
    }
    if note_refs:
        qualifiers["note_refs_pending"] = note_refs
    if extra:
        qualifiers.update(extra)
    row = {
        "statement_id": statement_id,
        "segment_id": BODY if printed_page == 344 else PREVIOUS,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote if quote is not None else "\n".join(body_lines[n] for n in range(line, line_end + 1)),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    if row["statement_id"] in statement_by_id or any(s["statement_id"] == row["statement_id"] for s in new_statements):
        raise SystemExit(f"duplicate statement ID: {row['statement_id']}")
    new_statements.append(row)


make_statement(
    "st-chp13-p344-delle_antiche_statue-scholarship",
    "cand-10104", None, "subordinated_fantasy_to_scholarly_demands", 117,
    "Haskell says that in Delle Antiche Statue Zanetti subordinated fantasy to the demands of scholarship.",
    qualification="The work title is given in p.343 L114; this continuation stays source-local to p.344 L117.",
    extra={"cross_reference_segments": [PREVIOUS]},
)
make_statement(
    "st-chp13-p344-delle_antiche_statue-neoclassical_taste",
    "cand-10104", None, "plates_marked_arrival_of_neoclassical_taste_in_venice", 117,
    "Haskell says the book's plates mark an important stage in the arrival of neo-classical taste in Venice.",
    note_refs=[{"printed_note": 1, "segment_id": NOTES, "line": 239, "status": "pending"}],
)
make_statement(
    "st-chp13-p344-dactyliotheca-catalogue",
    "cand-10012", None, "illustrated_catalogue_of_zanettis_gems_and_medals", 117,
    "Haskell identifies the 1749 Dactyliotheca as an illustrated catalogue of A. M. Zanetti's collection of gems and medals.",
    note_refs=[{"printed_note": 1, "segment_id": NOTES, "line": 239, "status": "pending"}],
    extra={"date_as_stated": "1749", "ocr_corrections": ["L117: retain the source transcription 'of-gems'; no semantic correction is made."]},
)
make_statement(
    "st-chp13-p344-zanetti-illustrated_dactyliotheca",
    "cand-2838", "cand-10012", "provided_illustrations_for", 117,
    "Haskell says A. M. Zanetti provided illustrations for the Dactyliotheca.",
    note_refs=[{"printed_note": 1, "segment_id": NOTES, "line": 239, "status": "pending"}],
    relation=True,
)
make_statement(
    "st-chp13-p344-albrizzi-publisher_dactyliotheca",
    "cand-10012", "cand-0025", "chosen_as_publisher_after_hesitation", 117,
    "Haskell says Albrizzi was again chosen as publisher after some hesitation.",
    note_refs=[{"printed_note": 1, "segment_id": NOTES, "line": 239, "status": "pending"}],
    relation=True,
)
make_statement(
    "st-chp13-p344-gori-latin_commentary",
    "cand-10105", "cand-10012", "wrote_latin_commentary_for", 118,
    "Haskell says Francesco Gori wrote a Latin commentary for the Dactyliotheca.",
    note_refs=[{"printed_note": 1, "segment_id": NOTES, "line": 239, "status": "pending"}],
    relation=True,
)
make_statement(
    "st-chp13-p344-italian_translation",
    "cand-10012", None, "italian_translation_provided_for_general_readership", 118,
    "Haskell says an Italian translation was provided while a broader public was kept in mind.",
    qualification="The translator is not named in this passage.",
)
make_statement(
    "st-chp13-p344-polish_king-considered_dedicatee",
    "cand-10012", "cand-10106", "initially_considered_as_dedication_target", 118,
    "The King of Poland was first considered as a suitable foreign dedicatee for the book.",
    relation=True,
)
make_statement(
    "st-chp13-p344-swedish_queen-chosen_dedicatee",
    "cand-10012", "cand-10107", "chosen_as_intended_dedication_target", 118,
    "The Queen of Sweden was eventually chosen as the book's intended dedicatee.",
    qualification="The passage reports the choice of a dedicatee; it does not establish that a dedication was printed.",
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-stated_purpose",
    "cand-2838", "cand-10012", "said_book_was_produced_to_please_friends_and_foreigners", 118,
    "Zanetti wrote that he produced the book to please his friends, especially foreigners unable to come to Venice to see his medals.",
    speaker="A. M. Zanetti, quoted by Haskell",
    text_layer="quoted first-person statement",
    qualification="The statement is attributed to Zanetti, not presented as Haskell's direct observation.",
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-paid_publication_expenses",
    "cand-2838", "cand-10012", "published_at_zanettis_expense", 118,
    "Haskell says the volume was published at Zanetti's own expense.",
    relation=True,
)
make_statement(
    "st-chp13-p344-haskell-sale_catalogue_interpretation",
    "cand-10012", None, "partly_designed_as_luxurious_sale_catalogue", 118,
    "Haskell infers that the magnificent volume was partly designed as an exceedingly luxurious sale catalogue.",
    qualification="This is Haskell's interpretation, signalled by 'there can be little doubt'; it is not converted into a documented sales purpose.",
    note_refs=[{"printed_note": 2, "segment_id": NOTES, "line": 240, "status": "pending"}],
)
make_statement(
    "st-chp13-p344-clement-description_of_zanetti",
    "cand-0789", "cand-2838", "described_as_famous_amateur_and_somewhat_an_antique_dealer", 118,
    "Haskell quotes Abbé Clement describing Zanetti as a famous amateur and somewhat an antique dealer.",
    speaker="Abbé Clement, quoted by Haskell",
    text_layer="quotation reported in authorial narrative",
    qualification="Retain Haskell's attribution to Clement and the qualified phrase 'un peu'.",
    relation=True,
    note_refs=[{"printed_note": 2, "segment_id": NOTES, "line": 240, "status": "pending"}],
)
make_statement(
    "st-chp13-p344-zanetti-painted_for_pleasure",
    "cand-2838", None, "painted_for_his_own_pleasure", 119,
    "Haskell says Zanetti used to paint for his own pleasure.",
    note_refs=[{"printed_note": 3, "segment_id": NOTES, "line": 241, "status": "pending"}],
)
make_statement(
    "st-chp13-p344-zanetti-drew_operatic_caricatures",
    "cand-2838", "cand-10108", "drew_caricatures_of_leading_operatic_figures", 119,
    "Haskell says Zanetti drew lively caricatures of leading operatic figures of the day.",
    note_refs=[{"printed_note": 4, "segment_id": NOTES, "line": 242, "status": "pending"}],
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-habits_gave_artistic_insight",
    "cand-2838", None, "drawing_printmaking_and_painting_gave_insight_into_artistic_processes", 119,
    "Haskell says Zanetti's painting, caricatures, revival of wood chiaroscuro, and engraving gave him insight into more creative artists' processes.",
)
make_statement(
    "st-chp13-p344-carriera-learning_claim",
    "cand-0581", "cand-2838", "was_claimed_to_have_learned_much_from", 119,
    "Haskell reports a late-eighteenth-century claim that Rosalba Carriera had learned much from Zanetti.",
    qualification="The claimant is not identified here; the wording remains reported rather than stated as settled fact.",
    note_refs=[{"printed_note": 5, "segment_id": NOTES, "line": 243, "status": "pending"}],
    extra={"ocr_corrections": ["L119: source transcription 'Rosalba Camera' reads 'Rosalba Carriera' in the printed page."]},
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-significance_for_vari_capricci",
    "cand-2838", "cand-10109", "was_important_figure_for", 119,
    "Haskell says Zanetti must have been an important figure for the Tiepolo of the Vari Capricci.",
    qualification="This is Haskell's interpretive assessment, not a documented commission or direct collaboration.",
    extra={"ocr_corrections": ["L119: source transcription 'Vari Capriccj' reads 'Vari Capricci' in the printed page."]},
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-employed_zompini",
    "cand-2838", "cand-2877", "employed_housed_and_supported_with_regular_allowance", 119,
    "Haskell says Zanetti employed Gaetano Zompini, took him into his house, and provided a regular allowance.",
    qualification="Haskell says this was the chief basis for Zanetti's significance as a patron.",
    note_refs=[{"printed_note": 6, "segment_id": NOTES, "line": 244, "status": "pending"}],
    relation=True,
)
make_statement(
    "st-chp13-p344-zompini-engraved_castiglione_series",
    "cand-2875", "cand-10110", "engraved_a_series_of", 119,
    "Haskell says Zompini engraved a series of Castiglione drawings belonging to Zanetti.",
    qualification="The source gives neither individual titles nor a count; this set remains distinct from Zanetti's 1759 Castiglione drawings.",
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-owned_castiglione_drawings",
    "cand-10110", "cand-2838", "belonged_to", 119,
    "Haskell says the Castiglione drawings engraved by Zompini belonged to Zanetti.",
    relation=True,
)
make_statement(
    "st-chp13-p344-zompini-drew_for_le_arti_1753",
    "cand-2876", "cand-10111", "made_drawings_for_in_1753", 119,
    "Haskell says Zompini made the drawings for Le Arti che vanno per via nella Città di Venezia in 1753.",
    end_line=120,
    relation=True,
)
make_statement(
    "st-chp13-p344-haskell-le_arti_assessment",
    "cand-10111", None, "described_as_new_subject_matter_and_survey_of_tradesmen_and_poor", 120,
    "Haskell describes Le Arti as a major attempt by a Venetian artist to break new ground in subject matter and as a moving survey of tradesmen's and poor people's lives.",
    qualification="The evaluative terms 'most serious', 'moving', and 'convincing' remain Haskell's assessment.",
    note_refs=[{"printed_note": 7, "segment_id": NOTES, "line": 245, "status": "pending"}],
)
make_statement(
    "st-chp13-p344-haskell-zanetti-unique_among_patronage",
    "cand-2838", None, "described_as_alone_among_italian_amateurs_and_patrons", 121,
    "Haskell says Zanetti was important but isolated, contrasting him with the broader company he might have had in Paris.",
    qualification="This is Haskell's comparison, not a literal count of patrons.",
)
make_statement(
    "st-chp13-p344-zanetti-1752-incomplete_letter_fragment",
    "cand-2838", "cand-3461", "reported_few_amateurs_or_patrons_interested_in_fine_arts_in_italy", 121,
    "In a 1752 letter, Zanetti says there were no more interested amateurs or patrons in Italy and that the few who remained 'turn over each zecchino two'.",
    speaker="A. M. Zanetti, quoted by Haskell",
    text_layer="quoted first-person statement",
    qualification="The available source ends after 'two'; the quotation is incomplete in the supplied PDF and source transcription. No completion or interpretation of the unfinished phrase is inferred.",
    note_refs=[{"printed_note": 8, "segment_id": NOTES, "line": 246, "status": "pending"}],
    extra={"quote_truncated_at_source": True},
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-employed_felicita_sartori",
    "cand-2838", "cand-2363", "employed_as_engraver", 122,
    "Haskell says Zanetti employed Rosalba Carriera's pupil Félicita Sartori as an engraver.",
    qualification="This is the continuation of p.344 printed note 5; the consolidated note's opening sentence is at L243 and remains pending.",
    speaker="Haskell, in printed note 5",
    text_layer="footnote continuation",
    note_refs=[{"printed_note": 5, "segment_id": NOTES, "line": 243, "status": "pending"}],
    extra={"ocr_corrections": ["L122: source transcription 'Félicita' reads 'Felicita' in the printed page."]},
    relation=True,
)
make_statement(
    "st-chp13-p344-zanetti-owned_felicita_work",
    "cand-2838", "cand-10112", "owned_a_large_collection_of_work_by", 122,
    "Haskell says Zanetti owned a large collection of Félicita Sartori's work.",
    qualification="No individual work titles or collection count are given; the claim occurs in the continuation of printed note 5.",
    speaker="Haskell, in printed note 5",
    text_layer="footnote continuation",
    note_refs=[{"printed_note": 5, "segment_id": NOTES, "line": 243, "status": "pending"}],
    relation=True,
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + [publisher_statement] + [
    row for row in new_statements if row["statement_id"] != publisher_statement["statement_id"]
]

coverage[BODY].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L116-122",
    "note": (
        "Printed p.344 footnotes 1-8 map to consolidated source lines L239-L246 and remain pending. "
        "The continuation of printed note 5 appears at source L122 and is recorded here. "
        "The 1752 quotation ends after 'two' in the supplied PDF; following PDF page is Plate 57, "
        "with no prose continuation or p.345 in the supplied asset."
    ),
})

if args.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, all_candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, all_statements)
    write_csv(coverage_path, coverage_fields, coverage_rows)
    print("Applied p.344 S2 migration and p.343 work-candidate correction.")
else:
    print("Dry run only; no files changed. Use --apply after reviewing this preview.")
print(f"Candidates: {len(candidates)} -> {len(all_candidates)} (+{len(all_candidates)-len(candidates)}); max ID 10103 -> 10112.")
print(f"Mentions: {len(mentions)} -> {len(all_mentions)} (+{len(new_mentions)}); p.343 title mention reassigned.")
print(f"Statements: {len(statements)} -> {len(all_statements)} (+{len(all_statements)-len(statements)}); p.343 publication statement split.")
print(f"p.344 coverage: {coverage[BODY]['disposition']}/{coverage[BODY]['migration_status']} L116-122.")
print("New candidates:")
for row in new_candidates:
    if row["candidate_id"] != "cand-10012":
        print(f"  {row['candidate_id']}: {row['canonical_name']}")
print(f"New mentions: {len(new_mentions)}; new statements: {len(all_statements)-len(statements)}.")
