#!/usr/bin/env python3
"""Classify and atomize the p.110 S2 statements after source-page review."""
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
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l130-137"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "ec71a683941495041787c93f6c1f6bbc6b3d69df2bd4664083fe030dd46f205a"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "179a048c1c4f27dfbd2f4e07a5d6661b827ea25c89549bac0aabcf749252e6a0",
    "entity-candidates.csv": "01eaae9a76cc32c5a12e78820594517a3382bbea6ac9447c121cd57bd141b1a2",
    "mentions.csv": "e8ce04ae40d08cef4fc2e5c094aebf8be01510c917e7d23b74b20c3e2e6a3516",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l130-137-relations-20261011"

ORIGINAL_IDS = {
    "st-chp4-sec-ii-p110-cassiano-religious-horizons",
    "st-chp4-sec-ii-p110-cassiano-sacred-art-beliefs",
    "st-chp4-sec-ii-p110-cassiano-willing-recipient",
    "st-chp4-sec-ii-p110-counterreformation-associations",
    "st-chp4-sec-ii-p110-flight-figures-above",
    "st-chp4-sec-ii-p110-flight-figures-background",
    "st-chp4-sec-ii-p110-flight-figures-foreground",
    "st-chp4-sec-ii-p110-flight-mysticism-geography",
    "st-chp4-sec-ii-p110-flight-poussin-contrast-fragment",
    "st-chp4-sec-ii-p110-flight-treatment-unique",
    "st-chp4-sec-ii-p110-inquiry-rites-resolved",
    "st-chp4-sec-ii-p110-no-proof-cassiano-chose-subject",
    "st-chp4-sec-ii-p110-poussin-christian-practices",
    "st-chp4-sec-ii-p110-poussin-historical-curiosity",
    "st-chp4-sec-ii-p110-sacraments-pride-copying",
    "st-chp4-sec-ii-p110-severe-imagery-possibility",
    "st-chp4-sec-ii-p110-testa-massacre-picture",
    "st-chp4-sec-ii-p110-testa-print-dedicated-flight",
    "st-chp4-sec-ii-p110-viewpoints",
}
NEW_IDS = {
    "st-chp4-sec-ii-p110-flight-dove-above",
    "st-chp4-sec-ii-p110-flight-associated-with-passion",
    "st-chp4-sec-ii-p110-flight-subsidiary-role",
    "st-chp4-sec-ii-p110-poussin-exactitude-pagan-scenes",
    "st-chp4-sec-ii-p110-poussin-refused-sacraments-copying",
    "st-chp4-sec-ii-p110-poussin-specified-christian-practices",
    "st-chp4-sec-ii-p110-testa-print-created-by-testa",
    "st-chp4-sec-ii-p110-testa-print-dedicated-to-cassiano",
    "st-chp4-sec-ii-p110-testa-picture-located-spada-gallery",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def quote_between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at) + len(end)
    return text[start_at:end_at]


def set_statement(
    row: dict,
    *,
    subject: str | None,
    object_: str | None,
    predicate: str,
    claim: str,
    quote: str,
    relation: bool,
    note: str,
    mentions: list[str],
    line_start: int,
    line_end: int,
    qualification: str | None = None,
    ocr_corrections: list[dict] | None = None,
) -> None:
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q["claim"] = claim
    q["relation_candidate"] = relation
    q["relation_candidate_note"] = note
    q["mentioned_candidate_ids"] = mentions
    q["source_line_start"] = line_start
    q["source_line_end"] = line_end
    q["pdf_physical_page"] = 21
    q["printed_page_locator"] = "p.110"
    if qualification is not None:
        q["qualification"] = qualification
    if ocr_corrections is not None:
        q["ocr_corrections"] = ocr_corrections


def make_statement(
    statement_id: str,
    *,
    subject: str,
    object_: str,
    predicate: str,
    claim: str,
    quote: str,
    line_start: int,
    line_end: int,
    note: str,
    mentions: list[str],
    qualification: str,
    ocr_corrections: list[dict] | None = None,
) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": 21,
        "printed_page_locator": "p.110",
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "mentioned_candidate_ids": mentions,
        "qualification": qualification,
        "relation_candidate": True,
        "relation_candidate_note": note,
    }
    if ocr_corrections:
        qualifiers["ocr_corrections"] = ocr_corrections
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


def segment_counts(rows: list[dict]) -> dict[str, int]:
    dual = [row for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    return {
        "statements": len(rows),
        "dual": len(dual),
        "relation_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in rows),
        "relation_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in rows),
        "dual_true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual),
        "dual_false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual),
        "unclassified": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in rows),
    }


def global_counts(rows: list[dict], candidate_count: int, mention_count: int) -> dict[str, int]:
    dual = [row for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    return {
        "all_statements": len(rows),
        "all_candidates": candidate_count,
        "all_mentions": mention_count,
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


def patched_jsonl_bytes(path: Path, updates: dict[str, dict], additions: list[dict]) -> bytes:
    serialized = {key: json.dumps(row, ensure_ascii=False) + "\n" for key, row in updates.items()}
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    output = []
    seen = set()
    for line in lines:
        if not line.strip():
            output.append(line)
            continue
        statement_id = json.loads(line)["statement_id"]
        if statement_id in serialized:
            output.append(serialized[statement_id])
            seen.add(statement_id)
        else:
            output.append(line)
    if seen != set(updates):
        raise SystemExit(f"preflight failed: update IDs not found: {sorted(set(updates) - seen)}")
    if output and not output[-1].endswith(("\n", "\r")):
        output[-1] += "\n"
    output.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in additions)
    return "".join(output).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted p.110 changes")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    for name, expected in EXPECTED_SHA256.items():
        actual = sha((TABLES / name).read_bytes())
        if actual != expected:
            raise SystemExit(f"preflight failed: {name} hash changed: {actual}")
    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source asset hash changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[129:137])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.110 segment text hash changed")

    statements = read_jsonl(statement_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: statement IDs are not unique")
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if {row["statement_id"] for row in segment_rows} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: p.110 original statement set changed")
    original_projection = {
        row["statement_id"]: {
            "subject": row.get("subject_candidate_id"),
            "predicate": row.get("predicate"),
            "object": row.get("object_candidate_id"),
            "relation_candidate": row.get("qualifiers", {}).get("relation_candidate"),
        }
        for row in segment_rows
    }
    dual_unclassified = [
        row for row in segment_rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
        and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    single_unclassified = [
        row for row in segment_rows
        if not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if len(dual_unclassified) != 15 or len(single_unclassified) != 3:
        raise SystemExit(
            f"preflight failed: p.110 classification state changed: dual={len(dual_unclassified)} single={len(single_unclassified)}"
        )
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in segment_rows) != 1:
        raise SystemExit("preflight failed: expected exactly one already-classified p.110 relation")
    if NEW_IDS.intersection(by_id):
        raise SystemExit("preflight failed: a planned p.110 statement ID already exists")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_rows = list(csv.DictReader(handle))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    candidate_names = {row["candidate_id"]: row["canonical_name"] for row in candidate_rows}
    endpoint_ids = {
        value
        for row in segment_rows
        for value in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        if value
    }
    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        segment_mentions = [row for row in csv.DictReader(handle) if row["segment_id"] == SEGMENT_ID]
    if len(segment_mentions) != 51:
        raise SystemExit(f"preflight failed: expected 51 current p.110 mentions, found {len(segment_mentions)}")
    mention_errors = []
    for row in segment_mentions:
        surface = segment_text[int(row["start_char"]):int(row["end_char"])]
        if surface != row["surface_form"]:
            mention_errors.append(row["mention_id"])
        if row["candidate_id"] not in candidate_ids:
            mention_errors.append(f"{row['mention_id']}:missing-candidate:{row['candidate_id']}")
    if mention_errors:
        raise SystemExit(f"preflight failed: p.110 mention issues: {mention_errors}")
    for endpoint in endpoint_ids:
        if endpoint not in candidate_ids:
            raise SystemExit(f"preflight failed: existing endpoint is missing: {endpoint}")

    quote = lambda start, end: quote_between(segment_text, start, end)
    corrections = {
        "religious": [{"source_line": 133, "source_form": "rehgious", "print_form": "religious"}],
        "beliefs": [{"source_line": 133, "source_form": "behed", "print_form": "belied"}],
        "flight": [{"source_line": 134, "source_form": "Egyptwith", "print_form": "Egypt with"}],
        "authenticity": [{"source_line": 131, "source_form": "a-kind", "print_form": "a kind"}],
    }
    relation_notes = {
        "st-chp4-sec-ii-p110-counterreformation-associations": "Haskell reports a recurring Counter-Reformation iconographic association between the Flight into Egypt and the Massacre of the Innocents; this does not equate the episodes or identify a specific print as the source of the convention.",
        "st-chp4-sec-ii-p110-flight-figures-above": "Haskell describes God the Father above the composition; the Dove is separated into its own depiction statement.",
        "st-chp4-sec-ii-p110-flight-figures-background": "Haskell describes Saint Joseph asleep in the print's background; the angel's action remains context rather than an endpoint in this statement.",
        "st-chp4-sec-ii-p110-flight-figures-foreground": "Haskell describes the Virgin in the foreground group adoring the Cross and Instruments of the Passion; the other figures and objects remain in the source context.",
        "st-chp4-sec-ii-p110-flight-mysticism-geography": "Haskell says this print recalls a type of mysticism more common in Spain than Italy; this is a comparative interpretation, not a claim about the print's origin.",
        "st-chp4-sec-ii-p110-flight-poussin-contrast-fragment": "Haskell contrasts the print's sentiment with Poussin's austere Sacraments; the comparison remains attributed to the author.",
        "st-chp4-sec-ii-p110-poussin-christian-practices": "Haskell says the practices Poussin specified were familiar to Cassiano and his learned friends; familiarity is kept separate from Poussin's act of specifying them.",
        "st-chp4-sec-ii-p110-sacraments-pride-copying": "Haskell says Poussin was proud of the Sacraments; his refusal to permit copying is recorded separately.",
        "st-chp4-sec-ii-p110-severe-imagery-possibility": "This remains Haskell's explicitly qualified possibility about Poussin's severe imagery being more acceptable to Cassiano, not an independently established motive or commission.",
        "st-chp4-sec-ii-p110-testa-massacre-picture": "Haskell reports Testa's authorship of the Massacre picture; its location in the Spada Gallery is recorded separately.",
        "st-chp4-sec-ii-p110-testa-print-dedicated-flight": "Haskell identifies the print as depicting the Flight into Egypt; its creator and dedicatee are separated into their own statements.",
    }
    nonrelation_notes = {
        "st-chp4-sec-ii-p110-cassiano-religious-horizons": "This is Haskell's scalar inference about Cassiano's religious horizons; the papal court is a comparison context, not a relation endpoint.",
        "st-chp4-sec-ii-p110-cassiano-sacred-art-beliefs": "This is Haskell's qualified interpretation of what unusual sacred art may confirm about Cassiano's beliefs.",
        "st-chp4-sec-ii-p110-cassiano-willing-recipient": "This is Haskell's inference about Cassiano's stance toward new ideas, not a direct relation to Testa.",
        "st-chp4-sec-ii-p110-flight-treatment-unique": "This records Haskell's scalar evaluation of the print's unusual treatment; the subsidiary role of the Flight is a separate relation candidate.",
        "st-chp4-sec-ii-p110-inquiry-rites-resolved": "This records Haskell's characterization of Cassiano's attitude and its capacity to reconcile several viewpoints, not a relation to each viewpoint.",
        "st-chp4-sec-ii-p110-no-proof-cassiano-chose-subject": "This is an evidentiary limitation stated by Haskell; it does not assert that Cassiano chose the print's subject.",
        "st-chp4-sec-ii-p110-poussin-historical-curiosity": "This records Haskell's qualified account of Poussin's motive as a scalar interpretation; the pagan scenes are contextual examples.",
        "st-chp4-sec-ii-p110-viewpoints": "This records Haskell's scalar description of an attitude that could reconcile several views, not pairwise relations with the listed views.",
    }

    updates: dict[str, dict] = {}
    def update(statement_id: str, **values: object) -> None:
        row = by_id[statement_id]
        set_statement(row, **values)
        updates[statement_id] = row

    update(
        "st-chp4-sec-ii-p110-cassiano-religious-horizons",
        subject="cand-2036", object_=None,
        predicate="author_infers_cassiano_religious_horizons_wider_than_court_position_suggests",
        claim="Haskell infers that Cassiano's religious horizons must have been wider than his position at the centre of the papal court might suggest.",
        quote=quote("his rehgious horizons must have been considerably wider", "one to suppose."),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-cassiano-religious-horizons"],
        mentions=["cand-2036", "cand-4730"], line_start=133, line_end=133,
        qualification="The comparison with the papal court is Haskell's inference and does not identify a separate religious institution.",
        ocr_corrections=corrections["religious"],
    )
    update(
        "st-chp4-sec-ii-p110-cassiano-sacred-art-beliefs",
        subject="cand-2036", object_=None,
        predicate="author_says_unusual_sacred_art_may_confirm_cassiano_belief_interpretation",
        claim="Haskell says the unusual sacred art produced under Cassiano's auspices may confirm his beliefs.",
        quote=quote("This view of his beliefs is perhaps confirmed rather than behed", "Cassiano’s auspices."),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-cassiano-sacred-art-beliefs"],
        mentions=["cand-2036"], line_start=133, line_end=133,
        qualification="Haskell says 'perhaps'; this remains his interpretation, not independent confirmation of Cassiano's beliefs.",
        ocr_corrections=corrections["beliefs"],
    )
    update(
        "st-chp4-sec-ii-p110-cassiano-willing-recipient",
        subject="cand-2036", object_=None,
        predicate="author_infers_cassiano_willing_recipient_of_new_ideas",
        claim="Haskell infers from Testa's other conventional religious prints that Cassiano was at least a willing recipient of new ideas, if not their positive inspirer.",
        quote=quote("But Testa’s other religious prints are all conventional enough", "if not their positive inspirer."),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-cassiano-willing-recipient"],
        mentions=["cand-2036", "cand-2556"], line_start=136, line_end=137,
        qualification="Haskell presents this as an inference from Testa's other prints, not as a direct exchange or commission.",
    )
    update(
        "st-chp4-sec-ii-p110-counterreformation-associations",
        subject="cand-5876", object_="cand-3488",
        predicate="author_reports_counter_reformation_association_between_flight_and_massacre",
        claim="Haskell says Counter-Reformation imagery often associated the Flight into Egypt with the Massacre of the Innocents.",
        quote=quote("It was frequent enough in the imagery of the Counter Reformation", "with the Massacre of the Innocents"),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-counterreformation-associations"],
        mentions=["cand-3396", "cand-5876", "cand-5877", "cand-3488"], line_start=134, line_end=134,
        qualification="The passage describes an iconographic convention; 'often' is retained and the OCR form Egyptwith is preserved in the source quote.",
        ocr_corrections=corrections["flight"],
    )
    update(
        "st-chp4-sec-ii-p110-flight-figures-above",
        subject="cand-5859", object_="cand-5862",
        predicate="print_depicts_god_the_father_above_composition",
        claim="Haskell says God the Father appears above the composition of Testa's print.",
        quote=quote("Above are God the Father", "God the Father"),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-flight-figures-above"],
        mentions=["cand-5859", "cand-5862"], line_start=134, line_end=134,
    )
    update(
        "st-chp4-sec-ii-p110-flight-figures-background",
        subject="cand-5859", object_="cand-5860",
        predicate="print_depicts_saint_joseph_sleeping_in_background",
        claim="Haskell describes Saint Joseph asleep in the background of the print while an angel points out the route of flight.",
        quote=quote("Scarcely visible in the shadow of a huge gnarled tree", "points out the route of his flight."),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-flight-figures-background"],
        mentions=["cand-5859", "cand-5860", "cand-5878"], line_start=134, line_end=134,
    )
    update(
        "st-chp4-sec-ii-p110-flight-figures-foreground",
        subject="cand-5859", object_="cand-3427",
        predicate="print_depicts_virgin_mary_in_foreground_group",
        claim="Haskell describes the Virgin in the foreground group with the Child, Mary Magdalene, angels, and putti adoring the Cross and Instruments of the Passion.",
        quote=quote("The whole foreground is taken up by the Virgin", "the Instruments of the Passion."),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-flight-figures-foreground"],
        mentions=["cand-5859", "cand-3427", "cand-3425", "cand-5861", "cand-5865", "cand-5866", "cand-5867", "cand-5868", "cand-5877"],
        line_start=134, line_end=134,
    )
    update(
        "st-chp4-sec-ii-p110-flight-mysticism-geography",
        subject="cand-5859", object_="cand-5196",
        predicate="print_recalled_mysticism_more_common_in_spain_than_italy",
        claim="Haskell says the print recalls a type of mysticism more common in Spain than in Italy.",
        quote=quote("In the whirling exuberant clusters of putti", "more common in Spain than in Italy."),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-flight-mysticism-geography"],
        mentions=["cand-5859", "cand-5196", "cand-5120", "cand-3461"], line_start=137, line_end=137,
        qualification="This is Haskell's comparative interpretation; no Spanish origin or direct transmission is asserted.",
    )
    update(
        "st-chp4-sec-ii-p110-flight-poussin-contrast-fragment",
        subject="cand-5859", object_="cand-5789",
        predicate="author_contrasts_print_sentiment_with_poussins_austere_sacraments",
        claim="Haskell says the print's sentiment stands at the opposite extreme from the austere world of Poussin's Sacraments.",
        quote=quote("In sentiment it certainly stands at the opposite extreme", "Poussin’s Sacraments."),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-flight-poussin-contrast-fragment"],
        mentions=["cand-5859", "cand-5789"], line_start=137, line_end=137,
        qualification="The sentence continues on p.111; only the complete comparison on p.110 is recorded here.",
    )
    update(
        "st-chp4-sec-ii-p110-flight-treatment-unique",
        subject="cand-5859", object_=None,
        predicate="author_calls_print_treatment_unique_and_explanation_long",
        claim="Haskell calls Testa's treatment of the subject unique and says Testa supplied a long explanation of the print.",
        quote=quote("Such a treatment of the subject is unique", "long explanation of his print."),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-flight-treatment-unique"],
        mentions=["cand-5859", "cand-2556", "cand-5876"], line_start=134, line_end=134,
    )
    update(
        "st-chp4-sec-ii-p110-inquiry-rites-resolved",
        subject="cand-2036", object_=None,
        predicate="author_attributes_dispassionate_inquiry_into_fundamental_rites_of_other_religions",
        claim="The p.109 sentence continues on p.110, completing Haskell's claim that Cassiano's scholarship encouraged dispassionate inquiry into fundamental rites of other religions.",
        quote=quote("rites of other religions.", "rites of other religions."),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-inquiry-rites-resolved"],
        mentions=["cand-2036"], line_start=131, line_end=131,
        qualification="This fragment closes the sentence begun on p.109; it is not a standalone relation to another entity.",
    )
    update(
        "st-chp4-sec-ii-p110-no-proof-cassiano-chose-subject",
        subject="cand-2036", object_=None,
        predicate="author_says_dedication_does_not_prove_cassiano_chose_subject",
        claim="Haskell says there is no proof that Cassiano himself chose the subject despite the dedication.",
        quote=quote("Despite the dedication", "chose the subject."),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-no-proof-cassiano-chose-subject"],
        mentions=["cand-2036", "cand-5859"], line_start=135, line_end=135,
        qualification="This is a limit on the available evidence, not a denial that Cassiano may have chosen it.",
    )
    update(
        "st-chp4-sec-ii-p110-poussin-christian-practices",
        subject="cand-5856", object_="cand-2036",
        predicate="early_christian_practices_familiar_to_cassiano",
        claim="Haskell says the early and obscure Christian practices Poussin specified were familiar to Cassiano and his learned friends.",
        quote=quote("practices that were, however, certainly familiar", "Cassiano and his learned friends."),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-poussin-christian-practices"],
        mentions=["cand-1984", "cand-5856", "cand-2036"], line_start=131, line_end=131,
        qualification="The claim reports Haskell's account of familiarity; the learned friends are not individually identified.",
    )
    update(
        "st-chp4-sec-ii-p110-poussin-historical-curiosity",
        subject="cand-1984", object_=None,
        predicate="author_says_poussin_accuracy_probably_motivated_by_historical_curiosity",
        claim="Haskell says Poussin's motives for such accuracy were probably inspired mainly by historical curiosity.",
        quote=quote("the motives for such accuracy were probably inspired mainly by historical curiosity", "historical curiosity"),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-poussin-historical-curiosity"],
        mentions=["cand-1984", "cand-5857"], line_start=131, line_end=131,
        qualification="Haskell says 'probably' and 'mainly'; this remains an attributed motive, not a direct relation to a work.",
    )
    update(
        "st-chp4-sec-ii-p110-sacraments-pride-copying",
        subject="cand-1984", object_="cand-5789",
        predicate="poussin_proud_of_sacraments_series",
        claim="Haskell says Poussin was enormously proud of the Sacraments.",
        quote=quote("he was enormously proud of the Sacraments", "the Sacraments"),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-sacraments-pride-copying"],
        mentions=["cand-1984", "cand-5789"], line_start=132, line_end=132,
    )
    update(
        "st-chp4-sec-ii-p110-severe-imagery-possibility",
        subject="cand-1984", object_="cand-2036",
        predicate="author_suggests_poussin_authenticity_might_make_imagery_more_acceptable_to_cassiano",
        claim="Haskell says it is perfectly possible that Poussin's pursuit of authenticity led him to severe, purified religious imagery more acceptable to Cassiano than the flamboyant Baroque of some contemporaries.",
        quote=quote("it is perfectly possible that in his pursuit of authenticity", "Baroque of some of his contemporaries."),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-severe-imagery-possibility"],
        mentions=["cand-1984", "cand-2036", "cand-4500"], line_start=131, line_end=132,
        qualification="Haskell's 'perfectly possible' and comparative wording remain explicit; this is not treated as a confirmed commission motive.",
        ocr_corrections=corrections["authenticity"],
    )
    update(
        "st-chp4-sec-ii-p110-testa-massacre-picture",
        subject="cand-5869", object_="cand-2556",
        predicate="work_created_by_pietro_testa_reported",
        claim="Haskell says Testa treated the Massacre of the Innocents in his large, vigorous picture.",
        quote=quote("a theme which Testa himself treated in his masterpiece", "a large and vigorous picture in the Spada Gallery."),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-testa-massacre-picture"],
        mentions=["cand-5869", "cand-2556", "cand-3488", "cand-5870"], line_start=134, line_end=134,
    )
    update(
        "st-chp4-sec-ii-p110-testa-print-dedicated-flight",
        subject="cand-5859", object_="cand-5876",
        predicate="print_depicts_flight_into_egypt_event",
        claim="Haskell says Pietro Testa's print depicts a unique representation of the Flight into Egypt.",
        quote=quote("depicting a unique representation of the", "Flight into Egypt (Plate 18a).1"),
        relation=True, note=relation_notes["st-chp4-sec-ii-p110-testa-print-dedicated-flight"],
        mentions=["cand-5859", "cand-5876", "cand-2556", "cand-2036"], line_start=133, line_end=134,
        qualification="Footnote 1 remains linked to this print statement; creator and dedicatee are recorded separately.",
    )
    update(
        "st-chp4-sec-ii-p110-viewpoints",
        subject="cand-2036", object_=None,
        predicate="author_says_cassiano_attitude_reconciled_multiple_viewpoints",
        claim="Haskell says this attitude could reconcile Cassiano's probably sincere, if not ardent, Christianity, scholarship, scientific enquiries, and libertin connections.",
        quote=quote("This was an attitude that could reconcile many differing viewpoints", "connections."),
        relation=False, note=nonrelation_notes["st-chp4-sec-ii-p110-viewpoints"],
        mentions=["cand-2036", "cand-5855", "cand-5752", "cand-5808"], line_start=131, line_end=131,
        qualification="These are contextual dimensions of the attitude; the statement does not assert pairwise relations among them.",
    )

    new_rows = [
        make_statement(
            "st-chp4-sec-ii-p110-flight-dove-above",
            subject="cand-5859", object_="cand-5864", predicate="print_depicts_dove_of_holy_ghost_above_composition",
            claim="Haskell says the Dove of the Holy Ghost appears above the composition of Testa's print.",
            quote=quote("the Dove of the Holy Ghost.", "the Dove of the Holy Ghost."),
            line_start=134, line_end=134,
            note="This records the Dove as a separate depicted figure from God the Father; the Holy Ghost is not substituted for the dove-symbol candidate.",
            mentions=["cand-5859", "cand-5864", "cand-5863"],
            qualification="The source names the Dove of the Holy Ghost; the endpoint is the existing dove-symbol candidate.",
        ),
        make_statement(
            "st-chp4-sec-ii-p110-flight-associated-with-passion",
            subject="cand-5876", object_="cand-5877", predicate="flight_associated_with_passion_in_counter_reformation_imagery",
            claim="Haskell says Counter-Reformation imagery often associated the Flight into Egypt with the Passion.",
            quote=quote("to associate the Flight into Egyptwith the Passion", "to associate the Flight into Egyptwith the Passion"),
            line_start=134, line_end=134,
            note="Haskell reports a recurring iconographic association between two represented episodes; this does not equate the events.",
            mentions=["cand-3396", "cand-5876", "cand-5877"],
            qualification="The source says 'frequent enough'; the OCR's missing space in Egyptwith is preserved and recorded as a correction.",
            ocr_corrections=corrections["flight"],
        ),
        make_statement(
            "st-chp4-sec-ii-p110-flight-subsidiary-role",
            subject="cand-5859", object_="cand-5876", predicate="print_depicts_flight_into_egypt_as_subsidiary_in_composition",
            claim="Haskell says Testa gave the Flight into Egypt an entirely subsidiary role in the print's composition.",
            quote=quote("has given the Flight itself an entirely subsidiary role", "has given the Flight itself an entirely subsidiary role"),
            line_start=134, line_end=134,
            note="This records the compositional role Haskell attributes to the Flight episode within the print; it is distinct from the print's depiction of that episode.",
            mentions=["cand-5859", "cand-5876", "cand-2556"],
            qualification="Haskell compares this treatment with the usual practice; the claim remains attributed to him.",
        ),
        make_statement(
            "st-chp4-sec-ii-p110-poussin-exactitude-pagan-scenes",
            subject="cand-1984", object_="cand-5857", predicate="poussin_ensured_exactitude_in_pagan_scenes",
            claim="Haskell says Poussin took equal trouble to ensure exactitude in some pagan scenes of sacrifices to Priapus.",
            quote=quote("he took equal trouble to ensure exactitude in some of his pagan scenes", "and so on"),
            line_start=131, line_end=131,
            note="This is Haskell's direct report about Poussin's care in the identified group of pagan scenes; the individual scenes remain unidentified.",
            mentions=["cand-1984", "cand-5857", "cand-5858"],
            qualification="Only some pagan scenes are specified; no individual work titles or complete group membership are inferred.",
        ),
        make_statement(
            "st-chp4-sec-ii-p110-poussin-refused-sacraments-copying",
            subject="cand-1984", object_="cand-5789", predicate="poussin_refused_permission_to_copy_sacraments",
            claim="Haskell says Poussin refused permission for the Sacraments to be copied.",
            quote=quote("refused permission to have them copied.", "refused permission to have them copied."),
            line_start=132, line_end=132,
            note="This is a separate statement from Poussin's pride in the series; the text does not name the requester or proposed copy.",
            mentions=["cand-1984", "cand-5789"],
            qualification="The person requesting permission and any resulting copy are not identified.",
        ),
        make_statement(
            "st-chp4-sec-ii-p110-poussin-specified-christian-practices",
            subject="cand-1984", object_="cand-5856", predicate="poussin_specified_early_christian_practices",
            claim="Haskell says Poussin took endless trouble to specify early and obscure Christian practices.",
            quote=quote("he took endless trouble to specify early and obscure Christian practices", "he took endless trouble to specify early and obscure Christian practices"),
            line_start=131, line_end=131,
            note="This records Poussin's act of specifying the practices, separately from Haskell's statement that they were familiar to Cassiano.",
            mentions=["cand-1984", "cand-5856"],
            qualification="The specific practices are not individually identified in this passage.",
        ),
        make_statement(
            "st-chp4-sec-ii-p110-testa-print-created-by-testa",
            subject="cand-5859", object_="cand-2556", predicate="print_created_by_pietro_testa_reported",
            claim="Haskell attributes the Flight into Egypt print to Pietro Testa.",
            quote=quote("a print fulsomely dedicated to him by Pietro Testa", "a print fulsomely dedicated to him by Pietro Testa"),
            line_start=133, line_end=133,
            note="Haskell identifies Testa as the artist associated with the print; the S1 index sub-entry is retained separately and not merged here.",
            mentions=["cand-5859", "cand-2556", "cand-2036"],
            qualification="This is the author's attribution in the book; the print has not been independently examined.",
        ),
        make_statement(
            "st-chp4-sec-ii-p110-testa-print-dedicated-to-cassiano",
            subject="cand-5859", object_="cand-2036", predicate="print_dedicated_to_cassiano",
            claim="Haskell says Pietro Testa's Flight into Egypt print was dedicated to Cassiano.",
            quote=quote("a print fulsomely dedicated to him by Pietro Testa", "a print fulsomely dedicated to him by Pietro Testa"),
            line_start=133, line_end=133,
            note="This records the dedicatee separately from the print's creator; Cassiano's choice of subject is not inferred.",
            mentions=["cand-5859", "cand-2556", "cand-2036"],
            qualification="The next page explicitly says there is no proof Cassiano chose the subject.",
        ),
        make_statement(
            "st-chp4-sec-ii-p110-testa-picture-located-spada-gallery",
            subject="cand-5869", object_="cand-5870", predicate="work_located_at_spada_gallery_reported",
            claim="Haskell locates Testa's Massacre of the Innocents picture in the Spada Gallery.",
            quote=quote("a large and vigorous picture in the Spada Gallery.", "a large and vigorous picture in the Spada Gallery."),
            line_start=134, line_end=134,
            note="This records the reported location of the picture separately from Testa's authorship; no present-day collection status is inferred.",
            mentions=["cand-5869", "cand-5870", "cand-3488"],
            qualification="The statement reports the location in Haskell's text and does not independently verify the work or its current whereabouts.",
        ),
    ]

    for row in new_rows:
        if row["statement_id"] not in NEW_IDS:
            raise SystemExit(f"preflight failed: unexpected new statement ID: {row['statement_id']}")
        if row["original_quote"] not in segment_text:
            raise SystemExit(f"preflight failed: new quote not in p.110 source: {row['statement_id']}")
        for endpoint in (row["subject_candidate_id"], row["object_candidate_id"]):
            if endpoint not in candidate_ids:
                raise SystemExit(f"preflight failed: new endpoint missing: {row['statement_id']} -> {endpoint}")
        for candidate_id in row["qualifiers"]["mentioned_candidate_ids"]:
            if candidate_id not in candidate_ids:
                raise SystemExit(f"preflight failed: new mentioned candidate missing: {row['statement_id']} -> {candidate_id}")
        by_id[row["statement_id"]] = row
    if {row["statement_id"] for row in new_rows} != NEW_IDS:
        raise SystemExit("preflight failed: p.110 new statement set differs from declared IDs")

    for statement_id, note in relation_notes.items():
        if statement_id in by_id:
            by_id[statement_id]["qualifiers"]["relation_candidate_note"] = note
    for statement_id, note in nonrelation_notes.items():
        if statement_id in by_id:
            by_id[statement_id]["qualifiers"]["relation_candidate_note"] = note

    segment_after = [row for row in by_id.values() if row.get("segment_id") == SEGMENT_ID]
    expected_segment = {
        "statements": 28, "dual": 20, "relation_true": 20, "relation_false": 8,
        "dual_true": 20, "dual_false": 0, "unclassified": 0,
    }
    actual_segment = segment_counts(segment_after)
    if actual_segment != expected_segment:
        raise SystemExit(f"preflight failed: projected p.110 counts differ: {actual_segment}")

    mention_count = sum(1 for _ in csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    expected_global = {
        "all_statements": 13006,
        "all_candidates": 11626,
        "all_mentions": 27564,
        "dual_statements": 8802,
        "dual_true": 5685,
        "dual_false": 515,
        "dual_unclassified": 2602,
        "relation_true": 5747,
        "relation_true_open": 62,
    }
    projected_global = global_counts(list(by_id.values()), len(candidate_ids), mention_count)
    if projected_global != expected_global:
        raise SystemExit(f"preflight failed: projected global counts differ: {projected_global}")

    projected_bytes = patched_jsonl_bytes(
        statement_path,
        {statement_id: by_id[statement_id] for statement_id in ORIGINAL_IDS},
        new_rows,
    )
    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "table_sha256_before": EXPECTED_SHA256,
        "original_statement_count": len(ORIGINAL_IDS),
        "p110_mentions_checked": len(segment_mentions),
        "mention_updates": [],
        "existing_statement_changes": [
            {
                "statement_id": statement_id,
                "before": original_projection[statement_id],
                "after": {
                    "subject": by_id[statement_id].get("subject_candidate_id"),
                    "predicate": by_id[statement_id].get("predicate"),
                    "object": by_id[statement_id].get("object_candidate_id"),
                    "relation_candidate": by_id[statement_id].get("qualifiers", {}).get("relation_candidate"),
                    "quote": by_id[statement_id].get("original_quote"),
                },
            }
            for statement_id in sorted(ORIGINAL_IDS)
        ],
        "new_statements": [
            {
                "statement_id": row["statement_id"],
                "subject": row["subject_candidate_id"],
                "predicate": row["predicate"],
                "object": row["object_candidate_id"],
                "relation_candidate": row["qualifiers"]["relation_candidate"],
                "quote": row["original_quote"],
            }
            for row in new_rows
        ],
        "segment_after": expected_segment,
        "global_after": expected_global,
        "backup": f"book-statements.jsonl.{BACKUP_SUFFIX}",
        "candidate_labels_checked": {
            key: candidate_names.get(key)
            for key in sorted(
                endpoint_ids
                | {
                    candidate_id
                    for row in segment_after + new_rows
                    for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
                }
                | {
                    candidate_id
                    for row in new_rows
                    for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
                    if candidate_id
                }
            )
        },
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup = statement_path.with_name(statement_path.name + "." + BACKUP_SUFFIX)
    expected_before = EXPECTED_SHA256[statement_path.name]
    if backup.exists():
        if sha(backup.read_bytes()) != expected_before:
            raise SystemExit(f"apply refused: existing backup differs from prewrite table: {backup.name}")
    else:
        shutil.copy2(statement_path, backup)

    temp_path = statement_path.with_name(statement_path.name + ".tmp-write")
    temp_path.write_bytes(projected_bytes)
    try:
        temp_path.replace(statement_path)
        written = read_jsonl(statement_path)
        actual_global = global_counts(written, len(candidate_ids), mention_count)
        actual_segment = segment_counts([row for row in written if row.get("segment_id") == SEGMENT_ID])
        if actual_global != expected_global or actual_segment != expected_segment:
            raise RuntimeError(f"postwrite mismatch: segment={actual_segment}, global={actual_global}")
    except Exception:
        shutil.copy2(backup, statement_path)
        temp_path.unlink(missing_ok=True)
        raise

    print(json.dumps({
        "apply": "written",
        "backup": backup.name,
        "backup_sha256": sha(backup.read_bytes()),
        "sha256_after": sha(statement_path.read_bytes()),
        "segment_after": actual_segment,
        "global_after": actual_global,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
