"""Semantically complete the p.349 S2 body and its four footnotes.

Default mode is a dry run. Pass --apply only after reviewing the proposed
statement, candidate, and exact-mention changes printed below.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY_SEGMENT = "chp-14:14_CHP-14_intro:l23-33"
NOTES_SEGMENT = "chp-14:14_CHP-14_intro:l168-220"
BODY_SEGMENT_SHA256 = "1745cb7234b595f967f5d20f960d680c3f2635e0e1aafbeaecd6eff54fe6663b"
NOTES_SEGMENT_SHA256 = "72edc0571341795562aee96338a6bf5de6261bf0ee2f9948cd29ce23318edaa4"
SOURCE_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA256 = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
STATEMENTS_SHA256 = "f1c506986ccf97a39a5ee78050faea5ad15e87b5bdcec8f0c0bc0eb16aaae2ac"
CANDIDATES_SHA256 = "8a74da6327caf690fead892719c6e8396aebe3f39b80c74dff002f2bed15f673"
MENTIONS_SHA256 = "5e00149e1f2c33dc0f0b49c25cb37bce275e2da90da3168d1e574ac12e9bfb72"
BACKUP_SUFFIX = ".bak-s2-ch14-p349-semantic-review-20261014"

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12182",
        "index_entry_id": "",
        "canonical_name": "Italian culture (object of Algarotti's contribution in Haskell's p.349 account)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes Algarotti's rendering of complex European ideas in accessible forms as his most important contribution to Italian culture; this is a source-specific conceptual referent.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l23-33#L28",
    },
    {
        "candidate_id": "cand-12183",
        "index_entry_id": "",
        "canonical_name": "The Carracci (collective reference to painters in Haskell's p.349 account)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The source refers collectively to frescoes of 'the Carracci'; it does not specify which Carracci painters or works.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l23-33#L33",
    },
    {
        "candidate_id": "cand-12184",
        "index_entry_id": "",
        "canonical_name": "Ancient monuments of Rome (unnamed group in Haskell's p.349 account)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "A source-defined group of ancient monuments associated with Rome; no individual monument is named or identified.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l23-33#L33",
    },
    {
        "candidate_id": "cand-12185",
        "index_entry_id": "",
        "canonical_name": "Venetian artists with whom Algarotti had contact during his three returns (unnamed group)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell refers to the Venetian artists with whom Algarotti had direct contact during the three return periods; the group is unnamed and is not assumed to consist only of Tiepolo and Canaletto.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-14:14_CHP-14_intro:l23-33#L32",
    },
]

# surface_form, candidate_id, occurrence number in the assembled S0 segment, note
MENTION_SPECS = [
    ("Paris", "cand-4653", 0, ""),
    ("Paris", "cand-4653", 1, ""),
    ("Paris", "cand-4653", 2, ""),
    ("London", "cand-1422", 0, ""),
    ("Pierre Crozat", "cand-0894", 0, ""),
    ("Maupertuis", "cand-1585", 0, ""),
    ("Voltaire", "cand-2791", 0, ""),
    ("Voltaire", "cand-2791", 1, ""),
    ("Cirey", "cand-10254", 0, ""),
    ("Lord Hervey", "cand-1298", 0, ""),
    ("Lady Mary Wortley Montagu", "cand-1688", 0, ""),
    ("Italy", "cand-3461", 0, ""),
    ("Venice", "cand-2719", 0, ""),
    ("Milan", "cand-3418", 0, ""),
    ("the work", "cand-10258", 0, ""),
    ("Newtonianismo per le\nDame", "cand-10258", 0, "Title continues across the printed line break."),
    ("Algarotti’s", "cand-0080", 0, ""),
    ("Italian culture", "cand-12182", 0, ""),
    ("the book", "cand-10258", 0, ""),
    ("Venice", "cand-2719", 1, ""),
    ("Algarotti", "cand-0080", 0, ""),
    ("Italy", "cand-3461", 1, ""),
    ("Turin", "cand-2662", 0, ""),
    ("France", "cand-5317", 0, ""),
    ("England", "cand-8983", 0, ""),
    ("Russia", "cand-10255", 0, ""),
    ("Frederick the Great", "cand-1079", 0, ""),
    ("Augustus", "cand-0148", 0, ""),
    ("Elector of Saxony", "cand-10256", 0, ""),
    ("Dresden", "cand-0947", 0, ""),
    ("the King", "cand-0148", 0, "The page's index identifies the King as Augustus III."),
    ("Venice", "cand-2719", 2, ""),
    ("Prussia", "cand-10246", 0, ""),
    ("Venice", "cand-2719", 3, ""),
    ("Bologna", "cand-3398", 0, ""),
    ("Florence", "cand-3397", 0, ""),
    ("Pisa", "cand-5628", 0, ""),
    ("his native city", "cand-2719", 0, "Coreferential description of Venice in this sentence."),
    ("Venetian artists", "cand-12185", 0, "Source-defined unnamed group; not equated with the two artists named next."),
    ("Venetian", "cand-2719", 0, ""),
    ("Tiepolo", "cand-2572", 0, ""),
    ("Canaletto", "cand-0499", 0, ""),
    ("the city", "cand-2719", 0, "Coreferential description of Venice."),
    ("ancient monuments of Rome", "cand-12184", 0, "Unnamed monuments are retained as a source-defined group."),
    ("Rome", "cand-4490", 0, ""),
    ("the Carracci", "cand-12183", 0, "Collective wording; individual painters and frescoes are not specified."),
    ("Domenichino", "cand-0932", 0, ""),
    ("England", "cand-8983", 1, ""),
    ("France", "cand-5317", 1, ""),
    ("Crozat", "cand-0894", 1, ""),
    ("French rococo painting", "cand-6555", 0, ""),
    ("Berlin", "cand-9073", 0, ""),
    ("classical taste", "cand-10257", 0, ""),
]

NEW_STATEMENTS = [
    {
        "statement_id": "st-chp14-p349-stayed-with-voltaire-at-cirey",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-2791",
        "predicate": "stayed_with_at",
        "source_line_start": 24,
        "source_line_end": 24,
        "claim": "Algarotti stayed with Voltaire at Cirey during the period in which he resided in Paris.",
        "qualification": "Cirey is retained as a place candidate; the exact site identity remains unresolved.",
        "mentioned_candidate_ids": ["cand-0080", "cand-2791", "cand-10254"],
        "relation_candidate": True,
        "relation_candidate_note": "The person-to-person relation is distinct from the place where the stay occurred.",
        "quote": "Voltaire, with whom he stayed at Cirey.",
    },
    {
        "statement_id": "st-chp14-p349-not-altogether-well-received",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-10258",
        "object_candidate_id": None,
        "predicate": "reception_assessed_as_mixed",
        "source_line_start": 28,
        "source_line_end": 28,
        "claim": "Haskell says that Newtonianismo per le Dame was not altogether well received.",
        "qualification": "This is Haskell's reception assessment; the cited contemporary warning is recorded separately in note 3.",
        "mentioned_candidate_ids": ["cand-10258"],
        "relation_candidate": False,
        "quote": "was not alfògether well received.3",
        "footnote_marker": "3",
        "footnote_segment": NOTES_SEGMENT,
        "footnote_line_range": "L176",
        "footnote_text_pending": False,
        "footnote_body_link_status": "linked",
        "footnote_note_statement_ids": ["st-chp14-p349-note3-albrizzi-issue"],
    },
    {
        "statement_id": "st-chp14-p349-turin-diplomatic-mission",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-2662",
        "predicate": "undertook_diplomatic_mission_to",
        "source_line_start": 29,
        "source_line_end": 30,
        "claim": "Early in 1741, Algarotti made a diplomatic mission to Turin, the exception to his absence from Italy.",
        "qualification": "The source gives no mission purpose, office, or other participants.",
        "mentioned_candidate_ids": ["cand-0080", "cand-2662", "cand-3461"],
        "relation_candidate": True,
        "relation_candidate_note": "Preserve the source's stated exception and broad date; do not infer additional diplomatic roles.",
        "quote": "except for a diplomatic mission to\nTurin early in 1741.",
    },
    {
        "statement_id": "st-chp14-p349-stay-between-venice-and-milan",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": None,
        "predicate": "stayed_between",
        "source_line_start": 26,
        "source_line_end": 26,
        "claim": "At the end of 1736 Algarotti stayed for about a year in the area between Venice and Milan.",
        "qualification": "The source does not apportion the stay between the two cities or say that he resided in either city separately.",
        "mentioned_candidate_ids": ["cand-0080", "cand-2719", "cand-3418"],
        "relation_candidate": True,
        "relation_candidate_note": "Keep the source-defined location range open; do not create separate residence edges to Venice and Milan.",
        "quote": "stayed for about a year between Venice and Milan",
    },
    {
        "statement_id": "st-chp14-p349-venice-residence-1753-1756",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-2719",
        "predicate": "resided_in",
        "source_line_start": 30,
        "source_line_end": 30,
        "claim": "Algarotti was back in Venice from 1753 to 1756.",
        "qualification": "The source gives the interval but no more precise residence dates.",
        "mentioned_candidate_ids": ["cand-0080", "cand-2719"],
        "relation_candidate": True,
        "relation_candidate_note": "A dated return to Venice, distinct from the following interval and the later brief visit.",
        "quote": "He was back in Venice from 1753 to 1756",
    },
    {
        "statement_id": "st-chp14-p349-brief-visit-1760",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": None,
        "predicate": "made_short_visit",
        "source_line_start": 30,
        "source_line_end": 30,
        "claim": "Algarotti made a visit of less than a month in 1760.",
        "qualification": "The destination is not named in this clause and is left unresolved.",
        "mentioned_candidate_ids": ["cand-0080"],
        "relation_candidate": True,
        "relation_candidate_note": "Open S2 travel candidate; do not infer that the visit was to Venice from the preceding clause.",
        "quote": "except for a short visit of less than a month in 1760",
    },
    {
        "statement_id": "st-chp14-p349-resided-bologna-until-death",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-3398",
        "predicate": "resided_in",
        "source_line_start": 30,
        "source_line_end": 31,
        "claim": "Haskell lists Bologna among the places where Algarotti lived after his later Prussian and Venetian periods; this residence sequence continued until his death in 1764.",
        "qualification": "The source lists Bologna, Florence, and Pisa together and gives no city-specific entry or exit dates.",
        "mentioned_candidate_ids": ["cand-0080", "cand-3398"],
        "relation_candidate": True,
        "quote": "he lived in Bologna,",
    },
    {
        "statement_id": "st-chp14-p349-resided-florence-until-death",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-3397",
        "predicate": "resided_in",
        "source_line_start": 30,
        "source_line_end": 31,
        "claim": "Haskell lists Florence among the places where Algarotti lived after his later Prussian and Venetian periods; this residence sequence continued until his death in 1764.",
        "qualification": "The source lists Bologna, Florence, and Pisa together and gives no city-specific entry or exit dates.",
        "mentioned_candidate_ids": ["cand-0080", "cand-3397"],
        "relation_candidate": True,
        "quote": "Florence",
    },
    {
        "statement_id": "st-chp14-p349-resided-pisa-until-death",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-5628",
        "predicate": "resided_in",
        "source_line_start": 30,
        "source_line_end": 31,
        "claim": "Haskell lists Pisa among the places where Algarotti lived after his later Prussian and Venetian periods; this residence sequence continued until his death in 1764.",
        "qualification": "The source lists Bologna, Florence, and Pisa together and gives no city-specific entry or exit dates.",
        "mentioned_candidate_ids": ["cand-0080", "cand-5628"],
        "relation_candidate": True,
        "quote": "Pisa until his death in 1764.",
    },
    {
        "statement_id": "st-chp14-p349-direct-contact-with-venetian-artists",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-12185",
        "predicate": "had_direct_contact_with",
        "source_line_start": 32,
        "source_line_end": 32,
        "claim": "Haskell says Algarotti was in direct contact with Venetian artists only during his three short returns: most of 1737, 1743-1745, and 1753-1756.",
        "qualification": "The group is unnamed; it is not assumed to consist only of Tiepolo and Canaletto, who are mentioned in the next sentence as active in Venice.",
        "mentioned_candidate_ids": ["cand-0080", "cand-12185", "cand-2719"],
        "relation_candidate": True,
        "relation_candidate_note": "Source-defined group relation with bounded periods; member identities remain open.",
        "quote": "Only during these years was he in direct contact with the Venetian artists whose champion, patron and critic he professed himself.",
        "cross_reference_statement_ids": ["st-chp14-p349-three-visits-to-venice"],
    },
    {
        "statement_id": "st-chp14-p349-canaletto-active-during-three-visits",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0499",
        "object_candidate_id": "cand-2719",
        "predicate": "worked_in",
        "source_line_start": 32,
        "source_line_end": 32,
        "claim": "Haskell says Canaletto was at work in Venice during all three of Algarotti's return periods.",
        "qualification": "This reports activity in Venice during the three periods; it does not assert that Algarotti met Canaletto on every occasion.",
        "mentioned_candidate_ids": ["cand-0499", "cand-2719", "cand-0080"],
        "relation_candidate": True,
        "quote": "Yet on all three occasions Tiepolo and Canaletto were at work in the city",
        "cross_reference_statement_ids": ["st-chp14-p349-three-visits-to-venice"],
    },
    {
        "statement_id": "st-chp14-p349-carracci-fresco-influence",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-12183",
        "predicate": "was_converted_by_frescoes_of",
        "source_line_start": 33,
        "source_line_end": 33,
        "claim": "Haskell's retrospective account includes the frescoes of the Carracci among the experiences that converted Algarotti in 1734.",
        "qualification": "The source uses the collective plural 'the Carracci'; it does not identify which painters or frescoes.",
        "mentioned_candidate_ids": ["cand-0080", "cand-12183"],
        "relation_candidate": True,
        "relation_candidate_note": "The source-defined collective remains an open candidate; no individual Carracci or titled fresco is inferred.",
        "quote": "and the frescoes of the Carracci",
    },
    {
        "statement_id": "st-chp14-p349-domenichino-fresco-influence",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-0932",
        "predicate": "was_converted_by_frescoes_of",
        "source_line_start": 33,
        "source_line_end": 33,
        "claim": "Haskell's retrospective account includes frescoes by Domenichino among the experiences that converted Algarotti in 1734.",
        "qualification": "No individual fresco is named.",
        "mentioned_candidate_ids": ["cand-0080", "cand-0932"],
        "relation_candidate": True,
        "quote": "and Domenichino.",
    },
    {
            "statement_id": "st-chp14-p349-travel-in-england",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-8983",
        "predicate": "travelled_in",
        "source_line_start": 30,
        "source_line_end": 30,
        "claim": "During the interval before settling at Frederick the Great's court, Algarotti travelled in England.",
        "qualification": "The source gives France, England, and Russia as destinations without country-by-country dates or durations.",
        "mentioned_candidate_ids": ["cand-0080", "cand-8983"],
        "relation_candidate": True,
        "quote": "During the interval he travelled in France, England and Russia",
    },
    {
        "statement_id": "st-chp14-p349-travel-in-russia",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": "cand-10255",
        "predicate": "travelled_in",
        "source_line_start": 30,
        "source_line_end": 30,
        "claim": "During the interval before settling at Frederick the Great's court, Algarotti travelled in Russia.",
        "qualification": "The source gives France, England, and Russia as destinations without country-by-country dates or durations.",
        "mentioned_candidate_ids": ["cand-0080", "cand-10255"],
        "relation_candidate": True,
        "quote": "During the interval he travelled in France, England and Russia",
    },
    {
        "statement_id": "st-chp14-p349-insufficient-evidence-about-classical-taste",
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": "cand-0080",
        "object_candidate_id": None,
        "predicate": "evidence_insufficient_to_assess_travel_effect_on_taste",
        "source_line_start": 33,
        "source_line_end": 33,
        "claim": "Haskell says there is little information on whether the two years Algarotti spent in England and France modified his classical taste.",
        "qualification": "This is an explicit limit on the evidence, not a claim that travel had no effect.",
        "mentioned_candidate_ids": ["cand-0080", "cand-10257", "cand-8983", "cand-5317"],
        "relation_candidate": False,
        "quote": "Was anything likely to modify this classical taste during the two years he then spent in England and France? Unfortunately he gives us little information on this point",
    },
    {
        "statement_id": "st-chp14-p349-note1-paris-letters-part-of-collection",
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-10259",
        "object_candidate_id": "cand-11497",
        "predicate": "part_of",
        "source_line_start": 174,
        "source_line_end": 174,
        "claim": "The letters from Paris between November 1734 and January 1736 are included in the larger Treviso collection described in note 1.",
        "qualification": "The manuscripts and repository catalogue were not independently consulted.",
        "mentioned_candidate_ids": ["cand-10259", "cand-11497"],
        "relation_candidate": True,
        "quote": "Among the large collection of letters from Algarotti to his brother Bonomo in the Archivio Comunale in Treviso are a number from Paris between November 1734 and January 1736.",
    },
    {
        "statement_id": "st-chp14-p349-note1-collection-authored-by-algarotti",
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-11497",
        "object_candidate_id": "cand-0080",
        "predicate": "authored_by",
        "source_line_start": 174,
        "source_line_end": 174,
        "claim": "The large Treviso collection described in note 1 consists of letters from Francesco Algarotti.",
        "qualification": "This records Haskell's description of the collection, not independent manuscript inspection.",
        "mentioned_candidate_ids": ["cand-11497", "cand-0080"],
        "relation_candidate": True,
        "quote": "Among the large collection of letters from Algarotti to his brother Bonomo in the Archivio Comunale in Treviso are a number from Paris between November 1734 and January 1736.",
    },
    {
        "statement_id": "st-chp14-p349-note1-collection-addressed-to-bonomo",
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-11497",
        "object_candidate_id": "cand-0040",
        "predicate": "addressed_to",
        "source_line_start": 174,
        "source_line_end": 174,
        "claim": "The large Treviso collection described in note 1 contains letters from Algarotti to his brother Bonomo.",
        "qualification": "This records Haskell's description of the collection, not independent manuscript inspection.",
        "mentioned_candidate_ids": ["cand-11497", "cand-0040"],
        "relation_candidate": True,
        "quote": "Among the large collection of letters from Algarotti to his brother Bonomo in the Archivio Comunale in Treviso are a number from Paris between November 1734 and January 1736.",
    },
    {
        "statement_id": "st-chp14-p349-note1-collection-held-in-archivio",
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-11497",
        "object_candidate_id": "cand-10251",
        "predicate": "held_in",
        "source_line_start": 174,
        "source_line_end": 174,
        "claim": "Haskell locates the large Algarotti-Bonomo letter collection in the Archivio Comunale in Treviso.",
        "qualification": "This note does not specify a shelfmark for the collection; do not transfer MSS. 1256 from note 2 on p.348.",
        "mentioned_candidate_ids": ["cand-11497", "cand-10251"],
        "relation_candidate": True,
        "relation_candidate_note": "The repository is named, but this note supplies no collection-level shelfmark.",
        "quote": "Among the large collection of letters from Algarotti to his brother Bonomo in the Archivio Comunale in Treviso are a number from Paris between November 1734 and January 1736.",
    },
    {
        "statement_id": "st-chp14-p349-note4-zanotti-letter-published-in-opere",
        "segment_id": NOTES_SEGMENT,
        "subject_candidate_id": "cand-10262",
        "object_candidate_id": "cand-10263",
        "predicate": "published_in",
        "source_line_start": 177,
        "source_line_end": 177,
        "claim": "Haskell cites the G. P. Zanotti letter of 12 February 1735 as published in Opere, volume XI, page 213.",
        "qualification": "The letter and cited edition were not independently consulted.",
        "mentioned_candidate_ids": ["cand-10262", "cand-10263"],
        "relation_candidate": True,
        "quote": "Through a letter from G. P. Zanotti of 12 February 1733 published in Opere, XI, p. 213.",
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    return rows, lines


def write_jsonl_preserving_unmodified(path: Path, original_lines: list[str], rows: list[dict], changed: set[str]) -> bytes:
    by_id = {row["statement_id"]: row for row in rows}
    output: list[str] = []
    seen: set[str] = set()
    for line in original_lines:
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id in changed:
            output.append(json.dumps(by_id[statement_id], ensure_ascii=False, separators=(",", ":")))
        else:
            output.append(line)
        seen.add(statement_id)
    for row in rows:
        if row["statement_id"] not in seen:
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
    return ("\n".join(output) + "\n").encode("utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    payload = path.read_bytes()
    has_bom = payload.startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"missing CSV header in {path.name}")
        return list(reader.fieldnames), list(reader), has_bom


def serialize_csv(fields: list[str], rows: list[dict[str, str]], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    payload = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + payload) if has_bom else payload


def segment_text(segment_id: str, expected_hash: str) -> tuple[str, dict]:
    records = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    row = next((item for item in records if item.get("segment_id") == segment_id), None)
    if row is None:
        raise ValueError(f"missing segment {segment_id}")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(row["line_start"]) - 1 : int(row["line_end"])])
    if row.get("sha256") != expected_hash or hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_hash:
        raise ValueError(f"source segment hash changed: {segment_id}")
    return text, row


def add_statement(existing: dict, definition: dict) -> dict:
    q = {
        "source_line_start": definition["source_line_start"],
        "source_line_end": definition["source_line_end"],
        "printed_page": 349,
        "pdf_physical_page": 3,
        "claim": definition["claim"],
        "speaker": "Haskell",
        "text_layer": "authorial bibliographic note" if definition["segment_id"] == NOTES_SEGMENT else "biographical narrative",
        "qualification": definition["qualification"],
        "mentioned_candidate_ids": definition["mentioned_candidate_ids"],
        "relation_candidate": definition["relation_candidate"],
    }
    if definition.get("relation_candidate_note"):
        q["relation_candidate_note"] = definition["relation_candidate_note"]
    for key in ("footnote_marker", "footnote_segment", "footnote_line_range", "footnote_text_pending",
                "footnote_body_link_status", "footnote_note_statement_ids", "cross_reference_statement_ids"):
        if key in definition:
            q[key] = definition[key]
    return {
        "statement_id": definition["statement_id"],
        "segment_id": definition["segment_id"],
        "subject_candidate_id": definition["subject_candidate_id"],
        "object_candidate_id": definition["object_candidate_id"],
        "predicate": definition["predicate"],
        "qualifiers": q,
        "original_quote": definition["quote"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all source and table checks pass")
    args = parser.parse_args()

    for path, expected in (
        (STATEMENTS, STATEMENTS_SHA256), (CANDIDATES, CANDIDATES_SHA256), (MENTIONS, MENTIONS_SHA256),
        (SOURCE, SOURCE_SHA256), (PDF, PDF_SHA256),
    ):
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} sha256={actual}; expected={expected}")

    body_text, body_segment = segment_text(BODY_SEGMENT, BODY_SEGMENT_SHA256)
    note_text, _ = segment_text(NOTES_SEGMENT, NOTES_SEGMENT_SHA256)
    statement_rows, original_statement_lines = read_jsonl(STATEMENTS)
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    if len(statement_by_id) != len(statement_rows):
        raise SystemExit("statement_id is not unique before apply")
    candidate_fields, candidate_rows, candidate_bom = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = read_csv(MENTIONS)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
        raise SystemExit("one or more new candidate IDs already exist")
    body_mentions_before = [row for row in mention_rows if row["segment_id"] == BODY_SEGMENT]
    if body_mentions_before:
        raise SystemExit(f"p.349 body mention segment is not empty: {len(body_mentions_before)} rows")
    expected_unset = {
        "st-chp14-p349-rome-to-paris", "st-chp14-p349-paris-residence", "st-chp14-p349-work-significance",
        "st-chp14-p349-publication-reception", "st-chp14-p349-left-italy-and-turin-mission",
        "st-chp14-p349-return-to-prussia-and-italian-residence", "st-chp14-p349-three-visits-to-venice",
        "st-chp14-p349-tiepolo-canaletto-active", "st-chp14-p349-rome-classical-conversion",
        "st-chp14-p349-french-rococo-influence-inference", "st-chp14-p349-note1-bonomo-paris-letters",
        "st-chp14-p349-note2-halsband", "st-chp14-p349-note3-albrizzi-issue", "st-chp14-p349-note4-zanotti-letter",
    }
    for statement_id in expected_unset:
        row = statement_by_id.get(statement_id)
        if row is None or "relation_candidate" in row.get("qualifiers", {}):
            raise SystemExit(f"expected p.349 statement is absent or already classified: {statement_id}")
    for statement_id in (
        "st-chp14-p349-return-publish-newtonianismo", "st-chp14-p349-travel-in-france-england-russia",
        "st-chp14-p349-authored-newtonianismo", "st-chp14-p349-met-voltaire-and-cirey",
        "st-chp14-p349-travel-and-frederick-court", "st-chp14-p349-frederick-made-algarotti-count",
        "st-chp14-p349-venice-purchase-for-king", "st-chp14-p349-limited-evidence-about-crozat",
    ):
        if statement_id not in statement_by_id:
            raise SystemExit(f"required existing p.349 statement missing: {statement_id}")

    # Add source-defined candidate objects before constructing references to them.
    candidate_rows = candidate_rows + copy.deepcopy(NEW_CANDIDATES)
    candidate_ids = {row["candidate_id"] for row in candidate_rows}

    mention_rows_new: list[dict[str, str]] = []
    for number, (surface, candidate_id, occurrence, note) in enumerate(MENTION_SPECS, 1):
        if candidate_id not in candidate_ids:
            raise SystemExit(f"mention spec references unknown candidate {candidate_id}")
        positions = []
        offset = 0
        while True:
            index = body_text.find(surface, offset)
            if index < 0:
                break
            positions.append(index)
            offset = index + 1
        if occurrence >= len(positions):
            raise SystemExit(f"surface occurrence not found: {surface!r} occurrence={occurrence}")
        start = positions[occurrence]
        mention_rows_new.append({
            "mention_id": f"m-s2-ch14-p349-20261014-{number:03d}",
            "segment_id": BODY_SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })
    mention_rows.extend(mention_rows_new)

    changed_ids: set[str] = set()

    def update(statement_id: str, *, predicate: str | None = None, subject: str | None = None,
               object_: str | None | object = ..., quote: str | None = None,
               qualifier_updates: dict | None = None, remove_qualifier_keys: tuple[str, ...] = ()) -> None:
        row = statement_by_id[statement_id]
        q = copy.deepcopy(row.get("qualifiers") or {})
        if qualifier_updates:
            q.update(copy.deepcopy(qualifier_updates))
        for key in remove_qualifier_keys:
            q.pop(key, None)
        row["qualifiers"] = q
        if predicate is not None:
            row["predicate"] = predicate
        if subject is not None:
            row["subject_candidate_id"] = subject
        if object_ is not ...:
            row["object_candidate_id"] = object_
        if quote is not None:
            row["original_quote"] = quote
        changed_ids.add(statement_id)

    # Classify the two previously unclassified movement statements and split their endpoints.
    update("st-chp14-p349-rome-to-paris", qualifier_updates={
        "relation_candidate": True,
        "relation_candidate_note": "The p.349 continuation closes the sentence begun on p.348; the destination is Paris and the printed reading is 'left'.",
    })
    update("st-chp14-p349-paris-residence", qualifier_updates={
        "relation_candidate": True,
        "relation_candidate_note": "The pronoun refers to Paris in the preceding clause; duration remains unspecified.",
    })
    update("st-chp14-p349-met-crozat", qualifier_updates={
        "mentioned_candidate_ids": ["cand-0080", "cand-0894", "cand-4653"],
    })
    update("st-chp14-p349-met-maupertuis", qualifier_updates={
        "mentioned_candidate_ids": ["cand-0080", "cand-1585", "cand-4653"],
    })
    update("st-chp14-p349-met-voltaire-and-cirey", predicate="met", quote="he met Pierre Crozat, Maupertuis and Voltaire",
           qualifier_updates={
               "claim": "During his Paris residence Algarotti met Voltaire.",
               "qualification": "This is separate from the lodging at Cirey recorded in its own statement.",
               "mentioned_candidate_ids": ["cand-0080", "cand-2791", "cand-4653"],
           })
    for statement_id, person_id in (
        ("st-chp14-p349-social-advances-hervey", "cand-1298"),
        ("st-chp14-p349-social-advances-montagu", "cand-1688"),
    ):
        row = statement_by_id[statement_id]
        current = row["qualifiers"].get("mentioned_candidate_ids", [])
        update(statement_id, qualifier_updates={
            "mentioned_candidate_ids": sorted(set(current + ["cand-4653", "cand-1422", person_id])),
        })

    update("st-chp14-p349-return-publish-newtonianismo", predicate="returned_to", object_="cand-3461",
           quote="he returned to\nItaly at the very end of 1736",
           qualifier_updates={
               "claim": "At the very end of 1736 Algarotti returned to Italy.",
               "qualification": "The following stay between Venice and Milan is recorded separately without assigning a separate residence to either city.",
               "mentioned_candidate_ids": ["cand-0080", "cand-3461"],
               "relation_candidate": True,
               "relation_candidate_note": "A source-reported return to Italy; the adjacent stay between cities remains a separate open location range.",
           })
    update("st-chp14-p349-work-significance", predicate="contributed_to", object_="cand-12182",
           qualifier_updates={
               "claim": "Haskell describes Newtonianismo per le Dame as the first of a series of works through which Algarotti made what Haskell calls his most important contribution to Italian culture: rendering complex European ideas in accessible forms.",
               "qualification": "This is Haskell's evaluative and source-attributed claim; the named work and conceptual object are kept separate.",
               "mentioned_candidate_ids": ["cand-0080", "cand-10258", "cand-12182"],
               "work_candidate_id": "cand-10258",
               "relation_candidate": True,
               "relation_candidate_note": "The source explicitly frames the work as a contribution to Italian culture; preserve Haskell's attribution and evaluation.",
           })
    update("st-chp14-p349-publication-reception", predicate="could_not_be_published_in", object_="cand-2719",
           quote="the book proved impossible to publish in Venice",
           qualifier_updates={
               "claim": "Haskell says Newtonianismo per le Dame could not be published in Venice.",
               "qualification": "The source attributes the impossibility to the reason stated in the preceding context but does not name a censor or authority.",
               "mentioned_candidate_ids": ["cand-10258", "cand-2719"],
               "relation_candidate": True,
               "relation_candidate_note": "A source-reported publication constraint with a named place; no responsible authority is inferred.",
           }, remove_qualifier_keys=("footnote_marker", "footnote_segment", "footnote_line_range", "footnote_text_pending", "footnote_body_link_status", "footnote_note_statement_ids"))
    update("st-chp14-p349-left-italy-and-turin-mission", predicate="left_and_later_returned_to", object_="cand-3461",
           quote="Immediately after its appearance in December\n1737 Algarotti left Italy, not to return till May 1743",
           qualifier_updates={
               "claim": "After the book appeared in December 1737, Algarotti left Italy and did not return until May 1743; the early-1741 Turin mission is recorded separately as the stated exception.",
               "qualification": "The source supplies the broad interval and one explicitly named exception; the exception is not treated as a full return to Italy.",
               "mentioned_candidate_ids": ["cand-0080", "cand-3461"],
               "relation_candidate": True,
               "relation_candidate_note": "The relation records departure and later return to Italy, while the Turin exception has its own endpoint and date.",
           })

    # Separate the multi-country itinerary from the court settlement and title.
    update("st-chp14-p349-travel-in-france-england-russia", predicate="travelled_in", object_="cand-5317",
           quote="During the interval he travelled in France",
           qualifier_updates={
               "printed_page": 349, "pdf_physical_page": 3,
               "claim": "During the interval before settling at Frederick the Great's court, Algarotti travelled in France.",
               "qualification": "The source gives France, England, and Russia as destinations without country-by-country dates or durations.",
               "mentioned_candidate_ids": ["cand-0080", "cand-5317"],
               "relation_candidate": True,
           })
    update("st-chp14-p349-travel-and-frederick-court", quote="before settling in the court of one of his most enthusiastic admirers, Frederick the Great",
           qualifier_updates={
               "claim": "Haskell reports that Algarotti settled at the court of Frederick the Great.",
               "mentioned_candidate_ids": ["cand-0080", "cand-1079"],
           })
    update("st-chp14-p349-frederick-made-algarotti-count", qualifier_updates={"printed_page": 349, "pdf_physical_page": 3})
    update("st-chp14-p349-authored-newtonianismo", predicate="published", quote="where he published the work that brought him immediate fame, Newtonianismo per le\nDame.",
           qualifier_updates={
               "claim": "Algarotti published Newtonianismo per le Dame, which Haskell says brought him immediate fame.",
               "qualification": "The text states that Algarotti published the work; it does not specify an edition or publication imprint on this page.",
               "mentioned_candidate_ids": ["cand-0080", "cand-10258"],
           })

    # Split the compound return/residence clauses into source-bounded endpoint claims.
    update("st-chp14-p349-return-to-prussia-and-italian-residence", predicate="returned_to", object_="cand-10246",
           quote="He then returned to Prussia for eight more years.",
           qualifier_updates={
               "claim": "After the Venice period ending in 1745, Algarotti returned to Prussia for eight more years.",
               "qualification": "The source gives an approximate duration and no more precise residence dates.",
               "mentioned_candidate_ids": ["cand-0080", "cand-10246"],
               "relation_candidate": True,
               "relation_candidate_note": "A source-reported return to Prussia; later Italian residences are recorded separately.",
           })
    update("st-chp14-p349-three-visits-to-venice", quote="Thus, after leaving Venice at the age of 20, he only returned to his native city for three relatively short visits—most of 1737; 1743-5! 1753-6.",
           qualifier_updates={
               "claim": "Haskell summarizes three relatively short returns by Algarotti to his native Venice: most of 1737, 1743-1745, and 1753-1756.",
               "qualification": "The printed page uses a semicolon between the latter two date ranges; S0's exclamation mark is recorded as an OCR correction.",
               "mentioned_candidate_ids": ["cand-0080", "cand-2719"],
               "ocr_corrections": [{"source_line": 32, "ocr": "1743-5!", "print": "1743-5;", "basis": "CHP-14.pdf physical page 3."}],
               "relation_candidate": True,
               "relation_candidate_note": "Grouped visit history with Venice as the single endpoint; each date range is preserved.",
           })
    update("st-chp14-p349-tiepolo-canaletto-active", subject="cand-2572", object_="cand-2719", predicate="worked_in",
           qualifier_updates={
               "claim": "Haskell says Tiepolo was at work in Venice during all three of Algarotti's return periods.",
               "qualification": "This reports activity in Venice during the three periods; it does not assert that Algarotti met Tiepolo on every occasion.",
               "mentioned_candidate_ids": ["cand-2572", "cand-2719", "cand-0080"],
               "relation_candidate": True,
               "cross_reference_statement_ids": ["st-chp14-p349-three-visits-to-venice"],
           })
    update("st-chp14-p349-rome-classical-conversion", object_="cand-12184", predicate="was_converted_by",
           quote="We left him in 1734 converted by die ancient monuments of Rome",
           qualifier_updates={
               "claim": "Haskell retrospectively says Algarotti was converted in 1734 by the ancient monuments of Rome.",
               "qualification": "This is Haskell's retrospective characterization; no individual monument is identified.",
               "mentioned_candidate_ids": ["cand-0080", "cand-12184", "cand-4490"],
               "relation_candidate": True,
               "relation_candidate_note": "The source names an unnamed monument group located in Rome; no specific building or work is inferred.",
               "ocr_corrections": [{"source_line": 33, "ocr": "die", "print": "the", "basis": "CHP-14.pdf physical page 3."}],
           })
    update("st-chp14-p349-limited-evidence-about-crozat", quote="it is only indirectly that we hear of his meetings with Crozat.4",
           qualifier_updates={
               "claim": "Haskell says that Algarotti's meetings with Crozat are known only indirectly; note 4 cites a G. P. Zanotti letter.",
               "qualification": "The cited letter and edition were not independently consulted.",
               "mentioned_candidate_ids": ["cand-0080", "cand-0894", "cand-7114", "cand-10262", "cand-10263"],
               "relation_candidate": True,
           })

    # The note statements encode source-backed relations when the note gives those relations.
    update("st-chp14-p349-note1-bonomo-paris-letters", subject="cand-10259", object_="cand-4653", predicate="originated_from",
           qualifier_updates={
               "claim": "The note identifies letters from Paris between November 1734 and January 1736 within the larger Treviso collection.",
               "qualification": "The manuscript collection and repository catalogue were not independently consulted.",
               "mentioned_candidate_ids": ["cand-10259", "cand-4653", "cand-11497"],
               "relation_candidate": True,
               "relation_candidate_note": "The location and period apply to the Paris subset of the larger collection.",
           })
    update("st-chp14-p349-note2-halsband", qualifier_updates={
        "relation_candidate": False,
        "relation_candidate_note": "A bare bibliographic surname supplies no independently stated person-to-person, work, or place relation.",
    })
    update("st-chp14-p349-note3-albrizzi-issue", subject="cand-10261", object_="cand-10258", predicate="warned_readers_about",
           qualifier_updates={
               "claim": "The 12 April 1758 issue of Novelle della Repubblica delle Lettere warned readers to treat some expressions and sentiments in the book with circumspection, especially Christian youth.",
               "qualification": "The work is supplied by the linked body sentence and footnote marker; the periodical issue was not independently consulted.",
               "mentioned_candidate_ids": ["cand-10261", "cand-10258", "cand-9988", "cand-0025"],
               "relation_candidate": True,
               "relation_candidate_note": "The warning is quoted in the footnote attached to Haskell's reception statement; preserve that evidential path.",
           })
    update("st-chp14-p349-note4-zanotti-letter", subject="cand-10262", object_="cand-7114", predicate="authored_by",
           qualifier_updates={
               "claim": "Haskell attributes the cited letter of 12 February 1735 to G. P. Zanotti.",
               "qualification": "The OCR gives 1733; the printed page reads 1735. The letter was not independently consulted.",
               "mentioned_candidate_ids": ["cand-10262", "cand-7114"],
               "relation_candidate": True,
               "ocr_corrections": [{"source_line": 177, "ocr": "1733", "print": "1735", "basis": "CHP-14.pdf physical page 3."}],
           })

    update("st-chp14-p349-french-rococo-influence-inference", qualifier_updates={
        "relation_candidate": True,
        "relation_candidate_note": "This is Haskell's modal inference about influence; preserve 'must have been powerful' rather than treating it as independently established influence.",
    })
    update("st-chp14-p349-travel-in-france-england-russia", predicate="travelled_in", object_="cand-5317",
           quote="During the interval he travelled in France",
           qualifier_updates={
               "claim": "During the interval before settling at Frederick the Great's court, Algarotti travelled in France.",
               "qualification": "The source gives France, England, and Russia as destinations without country-by-country dates or durations.",
               "mentioned_candidate_ids": ["cand-0080", "cand-5317"],
               "relation_candidate": True,
               "printed_page": 349,
               "pdf_physical_page": 3,
           })
    update("st-chp14-p349-frederick-made-algarotti-count", qualifier_updates={"printed_page": 349, "pdf_physical_page": 3})

    # Append each reviewed atomic statement exactly once.
    new_ids = [definition["statement_id"] for definition in NEW_STATEMENTS]
    if len(new_ids) != len(set(new_ids)) or any(statement_id in statement_by_id for statement_id in new_ids):
        raise SystemExit("new p.349 statement_id collision")
    new_statement_rows = [add_statement(statement_by_id, definition) for definition in NEW_STATEMENTS]
    statement_rows.extend(new_statement_rows)
    changed_ids.update(new_ids)
    statement_by_id = {row["statement_id"]: row for row in statement_rows}

    # Ensure every previously unset p.349 decision was made explicitly; never default a judgment to false.
    for statement_id in expected_unset:
        row = statement_by_id[statement_id]
        q = row["qualifiers"]
        if "relation_candidate" not in q:
            raise SystemExit(f"missing explicit relation decision: {statement_id}")
        q.setdefault("printed_page", 349)
        q.setdefault("pdf_physical_page", 3)
        q.setdefault("speaker", "Haskell")
        changed_ids.add(statement_id)
    for statement_id in ("st-chp14-p349-travel-in-france-england-russia", "st-chp14-p349-frederick-made-algarotti-count"):
        statement_by_id[statement_id]["qualifiers"].update({"printed_page": 349, "pdf_physical_page": 3})
        changed_ids.add(statement_id)

    # Make remaining classification decisions explicit; note 2 is a bare citation, note 1/3/4 carry relations.
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    for statement_id, relation in (
        ("st-chp14-p349-note1-bonomo-paris-letters", True),
        ("st-chp14-p349-note2-halsband", False),
        ("st-chp14-p349-note3-albrizzi-issue", True),
        ("st-chp14-p349-note4-zanotti-letter", True),
    ):
        statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = relation
        statement_by_id[statement_id]["qualifiers"].update({"printed_page": 349, "pdf_physical_page": 3})
        changed_ids.add(statement_id)

    # Validate every new claim against the immutable source text and candidate registry.
    all_statement_ids = [row["statement_id"] for row in statement_rows]
    if len(all_statement_ids) != len(set(all_statement_ids)):
        raise SystemExit("statement_id collision after planned additions")
    for row in statement_rows:
        if row["segment_id"] not in (BODY_SEGMENT, NOTES_SEGMENT):
            continue
        q = row.get("qualifiers", {})
        if q.get("printed_page") != 349 or q.get("pdf_physical_page") != 3:
            continue
        source_text = body_text if row["segment_id"] == BODY_SEGMENT else note_text
        if row["original_quote"] not in source_text:
            raise SystemExit(f"original_quote is not an exact source substring: {row['statement_id']}")
        for candidate_id in q.get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_ids:
                raise SystemExit(f"unknown mentioned candidate {candidate_id} in {row['statement_id']}")
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key) and row[key] not in candidate_ids:
                raise SystemExit(f"unknown {key} {row[key]} in {row['statement_id']}")
    if any(row["qualifiers"].get("relation_candidate") not in (True, False)
           for row in statement_rows if row["segment_id"] in (BODY_SEGMENT, NOTES_SEGMENT)
           and row["qualifiers"].get("printed_page") == 349):
        raise SystemExit("p.349 statement still has an unset relation_candidate status")

    # Validate exact mention anchors and the same non-overlap contract used by audit_tables.py.
    for row in mention_rows_new:
        start, end = int(row["start_char"]), int(row["end_char"])
        if body_text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']}")
    intervals = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"]) for r in mention_rows_new)
    for index, left in enumerate(intervals):
        for right in intervals[index + 1:]:
            if right[0] >= left[1]:
                break
            nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
            if left[:2] == right[:2] or not nested:
                raise SystemExit(f"duplicate or crossing new p.349 mention spans: {left[2]} / {right[2]}")

    statement_payload = write_jsonl_preserving_unmodified(STATEMENTS, original_statement_lines, statement_rows, changed_ids)
    candidate_payload = serialize_csv(candidate_fields, candidate_rows, candidate_bom)
    mention_payload = serialize_csv(mention_fields, mention_rows, mention_bom)
    print(f"p349_body_statements={sum(r['segment_id'] == BODY_SEGMENT for r in statement_rows)}")
    print(f"p349_note_statements={sum(r['segment_id'] == NOTES_SEGMENT and r['qualifiers'].get('printed_page') == 349 for r in statement_rows)}")
    print(f"new_statements={len(NEW_STATEMENTS)}; new_candidates={len(NEW_CANDIDATES)}; new_body_mentions={len(mention_rows_new)}")
    print(f"statement_sha256={digest(statement_payload)}; candidate_sha256={digest(candidate_payload)}; mentions_sha256={digest(mention_payload)}")
    print("all new source quotes and mention spans are exact; all p.349 statement relation decisions are set")
    if not args.apply:
        print("dry_run=true; no files written")
        return 0

    files = [(STATEMENTS, statement_payload), (CANDIDATES, candidate_payload), (MENTIONS, mention_payload)]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path, _ in files]
    for original_path, backup_path in backups:
        if backup_path.exists() and sha(backup_path) != sha(original_path):
            raise SystemExit(f"existing batch backup does not match current source: {backup_path.name}")
    for original_path, backup_path in backups:
        if not backup_path.exists():
            shutil.copy2(original_path, backup_path)
    try:
        for path, payload in files:
            path.write_bytes(payload)
        for path, payload in files:
            if sha(path) != digest(payload):
                raise OSError(f"post-write hash mismatch: {path.name}")
    except Exception:
        for original_path, backup_path in backups:
            shutil.copy2(backup_path, original_path)
        raise
    print("applied=true")
    for original_path, backup_path in backups:
        print(f"backup={backup_path.name}; written_sha256={sha(original_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
