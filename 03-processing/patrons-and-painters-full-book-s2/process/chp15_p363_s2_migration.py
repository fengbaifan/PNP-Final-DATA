"""Controlled S2 migration for printed p.363 and its footnotes; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_SHA = "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_i.md"
BODY_PREV = "chp-15:15_CHP-15_sec_i:l16-25"
BODY = "chp-15:15_CHP-15_sec_i:l27-36"
BODY_NEXT = "chp-15:15_CHP-15_sec_i:l38-41"
NOTES = "chp-15:15_CHP-15_sec_i:l43-56"
BACKUP_SUFFIX = ".bak-s2-chp15-p363-apply-20261004"
PREVIOUS_PARTIAL = "st-chp15-p362-country-villa-arcades-and-columns-partial"
P362_COLUMNS = "st-chp15-p362-country-villa-arcades-and-columns-partial"
DONATION_STATEMENT = "st-chp15-p363-pope-ceded-columns-to-farsetti"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.363 S2 migration")
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
    raise SystemExit("chapter 15 body source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-15 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (28, "him by the Pope.1 An excessive rigidity breaks up the natural rhythm"),
    (28, "Farsetti was said to have spent a million ducats on its adornment"),
    (29, "botanical rarities were among the most celebrated sights of the Veneto"),
    (32, "the last year of the latter’s Use.3"),
    (34, "Canova, who came to' Venice in 1768"),
    (35, "Daniele (17251787), himself an amateur painter"),
    (36, "Letter from P. Boscovich to Vallisnieri of 1772 published 1811"),
    (46, "De Tipaldo, 1833, and Mazzotti, 1954, p. 133"),
    (47, "Sezione Notarise: Lodovico Gabrieli—Atti, 7567, p. 788V, shows that on ri April 1764"),
    (48, "Malamani: Canova, p. 6"),
    (49, "6 Canova: Quaderni, pp. 18 and 31"),
    (50, "8 Haskell and Levey, 1958, p. 185"),
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
    or coverage_by_id[NOTES]["migration_status"] != "partial"
):
    raise SystemExit("S2 coverage preconditions changed")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10449:
    raise SystemExit("candidate sequence changed; expected max cand-10449")
if PREVIOUS_PARTIAL not in statement_by_id or not statement_by_id[PREVIOUS_PARTIAL]["predicate"].endswith("_partial"):
    raise SystemExit("missing open p.362 column statement")

new_candidates = [
    ("cand-10450", "Letter from P. Boscovich to Vallisnieri (1772; published 1811, p.33)", "archive", BODY, 36,
     "Citation trail in p.363 note 2 for the contemporary praise of Farsetti’s villa. The letter was not independently consulted; do not treat the cited locator as independent verification."),
    ("cand-10451", "De Tipaldo (1833), cited in p.363 note 1", "archive", NOTES, 46,
     "Short-form source cited for Farsetti’s life; title and exact passage are not supplied here, and the work was not independently consulted."),
    ("cand-10452", "Mazzotti (1954), p.133, cited in p.363 note 1", "archive", NOTES, 46,
     "Short-form source cited for Farsetti’s life; title and exact passage are not supplied here, and the work was not independently consulted."),
    ("cand-10453", "Archivio di Stato, Venice, Sezione Notarile, Lodovico Gabrieli—Atti 7567, p.788v (11 April 1764)", "archive", NOTES, 47,
     "Archival citation in p.363 note 3 for a yearly allowance of 550 zecchini from Filippo Farsetti to Francesco Algarotti. The record was not independently consulted; title spelling/date are page-image readings recorded at S2."),
    ("cand-10454", "Malamani, Canova, p.6, cited in p.363 note 4", "archive", NOTES, 48,
     "Short-form citation for the placement of Canova’s early works in Palazzo Farsetti. Full title/year are not supplied in this note; not independently consulted."),
    ("cand-10455", "Canova, Quaderni, pp.18 and 31, cited in p.363 note 5", "archive", NOTES, 49,
     "Short-form citation for Canova’s diary comments on Farsetti’s copies and Raphael’s loggie. The cited pages were not independently consulted."),
    ("cand-10456", "Haskell and Levey (1958), p.185, cited in p.363 note 6", "archive", NOTES, 50,
     "Citation locator for the account of Daniele Farsetti’s appearance at the S. Rocco exhibition. The cited page was not independently consulted; align with other Haskell and Levey citations at S3."),
    ("cand-10457", "Gardens of Filippo Farsetti’s villa at S. Maria di Sala (p.363)", "place", BODY, 28,
     "Garden area described alongside the villa; botanical rarities, columns, temples and towers are reported as features. No garden name or separate architect is supplied."),
    ("cand-10458", "Two baskets of fruit and flowers, among Antonio Canova’s first works (p.363)", "work", BODY, 34,
     "Unidentified pair of works said to have been placed on the staircase of Palazzo Farsetti. No titles, dates, materials or current locations are supplied."),
    ("cand-10459", "Raphael’s loggie in the version known to Canova in Venice (p.363)", "", BODY, 34,
     "Haskell names ‘Raphael’s loggie’ and a version Canova knew in Venice. Whether the referent is the architectural spaces, their painted decoration or a particular copy/version is not resolved here."),
    ("cand-10460", "Pastels by Daniele Farsetti shown at the S. Rocco exhibition (p.363)", "work", BODY, 35,
     "Unidentified group of pastels; Haskell says Daniele once showed some at the S. Rocco exhibition. No titles, count, date or attribution details are given."),
    ("cand-10461", "Classical models as a basis for art in the theories discussed on p.363", "term", BODY, 32,
     "Haskell describes Algarotti and others as advocating following classical models. Preserve this as the source’s account of a theory, not as a universal rule or a named treatise."),
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

segment_bounds = {BODY: (27, 36), NOTES: (43, 56)}
segment_lines = {
    BODY: {number: source_lines[number - 1] for number in range(27, 37)},
    NOTES: {number: source_lines[number - 1] for number in range(43, 57)},
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
    mention_id = f"m-chp15-p363-{mention_counter:04d}"
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


def footnote(marker, note_segment, note_line, body_line, statement_ids):
    return {
        "footnote_marker": str(marker), "footnote_segment": note_segment,
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
        "printed_page": 363, "pdf_physical_page": 3,
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


# Cross-page references: the p.362 architectural sentence closes here, while this page ends mid-sentence.
P362_COLUMNS = "st-chp15-p362-country-villa-arcades-and-columns-partial"
previous = statement_by_id[P362_COLUMNS]
previous["predicate"] = previous["predicate"].removesuffix("_partial")
previous["qualifiers"]["predicate_status"] = "complete"
previous["qualifiers"]["qualification"] = (
    "P.363 L28 closes the sentence and says the columns were ceded to Farsetti by the Pope; "
    "that transfer is recorded separately. The temple location follows the printed wording."
)
previous["qualifiers"]["cross_reference_segments"] = [BODY]
previous["qualifiers"]["cross_reference_text"] = (
    "P.362 L25 ends ‘which were ceded to’; p.363 L28 closes the sentence and identifies Farsetti as recipient."
)
previous["qualifiers"]["cross_reference_text_pending"] = False
previous["qualifiers"]["cross_reference_statement_ids"] = [DONATION_STATEMENT]

# Mentions on printed p.363 body (including the page's footnote 2, physically extracted at L36).
add_mention(BODY, "cand-10432", "An excessive rigidity", 28, "Haskell’s critique of the villa’s plan, not a separate object.")
add_mention(BODY, "cand-10432", "its glory", 28, "Possessive refers to the villa.")
add_mention(BODY, "cand-1002", "him", 28, "Farsetti is the recipient of the columns.")
add_mention(BODY, "cand-2137", "the Pope", 28, "P.362 names Carlo Rezzonico as Pope Clement XIII; p.363 uses only the title. The excluded index redirect cand-2898 is not a separate person.")
add_mention(BODY, "cand-10432", "It", 28, "Pronoun refers to Farsetti’s villa at S. Maria di Sala.")
add_mention(BODY, "cand-10432", "battered shell", 28, "Haskell’s description at the time of writing; not a claim about the building’s current state.")
add_mention(BODY, "cand-1002", "Farsetti", 28)
add_mention(BODY, "cand-10432", "its adornment", 28, "Possessive refers to the villa.")
add_mention(BODY, "cand-10431", "his family", 28, "Possessive refers to Farsetti; family identity remains source-relative.")
add_mention(BODY, "cand-10432", "The marvellous splendour of the villa", 28, "Quoted contemporary praise; not a separate title for the building.")
add_mention(BODY, "cand-1002", "this man", 28)
add_mention(BODY, "cand-4653", "Paris", 28)
add_mention(BODY, "cand-10457", "the gardens", 28)
add_mention(BODY, "cand-10432", "the house itself", 28)
add_mention(BODY, "cand-10457", "its great botanical rarities", 29, "Garden contents described collectively; no species are named.")
add_mention(BODY, "cand-4207", "the Veneto", 29)
add_mention(BODY, "cand-10457", "columns, temples and towers", 29, "Features of the garden; no individual structures are named.")
add_mention(BODY, "cand-1002", "Farsetti’s ostentatious wealth", 30)
add_mention(BODY, "cand-1002", "him", 30)
add_mention(BODY, "cand-1002", "his time", 30)
add_mention(BODY, "cand-1002", "his real influence", 30)
add_mention(BODY, "cand-1002", "his keen interest", 30)
add_mention(BODY, "cand-1002", "he was making a deliberate attempt", 30)
add_mention(BODY, "cand-3401", "Venetian", 31)
add_mention(BODY, "cand-1002", "he was at least partly successful", 31)
add_mention(BODY, "cand-1005", "His collections", 31, "Plural holdings are not fully itemized here; c1005 anchors the cast collection discussed on p.362.")
add_mention(BODY, "cand-8144", "the", 31, "Article at the end of L31; the name continues on L32.")
add_mention(BODY, "cand-8144", "Academy", 32, "Continuation of ‘the’ at the end of L31; institution remains unnamed on this page.")
add_mention(BODY, "cand-1005", "his casts from the antique", 32)
add_mention(BODY, "cand-1010", "his palace", 32)
add_mention(BODY, "cand-0041", "Algarotti", 32)
add_mention(BODY, "cand-10461", "classical models", 32)
add_mention(BODY, "cand-1002", "Farsetti", 32)
add_mention(BODY, "cand-0041", "Algarotti", 32)
add_mention(BODY, "cand-0041", "the latter’s Use", 32, "‘The latter’ refers to Algarotti; page image reads ‘life’, with OCR ‘Use’ corrected only in S2.")
add_mention(BODY, "cand-1010", "Palazzo Farsetti", 33)
add_mention(BODY, "cand-0532", "Antonio", 33, "The personal name continues as ‘Canova’ at the start of L34.")
add_mention(BODY, "cand-0532", "Canova", 34, "Continuation of the name at the end of L33; general person index candidate reused.")
add_mention(BODY, "cand-3401", "Venice", 34)
add_mention(BODY, "cand-10458", "two baskets of fruit and flowers", 34, "Unidentified pair described as Canova’s first works; titles are not supplied.")
add_mention(BODY, "cand-1010", "the palace", 34)
add_mention(BODY, "cand-0532", "the sculptor", 34, "Refers to Canova.")
add_mention(BODY, "cand-4490", "Rome", 34)
add_mention(BODY, "cand-1005", "the works of antiquity", 34, "The source gives no list of the works Canova saw.")
add_mention(BODY, "cand-0532", "he", 34, "Refers to Canova.")
add_mention(BODY, "cand-1005", "Farsetti’s copies", 34, "The text does not enumerate the copies viewed by Canova.")
add_mention(BODY, "cand-0532", "he", 34, "Refers to Canova.")
add_mention(BODY, "cand-2098", "Raphael", 34)
add_mention(BODY, "cand-10459", "loggie", 34, "The exact architectural/decorative object and the Venetian version are unresolved.")
add_mention(BODY, "cand-0532", "he", 34, "Refers to Canova.")
add_mention(BODY, "cand-3401", "Venice", 34)
add_mention(BODY, "cand-1002", "Farsetti", 35)
add_mention(BODY, "cand-0532", "the one artist", 35, "Refers to Canova, whose success Farsetti did not live to see.")
add_mention(BODY, "cand-10448", "his faith in a classic revival", 35, "Farsetti’s commitment; keep distinct from the p.362 neo-classical movement label pending S3.")
add_mention(BODY, "cand-1002", "his death in 1774", 35)
add_mention(BODY, "cand-1002", "he was struck down by illness", 35)
add_mention(BODY, "cand-10431", "member of his family", 35, "Family refers to the Farsetti family.")
add_mention(BODY, "cand-1001", "His cousin Daniele", 35, "Daniele Farsetti; source gives dates 1725–1787 after the name.")
add_mention(BODY, "cand-1001", "himself", 35, "Pronoun refers to Daniele Farsetti.")
add_mention(BODY, "cand-10460", "his pastels", 35)
add_mention(BODY, "cand-8587", "exhibitionof", 35, "OCR joins the line-end hyphenation; the print reads ‘exhibition-’ followed by ‘of’ on the next line.")
add_mention(BODY, "cand-8588", "S. Rocco", 35, "Venue name; exact institutional/building identity remains unresolved.")
add_mention(BODY, "cand-1005", "the collection", 35, "Refers back to Farsetti’s collection; exact transferred holdings are not itemized.")
add_mention(BODY, "cand-1005", "it", 35, "Pronoun refers to the collection Daniele inherited and increased.")
add_mention(BODY, "cand-0414", "P. Boscovich", 36)
add_mention(BODY, "cand-2687", "Vallisnieri", 36)
add_mention(BODY, "cand-10450", "1772 published 1811, p. 33", 36, "Citation locator in the printed footnote; the letter was not consulted.")

# Consolidated p.363 notes; printed footnote 2 is embedded at body L36 in this OCR layout.
add_mention(NOTES, "cand-10451", "De Tipaldo", 46)
add_mention(NOTES, "cand-10451", "1833", 46)
add_mention(NOTES, "cand-10452", "Mazzotti", 46)
add_mention(NOTES, "cand-10452", "1954, p. 133", 46)
add_mention(NOTES, "cand-10172", "Archivio di Stato", 47)
add_mention(NOTES, "cand-3401", "Venice", 47)
add_mention(NOTES, "cand-10453", "Lodovico Gabrieli—Atti, 7567, p. 788V", 47, "OCR citation locator; page image reads p.788v.")
add_mention(NOTES, "cand-10453", "ri April 1764", 47, "OCR reads ‘ri’; the page image reads ‘11 April 1764’.")
add_mention(NOTES, "cand-1002", "N. H. Filippo Farsetti", 47)
add_mention(NOTES, "cand-0041", "Algarotti", 47)
add_mention(NOTES, "cand-0532", "Canova", 48)
add_mention(NOTES, "cand-10454", "Malamani:", 48)
add_mention(NOTES, "cand-10454", "p. 6", 48)
add_mention(NOTES, "cand-0532", "Canova", 49)
add_mention(NOTES, "cand-10455", "Quaderni", 49)
add_mention(NOTES, "cand-10455", "pp. 18 and 31", 49)
add_mention(NOTES, "cand-10456", "Haskell and", 50)
add_mention(NOTES, "cand-8657", "Levey", 50, "Surname-only author candidate; full identity remains for bibliography/S3.")
add_mention(NOTES, "cand-10456", "1958, p. 185", 50)

# Close p.362's column sentence and record the separate papal transfer claim.
add_statement(
    DONATION_STATEMENT, BODY, "cand-2137", "cand-1002",
    "ceded_42_doric_columns_from_temple_to_farsetti", 28, 28,
    "Haskell says the forty-two Doric columns described on p.362 were ceded to Farsetti by the Pope.",
    qualification="P.363 names only ‘the Pope’; the immediate prior context names Carlo Rezzonico as Pope Clement XIII. The index entry for Clement XIII is a cross-reference, not a separate person.",
    mentioned=["cand-2137", "cand-1002", "cand-10435"], relation_candidate=True,
    cross_reference_segments=[BODY_PREV], cross_reference_text="The antecedent ‘which’ and the forty-two Doric columns are identified at p.362 L24-25.",
    cross_reference_statement_ids=[P362_COLUMNS], **footnote(1, NOTES, 46, 28, ["st-chp15-p363-note1-life-citations"]))
add_statement(
    "st-chp15-p363-villa-rigidity-breaks-natural-rhythm", BODY, "cand-10432", None,
    "excessive_rigidity_breaks_natural_rhythm_demanded_by_plan", 28, 28,
    "Haskell says excessive rigidity breaks up the natural rhythm demanded by the villa’s plan.",
    qualification="This is Haskell’s architectural assessment of the villa’s design.", mentioned=["cand-10432"])
add_statement(
    "st-chp15-p363-villa-impressive-rather-than-beautiful", BODY, "cand-10432", None,
    "at_height_of_glory_must_have_been_impressive_rather_than_beautiful", 28, 28,
    "Haskell says that even at the height of its glory the villa must have been impressive rather than beautiful.",
    qualification="Preserves the modal ‘must have been’ and the author’s evaluative contrast.", mentioned=["cand-10432"])
add_statement(
    "st-chp15-p363-villa-battered-shell-at-haskell-time", BODY, "cand-10432", None,
    "described_at_haskell_time_as_battered_shell_used_as_store", 28, 28,
    "Haskell says the villa had become a battered shell used as a store by local peasants.",
    qualification="‘Now’ is relative to Haskell’s account; this is not a statement about the building’s present-day condition.",
    mentioned=["cand-10432"])
add_statement(
    "st-chp15-p363-farsetti-said-spent-million-ducats", BODY, "cand-1002", "cand-10432",
    "was_said_to_spend_million_ducats_on_villa_adornment_nearly_ruining_family", 28, 28,
    "Haskell reports that Farsetti was said to have spent a million ducats on the villa’s adornment, nearly ruining his family, while striking his contemporaries’ imagination beyond measure.",
    qualification="The source explicitly says ‘was said’; amount and financial consequence remain reported rather than independently verified.",
    mentioned=["cand-1002", "cand-10432", "cand-10431"], **footnote(1, NOTES, 46, 28, ["st-chp15-p363-note1-life-citations"]))
add_statement(
    "st-chp15-p363-contemporary-praised-villa", BODY, "cand-10432", None,
    "contemporary_praised_villa_splendour_richness_and_taste", 28, 28,
    "Haskell quotes an unnamed contemporary praising the villa’s splendour, richness, arrangement and Farsetti’s magnificence, and says Farsetti was highly thought of in Paris.",
    qualification="The quoted speaker is not named in the body. Note 2 cites a Boscovich letter, but it was not independently consulted; the speaker attribution is not upgraded beyond Haskell’s citation trail.",
    mentioned=["cand-10432", "cand-1002", "cand-4653"], **footnote(2, BODY, 36, 28, ["st-chp15-p363-note2-boscovich-letter"]))
add_statement(
    "st-chp15-p363-attention-to-gardens", BODY, "cand-10432", "cand-10457",
    "gardens_received_attention_comparable_to_house", 28, 29,
    "Haskell says as much attention was paid to the villa’s gardens as to the house itself.",
    mentioned=["cand-10432", "cand-10457"])
add_statement(
    "st-chp15-p363-garden-botanical-rarities", BODY, "cand-10457", "cand-4207",
    "botanical_rarities_among_venetos_most_celebrated_sights", 29, 29,
    "Haskell says the garden’s botanical rarities were among the most celebrated sights of the Veneto.",
    qualification="No plant species or specific garden objects are identified.", mentioned=["cand-10457", "cand-4207"])
add_statement(
    "st-chp15-p363-garden-columns-temples-towers", BODY, "cand-10457", None,
    "garden_decorated_with_columns_temples_and_towers", 29, 29,
    "Haskell says the garden was decorated with columns, temples and towers.",
    qualification="These are described as garden features; individual structures are not named.", mentioned=["cand-10457"])
add_statement(
    "st-chp15-p363-wealth-and-sculpture-made-farsetti-important", BODY, "cand-1002", None,
    "wealth_and_classical_sculpture_would_make_him_important_in_society", 30, 30,
    "Haskell says Farsetti’s ostentatious wealth and devotion to classical sculpture would themselves have made him a most important figure in the society of his time.",
    qualification="This is Haskell’s assessment of social importance, not an independently measured ranking.", mentioned=["cand-1002"])
add_statement(
    "st-chp15-p363-real-influence-from-contemporary-arts", BODY, "cand-1002", None,
    "real_influence_derived_from_interest_in_contemporary_arts", 30, 30,
    "Haskell says Farsetti’s real influence derived from his keen interest in the contemporary arts.",
    mentioned=["cand-1002"])
add_statement(
    "st-chp15-p363-attempt-to-change-venetian-arts-partly-succeeded", BODY, "cand-1002", "cand-3401",
    "deliberately_attempted_to_change_venetian_painting_and_sculpture_at_least_partly_successful", 30, 31,
    "Haskell says Farsetti was deliberately trying to change the nature of Venetian painting and sculpture and was at least partly successful.",
    qualification="Retains ‘there seems no doubt’ and ‘at least partly’; does not claim a complete transformation.",
    mentioned=["cand-1002", "cand-3401"], relation_candidate=True)
add_statement(
    "st-chp15-p363-collections-open-to-students", BODY, "cand-1002", "cand-1005",
    "collections_open_to_students_encouraged_to_copy", 31, 31,
    "Haskell says Farsetti’s collections were open to students who were encouraged to come and copy them.",
    qualification="The passage does not name the students or enumerate which parts of the collections were copied.",
    mentioned=["cand-1002", "cand-1005"], relation_candidate=True)
add_statement(
    "st-chp15-p363-academy-lacked-comparable-antique-casts", BODY, "cand-8144", "cand-1005",
    "had_nothing_remotely_comparable_to_farsetti_casts_from_antique", 31, 32,
    "Haskell says the Academy had nothing remotely comparable to Farsetti’s casts from the antique.",
    qualification="The Academy is not named on this page; preserve the existing source-relative candidate without identifying it externally.",
    mentioned=["cand-8144", "cand-1005"])
add_statement(
    "st-chp15-p363-palace-centre-for-classical-model-theories", BODY, "cand-1010", "cand-10461",
    "palace_became_main_centre_for_students_absorbing_classical_model_theories", 32, 32,
    "Haskell says Palazzo Farsetti became the main centre for people absorbing Algarotti’s and others’ theories about following classical models.",
    qualification="The theories and the other advocates are not individually specified in this passage.",
    mentioned=["cand-1010", "cand-0041", "cand-10461"])
add_statement(
    "st-chp15-p363-farsetti-regular-allowance-to-algarotti", BODY, "cand-1002", "cand-0041",
    "gave_algarotti_regular_allowance_during_last_year_of_his_life", 32, 32,
    "Haskell says Farsetti gave Algarotti a regular allowance during the last year of Algarotti’s life.",
    qualification="The main text supplies no amount or exact date; p.363 note 3 cites an archival record with further details, not independently consulted.",
    mentioned=["cand-1002", "cand-0041", "cand-0042"], relation_candidate=True,
    **footnote(3, NOTES, 47, 32, ["st-chp15-p363-note3-archival-act"]))
add_statement(
    "st-chp15-p363-allowance-called-particularly-fitting", BODY, "cand-1002", "cand-0041",
    "allowance_described_as_fitting_given_algarottis_theories", 32, 32,
    "Haskell calls Farsetti’s allowance to Algarotti particularly fitting in light of Palazzo Farsetti’s role as a centre for classical-model theories.",
    text_layer="authorial evaluation",
    qualification="This records Haskell’s rhetorical evaluation, separately from the reported allowance itself.",
    mentioned=["cand-1002", "cand-0041", "cand-1010", "cand-10461"])
add_statement(
    "st-chp15-p363-note3-archival-act", NOTES, "cand-10453", None,
    "note_cites_archival_act_for_1764_allowance", 47, 47,
    "P.363 note 3 cites a notarial record which it says shows that Filippo Farsetti made Algarotti a yearly allowance of 550 zecchini on 11 April 1764.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The page image reads ‘Sezione Notarile’, ‘11 April’, and p.788v where OCR has ‘Notarise’, ‘ri April’, and ‘788V’. The archival record was not consulted.",
    mentioned=["cand-10453", "cand-1002", "cand-0041"])
add_statement(
    "st-chp15-p363-canova-most-famous-student", BODY, "cand-1010", "cand-0532",
    "canova_most_famous_among_those_who_studied_in_palazzo_farsetti", 33, 34,
    "Haskell calls Antonio Canova the most famous among those who studied in Palazzo Farsetti.",
    qualification="This is Haskell’s comparative characterization; the passage does not enumerate all students.",
    mentioned=["cand-1010", "cand-0532"])
add_statement(
    "st-chp15-p363-canova-came-to-venice-1768", BODY, "cand-0532", "cand-3401",
    "came_to_venice_in_1768", 34, 34,
    "Haskell says Canova came to Venice in 1768.",
    qualification="The printed page reads ‘came to Venice’; the apostrophe after ‘to’ in the OCR is not printed.",
    mentioned=["cand-0532", "cand-3401"])
add_statement(
    "st-chp15-p363-canova-first-baskets-placed-in-palace", BODY, "cand-0532", "cand-10458",
    "first_works_two_baskets_of_fruit_and_flowers_placed_on_palace_staircase", 34, 34,
    "Haskell says Canova’s first works, two baskets of fruit and flowers, were placed on Palazzo Farsetti’s staircase.",
    qualification="The pair is not titled or dated here. P.363 note 4 cites Malamani, Canova, p.6; that page was not consulted.",
    mentioned=["cand-0532", "cand-10458", "cand-1010"], relation_candidate=True,
    **footnote(4, NOTES, 48, 34, ["st-chp15-p363-note4-malamani-canova"]))
add_statement(
    "st-chp15-p363-canova-steeped-in-antiquity-before-rome", BODY, "cand-0532", None,
    "before_going_to_rome_was_already_steeped_in_works_of_antiquity", 34, 34,
    "Haskell says Canova was already steeped in the works of antiquity well before he went to Rome.",
    qualification="The source gives no date for the Rome journey in this sentence.", mentioned=["cand-0532", "cand-4490", "cand-1005"])
add_statement(
    "st-chp15-p363-canova-saw-farsetti-copies-before-originals", BODY, "cand-0532", "cand-1005",
    "often_noted_having_seen_farsetti_copies_before_viewing_originals_in_rome", 34, 34,
    "Haskell says that in Rome Canova often noted in his diary that he had already seen Farsetti’s copies of originals he was then viewing.",
    qualification="The diary statements are reported by Haskell; p.363 note 5 cites Canova’s Quaderni, pp.18 and 31, which were not consulted.",
    mentioned=["cand-0532", "cand-1002", "cand-1005", "cand-4490"],
    **footnote(5, NOTES, 49, 34, ["st-chp15-p363-note5-canova-quaderni"]))
add_statement(
    "st-chp15-p363-raphael-loggie-venetian-version", BODY, "cand-0532", "cand-10459",
    "found_raphael_loggie_easier_to_study_in_venetian_version_known_to_him", 34, 34,
    "Haskell says Canova found Raphael’s loggie much easier to study in the version he had known in Venice.",
    qualification="The exact loggie, the nature of the Venetian version, and whether it was architectural or pictorial are unresolved. P.363 note 5 cites Canova’s Quaderni, pp.18 and 31, not independently consulted.",
    mentioned=["cand-0532", "cand-2098", "cand-10459", "cand-3401"],
    **footnote(5, NOTES, 49, 34, ["st-chp15-p363-note5-canova-quaderni"]))
add_statement(
    "st-chp15-p363-farsetti-did-not-see-canova-success", BODY, "cand-1002", "cand-0532",
    "did_not_live_to_see_canova_success_that_appeared_to_justify_classic_revival", 35, 35,
    "Haskell says Farsetti did not live to see the success of the artist who appeared to justify his faith in a classic revival.",
    qualification="‘Appeared to justify’ preserves Haskell’s evaluative and qualified framing.", mentioned=["cand-1002", "cand-0532", "cand-10448"])
add_statement(
    "st-chp15-p363-farsetti-ill-incapacitated-before-death", BODY, "cand-1002", None,
    "struck_by_illness_five_or_six_years_before_1774_death_largely_incapacitated", 35, 35,
    "Haskell says Farsetti was struck down by illness some five or six years before his death in 1774 and thereafter was largely incapacitated.",
    qualification="The interval is explicitly approximate; no year is calculated.", mentioned=["cand-1002"])
add_statement(
    "st-chp15-p363-farsetti-not-only-family-arts-patron", BODY, "cand-1002", "cand-10431",
    "not_only_member_of_family_to_encourage_arts", 35, 35,
    "Haskell says Farsetti was not the only member of his family to encourage the arts.",
    mentioned=["cand-1002", "cand-10431"])
add_statement(
    "st-chp15-p363-daniele-cousin-amateur-painter", BODY, "cand-1001", "cand-1002",
    "cousin_of_filippo_farsetti_and_amateur_painter_dates_1725_1787", 35, 35,
    "Haskell identifies Daniele Farsetti as Filippo’s cousin, dates him 1725–1787, and describes him as an amateur painter.",
    qualification="The OCR omits the date hyphen; the page image reads 1725–1787. No further identity or biography is inferred.",
    mentioned=["cand-1001", "cand-1002"], relation_candidate=True)
add_statement(
    "st-chp15-p363-daniele-showed-pastels-at-s-rocco", BODY, "cand-1001", "cand-8587",
    "once_showed_some_pastels_at_s_rocco_exhibition", 35, 35,
    "Haskell says Daniele once showed some of his pastels at the exhibition of S. Rocco.",
    qualification="The exhibition date and individual pastels are not named. The p.363 note 6 locator is Haskell and Levey, 1958, p.185; it was not consulted.",
    mentioned=["cand-1001", "cand-10460", "cand-8587", "cand-8588"], relation_candidate=True,
    **footnote(6, NOTES, 50, 35, ["st-chp15-p363-note6-haskell-levey"]))
add_statement(
    "st-chp15-p363-daniele-inherited-increased-collection", BODY, "cand-1001", "cand-1002",
    "inherited_and_increased_filippo_farsetti_collection", 35, 35,
    "Haskell says Daniele inherited Filippo Farsetti’s collection and increased it.",
    qualification="The exact inventory or division of holdings is not specified; the source’s singular ‘collection’ is retained.",
    mentioned=["cand-1001", "cand-1002", "cand-1005"], relation_candidate=True)
add_statement(
    "st-chp15-p363-daniele-continued-patronage-partial", BODY, "cand-1001", None,
    "continued_patronage_of_contemporary_artists_partial", 35, 35,
    "Haskell says Daniele also continued the family’s patronage of contemporary artists.",
    qualification="The sentence ends at p.363 L35 with ‘continued the’ and resumes at p.364 L39. The recipient group and complete wording remain open until that continuation is processed.",
    mentioned=["cand-1001", "cand-10431"], predicate_status="partial",
    cross_reference_segments=[BODY_NEXT], cross_reference_text="P.363 L35 ends ‘continued the’; p.364 L39 begins ‘patronage of contemporary artists.’",
    cross_reference_text_pending=True)

# Citation trail statements: no cited source was independently consulted in this S2 pass.
add_statement(
    "st-chp15-p363-note1-life-citations", NOTES, None, None,
    "note_cites_de_tipaldo_1833_and_mazzotti_1954_p133_for_farsetti_life", 46, 46,
    "P.363 note 1 cites De Tipaldo (1833) and Mazzotti (1954, p.133) among the principal sources for Farsetti’s life.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="Full titles and exact passages are not supplied here; neither work was independently consulted.",
    mentioned=["cand-10451", "cand-10452", "cand-1002"], cited_sources_independently_consulted=False)
add_statement(
    "st-chp15-p363-note2-boscovich-letter", BODY, None, None,
    "note_cites_boscovich_letter_to_vallisnieri_1772_published_1811_page33", 36, 36,
    "P.363 note 2 cites a 1772 letter from P. Boscovich to Vallisnieri, published in 1811, page 33, for the preceding contemporary praise.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The letter was not independently consulted; the quotation’s author is not independently confirmed.",
    mentioned=["cand-10450", "cand-0414", "cand-2687"], cited_source_independently_consulted=False,
    footnote_marker="2", footnote_segment=BODY, footnote_line_range="L36", footnote_text_pending=False,
    footnote_body_link_status="linked", footnote_body_line_range="L28",
    footnote_note_statement_ids=["st-chp15-p363-contemporary-praised-villa"])
add_statement(
    "st-chp15-p363-note4-malamani-canova", NOTES, None, "cand-10454",
    "note_cites_malamani_canova_page6", 48, 48,
    "P.363 note 4 cites Malamani, Canova, page 6, for the first works placed on the palace staircase.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The source was not independently consulted; no year or full title is supplied in this note.",
    mentioned=["cand-10454", "cand-0532"], cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p363-note5-canova-quaderni", NOTES, None, "cand-10455",
    "note_cites_canova_quaderni_pages18_and31", 49, 49,
    "P.363 note 5 cites Canova’s Quaderni, pages 18 and 31, for Canova’s diary comments.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The page image confirms printed note number 5; OCR reads 6. The cited pages were not consulted.",
    mentioned=["cand-10455", "cand-0532"], cited_source_independently_consulted=False)
add_statement(
    "st-chp15-p363-note6-haskell-levey", NOTES, None, "cand-10456",
    "note_cites_haskell_and_levey_1958_page185", 50, 50,
    "P.363 note 6 cites Haskell and Levey (1958), page 185, for Daniele Farsetti and the S. Rocco exhibition.",
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The page image confirms printed note number 6; OCR reads 8. The cited page was not consulted.",
    mentioned=["cand-10456", "cand-8657"], cited_source_independently_consulted=False)

new_statement_ids = {row["statement_id"] for row in statements if row["statement_id"].startswith("st-chp15-p363-")}
expected_statement_count = 36
if len(new_statement_ids) != expected_statement_count:
    raise SystemExit(f"expected {expected_statement_count} new p.363 statements, got {len(new_statement_ids)}")

coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L16-25",
    "note": "Printed p.362 body is now closed by p.363 L28. The column-origin sentence and papal transfer have linked statements; p.362 note 1–2 remain linked to body markers at L17. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L27-36",
    "note": "Printed p.363 checked against CHP-15.pdf physical p.3. Semantic body lines are L27-35; OCR line L36 is the page’s footnote 2, linked to the L28 quotation. Records Farsetti’s villa, gardens, patronage, Canova, illness and Daniele. OCR corrections are recorded only in S2. L35 ends ‘continued the’ and resumes at p.364 L39; this body segment remains partial.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L44-50",
    "note": "P.362 notes 1–2 at L44–45 and p.363 notes 1, 3–6 at L46–50 are linked to their body statements. Printed note 2 was encountered at BODY L36. Remaining consolidated notes L51–56 belong to later pages and remain pending.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": len(new_candidates),
    "new_mentions": len(planned_mentions),
    "new_statements": len(new_statement_ids),
    "updated_statements": [P362_COLUMNS],
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (BODY_PREV, BODY, NOTES)},
    "printed_page": 363,
    "pdf_physical_page": 3,
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
