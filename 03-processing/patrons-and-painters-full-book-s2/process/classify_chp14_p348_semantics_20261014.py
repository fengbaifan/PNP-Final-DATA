#!/usr/bin/env python3
"""Review Chapter 14 p.348 statements and exact entity mentions."""
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
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY_SEGMENT = "chp-14:14_CHP-14_intro:l14-21"
NOTES_SEGMENT = "chp-14:14_CHP-14_intro:l168-220"
BACKUP_SUFFIX = ".bak-s2-ch14-p348-semantic-review-20261014"

EXPECTED = {
    STATEMENTS: "7ac024e4eef118fc9b64351ce25eb14c33d1f0eb724ec953a8e05134016ae404",
    MENTIONS: "1cd2709f8deda07b0b6ca14ec8fa9ea756a3b5a40862a832d6ff6936b51e2b94",
    SOURCE: "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7",
    PDF: "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0",
}

UNCLASSIFIED = {
    "st-chp14-p348-return-to-veneto",
    "st-chp14-p348-early-taste",
    "st-chp14-p348-florence-visit",
    "st-chp14-p348-raphael-titian-bartolommeo",
    "st-chp14-p348-revolt-against-baroque",
    "st-chp14-p348-judgement-shaken",
    "st-chp14-p348-carracci-domenichino",
    "st-chp14-p348-baroque-equivalence",
    "st-chp14-p348-roman-scholars",
    "st-chp14-p348-first-approach-to-painting",
    "st-chp14-p348-limited-artist-contact",
    "st-chp14-p348-note1-letters",
    "st-chp14-p348-note2-letter",
    "st-chp14-p348-note3-letters",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validation; default is dry-run")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} sha256={actual}, expected={expected}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    statement_rows = load_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("statement_id is not unique before apply")
    missing = UNCLASSIFIED - set(by_id)
    if missing:
        raise SystemExit(f"missing target statements: {sorted(missing)}")
    for statement_id in UNCLASSIFIED:
        row = by_id[statement_id]
        if "relation_candidate" in row.get("qualifiers", {}):
            raise SystemExit(f"target is already classified: {statement_id}")

    segment_rows = load_jsonl(SEGMENTS)
    bounds = {r["segment_id"]: (int(r["line_start"]), int(r["line_end"])) for r in segment_rows}
    if BODY_SEGMENT not in bounds or NOTES_SEGMENT not in bounds:
        raise SystemExit("expected p.348 source segments are missing")
    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        mention_fields = list(reader.fieldnames or [])
        mention_rows = list(reader)
    has_bom = MENTIONS.read_bytes().startswith(b"\xef\xbb\xbf")
    if any(r["segment_id"] == BODY_SEGMENT for r in mention_rows):
        raise SystemExit("p.348 body segment already contains mentions; review before applying")
    note_start, note_end = bounds[NOTES_SEGMENT]
    note_line_offsets: dict[int, tuple[int, int]] = {}
    cursor = 0
    for line_number in range(note_start, note_end + 1):
        line_length = len(source_lines[line_number - 1])
        note_line_offsets[line_number] = (cursor, cursor + line_length)
        cursor += line_length + 1
    for row in mention_rows:
        if row["segment_id"] != NOTES_SEGMENT:
            continue
        span_start, span_end = int(row["start_char"]), int(row["end_char"])
        if any(span_start < note_line_offsets[line][1] and span_end > note_line_offsets[line][0] for line in (171, 172, 173)):
            raise SystemExit("existing p.348 note-line mention span found; review before applying")

    new_rows: list[dict] = []
    updates: dict[str, dict] = {}

    def update_statement(statement_id: str, *, relation: bool, claim: str | None = None,
                         original_quote: str | None = None, subject: str | None = None,
                         predicate: str | None = None, object_: str | None = None,
                         mentioned: list[str] | None = None, qualification: str | None = None,
                         relation_note: str | None = None) -> None:
        row = by_id[statement_id]
        q = copy.deepcopy(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        if claim is not None:
            q["claim"] = claim
        if mentioned is not None:
            q["mentioned_candidate_ids"] = mentioned
        if qualification is not None:
            q["qualification"] = qualification
        if relation_note is not None:
            q["relation_candidate_note"] = relation_note
        elif not relation:
            q.pop("relation_candidate_note", None)
        updated = copy.deepcopy(row)
        updated["qualifiers"] = q
        if original_quote is not None:
            updated["original_quote"] = original_quote
        if subject is not None:
            updated["subject_candidate_id"] = subject
        if predicate is not None:
            updated["predicate"] = predicate
        if object_ is not None:
            updated["object_candidate_id"] = object_
        updates[statement_id] = updated

    def add_statement(statement_id: str, template_id: str, *, line: int, quote: str,
                      claim: str, relation: bool, subject: str | None,
                      predicate: str, object_: str | None, mentioned: list[str],
                      qualification: str, relation_note: str = "") -> None:
        if statement_id in by_id or any(r["statement_id"] == statement_id for r in new_rows):
            raise SystemExit(f"new statement ID already exists: {statement_id}")
        source_line = source_lines[line - 1]
        if quote not in source_line:
            raise SystemExit(f"quote not found at L{line}: {quote!r}")
        row = copy.deepcopy(by_id[template_id])
        row.update({
            "statement_id": statement_id,
            "segment_id": BODY_SEGMENT,
            "subject_candidate_id": subject,
            "object_candidate_id": object_,
            "predicate": predicate,
            "original_quote": quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        })
        q = row["qualifiers"]
        q.clear()
        q.update({
            "source_line_start": line,
            "source_line_end": line,
            "printed_page": 348,
            "pdf_physical_page": 2,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "biographical narrative",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation,
        })
        if relation and relation_note:
            q["relation_candidate_note"] = relation_note
        new_rows.append(row)

    # Keep the return to the Veneto, route, and first recorded artistic interest distinct.
    update_statement(
        "st-chp14-p348-return-to-veneto", relation=True,
        claim="After leaving Bologna, Algarotti returned to the Veneto for a short time.",
        original_quote="After leaving Bologna Algarotti returned to the Veneto for a short time.",
        subject="cand-0061", predicate="returned_to", object_="cand-4207",
        mentioned=["cand-0061", "cand-3398", "cand-4207"],
        qualification="Haskell gives no exact date or duration beyond 'a short time'.",
        relation_note="A source-reported return to the Veneto; keep distinct from the following multi-city travel route.",
    )
    route_quote = "He travelled between Venice, Padua, Vicenza and Verona"
    for suffix, place_id, place_name in [
        ("venice", "cand-2719", "Venice"),
        ("padua", "cand-1803", "Padua"),
        ("vicenza", "cand-2769", "Vicenza"),
        ("verona", "cand-7661", "Verona"),
    ]:
        add_statement(
            f"st-chp14-p348-travel-{suffix}", "st-chp14-p348-return-to-veneto",
            line=16, quote=route_quote,
            claim=f"Haskell says Algarotti travelled to {place_name} during this itinerary.",
            relation=True, subject="cand-0061", predicate="travelled_to", object_=place_id,
            mentioned=["cand-0061", place_id],
            qualification="The source supplies the route but no date for each city visit.",
            relation_note="One destination in the printed route between Venice, Padua, Vicenza, and Verona.",
        )
    add_statement(
        "st-chp14-p348-first-interest-in-arts", "st-chp14-p348-return-to-veneto",
        line=16, quote="and it is now that we first hear of his interest in the arts.",
        claim="Haskell first records Algarotti's interest in the arts in this period.",
        relation=False, subject="cand-0061", predicate="first_artistic_interest_recorded", object_=None,
        mentioned=["cand-0061"],
        qualification="This marks the point in Haskell's narrative; it does not date the beginning of Algarotti's interest.",
    )

    update_statement(
        "st-chp14-p348-early-taste", relation=False,
        claim="Haskell characterizes Algarotti's expressed taste as conventional among cultivated dilettantes and links his named painter preferences to his upbringing and the Veneto's early neo-classical tendency.",
        mentioned=["cand-0061", "cand-2755", "cand-2124", "cand-1807", "cand-2719", "cand-3398", "cand-6439", "cand-4207"],
        qualification="This is Haskell's evaluative and contextual characterization; it does not establish a formal relation among the named artists, places, and movement.",
    )
    update_statement(
        "st-chp14-p348-florence-visit", relation=True,
        claim="Toward the end of 1733, Algarotti went to Florence and stayed there for three months.",
        original_quote="Towards the end of 1733 he went to Florence, where he stayed three months.",
        subject="cand-0061", predicate="visited_and_stayed_at", object_="cand-3397",
        mentioned=["cand-0061", "cand-3397"],
        qualification="Haskell dates the visit to late 1733 and gives a three-month duration.",
        relation_note="A source-reported visit and stay; the same passage separately evaluates works seen there.",
    )
    add_statement(
        "st-chp14-p348-cellini-perseus-assessment", "st-chp14-p348-florence-visit",
        line=17, quote="He admired Cellini’s Perseus",
        claim="Haskell says Algarotti admired Cellini's Perseus during the Florence visit.",
        relation=False, subject="cand-0061", predicate="artwork_assessment", object_="cand-10240",
        mentioned=["cand-0061", "cand-0621", "cand-10240"],
        qualification="The source reports an aesthetic response but supplies no version or further work identification; admiration alone is not a formal relation in the current relation schema.",
    )
    add_statement(
        "st-chp14-p348-baptistery-doors-assessment", "st-chp14-p348-florence-visit",
        line=17, quote="and the doors of the Baptistery",
        claim="Haskell says Algarotti admired the doors of the Baptistery in Florence.",
        relation=False, subject="cand-0061", predicate="artwork_assessment", object_="cand-10241",
        mentioned=["cand-0061", "cand-10241", "cand-3397"],
        qualification="The source does not identify the gate, maker, or version; this aesthetic response is not a formal relation in the current relation schema.",
    )

    update_statement(
        "st-chp14-p348-move-to-rome", relation=True,
        claim="In February 1734, Algarotti moved to Rome.",
        subject="cand-0068", predicate="moved_to", object_="cand-4490",
        mentioned=["cand-0068", "cand-4490"],
        qualification="The source supplies the month and year.",
        relation_note="A source-reported move to Rome; the next claims describe his letters and responses there.",
    )
    update_statement(
        "st-chp14-p348-raphael-titian-bartolommeo", relation=False,
        claim="Haskell reports that Algarotti found Raphael's St John the Baptist disappointing after the S. Cecilia in Bologna.",
        original_quote="Raphael’s St John the Baptist disappointing after the S. Cecilia in Bologna;",
        subject="cand-0061", predicate="comparative_artwork_assessment", object_="cand-10242",
        mentioned=["cand-0061", "cand-2105", "cand-10242", "cand-10243", "cand-3398"],
        qualification="The exact versions of both paintings are unresolved; this is an attributed aesthetic comparison, not a formal relation.",
    )
    add_statement(
        "st-chp14-p348-titian-paintings-assessment", "st-chp14-p348-raphael-titian-bartolommeo",
        line=18, quote="talked of the excitement of discovering the Titians in the Grand Ducal collections",
        claim="Haskell says Algarotti was excited to discover unidentified Titian paintings in the Grand Ducal collections at Florence.",
        relation=False, subject="cand-0061", predicate="artwork_assessment", object_="cand-10244",
        mentioned=["cand-0061", "cand-10244", "cand-10245"],
        qualification="The paintings and collection are not individually identified; an aesthetic response does not establish a formal relation.",
    )
    add_statement(
        "st-chp14-p348-fra-bartolommeo-assessment", "st-chp14-p348-raphael-titian-bartolommeo",
        line=18, quote="and above all he was overwhelmed by the greatness of Fra Bartolommeo, of whom he now heard for the first time.",
        claim="Haskell says Algarotti was deeply impressed by Fra Bartolommeo, whom he had just heard of for the first time.",
        relation=False, subject="cand-0061", predicate="artist_assessment", object_="cand-0252",
        mentioned=["cand-0061", "cand-0252"],
        qualification="The passage reports an aesthetic response and first hearing, not a personal encounter or influence relation.",
    )

    update_statement(
        "st-chp14-p348-roman-scholars", relation=True,
        claim="Bottari was one of an unnamed group of scholars and antiquarians in Rome.",
        original_quote="Bottari was one of a group of scholars and antiquarians in Rome",
        subject="cand-0417", predicate="member_of", object_="cand-10247",
        mentioned=["cand-0417", "cand-10247", "cand-4490"],
        qualification="Haskell names Bottari as a member of a descriptive group but does not identify it as an institution or academy; the group's type remains unresolved.",
        relation_note="Explicit group membership in Haskell's account; keep the endpoint as an unnamed source-defined group pending S3 identity and type review.",
    )
    add_statement(
        "st-chp14-p348-roman-scholars-opposition", "st-chp14-p348-roman-scholars",
        line=21, quote="who disapproved of contemporary art on theoretical grounds",
        claim="Haskell says the unnamed Roman scholars and antiquarians disapproved of contemporary art on theoretical grounds.",
        relation=False, subject="cand-10247", predicate="group_view_of_contemporary_art", object_=None,
        mentioned=["cand-10247", "cand-4490"],
        qualification="This records Haskell's characterization of an unnamed group; no specific contemporary artwork or institution is identified.",
    )
    add_statement(
        "st-chp14-p348-roman-scholars-neoclassicism", "st-chp14-p348-roman-scholars",
        line=21, quote="for a full generation before Winckelmann and Mengs, were preparing the way for neo-classicism",
        claim="Haskell says the unnamed Roman group prepared the way for neo-classicism before Winckelmann and Mengs.",
        relation=True, subject="cand-10247", predicate="prepared_way_for", object_="cand-6439",
        mentioned=["cand-10247", "cand-2816", "cand-1652", "cand-6439"],
        qualification="This is Haskell's broad historical interpretation; the unnamed group's identity and composition remain unresolved.",
        relation_note="Source-attributed intellectual influence claim; preserve Haskell's 'preparing the way' wording and do not convert it to direct collaboration with Winckelmann or Mengs.",
    )

    # Remaining unset statements are classified as non-relational assessments or citation locators.
    update_statement("st-chp14-p348-revolt-against-baroque", relation=False,
                     qualification="Haskell contrasts Algarotti's self-characterization with his own assessment of the wider revolt against the Baroque; this is contextual interpretation, not an entity relation.")
    update_statement("st-chp14-p348-judgement-shaken", relation=False,
                     qualification="This is an attributed report about Algarotti's changing judgement of pictures as a general class; no specific work or relation endpoint is identified.")
    update_statement("st-chp14-p348-carracci-domenichino", relation=False,
                     qualification="This is Haskell's comparative account of Algarotti's changing esteem for named painters; it does not establish a relation among the painters.")
    update_statement("st-chp14-p348-baroque-equivalence", relation=False,
                     qualification="This is a critical comparison between named artists and writers; the analogy is not a formal relation among them.")
    update_statement("st-chp14-p348-first-approach-to-painting", relation=False,
                     qualification="The passage contrasts broad unnamed classes of scholars, artists, and collectors; it identifies no person-to-person relation beyond Bottari, recorded separately.")
    update_statement("st-chp14-p348-limited-artist-contact", relation=False,
                     qualification="This is a qualified negative report about contact with unnamed living artists; no identifiable endpoint is supplied.")
    update_statement("st-chp14-p348-note1-letters", relation=False,
                     qualification="Bibliographic locator for a cited group of letters and printed volumes; the letters and edition were not independently consulted.")
    update_statement("st-chp14-p348-note2-letter", relation=False,
                     qualification="Bibliographic and repository locator for a cited letter; the manuscript and repository catalogue were not independently consulted.")
    update_statement("st-chp14-p348-note3-letters", relation=False,
                     qualification="Bibliographic locator for cited letters and printed volumes; the letters and edition were not independently consulted.")

    mention_specs = [
        # Body, source segment L14-L21. The offset is computed against the full segment text.
        (BODY_SEGMENT, 15, "Francesco’s", "cand-0061", "Possessive reference to Algarotti in the preceding sentence.", 0),
        (BODY_SEGMENT, 16, "Bologna", "cand-3398", "", 0),
        (BODY_SEGMENT, 16, "Algarotti", "cand-0061", "", 0),
        (BODY_SEGMENT, 16, "the Veneto", "cand-4207", "", 0),
        (BODY_SEGMENT, 16, "Venice", "cand-2719", "", 0),
        (BODY_SEGMENT, 16, "Padua", "cand-1803", "", 0),
        (BODY_SEGMENT, 16, "Vicenza", "cand-2769", "", 0),
        (BODY_SEGMENT, 16, "Verona", "cand-7661", "", 0),
        (BODY_SEGMENT, 16, "Veronese", "cand-2755", "Adjectival reference to Paolo Veronese.", 0),
        (BODY_SEGMENT, 16, "Guido Reni", "cand-2124", "", 0),
        (BODY_SEGMENT, 16, "Venetian", "cand-2719", "Adjectival geographic reference.", 0),
        (BODY_SEGMENT, 16, "Bolognese", "cand-3398", "Adjectival geographic reference.", 0),
        (BODY_SEGMENT, 16, "Palladio", "cand-1807", "", 0),
        (BODY_SEGMENT, 16, "neo-classicism", "cand-6439", "", 0),
        (BODY_SEGMENT, 16, "the Veneto", "cand-4207", "", 1),
        (BODY_SEGMENT, 17, "Palladio", "cand-1807", "", 0),
        (BODY_SEGMENT, 17, "Vicenza", "cand-2769", "", 0),
        (BODY_SEGMENT, 17, "Palladio", "cand-1807", "", 1),
        (BODY_SEGMENT, 17, "Prussia", "cand-10246", "", 0),
        (BODY_SEGMENT, 17, "Florence", "cand-3397", "", 0),
        (BODY_SEGMENT, 17, "Cellini", "cand-0621", "", 0),
        (BODY_SEGMENT, 17, "Perseus", "cand-10240", "", 0),
        (BODY_SEGMENT, 17, "Baptistery", "cand-10241", "", 0),
        (BODY_SEGMENT, 18, "Raphael", "cand-2105", "", 0),
        (BODY_SEGMENT, 18, "St John the Baptist", "cand-10242", "", 0),
        (BODY_SEGMENT, 18, "S. Cecilia", "cand-10243", "", 0),
        (BODY_SEGMENT, 18, "Bologna", "cand-3398", "", 0),
        (BODY_SEGMENT, 18, "Titians", "cand-10244", "Plural reference to unidentified Titian paintings.", 0),
        (BODY_SEGMENT, 18, "Grand Ducal collections", "cand-10245", "Collection identity and type remain unresolved.", 0),
        (BODY_SEGMENT, 18, "Fra Bartolommeo", "cand-0252", "", 0),
        (BODY_SEGMENT, 19, "Rome", "cand-4490", "", 0),
        (BODY_SEGMENT, 19, "his brother", "cand-0040", "Kinship reference to Bonomo from the preceding page context.", 0),
        (BODY_SEGMENT, 19, "Francesco\nZanotti", "cand-2864", "Name split across adjacent S0 lines.", 0),
        (BODY_SEGMENT, 20, "St Peter’s", "cand-6960", "", 0),
        (BODY_SEGMENT, 20, "Pantheon", "cand-4236", "", 0),
        (BODY_SEGMENT, 20, "Baroque", "cand-4500", "", 0),
        (BODY_SEGMENT, 20, "Algarotti", "cand-0068", "", 0),
        (BODY_SEGMENT, 20, "Baroque", "cand-4500", "", 1),
        (BODY_SEGMENT, 20, "Carracci", "cand-0576", "", 0),
        (BODY_SEGMENT, 20, "Galleria Farnese", "cand-5423", "", 0),
        (BODY_SEGMENT, 20, "Domenichino", "cand-0932", "", 0),
        (BODY_SEGMENT, 20, "Bolognese", "cand-3398", "Adjectival geographic reference.", 0),
        (BODY_SEGMENT, 20, "Monti", "cand-1698", "", 0),
        (BODY_SEGMENT, 20, "Torelli", "cand-2645", "", 0),
        (BODY_SEGMENT, 20, "Bernini", "cand-0295", "", 0),
        (BODY_SEGMENT, 20, "Borromini", "cand-0404", "", 0),
        (BODY_SEGMENT, 20, "Fulvio Testi", "cand-2560", "", 0),
        (BODY_SEGMENT, 21, "Marino", "cand-1548", "", 0),
        (BODY_SEGMENT, 21, "Giovanni Bottari", "cand-0417", "", 0),
        (BODY_SEGMENT, 21, "Rome", "cand-4490", "", 0),
        (BODY_SEGMENT, 21, "group of scholars and antiquarians in Rome", "cand-10247", "Unnamed group described by Haskell; not assumed to be an institution.", 0),
        (BODY_SEGMENT, 21, "Winckelmann", "cand-2816", "", 0),
        (BODY_SEGMENT, 21, "Mengs", "cand-1652", "", 0),
        (BODY_SEGMENT, 21, "neo-classicism", "cand-6439", "", 0),
        (BODY_SEGMENT, 21, "Algarotti’s", "cand-0068", "Possessive reference.", 0),
        (BODY_SEGMENT, 21, "Algarotti", "cand-0068", "", 1),
        # Notes on this page share the existing p.347 notes segment.
        (NOTES_SEGMENT, 171, "his letters to F. M. Zanotti", "cand-10248", "Descriptive candidate for the cited letter group.", 0),
        (NOTES_SEGMENT, 171, "F. M. Zanotti", "cand-2864", "", 0),
        (NOTES_SEGMENT, 171, "Opere, XI and XII", "cand-10249", "Printed volume locator.", 0),
        (NOTES_SEGMENT, 172, "Letter of 22 February 1734 to his brother Bonomo", "cand-10250", "Descriptive candidate for the cited letter.", 0),
        (NOTES_SEGMENT, 172, "Bonomo", "cand-0040", "", 0),
        (NOTES_SEGMENT, 172, "Treviso", "cand-10251", "Place included in the printed repository citation; no separate place candidate is supplied here.", 0),
        (NOTES_SEGMENT, 172, "Archivio Comunale, MSS. 1256", "cand-10251", "Repository and shelfmark as printed.", 0),
        (NOTES_SEGMENT, 173, "letters to F. M. and Eustachio Zanotti and Antonio Conti from Rome between February and June 1734", "cand-10252", "Descriptive candidate for the cited letter group.", 0),
        (NOTES_SEGMENT, 173, "F. M.", "cand-2864", "", 0),
        (NOTES_SEGMENT, 173, "Eustachio Zanotti", "cand-2863", "", 0),
        (NOTES_SEGMENT, 173, "Antonio Conti", "cand-0826", "", 0),
        (NOTES_SEGMENT, 173, "Rome", "cand-4490", "", 0),
        (NOTES_SEGMENT, 173, "Opere, X and XII", "cand-10253", "Printed volume locator.", 0),
    ]

    texts: dict[str, str] = {}
    for segment_id in (BODY_SEGMENT, NOTES_SEGMENT):
        start, end = bounds[segment_id]
        texts[segment_id] = "\n".join(source_lines[start - 1:end])

    new_mentions: list[dict] = []
    existing_ids = {r["mention_id"] for r in mention_rows}
    next_number = 1
    for segment_id, line_number, phrase, candidate_id, note, occurrence in mention_specs:
        if not bounds[segment_id][0] <= line_number <= bounds[segment_id][1]:
            raise SystemExit(f"mention line outside segment: L{line_number} / {segment_id}")
        source_line = source_lines[line_number - 1]
        line_start, _ = bounds[segment_id]
        positions: list[int] = []
        if "\n" in phrase:
            haystack = texts[segment_id]
        else:
            haystack = source_line
        pos = 0
        while True:
            found = haystack.find(phrase, pos)
            if found < 0:
                break
            positions.append(found)
            pos = found + 1
        if occurrence >= len(positions):
            raise SystemExit(f"mention phrase occurrence missing at L{line_number}: {phrase!r}; found={len(positions)}")
        if "\n" in phrase:
            start_char = positions[occurrence]
        else:
            segment_offset = sum(len(source_lines[i - 1]) + 1 for i in range(line_start, line_number))
            start_char = segment_offset + positions[occurrence]
        mention_id = f"m-s2-ch14-p348-{next_number:03d}"
        if mention_id in existing_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": phrase,
            "start_char": str(start_char),
            "end_char": str(start_char + len(phrase)),
            "note": note,
        })
        next_number += 1

    all_ids = set(by_id) | {r["statement_id"] for r in new_rows}
    if len(all_ids) != len(by_id) + len(new_rows):
        raise SystemExit("new statement IDs are not unique")
    mention_candidate_ids = {r["candidate_id"] for r in mention_rows} | {r["candidate_id"] for r in new_mentions}
    candidate_rows = {r["candidate_id"] for r in csv.DictReader((ROOT / "04-knowledge" / "tables" / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))}
    if mention_candidate_ids - candidate_rows:
        raise SystemExit(f"mention candidate IDs missing from registry: {sorted(mention_candidate_ids - candidate_rows)}")

    for statement_id, row in updates.items():
        q = row["qualifiers"]
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1:end]):
            raise SystemExit(f"updated quote mismatch: {statement_id}")
    projected = [updates.get(row["statement_id"], row) for row in statement_rows] + new_rows
    projected.extend([])
    for row in projected:
        q = row.get("qualifiers") or {}
        if q.get("printed_page") == 348 and q.get("relation_candidate") is None:
            raise SystemExit(f"p.348 statement remains unclassified: {row['statement_id']}")

    mention_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(mention_buffer, fieldnames=mention_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(mention_rows + new_mentions)
    mention_payload = mention_buffer.getvalue().encode("utf-8")
    if has_bom:
        mention_payload = b"\xef\xbb\xbf" + mention_payload

    statement_payload = dump_jsonl(projected)
    print(f"mode={'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"updated statements={len(updates)}; added atomic statements={len(new_rows)}; added exact mentions={len(new_mentions)}")
    print(f"p.348 statements after apply={sum((r.get('qualifiers') or {}).get('printed_page') == 348 for r in projected)}; unset=0")
    print(f"mention segments={BODY_SEGMENT}: {sum(r['segment_id']==BODY_SEGMENT for r in new_mentions)}, {NOTES_SEGMENT}: {sum(r['segment_id']==NOTES_SEGMENT for r in new_mentions)}")
    print(f"projected hashes: statements={hashlib.sha256(statement_payload).hexdigest()} mentions={hashlib.sha256(mention_payload).hexdigest()}")
    if not args.apply:
        return

    statement_backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    mention_backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    if statement_backup.exists() or mention_backup.exists():
        raise SystemExit("backup already exists; inspect before apply")
    shutil.copy2(STATEMENTS, statement_backup)
    shutil.copy2(MENTIONS, mention_backup)
    try:
        STATEMENTS.write_bytes(statement_payload)
        MENTIONS.write_bytes(mention_payload)
    except Exception:
        shutil.copy2(statement_backup, STATEMENTS)
        shutil.copy2(mention_backup, MENTIONS)
        raise
    print(f"backups: {statement_backup.name}; {mention_backup.name}")
    print(f"written hashes: statements={sha(STATEMENTS)} mentions={sha(MENTIONS)}")


if __name__ == "__main__":
    main()
