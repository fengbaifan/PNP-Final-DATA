#!/usr/bin/env python3
"""Classify and atomize p.111 S2 statements after checking the printed page."""
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
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l139-149"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "fd34c6d6a82174b0ffc5f9393b4de90a32aa47c7a9b1c93d60a4065d35ee293d"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "97a6aacd17f44b45051b9070bdcf111bafe746e205776c0f02e6b8989e98d604",
    "entity-candidates.csv": "01eaae9a76cc32c5a12e78820594517a3382bbea6ac9447c121cd57bd141b1a2",
    "mentions.csv": "e8ce04ae40d08cef4fc2e5c094aebf8be01510c917e7d23b74b20c3e2e6a3516",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l139-149-relations-20261011"
ORIGINAL_IDS = {
    "st-chp4-sec-ii-p111-biographers-describe-testa",
    "st-chp4-sec-ii-p111-cassiano-climate-pressure",
    "st-chp4-sec-ii-p111-cassiano-influence-shared",
    "st-chp4-sec-ii-p111-cassiano-no-claude-mola-rosa-landscapes",
    "st-chp4-sec-ii-p111-cassiano-no-objection",
    "st-chp4-sec-ii-p111-cassiano-takes-up-testa",
    "st-chp4-sec-ii-p111-classical-culture-testa",
    "st-chp4-sec-ii-p111-classical-painting-pressure",
    "st-chp4-sec-ii-p111-lumbroso-reference-to-testa",
    "st-chp4-sec-ii-p111-poussin-landscapes-ideal-content",
    "st-chp4-sec-ii-p111-rosa-character-clientele",
    "st-chp4-sec-ii-p111-rosa-influenced-by-testa",
    "st-chp4-sec-ii-p111-shared-devotional-imagery",
    "st-chp4-sec-ii-p111-testa-arrival-rome",
    "st-chp4-sec-ii-p111-testa-career-cassiano-inspiration",
    "st-chp4-sec-ii-p111-testa-character",
    "st-chp4-sec-ii-p111-testa-clash-insuperable",
    "st-chp4-sec-ii-p111-testa-draws-antiquities",
    "st-chp4-sec-ii-p111-testa-escape-counterfactual",
    "st-chp4-sec-ii-p111-testa-giustiniani-print",
    "st-chp4-sec-ii-p111-testa-imprisonment",
    "st-chp4-sec-ii-p111-testa-landscape-character",
    "st-chp4-sec-ii-p111-testa-patronage-milieu",
    "st-chp4-sec-ii-p111-testa-pictures-lucchese-community",
    "st-chp4-sec-ii-p111-testa-pictures-sacchetti",
    "st-chp4-sec-ii-p111-testa-poussin-friendship",
    "st-chp4-sec-ii-p111-testa-romantic-classicist-tension",
    "st-chp4-sec-ii-p111-testa-suppresses-talent-fragment",
    "st-chp4-sec-ii-p111-testa-tendencies-meet-under-poussin",
}
NEW_IDS = {
    "st-chp4-sec-ii-p111-testa-mola-friendship",
    "st-chp4-sec-ii-p111-testa-native-lucca",
    "st-chp4-sec-ii-p111-testa-buonvisi-pictures",
    "st-chp4-sec-ii-p111-classical-culture-art-advantage",
    "st-chp4-sec-ii-p111-poussin-landscapes-ideal-content-claim",
    "st-chp4-sec-ii-p111-rosa-suffers-from-classical-pressure",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def quote_between(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at) + len(end)
    return text[start_at:end_at]


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


def set_row(
    row: dict,
    *,
    subject: str | None,
    object_: str | None,
    predicate: str,
    claim: str,
    quote: str,
    line_start: int,
    line_end: int,
    relation: bool,
    note: str,
    mentions: list[str],
    qualification: str,
    text_layer: str = "authorial narrative",
    open_endpoint_reason: str | None = None,
    ocr_corrections: list[dict] | None = None,
    related_statement_ids: list[str] | None = None,
) -> None:
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": 22,
        "printed_page_locator": "p.111",
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "mentioned_candidate_ids": mentions,
        "qualification": qualification,
        "relation_candidate": relation,
        "relation_candidate_note": note,
    })
    if open_endpoint_reason is not None:
        q["open_endpoint_reason"] = open_endpoint_reason
    else:
        q.pop("open_endpoint_reason", None)
    if ocr_corrections is not None:
        q["ocr_corrections"] = ocr_corrections
    else:
        q.pop("ocr_corrections", None)
    if related_statement_ids is not None:
        q["related_statement_ids"] = related_statement_ids


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
    relation: bool,
    note: str,
    mentions: list[str],
    qualification: str,
    text_layer: str = "authorial narrative",
    ocr_corrections: list[dict] | None = None,
    related_statement_ids: list[str] | None = None,
) -> dict:
    row = {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": "placeholder",
        "qualifiers": {},
        "original_quote": "placeholder",
        "origin": "book",
        "source_file": SOURCE_REL,
    }
    set_row(
        row, subject=subject, object_=object_, predicate=predicate, claim=claim, quote=quote,
        line_start=line_start, line_end=line_end, relation=relation, note=note,
        mentions=mentions, qualification=qualification, text_layer=text_layer,
        ocr_corrections=ocr_corrections,
        related_statement_ids=related_statement_ids,
    )
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the preflighted p.111 changes")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    for name, expected in EXPECTED_SHA256.items():
        actual = sha((TABLES / name).read_bytes())
        if actual != expected:
            raise SystemExit(f"preflight failed: {name} hash changed: {actual}")
    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source asset hash changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[138:149])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.111 segment text hash changed")

    statements = read_jsonl(statement_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: statement IDs are not unique")
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if {row["statement_id"] for row in segment_rows} != ORIGINAL_IDS:
        raise SystemExit("preflight failed: p.111 original statement set changed")
    if len(segment_rows) != 29 or any(row.get("qualifiers", {}).get("relation_candidate") is not None for row in segment_rows):
        raise SystemExit("preflight failed: p.111 classification state changed")
    if NEW_IDS.intersection(by_id):
        raise SystemExit("preflight failed: a planned p.111 statement ID already exists")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_rows = list(csv.DictReader(handle))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        segment_mentions = [row for row in csv.DictReader(handle) if row["segment_id"] == SEGMENT_ID]
    if len(segment_mentions) != 59:
        raise SystemExit(f"preflight failed: expected 59 p.111 mentions, found {len(segment_mentions)}")
    mention_errors = []
    for row in segment_mentions:
        surface = segment_text[int(row["start_char"]):int(row["end_char"])]
        if surface != row["surface_form"]:
            mention_errors.append(row["mention_id"])
        if row["candidate_id"] not in candidate_ids:
            mention_errors.append(f"{row['mention_id']}:missing-candidate:{row['candidate_id']}")
    if mention_errors:
        raise SystemExit(f"preflight failed: p.111 mention issues: {mention_errors}")

    quote = lambda start, end: quote_between(segment_text, start, end)
    correction_144 = [{"source_line": 144, "source_form": "culture'which", "print_form": "culture, which"}]
    correction_145 = [
        {"source_line": 145, "source_form": "ofhis", "print_form": "of his"},
        {"source_line": 145, "source_form": "character-—landscapes", "print_form": "character—landscapes"},
    ]
    correction_147 = [
        {"source_line": 147, "source_form": "AricTso", "print_form": "And so"},
        {"source_line": 147, "source_form": "ofhis", "print_form": "of his"},
    ]
    updates: dict[str, dict] = {}

    def update(statement_id: str, **values: object) -> None:
        row = by_id[statement_id]
        set_row(row, **values)
        updates[statement_id] = row

    update(
        "st-chp4-sec-ii-p111-biographers-describe-testa",
        subject="cand-2557", object_=None,
        predicate="author_reports_testas_biographers_described_him_as_strange_solitary_melancholy",
        claim="Haskell reports that Testa’s biographers described him as strange, solitary, and melancholy.",
        quote=quote("His biographers all describe him", "strange, solitary and melancholy"),
        line_start=145, line_end=145, relation=False,
        note="Attributed biographical characterization; the biographers are unnamed, and no separate person-to-person relation is asserted.",
        mentions=["cand-2557"],
        qualification="The biographies are not named or independently consulted.",
    )
    update(
        "st-chp4-sec-ii-p111-cassiano-climate-pressure",
        subject="cand-2557", object_="cand-5891",
        predicate="author_suggests_landscape_attitude_may_seem_insufficient_to_testa",
        claim="Haskell suggests that the apparently frivolous landscape attitude may have seemed insufficient in Cassiano’s intellectual climate, especially to the sensitive and self-conscious Testa, more than to his patron.",
        quote=quote("In the intense intellectual climate", "Testa than to his patron."),
        line_start=145, line_end=146, relation=True,
        note="This is a qualified interpretive link between Testa and the landscape attitude; Cassiano’s intellectual climate is context, and the sentence does not say that Cassiano objected.",
        mentions=["cand-2557", "cand-5891", "cand-2036", "cand-5885"],
        qualification="Haskell’s ‘may well’ and ‘more to’ remain explicit; the relative sensitivity is his interpretation.",
    )
    update(
        "st-chp4-sec-ii-p111-cassiano-influence-shared",
        subject="cand-2036", object_="cand-5908",
        predicate="author_traces_cassiano_influence_on_shared_testa_poussin_direction",
        claim="Haskell says Cassiano’s influence can be traced in the shared movement of Testa and Poussin toward private devotional imagery.",
        quote=quote("And here surely", "influence of Cassiano."),
        line_start=140, line_end=140, relation=True,
        note="The paired endpoint represents the preceding ‘both artists’ reference to Testa and Poussin; Haskell attributes their shared direction to Cassiano’s influence, without asserting a commission or collaboration.",
        mentions=["cand-2036", "cand-5908", "cand-5885"],
        qualification="‘Surely’ is Haskell’s interpretive emphasis; the paired endpoint is a source referent, not a collaborative entity.",
    )
    update(
        "st-chp4-sec-ii-p111-cassiano-no-claude-mola-rosa-landscapes",
        subject="cand-2036", object_=None,
        predicate="author_says_cassiano_evidently_owned_no_landscapes_by_named_artists",
        claim="Haskell says Cassiano evidently owned no landscape by Claude, Pier Francesco Mola, or Salvator Rosa.",
        quote=quote("he evidently owned no landscape by Claude", "Salvator Rosa."),
        line_start=148, line_end=149, relation=True,
        note="This is an attributed negative collection-holding relation; no individual landscape or bounded work group is identified, and ‘evidently’ remains Haskell’s qualification.",
        mentions=["cand-2036", "cand-3481", "cand-2557", "cand-1676", "cand-2258"],
        qualification="Footnote 2 commentary; Haskell’s claim is not independently checked against a collection catalogue.",
        text_layer="footnote commentary",
        open_endpoint_reason="The named painters are identified, but no individual landscape or bounded set of works is named; keep the object endpoint open.",
    )
    update(
        "st-chp4-sec-ii-p111-cassiano-no-objection",
        subject="cand-2036", object_=None,
        predicate="author_says_little_evidence_cassiano_objected_to_landscape_themes",
        claim="Haskell says there is little reason to believe Cassiano objected to these landscape themes.",
        quote=quote("Indeed there is little reason to believe", "objected to such themes."),
        line_start=146, line_end=146, relation=False,
        note="This is a qualified statement about the limits of evidence; it does not assert that Cassiano approved, commissioned, or definitively did not object to the themes.",
        mentions=["cand-2036", "cand-5891", "cand-2557"],
        qualification="The negative is epistemic (‘little reason to believe’), not a confirmed statement of Cassiano’s attitude.",
    )
    update(
        "st-chp4-sec-ii-p111-cassiano-takes-up-testa",
        subject="cand-2036", object_="cand-2557",
        predicate="cassiano_took_up_testa_early_in_his_career",
        claim="Haskell says Cassiano took Testa up quite early in Testa’s career.",
        quote=quote("was taken up quite early in his career by Cassiano." , "was taken up quite early in his career by Cassiano."),
        line_start=142, line_end=142, relation=True,
        note="The source reports a patronage or support connection; ‘took up’ is retained without specifying a commission, employment, or particular work.",
        mentions=["cand-2036", "cand-2557"],
        qualification="This is an S2 relation candidate, not a formal S6 relation.",
    )
    update(
        "st-chp4-sec-ii-p111-classical-culture-testa",
        subject="cand-2557", object_="cand-5886",
        predicate="testa_acquired_classical_culture_through_antiquarian_work",
        claim="Haskell says Testa acquired a vast classical culture through his antiquarian drawing work.",
        quote=quote("and thereby acquired a vast classical culture", "and thereby acquired a vast classical culture"),
        line_start=144, line_end=144, relation=True,
        note="The source explicitly links Testa’s antiquarian work to the acquisition of classical learning; the separate assessment of its benefit to his art is recorded apart.",
        mentions=["cand-2557", "cand-5884", "cand-5666", "cand-5886"],
        qualification="The acquisition is Haskell’s account; no external biographical verification is implied.",
    )
    update(
        "st-chp4-sec-ii-p111-classical-painting-pressure",
        subject="cand-5894", object_=None,
        predicate="author_says_pressure_for_classical_painting_was_strong_in_art_theory",
        claim="Haskell says pressure in favour of classical painting was always strong wherever art theory was discussed.",
        quote=quote("Yet the pressures in favour of classical painting", "theory of art was discussed."),
        line_start=146, line_end=146, relation=False,
        note="This is a general claim about the strength of an art-theoretical pressure; no particular person, institution, or bounded group is identified as its agent.",
        mentions=["cand-5894"],
        qualification="Broad authorial generalization; no specific theorist or institution is named.",
    )
    update(
        "st-chp4-sec-ii-p111-lumbroso-reference-to-testa",
        subject="cand-2036", object_="cand-2557",
        predicate="cassiano_made_one_passing_reference_to_testa_as_reported_by_haskell",
        claim="Haskell reports that Cassiano made one passing reference to Testa and locates it at Lumbroso page 196.",
        quote=quote("though Cassiano made one passing reference", "Lumbroso, p. 196)"),
        line_start=148, line_end=148, relation=True,
        note="The reported act of reference links Cassiano and Testa; Lumbroso p.196 is only Haskell’s locator and has not been independently consulted.",
        mentions=["cand-2036", "cand-2557", "cand-5626", "cand-5907"],
        qualification="Footnote 2 commentary; this records Haskell’s report, not direct inspection of Lumbroso.",
        text_layer="footnote commentary",
    )
    update(
        "st-chp4-sec-ii-p111-poussin-landscapes-ideal-content",
        subject="cand-5893", object_="cand-2036",
        predicate="poussin_painted_unspecified_landscapes_for_cassiano",
        claim="Haskell says Poussin painted some unspecified landscapes for Cassiano.",
        quote=quote("Some of the landscapes that Poussin painted for him", "Some of the landscapes that Poussin painted for him"),
        line_start=146, line_end=146, relation=True,
        note="The quoted clause directly reports that Poussin painted the landscape group for Cassiano; the author’s assessment of their ideal content is separated.",
        mentions=["cand-5893", "cand-1984", "cand-2036"],
        qualification="No individual landscape is identified; ‘some’ limits the group.",
    )
    update(
        "st-chp4-sec-ii-p111-rosa-character-clientele",
        subject="cand-2258", object_=None,
        predicate="author_compares_rosa_as_tougher_and_with_wider_clientele_than_testa",
        claim="Haskell says Rosa was a tougher character than Testa and had a much wider clientele despite his incessant grumbling.",
        quote=quote("but for all his incessant grumbling", "much wider clientele."),
        line_start=146, line_end=146, relation=False,
        note="This is Haskell’s comparative characterization of Rosa; it is not a relationship claim with an identified clientele group.",
        mentions=["cand-2258", "cand-2557"],
        qualification="Comparative characterization by Haskell.",
    )
    update(
        "st-chp4-sec-ii-p111-rosa-influenced-by-testa",
        subject="cand-2258", object_="cand-5887",
        predicate="rosa_was_probably_influenced_by_testas_romantic_views",
        claim="Haskell says Salvator Rosa was probably influenced by Testa’s romantic views.",
        quote=quote("Salvator Rosa, himself probably influenced by", "romantic views"),
        line_start=146, line_end=146, relation=True,
        note="This is an explicitly qualified influence relation; the following claim that Rosa suffered from conflicts is recorded separately.",
        mentions=["cand-2258", "cand-5887", "cand-2557"],
        qualification="‘Probably’ is retained as Haskell’s interpretation.",
    )
    update(
        "st-chp4-sec-ii-p111-shared-devotional-imagery",
        subject="cand-2557", object_="cand-1984",
        predicate="haskell_links_testa_and_poussin_by_shared_devotional_direction",
        claim="Haskell says Testa’s and Poussin’s work shared a movement away from ordinary expressions of religious emotion toward private devotional imagery.",
        quote=quote("work of both artists", "to a private devotional imagery."),
        line_start=140, line_end=140, relation=True,
        note="The paired artists share an interpreted artistic direction; this does not assert collaboration or a formal relationship between the artists.",
        mentions=["cand-5908", "cand-2557", "cand-1984", "cand-5885"],
        qualification="Continues the p.110 sentence; ‘both artists’ refers to Testa and Poussin in context.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-arrival-rome",
        subject="cand-2557", object_="cand-4490",
        predicate="testa_came_to_rome_from_lucca_before_1630",
        claim="Haskell says Testa came to Rome from his native Lucca in his early twenties, sometime before 1630.",
        quote=quote("He had come to Rome", "sometime before 1630"),
        line_start=142, line_end=142, relation=True,
        note="This records Rome as the destination; the source’s stated Lucca origin is recorded as a separate location relation.",
        mentions=["cand-2557", "cand-4490", "cand-1454"],
        qualification="‘Early twenties’ and ‘sometime before 1630’ are approximate source dates; no birth year is calculated.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-career-cassiano-inspiration",
        subject="cand-2557", object_=None,
        predicate="author_evaluates_testas_career_as_illustrating_cassianos_inspiration",
        claim="Haskell says Testa’s tragic career illustrates the fascination and power of Cassiano’s inspiration.",
        quote=quote("Testa, in fact", "power of Cassiano’s inspiration."),
        line_start=141, line_end=141, relation=False,
        note="This is Haskell’s rhetorical evaluation of Testa’s career, not an independent causal relation; the explicit influence claim about shared imagery is recorded separately.",
        mentions=["cand-2557", "cand-2036"],
        qualification="Evaluative framing by Haskell; it does not independently establish how Cassiano influenced Testa.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-character",
        subject="cand-2557", object_=None,
        predicate="author_describes_testa_as_stubborn_proud_self_educated_and_independent",
        claim="Haskell describes Testa as stubborn, proud, self-educated, and independent in his views.",
        quote=quote("Like his close friend", "independent views."),
        line_start=141, line_end=142, relation=False,
        note="Attributed character traits, not a relation to Poussin; the preceding words identify Poussin as Testa’s close friend.",
        mentions=["cand-2557", "cand-1984"],
        qualification="Characterization is Haskell’s account; footnote 1 points to Marabottini (1954), not independently consulted here.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-clash-insuperable",
        subject="cand-2557", object_=None,
        predicate="author_says_classical_romantic_clash_seemed_insuperable_for_testa",
        claim="Haskell says the clash between Testa’s romantic temperament and acquired classicism seemed insuperable for him.",
        quote=quote("For Testa the clash", "insuperable."),
        line_start=146, line_end=146, relation=False,
        note="This is an evaluative conclusion about the difficulty of Testa’s artistic conflict, not a separate relation between two entities.",
        mentions=["cand-2557", "cand-5887", "cand-5888", "cand-5894"],
        qualification="‘Seems’ preserves Haskell’s qualification.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-draws-antiquities",
        subject="cand-2557", object_="cand-5884",
        predicate="testa_was_set_to_draw_antiquities_for_paper_museum",
        claim="Haskell says Testa was set to work drawing antiquities for Cassiano’s paper museum.",
        quote=quote("He was set to work drawing antiquities", "paper museum"),
        line_start=143, line_end=144, relation=True,
        note="The source links Testa’s drawing work to the paper museum; its passive wording does not identify who assigned the work, and no direct commission by Cassiano is inferred.",
        mentions=["cand-2557", "cand-5884", "cand-5666", "cand-2036"],
        qualification="The individual drawings are not identified; the museum is Cassiano’s in the surrounding context.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-escape-counterfactual",
        subject="cand-2557", object_="cand-2036",
        predicate="author_suggests_testa_might_have_done_better_to_escape_patron",
        claim="Haskell suggests Testa might have done better to escape from his excessively benevolent but oppressive patron.",
        quote=quote("He might perhaps have done better", "oppressive patron."),
        line_start=146, line_end=146, relation=True,
        note="This is a counterfactual relation candidate about leaving the patron; it is not a claim that Testa escaped or that doing so would actually have improved his career.",
        mentions=["cand-2557", "cand-2036"],
        qualification="‘Might perhaps’ and the evaluative description of the patron remain attributed to Haskell.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-giustiniani-print",
        subject="cand-2557", object_="cand-5881",
        predicate="testa_made_a_drawing_for_a_galleria_giustiniani_print",
        claim="Haskell says Testa made a drawing for one of the prints of the Galleria Giustiniani.",
        quote=quote("He made a drawing", "Galleria Giustiniani,"),
        line_start=142, line_end=142, relation=True,
        note="The source identifies one print in the Galleria Giustiniani series or publication but does not give its individual subject or exact bibliographic identity.",
        mentions=["cand-2557", "cand-5881"],
        qualification="No individual print is identified.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-imprisonment",
        subject="cand-2557", object_="cand-5895",
        predicate="testa_attempted_to_escape_and_was_imprisoned_for_contract_breach",
        claim="Haskell says Testa once tried to escape and was imprisoned for breach of contract.",
        quote=quote("On one occasion he tried to do so", "breach of contract."),
        line_start=146, line_end=146, relation=True,
        note="This links Testa to the reported imprisonment event; the source does not say Cassiano caused the imprisonment.",
        mentions=["cand-2557", "cand-2036", "cand-5895"],
        qualification="Footnote 3 points to Testa’s letters from prison, which are not independently consulted here.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-landscape-character",
        subject="cand-2557", object_="cand-5891",
        predicate="testas_landscapes_reflected_his_melancholic_character",
        claim="Haskell says Testa’s more attractive paintings reflected this side of his character, especially landscapes with threatening winds and small Old Testament or mythological figures sheltering or resting.",
        quote=quote("and his more attractive paintings reflect", "relaxing in the sun."),
        line_start=145, line_end=145, relation=True,
        note="This is Haskell’s interpretive link between Testa’s character and a generalized landscape group; no individual painting or depicted figure is identified.",
        mentions=["cand-2557", "cand-5891", "cand-5892", "cand-5890", "cand-5889"],
        qualification="The passage generalizes about attractive landscapes; it does not identify a specific work or prove direct Titian influence.",
        ocr_corrections=correction_145,
    )
    update(
        "st-chp4-sec-ii-p111-testa-patronage-milieu",
        subject="cand-2557", object_="cand-5879",
        predicate="testa_entered_orbit_of_private_connoisseurs_in_rome",
        claim="Haskell says Testa entered the orbit of private connoisseurs rather than major church patrons.",
        quote=quote("and had at once drifted into the orbit", "great patrons of the church."),
        line_start=142, line_end=142, relation=True,
        note="The positive endpoint is the private-connoisseur milieu; the contrast with church patrons does not prove that Testa had no contact with any church patron.",
        mentions=["cand-2557", "cand-5879", "cand-5880"],
        qualification="The collective categories remain broad; individual patrons are not named in this sentence.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-pictures-lucchese-community",
        subject="cand-2557", object_="cand-5882",
        predicate="testa_painted_pictures_for_members_of_rome_lucchese_community",
        claim="Haskell says Testa painted pictures for members of the Lucchese community in Rome.",
        quote=quote("members of the Lucchese community in Rome", "members of the Lucchese community in Rome"),
        line_start=142, line_end=142, relation=True,
        note="The statement records the named community as a recipient group; the separately emphasized Buonvisi group is recorded in its own statement.",
        mentions=["cand-2557", "cand-5882", "cand-4490", "cand-5883"],
        qualification="Individual community members are not identified.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-pictures-sacchetti",
        subject="cand-2557", object_="cand-2314",
        predicate="testa_painted_pictures_for_marcello_sacchetti",
        claim="Haskell says Testa painted pictures for Marcello Sacchetti.",
        quote=quote("painted pictures for Marcello Sacchetti", "painted pictures for Marcello Sacchetti"),
        line_start=142, line_end=142, relation=True,
        note="The source reports the patronage or recipient connection but does not identify the pictures individually or establish a formal commission.",
        mentions=["cand-2557", "cand-2314"],
        qualification="The works are not individually identified.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-poussin-friendship",
        subject="cand-2557", object_="cand-1984",
        predicate="haskell_identifies_poussin_as_testas_close_friend",
        claim="Haskell identifies Poussin as Testa’s close friend.",
        quote=quote("Like his close friend", "Poussin"),
        line_start=141, line_end=142, relation=True,
        note="This is an explicit source-attributed friendship claim.",
        mentions=["cand-2557", "cand-1984"],
        qualification="The relation is attributed to Haskell; its period and independent corroboration are not established here.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-romantic-classicist-tension",
        subject="cand-2557", object_="cand-5888",
        predicate="haskell_says_testa_could_not_fuse_romantic_temperament_with_classicism",
        claim="Haskell says Testa could not fuse a romantic temperament with intellectually acquired classicism to intensify his recreation of antique myths.",
        quote=quote("For, unlike Poussin, Testa could not fuse", "recreation of antique myths."),
        line_start=144, line_end=144, relation=True,
        note="The source explicitly describes an inability to combine two artistic tendencies; this is Haskell’s interpretive relationship, not a measurable property or formal relation between artists.",
        mentions=["cand-2557", "cand-1984", "cand-5887", "cand-5888", "cand-5889"],
        qualification="Comparative art-historical judgment by Haskell.",
    )
    update(
        "st-chp4-sec-ii-p111-testa-suppresses-talent-fragment",
        subject="cand-2557", object_=None,
        predicate="author_says_testa_suppressed_a_natural_aspect_of_his_talent",
        claim="Haskell says Testa set about suppressing what he regarded as the most natural aspect of his talent to concentrate on ideas he misguidedly thought would appeal to Cassiano’s learned circle.",
        quote=quote("AricTso", "would most appeal to"),
        line_start=147, line_end=147, relation=False,
        note="The p.111 fragment attributes an interpretive change in Testa’s practice; the sentence’s endpoint continues onto p.112, and this fragment alone does not establish a distinct relation to an identified idea or group.",
        mentions=["cand-2557", "cand-2036"],
        qualification="‘Misguidedly’ remains Haskell’s characterization; the continuation to ‘Cassiano’s learned circle’ is linked to p.112.",
        ocr_corrections=correction_147,
    )
    update(
        "st-chp4-sec-ii-p111-testa-tendencies-meet-under-poussin",
        subject="cand-2557", object_="cand-1984",
        predicate="testas_opposing_tendencies_met_rarely_under_poussins_impact",
        claim="Haskell says Testa’s opposing tendencies rarely met to good purpose, chiefly when Testa was under Poussin’s direct impact.",
        quote=quote("In him these opposing tendencies", "under the direct impact of Poussin."),
        line_start=144, line_end=144, relation=True,
        note="This is an explicitly qualified influence relation in Haskell’s interpretation; it does not establish a formal teacher-pupil relation.",
        mentions=["cand-2557", "cand-1984", "cand-5887", "cand-5888"],
        qualification="‘Rarely’ and ‘chiefly’ limit the claim.",
    )

    # Add atomic claims that were obscured by compound or incomplete first-pass statements.
    additions = [
        make_statement(
            "st-chp4-sec-ii-p111-testa-mola-friendship",
            subject="cand-2557", object_="cand-1676", predicate="haskell_identifies_mola_as_testas_friend",
            claim="Haskell identifies Pier Francesco Mola as Testa’s friend.",
            quote=quote("Testa’s friend", "Pier Francesco Mola"), line_start=148, line_end=148,
            relation=True,
            note="The footnote explicitly identifies Mola as Testa’s friend; this is separate from its claim that Cassiano evidently owned no landscape by Mola.",
            mentions=["cand-2557", "cand-1676"],
            qualification="Footnote 2 commentary; the friendship is reported by Haskell and not independently verified here.",
            text_layer="footnote commentary",
        ),
        make_statement(
            "st-chp4-sec-ii-p111-testa-native-lucca",
            subject="cand-2557", object_="cand-1454", predicate="haskell_identifies_lucca_as_testas_native_place",
            claim="Haskell identifies Lucca as Testa’s native place.",
            quote=quote("from his native Lucca", "from his native Lucca"), line_start=142, line_end=142,
            relation=True,
            note="The clause names Lucca as Testa’s native place; this is separated from the destination Rome and approximate arrival date.",
            mentions=["cand-2557", "cand-1454"],
            qualification="This records the source’s statement, not an independently verified birthplace or residence record.",
            related_statement_ids=["st-chp4-sec-ii-p111-testa-arrival-rome"],
        ),
        make_statement(
            "st-chp4-sec-ii-p111-testa-buonvisi-pictures",
            subject="cand-2557", object_="cand-5883", predicate="testa_painted_pictures_for_buonvisi_members",
            claim="Haskell singles out the Buonvisi as especially notable among the Lucchese community members for whom Testa painted pictures.",
            quote=quote("especially the Buonvisi", "especially the Buonvisi"), line_start=142, line_end=142,
            relation=True,
            note="The source emphasizes the Buonvisi within the Lucchese community; no individual family member or family boundary is inferred.",
            mentions=["cand-2557", "cand-5883", "cand-5882"],
            qualification="The group’s membership and individual recipients are not identified.",
            related_statement_ids=["st-chp4-sec-ii-p111-testa-pictures-lucchese-community"],
        ),
        make_statement(
            "st-chp4-sec-ii-p111-classical-culture-art-advantage",
            subject="cand-2557", object_=None, predicate="author_says_classical_culture_only_occasionally_benefited_testas_art",
            claim="Haskell says Testa’s acquired classical culture only occasionally proved advantageous to his art.",
            quote=quote("culture'which", "advantage to his art."),
            line_start=144, line_end=144, relation=False,
            note="This is Haskell’s scalar assessment of the usefulness of Testa’s learning, not a separately identified relation to a work or bounded class of works.",
            mentions=["cand-2557", "cand-5886"],
            qualification="The assessment remains attributed to Haskell; ‘only occasionally’ is retained.",
            ocr_corrections=correction_144,
            related_statement_ids=["st-chp4-sec-ii-p111-classical-culture-testa"],
        ),
        make_statement(
            "st-chp4-sec-ii-p111-poussin-landscapes-ideal-content-claim",
            subject="cand-5893", object_=None, predicate="author_says_some_poussin_landscapes_had_little_ideal_content",
            claim="Haskell says some Poussin landscapes for Cassiano had little more ideal content despite their more solid intellectual construction.",
            quote=quote("though constructed on much more solid intellectual principles", "have little more ideal content."),
            line_start=146, line_end=146, relation=False,
            note="This records Haskell’s comparative assessment of the landscapes’ ideal content; the separate work-for-Cassiano relation is recorded in its own statement.",
            mentions=["cand-5893", "cand-1984", "cand-2036", "cand-5894", "cand-5891"],
            qualification="‘Some’ limits the group; ‘little more’ is Haskell’s comparison with the preceding landscape discussion, not an objective measurement.",
            related_statement_ids=["st-chp4-sec-ii-p111-poussin-landscapes-ideal-content"],
        ),
        make_statement(
            "st-chp4-sec-ii-p111-rosa-suffers-from-classical-pressure",
            subject="cand-2258", object_="cand-5894", predicate="rosa_suffered_from_conflicts_over_classical_painting_pressure",
            claim="Haskell says Rosa suffered bitterly from conflicts associated with the pressure favouring classical painting in art-theory discussions.",
            quote=quote("suffered bitterly from such conflicts", "suffered bitterly from such conflicts"),
            line_start=146, line_end=146, relation=True,
            note="‘Such conflicts’ refers to the preceding pressure in favour of classical painting and Testa’s romantic views; no specific opponent or episode is identified.",
            mentions=["cand-2258", "cand-5894", "cand-5887", "cand-2557"],
            qualification="The relation is Haskell’s account; its precise historical circumstances are not specified.",
            related_statement_ids=["st-chp4-sec-ii-p111-rosa-influenced-by-testa", "st-chp4-sec-ii-p111-classical-painting-pressure"],
        ),
    ]

    if set(updates) != ORIGINAL_IDS or len(additions) != len(NEW_IDS) or {r["statement_id"] for r in additions} != NEW_IDS:
        raise SystemExit("preflight failed: planned statement set is incomplete")
    endpoint_ids = {
        candidate
        for row in [*updates.values(), *additions]
        for candidate in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        if candidate
    }
    if endpoint_ids - candidate_ids:
        raise SystemExit(f"preflight failed: endpoint candidates are missing: {sorted(endpoint_ids - candidate_ids)}")
    preview_rows = [*updates.values(), *additions]
    if any(row["segment_id"] != SEGMENT_ID or row.get("origin") != "book" for row in additions):
        raise SystemExit("preflight failed: addition source metadata is invalid")
    if any(not row.get("original_quote") or row["original_quote"] not in segment_text for row in preview_rows):
        bad = [row["statement_id"] for row in preview_rows if not row.get("original_quote") or row["original_quote"] not in segment_text]
        raise SystemExit(f"preflight failed: a quote is not reproducible from p.111 source segment: {bad}")

    patched = []
    for row in statements:
        if row["statement_id"] in updates:
            patched.append(updates[row["statement_id"]])
        else:
            patched.append(row)
    patched.extend(additions)
    post_target = [row for row in patched if row.get("segment_id") == SEGMENT_ID]
    counts = segment_counts(post_target)
    if counts != {"statements": 35, "dual": 24, "relation_true": 25, "relation_false": 10,
                  "dual_true": 24, "dual_false": 0, "unclassified": 0}:
        raise SystemExit(f"preflight failed: unexpected p.111 post-counts: {counts}")

    output = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in patched).encode("utf-8")
    print("P.111 S2 preview (printed page 111 / PDF physical page 22)")
    print("source: 04_CHP-4_sec_ii.md L139–149; PDF page inspected against original scan")
    print(f"mentions checked: {len(segment_mentions)} exact spans; all candidates and endpoints resolve")
    print(f"existing statements refined: {len(updates)}; atomic statements added: {len(additions)}")
    print(f"segment classification: {counts}")
    for row in sorted(preview_rows, key=lambda item: item["statement_id"]):
        q = row["qualifiers"]
        label = "RELATION" if q["relation_candidate"] else "NONRELATION"
        print(f"{label:12} {row['statement_id']} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {q['claim']}")
    print(f"post-write statement count: {len(patched)}; new file SHA-256: {sha(output)}")
    if not args.apply:
        print("dry-run only; no table was written")
        return

    backup = statement_path.with_name(statement_path.name + "." + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"apply refused: recovery copy already exists: {backup.name}")
    if sha(statement_path.read_bytes()) != EXPECTED_SHA256["book-statements.jsonl"]:
        raise SystemExit("apply refused: book-statements changed after preflight")
    shutil.copy2(statement_path, backup)
    if sha(backup.read_bytes()) != EXPECTED_SHA256["book-statements.jsonl"]:
        raise SystemExit("apply refused: backup does not match the pre-write statements table")
    temp = statement_path.with_name(statement_path.name + "." + BACKUP_SUFFIX + ".tmp")
    try:
        temp.write_bytes(output)
        temp.replace(statement_path)
        written = read_jsonl(statement_path)
        written_target = [row for row in written if row.get("segment_id") == SEGMENT_ID]
        if len(written) != len(patched) or segment_counts(written_target) != counts:
            raise RuntimeError("post-write count validation failed")
        if any(row["original_quote"] not in segment_text for row in written_target):
            raise RuntimeError("post-write quote validation failed")
        if sha(statement_path.read_bytes()) != sha(output):
            raise RuntimeError("post-write hash validation failed")
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(backup, statement_path)
        raise
    print(f"applied: {statement_path.relative_to(ROOT)}")
    print(f"recovery copy: {backup.relative_to(ROOT)} (pre-write SHA-256 {sha(backup.read_bytes())})")


if __name__ == "__main__":
    main()
