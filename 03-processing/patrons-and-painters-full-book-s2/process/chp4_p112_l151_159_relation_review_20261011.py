#!/usr/bin/env python3
"""Classify and atomize the p.112 S2 statements against the printed page."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l151-159"
NEXT_SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l161-170"
NEXT_STATEMENT_ID = "st-chp4-sec-ii-p113-cassiano-health"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "e44be04bf22b6a5737298cfa390c99d36ddecd369a1b775d2ad9aba17e8f0c51"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "51d19e1c2f5d641879e64d363f28abe3fb1eec753a6640d5bd2b3107fed20fcd",
    "entity-candidates.csv": "01eaae9a76cc32c5a12e78820594517a3382bbea6ac9447c121cd57bd141b1a2",
    "mentions.csv": "e8ce04ae40d08cef4fc2e5c094aebf8be01510c917e7d23b74b20c3e2e6a3516",
}
STATEMENT_BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l151-159-relations-20261011"
MENTION_BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l151-159-italy-mention-20261011"
FOOTNOTE_FIELDS = (
    "footnote_marker",
    "footnote_segment",
    "footnote_source_line",
    "footnote_link_status",
    "footnote_statement_id",
)
ORIGINAL_IDS = {
    "st-chp4-sec-ii-p112-attack-on-baroque",
    "st-chp4-sec-ii-p112-autopsy-gallstones",
    "st-chp4-sec-ii-p112-cardinal-flight-return",
    "st-chp4-sec-ii-p112-cassiano-illness-account",
    "st-chp4-sec-ii-p112-cassiano-owned-pictures-and-summary",
    "st-chp4-sec-ii-p112-cassiano-patron-reputation",
    "st-chp4-sec-ii-p112-cassiano-position-change",
    "st-chp4-sec-ii-p112-cloudless-plan",
    "st-chp4-sec-ii-p112-clouds-disturb-serenity",
    "st-chp4-sec-ii-p112-de-noyers-assessment",
    "st-chp4-sec-ii-p112-engraving-success-bitter",
    "st-chp4-sec-ii-p112-engraving-themes",
    "st-chp4-sec-ii-p112-fabio-chigi-election",
    "st-chp4-sec-ii-p112-hard-classical-figures",
    "st-chp4-sec-ii-p112-innocent-hostility",
    "st-chp4-sec-ii-p112-painting-nobility-doctrine",
    "st-chp4-sec-ii-p112-planned-apse-scheme",
    "st-chp4-sec-ii-p112-small-heart-interpretation",
    "st-chp4-sec-ii-p112-suicide-date",
    "st-chp4-sec-ii-p112-testa-suicide",
    "st-chp4-sec-ii-p112-treatise",
    "st-chp4-sec-ii-p112-turn-to-engraving",
    "st-chp4-sec-ii-p112-urban-death",
    "st-chp4-sec-ii-p112-withdrawal-from-ceremonies",
}
NEW_IDS = {
    "st-chp4-sec-ii-p112-largest-gallstone-size",
    "st-chp4-sec-ii-p112-cardinal-flight-income-ended",
    "st-chp4-sec-ii-p112-cardinal-return-reinstatement",
    "st-chp4-sec-ii-p112-cassiano-regrets-urban",
    "st-chp4-sec-ii-p112-barberini-family-helped-career",
    "st-chp4-sec-ii-p112-cassiano-appraisal-of-testa",
    "st-chp4-sec-ii-p112-cassiano-reputation-beyond-italy",
    "st-chp4-sec-ii-p112-denoyers-assessment-of-cassiano",
    "st-chp4-sec-ii-p112-engraving-success-bitter-assessment",
    "st-chp4-sec-ii-p112-cassiano-fabio-chigi-friendship",
    "st-chp4-sec-ii-p112-paintings-popularity-declined",
    "st-chp4-sec-ii-p112-innocent-hostile-to-cassiano-pursuits",
    "st-chp4-sec-ii-p112-cassiano-acknowledges-innocent-hostility",
    "st-chp4-sec-ii-p112-apse-scheme-location",
    "st-chp4-sec-ii-p112-apse-scheme-departs-correggio-custom",
    "st-chp4-sec-ii-p112-scientists-interpret-small-heart",
    "st-chp4-sec-ii-p112-tiber-suicide-location",
    "st-chp4-sec-ii-p112-treatise-content",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def segment_counts(rows: list[dict]) -> dict[str, int]:
    segment = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    dual = [row for row in segment if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    relation = [row for row in segment if row.get("qualifiers", {}).get("relation_candidate") is True]
    return {
        "statements": len(segment),
        "dual": len(dual),
        "relation_true": len(relation),
        "relation_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in segment),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "open_relation": sum(
            row.get("qualifiers", {}).get("relation_candidate") is True
            and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
            for row in segment
        ),
        "unclassified": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in segment),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted p.112 changes")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    paths = {path.name: path for path in (statement_path, candidate_path, mention_path)}
    for name, path in paths.items():
        if sha(path.read_bytes()) != EXPECTED_SHA256[name]:
            raise SystemExit(f"preflight failed: {name} changed since the reviewed p.111 state")
    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source asset changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[150:159])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.112 segment text changed")

    def quote(text: str) -> str:
        if text not in segment_text:
            raise ValueError(f"quote is not an exact S0 substring: {text!r}")
        return text

    rows = read_jsonl(statement_path)
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("preflight failed: statement IDs are not unique")
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    if {row["statement_id"] for row in segment_rows} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: the p.112 statement set changed")

    candidates = list(csv.DictReader(candidate_path.open(encoding="utf-8-sig", newline="")))
    candidate_ids = {row["candidate_id"] for row in candidates}
    mentions = list(csv.DictReader(mention_path.open(encoding="utf-8-sig", newline="")))
    segment_mentions = [row for row in mentions if row["segment_id"] == SEGMENT_ID]
    if len(segment_mentions) != 28:
        raise SystemExit(f"preflight failed: expected 28 p.112 mentions, found {len(segment_mentions)}")
    bad_spans = [
        row["mention_id"]
        for row in segment_mentions
        if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
    ]
    if bad_spans:
        raise SystemExit(f"preflight failed: mention spans differ from p.112 source: {bad_spans}")
    italy = [row for row in candidates if row["candidate_id"] == "cand-3461"]
    if len(italy) != 1 or italy[0]["canonical_name"] != "Italy":
        raise SystemExit("preflight failed: the existing Italy candidate is not unique")
    italy_start = segment_text.index("Italy")
    new_mention = {
        "mention_id": "m-chp4-sec-ii-p112-0029",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-3461",
        "surface_form": "Italy",
        "start_char": str(italy_start),
        "end_char": str(italy_start + len("Italy")),
        "note": "Named geographic boundary of Haskell's reputation claim.",
    }
    if any(row["mention_id"] == new_mention["mention_id"] for row in mentions):
        raise SystemExit("preflight failed: the planned Italy mention ID already exists")

    footnote_sources = {
        "fn1": "st-chp4-sec-ii-p112-clouds-disturb-serenity",
        "fn2": "st-chp4-sec-ii-p112-engraving-themes",
        "fn3": "st-chp4-sec-ii-p112-cassiano-owned-pictures-and-summary",
        "fn4": "st-chp4-sec-ii-p112-de-noyers-assessment",
        "fn5": "st-chp4-sec-ii-p112-cassiano-illness-account",
        "fn6": "st-chp4-sec-ii-p112-cardinal-flight-return",
        "fn7": "st-chp4-sec-ii-p112-innocent-hostility",
    }

    def footnote_meta(source_id: str | None) -> dict:
        if not source_id:
            return {}
        source_q = by_id[source_id]["qualifiers"]
        return {key: source_q[key] for key in FOOTNOTE_FIELDS if key in source_q}

    def patch_existing(
        statement_id: str,
        *,
        subject: str | None,
        object_: str | None,
        predicate: str,
        claim: str,
        original_quote: str,
        lines: tuple[int, int],
        relation: bool,
        relation_note: str,
        mentioned: list[str],
        speaker: str = "Haskell",
        text_layer: str = "authorial narrative",
        qualification: str,
        remove_footnote: bool = False,
        copy_footnote_from: str | None = None,
        ocr_corrections: list[dict] | None = None,
        related_statement_ids: list[str] | None = None,
        open_endpoint_reason: str | None = None,
    ) -> dict:
        row = by_id[statement_id]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_
        row["predicate"] = predicate
        row["original_quote"] = quote(original_quote)
        q = row["qualifiers"]
        q.update({
            "source_line_start": lines[0],
            "source_line_end": lines[1],
            "pdf_physical_page": 23,
            "printed_page_locator": "p.112",
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "mentioned_candidate_ids": mentioned,
            "qualification": qualification,
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
        })
        if remove_footnote:
            for key in FOOTNOTE_FIELDS:
                q.pop(key, None)
        if copy_footnote_from:
            q.update(footnote_meta(copy_footnote_from))
        if ocr_corrections is not None:
            q["ocr_corrections"] = ocr_corrections
        if related_statement_ids is not None:
            q["related_statement_ids"] = related_statement_ids
        if open_endpoint_reason:
            q["open_endpoint_reason"] = open_endpoint_reason
        else:
            q.pop("open_endpoint_reason", None)
        return row

    def new_statement(
        statement_id: str,
        *,
        subject: str | None,
        object_: str | None,
        predicate: str,
        claim: str,
        original_quote: str,
        lines: tuple[int, int],
        relation: bool,
        relation_note: str,
        mentioned: list[str],
        speaker: str = "Haskell",
        text_layer: str = "authorial narrative",
        qualification: str,
        copy_footnote_from: str | None = None,
        ocr_corrections: list[dict] | None = None,
        related_statement_ids: list[str] | None = None,
        open_endpoint_reason: str | None = None,
    ) -> dict:
        if statement_id in by_id or statement_id not in NEW_IDS:
            raise SystemExit(f"preflight failed: duplicate new statement ID {statement_id}")
        q = {
            "source_line_start": lines[0],
            "source_line_end": lines[1],
            "pdf_physical_page": 23,
            "printed_page_locator": "p.112",
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "mentioned_candidate_ids": mentioned,
            "qualification": qualification,
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
        }
        q.update(footnote_meta(copy_footnote_from))
        if ocr_corrections:
            q["ocr_corrections"] = ocr_corrections
        if related_statement_ids:
            q["related_statement_ids"] = related_statement_ids
        if open_endpoint_reason:
            q["open_endpoint_reason"] = open_endpoint_reason
        row = {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": object_,
            "predicate": predicate,
            "qualifiers": q,
            "original_quote": quote(original_quote),
            "origin": "book",
            "source_file": SOURCE_REL,
        }
        by_id[statement_id] = row
        return row

    p112_rows: list[dict] = []
    # Haskell's interpretation refers to Testa's cloudless scheme, not to Testa's person in general.
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-attack-on-baroque", subject="cand-5910", object_="cand-4500",
        predicate="scheme_interpreted_as_attack_on_baroque_tradition",
        claim="Haskell interprets Testa's objection to clouds in the planned apse scheme as a direct attack on the Baroque tradition.",
        original_quote="This was a direct attack on the whole Baroque tradition.", lines=(154, 154), relation=True,
        relation_note="The demonstrative refers to Testa's cloudless scheme. This is Haskell's interpretive link between the proposed work and the Baroque tradition, not a claim that Testa used that category.",
        mentioned=["cand-2557", "cand-5910", "cand-4500"],
        qualification="Haskell's interpretation of the reported position; it does not establish that the scheme was executed.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-autopsy-gallstones", subject="cand-0209", object_=None,
        predicate="quoted_account_reports_six_gallstones_found_after_death",
        claim="The account quoted by Haskell says an examination two hours after Urban VIII's death found six gallstones.",
        original_quote="When the corpse was opened just two hours after the poor man’s death they found six stones in his gall bladder,",
        lines=(157, 157), relation=False,
        relation_note="This is a reported medical observation about Urban VIII, not a relation between two knowledge entities.",
        mentioned=["cand-0209"], speaker="Cassiano's account as quoted by Haskell", text_layer="nested quotation",
        qualification="Quoted report, not independently verified medical evidence; the stone-size detail is recorded separately.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-largest-gallstone-size", subject="cand-0209", object_=None,
        predicate="quoted_account_describes_largest_gallstone_as_cashew_sized",
        claim="The quoted account says the largest of Urban VIII's gallstones was the size of a cashew nut.",
        original_quote="the largest of them the size of a cashew nut", lines=(157, 157), relation=False,
        relation_note="This is a scalar detail of the quoted medical report, not a relation between entities.",
        mentioned=["cand-0209"], speaker="Cassiano's account as quoted by Haskell", text_layer="nested quotation",
        qualification="The comparison and medical claim are preserved as Haskell's quotation, not independently verified.",
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-cardinal-flight-return", subject="cand-2036", object_="cand-5916",
        predicate="official_post_ended_during_unidentified_cardinals_flight",
        claim="Haskell says Cassiano's official post ended with the flight of the unidentified Cardinal Barberini.",
        original_quote="With the flight of Cardinal Barberini his own official post, and part of his income, came to an end",
        lines=(157, 157), relation=True,
        relation_note="This records the source-attributed end of Cassiano's post during the cardinal's flight. The cardinal remains unidentified and the statement does not infer the exact date.",
        mentioned=["cand-2036", "cand-5915", "cand-5916"],
        qualification="Haskell's account; the Cardinal's identity and exact chronology remain unresolved.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-cardinal-flight-income-ended", subject="cand-2036", object_="cand-5916",
        predicate="part_of_cassianos_income_ended_during_cardinals_flight",
        claim="Haskell says part of Cassiano's income ended with the unidentified Cardinal Barberini's flight.",
        original_quote="With the flight of Cardinal Barberini his own official post, and part of his income, came to an end",
        lines=(157, 157), relation=True,
        relation_note="This separates the income consequence from the end of the official post; it uses the same source-described flight event without identifying the cardinal.",
        mentioned=["cand-2036", "cand-5915", "cand-5916"],
        qualification="Haskell's account; the Cardinal's identity and exact chronology remain unresolved.",
        copy_footnote_from=footnote_sources["fn6"],
        related_statement_ids=["st-chp4-sec-ii-p112-cardinal-flight-return"],
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-cardinal-return-reinstatement", subject="cand-2036", object_="cand-5916",
        predicate="reinstated_when_unidentified_cardinal_returned_to_rome",
        claim="Haskell says Cassiano was reinstated when the Cardinal Barberini returned to Rome.",
        original_quote="on the Cardinal’s return to Rome he was reinstated",
        lines=(157, 157), relation=True,
        relation_note="This records the reported reinstatement on the cardinal's return; the identity of the cardinal and chronology remain unresolved.",
        mentioned=["cand-2036", "cand-5915", "cand-5916", "cand-4490"],
        qualification="Haskell's account; the Cardinal's identity and exact chronology remain unresolved.",
        copy_footnote_from=footnote_sources["fn6"],
        related_statement_ids=["st-chp4-sec-ii-p112-cardinal-flight-return"],
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-cassiano-illness-account", subject="cand-2036", object_="cand-0209",
        predicate="recorded_urban_viiis_last_illness_with_scientific_precision",
        claim="Haskell says Cassiano recorded Urban VIII's last illness with scientific precision.",
        original_quote="Cassiano recorded his last illness with a mixture of true scientific precision",
        lines=(156, 156), relation=True,
        relation_note="The source explicitly links Cassiano's record to Urban VIII's last illness; the evaluation of scientific precision remains Haskell's wording.",
        mentioned=["cand-2036", "cand-0209"],
        qualification="Haskell's characterization; the cited Lumbroso passage has not been independently consulted.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-cassiano-regrets-urban", subject="cand-2036", object_="cand-0209",
        predicate="regretted_the_loss_of_urban_viii_as_barberini_family_head",
        claim="Haskell says Cassiano felt deep regret for Urban VIII as head of the family that had helped his career.",
        original_quote="deep regret for the head of a family",
        lines=(156, 156), relation=True,
        relation_note="The head of the family is Urban VIII in the preceding clause. The emotional response is attributed to Cassiano by Haskell, not treated as independently verified testimony.",
        mentioned=["cand-2036", "cand-0209", "cand-0198"],
        qualification="Haskell's characterization of Cassiano's response; no stronger personal tie is inferred.",
        copy_footnote_from=footnote_sources["fn5"],
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-barberini-family-helped-career", subject="cand-0198", object_="cand-2036",
        predicate="barberini_family_helped_cassianos_career",
        claim="Haskell says the Barberini family had helped Cassiano's career.",
        original_quote="a family which had so helped his career",
        lines=(156, 156), relation=True,
        relation_note="The phrase refers to the Barberini family named immediately before the illness account; direction is family to Cassiano.",
        mentioned=["cand-0198", "cand-2036", "cand-0209"],
        qualification="Haskell's summary, not an independently verified account of specific assistance.",
        copy_footnote_from=footnote_sources["fn5"],
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-cassiano-owned-pictures-and-summary", subject="cand-2036", object_="cand-5913",
        predicate="owned_unspecified_testa_pictures",
        claim="Haskell says Cassiano owned a number of Testa's pictures.",
        original_quote="Cassiano, who owned a number of pictures by him",
        lines=(154, 154), relation=True,
        relation_note="This records Cassiano's reported ownership of an unspecified group of Testa pictures; individual works are not identified.",
        mentioned=["cand-2036", "cand-2557", "cand-5913"],
        qualification="The pictures are unspecified; Haskell's cited Lumbroso text has not been independently consulted.",
        remove_footnote=True,
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-cassiano-appraisal-of-testa", subject="cand-2036", object_="cand-2557",
        predicate="described_testa_as_good_painter_and_antique_draughtsman",
        claim="Cassiano called Testa a good painter and an excellent draughtsman of the antique.",
        original_quote="He was a good painter and an excellent draughtsman of the antique.",
        lines=(154, 154), relation=True,
        relation_note="This is Cassiano's attributed appraisal of Testa, transmitted through Haskell; it is not an independent assessment by Haskell.",
        mentioned=["cand-2036", "cand-2557"], speaker="Cassiano as quoted by Haskell",
        text_layer="nested quotation",
        qualification="The appraisal is attributed to Cassiano through Haskell; the cited Lumbroso passage has not been independently consulted.",
        copy_footnote_from=footnote_sources["fn3"],
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-cassiano-patron-reputation", subject="cand-2036", object_="cand-4490",
        predicate="acknowledged_as_major_private_art_patron_in_rome_under_barberini",
        claim="Haskell says Cassiano was acknowledged under the Barberini as Rome's most important private art patron.",
        original_quote="Under the regime of the Barberini he had been acknowledged as the most important private art patron in Rome",
        lines=(155, 155), relation=False,
        relation_note="This is a source-attributed status and ranking; Rome and the Barberini regime give its scope, not a patronage target or a personal relation.",
        mentioned=["cand-2036", "cand-0198", "cand-4490"],
        qualification="A reported contemporary ranking, not an independently measured comparison.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-cassiano-reputation-beyond-italy", subject="cand-2036", object_=None,
        predicate="reputation_extended_beyond_italy",
        claim="Haskell says Cassiano's reputation travelled far beyond Italy.",
        original_quote="his reputation had travelled far beyond the frontiers of Italy",
        lines=(155, 155), relation=False,
        relation_note="This is a scalar claim about Cassiano's reputation; Italy is its geographic boundary, not a person-to-place relation.",
        mentioned=["cand-2036", "cand-3461"],
        qualification="Haskell's report of reputation, not a quantified measure of its geographic reach.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-cassiano-position-change", subject="cand-2036", object_=None,
        predicate="position_had_changed_by_testa_suicide_in_1650",
        claim="Haskell says Cassiano's position had greatly changed by the time of Testa's suicide in 1650.",
        original_quote="By this date Cassiano’s own position had greatly changed.",
        lines=(155, 155), relation=False,
        relation_note="This is a scalar status change with no specified dimensions; the text does not define a relation to another entity.",
        mentioned=["cand-2036", "cand-2557", "cand-5914"],
        qualification="The dimensions of the change are not specified in this sentence.",
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-cloudless-plan", subject="cand-2557", object_="cand-5910",
        predicate="wished_proposed_apse_scheme_to_be_shown_without_clouds",
        claim="Haskell reports that Testa wished his proposed apse scheme to be shown without clouds.",
        original_quote="He wished\n. to show it without clouds",
        lines=(152, 153), relation=True,
        relation_note="This is Testa's reported intention for the proposed scheme; it does not establish that the decoration was executed.",
        mentioned=["cand-2557", "cand-5910"],
        speaker="Testa as reported by Haskell",
        qualification="The leading period on L153 is an OCR artifact; the printed sentence continues across the line break. The project is only planned.",
        ocr_corrections=[{"source_line": 153, "source_form": ". to show it", "print_form": "to show it"}],
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-clouds-disturb-serenity", subject="cand-2557", object_="cand-5918",
        predicate="objected_to_clouds_around_trinity_and_home_of_blessed",
        claim="In Haskell's quotation, Testa says clouds would make the Throne of Light of the Trinity and the Home of the Blessed turbulent and dark.",
        original_quote="for he said that it was a very serious mistake to surround the\nThrone of Light of the Trinity and the Home of the Blessed with clouds. For such places were havens of peace and everlasting serenity, and clouds only made them turbulent and dark.",
        lines=(153, 154), relation=True,
        relation_note="This is Testa's reported objection to clouds in the proposed scheme. The endpoint candidate records the Trinity subject; the Home of the Blessed remains part of the quoted rationale and is not collapsed into a separate identified entity.",
        mentioned=["cand-2557", "cand-5918", "cand-5910"], speaker="Testa as quoted by Haskell",
        text_layer="nested quotation",
        qualification="Attributed to Testa by Haskell; 'Home of the Blessed' is not independently identified as a work or place.",
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-de-noyers-assessment", subject="cand-1764", object_="cand-5317",
        predicate="identified_as_surintendant_des_batiments_for_king_of_france",
        claim="Haskell identifies François Sublet de Noyers as Surintendant des Bâtiments of the King of France.",
        original_quote="M. de Noyers, Surintendant des Bâtiments of the\nKing of France",
        lines=(155, 156), relation=False,
        relation_note="This is an office description of de Noyers; France supplies the jurisdictional context, while the office itself is not represented by a separate candidate.",
        mentioned=["cand-1764", "cand-5317", "cand-2036"],
        qualification="Haskell's identification; the passage does not name the king or identify a particular appointment record.",
        remove_footnote=True,
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-denoyers-assessment-of-cassiano", subject="cand-1764", object_="cand-2036",
        predicate="described_cassiano_as_held_in_singular_esteem",
        claim="François Sublet de Noyers wrote that Cassiano was held in singular esteem and stood in place of the head of the virtuous.",
        original_quote="icy en un’estime singulière et tient lieu du chef des vertueux",
        lines=(156, 156), relation=True,
        relation_note="The text explicitly attributes this French assessment to de Noyers. This records an attributed description of Cassiano, not a claim that de Noyers was his friend or that the public's scope is fully known.",
        mentioned=["cand-1764", "cand-2036"], speaker="François Sublet de Noyers as quoted by Haskell",
        text_layer="nested quotation in French",
        qualification="The quoted assessment is not independently consulted; preserve it as Haskell's attributed report.",
        copy_footnote_from=footnote_sources["fn4"],
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-engraving-success-bitter", subject="cand-2557", object_="cand-5912",
        predicate="found_success_as_engraver_with_unidentified_print_group",
        claim="Haskell says Testa finally found success as an engraver.",
        original_quote="Here, at last, he met with the success he deserved",
        lines=(154, 154), relation=True,
        relation_note="The surrounding passage identifies the success with Testa's engraving practice and the described print group; no individual print is identified.",
        mentioned=["cand-2557", "cand-5912"],
        qualification="Haskell's biographical assessment; individual engravings remain unidentified.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-engraving-success-bitter-assessment", subject="cand-2557", object_=None,
        predicate="experienced_engraving_success_as_bitter_due_to_painting_failure",
        claim="Haskell says Testa experienced his engraving success as bitter because it emphasized his failure as a large-scale painter.",
        original_quote="but even that was bitter, for it only emphasised his failure as a large-scale painter.",
        lines=(154, 154), relation=False,
        relation_note="This is Haskell's characterization of Testa's reaction and career; it does not identify a separate painting or another relation endpoint.",
        mentioned=["cand-2557", "cand-5912"],
        qualification="Haskell's interpretation of Testa's response, not a first-person statement by Testa.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-engraving-themes", subject="cand-2557", object_="cand-5912",
        predicate="used_antiquarian_trappings_for_virtue_and_vice_engravings",
        claim="Haskell says Testa used antiquarian material from his drawing expeditions to depict the oppression of Virtue, the triumph of Vice, and the miseries of the virtuous in engravings.",
        original_quote="Full of self-pity, he used all those trappings of antiquity which he had picked up on his drawing expeditions to portray ‘the oppression of Virtue, the triumph of Vice, the misfortunes, the discomforts and the miseries of the Virtuous’.",
        lines=(154, 154), relation=True,
        relation_note="This links Testa to the source-described group of engravings and their themes; it does not identify individual prints or equate the drawing expeditions with a specific drawing group.",
        mentioned=["cand-2557", "cand-5912", "cand-5884"],
        qualification="Haskell's account and wording; the prints and their full set remain unidentified.",
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-fabio-chigi-election", subject="cand-0665", object_=None,
        predicate="elected_pope_alexander_vii_in_1655",
        claim="Haskell states that Fabio Chigi was elected Pope Alexander VII in 1655.",
        original_quote="In 1655 his friend Fabio Chigi was elected Pope Alexander VII",
        lines=(159, 159), relation=False,
        relation_note="Fabio Chigi and Pope Alexander VII are the same candidate, so this is an election/status claim rather than a relation between two entities.",
        mentioned=["cand-0665", "cand-2036"],
        qualification="The source sentence continues across the page break; the cross-page link points to Cassiano's health statement.",
        related_statement_ids=[NEXT_STATEMENT_ID],
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-cassiano-fabio-chigi-friendship", subject="cand-2036", object_="cand-0665",
        predicate="was_friend_of_fabio_chigi",
        claim="Haskell calls Fabio Chigi Cassiano's friend.",
        original_quote="his friend Fabio Chigi",
        lines=(159, 159), relation=True,
        relation_note="The possessive directly identifies a friendship between Cassiano and Fabio Chigi; the friendship is not inferred from the later election.",
        mentioned=["cand-2036", "cand-0665"],
        qualification="Haskell's account; the name Fabio Chigi and papal name Alexander VII map to one candidate.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-hard-classical-figures", subject="cand-5913", object_="cand-5888",
        predicate="figures_in_testa_pictures_became_harder_and_more_classical",
        claim="Haskell says figures in Testa's pictures became increasingly hard and classical.",
        original_quote="the figures in his pictures became more and more hard and ‘classical’",
        lines=(154, 154), relation=True,
        relation_note="This is a source-level style association between Testa's picture group and Haskell's classicism term; it does not identify individual works or assign a definitive period label.",
        mentioned=["cand-2557", "cand-5913", "cand-5888"],
        qualification="Haskell's evaluative style description; 'classical' remains in quotation marks in the source.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-paintings-popularity-declined", subject="cand-5913", object_=None,
        predicate="testa_pictures_became_increasingly_unpopular",
        claim="Haskell says Testa's pictures became increasingly unpopular.",
        original_quote="and at the same time increasingly unpopular.",
        lines=(154, 154), relation=False,
        relation_note="This is a reception claim about the pictures, with no named audience or separate relation endpoint.",
        mentioned=["cand-2557", "cand-5913"],
        qualification="Haskell's generalized assessment; no specific audience or date is supplied.",
    ))

    open_associates = "The source names only a general group of associates of the Barberini; its members are not identified or bounded. The Barberini family candidate is contextual and is not substituted as the associates endpoint."
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-innocent-hostility", subject="cand-1819", object_=None,
        predicate="hostile_to_unidentified_associates_of_barberini",
        claim="Haskell says Innocent X was hostile to associates of the Barberini.",
        original_quote="Pope Innocent X was hostile both to associates of the Barberini",
        lines=(158, 158), relation=True,
        relation_note="The relation is kept open because the source gives no identified or bounded set of associates.",
        mentioned=["cand-1819", "cand-0198"],
        qualification="Haskell reports the hostility as acknowledged by Cassiano in a bitter comment; the affected associates are not specified.",
        copy_footnote_from=footnote_sources["fn7"],
        open_endpoint_reason=open_associates,
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-innocent-hostile-to-cassiano-pursuits", subject="cand-1819", object_=None,
        predicate="hostile_to_unidentified_pursuits_appealing_to_cassiano",
        claim="Haskell says Innocent X was hostile to pursuits that appealed to Cassiano.",
        original_quote="and to the pursuits which appealed to Cassiano",
        lines=(158, 158), relation=True,
        relation_note="The relation is kept open: no specific pursuit, work, or bounded practice is identified, and the source does not say Innocent X was personally hostile to Cassiano.",
        mentioned=["cand-1819", "cand-2036"],
        qualification="Haskell attributes this account to Cassiano's bitter comment; the pursuits themselves remain unidentified.",
        copy_footnote_from=footnote_sources["fn7"],
        open_endpoint_reason="The source refers only to unidentified pursuits appealing to Cassiano; no specific activity or bounded group can be resolved from this passage.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-cassiano-acknowledges-innocent-hostility", subject="cand-2036", object_="cand-1819",
        predicate="acknowledged_innocent_x_hostility_in_bitter_comment",
        claim="Haskell says Cassiano acknowledged Innocent X's hostility in a bitter comment.",
        original_quote="as the latter acknowledged in a bitter comment",
        lines=(158, 158), relation=True,
        relation_note="This records the explicit attribution of the comment to Cassiano and its subject to Innocent X; it does not identify the comment's full wording or a separate document.",
        mentioned=["cand-2036", "cand-1819"], speaker="Haskell reporting Cassiano",
        text_layer="reported comment",
        qualification="The comment is not quoted verbatim in this passage; footnote 7 cites Lumbroso p.202 and has not been independently consulted.",
        copy_footnote_from=footnote_sources["fn7"],
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-painting-nobility-doctrine", subject="cand-5911", object_=None,
        predicate="treatise_quotes_hierarchical_doctrine_of_arts_and_painting",
        claim="The doctrine quoted from Testa's treatise says arts nearest mathematics are noblest because they rest on true reason, and identifies painting as such an art.",
        original_quote="that those arts which are nearest mathematics are the noblest because they arc based on true reason. Of such is painting.",
        lines=(152, 152), relation=False,
        relation_note="This records doctrine described as content of the treatise; it does not attribute the doctrine as Testa's settled belief or create a relation to an unmodeled abstract class.",
        mentioned=["cand-5911"], speaker="Doctrine quoted by Haskell from the treatise",
        text_layer="nested quotation",
        qualification="Haskell calls the doctrine secondhand. S0 retains the OCR form 'arc'; the printed page reads 'are'.",
        ocr_corrections=[{"source_line": 152, "source_form": "arc", "print_form": "are"}],
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-planned-apse-scheme", subject="cand-2557", object_="cand-5910",
        predicate="planned_proposed_glory_of_paradise_apse_scheme",
        claim="Haskell says Testa planned a Glory of Paradise scheme for an apse.",
        original_quote="He put his increasingly classical ideas into practice, planning to represent",
        lines=(152, 152), relation=True,
        relation_note="This records a planned work by Testa; the source does not establish that the scheme was executed.",
        mentioned=["cand-2557", "cand-5910"],
        qualification="The scheme is proposed; no completed decoration is established.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-apse-scheme-location", subject="cand-5910", object_="cand-5909",
        predicate="planned_for_apse_of_s_martino_ai_monti",
        claim="Haskell says the proposed Glory of Paradise scheme was intended for the apse of S. Martino ai Monti.",
        original_quote="in the apse of S. Martino ai Monti",
        lines=(152, 152), relation=True,
        relation_note="This is the intended location of the proposed scheme, not evidence that it was installed or completed.",
        mentioned=["cand-5910", "cand-5909"],
        qualification="Haskell's account of a plan; the church is the intended site only.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-apse-scheme-departs-correggio-custom", subject="cand-5910", object_="cand-0852",
        predicate="planned_to_depart_from_custom_attributed_to_correggio",
        claim="Haskell says the planned scheme would break from a general custom that he attributes to Correggio.",
        original_quote="a glory of Paradise which should break away from the general custom started by Correggio",
        lines=(152, 152), relation=True,
        relation_note="Correggio is the stated originator of the custom from which the proposed scheme would depart; this does not assert direct influence or identify the broader custom as a separate entity.",
        mentioned=["cand-5910", "cand-0852"],
        qualification="Haskell's characterization of an unrealized plan and a custom attributed to Correggio.",
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-urban-death", subject="cand-0209", object_=None,
        predicate="died_in_1644",
        claim="Haskell states that Urban VIII died in 1644.",
        original_quote="Then in 1644 Urban VIII died.",
        lines=(156, 156), relation=False,
        relation_note="This is a date claim about one person, not a relation between entities.",
        mentioned=["cand-0209"],
        qualification="Recorded as Haskell's statement; no independent external verification is claimed.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-small-heart-interpretation", subject="cand-0209", object_=None,
        predicate="quoted_account_describes_urban_viiis_heart_as_extraordinarily_small",
        claim="The quoted account describes Urban VIII's heart as extraordinarily small.",
        original_quote="His heart was extraordinarily small",
        lines=(157, 157), relation=False,
        relation_note="This is a scalar description in the quoted postmortem account, not a relation between entities.",
        mentioned=["cand-0209"], speaker="Cassiano's account as quoted by Haskell", text_layer="nested quotation",
        qualification="Quoted medical description; not independently verified.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-scientists-interpret-small-heart", subject="cand-0209", object_=None,
        predicate="quoted_account_attributes_vivacity_and_magnanimity_interpretation_to_scientists",
        claim="The quoted account says natural scientists interpreted Urban VIII's unusually small heart as a sign of vivacity and magnanimity.",
        original_quote="a sign of his vivacity and magnanimity, so the natural scientists say",
        lines=(157, 157), relation=False,
        relation_note="The unnamed natural scientists are not a bounded endpoint; this records the quoted interpretation as a scalar claim.",
        mentioned=["cand-0209"], speaker="Natural scientists as cited in Cassiano's account quoted by Haskell",
        text_layer="nested quotation",
        qualification="The unnamed scientists' interpretation is reported in a quotation and is not independently verified.",
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-suicide-date", subject="cand-2557", object_="cand-5914",
        predicate="suicide_dated_to_1650_by_haskell",
        claim="Haskell dates Testa's suicide to 1650.",
        original_quote="Testa’s suicide took place in 1650.",
        lines=(155, 155), relation=True,
        relation_note="The person-to-event link preserves Haskell's dating as a source claim; it is not an independently verified date.",
        mentioned=["cand-2557", "cand-5914"],
        qualification="Date is attributed to Haskell; no independent verification is claimed.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-testa-suicide", subject="cand-2557", object_="cand-5914",
        predicate="threw_himself_into_tiber_in_reported_suicide",
        claim="Haskell says Testa threw himself into the Tiber in an act of despair.",
        original_quote="In an agony of despair he threw himself into the Tiber.",
        lines=(154, 154), relation=True,
        relation_note="This records Testa's reported participation in the suicide event. The Tiber location is represented in a separate relation statement.",
        mentioned=["cand-2557", "cand-5914"],
        qualification="Haskell's biographical account; the event is not independently verified.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-tiber-suicide-location", subject="cand-5914", object_="cand-4453",
        predicate="reported_suicide_occurred_in_tiber",
        claim="Haskell locates Testa's reported suicide in the Tiber.",
        original_quote="he threw himself into the Tiber",
        lines=(154, 154), relation=True,
        relation_note="The source names the Tiber as the location of the reported event; this is separate from Testa's participation in the event.",
        mentioned=["cand-5914", "cand-4453"],
        qualification="Haskell's biographical account; the event is not independently verified.",
    ))

    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-treatise", subject="cand-2557", object_="cand-5911",
        predicate="authored_unidentified_treatise_on_painting",
        claim="Haskell says Testa wrote an unidentified Treatise on Painting.",
        original_quote="He wrote a muddled Treatise on painting",
        lines=(152, 152), relation=True,
        relation_note="This records authorship of the unidentified text; Haskell's evaluation and the text's described content are separated below.",
        mentioned=["cand-2557", "cand-5911"],
        qualification="No manuscript, edition, or fuller title is identified; 'muddled' is Haskell's evaluation.",
    ))
    p112_rows.append(new_statement(
        "st-chp4-sec-ii-p112-treatise-content", subject="cand-5911", object_=None,
        predicate="described_as_muddled_with_observation_colour_and_secondhand_doctrine",
        claim="Haskell characterizes the Treatise as muddled and says sensitive observation and love of colour alternate with secondhand doctrines.",
        original_quote="a muddled Treatise on painting in which flashes of genuinely sensitive observation and a deeply felt love of colour alternate with secondhand doctrines",
        lines=(152, 152), relation=False,
        relation_note="This is Haskell's evaluative description of the text's contents, not an additional authorship relation or an endorsement of every doctrine by Testa.",
        mentioned=["cand-2557", "cand-5911"],
        qualification="Haskell's characterization; the treatise itself has not been independently consulted.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-turn-to-engraving", subject="cand-2557", object_=None,
        predicate="turned_to_engraving_in_discouragement",
        claim="Haskell says Testa turned to engraving in discouragement.",
        original_quote="In his discouragement he turned to engraving.",
        lines=(154, 154), relation=False,
        relation_note="This is a career-change claim about Testa; the generic practice of engraving is not equated with the later unidentified print group.",
        mentioned=["cand-2557"],
        qualification="Haskell's interpretation of the career change; the specific works are discussed separately.",
    ))
    p112_rows.append(patch_existing(
        "st-chp4-sec-ii-p112-withdrawal-from-ceremonies", subject="cand-2036", object_=None,
        predicate="compelled_to_withdraw_from_empty_ceremonies",
        claim="Haskell says Cassiano was compelled, whether reluctantly or not, to withdraw from what he called the boring exercise of empty ceremonies.",
        original_quote="Reluc-\n- tantly or not, he was compelled to withdraw from ‘the boring exercise of empty ceremonies’.",
        lines=(158, 159), relation=False,
        relation_note="This records Cassiano's reported withdrawal as a scalar career/status claim. The passive wording does not identify an agent, so the statement is not connected causally to Innocent X.",
        mentioned=["cand-2036", "cand-1819"], speaker="Haskell reporting Cassiano",
        text_layer="authorial narrative with quoted phrase",
        qualification="'Reluctantly or not' preserves Haskell's uncertainty. The extra line-start hyphen in S0 is an OCR artifact; no compelling agent is named.",
        ocr_corrections=[{"source_line": 159, "source_form": "Reluc-\n- tantly", "print_form": "Reluc-\ntantly"}],
    ))

    expected_new_statement_ids = set(NEW_IDS)
    new_rows = [row for row in by_id.values() if row["statement_id"] in expected_new_statement_ids]
    if {row["statement_id"] for row in new_rows} != expected_new_statement_ids:
        raise SystemExit("preflight failed: the new statement set differs from the declared set")
    if {row["statement_id"] for row in p112_rows if row["statement_id"] in ORIGINAL_IDS} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: not all original p.112 statements were revised")

    # Keep the page-turn continuation linked to the p.113 sentence it completes.
    if NEXT_STATEMENT_ID not in by_id or by_id[NEXT_STATEMENT_ID].get("segment_id") != NEXT_SEGMENT_ID:
        raise SystemExit("preflight failed: expected p.113 continuation statement is absent")
    fabio_id = "st-chp4-sec-ii-p112-fabio-chigi-election"
    p113_q = by_id[NEXT_STATEMENT_ID]["qualifiers"]
    linked = set(p113_q.get("related_statement_ids", []))
    linked.add(fabio_id)
    p113_q["related_statement_ids"] = sorted(linked)

    # Add the already-existing Italy candidate to the mention ledger; no candidate is created.
    mentions.append(new_mention)

    for row in by_id.values():
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: missing candidate endpoint {endpoint} in {row['statement_id']}")
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in candidate_ids:
                raise SystemExit(f"preflight failed: missing mentioned candidate {candidate_id} in {row['statement_id']}")

    for row in p112_rows + new_rows:
        q = row["qualifiers"]
        if not (151 <= q["source_line_start"] <= q["source_line_end"] <= 159):
            raise SystemExit(f"preflight failed: out-of-segment line anchor in {row['statement_id']}")
        if q.get("relation_candidate") not in (True, False):
            raise SystemExit(f"preflight failed: unclassified statement {row['statement_id']}")
        for key in ("relation_candidate_note",):
            if not q.get(key, "").strip():
                raise SystemExit(f"preflight failed: missing {key} in {row['statement_id']}")
    mention_spans = [
        row for row in mentions if row["segment_id"] == SEGMENT_ID
    ]
    if len(mention_spans) != 29 or any(
        segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]
        for row in mention_spans
    ):
        raise SystemExit("preflight failed: p.112 mention set or spans changed unexpectedly")

    # Insert added statements next to their source segment, retaining book order.
    original_positions = [i for i, row in enumerate(rows) if row.get("segment_id") == SEGMENT_ID]
    insert_at = max(original_positions) + 1
    for row in p112_rows:
        by_id[row["statement_id"]] = row
    rows[insert_at:insert_at] = new_rows

    counts = segment_counts(rows)
    expected_counts = {
        "statements": 42,
        "dual": 26,
        "relation_true": 26,
        "relation_false": 16,
        "dual_true": 24,
        "dual_false": 2,
        "open_relation": 2,
        "unclassified": 0,
    }
    if counts != expected_counts:
        raise SystemExit(f"preflight failed: unexpected p.112 counts {counts}")
    if len(rows) != 13030:
        raise SystemExit(f"preflight failed: unexpected statement total {len(rows)}")
    if len(mentions) != 27565:
        raise SystemExit(f"preflight failed: unexpected mention total {len(mentions)}")
    if len({row["statement_id"] for row in rows}) != len(rows):
        raise SystemExit("preflight failed: duplicate statement IDs after update")

    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "original_statements": len(ORIGINAL_IDS),
        "new_statements": len(new_rows),
        "resulting_segment_counts": counts,
        "new_mention": new_mention,
        "table_totals": {"statements": len(rows), "mentions": len(mentions), "candidates": len(candidates)},
        "new_statement_ids": sorted(expected_new_statement_ids),
        "classification_plan": [
            {
                "statement_id": row["statement_id"],
                "predicate": row["predicate"],
                "subject": row.get("subject_candidate_id"),
                "object": row.get("object_candidate_id"),
                "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
                "open_endpoint": bool(row.get("qualifiers", {}).get("open_endpoint_reason")),
            }
            for row in rows if row.get("segment_id") == SEGMENT_ID
        ],
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    statement_backup = statement_path.with_name(f"{statement_path.name}.{STATEMENT_BACKUP_SUFFIX}")
    mention_backup = mention_path.with_name(f"{mention_path.name}.{MENTION_BACKUP_SUFFIX}")
    for backup in (statement_backup, mention_backup):
        if backup.exists():
            raise SystemExit(f"apply refused: recovery copy already exists: {backup.name}")

    statement_bytes = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    mention_path_bytes = mention_path.read_bytes()
    if not mention_path_bytes.endswith(b"\n"):
        mention_path_bytes += b"\n"
    mention_path_bytes += ",".join([
        new_mention["mention_id"], new_mention["segment_id"], new_mention["candidate_id"],
        new_mention["surface_form"], new_mention["start_char"], new_mention["end_char"],
        new_mention["note"],
    ]).encode("utf-8") + b"\n"
    statement_tmp = statement_path.with_name(statement_path.name + ".p112.tmp")
    mention_tmp = mention_path.with_name(mention_path.name + ".p112.tmp")
    if statement_tmp.exists() or mention_tmp.exists():
        raise SystemExit("apply refused: a p.112 temporary write file already exists")
    shutil.copy2(statement_path, statement_backup)
    shutil.copy2(mention_path, mention_backup)
    statement_tmp.write_bytes(statement_bytes)
    mention_tmp.write_bytes(mention_path_bytes)
    try:
        os.replace(statement_tmp, statement_path)
        os.replace(mention_tmp, mention_path)
        written_rows = read_jsonl(statement_path)
        written_mentions = list(csv.DictReader(mention_path.open(encoding="utf-8-sig", newline="")))
        if len(written_rows) != 13030 or len(written_mentions) != 27565:
            raise RuntimeError("post-write table count mismatch")
        if segment_counts(written_rows) != expected_counts:
            raise RuntimeError("post-write p.112 statement classification mismatch")
        written_p112 = [row for row in written_rows if row.get("segment_id") == SEGMENT_ID]
        if any(row.get("qualifiers", {}).get("relation_candidate") is None for row in written_p112):
            raise RuntimeError("post-write p.112 has an unclassified statement")
        if sha(candidate_path.read_bytes()) != EXPECTED_SHA256["entity-candidates.csv"]:
            raise RuntimeError("candidate table unexpectedly changed")
    except Exception:
        shutil.copy2(statement_backup, statement_path)
        shutil.copy2(mention_backup, mention_path)
        statement_tmp.unlink(missing_ok=True)
        mention_tmp.unlink(missing_ok=True)
        raise

    print(json.dumps({
        "write": "success",
        "statement_sha256": sha(statement_path.read_bytes()),
        "mentions_sha256": sha(mention_path.read_bytes()),
        "recovery_copies": [statement_backup.name, mention_backup.name],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
