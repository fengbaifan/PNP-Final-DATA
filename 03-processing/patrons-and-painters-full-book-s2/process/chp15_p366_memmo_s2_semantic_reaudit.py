"""Evidence-locked semantic re-audit of the already migrated p.366 S2 rows.

Default mode is a dry-run. This intentionally does not reuse the 2026-10-04
first-pass migration, whose preconditions no longer match the current tables.
"""
from __future__ import annotations

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
BODY = "chp-15:15_CHP-15_sec_ii:l14-28"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BACKUP_SUFFIX = ".bak-s2-chp15-p366-semantic-reaudit-20261009"
EXPECTED = {
    SOURCE: "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    PDF: "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
    TABLES / "entity-candidates.csv": "d33a36b7c1ca81c34d0a282a654c467ff7a19c071dad82c32f4edd4e712f51f5",
    TABLES / "mentions.csv": "cb015591c191b0f5520d3eb8aa74729eb433aa35f22f294813cf44b5a8f56391",
    TABLES / "book-statements.jsonl": "e2f15423a45bdec26f75cc22694e8ee2650e9fdc64481c4dafaf179291ed5f43",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write after the dry-run has been reviewed")
args = parser.parse_args()

for path, expected_hash in EXPECTED.items():
    if sha256(path) != expected_hash:
        raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_text = "\n".join(source_lines[14:28])
mention_text = "\n".join(source_lines[13:28])  # The [Page 66] marker is included in mention offsets.


def exact_quote(value: str) -> str:
    if value not in body_text:
        raise SystemExit(f"quote is not an exact p.366 source substring: {value!r}")
    return value


def source_offset(surface: str) -> tuple[int, int]:
    start = mention_text.find(surface)
    if start < 0:
        raise SystemExit(f"mention surface not found on p.366: {surface!r}")
    return start, start + len(surface)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}

p366_statements = [row for row in statements if row.get("segment_id") == BODY]
p366_mentions = [row for row in mentions if row.get("segment_id") == BODY]
if len(p366_statements) != 27 or len(p366_mentions) != 86:
    raise SystemExit(f"unexpected p.366 inventory: {len(p366_statements)} statements, {len(p366_mentions)} mentions")
coverage_fields, coverage = read_csv(TABLES / "s2-coverage.csv")
coverage_row = next((row for row in coverage if row["segment_id"] == BODY), None)
if not coverage_row or coverage_row["migration_status"] != "complete":
    raise SystemExit("p.366 coverage precondition changed; inspect before applying")

new_candidates = [
    ("cand-11526", "Unidentified 1786 account written by Radicchio to accompany the Prà engraving", "archive",
     "Haskell identifies the author, year, and function but supplies no title or publication details; do not identify it with another citation without evidence."),
    ("cand-11527", "Unidentified friends whom Andrea Memmo urged to contribute statues", "",
     "The source names only Memmo’s friends as a group. Preserve the relation endpoint without identifying individual contributors."),
    ("cand-11528", "Unidentified distinguished visitors who contributed statues after following the Pope’s example", "",
     "Haskell gives no names for the visitors or the Pope. This is a source-level collective, not an identified institution."),
    ("cand-11529", "Unidentified Padua councillors who objected to the Prà expense", "",
     "The source identifies councillors but not their names or exact civic body; do not equate them with the City of Padua civic-body candidate."),
]
for cid, name, typ, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": typ,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": (
            f"{BODY}#L22" if cid == "cand-11526" else
            f"{BODY}#L21" if cid == "cand-11528" else
            f"{BODY}#L20"
        ),
    }
    candidates.append(row)
    candidate_by_id[cid] = row

for mention_id, candidate_id, note in [
    ("m-chp15-p366-memmo-0046", "cand-11527", "Unidentified friends; retained as a group endpoint, not mapped to Memmo."),
    ("m-chp15-p366-memmo-0042", "cand-11529", "Unidentified councillors; kept distinct from the City of Padua civic-body candidate."),
]:
    mention = mention_by_id[mention_id]
    if mention["candidate_id"] not in {"cand-1642", "cand-8406"}:
        raise SystemExit(f"unexpected candidate mapping for {mention_id}")
    mention["candidate_id"] = candidate_id
    mention["note"] = note

new_mentions = []
for mention_id, candidate_id, surface, line_number, note in [
    ("m-chp15-p366-memmo-0086", "cand-11526", "an account", 22, "Unidentified text accompanying Piranesi’s engraving; title and edition are not supplied."),
    ("m-chp15-p366-memmo-0087", "cand-11528", "distinguished visitors", 21, "Unnamed visitors are treated as a source-level group; no individuals are inferred."),
]:
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    start, end = source_offset(surface)
    if mention_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch for {mention_id}")
    row = {
        "mention_id": mention_id,
        "segment_id": BODY,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    }
    mentions.append(row)
    mention_by_id[mention_id] = row
    new_mentions.append(row)


updated_statement_ids = set()


def update_statement(statement_id: str, *, subject=None, object_id=None, predicate=None, quote=None,
                     claim=None, mentioned=None, relation=None, qualification=None, ocr_correction=None):
    if statement_id not in statement_by_id:
        raise SystemExit(f"missing existing statement: {statement_id}")
    row = statement_by_id[statement_id]
    if subject is not None or statement_id in {
        "st-chp15-p366-1777-progress-and-ambassadorship",
        "st-chp15-p366-difficulties-at-pra-while-memmo-away",
        "st-chp15-p366-subleyras-plans-displayed",
        "st-chp15-p366-pope-and-visitors-contribute",
        "st-chp15-p366-radicchio-account-accompanies-engraving",
    }:
        row["subject_candidate_id"] = subject
    if object_id is not None or statement_id in {
        "st-chp15-p366-1777-progress-and-ambassadorship",
        "st-chp15-p366-difficulties-at-pra-while-memmo-away",
        "st-chp15-p366-subleyras-plans-displayed",
        "st-chp15-p366-pope-and-visitors-contribute",
        "st-chp15-p366-radicchio-account-accompanies-engraving",
    }:
        row["object_candidate_id"] = object_id
    if predicate is not None:
        row["predicate"] = predicate
    if quote is not None:
        row["original_quote"] = exact_quote(quote)
    q = row["qualifiers"]
    if claim is not None:
        q["claim"] = claim
    if mentioned is not None:
        q["mentioned_candidate_ids"] = mentioned
    if relation is not None:
        if relation:
            q["relation_candidate"] = True
        else:
            q.pop("relation_candidate", None)
    if qualification is not None:
        q["qualification"] = qualification
    if ocr_correction is not None:
        corrections = q.setdefault("ocr_corrections", [])
        if ocr_correction not in corrections:
            corrections.append(ocr_correction)
    updated_statement_ids.add(statement_id)


added_statements = []


def add_statement(statement_id: str, subject: str | None, object_id: str | None, predicate: str,
                  claim: str, line_start: int, line_end: int, quote: str,
                  mentioned: list[str], *, relation: bool = False, speaker: str = "Haskell",
                  text_layer: str = "authorial report", qualification: str | None = None,
                  cited_source_independently_consulted: bool | None = None,
                  ocr_corrections: list[dict] | None = None):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    for cid in [subject, object_id, *mentioned]:
        if cid is not None and cid not in candidate_by_id:
            raise SystemExit(f"statement {statement_id} refers to missing candidate {cid}")
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 366,
        "pdf_physical_page": 6,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "mentioned_candidate_ids": mentioned,
    }
    if qualification:
        q["qualification"] = qualification
    if relation:
        q["relation_candidate"] = True
    if cited_source_independently_consulted is not None:
        q["cited_source_independently_consulted"] = cited_source_independently_consulted
    if ocr_corrections:
        q["ocr_corrections"] = ocr_corrections
    row = {
        "statement_id": statement_id,
        "segment_id": BODY,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": exact_quote(quote),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    added_statements.append(row)
    statement_by_id[statement_id] = row


# Keep the p.365 representation-eligibility continuation separate from the new presenter rule.
update_statement(
    "st-chp15-p366-eligible-presenters",
    quote="moreover, only certain classes of people could present statues in their own names—nobles or important churchmen or a few old and distinguished professions such as university teachers.",
)
update_statement(
    "st-chp15-p366-memmo-not-only-rich",
    quote="On the other hand Memmo was especially anxious that the opportunity to raise a statue should not be available only to the rich.",
)
update_statement(
    "st-chp15-p366-price-and-appearance",
    predicate="avoiding_costly_marble_and_famous_sculptors_kept_statue_prices_low",
    claim="Haskell says avoiding precious marbles and famous sculptors could keep statue prices low, at 135 zecchini or 150 for something rather better.",
    quote="If precious marbles and famous sculptors were avoided—and, after all, he claimed, it was the general appearance that mattered—the price could be kept low enough: 135 zecchini or, for something rather better, 150.",
)
add_statement(
    "st-chp15-p366-general-appearance-mattered", "cand-1650", None,
    "general_appearance_mattered_in_statue_design",
    "Haskell says Memmo claimed that the general appearance of a statue mattered.", 16, 16,
    "after all, he claimed, it was the general appearance that mattered",
    ["cand-1650"],
    qualification="This is reported as Memmo’s stated design view, not an independently verified quotation from him.",
)
update_statement(
    "st-chp15-p366-quality-committee-and-stone",
    predicate="quality_standard_required_for_statues",
    claim="Haskell says a certain standard of quality was required for the statues.",
    quote="A certain standard of quality was insisted on",
)
add_statement(
    "st-chp15-p366-committee-appointed-for-quality", "cand-1650", None,
    "committee_appointed_to_enforce_quality_standard",
    "Haskell says a committee was appointed to ensure that the required quality standard was followed.", 16, 16,
    "a committee was appointed to see that it was adhered to",
    ["cand-1650"], qualification="The committee is unnamed and is not assigned a separate institutional identity.",
)
add_statement(
    "st-chp15-p366-uniform-stone-required", "cand-1650", None,
    "same_kind_of_stone_required_for_every_statue",
    "Haskell says every statue was to use the same kind of stone.", 16, 16,
    "The same kind of stone must be used for every statue",
    ["cand-1650"],
)
update_statement(
    "st-chp15-p366-latin-inscriptions-pedestals",
    predicate="statue_inscriptions_required_to_be_latin_and_brief",
    claim="Haskell says the inscriptions had to be in Latin and brief.",
    quote="the inscriptions must be in Latin and must be brief",
)
add_statement(
    "st-chp15-p366-pedestal-space-limited-inscriptions", "cand-1650", None,
    "limited_pedestal_space_ensured_brief_inscriptions",
    "Haskell says limited space on the pedestals ensured that inscriptions remained brief.", 16, 16,
    "this was ensured by designing pedestals with only limited available space",
    ["cand-1650"],
)

update_statement(
    "st-chp15-p366-memmo-offers-antenor-statue",
    claim="Haskell says Memmo inaugurated the scheme by offering a statue.",
    quote="Memmo himself inaugurated the scheme by offering a statue",
    mentioned=["cand-1642", "cand-10484", "cand-3944"], relation=True,
)
add_statement(
    "st-chp15-p366-antenor-statue-made-by-andreosi", "cand-10484", "cand-0104",
    "statue_planned_to_be_made_by_andreosi",
    "Haskell says Francesco Andreosi was to make the offered statue of Antenor.", 17, 18,
    "to be made by\nFrancesco Andreosi", ["cand-10484", "cand-0104"], relation=True,
    qualification="The passage states the intended maker; it does not confirm completion.",
)
add_statement(
    "st-chp15-p366-antenor-statue-depicts-antenor", "cand-10484", "cand-10483",
    "statue_depicted_antenor",
    "Haskell identifies Antenor as the subject of the offered statue.", 17, 18,
    "Francesco Andreosi, of Antenor", ["cand-10484", "cand-10483"], relation=True,
)
add_statement(
    "st-chp15-p366-antenor-described-as-founder-of-padua", "cand-10483", "cand-3944",
    "described_as_legendary_founder_of_padua",
    "Haskell describes Antenor as the legendary founder of Padua.", 18, 18,
    "Antenor, the legendary founder of-Padua", ["cand-10483", "cand-3944"], relation=True,
    qualification="The legendary description is attributed to Haskell, not asserted as independently verified history.",
)
update_statement(
    "st-chp15-p366-duke-gloucester-azzo-statue",
    claim="Haskell says the Duke of Gloucester, passing through Padua, erected a statue of Azzo, Marchese d’Este.",
    quote="He was followed by the Duke of Gloucester who happened to be passing through and who erected a statue of Azzo, Marchese d’Este",
    mentioned=["cand-1204", "cand-10486", "cand-0981", "cand-3944"], relation=True,
)
update_statement(
    "st-chp15-p366-azzo-statue-subject",
    claim="Haskell identifies Azzo, Marchese d’Este, as the subject of the Duke’s statue.",
    quote="a statue of Azzo, Marchese d’Este",
    mentioned=["cand-10486", "cand-0981"], relation=True,
)
add_statement(
    "st-chp15-p366-azzo-described-as-paduan-citizen", "cand-0981", "cand-3944",
    "described_as_citizen_of_padua",
    "Haskell describes Azzo as a Paduan citizen.", 18, 18,
    "Azzo, Marchese d’Este, a Paduan citizen", ["cand-0981", "cand-3944"], relation=True,
)
add_statement(
    "st-chp15-p366-azzo-originator-of-house-of-brunswick", "cand-0981", "cand-10485",
    "described_as_originator_of_house_of_brunswick",
    "Haskell describes Azzo as the originator of the House of Brunswick.", 18, 18,
    "who had been the originator of the house of Brunswick", ["cand-0981", "cand-10485"], relation=True,
    qualification="This records Haskell’s description and does not infer a wider genealogy.",
)
update_statement(
    "st-chp15-p366-padua-offers-memmo-ancestor-statue",
    predicate="city_of_padua_offered_third_statue_for_scheme",
    claim="Haskell says the city of Padua offered a third statue for the scheme.",
    quote="And a third was offered by the city of Padua",
    mentioned=["cand-8406", "cand-10488"], relation=True,
)
add_statement(
    "st-chp15-p366-third-statue-depicts-memmo-ancestor", "cand-10488", "cand-10487",
    "third_statue_subject_was_memmo_ancestor_podesta",
    "Haskell says the city chose one of Memmo’s ancestors, a fourteenth-century podestà, as the third statue’s subject.", 18, 19,
    "which chose one of\nMemmo’s ancestors, a fourteenth century podestà",
    ["cand-10488", "cand-10487", "cand-1642"], relation=True,
    qualification="The ancestor is unnamed; his identity is not inferred.",
)
add_statement(
    "st-chp15-p366-memmo-declined-self-representation", "cand-1642", None,
    "memmo_declined_proposal_to_be_represented",
    "Haskell says Memmo declined a proposal that he himself be represented.", 19, 19,
    "after he had turned down their proposal that he himself should be represented",
    ["cand-1642"],
)
update_statement(
    "st-chp15-p366-poets-new-athens",
    quote="Within a few months enough progress had been made for the poets to ask whether they were dreaming or whether they really found themselves in some new Athens.",
)
update_statement(
    "st-chp15-p366-1777-progress-and-ambassadorship",
    subject="cand-1650", object_id=None, predicate="nineteen_statues_in_place_in_1777",
    claim="Haskell says that 19 statues were in place by the time of the 1777 progress report.",
    quote="with 19 statues in place", mentioned=["cand-1650"], relation=False,
)
add_statement(
    "st-chp15-p366-memmo-left-as-ambassador-1777", "cand-1642", "cand-10492",
    "memmo_left_for_four_year_ambassadorship_in_constantinople",
    "Haskell says Memmo left in 1777 for a four-year ambassadorship in Constantinople.", 20, 20,
    "But in 1777, with 19 statues in place, Memmo left for four years as Ambassador in Constantinople",
    ["cand-1642", "cand-10492", "cand-10491"], relation=True,
    qualification="The passage gives a year and duration, not exact start and end dates.",
)
update_statement(
    "st-chp15-p366-another-six-in-rome-ambiguous",
    quote="to be followed immediately by another six in Rome",
)
update_statement(
    "st-chp15-p366-difficulties-at-pra-while-memmo-away",
    subject="cand-1650", object_id=None, predicate="pra_encountered_difficulties_while_memmo_away",
    claim="Haskell says the Prà della Valle encountered serious difficulties while Memmo was away.",
    quote="While he was away the Prato della Valle ran into serious difficulties.",
    mentioned=["cand-1650", "cand-3960", "cand-11529"],
    qualification="OCR reads Prato; the printed page reads Prà. The councillors are unnamed.",
    ocr_correction={"source_file": SOURCE_FILE, "source_line": 20, "ocr": "Prato", "print": "Prà", "basis": "CHP-15.pdf physical page 6."},
)
add_statement(
    "st-chp15-p366-debts-piled-up", "cand-1650", None,
    "pra_project_debts_piled_up",
    "Haskell says debts piled up while Memmo was away.", 20, 20,
    "Debts piled up", ["cand-1650"],
)
add_statement(
    "st-chp15-p366-councillors-objected-to-expense", "cand-11529", "cand-1650",
    "councillors_objected_to_project_expense",
    "Haskell says the councillors objected to the expense of the Prà project.", 20, 20,
    "the councillors objected to the expense", ["cand-11529", "cand-1650"], relation=True,
)
add_statement(
    "st-chp15-p366-work-slowed-while-memmo-away", "cand-1650", None,
    "pra_project_work_slowed_while_memmo_away",
    "Haskell says work on the Prà project slowed alarmingly while Memmo was away.", 20, 20,
    "work slowed down alarmingly", ["cand-1650"],
)
update_statement(
    "st-chp15-p366-memmo-urges-friends-for-statues",
    subject="cand-1642", object_id="cand-11527", predicate="memmo_badgered_friends_to_contribute_statues",
    claim="Haskell says Memmo repeatedly pressed his friends to put up statues.",
    quote="He was constantly badgering his friends to put up statues",
    mentioned=["cand-1642", "cand-11527", "cand-1650"], relation=True,
    qualification="The friends are unnamed; this statement does not imply that every person contacted contributed.",
)
add_statement(
    "st-chp15-p366-memmo-proposed-subjects-to-friends", "cand-1642", "cand-11527",
    "memmo_proposed_statue_subjects_to_friends",
    "Haskell says Memmo proposed statue subjects to his friends.", 20, 20,
    "proposing subjects to them", ["cand-1642", "cand-11527", "cand-1650"], relation=True,
    qualification="The friends are unnamed and the proposed subjects are not listed in this sentence.",
)
add_statement(
    "st-chp15-p366-memmo-remained-enthusiastic-in-rome", "cand-1642", None,
    "memmo_remained_enthusiastic_in_rome",
    "Haskell says Memmo remained enthusiastic in Rome while away from Padua.", 20, 20,
    "Meanwhile in Rome Memmo remained as enthusiastic as ever",
    ["cand-1642", "cand-4490"],
)
add_statement(
    "st-chp15-p366-memmo-spread-ideas", "cand-1642", "cand-1650",
    "memmo_spread_his_ideas_for_the_scheme",
    "Haskell says Memmo spread his ideas in every way.", 20, 20,
    "spreading his ideas in every way", ["cand-1642", "cand-1650"],
)
update_statement(
    "st-chp15-p366-subleyras-plans-displayed",
    subject="cand-1642", object_id="cand-10494", predicate="memmo_displayed_plans_in_apartments",
    claim="Haskell says Memmo hung the plans in his apartments, where the nobility and distinguished visitors admired them.",
    quote="and hung in his apartments where they were admired by all the nobility and distinguished visitors",
    mentioned=["cand-1642", "cand-10494", "cand-8108", "cand-11528"], relation=True,
    qualification="The passage does not supply a title, exact number of drawings, or precise apartment location.",
)
add_statement(
    "st-chp15-p366-subleyras-drew-pra-plans", "cand-2532", "cand-10494",
    "subleyras_drew_plans_for_pra_scheme",
    "Haskell says Giuseppe Subleyras drew the plans for Memmo’s Prà scheme.", 20, 21,
    "He had his plans drawn by\nGiuseppe Subleyras, son of the French painter",
    ["cand-2532", "cand-1642", "cand-10494", "cand-1650"], relation=True,
    qualification="No title or exact number of drawings is supplied.",
)
update_statement(
    "st-chp15-p366-pope-and-visitors-contribute",
    subject="cand-11528", object_id="cand-1650", predicate="visitors_contributed_statues_following_popes_example",
    claim="Haskell says many distinguished visitors followed the Pope’s example and contributed a statue.",
    quote="many of whom, followed the example of the Pope and contributed a statue",
    mentioned=["cand-11528", "cand-10493", "cand-1650"], relation=True,
    qualification="The visitors and Pope are unnamed; the passage does not identify the individual statues.",
)
update_statement(
    "st-chp15-p366-poland-sweden-subscriptions",
    predicate="king_of_poland_subscribed_to_scheme",
    claim="Haskell says the King of Poland subscribed to the scheme.",
    quote="the Kings of Poland and Sweden both subscribed",
    mentioned=["cand-2505", "cand-1650"], relation=True,
)
add_statement(
    "st-chp15-p366-king-of-sweden-subscribed", "cand-1283", "cand-1650",
    "king_of_sweden_subscribed_to_scheme",
    "Haskell says the King of Sweden subscribed to the scheme.", 21, 21,
    "the Kings of Poland and Sweden both subscribed",
    ["cand-1283", "cand-1650"], relation=True,
    qualification="The text supplies the title; the p.366 index names Gustavus III, whose identity alignment remains for S3.",
)
update_statement(
    "st-chp15-p366-radicchio-account-accompanies-engraving",
    subject="cand-11526", object_id="cand-10495", predicate="radicchio_account_accompanied_engraving",
    claim="Haskell says an account was written in 1786 to accompany the engraving.",
    quote="one of Memiiio’s secretaries, Don Vincenzo Radicchio, wrote an account to accompany the engraving",
    mentioned=["cand-2089", "cand-1642", "cand-11526", "cand-10495"], relation=True,
    qualification="The account’s title and publication details are not supplied; the p.365 note 2 citation is linked but not identified as the same work.",
    ocr_correction={"source_file": SOURCE_FILE, "source_line": 22, "ocr": "Memiiio’s", "print": "Memmo’s", "basis": "CHP-15.pdf physical page 6."},
)
add_statement(
    "st-chp15-p366-radicchio-account-authored-by", "cand-11526", "cand-2089",
    "account_authored_by_radicchio",
    "Haskell identifies Don Vincenzo Radicchio as the author of the 1786 account.", 22, 22,
    "Don Vincenzo Radicchio, wrote an account", ["cand-2089", "cand-11526"], relation=True,
    qualification="The account is described by Haskell; the text itself has not been independently consulted.",
    ocr_corrections=[{"source_file": SOURCE_FILE, "source_line": 22, "ocr": "Memiiio’s", "print": "Memmo’s", "basis": "CHP-15.pdf physical page 6."}],
)
add_statement(
    "st-chp15-p366-radicchio-secretary-to-memmo", "cand-2089", "cand-1642",
    "radicchio_identified_as_memmos_secretary",
    "Haskell identifies Radicchio as one of Memmo’s secretaries.", 22, 22,
    "one of Memiiio’s secretaries, Don Vincenzo Radicchio", ["cand-2089", "cand-1642"], relation=True,
    qualification="The source describes a secretary role but gives no dates or further employment details.",
    ocr_corrections=[{"source_file": SOURCE_FILE, "source_line": 22, "ocr": "Memiiio’s", "print": "Memmo’s", "basis": "CHP-15.pdf physical page 6."}],
)
update_statement(
    "st-chp15-p366-memmo-expert-patron-reputation-partial",
    predicate="memmo_reputation_as_expert_and_patron_was_great",
    claim="Haskell says Memmo’s reputation as an expert and patron was by then very great.",
    quote="Memmo’s reputation as an expert and patron was by now very great",
    mentioned=["cand-1642"],
    qualification="P.367 separately records the publication of the Elementi; OCR reads ‘dining’ where the printed page reads ‘during’. The cross-page link is retained.",
    ocr_correction={"source_file": SOURCE_FILE, "source_line": 24, "ocr": "dining", "print": "during", "basis": "CHP-15.pdf physical page 6."},
)
update_statement(
    "st-chp15-p366-note1-memmo-contact-and-order-date",
    predicate="memmo_contacted_duke_during_first_visit_order_date_uncertain",
    relation=True,
)
add_statement(
    "st-chp15-p366-note1-egerton-letter-authored-by-memmo", "cand-10499", "cand-1642",
    "letter_authored_by_memmo",
    "Haskell’s note identifies Egerton MSS. 1969, no. 80 as a letter from Memmo.", 27, 27,
    "No. 80 is from Memmo in Padua, dated 18 October [1775]",
    ["cand-10499", "cand-1642"], relation=True, speaker="Haskell’s note", text_layer="citation trail",
    qualification="The manuscript has not been independently consulted.", cited_source_independently_consulted=False,
)
add_statement(
    "st-chp15-p366-note1-egerton-letter-addressed-to-strange", "cand-10499", "cand-2516",
    "letter_addressed_to_john_strange",
    "Haskell’s note says the cited letters were to John Strange.", 26, 26,
    "the letters to John Strange in the British Museum",
    ["cand-10499", "cand-2516"], relation=True, speaker="Haskell’s note", text_layer="citation trail",
    qualification="The cited manuscript has not been independently consulted.", cited_source_independently_consulted=False,
)
update_statement(
    "st-chp15-p366-note1-statue-and-strange-letter-1777",
    predicate="strange_letter_requested_drawing_of_dukes_statue",
    claim="Haskell’s note says that on 8 October 1777 Strange wrote to G. M. Sasso asking him to get Mingardi to make a drawing of the Duke’s statue.",
    quote="on the 8th of that month Strange wrote to G. M. Sasso asking him to get Mingardi to make a drawing of the statue in the Prato della Valle",
    mentioned=["cand-10500", "cand-10501", "cand-2516", "cand-2364", "cand-1669", "cand-10486", "cand-3960", "cand-1204"],
    relation=True,
    qualification="The letter and requested drawing have not been independently consulted; the passage does not establish that the drawing was completed. The p.373 note 2 cross-reference is resolved to the existing source-trail statement.",
    ocr_correction={"source_file": SOURCE_FILE, "source_line": 28, "ocr": "Prato", "print": "Prà", "basis": "CHP-15.pdf physical page 6."},
)
add_statement(
    "st-chp15-p366-note1-azzo-statue-erected-by-1777", "cand-10486", None,
    "dukes_statue_erected_by_october_1777",
    "Haskell’s note says the Duke’s statue had been erected by October 1777.", 27, 27,
    "the statue was erected by October 1777", ["cand-10486", "cand-1204"],
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="This is Haskell’s report; the cited letters have not been independently consulted.",
    cited_source_independently_consulted=False,
)
add_statement(
    "st-chp15-p366-note1-strange-letter-authored-by-strange", "cand-10500", "cand-2516",
    "letter_authored_by_john_strange",
    "Haskell’s note identifies John Strange as the writer of the 8 October 1777 letter.", 27, 27,
    "Strange wrote to G. M. Sasso", ["cand-10500", "cand-2516"], relation=True,
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The letter has not been independently consulted.", cited_source_independently_consulted=False,
)
add_statement(
    "st-chp15-p366-note1-strange-letter-addressed-to-sasso", "cand-10500", "cand-2364",
    "letter_addressed_to_g_m_sasso",
    "Haskell’s note identifies G. M. Sasso as the recipient of Strange’s letter.", 27, 27,
    "Strange wrote to G. M. Sasso", ["cand-10500", "cand-2364"], relation=True,
    speaker="Haskell’s note", text_layer="citation trail",
    qualification="The source abbreviates the recipient’s name; the candidate’s full form remains for S3 alignment. The letter has not been independently consulted.",
    cited_source_independently_consulted=False,
)

if "st-chp15-p366-general-appearance-mattered" not in statement_by_id:
    raise SystemExit("planned statement missing")
if any(row["qualifiers"].get("predicate_status") == "partial" for row in p366_statements):
    raise SystemExit("unexpected partial p.366 statement remains")

# Place new rows next to their page segment while preserving the table’s source order.
statement_positions = [i for i, row in enumerate(statements) if row.get("segment_id") == BODY]
if not statement_positions or statement_positions != list(range(statement_positions[0], statement_positions[-1] + 1)):
    raise SystemExit("p.366 statements are not a contiguous block; inspect before applying")
statements[statement_positions[-1] + 1:statement_positions[-1] + 1] = added_statements

new_mention_ids = {row["mention_id"] for row in new_mentions}
mentions = [row for row in mentions if row["mention_id"] not in new_mention_ids]
mention_positions = [i for i, row in enumerate(mentions) if row.get("segment_id") == BODY]
if not mention_positions:
    raise SystemExit("no existing p.366 mentions; inspect before applying")
insert_at = mention_positions[-1] + 1
new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
mentions[insert_at:insert_at] = new_mentions

candidate_ids = [row[0] for row in new_candidates]
new_relation_ids = [row["statement_id"] for row in added_statements if row["qualifiers"].get("relation_candidate")]
updated_relation_ids = [
    "st-chp15-p366-memmo-offers-antenor-statue",
    "st-chp15-p366-duke-gloucester-azzo-statue",
    "st-chp15-p366-azzo-statue-subject",
    "st-chp15-p366-padua-offers-memmo-ancestor-statue",
    "st-chp15-p366-memmo-urges-friends-for-statues",
    "st-chp15-p366-subleyras-plans-displayed",
    "st-chp15-p366-pope-and-visitors-contribute",
    "st-chp15-p366-poland-sweden-subscriptions",
    "st-chp15-p366-radicchio-account-accompanies-engraving",
    "st-chp15-p366-note1-memmo-contact-and-order-date",
    "st-chp15-p366-note1-statue-and-strange-letter-1777",
]
result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": sha256(SOURCE),
    "pdf_sha256": sha256(PDF),
    "updated_statements": len(updated_statement_ids),
    "updated_statement_ids": sorted(updated_statement_ids),
    "new_statements": len(added_statements),
    "new_mentions": [row["mention_id"] for row in new_mentions],
    "new_candidates": candidate_ids,
    "new_relation_candidates": new_relation_ids,
    "updated_relation_candidates": updated_relation_ids,
    "p366_counts_after": {"statements": len(p366_statements) + len(added_statements), "mentions": len(p366_mentions) + len(new_mentions)},
    "ocr_corrections": ["Prato -> Prà (L20, L28)", "Memiiio’s -> Memmo’s (L22)", "dining -> during (L24)"],
}

if args.apply:
    targets = [candidate_path, mention_path, statement_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in targets]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"recovery backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)

print(json.dumps(result, ensure_ascii=False, indent=2))
