#!/usr/bin/env python3
"""Guarded S2 semantic review for chapter 5, printed page 144, lines 23-31."""
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
SEGMENT_ID = "chp-5:05_CHP-5_sec_iv:l23-31"
SOURCE_SEGMENT_SHA = "ed42fbd51762beab6e6aabe77d034b39ac18e125e38a387788d3fe824a2d5269"
EXPECTED_HASHES = {
    "book-statements.jsonl": "adeec45cae15f435f7bf27c43664e48bf467a27d894dbd0a5a7817f5ed0c4e7a",
    "entity-candidates.csv": "fb54c848b0ebfb35cae48d333cef58fd6505b4bae2581ce0406dd3029ed65a27",
    "mentions.csv": "6049e7c44579b82a1e74fdb2d6374c8af5c7b445c383fb787084ac5c0e4da5c7",
    "s2-coverage.csv": "e2c37d25b78601fbf9957d8e13534642417ad3531871cbb32d4dfc249f8f54d3",
}
BACKUP_SUFFIX = ".bak-s2-chp5-seciv-l23-31-20261013"
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

    segment = next(
        (row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID),
        None,
    )
    if not segment or segment.get("sha256") != SOURCE_SEGMENT_SHA:
        raise SystemExit("Refusing: S0 segment fingerprint changed or is missing")
    if segment.get("asset_sha256") != "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f":
        raise SystemExit("Refusing: source asset fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[22:31])

    def line(n: int) -> str:
        return source_lines[n - 1]

    def line_slice(n: int, start: str, stop: str) -> str:
        text = line(n)
        a = text.index(start)
        b = text.index(stop, a)
        return text[a:b]

    def quote_between(start: str, end: str) -> str:
        a = segment_text.index(start)
        b = segment_text.index(end, a) + len(end)
        return segment_text[a:b]

    statement_path = TABLES / "book-statements.jsonl"
    coverage_path = TABLES / "s2-coverage.csv"
    statements = read_jsonl(statement_path)
    coverage_fields, coverage = read_csv(coverage_path)
    candidate_fields, candidates = read_csv(TABLES / "entity-candidates.csv")
    mention_fields, mentions = read_csv(TABLES / "mentions.csv")
    candidate_ids = {row["candidate_id"] for row in candidates}

    target = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    row_by_id = {row["statement_id"]: row for row in target}
    target_ids = {
        "st-chp5-p144-de-rossi-displayed-la-fortuna",
        "st-chp5-p144-de-rossi-displayed-prometheus",
        "st-chp5-p144-de-rossi-displayed-regulus",
        "st-chp5-p144-de-rossi-not-an-intellectual-patron-like-dal-pozzo",
        "st-chp5-p144-de-rossi-obtained-smaller-rosa-pictures",
        "st-chp5-p144-de-rossi-private-museum-of-rosa-works",
        "st-chp5-p144-no-evidence-of-de-rossi-intellectual-stimulus",
        "st-chp5-p144-regulus-raised-small-picture-idiom-to-heroic-tragedy",
        "st-chp5-p144-rosa-claimed-rome-heard-of-his-originality",
        "st-chp5-p144-rosa-landscape-letters-express-genuine-romantic-sentiment",
        "st-chp5-p144-rosa-letter-described-landscape-contrast",
        "st-chp5-p144-rosa-painted-altarpieces-for-family-chapel",
        "st-chp5-p144-rosa-painted-for-ricciardi-and-sought-advice",
        "st-chp5-p144-rosa-proposed-georgics-subject-of-justice",
        "st-chp5-p144-rosa-requested-lively-story-for-picture",
        "st-chp5-p144-rosa-requested-new-composition-with-few-figures",
        "st-chp5-p144-rosa-sought-patronage-in-florence-through-ricciardi",
    }
    if len(target) != 17 or set(row_by_id) != target_ids:
        raise SystemExit(f"Refusing: expected the reviewed 17-row target set, found {len(target)}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") not in (True, False) for row in target) != 14:
        raise SystemExit("Refusing: expected exactly 14 unclassified target statements")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in target) != 3:
        raise SystemExit("Refusing: the three already classified display statements changed")

    p143_quarrel_id = "st-chp5-p143-rosa-and-de-rossi-quarrel-in-1667"
    p144_note1_id = "st-chp5-seciv-note-l46-p144-marker1"
    p144_note4_id = "st-chp5-seciv-note-l48-p144-marker4"
    p144_note5_id = "st-chp5-seciv-note-l49-p144-marker5"
    p144_note6_id = "st-chp5-seciv-note-l50-p144-marker6"
    all_rows = {row["statement_id"]: row for row in statements}
    required_link_ids = {p143_quarrel_id, p144_note1_id, p144_note4_id, p144_note5_id, p144_note6_id}
    if not required_link_ids <= set(all_rows):
        raise SystemExit("Refusing: a required p.143/p.144 statement or footnote row is missing")

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
        line_start: int | None = None,
        line_end: int | None = None,
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
        if line_start is not None:
            q["source_line_start"] = line_start
        if line_end is not None:
            q["source_line_end"] = line_end
        for key in remove:
            q.pop(key, None)
        if updates:
            q.update(updates)

    configure(
        "st-chp5-p144-de-rossi-not-an-intellectual-patron-like-dal-pozzo",
        relation=False,
        relation_note="This is Haskell's comparative characterization of De' Rossi's patronage, not a direct relation between the two men.",
        claim="Haskell says De' Rossi was no Dal Pozzo as a source of intellectual encouragement for Rosa, despite his friendship.",
        subject=None,
        obj=None,
        updates={"mentioned_candidate_ids": ["cand-2269", "cand-2045"]},
    )
    configure(
        "st-chp5-p144-de-rossi-obtained-smaller-rosa-pictures",
        relation=True,
        relation_note="Haskell reports that De' Rossi acquired a group of Rosa's smaller pictures; the works themselves are not individually identified.",
        obj=None,
        predicate="obtained_unnamed_small_works_by_artist",
        claim="Haskell says De' Rossi obtained many smaller pictures by Rosa, including battles, sea pieces, landscapes, and witchcraft scenes.",
        open_reason="The acquired pictures form an unnamed group; Rosa is retained as the artist rather than the work endpoint.",
        updates={
            "artist_candidate_id": "cand-2236",
            "collection_candidate_id": "cand-11484",
            "work_types": ["battles", "sea pieces", "landscapes", "witchcraft scenes"],
            "mentioned_candidate_ids": ["cand-2269", "cand-2236", "cand-11484"],
            "qualification": "The individual pictures are not identified; 'affected to despise' is Haskell's characterization.",
        },
    )
    configure(
        "st-chp5-p144-de-rossi-private-museum-of-rosa-works",
        relation=True,
        relation_note="The source-defined private museum is the collection assembled by De' Rossi; Rosa is its artist, not the collection endpoint.",
        obj="cand-11484",
        predicate="assembled_private_collection",
        claim="Haskell says De' Rossi assembled what amounted to a private museum of Rosa's works, with a large gallery and several small rooms.",
        updates={"mentioned_candidate_ids": ["cand-2269", "cand-2236", "cand-11484"]},
    )
    configure(
        "st-chp5-p144-no-evidence-of-de-rossi-intellectual-stimulus",
        relation=True,
        relation_note="This is a source-bounded negative claim about the encouragement De' Rossi gave Rosa; it does not prove that no support occurred.",
        predicate="source_reports_no_evidence_of_intellectual_encouragement",
        claim="Haskell says there is no evidence that De' Rossi gave Rosa the encouragement and intellectual stimulus Rosa wanted.",
    )
    configure(
        "st-chp5-p144-regulus-raised-small-picture-idiom-to-heroic-tragedy",
        relation=True,
        relation_note="Haskell interprets the named painting through Rosa's study of Stoic historians; this is an art-historical reading, not an independently verified account of the artist's intent.",
        obj="cand-2510",
        predicate="interpreted_as_transformed_by_stoic_study",
        claim="Haskell interprets Regulus as raising Rosa's obligations to the Bamboccianti and love of the picturesque to heroic tragedy through study of Stoic historians.",
        updates={"mentioned_candidate_ids": ["cand-6225", "cand-2236", "cand-0173", "cand-2510"]},
    )
    configure(
        "st-chp5-p144-rosa-claimed-rome-heard-of-his-originality",
        relation=True,
        relation_note="This is Rosa's reported claim to Ricciardi in a cited letter; it does not independently establish that Rome had heard the claim.",
        predicate="claimed_original_reputation_to_recipient",
        claim="In a letter to Ricciardi, Rosa says Rome had heard that he had the most original ideas and that he must live up to this reputation.",
        updates={
            "letter_candidate_id": "cand-11574",
            "reported_audience_candidate_id": "cand-4490",
            "footnote_marker": 5,
            "footnote_target_line": 49,
            "footnote_printed_page": "144",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
            "print_reading_correction": {"source_line": 29, "source_form": "five up", "printed_reading": "live up"},
            "qualification": "Rosa's letter is reported by Haskell; the quoted claim is not independent confirmation of his reputation. The underlying letter was not independently examined.",
        },
    )
    configure(
        "st-chp5-p144-rosa-landscape-letters-express-genuine-romantic-sentiment",
        relation=False,
        relation_note="This is Haskell's literary interpretation of Rosa's landscape writing, not a relation between Rosa and Ricciardi.",
        subject=None,
        obj=None,
        predicate="haskell_assessed_romantic_sentiment_as_deeply_felt_and_genuine",
        original_quote=quote_between("which showed how deeply felt and genuine", "in his painting."),
        claim="Haskell interprets the romantic sentiment in Rosa's painting as deeply felt and genuine.",
        updates={"artist_candidate_id": "cand-2236", "mentioned_candidate_ids": ["cand-2236"]},
    )
    landscape_quote = quote_between("is such an extravagant mixture", "mountains I have crossed.")
    configure(
        "st-chp5-p144-rosa-letter-described-landscape-contrast",
        relation=True,
        relation_note="This row records Rosa's landscape description to Ricciardi; the route and wish to have Ricciardi present are split into separate statements below.",
        predicate="described_landscape_to_friend_in_letter",
        original_quote=landscape_quote,
        claim="In a letter to Ricciardi, Rosa describes contrasts between tame and horrid, flat and precipitous scenery, praises the mountains above the Tuscan sky, and compares Verrucola to a garden.",
        line_end=30,
        updates={
            "letter_candidate_id": "cand-11575",
            "places_candidate_ids": ["cand-6232", "cand-6229"],
            "mentioned_candidate_ids": ["cand-2236", "cand-2187", "cand-6232", "cand-6229"],
            "print_reading_correction": {"source_line": 30, "source_form": "suture", "printed_reading": "future"},
            "qualification": "Reported letter to Ricciardi, cited by Haskell through Bottari; the letter and edition were not independently examined.",
        },
    )
    configure(
        "st-chp5-p144-rosa-painted-altarpieces-for-family-chapel",
        relation=True,
        relation_note="Rosa is linked to the unnamed altarpiece group; the chapel is preserved as the venue rather than the work endpoint.",
        obj="cand-11485",
        predicate="painted_works_for_chapel_without_charge",
        claim="Haskell says Rosa painted unnamed altarpieces without charge for De' Rossi's family chapel at Madonna di Montesanto, seeking at least one public appearance for his work.",
        updates={
            "place_candidate_id": "cand-6228",
            "mentioned_candidate_ids": ["cand-2269", "cand-2236", "cand-6228", "cand-11485"],
        },
    )
    configure(
        "st-chp5-p144-rosa-painted-for-ricciardi-and-sought-advice",
        relation=True,
        relation_note="This row records the continued painting relationship only; the advice relationship is split below.",
        predicate="continued_painting_for",
        original_quote=quote_between("For him he went on painting", "settled in Rome"),
        claim="Haskell says Rosa continued painting pictures for Ricciardi long after he had settled in Rome.",
        updates={
            "letter_candidate_id": "cand-11573",
            "mentioned_candidate_ids": ["cand-2236", "cand-2187", "cand-4490"],
        },
    )
    configure(
        "st-chp5-p144-rosa-proposed-georgics-subject-of-justice",
        relation=True,
        relation_note="Rosa proposes a possible image from Virgil's Georgics to Ricciardi; it is not evidence of a completed painting.",
        predicate="proposed_picture_subject_from_literary_work",
        claim="Rosa asks Ricciardi to consider a subject from Virgil's Georgics: Justice departing Earth and leaving sword and scales with shepherds.",
        updates={
            "letter_candidate_id": "cand-11574",
            "footnote_marker": 5,
            "footnote_target_line": 49,
            "footnote_printed_page": "144",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
            "print_reading_correction": {"source_line": 29, "source_form": "Georgies", "printed_reading": "Georgics"},
            "qualification": "This is a proposed image only, not evidence of a completed painting. The scan reads 'Georgics'; S0 preserves 'Georgies'. The underlying letter was not independently examined.",
        },
    )
    configure(
        "st-chp5-p144-rosa-requested-lively-story-for-picture",
        relation=True,
        relation_note="This is Rosa's request to Ricciardi for a possible picture subject, not evidence that the story was supplied or painted.",
        predicate="asked_friend_to_find_story_for_picture",
        updates={"letter_candidate_id": "cand-11573", "recipient_candidate_id": "cand-2187"},
    )
    configure(
        "st-chp5-p144-rosa-requested-new-composition-with-few-figures",
        relation=True,
        relation_note="This is a reported request concerning a possible composition, not evidence of a completed work.",
        predicate="requested_feedback_on_new_composition",
        updates={
            "letter_candidate_id": "cand-11574",
            "canvas_candidate_id": "cand-3571",
            "footnote_marker": 5,
            "footnote_target_line": 49,
            "footnote_printed_page": "144",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
            "mentioned_candidate_ids": ["cand-2236", "cand-2187", "cand-3571"],
        },
    )
    configure(
        "st-chp5-p144-rosa-sought-patronage-in-florence-through-ricciardi",
        relation=True,
        relation_note="The passage says Rosa turned to Florence to find a patron; it identifies Ricciardi as his closest friend there but does not say Ricciardi supplied the patronage.",
        obj="cand-3397",
        predicate="turned_to_city_to_seek_patronage",
        claim="Haskell says Rosa turned to Florence to find the patron he wanted; Ricciardi lived there and was his closest friend.",
        updates={
            "friend_candidate_id": "cand-2187",
            "place_candidate_id": "cand-3397",
            "mentioned_candidate_ids": ["cand-2236", "cand-3397", "cand-2187"],
        },
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
        relation_note: str,
        line_start: int,
        line_end: int,
        mentioned: tuple[str, ...],
        speaker: str = "Haskell",
        text_layer: str = "authorial narration",
        qualification: str = "",
        extras: dict | None = None,
        open_reason: str | None = None,
    ) -> None:
        if statement_id in all_rows:
            raise SystemExit(f"Refusing: new statement ID exists: {statement_id}")
        if quote not in segment_text:
            raise SystemExit(f"Refusing: new quote is not an exact S0 substring: {statement_id}")
        q = {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "printed_page": "144",
            "pdf_physical_page": 29,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "relation_candidate": True,
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
        "st-chp5-p144-de-rossi-friend-of-rosa",
        subject="cand-2269", obj="cand-2236", predicate="friend_of",
        quote=quote_between("for all his friendship", "was no Dal Pozzo"),
        claim="Haskell describes De' Rossi as Rosa's friend.",
        relation_note="The source directly describes their relationship as friendship.",
        line_start=28, line_end=28, mentioned=("cand-2269", "cand-2236"),
    )
    add_statement(
        "st-chp5-p144-ricciardi-closest-friend-of-rosa",
        subject="cand-2236", obj="cand-2187", predicate="identified_as_closest_friend",
        quote=quote_between("the home of his closest friend", "Giambattista Ricciardi"),
        claim="Haskell identifies Giambattista Ricciardi as Rosa's closest friend.",
        relation_note="The source explicitly names Ricciardi as Rosa's closest friend; the passage does not identify him as the patron Rosa sought.",
        line_start=28, line_end=28, mentioned=("cand-2236", "cand-2187", "cand-3397"),
        extras={"place_candidate_id": "cand-3397"},
    )
    add_statement(
        "st-chp5-p144-rosa-looked-to-ricciardi-for-advice",
        subject="cand-2236", obj="cand-2187", predicate="looked_to_friend_for_advice",
        quote=quote_between("to him he looked for constant advice", "constant advice"),
        claim="Haskell says Rosa looked to Ricciardi for constant advice.",
        relation_note="The source states an advice-seeking relationship; no particular advice or occasion is identified.",
        line_start=28, line_end=28, mentioned=("cand-2236", "cand-2187"),
        extras={
            "letter_candidate_id": "cand-11573",
            "footnote_marker": 4,
            "footnote_target_line": 48,
            "footnote_printed_page": "144",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
        },
    )
    route_quote = quote_between("We went to Ancona", "Assisi")
    for place_id, place_label, role in [
        ("cand-6230", "Ancona", "outbound destination"),
        ("cand-6231", "Sirolo", "outbound destination"),
        ("cand-5407", "Assisi", "place on the return route"),
    ]:
        add_statement(
            f"st-chp5-p144-rosa-reported-travel-to-{place_label.lower()}",
            subject="cand-2236", obj=place_id, predicate="reported_travel_to",
            quote=route_quote,
            claim=f"In the letter quoted by Haskell, Rosa reports that his party went to {place_label}.",
            relation_note="This records the source-reported itinerary; the letter uses 'we' and does not identify the other travelers.",
            line_start=31, line_end=31, mentioned=("cand-2236", "cand-2187", place_id),
            speaker="Salvator Rosa, as quoted by Haskell",
            text_layer="letter quotation mediated by Haskell",
            qualification=f"{role}; no companions beyond the plural 'we' are identified.",
            extras={
                "letter_candidate_id": "cand-11575",
                "trip_group": "unidentified party described as 'we'",
                "footnote_marker": 6,
                "footnote_target_line": 50,
                "footnote_printed_page": "144",
                "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
                "footnote_link_status": "linked",
            },
        )
    add_statement(
        "st-chp5-p144-rosa-wished-ricciardi-were-with-him",
        subject="cand-2236", obj="cand-2187", predicate="wished_friend_accompanied_him",
        quote=quote_between("how many times I wanted you with me", "how many times I wanted you with me"),
        claim="In the letter, Rosa says he repeatedly wished Ricciardi had been with him on the journey.",
        relation_note="This is Rosa's expressed wish in a reported letter, not evidence that Ricciardi traveled with him.",
        line_start=31, line_end=31, mentioned=("cand-2236", "cand-2187"),
        speaker="Salvator Rosa, as quoted by Haskell",
        text_layer="letter quotation mediated by Haskell",
        qualification="The underlying letter and cited edition were not independently examined.",
        extras={
            "letter_candidate_id": "cand-11575",
            "footnote_marker": 6,
            "footnote_target_line": 50,
            "footnote_printed_page": "144",
            "footnote_segment": "chp-5:05_CHP-5_sec_iv:l39-54",
            "footnote_link_status": "linked",
        },
    )

    # P.144 note 1 gives only a citation locator. Remove unsupported date and
    # recipient previously carried over from the distinct p.143 note 1.
    note1 = all_rows[p144_note1_id]["qualifiers"]
    note1["claim"] = "Haskell cites de Rinaldis (1939), page 199, after the continuation of Rosa's complaint about De' Rossi."
    note1["qualification"] = "This is a citation locator linked to the quarrel quotation begun on p.143. The note does not state a letter date or addressee; the cited page was not independently consulted."
    note1.pop("date", None)
    note1.pop("recipient_candidate_id", None)
    note1["linked_body_statement_ids"] = [p143_quarrel_id]
    note1["citation_body_statement_ids"] = [p143_quarrel_id]

    note4 = all_rows[p144_note4_id]["qualifiers"]
    note4_links = [
        "st-chp5-p144-rosa-painted-for-ricciardi-and-sought-advice",
        "st-chp5-p144-rosa-looked-to-ricciardi-for-advice",
        "st-chp5-p144-rosa-requested-lively-story-for-picture",
    ]
    note4["linked_body_statement_ids"] = note4_links
    note4["citation_body_statement_ids"] = note4_links
    note5 = all_rows[p144_note5_id]["qualifiers"]
    note5_links = [
        "st-chp5-p144-rosa-proposed-georgics-subject-of-justice",
        "st-chp5-p144-rosa-claimed-rome-heard-of-his-originality",
        "st-chp5-p144-rosa-requested-new-composition-with-few-figures",
    ]
    note5["linked_body_statement_ids"] = note5_links
    note5["citation_body_statement_ids"] = note5_links
    note6 = all_rows[p144_note6_id]["qualifiers"]
    note6_links = [
        "st-chp5-p144-rosa-letter-described-landscape-contrast",
        "st-chp5-p144-rosa-reported-travel-to-ancona",
        "st-chp5-p144-rosa-reported-travel-to-sirolo",
        "st-chp5-p144-rosa-reported-travel-to-assisi",
        "st-chp5-p144-rosa-wished-ricciardi-were-with-him",
    ]
    note6["linked_body_statement_ids"] = note6_links
    note6["citation_body_statement_ids"] = note6_links

    statements.extend(added)
    target_final = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(added) != 7 or len(target_final) != 24:
        raise SystemExit(f"Refusing: expected 7 additions and 24 final statements; found {len(added)} / {len(target_final)}")
    counts = {"true": 0, "false": 0, "unset": 0}
    for row in target_final:
        q = row.get("qualifiers", {})
        value = q.get("relation_candidate")
        counts["true" if value is True else "false" if value is False else "unset"] += 1
        if value is None:
            raise SystemExit(f"Refusing: unset statement remains: {row['statement_id']}")
        if value is True and (row.get("subject_candidate_id") is None or row.get("object_candidate_id") is None) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"Refusing: open relation lacks endpoint reason: {row['statement_id']}")
        if q.get("mentioned_candidate_ids"):
            unknown = set(q["mentioned_candidate_ids"]) - candidate_ids
            if unknown:
                raise SystemExit(f"Refusing: unknown mentioned candidates in {row['statement_id']}: {sorted(unknown)}")
        if row.get("original_quote") and row["original_quote"] not in segment_text:
            raise SystemExit(f"Refusing: quote outside S0 segment: {row['statement_id']}")
    if counts != {"true": 22, "false": 2, "unset": 0}:
        raise SystemExit(f"Refusing: classification distribution differs from plan: {counts}")

    target_mentions = [row for row in mentions if row.get("segment_id") == SEGMENT_ID]
    for row in target_mentions:
        a, b = int(row["start_char"]), int(row["end_char"])
        if segment_text[a:b] != row["surface_form"]:
            raise SystemExit(f"Refusing: mention span mismatch: {row['mention_id']}")

    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_row["disposition"] = "reviewed"
    coverage_row["migration_status"] = "complete"
    coverage_row["source_line_ranges"] = "L24-31"
    coverage_row["note"] = (
        "S2完成印刷p.144正文L24-31语义复核：区分De’ Rossi的收藏、购画、与Rosa的友谊及未获智识鼓励；"
        "将Rosa与Ricciardi的持续绘画、建议、友谊和书信请求分开；拆出来自Georgics的拟议画题、"
        "Rosa对Rome声誉的书信陈述，以及Ancona、Sirolo、Assisi行程与同行愿望。扫描确认Georgics、"
        "live up、future；未改写S0。p.144注1仍仅作de Rinaldis页码定位，移除无法由该注支持的日期和收信人；"
        "修正注4-6的statement回链。未写S6正式关系。"
    )

    for note_id, links in [(p144_note4_id, note4_links), (p144_note5_id, note5_links), (p144_note6_id, note6_links)]:
        actual = all_rows[note_id]["qualifiers"].get("linked_body_statement_ids", [])
        if actual != links or any(link not in all_rows for link in links):
            raise SystemExit(f"Refusing: p.144 footnote backlink mismatch: {note_id}")
    if all_rows[p144_note1_id]["qualifiers"].get("linked_body_statement_ids") != [p143_quarrel_id]:
        raise SystemExit("Refusing: p.144 note 1 is not linked to the continued quarrel quotation")

    print("PREVIEW" if not args.apply else "APPLY PLAN")
    print(f"segment={SEGMENT_ID}; existing=17; added={len(added)}; final={len(target_final)}")
    print(f"classification={counts}; current target mentions={len(target_mentions)}; candidates/mentions unchanged")
    print("corrected work/collection endpoints; split friendship, advice, city-patronage and travel claims")
    print("corrected footnote 1 citation-only metadata; updated note 4-6 body back-links")
    print("scan corrections: Georgics, live up, future; S0 unchanged; quotes and mention spans verified")
    if not args.apply:
        return

    for path in [statement_path, coverage_path]:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"Refusing: backup already exists: {backup.name}")
        shutil.copy2(path, backup)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("Wrote book-statements.jsonl and s2-coverage.csv; backups saved with suffix", BACKUP_SUFFIX)


if __name__ == "__main__":
    main()
