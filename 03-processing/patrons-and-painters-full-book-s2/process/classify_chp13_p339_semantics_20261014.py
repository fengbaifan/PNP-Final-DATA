#!/usr/bin/env python3
"""Review p.339 S2 claims, candidate endpoints, and mentions; dry-run by default."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l70-77"
SEGMENT_SHA256 = "43172602cf35b362d91811b6735bfb843abe37e012116206f32184edd14580bb"
PRE_HASHES = {
    STATEMENTS.name: "ef145e6542945acb6ee1c6101e49f4f918c4cb5479fd630de1170c9bd569ece5",
    CANDIDATES.name: "6061cd6c2390ef3f4865baafebe0f51dc7f475110c818d6fbc04a2553e53b5bd",
    MENTIONS.name: "4efe0a6646c96e54947de636f5a78ecbe01505d0327eb87463bb3541b50e23f9",
}
BACKUP_SUFFIX = ".bak-s2-ch13-p339-semantic-review-20261014"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def csv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    with tempfile.SpooledTemporaryFile(
        mode="w+", encoding="utf-8-sig", newline="", max_size=8 * 1024 * 1024
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        stream.seek(0)
        return stream.read().encode("utf-8-sig")


def make_statement(
    statement_id: str,
    predicate: str,
    subject: str,
    obj: str | None,
    claim: str,
    original_quote: str,
    source_line_start: int,
    source_line_end: int,
    relation_candidate: bool,
    mentioned_candidate_ids: list[str],
    qualification: str,
    speaker: str = "Haskell",
    text_layer: str = "authorial narrative",
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": source_line_start,
            "source_line_end": source_line_end,
            "printed_page": 339,
            "pdf_physical_page": 8,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned_candidate_ids,
            "ocr_corrections": [],
            "relation_candidate": relation_candidate,
        },
        "original_quote": original_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks")
    args = parser.parse_args()

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = digest(path)
        expected = PRE_HASHES[path.name]
        if actual != expected:
            raise SystemExit(f"preflight failed: {path.name} SHA-256 {actual} != {expected}")
    segment = next(
        (row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID),
        None,
    )
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.339 segment identity/hash changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: duplicate statement_id")
    local = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(local) != 23:
        raise SystemExit(f"preflight failed: expected 23 p.339 statements, found {len(local)}")
    unset = {
        row["statement_id"]
        for row in local
        if row.get("qualifiers", {}).get("relation_candidate") is None
    }
    decisions = {
        "st-chp13-p339-dante-illustrations-results-engaging-limited-interpretation": False,
        "st-chp13-p339-dante-medieval-iconography-difficult-for-artists": True,
        "st-chp13-p339-haskell-metastasio-illustrations-herald-romantic": False,
        "st-chp13-p339-novelli-goldoni-lower-social-world": True,
        "st-chp13-p339-other-illustrated-book-publishers-limited-artistic-influence": True,
        "st-chp13-p339-pinelli-library-famous-in-europe": True,
        "st-chp13-p339-pinelli-private-collector-patron": False,
        "st-chp13-p339-satirical-secretary-reads-vignette-as-jesuit-attack": True,
        "st-chp13-p339-zatta-activities-untraced-in-others-writings": False,
        "st-chp13-p339-zatta-indistinct-from-past": False,
        "st-chp13-p339-zatta-little-social-life": False,
        "st-chp13-p339-zatta-most-prolific-in-eighteenth-century-venice": False,
        "st-chp13-p339-zatta-parodied-symbolic-readings": True,
        "st-chp13-p339-zatta-prefaces-characterization": False,
        "st-chp13-p339-zatta-range-of-illustrated-books": True,
    }
    if unset != set(decisions):
        raise SystemExit(f"preflight failed: unexpected unset IDs: {sorted(unset ^ set(decisions))}")
    for statement_id, value in decisions.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = value

    new_candidates = [
        {
            "candidate_id": "cand-12154",
            "index_entry_id": "",
            "canonical_name": "Catalogues of Antonio Zatta's publishing output (unnamed group)",
            "index_page_range": "",
            "suggested_type": "archive",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell refers to Zatta's catalogues in the plural; p.339 note 4 identifies one 1790 catalogue (cand-10184). Keep the general group separate from that title; neither was independently consulted.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L75",
        },
        {
            "candidate_id": "cand-12155",
            "index_entry_id": "",
            "canonical_name": "Unnamed opponents Zatta mocked for finding Jesuits everywhere",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "A source-defined group of Zatta's unnamed enemies, described as finding Jesuits everywhere; no members or complete boundaries are supplied.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L72",
        },
        {
            "candidate_id": "cand-12156",
            "index_entry_id": "",
            "canonical_name": "Other Venetian publishers besides Albrizzi, Pasquali, and Zatta (unnamed group)",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell refers to many additional publishers without naming them; the group is explicitly distinct from Albrizzi, Pasquali, and Zatta.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L77",
        },
        {
            "candidate_id": "cand-12157",
            "index_entry_id": "",
            "canonical_name": "Fine illustrated books by other Venetian publishers (unnamed group)",
            "index_page_range": "",
            "suggested_type": "archive",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Publication group attributed to the unnamed publishers distinct from the three principal Venetian publishers; no individual titles are given.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L77",
        },
        {
            "candidate_id": "cand-12158",
            "index_entry_id": "",
            "canonical_name": "Artistic output discussed in Haskell's comparison of Venetian publishers",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "The broad artistic production that Haskell says the unnamed publishers influenced less strongly than Albrizzi, Pasquali, and Zatta; no medium or individual maker is specified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L77",
        },
        {
            "candidate_id": "cand-12159",
            "index_entry_id": "",
            "canonical_name": "Metastasio's works illustrated in Zatta's editions (unnamed group)",
            "index_page_range": "",
            "suggested_type": "archive",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "The textual works for which Novelli's illustrations appeared from 1781; individual titles and edition details are not identified in this passage.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L76",
        },
        {
            "candidate_id": "cand-12160",
            "index_entry_id": "",
            "canonical_name": "Goldoni comedies illustrated by Novelli for Zatta's edition (unnamed group)",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "The comedies represented in Novelli's second drawing set for a complete Goldoni edition; no individual play or drawing is identified here.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L76",
        },
        {
            "candidate_id": "cand-12161",
            "index_entry_id": "",
            "canonical_name": "Books Pinelli produced for the Venetian State (unnamed group)",
            "index_page_range": "",
            "suggested_type": "archive",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says Pinelli mostly produced books for an unspecified Venetian State authority; no titles are named. His judgment that they lacked artistic interest is kept as an attributed evaluation.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L77",
        },
    ]
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    if any(row["candidate_id"] in candidate_ids for row in new_candidates):
        raise SystemExit("preflight failed: one or more new candidate IDs already exist")
    candidates.extend(new_candidates)

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("preflight failed: duplicate mention_id")
    expected_mappings = {
        "m-s2-ch13-p339-009": "cand-2865",
        "m-s2-ch13-p339-019": "cand-2865",
        "m-s2-ch13-p339-022": "cand-2068",
        "m-s2-ch13-p339-023": "cand-2068",
        "m-s2-ch13-p339-039": "cand-10029",
        "m-s2-ch13-p339-046": "cand-1761",
        "m-s2-ch13-p339-053": "cand-2068",
        "m-s2-ch13-p339-054": "cand-2068",
    }
    for mention_id, expected_candidate in expected_mappings.items():
        if mention_id not in mention_by_id or mention_by_id[mention_id]["candidate_id"] != expected_candidate:
            raise SystemExit(f"preflight failed: unexpected candidate mapping for {mention_id}")
    repairs = {
        "m-s2-ch13-p339-009": "cand-12155",
        "m-s2-ch13-p339-019": "cand-12154",
        "m-s2-ch13-p339-022": "cand-0390",
        "m-s2-ch13-p339-023": "cand-12146",
        "m-s2-ch13-p339-039": "cand-12159",
        "m-s2-ch13-p339-046": "cand-12160",
        "m-s2-ch13-p339-053": "cand-12157",
        "m-s2-ch13-p339-054": "cand-12158",
    }
    for mention_id, candidate_id in repairs.items():
        mention_by_id[mention_id]["candidate_id"] = candidate_id
    mention_by_id["m-s2-ch13-p339-009"]["note"] = "Unnamed source-defined opponent group; no individuals are identified."
    mention_by_id["m-s2-ch13-p339-019"]["note"] = (
        "The body refers to Zatta's catalogues generally; note 4 identifies one specific 1790 catalogue."
    )
    mention_by_id["m-s2-ch13-p339-022"]["note"] = "Publication category, not a group of publishers."
    mention_by_id["m-s2-ch13-p339-023"]["note"] = "Ceremonial pamphlet category; linked to the corresponding p.337 term candidate."
    mention_by_id["m-s2-ch13-p339-039"]["note"] = "The textual works are distinct from Novelli's illustration group."
    mention_by_id["m-s2-ch13-p339-046"]["note"] = "Goldoni's plays are distinct from the illustration group that depicts them."
    mention_by_id["m-s2-ch13-p339-053"]["note"] = "Publication group attributed to unnamed publishers apart from the three named firms."
    mention_by_id["m-s2-ch13-p339-054"]["note"] = "A broad subject of artistic production, not the publisher group."

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    # Existing page-relative mention offsets include the [Page 339] marker at L70.
    segment_text = "\n".join(source_lines[69:77])

    def unique_span(surface: str) -> tuple[int, int]:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"preflight failed: source mention missing or ambiguous: {surface!r}")
        return start, start + len(surface)

    def add_mention(mention_id: str, candidate_id: str, surface: str, note: str) -> None:
        if mention_id in mention_by_id:
            raise SystemExit(f"preflight failed: {mention_id} already exists")
        start, end = unique_span(surface)
        row = {
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": segment_text[start:end],
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        }
        mentions.append(row)
        mention_by_id[mention_id] = row

    add_mention(
        "m-s2-ch13-p339-060",
        "cand-12156",
        "Many other publishers",
        "The unnamed group excludes the three publishers named in the same sentence.",
    )
    add_mention(
        "m-s2-ch13-p339-061",
        "cand-12161",
        "books for the State",
        "Unnamed publication group; keep distinct from the State/public authority candidate.",
    )

    def quote_between(first: str, after: str) -> str:
        start = segment_text.find(first)
        end = segment_text.find(after, start + len(first))
        if start < 0 or end < 0:
            raise SystemExit(f"preflight failed: quote boundary not found: {first!r} ... {after!r}")
        return segment_text[start:end].rstrip()

    additions = [
        make_statement(
            "st-chp13-p339-dante-iconography-difficult-for-zompini",
            "medieval_iconography_difficult_for_zompini",
            "cand-10034",
            "cand-2874",
            "Haskell says the medieval iconography in Zatta's Dante illustration was difficult for Gaetano Zompini.",
            by_id["st-chp13-p339-dante-medieval-iconography-difficult-for-artists"]["original_quote"],
            75,
            76,
            True,
            ["cand-10028", "cand-10034", "cand-2874", "cand-2865"],
            "The context is Zatta's illustrated Dante edition; the challenge is attributed to the iconography, not to the artists' general abilities.",
        ),
        make_statement(
            "st-chp13-p339-zatta-parodied-symbolic-interpretations",
            "parodied_enemies_symbolic_readings_of_decorative_ornament",
            "cand-2865",
            "cand-10025",
            "Haskell says Zatta parodied his enemies' heavy symbolic readings of decorative ornament through the fountain-and-dolphin vignette.",
            "and parodied their pedantic efforts to give heavy symbolical interpretations to merely decorative ornament:",
            72,
            72,
            True,
            ["cand-2865", "cand-12155", "cand-10025", "cand-10024"],
            "The vignette is the source example of the parody; the alleged interpretation is preserved as Haskell's account.",
        ),
        make_statement(
            "st-chp13-p339-vignette-basin-allegory-of-venetian-morals",
            "represented_accommodating_venetian_morals_in_satirical_reading",
            "cand-10025",
            "cand-10035",
            "In the satirical gloss quoted by Haskell, the vignette's basin represents the accommodating nature of Venetian morals.",
            quote_between("the basin of water", "A glance at his catalogues"),
            73,
            75,
            True,
            ["cand-10025", "cand-10024", "cand-10026", "cand-10035"],
            "This is the satirical secretary's interpretation as presented by Haskell, not a verified claim about Venetian society.",
            speaker="Satirical secretary quoted in Zatta's preface (as presented by Haskell)",
            text_layer="nested quotation and authorial paraphrase",
        ),
        make_statement(
            "st-chp13-p339-pinelli-library-among-europes-most-famous",
            "described_as_one_of_europes_most_famous_libraries",
            "cand-10030",
            None,
            "Haskell describes Pinelli's library as one of the most famous in Europe.",
            "one of the most famous in Europe",
            77,
            77,
            False,
            ["cand-10030"],
            "This is Haskell's superlative evaluation; the personal library remains without a forced taxonomy type.",
        ),
        make_statement(
            "st-chp13-p339-pinelli-state-books-no-artistic-interest",
            "judged_to_have_no_artistic_interest",
            "cand-12161",
            None,
            "Haskell judges the books Pinelli produced for the State to have no artistic interest.",
            "of no artistic interest",
            77,
            77,
            False,
            ["cand-12161", "cand-1932", "cand-10032"],
            "This is Haskell's evaluation of the book group, not an objective property or an evaluation of the State.",
        ),
        make_statement(
            "st-chp13-p339-other-publishers-limited-influence-on-artistic-output",
            "had_less_influence_on_artistic_output_than_major_publishers",
            "cand-12156",
            "cand-12158",
            "Haskell says the unnamed publishers failed to influence artistic output as strikingly as Albrizzi, Pasquali, and Zatta.",
            "but on the whole they failed to influence artistic output in the striking way achieved by their more important colleagues and they cannot therefore be discussed here.",
            77,
            77,
            True,
            ["cand-12156", "cand-12158", "cand-0025", "cand-1844", "cand-2865"],
            "The comparison is Haskell's stated reason for omitting these publishers; it does not imply that they produced no books.",
        ),
    ]

    required_new_ids = {row["statement_id"] for row in additions}
    if required_new_ids & set(by_id):
        raise SystemExit("preflight failed: one or more new statement IDs already exist")

    dante = by_id["st-chp13-p339-dante-medieval-iconography-difficult-for-artists"]
    dante["subject_candidate_id"] = "cand-10034"
    dante["object_candidate_id"] = "cand-1047"
    dante["predicate"] = "medieval_iconography_difficult_for_fontebasso"
    dante["qualifiers"]["claim"] = (
        "Haskell says the medieval iconography in Zatta's Dante illustration was difficult for Francesco Fontebasso."
    )
    dante["qualifiers"]["qualification"] = (
        "The context is Zatta's illustrated Dante edition; the challenge is attributed to the iconography, not to the artists' general abilities."
    )
    dante["qualifiers"]["mentioned_candidate_ids"] = ["cand-10028", "cand-10034", "cand-1047", "cand-2865"]

    social_world = by_id["st-chp13-p339-novelli-goldoni-lower-social-world"]
    social_world["object_candidate_id"] = "cand-1210"
    social_world["predicate"] = "depicted_comedies_in_lower_social_world_than_pasquali_edition"
    social_world["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-1758", "cand-1761", "cand-1210", "cand-1211", "cand-10036", "cand-1205", "cand-1844"
    ]
    social_world["qualifiers"]["qualification"] = (
        "Haskell compares Novelli's later Zatta edition illustrations with his earlier work for Pasquali; the lower social world remains Haskell's characterization."
    )

    other_publishers = by_id["st-chp13-p339-other-illustrated-book-publishers-limited-artistic-influence"]
    other_publishers["subject_candidate_id"] = "cand-12156"
    other_publishers["object_candidate_id"] = "cand-12157"
    other_publishers["predicate"] = "produced_fine_illustrated_books"
    other_publishers["qualifiers"]["claim"] = (
        "Haskell says many other publishers besides Albrizzi, Pasquali, and Zatta produced fine illustrated books."
    )
    other_publishers["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-12156", "cand-12157", "cand-0025", "cand-1844", "cand-2865"
    ]
    other_publishers["qualifiers"]["qualification"] = (
        "The additional publishers are not named; the claim is separated from Haskell's comparison of their artistic influence."
    )
    other_publishers["qualifiers"]["ocr_corrections"] = []
    other_publishers["original_quote"] = (
        "Many other publishers besides Albrizzi, Pasquali and Zatta produced fine illustrated books"
    )

    library = by_id["st-chp13-p339-pinelli-library-famous-in-europe"]
    library["predicate"] = "best_known_for_personal_library"
    library["qualifiers"]["claim"] = "Haskell says Pinelli was best known for his library."
    library["qualifiers"]["qualification"] = (
        "This is Haskell's statement about Pinelli's public association with the private library; the library's type remains unresolved."
    )
    library["qualifiers"]["mentioned_candidate_ids"] = ["cand-1932", "cand-10030"]
    library["qualifiers"]["ocr_corrections"] = []
    library["original_quote"] = "he is best known for his library"

    state_books = by_id["st-chp13-p339-pinelli-published-books-for-state"]
    state_books["qualifiers"]["claim"] = (
        "Haskell says Pinelli was mostly engaged in producing books for the unspecified State/public authority."
    )
    state_books["qualifiers"]["qualification"] = (
        "The authority's exact identity is not stated; the separate statement records Haskell's evaluation of the books."
    )
    state_books["qualifiers"]["mentioned_candidate_ids"] = ["cand-1932", "cand-10032", "cand-12161"]
    state_books["qualifiers"]["ocr_corrections"] = [
        {
            "source_line": 77,
            "ocr": "thepublisher",
            "print": "the publisher",
            "basis": "CHP-13.pdf physical page 8.",
        }
    ]
    state_books["original_quote"] = "was mostly engaged in turning out books for the State"

    picture_collection = by_id["st-chp13-p339-pinelli-owned-many-hundred-pictures"]
    picture_collection["qualifiers"]["ocr_corrections"] = [
        {
            "source_line": 77,
            "ocr": "pictures.8",
            "print": "pictures.6",
            "basis": "The printed superscript footnote marker is 6, not OCR 8.",
        }
    ]

    private_collector = by_id["st-chp13-p339-pinelli-private-collector-patron"]
    private_collector["qualifiers"]["ocr_corrections"] = []
    zatta_parody = by_id["st-chp13-p339-zatta-parodied-symbolic-readings"]
    zatta_parody["object_candidate_id"] = "cand-12155"
    zatta_parody["predicate"] = "mocked_unnamed_enemies_for_finding_jesuits_everywhere"
    zatta_parody["qualifiers"]["claim"] = "Haskell says Zatta mocked his unnamed enemies for finding Jesuits everywhere."
    zatta_parody["qualifiers"]["mentioned_candidate_ids"] = ["cand-2865", "cand-12155"]
    zatta_parody["qualifiers"]["qualification"] = (
        "The enemies are not identified; the adjoining statement records the parody of their symbolic readings."
    )
    zatta_parody["qualifiers"]["ocr_corrections"] = []
    zatta_parody["original_quote"] = "He once mocked his enemies for finding Jesuits everywhere"

    allegory = by_id["st-chp13-p339-satirical-secretary-reads-vignette-as-jesuit-attack"]
    first_start = segment_text.find("the vignette on one of his books")
    first_end = segment_text.find("and the basin of water", first_start)
    if first_start < 0 or first_end < 0:
        raise SystemExit("preflight failed: allegory quote boundaries not found")
    jesuit_quote = segment_text[first_start:first_end].rstrip()
    if "represents the Jesuits" not in jesuit_quote:
        raise SystemExit("preflight failed: Jesuit allegory quote was not fully captured")
    allegory["predicate"] = "represented_jesuits_through_dolphin_in_satirical_reading"
    allegory["qualifiers"]["claim"] = (
        "In the satirical account quoted by Haskell, a fountain-and-dolphin vignette is presented as an attack on the Jesuits, with the dolphin said to represent them."
    )
    allegory["qualifiers"]["qualification"] = (
        "The secretary is a fictional voice in Zatta's preface; this is the parody's allegorical reading, not independently verified authorial intent."
    )
    allegory["qualifiers"]["mentioned_candidate_ids"] = ["cand-10025", "cand-10024", "cand-10026", "cand-1321"]
    allegory["original_quote"] = jesuit_quote

    prolific = by_id["st-chp13-p339-zatta-most-prolific-in-eighteenth-century-venice"]
    prolific["qualifiers"]["mentioned_candidate_ids"] = ["cand-2865", "cand-12154", "cand-10184", "cand-2719"]
    prolific["qualifiers"]["qualification"] = (
        "Haskell bases this superlative on Zatta's catalogues. Note 4 cites one 1790 catalogue (cand-10184); neither it nor the general catalogue group has been independently consulted."
    )

    source_quotes = [row["original_quote"] for row in additions]
    source_quotes += [
        dante["original_quote"],
        social_world["original_quote"],
        other_publishers["original_quote"],
        library["original_quote"],
        state_books["original_quote"],
        zatta_parody["original_quote"],
        jesuit_quote,
    ]
    if any(quote not in segment_text for quote in source_quotes):
        absent = [quote for quote in source_quotes if quote not in segment_text]
        raise SystemExit(f"preflight failed: one or more final quotations do not match S0: {absent!r}")

    morals = next(row for row in additions if row["statement_id"] == "st-chp13-p339-vignette-basin-allegory-of-venetian-morals")
    original_allegory_qualifiers = by_id["st-chp13-p339-satirical-secretary-reads-vignette-as-jesuit-attack"]["qualifiers"]
    for key in (
        "footnote_marker",
        "footnote_printed_page",
        "footnote_text_pending",
        "footnote_segment",
        "footnote_body_link_status",
        "cross_reference_segments",
        "footnote_note_statement_ids",
        "footnote_refs",
    ):
        if key in original_allegory_qualifiers:
            morals["qualifiers"][key] = deepcopy(original_allegory_qualifiers[key])
    morals["qualifiers"]["ocr_corrections"] = []

    add_ids = {row["statement_id"] for row in additions}
    if add_ids & set(by_id):
        raise SystemExit("preflight failed: one or more split statement IDs already exist")
    statements.extend(additions)
    print(f"segment={SEGMENT_ID}; SHA-256={SEGMENT_SHA256}; original statements={len(local)}; classified={len(decisions)}")
    print("splits: two named artists; Zatta's mockery and its vignette example; two allegorical readings; Pinelli library association/ranking; State books/publication quality; other publishers' books/influence")
    print("endpoint repairs: illustration group vs person; publishers vs publication groups; source books vs illustrations; State vs book group")
    print("new candidates: cand-12154 through cand-12161; new mentions: 2")
    for statement_id, value in decisions.items():
        print(f"  {statement_id}: {value}")
    if not args.apply:
        print("DRY RUN only; no files written. Pass --apply to write after review.")
        return

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    statement_bytes = (
        "\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n"
    ).encode("utf-8")
    write_atomic(STATEMENTS, statement_bytes)
    write_atomic(CANDIDATES, csv_bytes(candidate_fields, candidates))
    write_atomic(MENTIONS, csv_bytes(mention_fields, mentions))
    print("APPLIED. Backups saved for statements, candidates, and mentions.")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"  {path.name}: {digest(path)}")


if __name__ == "__main__":
    main()
