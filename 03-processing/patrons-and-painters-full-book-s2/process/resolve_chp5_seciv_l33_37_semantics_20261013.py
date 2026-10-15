#!/usr/bin/env python3
"""Guarded S2 semantic review for chapter 5, printed page 145, lines 33-37."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iv.md"
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l33-37"
SOURCE_SEGMENT_SHA = "0540efc47bd2dfba10c88798fe500c2804a8f4446f96857a6118f715f5c1f10f"
ASSET_SHA = "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f"
EXPECTED_HASHES = {
    "book-statements.jsonl": "1790f380a481300370291a604bdd01c35626ac871b129581e34dde371db85550",
    "entity-candidates.csv": "fb54c848b0ebfb35cae48d333cef58fd6505b4bae2581ce0406dd3029ed65a27",
    "mentions.csv": "6049e7c44579b82a1e74fdb2d6374c8af5c7b445c383fb787084ac5c0e4da5c7",
    "s2-coverage.csv": "e21320b8517801461bfaf18667f4c4831e1bb805d389d9523620bdc381acd43d",
}
BACKUP_SUFFIX = ".bak-s2-chp5-seciv-l33-37-20261013"
MISSING = object()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes")
    args = parser.parse_args()

    for name, expected in EXPECTED_HASHES.items():
        actual = digest(TABLES / name)
        if actual != expected:
            raise SystemExit(f"Refusing: {name} changed; current SHA-256 is {actual}")

    segments = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SOURCE_SEGMENT_SHA:
        raise SystemExit("Refusing: S0 segment fingerprint changed or is missing")
    if segment.get("asset_sha256") != ASSET_SHA:
        raise SystemExit("Refusing: source asset fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[32:37])

    def line(n: int) -> str:
        return source_lines[n - 1]

    def quote_between(start: str, end: str) -> str:
        a = segment_text.index(start)
        b = segment_text.index(end, a) + len(end)
        return segment_text[a:b]

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    coverage_path = TABLES / "s2-coverage.csv"
    statements = read_jsonl(statement_path)
    candidate_fields, candidates = read_csv(candidate_path)
    mention_fields, mentions = read_csv(mention_path)
    coverage_fields, coverage = read_csv(coverage_path)
    all_rows = {row["statement_id"]: row for row in statements}

    target_ids = {
        "st-chp5-p145-giordano-three-brushes-audience-metaphor",
        "st-chp5-p145-haskell-asks-whether-ricciardi-shared-rosa-enthusiasm",
        "st-chp5-p145-haskell-questions-ricciardi-appreciation",
        "st-chp5-p145-haskell-speculates-about-quality-in-humble-dwellings",
        "st-chp5-p145-passeri-pictures-found-in-homes-of-different-status",
        "st-chp5-p145-ricciardi-could-not-offer-personal-patronage",
        "st-chp5-p145-ricciardi-letters-not-survived",
        "st-chp5-p145-rosa-career-success-and-isolation",
        "st-chp5-p145-rosa-frequently-confused-with-bamboccianti",
        "st-chp5-p145-rosa-friendship-and-doubts-about-ricciardi-judgment",
        "st-chp5-p145-rosa-launched-onslaught-to-impose-serious-artist-image",
        "st-chp5-p145-rosa-letter-at-terni-waterfall",
        "st-chp5-p145-rosa-letter-disagreed-about-little-picture",
        "st-chp5-p145-rosa-looked-beyond-select-patronage-circles",
    }
    target = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    row_by_id = {row["statement_id"]: row for row in target}
    if len(target) != 14 or set(row_by_id) != target_ids:
        raise SystemExit(f"Refusing: expected the reviewed 14-row target set, found {len(target)}")
    if any(row.get("qualifiers", {}).get("relation_candidate") in (True, False) for row in target):
        raise SystemExit("Refusing: the expected 14 target statements are no longer all unclassified")
    for row in target:
        if row.get("original_quote") and row["original_quote"] not in segment_text:
            raise SystemExit(f"Refusing: existing quote outside S0 segment: {row['statement_id']}")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    expected_new_candidates = {"cand-11950", "cand-11951", "cand-11952", "cand-11953"}
    if expected_new_candidates & set(candidate_by_id):
        raise SystemExit("Refusing: one or more planned candidate IDs already exist")
    numeric_ids = [int(row["candidate_id"].split("-")[1]) for row in candidates]
    if max(numeric_ids) != 11949:
        raise SystemExit(f"Refusing: candidate sequence changed; current max is {max(numeric_ids)}")

    new_candidates = [
        {
            "candidate_id": "cand-11950",
            "index_entry_id": "",
            "canonical_name": "Unidentified picture condemned by Ricciardi and judged least bad by Salvator Rosa",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "The wording distinguishes this picture from the little picture first described as Florentine by Ricciardi and Flemish by Rosa. Its title, maker, and identity are not given.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L35",
        },
        {
            "candidate_id": "cand-11951",
            "index_entry_id": "",
            "canonical_name": "Unspecified group of Salvator Rosa pictures reported in houses of varying social status",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Passeri, as quoted by Haskell, says Rosa's pictures appeared in houses belonging to gentlemen and princes and to people of mediocre status. No individual pictures or houses are identified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L36",
        },
        {
            "candidate_id": "cand-11952",
            "index_entry_id": "",
            "canonical_name": "Elevated moral and poetic qualities sought by Salvator Rosa (Haskell's wording)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Abstract qualities are described by Haskell as rejected by the Bamboccianti and sought by Rosa; the source does not enumerate or define them further.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L36",
        },
        {
            "candidate_id": "cand-11953",
            "index_entry_id": "",
            "canonical_name": "Most of Salvator Rosa's fellow artists (unnamed group)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Rosa was contemptuous of most of his fellow artists; no members or exact group boundaries are supplied.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L36",
        },
    ]
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    def configure(
        statement_id: str,
        *,
        relation: bool,
        relation_note: str,
        claim: str | object = MISSING,
        subject: str | None | object = MISSING,
        obj: str | None | object = MISSING,
        predicate: str | None = None,
        original_quote: str | None = None,
        open_reason: str | None = None,
        updates: dict | None = None,
        remove: tuple[str, ...] = (),
    ) -> None:
        row = all_rows[statement_id]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = relation_note
        if claim is not MISSING:
            q["claim"] = claim
        if relation and open_reason:
            q["open_endpoint_reason"] = open_reason
        elif not relation:
            q.pop("open_endpoint_reason", None)
        if subject is not MISSING:
            row["subject_candidate_id"] = subject
        if obj is not MISSING:
            row["object_candidate_id"] = obj
        if predicate:
            row["predicate"] = predicate
        if original_quote is not None:
            row["original_quote"] = original_quote
        for key in remove:
            q.pop(key, None)
        if updates:
            q.update(updates)

    configure(
        "st-chp5-p145-giordano-three-brushes-audience-metaphor",
        relation=True,
        relation_note="This preserves De Dominici's source-attributed metaphor about Giordano and named audience classes. It is not treated as literal brush use or as a verified practice of Rosa.",
        subject="cand-1172",
        obj=None,
        predicate="reported_metaphor_of_three_brushes_for_audiences",
        open_reason="The quote names audience classes rather than independently identified people or organizations; their exact membership is unspecified.",
        updates={
            "relation_participants": ["nobility", "private citizens", "populace"],
            "mentioned_candidate_ids": ["cand-1172", "cand-2236"],
        },
    )
    configure(
        "st-chp5-p145-haskell-asks-whether-ricciardi-shared-rosa-enthusiasm",
        relation=False,
        relation_note="This is Haskell's unanswered rhetorical question, not a reported response by Ricciardi.",
        subject=None,
        obj=None,
        updates={"mentioned_candidate_ids": ["cand-2187", "cand-2236"]},
    )
    configure(
        "st-chp5-p145-haskell-questions-ricciardi-appreciation",
        relation=False,
        relation_note="This is Haskell's evaluative inference from Ricciardi's literary work, not evidence of a specific interaction or event between the two men.",
        subject=None,
        obj=None,
        updates={"mentioned_candidate_ids": ["cand-2187", "cand-2236"]},
    )
    configure(
        "st-chp5-p145-haskell-speculates-about-quality-in-humble-dwellings",
        relation=False,
        relation_note="This is Haskell's qualified speculation about picture quality and Rosa's likely reaction, not a relation between independently identified entities.",
        subject=None,
        updates={
            "work_group_candidate_id": "cand-11951",
            "mentioned_candidate_ids": ["cand-2236", "cand-11951"],
        },
    )
    configure(
        "st-chp5-p145-passeri-pictures-found-in-homes-of-different-status",
        relation=True,
        relation_note="The reported works are the relational subject; Passeri is the cited source and Rosa is their artist, not the work endpoint.",
        subject="cand-11951",
        obj=None,
        predicate="reported_seen_in_houses_of_varying_social_status",
        open_reason="The source gives classes of house owners but identifies no particular houses or bounded set of residences.",
        updates={
            "artist_candidate_id": "cand-2236",
            "source_author_candidate_id": "cand-1856",
            "social_category_candidate_id": "cand-6238",
            "mentioned_candidate_ids": ["cand-1856", "cand-2236", "cand-6238", "cand-11951"],
        },
    )
    configure(
        "st-chp5-p145-ricciardi-could-not-offer-personal-patronage",
        relation=True,
        relation_note="Haskell explicitly links Ricciardi's residence in a different town to his inability to provide the personal patronage Rosa wanted; no city is supplied.",
        predicate="could_not_provide_personal_patronage_from_other_town",
        updates={"mentioned_candidate_ids": ["cand-2187", "cand-2236"]},
    )
    configure(
        "st-chp5-p145-ricciardi-letters-not-survived",
        relation=False,
        relation_note="This is Haskell's report about the survival of Ricciardi's letters; Rosa's trust is split into a separate relation statement.",
        subject=None,
        original_quote=quote_between("As his letters have not survived", "As his letters have not survived"),
        claim="Haskell says Ricciardi's letters have not survived.",
        updates={"mentioned_candidate_ids": ["cand-2187"]},
    )
    configure(
        "st-chp5-p145-rosa-career-success-and-isolation",
        relation=False,
        relation_note="This records Haskell's evaluative character description; the contempt for fellow artists and reception claim are split into separate rows.",
        subject=None,
        original_quote=quote_between("Thus Rosa, despite", "fiercely independent"),
        claim="Haskell describes Rosa as artistically and socially successful, though fitfully, isolated, proud and melancholic yet buoyant, and fiercely independent.",
        updates={"mentioned_candidate_ids": ["cand-2236"]},
    )
    configure(
        "st-chp5-p145-rosa-frequently-confused-with-bamboccianti",
        relation=True,
        relation_note="Haskell says Rosa was often confused with the named Bamboccianti group; the group's rejection of qualities and Rosa's aspiration to them are recorded separately.",
        predicate="frequently_confused_with_artist_group",
        original_quote=quote_between("all too frequently confused with", "bamhoccianti"),
        claim="Haskell says Rosa was too often confused with the Bamboccianti.",
        updates={
            "print_reading_correction": {"source_line": 36, "source_form": "bamhoccianti", "printed_reading": "bamboccianti"},
            "mentioned_candidate_ids": ["cand-2236", "cand-0173"],
        },
    )
    configure(
        "st-chp5-p145-rosa-friendship-and-doubts-about-ricciardi-judgment",
        relation=True,
        relation_note="This row now records Haskell's explicit description of Ricciardi as Rosa's devoted, much-loved friend; Rosa's assessment of his artistic judgment is split below.",
        subject="cand-2236",
        obj="cand-2187",
        predicate="devoted_friend_of",
        original_quote=quote_between("He was certainly a devoted", "He was certainly a devoted and muchloved friend"),
        claim="Haskell describes Ricciardi as a devoted and much-loved friend of Rosa.",
        updates={
            "print_reading_correction": {"source_line": 35, "source_form": "muchloved", "printed_reading": "much-loved"},
            "mentioned_candidate_ids": ["cand-2236", "cand-2187"],
        },
    )
    configure(
        "st-chp5-p145-rosa-launched-onslaught-to-impose-serious-artist-image",
        relation=True,
        relation_note="This is Haskell's source-attributed account of Rosa's strategy against conventional patronage; the intended artistic image remains a stated purpose, not an independently established identity.",
        subject="cand-2236",
        obj=None,
        predicate="attacked_conventional_patronage_to_project_artist_image",
        original_quote=quote_between("launch the onslaught on conventional patronage", "wholly new kind"),
        open_reason="The source names conventional patronage as a general practice, not a separately identified organization or person.",
        updates={"mentioned_candidate_ids": ["cand-2236"]},
    )
    configure(
        "st-chp5-p145-rosa-letter-at-terni-waterfall",
        relation=True,
        relation_note="This records the continuing Rosa letter passage about the waterfall and landscape; the thought of Ricciardi at the described place is split into its own statement.",
        predicate="described_velino_waterfall_and_landscape",
        updates={
            "letter_candidate_id": "cand-11575",
            "footnote_marker": 6,
            "footnote_target_line": 50,
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_printed_page": "144",
            "footnote_link_status": "linked",
            "mentioned_candidate_ids": ["cand-2236", "cand-6233", "cand-6234", "cand-6235", "cand-6236", "cand-2187"],
        },
    )
    configure(
        "st-chp5-p145-rosa-letter-disagreed-about-little-picture",
        relation=True,
        relation_note="This preserves the first picture's contrasting attributions in Rosa's letter; the separate picture Ricciardi condemned is recorded below.",
        predicate="disputed_attribution_of_picture_with_ricciardi",
        original_quote=quote_between("‘the little picture which you consider", "to be Flemish"),
        claim="Rosa writes that Ricciardi considered the little picture Florentine while Rosa thought it Flemish.",
        updates={
            "letter_candidate_id": "cand-11576",
            "cited_material_not_independently_consulted": True,
            "attributions": ["Ricciardi: Florentine", "Rosa: Flemish"],
            "footnote_marker": 1,
            "footnote_target_line": 51,
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_printed_page": "145",
            "footnote_link_status": "linked",
            "recipient_candidate_id": "cand-2187",
            "mentioned_candidate_ids": ["cand-2236", "cand-2187", "cand-6237"],
            "qualification": "Neither picture is identified; the letter and cited edition were not independently examined. The printed reading is retained where S0 has a transcription error.",
        },
    )
    configure(
        "st-chp5-p145-rosa-looked-beyond-select-patronage-circles",
        relation=True,
        relation_note="Haskell describes Rosa's response to the failure to appeal to selective clients as looking beyond the outer circles of patronage; this remains Haskell's interpretation of strategy.",
        subject="cand-2236",
        obj=None,
        predicate="looked_beyond_selective_patronage_circles",
        open_reason="The outer circles of contemporary patronage are a generalized social field, not a separately identified entity.",
        updates={"mentioned_candidate_ids": ["cand-2236"]},
    )

    added: list[dict] = []

    def add_statement(
        statement_id: str,
        *,
        subject: str | None,
        obj: str | None,
        predicate: str,
        quote: str,
        claim: str,
        relation: bool,
        relation_note: str,
        line_number: int,
        mentioned: tuple[str, ...],
        speaker: str = "Haskell",
        text_layer: str = "authorial narration",
        qualification: str = "",
        open_reason: str | None = None,
        extras: dict | None = None,
    ) -> None:
        if statement_id in all_rows:
            raise SystemExit(f"Refusing: new statement ID exists: {statement_id}")
        if not quote or quote not in segment_text:
            raise SystemExit(f"Refusing: new quote is not an exact S0 substring: {statement_id}")
        q = {
            "source_line_start": line_number,
            "source_line_end": line_number,
            "printed_page": "145",
            "pdf_physical_page": 30,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
            "mentioned_candidate_ids": list(mentioned),
        }
        if open_reason:
            q["open_endpoint_reason"] = open_reason
        if extras:
            q.update(extras)
        row = {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": q,
            "original_quote": quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iv.md",
        }
        added.append(row)
        all_rows[statement_id] = row

    add_statement(
        "st-chp5-p145-rosa-trusted-ricciardi",
        subject="cand-2236", obj="cand-2187", predicate="trusted_friend",
        quote=quote_between("we must accept the artist’s trust", "we must accept the artist’s trust"),
        claim="Haskell says readers must accept Rosa's trust in Ricciardi because Ricciardi's letters have not survived.",
        relation=True,
        relation_note="This captures Haskell's explicit statement of Rosa's trust in Ricciardi, separate from the report that Ricciardi's letters have not survived.",
        line_number=35, mentioned=("cand-2236", "cand-2187"),
        speaker="Haskell", text_layer="authorial evidence assessment",
        qualification="The trust is Haskell's characterization of Rosa's confidence in Ricciardi; the underlying letters have not survived according to Haskell.",
    )
    add_statement(
        "st-chp5-p145-rosa-doubted-ricciardi-artistic-judgment",
        subject="cand-2236", obj="cand-2187", predicate="doubted_friend_artistic_judgment",
        quote=quote_between("Rosa does not seem to have thought very highly", "artistic judgement"),
        claim="Haskell says Rosa does not seem to have rated Ricciardi's artistic judgment highly.",
        relation=True,
        relation_note="This records a source-qualified relation of artistic judgment between Rosa and Ricciardi; Haskell's 'does not seem' qualification is retained.",
        line_number=35, mentioned=("cand-2236", "cand-2187"),
        qualification="This is Haskell's interpretation; 'does not seem' is not strengthened into certainty.",
    )
    add_statement(
        "st-chp5-p145-ricciardi-condemned-second-picture",
        subject="cand-2187", obj="cand-11950", predicate="condemned_picture",
        quote=quote_between("the one which you damn", "the one which you damn"),
        claim="Rosa says Ricciardi condemned an unidentified picture distinct from the little picture discussed immediately before.",
        relation=True,
        relation_note="The letter explicitly attributes condemnation of the second, unidentified picture to Ricciardi; the work itself is not identified.",
        line_number=35, mentioned=("cand-2187", "cand-11950"),
        speaker="Salvator Rosa, as quoted by Haskell",
        text_layer="letter quotation mediated by Haskell",
        qualification="The letter and cited edition were not independently examined.",
        extras={
            "letter_candidate_id": "cand-11576",
            "recipient_candidate_id": "cand-2187",
            "footnote_marker": 1,
            "footnote_target_line": 51,
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_printed_page": "145",
            "footnote_link_status": "linked",
            "cited_material_not_independently_consulted": True,
        },
    )
    add_statement(
        "st-chp5-p145-rosa-judged-second-picture-least-bad",
        subject="cand-2236", obj="cand-11950", predicate="judged_picture_least_bad",
        quote=quote_between("I find the least bad", "I find the least bad"),
        claim="Rosa says he found the picture condemned by Ricciardi the least bad.",
        relation=True,
        relation_note="This records Rosa's distinct evaluation of the unidentified picture; it is not merged with the disagreement over the first picture's attribution.",
        line_number=35, mentioned=("cand-2236", "cand-11950"),
        speaker="Salvator Rosa, as quoted by Haskell",
        text_layer="letter quotation mediated by Haskell",
        qualification="The letter and cited edition were not independently examined.",
        extras={
            "letter_candidate_id": "cand-11576",
            "footnote_marker": 1,
            "footnote_target_line": 51,
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_printed_page": "145",
            "footnote_link_status": "linked",
            "cited_material_not_independently_consulted": True,
        },
    )
    add_statement(
        "st-chp5-p145-bamboccianti-rejected-rosa-sought-qualities",
        subject="cand-0173", obj="cand-11952", predicate="rejected_qualities_sought_by_rosa",
        quote=quote_between("the very artists who most consistently rejected", "the elevated moral and poetic qualities"),
        claim="Haskell says the Bamboccianti most consistently rejected the elevated moral and poetic qualities Rosa sought.",
        relation=True,
        relation_note="This records Haskell's explicit account of the group's rejection of the qualities; Rosa's aspiration to them is recorded separately.",
        line_number=36, mentioned=("cand-0173", "cand-11952"),
        qualification="The qualities are preserved as Haskell's description and are not independently defined.",
    )
    add_statement(
        "st-chp5-p145-rosa-aspired-to-moral-poetic-qualities",
        subject="cand-2236", obj="cand-11952", predicate="aspired_to_qualities",
        quote=quote_between("to which he so avidly aspired", "to which he so avidly aspired"),
        claim="Haskell says Rosa avidly aspired to the elevated moral and poetic qualities described in the passage.",
        relation=True,
        relation_note="This records Rosa's aspiration to the source-defined qualities, distinct from the Bamboccianti's rejection of them.",
        line_number=36, mentioned=("cand-2236", "cand-11952"),
        qualification="The qualities are preserved as Haskell's description and are not independently defined.",
    )
    add_statement(
        "st-chp5-p145-rosa-contemptuous-of-fellow-artists",
        subject="cand-2236", obj="cand-11953", predicate="contemptuous_of_fellow_artists",
        quote=quote_between("contemptuous of most of his fellow-artists", "contemptuous of most of his fellow-artists"),
        claim="Haskell describes Rosa as contemptuous of most of his fellow artists.",
        relation=True,
        relation_note="The source defines an unnamed peer group; its members remain unspecified and are kept separate from the Bamboccianti group.",
        line_number=36, mentioned=("cand-2236", "cand-11953"),
        qualification="This is Haskell's characterization; no individual fellow artists are named.",
    )
    add_statement(
        "st-chp5-p145-rosa-not-taken-seriously-by-unnamed-audience",
        subject="cand-2236", obj=None, predicate="reported_not_taken_seriously_by_audience",
        quote=quote_between("whom no one would take seriously", "whom no one would take seriously"),
        claim="Haskell characterizes Rosa as an intellectual painter whom no one would take seriously.",
        relation=True,
        relation_note="This preserves Haskell's broad reception claim as a source-attributed relation with an unidentified audience.",
        line_number=36, mentioned=("cand-2236",),
        open_reason="Haskell's phrase 'no one' does not identify a bounded audience or any individual person.",
        qualification="This is Haskell's authorial characterization, not a measured consensus.",
    )
    add_statement(
        "st-chp5-p145-haskell-called-rosa-failed-intellectual-painter",
        subject=None, obj=None, predicate="authorial_characterization_as_failed_intellectual_painter",
        quote=quote_between("a failed intellectual painter", "a failed intellectual painter"),
        claim="Haskell characterizes Rosa as a failed intellectual painter.",
        relation=False,
        relation_note="This is an authorial evaluative description of Rosa, not a relation between entities.",
        line_number=36, mentioned=("cand-2236",),
        qualification="The phrase is Haskell's judgment and is not converted into a verified career outcome.",
    )
    add_statement(
        "st-chp5-p145-rosa-thought-of-ricciardi-in-waterfall-letter",
        subject="cand-2236", obj="cand-2187", predicate="thought_of_letter_recipient_at_described_place",
        quote=quote_between("Believe me, nowhere there did I look or move without thinking of you", "Believe me, nowhere there did I look or move without thinking of you"),
        claim="In the continuing letter, Rosa says that wherever he looked or moved at the described place, he thought of Ricciardi.",
        relation=True,
        relation_note="This captures the letter's explicit statement about Rosa thinking of its addressee; it does not imply Ricciardi was present.",
        line_number=34, mentioned=("cand-2236", "cand-2187", "cand-6233", "cand-6234"),
        speaker="Salvator Rosa, as quoted by Haskell",
        text_layer="letter quotation mediated by Haskell",
        qualification="This continues the letter passage cited by p.144 note 6; the letter and cited edition were not independently examined.",
        extras={
            "letter_candidate_id": "cand-11575",
            "recipient_candidate_id": "cand-2187",
            "continuation_of_statement_id": "st-chp5-p144-rosa-letter-described-landscape-contrast",
            "footnote_marker": 6,
            "footnote_target_line": 50,
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_printed_page": "144",
            "footnote_link_status": "linked",
        },
    )

    statements.extend(added)
    all_rows = {row["statement_id"]: row for row in statements}
    p144_note6_id = "st-chp5-seciv-note-l50-p144-marker6"
    p145_note1_id = "st-chp5-seciv-note-l51-p145-marker1"
    p145_authored_id = "st-chp5-l51-letter-authored-by"
    p145_addressed_id = "st-chp5-l51-letter-addressed-to"
    required_links = [
        "st-chp5-p145-rosa-letter-disagreed-about-little-picture",
        "st-chp5-p145-ricciardi-condemned-second-picture",
        "st-chp5-p145-rosa-judged-second-picture-least-bad",
    ]
    for statement_id in [p144_note6_id, p145_note1_id, p145_authored_id, p145_addressed_id]:
        if statement_id not in all_rows:
            raise SystemExit(f"Refusing: required footnote row is missing: {statement_id}")

    note6 = all_rows[p144_note6_id]["qualifiers"]
    p144_links = list(note6.get("linked_body_statement_ids", []))
    for statement_id in [
        "st-chp5-p145-rosa-letter-at-terni-waterfall",
        "st-chp5-p145-rosa-thought-of-ricciardi-in-waterfall-letter",
    ]:
        if statement_id not in p144_links:
            p144_links.append(statement_id)
    note6["linked_body_statement_ids"] = p144_links
    note6["citation_body_statement_ids"] = list(p144_links)
    note6["related_source_lines"] = sorted(set(note6.get("related_source_lines", [])) | {34})

    for statement_id in [p145_note1_id, p145_authored_id, p145_addressed_id]:
        q = all_rows[statement_id]["qualifiers"]
        q["linked_body_statement_ids"] = list(required_links)
        if statement_id == p145_note1_id:
            q["citation_body_statement_ids"] = list(required_links)

    def add_mention(mention_id: str, candidate_id: str, surface: str, note: str, *, occurrence: int = 0) -> None:
        if any(row["mention_id"] == mention_id for row in mentions):
            raise SystemExit(f"Refusing: mention ID already exists: {mention_id}")
        locations = []
        cursor = 0
        while True:
            start = segment_text.find(surface, cursor)
            if start < 0:
                break
            locations.append(start)
            cursor = start + 1
        if occurrence >= len(locations):
            raise SystemExit(f"Refusing: mention surface not found at requested occurrence: {surface!r} #{occurrence}")
        start = locations[occurrence]
        mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(start + len(surface)),
                "note": note,
            }
        )

    add_mention("m-chp5-p145-ricciardi-you-l34", "cand-2187", "you", "letter recipient identified from the continuing p.144 letter passage")
    add_mention("m-chp5-p145-ricciardi-you-l35a", "cand-2187", "you", "letter recipient in Rosa's first picture attribution", occurrence=1)
    add_mention("m-chp5-p145-ricciardi-you-l35b", "cand-2187", "you", "letter recipient in Rosa's second picture comparison", occurrence=2)
    add_mention("m-chp5-p145-rosa-artist-reference", "cand-2236", "the artist", "Haskell's anaphoric reference to Rosa in the trust statement")
    add_mention("m-chp5-p145-second-picture", "cand-11950", "the one", "source distinguishes this picture from the little picture mentioned immediately before")
    add_mention("m-chp5-p145-rosa-picture-group", "cand-11951", "his pictures", "Passeri's source-defined group of Rosa pictures")
    add_mention("m-chp5-p145-rosa-picture-group-humble-dwellings", "cand-11951", "such pictures", "Haskell's anaphoric reference to the pictures in the preceding Passeri quotation")
    add_mention("m-chp5-p145-mediocre-status", "cand-6238", "persone di mediocre stato", "historical social category quoted from Passeri")
    add_mention("m-chp5-p145-fellow-artists-group", "cand-11953", "most of his fellow-artists", "unnamed peer group described by Haskell")
    add_mention("m-chp5-p145-moral-poetic-qualities", "cand-11952", "elevated moral and poetic qualities", "source-defined abstract qualities sought by Rosa")

    def merge_ids(existing: list[str], additions: list[str]) -> list[str]:
        return existing + [item for item in additions if item not in existing]

    all_rows["st-chp5-p145-passeri-pictures-found-in-homes-of-different-status"]["qualifiers"]["mentioned_candidate_ids"] = merge_ids(
        all_rows["st-chp5-p145-passeri-pictures-found-in-homes-of-different-status"]["qualifiers"].get("mentioned_candidate_ids", []),
        ["cand-11951"],
    )
    all_rows["st-chp5-p145-haskell-speculates-about-quality-in-humble-dwellings"]["qualifiers"]["mentioned_candidate_ids"] = merge_ids(
        all_rows["st-chp5-p145-haskell-speculates-about-quality-in-humble-dwellings"]["qualifiers"].get("mentioned_candidate_ids", []),
        ["cand-11951"],
    )

    target_final = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(added) != 10 or len(target_final) != 24:
        raise SystemExit(f"Refusing: expected 10 additions and 24 final statements; found {len(added)} / {len(target_final)}")
    counts = {"true": 0, "false": 0, "unset": 0}
    for row in target_final:
        q = row.get("qualifiers", {})
        value = q.get("relation_candidate")
        counts["true" if value is True else "false" if value is False else "unset"] += 1
        if value is None:
            raise SystemExit(f"Refusing: unset statement remains: {row['statement_id']}")
        if value is True and (row.get("subject_candidate_id") is None or row.get("object_candidate_id") is None) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"Refusing: open relation lacks endpoint reason: {row['statement_id']}")
        if set(q.get("mentioned_candidate_ids", [])) - set(candidate_by_id):
            raise SystemExit(f"Refusing: unknown mentioned candidate in {row['statement_id']}")
        if row.get("original_quote") and row["original_quote"] not in segment_text:
            raise SystemExit(f"Refusing: quote outside S0 segment: {row['statement_id']}")
    if counts != {"true": 18, "false": 6, "unset": 0}:
        raise SystemExit(f"Refusing: classification distribution differs from plan: {counts}")

    target_mentions = [row for row in mentions if row.get("segment_id") == SEGMENT_ID]
    for row in target_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"Refusing: mention span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in candidate_by_id:
            raise SystemExit(f"Refusing: mention has unknown candidate: {row['mention_id']}")

    coverage_row = next((row for row in coverage if row.get("segment_id") == SEGMENT_ID), None)
    if not coverage_row:
        raise SystemExit("Refusing: p.145 body coverage row is missing")
    coverage_row["disposition"] = "reviewed"
    coverage_row["migration_status"] = "complete"
    coverage_row["source_line_ranges"] = "L34-37"
    coverage_row["note"] = (
        "S2语义处理：闭合Rosa书信续段，拆分其对Ricciardi的思念、信任、友情及艺术判断；"
        "区分两幅未识别绘画的不同判断；将Passeri所述Rosa画作作为作品组，保留房屋社会身份范围；"
        "拆分Rosa与Bamboccianti、同业群体及道德/诗性品质的关系。PDF物理页30核正much-loved与bamboccianti；"
        "注1–4及p.144注6回链已更新。新增候选均为来源限定开放项，不写入S6。"
    )

    for statement_id in required_links:
        if statement_id not in all_rows:
            raise SystemExit(f"Refusing: p.145 note 1 link target is missing: {statement_id}")
    for statement_id in [
        "st-chp5-p145-rosa-letter-at-terni-waterfall",
        "st-chp5-p145-rosa-thought-of-ricciardi-in-waterfall-letter",
    ]:
        if statement_id not in note6.get("linked_body_statement_ids", []):
            raise SystemExit(f"Refusing: p.144 note 6 continuation link is missing: {statement_id}")

    print("PREVIEW" if not args.apply else "APPLY PLAN")
    print(f"segment={SEGMENT_ID}; existing=14; added={len(added)}; final={len(target_final)}")
    print(f"classification={counts}; candidates_added={len(new_candidates)}; mentions_added=10; target_mentions={len(target_mentions)}")
    print("split the continuing letter, friendship/judgment, two picture comparisons, group attitudes, and patronage strategy")
    print("corrected Passeri endpoint to Rosa picture group; linked p.145 letter claims to note 1 and p.144 continuation to note 6")
    print("S0 unchanged; exact quote and mention spans checked; no S6 relations changed")
    if not args.apply:
        return

    for path in [statement_path, candidate_path, mention_path, coverage_path]:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"Refusing: backup already exists: {backup.name}")
        shutil.copy2(path, backup)
    write_jsonl(statement_path, statements)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_csv(coverage_path, coverage_fields, coverage)
    print("Wrote book-statements.jsonl, entity-candidates.csv, mentions.csv, and s2-coverage.csv.")
    print("Backups saved with suffix", BACKUP_SUFFIX)


if __name__ == "__main__":
    main()
