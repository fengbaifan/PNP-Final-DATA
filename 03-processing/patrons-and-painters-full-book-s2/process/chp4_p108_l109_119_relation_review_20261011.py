#!/usr/bin/env python3
"""Classify and atomize the p.108 S2 statements with a hash-locked writeback."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l109-119"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "831e90691fb1d82f1bbc6c09514dd007e656f461a959eecd4a37d480b7c4492e"
STATEMENTS_SHA256 = "51fe364f9bd087d86dde3f263282b14bc99a005572b1147781320766013a99b1"
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l109-119-relations-20261011"

ORIGINAL_IDS = {
    "st-chp4-sec-ii-l109-119-bouchard-papers-continued",
    "st-chp4-sec-ii-l109-119-cassiano-friendly-writing-to-galileo",
    "st-chp4-sec-ii-l109-119-cassiano-religious-position-qualified",
    "st-chp4-sec-ii-l109-119-cassiano-science-and-new-thought",
    "st-chp4-sec-ii-l109-119-cassiano-shows-papers-to-dupuy",
    "st-chp4-sec-ii-l109-119-dati-disciple-friend",
    "st-chp4-sec-ii-l109-119-dati-pages-orthodoxy-alchemy",
    "st-chp4-sec-ii-l109-119-dati-rhetorical-question",
    "st-chp4-sec-ii-l109-119-dupuy-indignation-uncertain",
    "st-chp4-sec-ii-l109-119-dupuy-knew-official-bouchard",
    "st-chp4-sec-ii-l109-119-dupuy-letter-to-brother",
    "st-chp4-sec-ii-l109-119-dupuy-prior-in-rome",
    "st-chp4-sec-ii-l109-119-dupuy-quoted-account",
    "st-chp4-sec-ii-l109-119-galileo-condemnation",
    "st-chp4-sec-ii-l109-119-galileo-letter-from-arcetri",
    "st-chp4-sec-ii-l109-119-galileo-thanks-for-portrait",
    "st-chp4-sec-ii-l109-119-naude-alternative-response",
    "st-chp4-sec-ii-l109-119-portraits-naude-fragment",
    "st-chp4-sec-ii-l109-119-science-spiritual-danger",
}

NEW_IDS = {
    "st-chp4-sec-ii-l109-119-cassiano-passionate-student-science",
    "st-chp4-sec-ii-l109-119-dati-friend-cassiano",
    "st-chp4-sec-ii-l109-119-dati-pages-about-cassiano-orthodoxy-alchemy",
    "st-chp4-sec-ii-l109-119-dati-attributes-praise-of-god-to-cassiano",
    "st-chp4-sec-ii-l109-119-dupuy-shared-indignation-unknown",
    "st-chp4-sec-ii-l109-119-dupuy-returns-collection-to-cassiano",
    "st-chp4-sec-ii-l109-119-galileo-portrait-kept-in-cassiano-library",
    "st-chp4-sec-ii-l109-119-naude-alternative-response-to-science",
}

RELATION_NOTES = {
    "st-chp4-sec-ii-l109-119-bouchard-papers-continued":
        "Haskell attributes the description to the contents of Bouchard's private papers; this is a source-level evidentiary link, not independent verification of the alleged beliefs.",
    "st-chp4-sec-ii-l109-119-cassiano-friendly-writing-to-galileo":
        "Haskell reports a particular friendly communication; the approximate interval is retained and this does not by itself establish a sustained correspondence.",
    "st-chp4-sec-ii-l109-119-cassiano-science-and-new-thought":
        "This records Haskell's qualified account of Cassiano's sympathy with unspecified new thought during a conflict with the papacy.",
    "st-chp4-sec-ii-l109-119-cassiano-shows-papers-to-dupuy":
        "Haskell reports Cassiano showing the papers to Dupuy in 1641; custody and the exact identity of the material remain source-limited.",
    "st-chp4-sec-ii-l109-119-dati-disciple-friend":
        "This retains only the stated teacher-disciple relation; Dati's friendship with Cassiano is recorded separately.",
    "st-chp4-sec-ii-l109-119-dupuy-knew-official-bouchard":
        "The relation is limited to Dupuy's prior knowledge of Bouchard's restrained public persona as reported by Haskell.",
    "st-chp4-sec-ii-l109-119-dupuy-letter-to-brother":
        "The archive endpoint is the reported letter and the person endpoint is its unnamed recipient; Dupuy is its reported author, and neither identity is independently verified here.",
    "st-chp4-sec-ii-l109-119-dupuy-prior-in-rome":
        "This records Dupuy's reported office in the Carthusian Order at Rome; the province or local house is unspecified.",
    "st-chp4-sec-ii-l109-119-galileo-condemnation":
        "Haskell uses the condemnation as a temporal reference; the Inquisition tribunal and proceeding are not further identified.",
    "st-chp4-sec-ii-l109-119-galileo-letter-from-arcetri":
        "The archive endpoint is the reported 1641 letter and Cassiano its recipient; Galileo is preserved as sender and Villa d'Arcetri as the letter's stated origin.",
    "st-chp4-sec-ii-l109-119-galileo-thanks-for-portrait":
        "This records Galileo's reported thanks to Cassiano; the portrait's presence in Cassiano's library is stated separately.",
    "st-chp4-sec-ii-l109-119-naude-alternative-response":
        "The explicit phrase 'Cassiano's great friend' supports this person-to-person relation; Naude's comparative role is recorded separately.",
    "st-chp4-sec-ii-l109-119-portraits-naude-fragment":
        "The source explicitly says the unspecified portraits carry inscriptions written by Naude; the sentence continues into the next page, where a separate Cassiano-Gaudenzi relation is introduced.",
    "st-chp4-sec-ii-l109-119-dati-friend-cassiano":
        "Haskell explicitly calls Dati Cassiano's friend; this is separated from the distinct disciple relation.",
    "st-chp4-sec-ii-l109-119-dati-pages-about-cassiano-orthodoxy-alchemy":
        "Haskell says Dati devoted pages to Cassiano's religious orthodoxy and detestation of alchemy; the specific Dati work is not identified beyond the cited note.",
    "st-chp4-sec-ii-l109-119-dupuy-returns-collection-to-cassiano":
        "In the quotation attributed to Dupuy, he says he returned the collection to Cassiano that same hour; the collection's relation to Bouchard's papers remains unestablished.",
    "st-chp4-sec-ii-l109-119-galileo-portrait-kept-in-cassiano-library":
        "Haskell reports that Cassiano kept the unidentified portrait in his library; no artist, surviving object, or present location is established.",
}

NONRELATION_NOTES = {
    "st-chp4-sec-ii-l109-119-cassiano-religious-position-qualified":
        "This is Haskell's paired assessment of two religious identifications as unlikely, not an asserted affiliation.",
    "st-chp4-sec-ii-l109-119-dati-pages-orthodoxy-alchemy":
        "This records Haskell's scalar evaluation of Dati's treatment as over-shrill; the subject matter and Dati-Cassiano relation are recorded separately.",
    "st-chp4-sec-ii-l109-119-dati-rhetorical-question":
        "This is a rhetorical argument attributed to Dati through Haskell, not independent evidence of either man's beliefs.",
    "st-chp4-sec-ii-l109-119-dupuy-indignation-uncertain":
        "This preserves Haskell's inference that Cassiano could hardly have been surprised; it does not assert that he shared Dupuy's reaction.",
    "st-chp4-sec-ii-l109-119-dupuy-quoted-account":
        "This retains Dupuy's attributed description of the collection's contents and reaction; the return to Cassiano is a separate relation candidate.",
    "st-chp4-sec-ii-l109-119-science-spiritual-danger":
        "This is a general authorial statement about scientific inquiry and unnamed contemporaries, not a relation between Cassiano and a bounded group.",
    "st-chp4-sec-ii-l109-119-cassiano-passionate-student-science":
        "This is Haskell's scalar characterization of Cassiano's intellectual interest.",
    "st-chp4-sec-ii-l109-119-dati-attributes-praise-of-god-to-cassiano":
        "This is a claim attributed to Dati about Cassiano's religious praise, not a relation between Dati and Cassiano.",
    "st-chp4-sec-ii-l109-119-dupuy-shared-indignation-unknown":
        "Haskell explicitly says the passage does not tell us whether Cassiano shared Dupuy's indignation.",
    "st-chp4-sec-ii-l109-119-naude-alternative-response-to-science":
        "This is Haskell's comparative interpretation; the alternative response is not specified closely enough to form an entity endpoint.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def quote_between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at) + len(end)
    return text[start_at:end_at]


def set_classification(row: dict, is_relation: bool, note: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = is_relation
    qualifiers["relation_candidate_note"] = note


def set_quote_claim(
    row: dict,
    *,
    predicate: str,
    claim: str,
    quote: str,
    subject: str | None,
    object_: str | None,
    qualification: str | None = None,
    line_start: int | None = None,
    line_end: int | None = None,
) -> None:
    row["predicate"] = predicate
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["original_quote"] = quote
    q = row["qualifiers"]
    q["claim"] = claim
    if qualification is not None:
        q["qualification"] = qualification
    if line_start is not None:
        q["source_line_start"] = line_start
    if line_end is not None:
        q["source_line_end"] = line_end


def make_statement(
    statement_id: str,
    *,
    subject: str | None,
    object_: str | None,
    predicate: str,
    claim: str,
    quote: str,
    line_start: int,
    line_end: int,
    speaker: str,
    is_relation: bool,
    note: str,
    mentioned: list[str],
    qualification: str,
    footnote_from: dict | None = None,
) -> dict:
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": 19,
        "printed_page_locator": "p.108",
        "claim": claim,
        "speaker": speaker,
        "text_layer": "authorial narrative",
        "mentioned_candidate_ids": mentioned,
        "qualification": qualification,
        "relation_candidate": is_relation,
        "relation_candidate_note": note,
    }
    if footnote_from:
        for key, value in footnote_from.items():
            if key.startswith("footnote_"):
                q[key] = value
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def counts(rows: list[dict]) -> dict[str, int]:
    dual = [
        row for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    return {
        "statements": len(rows),
        "dual": len(dual),
        "relation_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in rows),
        "relation_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in rows),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "unclassified": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in rows),
    }


def totals(rows: list[dict], candidates: int, mentions: int) -> dict[str, int]:
    dual = [
        row for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    return {
        "all_statements": len(rows),
        "all_candidates": candidates,
        "all_mentions": mentions,
        "dual_statements": len(dual),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "dual_unclassified": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in dual),
        "relation_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in rows),
        "relation_true_open": sum(
            row.get("qualifiers", {}).get("relation_candidate") is True
            and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
            for row in rows
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted changes")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    if sha(statement_path.read_bytes()) != STATEMENTS_SHA256:
        raise SystemExit("preflight failed: statement table hash changed")
    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source asset hash changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[108:119])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: segment text hash changed")

    rows = read_jsonl(statement_path)
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("preflight failed: statement IDs are not unique")
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    if {row["statement_id"] for row in segment_rows} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: p.108 original statement set changed")
    original_projection = {
        row["statement_id"]: {
            "subject": row.get("subject_candidate_id"),
            "predicate": row.get("predicate"),
            "object": row.get("object_candidate_id"),
            "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
        }
        for row in segment_rows
    }
    if any(row.get("qualifiers", {}).get("relation_candidate") is not None for row in segment_rows):
        raise SystemExit("preflight failed: p.108 statements are no longer all unclassified")
    if NEW_IDS.intersection(by_id):
        raise SystemExit("preflight failed: one or more new statement IDs already exist")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    for row in segment_rows:
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: existing endpoint is missing: {endpoint}")

    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        segment_mentions = [
            row for row in csv.DictReader(handle)
            if row["segment_id"] == SEGMENT_ID
        ]
    mention_errors = [
        row["mention_id"] for row in segment_mentions
        if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
    ]
    if mention_errors:
        raise SystemExit(f"preflight failed: p.108 mention span errors: {mention_errors}")

    for statement_id, note in RELATION_NOTES.items():
        if statement_id in by_id:
            set_classification(by_id[statement_id], True, note)
    for statement_id, note in NONRELATION_NOTES.items():
        if statement_id in by_id:
            set_classification(by_id[statement_id], False, note)

    q = quote_between
    updates = {
        "st-chp4-sec-ii-l109-119-bouchard-papers-continued": {
            "predicate": "papers_reveal_disbelief_under_bouchards_potential_bishop_professions",
            "subject": "cand-5811", "object_": "cand-0419",
            "claim": "Haskell describes Bouchard's private papers as revealing disbelief beneath his professions as a potential bishop.",
            "quote": by_id["st-chp4-sec-ii-l109-119-bouchard-papers-continued"]["original_quote"],
        },
        "st-chp4-sec-ii-l109-119-cassiano-friendly-writing-to-galileo": {
            "predicate": "reports_cassiano_wrote_to_galileo_in_a_friendly_spirit",
            "subject": "cand-2036", "object_": "cand-1105",
            "claim": "Haskell says Cassiano wrote to his former colleague Galileo in a friendly spirit about a year after Galileo's condemnation.",
            "quote": q(segment_text, "We find him writing in the most friendly spirit", "condemnation by the Inquisition"),
            "qualification": "The interval is approximate; the statement records this reported communication and does not by itself establish a sustained correspondence.",
        },
        "st-chp4-sec-ii-l109-119-cassiano-religious-position-qualified": {
            "predicate": "author_assesses_cassianos_libertin_and_orthodox_affiliations_as_unlikely",
            "subject": "cand-2036", "object_": None,
            "claim": "Haskell considers it very unlikely that Cassiano was a libertin and almost equally unlikely that he was a convinced adherent of contemporary orthodox religious views.",
            "quote": by_id["st-chp4-sec-ii-l109-119-cassiano-religious-position-qualified"]["original_quote"],
        },
        "st-chp4-sec-ii-l109-119-cassiano-science-and-new-thought": {
            "predicate": "shows_sympathy_with_unspecified_new_thought_in_conflict_with_papacy",
            "subject": "cand-2036", "object_": "cand-5824",
            "claim": "Haskell says that when Cassiano faced a conflict between the papacy and unspecified new thought, he showed where his sympathies lay.",
            "quote": q(segment_text, "when it came to a conflict between the papacy", "he showed where his sympathies lay."),
            "qualification": "New thought is Haskell's unspecified phrase; the passage does not identify a movement or doctrine.",
        },
        "st-chp4-sec-ii-l109-119-cassiano-shows-papers-to-dupuy": {
            "predicate": "reports_cassiano_showed_bouchard_papers_to_dupuy",
            "subject": "cand-2036", "object_": "cand-0951",
            "claim": "Haskell reports that Cassiano showed Bouchard's papers to Christophe Dupuy in 1641.",
            "quote": q(segment_text, "In 1641 we find Cassiano showing these to Christophe Dupuy", "in Rome"),
        },
        "st-chp4-sec-ii-l109-119-dati-disciple-friend": {
            "predicate": "author_describes_dati_as_cassianos_florentine_disciple",
            "subject": "cand-0905", "object_": "cand-2036",
            "claim": "Haskell describes Carlo Dati as Cassiano's Florentine disciple.",
            "quote": q(segment_text, "Carlo Dati, his Florentine disciple", "disciple"),
        },
        "st-chp4-sec-ii-l109-119-dati-pages-orthodoxy-alchemy": {
            "predicate": "author_judges_datis_treatment_as_over_shrill",
            "subject": "cand-0905", "object_": None,
            "claim": "Haskell judges Dati's repeated treatment of the subject as over-shrill.",
            "quote": q(segment_text, "There is surely something a little over-shrill", "page after page"),
        },
        "st-chp4-sec-ii-l109-119-dati-rhetorical-question": {
            "predicate": "rhetorically_links_science_with_not_hating_atheism_and_praising_god",
            "subject": "cand-0905", "object_": None,
            "claim": "In Haskell's quotation of Dati, the rhetorical question frames Nature and Science as compatible with not hating atheism and proclaiming the Almighty's greatness and goodness.",
            "quote": q(segment_text, "Nature and Science, he asks rhetorically", "goodness of the Almighty?"),
        },
        "st-chp4-sec-ii-l109-119-dupuy-indignation-uncertain": {
            "predicate": "author_inferrs_cassiano_was_hardly_surprised_by_legacy",
            "subject": "cand-2036", "object_": None,
            "claim": "Haskell infers that Cassiano can hardly have been surprised at the nature of his strange legacy.",
            "quote": q(segment_text, "He can hardly have been surprised", "his strange legacy."),
        },
        "st-chp4-sec-ii-l109-119-dupuy-knew-official-bouchard": {
            "predicate": "reports_dupuy_had_known_only_bouchards_official_persona",
            "subject": "cand-0951", "object_": "cand-0419",
            "claim": "Haskell says Dupuy had known only Bouchard's restrained official persona.",
            "quote": q(segment_text, "a man who had known only the", "whose conversation was so restrained"),
        },
        "st-chp4-sec-ii-l109-119-dupuy-letter-to-brother": {
            "predicate": "reports_letter_from_dupuy_addressed_to_his_brother_in_paris",
            "subject": "cand-5821", "object_": "cand-5820",
            "claim": "Haskell says Dupuy wrote incoherently to his brother in Paris about the encounter.",
            "quote": q(segment_text, "Rather incoherently he wrote", "his brother in Paris.2"),
        },
        "st-chp4-sec-ii-l109-119-dupuy-prior-in-rome": {
            "predicate": "reports_dupuy_as_prior_of_carthusian_order_in_rome",
            "subject": "cand-0951", "object_": "cand-5819",
            "claim": "Haskell identifies Christophe Dupuy as prior of the Carthusian Order in Rome.",
            "quote": q(segment_text, "the prior of the Carthusian Order in Rome", "Order in Rome"),
        },
        "st-chp4-sec-ii-l109-119-dupuy-quoted-account": {
            "predicate": "dupuy_describes_the_collection_as_impious_and_obscene",
            "subject": "cand-5822", "object_": None,
            "claim": "In Dupuy's account quoted by Haskell, he describes the collection as impious verses and obscene material and says its contents horrified him.",
            "quote": q(segment_text, "Cavali", "devilish things,"),
            "qualification": "The quotation is mediated by Haskell; the exact relation between this collection and Bouchard's private papers is not established.",
        },
        "st-chp4-sec-ii-l109-119-galileo-condemnation": {
            "predicate": "reports_galileo_condemned_by_inquisition",
            "subject": "cand-1105", "object_": "cand-5826",
            "claim": "Haskell identifies Galileo as having been condemned by the Inquisition before the reported friendly communication with Cassiano.",
            "quote": q(segment_text, "about a year after his condemnation", "condemnation by the Inquisition"),
        },
        "st-chp4-sec-ii-l109-119-galileo-letter-from-arcetri": {
            "predicate": "reports_letter_from_galileo_to_cassiano_sent_from_arcetri",
            "subject": "cand-5827", "object_": "cand-2036",
            "claim": "Haskell reports that Cassiano received a letter from Galileo in 1641, written from the Villa d'Arcetri, which Galileo called his unending prison and exile from town.",
            "quote": q(segment_text, "and in 1641 he received a letter from the scientist", "exile from town"),
        },
        "st-chp4-sec-ii-l109-119-galileo-thanks-for-portrait": {
            "predicate": "reports_galileo_thanked_cassiano_for_including_his_portrait",
            "subject": "cand-1105", "object_": "cand-2036",
            "claim": "Haskell says Galileo thanked Cassiano for including Galileo's portrait among those kept in Cassiano's library.",
            "quote": q(segment_text, "In this Galileo thanked Cassiano", "in his library.3"),
        },
        "st-chp4-sec-ii-l109-119-naude-alternative-response": {
            "predicate": "author_describes_naude_as_cassianos_great_friend",
            "subject": "cand-1726", "object_": "cand-2036",
            "claim": "Haskell describes Gabriel Naudé as Cassiano's great friend.",
            "quote": segment_text[
                segment_text.rfind("Cassiano", 0, segment_text.index("was there to show"))
                :segment_text.index("was there to show")
            ].rstrip(),
        },
        "st-chp4-sec-ii-l109-119-portraits-naude-fragment": {
            "predicate": "portraits_bear_latin_inscriptions_written_by_naude",
            "subject": "cand-5831", "object_": "cand-1726",
            "claim": "Haskell says the unspecified portraits in Cassiano's collection bear suitable Latin inscriptions written by Naudé; the sentence continues onto p.109, where a separate relation with Gaudenzi is introduced.",
            "quote": q(segment_text, "It is through the portraits", ")"),
            "qualification": "The portraits and inscriptions remain unidentified; the p.109 continuation concerns Cassiano's relation with Paganino Gaudenzi, not a relation with Naudé.",
        },
        "st-chp4-sec-ii-l109-119-science-spiritual-danger": {
            "predicate": "author_reports_spiritual_dangers_of_serious_science_recognized_by_contemporaries",
            "subject": "cand-5752", "object_": None,
            "claim": "Haskell says Cassiano's contemporaries recognized spiritual dangers in the serious pursuit of science.",
            "quote": q(segment_text, "The serious pursuit of science", "contemporaries recognised."),
        },
    }

    for statement_id, values in updates.items():
        set_quote_claim(by_id[statement_id], **values)
    by_id["st-chp4-sec-ii-l109-119-dati-rhetorical-question"]["qualifiers"]["speaker"] = (
        "Carlo Dati as quoted by Haskell"
    )
    by_id["st-chp4-sec-ii-l109-119-dupuy-quoted-account"]["qualifiers"]["speaker"] = (
        "Christophe Dupuy as quoted by Haskell"
    )

    new_rows = [
        make_statement(
            "st-chp4-sec-ii-l109-119-cassiano-passionate-student-science",
            subject="cand-2036", object_=None,
            predicate="author_describes_cassiano_as_passionate_student_of_science",
            claim="Haskell describes Cassiano as a passionate student of science.",
            quote=q(segment_text, "He was, after all, a passionate student of science", "science"),
            line_start=113, line_end=113, speaker="Haskell", is_relation=False,
            note=NONRELATION_NOTES["st-chp4-sec-ii-l109-119-cassiano-passionate-student-science"],
            mentioned=["cand-2036", "cand-5752"],
            qualification="This is an authorial characterization of Cassiano's intellectual interest.",
        ),
        make_statement(
            "st-chp4-sec-ii-l109-119-dati-friend-cassiano",
            subject="cand-0905", object_="cand-2036",
            predicate="describes_dati_as_cassianos_florentine_friend",
            claim="Haskell describes Carlo Dati as Cassiano's Florentine friend.",
            quote=q(segment_text, "Carlo Dati, his Florentine disciple and friend", "friend"),
            line_start=116, line_end=116, speaker="Haskell", is_relation=True,
            note=RELATION_NOTES["st-chp4-sec-ii-l109-119-dati-friend-cassiano"],
            mentioned=["cand-0905", "cand-2036"],
            qualification="The specific period and circumstances of the friendship are not supplied here.",
        ),
        make_statement(
            "st-chp4-sec-ii-l109-119-dati-pages-about-cassiano-orthodoxy-alchemy",
            subject="cand-0905", object_="cand-2036",
            predicate="reports_dati_devoted_pages_to_cassianos_orthodoxy_and_detestation_of_alchemy",
            claim="Haskell reports that Dati devoted many pages to the orthodoxy of Cassiano's religious opinions and his detestation of alchemy.",
            quote=q(segment_text, "page after page devoted by Carlo Dati", "detestation of alchemy.4"),
            line_start=116, line_end=116, speaker="Haskell", is_relation=True,
            note=RELATION_NOTES["st-chp4-sec-ii-l109-119-dati-pages-about-cassiano-orthodoxy-alchemy"],
            mentioned=["cand-0905", "cand-2036", "cand-5829", "cand-5657"],
            qualification="Haskell's summary of Dati's writing; the specific Dati work is not identified beyond the cited note.",
            footnote_from=by_id["st-chp4-sec-ii-l109-119-dati-pages-orthodoxy-alchemy"]["qualifiers"],
        ),
        make_statement(
            "st-chp4-sec-ii-l109-119-dati-attributes-praise-of-god-to-cassiano",
            subject="cand-2036", object_=None,
            predicate="quoted_dati_attributes_tireless_praise_of_god_to_cassiano",
            claim="In Haskell's quotation, Dati portrays Cassiano as tirelessly praising and demonstrating the Almighty's greatness and goodness.",
            quote=q(segment_text, "Just as Cavalier Cassiano tirelessly exalted", "strongest arguments"),
            line_start=117, line_end=117, speaker="Carlo Dati as quoted by Haskell", is_relation=False,
            note=NONRELATION_NOTES["st-chp4-sec-ii-l109-119-dati-attributes-praise-of-god-to-cassiano"],
            mentioned=["cand-2036", "cand-0905", "cand-5752", "cand-5830"],
            qualification="This is a nested quotation attributed to Dati by Haskell, not independent confirmation of Cassiano's beliefs.",
        ),
        make_statement(
            "st-chp4-sec-ii-l109-119-dupuy-shared-indignation-unknown",
            subject="cand-2036", object_=None,
            predicate="author_says_whether_cassiano_shared_dupuy_indignation_is_unknown",
            claim="Haskell says the passage does not tell us whether Cassiano shared Dupuy's indignation.",
            quote=q(segment_text, "We are not told whether Cassiano shared", "indignation."),
            line_start=112, line_end=112, speaker="Haskell", is_relation=False,
            note=NONRELATION_NOTES["st-chp4-sec-ii-l109-119-dupuy-shared-indignation-unknown"],
            mentioned=["cand-2036", "cand-0951"],
            qualification="This is an explicit limit on what the passage establishes.",
        ),
        make_statement(
            "st-chp4-sec-ii-l109-119-dupuy-returns-collection-to-cassiano",
            subject="cand-5822", object_="cand-2036",
            predicate="reports_dupuy_returned_collection_to_cassiano",
            claim="In the quotation attributed to Dupuy, he says he returned the collection to Cassiano that same hour.",
            quote=q(segment_text, "that I shut it up to send it back", "as I did that very hour."),
            line_start=112, line_end=112, speaker="Christophe Dupuy as quoted by Haskell", is_relation=True,
            note=RELATION_NOTES["st-chp4-sec-ii-l109-119-dupuy-returns-collection-to-cassiano"],
            mentioned=["cand-0951", "cand-5822", "cand-2036"],
            qualification="This is Dupuy's account as quoted by Haskell; the exact identity of the collection remains unresolved.",
            footnote_from=by_id["st-chp4-sec-ii-l109-119-dupuy-letter-to-brother"]["qualifiers"],
        ),
        make_statement(
            "st-chp4-sec-ii-l109-119-galileo-portrait-kept-in-cassiano-library",
            subject="cand-5828", object_="cand-2036",
            predicate="reports_galileo_portrait_kept_in_cassianos_library",
            claim="Haskell reports that Cassiano kept the unidentified portrait of Galileo in his library.",
            quote=q(segment_text, "In this Galileo thanked Cassiano", "in his library.3"),
            line_start=115, line_end=115, speaker="Haskell", is_relation=True,
            note=RELATION_NOTES["st-chp4-sec-ii-l109-119-galileo-portrait-kept-in-cassiano-library"],
            mentioned=["cand-5828", "cand-1105", "cand-2036"],
            qualification="The portrait is not individually identified; this report does not establish its survival or present location.",
            footnote_from=by_id["st-chp4-sec-ii-l109-119-galileo-thanks-for-portrait"]["qualifiers"],
        ),
        make_statement(
            "st-chp4-sec-ii-l109-119-naude-alternative-response-to-science",
            subject="cand-1726", object_=None,
            predicate="author_presents_naude_as_showing_science_had_an_alternative_religious_response",
            claim="Haskell presents Naudé as showing that religious affirmation was not the only response to scientific discoveries.",
            quote=q(segment_text, "Certainly this was a possible", "not the only one."),
            line_start=117, line_end=118, speaker="Haskell", is_relation=False,
            note=NONRELATION_NOTES["st-chp4-sec-ii-l109-119-naude-alternative-response-to-science"],
            mentioned=["cand-1726", "cand-2036", "cand-5752"],
            qualification="Haskell's comparison does not identify Naudé's alternative position in this passage.",
        ),
    ]

    for row in new_rows:
        if row["statement_id"] not in NEW_IDS:
            raise SystemExit(f"preflight failed: unexpected new statement ID {row['statement_id']}")
        if not row["original_quote"] or row["original_quote"] not in segment_text:
            raise SystemExit(f"preflight failed: new quote is not an exact source substring: {row['statement_id']}")
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: new endpoint is missing: {row['statement_id']} -> {endpoint}")
        q = row["qualifiers"]
        if not (109 <= q["source_line_start"] <= q["source_line_end"] <= 119):
            raise SystemExit(f"preflight failed: new line anchor is outside p.108: {row['statement_id']}")
        by_id[row["statement_id"]] = row
    if {row["statement_id"] for row in new_rows} != NEW_IDS:
        raise SystemExit("preflight failed: new statement set differs from declared IDs")

    after_segment = [row for row in by_id.values() if row.get("segment_id") == SEGMENT_ID]
    expected_segment = {
        "statements": 27, "dual": 17, "relation_true": 17, "relation_false": 10,
        "dual_true": 17, "dual_false": 0, "unclassified": 0,
    }
    if counts(after_segment) != expected_segment:
        raise SystemExit(f"preflight failed: unexpected p.108 result: {counts(after_segment)}")

    after_totals = totals(list(by_id.values()), len(candidate_ids), 27564)
    expected_totals = {
        "all_statements": 12995,
        "all_candidates": 11626,
        "all_mentions": 27564,
        "dual_statements": 8798,
        "dual_true": 5652,
        "dual_false": 515,
        "dual_unclassified": 2631,
        "relation_true": 5713,
        "relation_true_open": 61,
    }
    if after_totals != expected_totals:
        raise SystemExit(f"preflight failed: unexpected projected global totals: {after_totals}")

    changed_ids = set(updates) | NEW_IDS
    for statement_id in changed_ids:
        if statement_id in by_id:
            q = by_id[statement_id].get("qualifiers", {})
            if q.get("relation_candidate") not in (True, False):
                raise SystemExit(f"preflight failed: relation classification missing: {statement_id}")

    review_changes = []
    for statement_id in sorted(ORIGINAL_IDS):
        row = by_id[statement_id]
        review_changes.append({
            "statement_id": statement_id,
            "before": original_projection[statement_id],
            "after": {
                "subject": row.get("subject_candidate_id"),
                "predicate": row.get("predicate"),
                "object": row.get("object_candidate_id"),
                "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
            },
        })
    new_statement_summary = [
        {
            "statement_id": row["statement_id"],
            "subject": row.get("subject_candidate_id"),
            "predicate": row.get("predicate"),
            "object": row.get("object_candidate_id"),
            "relation_candidate": row["qualifiers"]["relation_candidate"],
            "source_lines": [
                row["qualifiers"]["source_line_start"],
                row["qualifiers"]["source_line_end"],
            ],
        }
        for row in new_rows
    ]

    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "statements_sha256_before": STATEMENTS_SHA256,
        "original_statements_reviewed": len(ORIGINAL_IDS),
        "existing_statement_changes": review_changes,
        "new_statement_summary": new_statement_summary,
        "new_statements": sorted(NEW_IDS),
        "segment_after": expected_segment,
        "global_after": expected_totals,
        "candidate_and_mention_rows_changed": 0,
        "backup": f"book-statements.jsonl.{BACKUP_SUFFIX}",
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup_path = statement_path.with_name(statement_path.name + "." + BACKUP_SUFFIX)
    if backup_path.exists():
        if sha(backup_path.read_bytes()) != STATEMENTS_SHA256:
            raise SystemExit(f"apply refused: existing recovery backup has unexpected content: {backup_path.name}")
    else:
        shutil.copy2(statement_path, backup_path)

    serialized_updates = {
        statement_id: json.dumps(by_id[statement_id], ensure_ascii=False) + "\n"
        for statement_id in updates
    }
    raw_lines = statement_path.read_text(encoding="utf-8").splitlines(keepends=True)
    output_lines = []
    for raw_line in raw_lines:
        if not raw_line.strip():
            output_lines.append(raw_line)
            continue
        statement_id = json.loads(raw_line)["statement_id"]
        output_lines.append(serialized_updates.get(statement_id, raw_line))
    if output_lines and not output_lines[-1].endswith(("\n", "\r")):
        output_lines[-1] += "\n"
    output_lines.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in new_rows)
    statement_path.write_bytes("".join(output_lines).encode("utf-8"))

    written = read_jsonl(statement_path)
    written_segment = [row for row in written if row.get("segment_id") == SEGMENT_ID]
    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        written_mention_count = sum(1 for _ in csv.DictReader(handle))
    written_totals = totals(
        written,
        len(candidate_ids),
        written_mention_count,
    )
    if counts(written_segment) != expected_segment or written_totals != expected_totals:
        shutil.copy2(backup_path, statement_path)
        raise SystemExit(
            "postwrite verification failed; restored statement table from backup: "
            f"segment={counts(written_segment)}, totals={written_totals}"
        )
    if sha(statement_path.read_bytes()) == STATEMENTS_SHA256:
        shutil.copy2(backup_path, statement_path)
        raise SystemExit("postwrite verification failed: statement table did not change; backup restored")
    print(json.dumps({
        "apply": "written",
        "backup": backup_path.name,
        "statements_sha256_after": sha(statement_path.read_bytes()),
        "segment_after": counts(written_segment),
        "global_after": written_totals,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
