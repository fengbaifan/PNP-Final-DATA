#!/usr/bin/env python3
"""Semantically review p.347 and restore its exact entity mentions."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY_SEGMENT = "chp-14:14_CHP-14_intro:l3-12"
NOTES_SEGMENT = "chp-14:14_CHP-14_intro:l168-220"
STATEMENT_BACKUP_SUFFIX = ".bak-s2-ch14-p347-semantic-review-20261014"
MENTION_BACKUP_SUFFIX = ".bak-s2-ch14-p347-semantic-review-20261014"
EXPECTED_STATEMENTS = "702ab2991ad114d55c09df9ca6fb4307a05ad7aa4296bbe6f03297d75ff9cb47"
EXPECTED_MENTIONS = "973be191a73cc8d710d9779a8ee2c954bd420b40797d8a917f0f8157d94ab9e0"
EXPECTED_SOURCE = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
EXPECTED_PDF = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"

UNCLASSIFIED_IDS = {
    "st-chp14-p347-note1-bibliography",
    "st-chp14-p347-note2-bosdari",
    "st-chp14-p347-patronage-tensions",
    "st-chp14-p347-receptive-character",
    "st-chp14-p347-note1-continuation",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def quote_on(lines: list[str], line_number: int, fragment: str) -> str:
    line = lines[line_number - 1]
    if fragment not in line:
        raise SystemExit(f"source fragment missing at L{line_number}: {fragment!r}")
    return fragment


def make_statement(template: dict, statement_id: str, *, subject: str | None, object_: str | None,
                   predicate: str, line: int, quote: str, claim: str, relation: bool,
                   qualification: str, mentioned: list[str], relation_note: str = "",
                   extra_qualifiers: dict | None = None) -> dict:
    row = copy.deepcopy(template)
    row.update({
        "statement_id": statement_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "original_quote": quote,
    })
    q = row["qualifiers"]
    q.clear()
    q.update({
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 347,
        "pdf_physical_page": 1,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": template.get("qualifiers", {}).get("text_layer", "authorial assertion"),
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
    })
    if row.get("segment_id") == NOTES_SEGMENT:
        q.update({
            "footnote_marker": "1",
            "footnote_printed_page": 347,
            "linked_body_statement_ids": ["st-chp14-p347-birth"],
        })
    if relation and relation_note:
        q["relation_candidate_note"] = relation_note
    if extra_qualifiers:
        q.update(extra_qualifiers)
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validation; default is dry-run")
    args = parser.parse_args()
    for path, expected in (
        (STATEMENTS, EXPECTED_STATEMENTS), (MENTIONS, EXPECTED_MENTIONS),
        (SOURCE, EXPECTED_SOURCE), (PDF, EXPECTED_PDF),
    ):
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} sha256={actual}, expected={expected}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    rows = load_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("statement_id is not unique before apply")
    if set(UNCLASSIFIED_IDS) - set(by_id):
        raise SystemExit(f"missing target statements: {sorted(set(UNCLASSIFIED_IDS) - set(by_id))}")
    for statement_id in UNCLASSIFIED_IDS:
        row = by_id[statement_id]
        if "relation_candidate" in row.get("qualifiers", {}):
            raise SystemExit(f"target is already classified: {statement_id}")
        q = row["qualifiers"]
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1:end]):
            raise SystemExit(f"existing S0 quote mismatch: {statement_id}")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        mention_fields = list(reader.fieldnames or [])
        mention_rows = list(reader)
        has_bom = MENTIONS.read_bytes().startswith(b"\xef\xbb\xbf")
    existing_mention_ids = {row["mention_id"] for row in mention_rows}
    if any(row["segment_id"] in {BODY_SEGMENT, NOTES_SEGMENT} for row in mention_rows):
        raise SystemExit("p.347 source segments already contain mentions; review current rows before applying")

    segment_rows = load_jsonl(ROOT / "04-knowledge" / "tables" / "segments.jsonl")
    bounds = {r["segment_id"]: (int(r["line_start"]), int(r["line_end"])) for r in segment_rows}
    texts: dict[str, str] = {}
    for segment_id in (BODY_SEGMENT, NOTES_SEGMENT):
        start, end = bounds[segment_id]
        texts[segment_id] = "\n".join(source_lines[start - 1:end])

    new_mentions: list[dict] = []
    next_mention_number = 1

    def add_mention(segment_id: str, line_number: int, phrase: str, candidate_id: str,
                    note: str = "", occurrence: int = 0) -> None:
        nonlocal next_mention_number
        if segment_id not in texts:
            raise SystemExit(f"unknown mention segment {segment_id}")
        line_start, _ = bounds[segment_id]
        if not line_start <= line_number:
            raise SystemExit(f"mention line outside segment: L{line_number} / {segment_id}")
        source_line = source_lines[line_number - 1]
        positions = []
        offset = 0
        while True:
            found = source_line.find(phrase, offset)
            if found < 0:
                break
            positions.append(found)
            offset = found + 1
        if occurrence >= len(positions):
            raise SystemExit(f"mention phrase occurrence missing at L{line_number}: {phrase!r}")
        segment_offset = sum(len(source_lines[i - 1]) + 1 for i in range(line_start, line_number))
        start_char = segment_offset + positions[occurrence]
        mention_id = f"m-s2-ch14-p347-{next_mention_number:03d}"
        if mention_id in existing_mention_ids:
            raise SystemExit(f"mention_id already exists: {mention_id}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": phrase,
            "start_char": str(start_char),
            "end_char": str(start_char + len(phrase)),
            "note": note,
        })
        next_mention_number += 1

    # Body, p.347 L6-L12: named people, places, works and source-defined groups.
    add_mention(BODY_SEGMENT, 6, "Venetian art patrons", "cand-4129", "The page's general art-patron category.")
    add_mention(BODY_SEGMENT, 6, "Venetian", "cand-2719", "Adjectival geographic reference to Venice.")
    add_mention(BODY_SEGMENT, 7, "Francesco Algarotti", "cand-0043")
    add_mention(BODY_SEGMENT, 7, "his own collection of paintings", "cand-10223")
    add_mention(BODY_SEGMENT, 7, "Consul Smith", "cand-2440", "Keep the printed form; identity alignment remains S3.")
    add_mention(BODY_SEGMENT, 7, "royal gallery at Dresden", "cand-10222")
    add_mention(BODY_SEGMENT, 7, "Dresden", "cand-0947")
    add_mention(BODY_SEGMENT, 7, "Tiepolo", "cand-2572")
    add_mention(BODY_SEGMENT, 7, "Canaletto", "cand-0499")
    add_mention(BODY_SEGMENT, 8, "Venetian", "cand-2719", "Adjectival geographic wording in Haskell's qualified patriotism characterization.")
    add_mention(BODY_SEGMENT, 8, "Venice", "cand-2719", occurrence=0)
    add_mention(BODY_SEGMENT, 8, "European", "cand-3462", "Geographic adjective in Haskell's general characterization of new experiences.")
    add_mention(BODY_SEGMENT, 8, "Europe", "cand-3462")
    add_mention(BODY_SEGMENT, 8, "Venice", "cand-2719", occurrence=1)
    add_mention(BODY_SEGMENT, 9, "Francesco Algarotti", "cand-0043")
    add_mention(BODY_SEGMENT, 9, "Venice", "cand-2719")
    add_mention(BODY_SEGMENT, 9, "his father", "cand-10225", "Unnamed father; the phrase is anaphoric.")
    add_mention(BODY_SEGMENT, 9, "a rich merchant", "cand-10225", "The source describes the same unnamed father as a rich merchant.")
    add_mention(BODY_SEGMENT, 9, "Rome", "cand-4490")
    add_mention(BODY_SEGMENT, 9, "Bologna", "cand-3398", occurrence=0)
    add_mention(BODY_SEGMENT, 9, "Bologna", "cand-3398", occurrence=1)
    add_mention(BODY_SEGMENT, 9, "Eustachio Manfredi", "cand-1511")
    add_mention(BODY_SEGMENT, 9, "the Zanotti brothers", "cand-10226", "Collective endpoint; do not assign to an individual brother.")
    add_mention(BODY_SEGMENT, 10, "Bonomo", "cand-0040")
    add_mention(BODY_SEGMENT, 10, "Francesco", "cand-0043", "Short-form reference to Francesco Algarotti.")
    add_mention(BODY_SEGMENT, 11, "Bonomo", "cand-0040", occurrence=0)
    add_mention(BODY_SEGMENT, 11, "Francesco", "cand-0043")
    add_mention(BODY_SEGMENT, 11, "Europe", "cand-3462")
    add_mention(BODY_SEGMENT, 11, "Bonomo", "cand-0040", occurrence=1)
    add_mention(BODY_SEGMENT, 11, "their joint collection", "cand-10224", "Keep distinct from Francesco's own collection on p.347.")
    add_mention(BODY_SEGMENT, 11, "Bonomo", "cand-0040", occurrence=2)
    add_mention(BODY_SEGMENT, 12, "80-99", "cand-10237", "Continuation of p.347 note 1's Lepre page range.")

    # Printed footnotes: p.347 note 1 and note 2, only at their exact source lines.
    add_mention(NOTES_SEGMENT, 169, "Algarotti", "cand-0043", occurrence=0)
    add_mention(NOTES_SEGMENT, 169, "Michelessi", "cand-10227")
    add_mention(NOTES_SEGMENT, 169, "Memorie", "cand-10228")
    add_mention(NOTES_SEGMENT, 169, "first volume of the seventeen-volume edition of Algarotti’s works", "cand-10229")
    add_mention(NOTES_SEGMENT, 169, "Algarotti’s", "cand-0043", "Possessive reference within the edition title description.")
    add_mention(NOTES_SEGMENT, 169, "Carlo Palese", "cand-9798")
    add_mention(NOTES_SEGMENT, 169, "Venice", "cand-2719")
    add_mention(NOTES_SEGMENT, 169, "short and rare Latin life", "cand-10230")
    add_mention(NOTES_SEGMENT, 169, "T. G. Farsetti", "cand-1013")
    add_mention(NOTES_SEGMENT, 169, "Bonomo", "cand-0040")
    add_mention(NOTES_SEGMENT, 169, "complete modern life", "cand-10232")
    add_mention(NOTES_SEGMENT, 169, "Ida Treat", "cand-10231")
    add_mention(NOTES_SEGMENT, 169, "Annamaria Gabrielli", "cand-10233")
    add_mention(NOTES_SEGMENT, 169, "1938, pp. 155-69", "cand-10234")
    add_mention(NOTES_SEGMENT, 169, "1939, pp. 24-31", "cand-10235")
    add_mention(NOTES_SEGMENT, 169, "stimulating article on him", "cand-10237")
    add_mention(NOTES_SEGMENT, 169, "Aurelio Lepre", "cand-10236")
    add_mention(NOTES_SEGMENT, 169, "Algarotti", "cand-0043", occurrence=1)
    add_mention(NOTES_SEGMENT, 170, "Bologna", "cand-3398")
    add_mention(NOTES_SEGMENT, 170, "Algarotti’s", "cand-0043")
    add_mention(NOTES_SEGMENT, 170, "Bosdari", "cand-10238")
    add_mention(NOTES_SEGMENT, 170, "1928, pp. 157-222", "cand-10239")

    note_template = by_id["st-chp14-p347-note1-bibliography"]
    note_template["original_quote"] = quote_on(source_lines, 169, "1 The literature on Algarotti is vast.")
    note_template["qualifiers"].update({
        "claim": "Haskell characterizes the literature on Algarotti as vast.",
        "qualification": "This is Haskell's assessment of the secondary literature; it does not independently establish the claims in the cited works.",
        "mentioned_candidate_ids": ["cand-0043"],
        "relation_candidate": False,
        "footnote_marker": "1",
        "footnote_printed_page": 347,
        "linked_body_statement_ids": ["st-chp14-p347-birth"],
    })

    # Separate explicit publication, dedication, and scholarship relations from the citation survey.
    note_specs = [
        ("st-chp14-p347-note1-memorie-posthumous-appearance", "cand-10228", "cand-0043", "appeared_six_years_after_death_of",
         "Six years after his death appeared Michelessi’s Memorie", "Haskell reports that Michelessi's Memorie appeared six years after Algarotti's death.", True,
         "The relative date is Haskell's report; the work and its publication history were not independently checked.",
         ["cand-10227", "cand-10228", "cand-0043"], "The note explicitly places the Memorie six years after Algarotti's death; preserve the relative date as reported.",
         {"citations": [{"work_candidate_id": "cand-10228", "author_candidate_id": "cand-10227", "relative_to_person_candidate_id": "cand-0043"}]}),
        ("st-chp14-p347-note1-memorie-in-palese-edition", "cand-10228", "cand-10229", "included_in_first_volume_of",
         "in 1791 this was included in the first volume of the seventeen-volume edition of Algarotti’s works", "Haskell says the Memorie was included in 1791 in the first volume of the seventeen-volume edition of Algarotti's works.", True,
         "'This' refers to Michelessi's Memorie. Haskell's bibliographic statement is transcribed; the edition was not independently consulted.",
         ["cand-10228", "cand-10229", "cand-0043"], "The note explicitly identifies the Memorie as included in the edition's first volume; retain the stated year.",
         {"date": "1791", "citations": [{"included_work_candidate_id": "cand-10228", "edition_candidate_id": "cand-10229"}]}),
        ("st-chp14-p347-note1-edition-published-by-palese", "cand-10229", "cand-9798", "published_by",
         "published by Carlo Palese", "Haskell identifies Carlo Palese as the publisher of the seventeen-volume edition.", True,
         "This is Haskell's printed bibliographic attribution; the edition's title page was not independently checked.",
         ["cand-10229", "cand-9798"], "The note directly names Carlo Palese as publisher; the exact edition identity remains open pending bibliographic alignment.",
         {"date": "1791", "citations": [{"edition_candidate_id": "cand-10229", "publisher_candidate_id": "cand-9798"}]}),
        ("st-chp14-p347-note1-edition-published-in-venice", "cand-10229", "cand-2719", "published_in",
         "published by Carlo Palese in Venice", "Haskell locates publication of the seventeen-volume edition in Venice.", True,
         "This is the city stated in Haskell's note, not independently verified from the edition.",
         ["cand-10229", "cand-2719"], "The note explicitly gives Venice as the publication place for this edition.",
         {"date": "1791", "citations": [{"edition_candidate_id": "cand-10229", "place_candidate_id": "cand-2719"}]}),
        ("st-chp14-p347-note1-farsetti-life-authorship", "cand-10230", "cand-1013", "authored_by",
         "There is also a short and rare Latin life by T. G. Farsetti", "Haskell lists a short, rare Latin life of Francesco Algarotti by T. G. Farsetti.", True,
         "The title and edition are absent; the subject is inferred from the note's explicit focus on literature about Algarotti. The life was not independently consulted.",
         ["cand-10230", "cand-1013", "cand-0043"], "Haskell explicitly attributes the listed Latin life to Farsetti; its full identity remains unresolved.",
         {"citations": [{"work_candidate_id": "cand-10230", "author_candidate_id": "cand-1013"}]}),
        ("st-chp14-p347-note1-farsetti-life-dedicated-to-bonomo", "cand-10230", "cand-0040", "dedicated_to",
         "dedicated to Francesco’s brother Bonomo", "Haskell says Farsetti's Latin life was dedicated to Bonomo, Francesco's brother.", True,
         "The dedication is reported in Haskell's note; neither the life nor its dedication page was independently consulted.",
         ["cand-10230", "cand-0040", "cand-0043"], "The printed note directly identifies Bonomo as the dedicatee; no additional identity is inferred.",
         {"citations": [{"work_candidate_id": "cand-10230", "dedicatee_candidate_id": "cand-0040"}]}),
        ("st-chp14-p347-note1-bonomo-death-date", "cand-0040", None, "died_in_1776",
         "Bonomo who died in 1776", "Haskell's note says Bonomo died in 1776.", False,
         "This is a source-reported biographical date, not independently verified.",
         ["cand-0040"], "",
         {"date": "1776"}),
        ("st-chp14-p347-note1-treat-life-authorship", "cand-10232", "cand-10231", "authored_by",
         "The only complete modern life is by Ida Treat", "Haskell identifies Ida Treat as the author of what he calls the only complete modern life of Algarotti.", True,
         "Preserve 'only complete' as Haskell's assessment; title, edition, and text were not supplied or independently consulted.",
         ["cand-10232", "cand-10231", "cand-0043"], "The note explicitly attributes this biography to Ida Treat; the comparative 'only complete' judgment is Haskell's.",
         {"citations": [{"work_candidate_id": "cand-10232", "author_candidate_id": "cand-10231"}]}),
        ("st-chp14-p347-note1-gabrielli-aesthetics-research", "cand-10233", "cand-0043", "examined_algarottis_aesthetics",
         "His aesthetics have been examined by Annamaria Gabrielli, 1938, pp. 155-69, and 1939, pp. 24-31", "Haskell reports that Annamaria Gabrielli examined Algarotti's aesthetics in the two cited studies from 1938 and 1939.", True,
         "The claim is Haskell's bibliographic report; titles and cited-page contents were not independently consulted.",
         ["cand-10233", "cand-0043", "cand-10234", "cand-10235"], "The note names Gabrielli and two publication locators as studies of Algarotti's aesthetics; preserve both years.",
         {"citations": [{"study_candidate_id": "cand-10234", "author_candidate_id": "cand-10233"}, {"study_candidate_id": "cand-10235", "author_candidate_id": "cand-10233"}]}),
        ("st-chp14-p347-note1-lepre-article-on-algarotti", "cand-10236", "cand-0043", "wrote_article_about",
         "there is a stimulating article on him by Aurelio Lepre, 1959, pp.", "Haskell notes a 1959 article on Algarotti by Aurelio Lepre.", True,
         "The source's continuation at L12 gives the cited range as pp. 80-99; the article was not independently consulted.",
         ["cand-10236", "cand-10237", "cand-0043"], "The note explicitly attributes an article on Algarotti to Lepre; the continued page range is cross-linked separately.",
         {"date": "1959", "citations": [{"article_candidate_id": "cand-10237", "author_candidate_id": "cand-10236", "page_range": "80-99"}],
          "cross_reference_segments": [BODY_SEGMENT], "cross_reference_statement_ids": ["st-chp14-p347-note1-continuation"]}),
    ]
    new_note_statements: list[dict] = []
    note_line = source_lines[168]
    for (statement_id, subject, object_, predicate, fragment, claim, relation, qualification,
         mentioned, relation_note, extra) in note_specs:
        new_note_statements.append(make_statement(
            note_template, statement_id, subject=subject, object_=object_, predicate=predicate,
            line=169, quote=quote_on(source_lines, 169, fragment), claim=claim,
            relation=relation, qualification=qualification, mentioned=mentioned,
            relation_note=relation_note, extra_qualifiers=extra,
        ))

    # Classify bibliographic locators and the continuation without treating them as history.
    note2 = by_id["st-chp14-p347-note2-bosdari"]
    note2["qualifiers"].update({
        "relation_candidate": False,
        "qualification": "This is a bibliographic locator for Haskell's discussion of Bologna and Algarotti's relationships; Bosdari's cited pages were not independently consulted.",
    })
    continuation = by_id["st-chp14-p347-note1-continuation"]
    continuation["qualifiers"].update({
        "relation_candidate": False,
        "qualification": "This is the physical continuation of note 1 on the same printed page. It completes the Lepre page locator and says further references follow; it is not an independent historical relation.",
    })
    continuation_refs = continuation["qualifiers"].setdefault("cross_reference_statement_ids", [])
    lepre_id = "st-chp14-p347-note1-lepre-article-on-algarotti"
    if lepre_id not in continuation_refs:
        continuation_refs.append(lepre_id)

    # Keep the note marker on the biographical sentence while preserving that it is guidance, not evidence.
    birth = by_id["st-chp14-p347-birth"]
    note_ids = ["st-chp14-p347-note1-bibliography", "st-chp14-p347-note1-continuation"] + [r["statement_id"] for r in new_note_statements]
    q_birth = birth["qualifiers"]
    for key in ("footnote_note_statement_ids",):
        current = q_birth.setdefault(key, [])
        for note_id in note_ids:
            if note_id not in current:
                current.append(note_id)
    for ref in q_birth.get("footnote_refs", []):
        if ref.get("footnote_marker") == "1":
            current = ref.setdefault("footnote_note_statement_ids", [])
            for note_id in note_ids:
                if note_id not in current:
                    current.append(note_id)

    # Separate the two explicit historical relations embedded in Haskell's characterization.
    patronage = by_id["st-chp14-p347-patronage-tensions"]
    patronage["qualifiers"].update({
        "relation_candidate": False,
        "qualification": "Haskell's interpretive social and intellectual profile. The explicit friendship and rare-presence claims are captured separately as source-limited relation candidates; the unnamed classes are not turned into identified persons.",
    })
    receptive = by_id["st-chp14-p347-receptive-character"]
    receptive["original_quote"] = quote_on(source_lines, 8, "Above all the very weaknesses of his reasoning power and temperament made him unable to choose between the opposing tensions which he tried so hard to reconcile.")
    receptive["qualifiers"].update({
        "source_line_start": 8, "source_line_end": 8,
        "claim": "Haskell attributes Algarotti's inability to choose between opposing tendencies to perceived weaknesses of reasoning and temperament.",
        "qualification": "This is Haskell's psychological interpretation, not a direct self-description or independently verified diagnosis.",
        "mentioned_candidate_ids": ["cand-0043"],
        "relation_candidate": False,
    })

    body_template = copy.deepcopy(patronage)
    friend_id = "st-chp14-p347-algarotti-intimate-friend-of-princes-patricians"
    rarely_id = "st-chp14-p347-algarotti-rarely-present-in-venice"
    receptive_id = "st-chp14-p347-receptive-to-new-european-experiences"
    research_id = "st-chp14-p347-research-agenda-on-algarotti"
    body_new = [
        make_statement(body_template, friend_id, subject="cand-0043", object_=None,
            predicate="intimate_friend_of_unnamed_princes_and_patricians", line=7,
            quote=quote_on(source_lines, 7, "the intimate friend of princes and patricians"),
            claim="Haskell characterizes Algarotti as an intimate friend of princes and patricians.", relation=True,
            qualification="The social classes are named, but no individuals or bounded group are identified.",
            mentioned=["cand-0043"], relation_note="Source-explicit friendship claim with an open endpoint; do not infer specific princes or patricians.",
            extra_qualifiers={"open_endpoint_reason": "The source names only broad social classes, not individual friends or a bounded group."}),
        make_statement(body_template, rarely_id, subject="cand-0043", object_="cand-2719",
            predicate="was_rarely_present_in", line=8,
            quote=quote_on(source_lines, 8, "though rarely in Venice"),
            claim="Haskell says Algarotti was rarely in Venice.", relation=True,
            qualification="This is Haskell's qualified characterization; no frequency or date range is specified.",
            mentioned=["cand-0043", "cand-2719"], relation_note="A source-reported geographic presence claim; retain 'rarely' and do not infer residence dates."),
        make_statement(body_template, receptive_id, subject="cand-0043", object_=None,
            predicate="authorially_characterized_as_receptive_to_new_experiences", line=8,
            quote=quote_on(source_lines, 8, "His was an exceptionally receptive character, open to all the new experiences that were coming to the fore in Europe,"),
            claim="Haskell describes Algarotti as exceptionally receptive to new experiences emerging in Europe.", relation=False,
            qualification="This is Haskell's interpretive characterization, not a relation to a specific movement or set of ideas.",
            mentioned=["cand-0043", "cand-3462"]),
        make_statement(body_template, research_id, subject="cand-0043", object_=None,
            predicate="authorial_research_agenda", line=8,
            quote=quote_on(source_lines, 8, "and in evaluating his influence on the painters of the day it is therefore important to investigate what were his artistic ideas at various stages in his life, and also when exactly he came into contact with the painters of Venice."),
            claim="Haskell argues that evaluating Algarotti's influence requires studying his artistic ideas across life stages and when he met painters in Venice.", relation=False,
            qualification="This is Haskell's proposed research agenda, not a claim that supplies dates or identifies the painters beyond other statements on the page.",
            mentioned=["cand-0043", "cand-2719"]),
    ]

    new_ids = {row["statement_id"] for row in new_note_statements + body_new}
    if new_ids & set(by_id):
        raise SystemExit(f"new statement ID already exists: {sorted(new_ids & set(by_id))}")
    for row in new_note_statements:
        if row["original_quote"] not in note_line:
            raise SystemExit(f"new note quote is not anchored at L169: {row['statement_id']}")
    for row in body_new:
        q = row["qualifiers"]
        if row["original_quote"] not in "\n".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])]):
            raise SystemExit(f"new body quote is not anchored: {row['statement_id']}")

    # Insert new rows immediately after their corresponding source statements.
    additions_after = {
        "st-chp14-p347-note1-bibliography": new_note_statements,
        "st-chp14-p347-patronage-tensions": body_new[:2],
        "st-chp14-p347-receptive-character": body_new[2:],
    }
    ordered: list[dict] = []
    for row in rows:
        ordered.append(row)
        ordered.extend(additions_after.get(row["statement_id"], []))
    if len({row["statement_id"] for row in ordered}) != len(ordered):
        raise SystemExit("statement_id is not unique after planned additions")

    known_candidates = set()
    with (ROOT / "04-knowledge" / "tables" / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        known_candidates = {row["candidate_id"] for row in csv.DictReader(handle)}
    for mention in new_mentions:
        if mention["candidate_id"] not in known_candidates:
            raise SystemExit(f"unknown candidate in mention: {mention['candidate_id']}")
    payload_statements = dump_jsonl(ordered)
    mention_rows.extend(new_mentions)
    mention_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(mention_buffer, fieldnames=mention_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(mention_rows)
    payload_mentions = ("\ufeff" if has_bom else "") + mention_buffer.getvalue()
    payload_mentions = payload_mentions.encode("utf-8")

    print("dry-run preview:")
    print(f"classified existing unset rows: {len(UNCLASSIFIED_IDS)}")
    print(f"added atomic statements: {len(new_note_statements) + len(body_new)} (relation candidates={sum(r['qualifiers']['relation_candidate'] for r in new_note_statements + body_new)})")
    print(f"added exact mentions: {len(new_mentions)}")
    print(f"statements={len(ordered)} sha256={hashlib.sha256(payload_statements).hexdigest()}")
    print(f"mentions={len(mention_rows)} sha256={hashlib.sha256(payload_mentions).hexdigest()}")
    if not args.apply:
        return

    statement_backup = STATEMENTS.with_name(STATEMENTS.name + STATEMENT_BACKUP_SUFFIX)
    mention_backup = MENTIONS.with_name(MENTIONS.name + MENTION_BACKUP_SUFFIX)
    if statement_backup.exists() or mention_backup.exists():
        raise SystemExit("a recovery backup for this batch already exists")
    shutil.copy2(STATEMENTS, statement_backup)
    shutil.copy2(MENTIONS, mention_backup)
    try:
        STATEMENTS.write_bytes(payload_statements)
        MENTIONS.write_bytes(payload_mentions)
    except Exception:
        shutil.copy2(statement_backup, STATEMENTS)
        shutil.copy2(mention_backup, MENTIONS)
        raise
    print(f"applied; recovery copies: {statement_backup.relative_to(ROOT)}, {mention_backup.relative_to(ROOT)}")
    print(f"post-write hashes: statements={sha(STATEMENTS)} mentions={sha(MENTIONS)}")


if __name__ == "__main__":
    main()
