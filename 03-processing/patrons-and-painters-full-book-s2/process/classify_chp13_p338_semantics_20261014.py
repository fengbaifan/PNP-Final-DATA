#!/usr/bin/env python3
"""Review p.338 S2 claims, endpoints, and source mentions; dry-run by default."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l61-68"
SEGMENT_SHA256 = "620218f342bfa723e9e5b399102e36d0579adbbe358d6df0df7048a2f1669f83"
PRE_HASHES = {
    STATEMENTS.name: "6b259e12f99a040894ffe09d4efc55c4a9797823e4644176e79d20b7e833bd52",
    CANDIDATES.name: "cb638a7297ef674590e9f1ec18ccc4dcc00c2a3e44d5870de109480d5b68f79c",
    MENTIONS.name: "e8ea0913ee0bd11e1414fbd0f67a482ab75450eda054ad9e672440575ea3aa45",
}
BACKUP_SUFFIX = ".bak-s2-ch13-p338-semantic-review-20261014"


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
    line: int,
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
            "source_line_start": line,
            "source_line_end": line,
            "printed_page": 338,
            "pdf_physical_page": 7,
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
        raise SystemExit("preflight failed: p.338 segment identity/hash changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: duplicate statement_id")
    local = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(local) != 23:
        raise SystemExit(f"preflight failed: expected 23 p.338 statements, found {len(local)}")
    unset = {
        row["statement_id"]
        for row in local
        if row.get("qualifiers", {}).get("relation_candidate") is None
    }
    decisions = {
        "st-chp13-p338-authorities-opposed-jesuits-and-suppressed-disputes": True,
        "st-chp13-p338-goldoni-biographical-episodes-in-illustrations": True,
        "st-chp13-p338-goldoni-criticised-conventional-frontispieces": True,
        "st-chp13-p338-goldoni-explained-illustration-novelty": True,
        "st-chp13-p338-goldoni-general-symbols-no-longer-attracted-public": True,
        "st-chp13-p338-haskell-called-pasquali-most-enlightened-venetian-publisher": False,
        "st-chp13-p338-haskell-longhi-comparison-and-vivid-period-impression": True,
        "st-chp13-p338-haskell-praised-drawings-quality": False,
        "st-chp13-p338-illustrated-intimacy-affected-play-plates": True,
        "st-chp13-p338-no-subscribers-wide-public": True,
        "st-chp13-p338-novelli-scenes-depict-venetian-professional-world": True,
        "st-chp13-p338-pasquali-books-shared-audience-and-lacked-pomp": True,
        "st-chp13-p338-pasquali-ideals-enlightened-bourgeoisie": True,
        "st-chp13-p338-zatta-third-greater-venetian-publisher": True,
    }
    if unset != set(decisions):
        raise SystemExit(f"preflight failed: unexpected unset IDs: {sorted(unset ^ set(decisions))}")
    for statement_id, value in decisions.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = value

    new_candidates = [
        {
            "candidate_id": "cand-12148",
            "index_entry_id": "",
            "canonical_name": "Wide public addressed by Pasquali's Goldoni edition",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell says the edition was aimed at a wide general public and links the same sort of public to that represented in Novelli's drawings; membership and actual reception are unspecified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L62",
        },
        {
            "candidate_id": "cand-12149",
            "index_entry_id": "",
            "canonical_name": "Most of Pasquali's books discussed in Haskell's p.338 account (unnamed group)",
            "index_page_range": "",
            "suggested_type": "archive",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Source-defined group qualified as 'most' of Pasquali's books; no complete title list is given. Keep distinct from the p.336 fine and luxurious books group cand-12142.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L65",
        },
        {
            "candidate_id": "cand-12150",
            "index_entry_id": "",
            "canonical_name": "Novelli's illustrations for Goldoni's plays (unnamed group)",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "The plates Novelli designed to illustrate Goldoni's plays, which Haskell says were affected by the intimacy and public confidence of the autobiographical drawings; individual plates are not named.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L65",
        },
        {
            "candidate_id": "cand-12151",
            "index_entry_id": "",
            "canonical_name": "Conventional motifs in the frontispiece repertory discussed by Goldoni",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Source-defined frontispiece repertory including Muses, Apollos, Masks, Satyrs, and Apes; the motifs are not individual historical people or works.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L64",
        },
        {
            "candidate_id": "cand-12152",
            "index_entry_id": "",
            "canonical_name": "Religious disputes the Venetian authorities sought to damp down",
            "index_page_range": "",
            "suggested_type": "term",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Generic class of disputes mentioned by Haskell; no individual dispute or complete membership is identified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L68",
        },
        {
            "candidate_id": "cand-12153",
            "index_entry_id": "",
            "canonical_name": "Unspecified pictures by Pietro Longhi cited as a comparator",
            "index_page_range": "",
            "suggested_type": "work",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": "Haskell contrasts these unspecified pictures with the period impression conveyed by Novelli's illustration program; no picture title or collection is identified.",
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + "#L65",
        },
    ]
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    if any(row["candidate_id"] in candidate_ids for row in new_candidates):
        raise SystemExit("preflight failed: one or more new candidate IDs already exist")
    required_existing = {
        "cand-1758": "person",
        "cand-10018": "term",
        "cand-10019": "term",
        "cand-10017": "institution",
    }
    by_candidate = {row["candidate_id"]: row for row in candidates}
    for candidate_id, expected_type in required_existing.items():
        if candidate_id not in by_candidate or by_candidate[candidate_id]["suggested_type"] != expected_type:
            raise SystemExit(f"preflight failed: expected candidate {candidate_id} of type {expected_type}")
    candidates.extend(new_candidates)

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("preflight failed: duplicate mention_id")
    expected_mappings = {
        "m-s2-ch13-p338-003": "cand-1760",
        "m-s2-ch13-p338-006": "cand-0390",
        "m-s2-ch13-p338-007": "cand-0390",
        "m-s2-ch13-p338-018": "cand-1760",
        "m-s2-ch13-p338-024": "cand-1844",
    }
    for mention_id, expected_candidate in expected_mappings.items():
        if mention_id not in mention_by_id or mention_by_id[mention_id]["candidate_id"] != expected_candidate:
            raise SystemExit(f"preflight failed: unexpected candidate mapping for {mention_id}")
    mention_by_id["m-s2-ch13-p338-003"]["candidate_id"] = "cand-1758"
    mention_by_id["m-s2-ch13-p338-003"]["note"] = "This occurrence names the person Novelli; the illustration group has its own candidate."
    mention_by_id["m-s2-ch13-p338-006"]["candidate_id"] = "cand-12151"
    mention_by_id["m-s2-ch13-p338-006"]["note"] = "Frontispiece repertory discussed by Goldoni."
    mention_by_id["m-s2-ch13-p338-007"]["candidate_id"] = "cand-12151"
    mention_by_id["m-s2-ch13-p338-007"]["note"] = "Examples of motifs in the frontispiece repertory, not individual actor/work candidates."
    mention_by_id["m-s2-ch13-p338-018"]["candidate_id"] = "cand-1758"
    mention_by_id["m-s2-ch13-p338-018"]["note"] = "This occurrence names Novelli as the designer, not the illustration work."
    mention_by_id["m-s2-ch13-p338-024"]["candidate_id"] = "cand-12149"
    mention_by_id["m-s2-ch13-p338-024"]["note"] = "The passage refers to most of Pasquali's books as an unnamed publication group."

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    # Include the printed-page marker at L61, matching existing segment-relative mention offsets.
    segment_text = "\n".join(source_lines[60:68])

    def one_span(surface: str, after: str = "") -> tuple[int, int]:
        start_at = segment_text.find(after) + len(after) if after else 0
        start = segment_text.find(surface, start_at)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"preflight failed: mention surface is missing or ambiguous: {surface!r}")
        return start, start + len(surface)

    def add_mention(mention_id: str, candidate_id: str, surface: str, note: str, after: str = "") -> None:
        if mention_id in mention_by_id:
            raise SystemExit(f"preflight failed: {mention_id} already exists")
        start, end = one_span(surface, after)
        mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": segment_text[start:end],
                "start_char": str(start),
                "end_char": str(end),
                "note": note,
            }
        )
        mention_by_id[mention_id] = mentions[-1]

    add_mention(
        "m-s2-ch13-p338-049",
        "cand-12148",
        "wide general public",
        "Haskell's stated intended readership; no named readers or reception are documented.",
    )
    public_occurrences = []
    at = 0
    while (at := segment_text.find("the public", at)) >= 0:
        public_occurrences.append(at)
        at += len("the public")
    if len(public_occurrences) != 2:
        raise SystemExit(f"preflight failed: expected two p.338 'the public' mentions, found {len(public_occurrences)}")
    for suffix, start in zip(("050", "051"), public_occurrences):
        mention_id = f"m-s2-ch13-p338-{suffix}"
        mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": "cand-12148",
                "surface_form": segment_text[start : start + len("the public")],
                "start_char": str(start),
                "end_char": str(start + len("the public")),
                "note": "Unspecified public referred to in the Goldoni-edition discussion.",
            }
        )
        mention_by_id[mention_id] = mentions[-1]
    add_mention(
        "m-s2-ch13-p338-052",
        "cand-12148",
        "the very same sort of public",
        "Audience category linked by Haskell to the public represented in Novelli's drawings.",
    )
    add_mention(
        "m-s2-ch13-p338-053",
        "cand-12150",
        "the plates that Novelli designed to illustrate the plays themselves",
        "Source-defined group of Goldoni-play illustrations; no individual plate is named.",
    )
    add_mention(
        "m-s2-ch13-p338-054",
        "cand-12153",
        "the pictures of Pietro Longhi",
        "The person is also mentioned separately; this phrase refers to an unspecified picture group.",
    )
    add_mention(
        "m-s2-ch13-p338-055",
        "cand-12152",
        "any religious disputes",
        "Generic class of disputes; no individual event is named.",
    )

    authorities = by_id["st-chp13-p338-authorities-opposed-jesuits-and-suppressed-disputes"]
    authorities["subject_candidate_id"] = "cand-10017"
    authorities["predicate"] = "often_antagonistic_to_society_of_jesus"
    authorities["qualifiers"]["claim"] = (
        "Haskell says the unidentified Venetian authorities were often antagonistic to the Society of Jesus."
    )
    authorities["qualifiers"]["qualification"] = (
        "This statement covers opposition to the Society; Haskell does not identify every authority or equate this group with the Inquisitori di Stato."
    )
    authorities["qualifiers"]["mentioned_candidate_ids"] = ["cand-10017", "cand-1321"]
    authorities["original_quote"] = "the authorities, who were often antagonistic to the Society"

    add_statement_ids = {
        "st-chp13-p338-authorities-sought-to-suppress-religious-disputes",
        "st-chp13-p338-goldoni-edition-no-list-of-subscribers",
        "st-chp13-p338-pasquali-books-aimed-at-public-of-novelli-drawings",
        "st-chp13-p338-zatta-controversial-political-figure",
        "st-chp13-p338-novelli-beginning-to-acquire-reputation",
    }
    if add_statement_ids & set(by_id):
        raise SystemExit("preflight failed: one or more split statement IDs already exist")
    additions = [
        make_statement(
            "st-chp13-p338-authorities-sought-to-suppress-religious-disputes",
            "sought_to_damp_down_religious_disputes",
            "cand-10017",
            "cand-12152",
            "Haskell says the unidentified Venetian authorities were at all times anxious to damp down religious disputes.",
            "who were at all times anxious to damp down any religious disputes.",
            68,
            True,
            ["cand-10017", "cand-12152"],
            "This records a stated disposition toward a generic class of disputes; no individual event is identified.",
        ),
        make_statement(
            "st-chp13-p338-goldoni-edition-no-list-of-subscribers",
            "had_no_list_of_subscribers",
            "cand-1851",
            None,
            "Haskell says the edition had no list of subscribers.",
            "There was no list of subscribers",
            62,
            False,
            ["cand-1851"],
            "This is a publication/distribution feature; it does not imply there were no purchasers.",
        ),
        make_statement(
            "st-chp13-p338-pasquali-books-aimed-at-public-of-novelli-drawings",
            "aimed_at_public_comparable_to_public_depicted_in_novelli_drawings",
            "cand-12149",
            "cand-12148",
            "Haskell says most of Pasquali's books were aimed at the same sort of public represented in Novelli's drawings.",
            "which were aimed at the very same sort of public as that illustrated in Novelli\u2019s drawings",
            65,
            True,
            ["cand-12149", "cand-12148", "cand-10013", "cand-10018"],
            "The comparison concerns the kind of public; it does not identify actual readers or assert that depicted people bought the books.",
        ),
        make_statement(
            "st-chp13-p338-zatta-controversial-political-figure",
            "described_as_controversial_figure_in_politics",
            "cand-2865",
            None,
            "Haskell describes Antonio Zatta as a controversial figure in the political field.",
            "was also a controversial figure in the political field.",
            67,
            False,
            ["cand-2865"],
            "This is Haskell's characterization, separated from the preceding identification of Zatta among the greater Venetian publishers.",
        ),
        make_statement(
            "st-chp13-p338-novelli-beginning-to-acquire-reputation",
            "beginning_to_acquire_a_reputation",
            "cand-1758",
            None,
            "Haskell says Novelli was just beginning to acquire a reputation at the time described.",
            "who was just beginning to acquire a reputation.",
            63,
            False,
            ["cand-1758"],
            "This is a biographical characterization, not a formal relation to the Goldoni edition.",
        ),
    ]
    additions_by_id = {row["statement_id"]: row for row in additions}
    if set(additions_by_id) != add_statement_ids:
        raise SystemExit("preflight failed: split statement ID set mismatch")

    goldoni_frontispieces = by_id["st-chp13-p338-goldoni-criticised-conventional-frontispieces"]
    goldoni_frontispieces["object_candidate_id"] = "cand-12151"
    goldoni_frontispieces["qualifiers"]["mentioned_candidate_ids"] = ["cand-1205", "cand-12151"]

    public_symbols = by_id["st-chp13-p338-goldoni-general-symbols-no-longer-attracted-public"]
    public_symbols["subject_candidate_id"] = "cand-12151"
    public_symbols["object_candidate_id"] = "cand-12148"
    public_symbols["qualifiers"]["mentioned_candidate_ids"] = ["cand-1205", "cand-12151", "cand-12148"]

    longhi = by_id["st-chp13-p338-haskell-longhi-comparison-and-vivid-period-impression"]
    longhi["object_candidate_id"] = "cand-12153"
    longhi["qualifiers"]["mentioned_candidate_ids"] = ["cand-10013", "cand-12153", "cand-1429", "cand-1205"]

    intimacy = by_id["st-chp13-p338-illustrated-intimacy-affected-play-plates"]
    intimacy["object_candidate_id"] = "cand-12150"
    intimacy["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-10013", "cand-12148", "cand-1758", "cand-12150", "cand-1205", "cand-1851"
    ]
    intimacy["qualifiers"]["qualification"] = (
        "Haskell describes an effect from the autobiographical illustration group and the idea of addressing the public "
        "to a distinct group of Novelli's play illustrations within the Goldoni edition."
    )

    broad_public = by_id["st-chp13-p338-no-subscribers-wide-public"]
    broad_public["object_candidate_id"] = "cand-12148"
    broad_public["qualifiers"]["claim"] = "Haskell says the Goldoni edition's volumes were aimed at a wide general public."
    broad_public["qualifiers"]["qualification"] = (
        "This records intended readership only; the separate statement records the absence of a subscriber list."
    )
    broad_public["qualifiers"]["mentioned_candidate_ids"] = ["cand-1851", "cand-12148"]
    broad_public["original_quote"] = "the volumes were aimed at a wide general public."

    scene = by_id["st-chp13-p338-novelli-scenes-depict-venetian-professional-world"]
    scene["object_candidate_id"] = "cand-10018"
    scene["qualifiers"]["relation_candidate"] = True
    scene["qualifiers"]["mentioned_candidate_ids"] = ["cand-10013", "cand-10018", "cand-2719"]
    scene["qualifiers"]["qualification"] = (
        "The represented class is a source-defined social category; Haskell's characterization is not a census or demographic measure."
    )

    pasquali_books = by_id["st-chp13-p338-pasquali-books-shared-audience-and-lacked-pomp"]
    pasquali_books["subject_candidate_id"] = "cand-12149"
    pasquali_books["object_candidate_id"] = "cand-10023"
    pasquali_books["predicate"] = "lacked_pomp_characterizing_albrizzi_publications"
    pasquali_books["qualifiers"]["claim"] = (
        "Haskell says most of Pasquali's books lacked the pomp that characterized Albrizzi's publications."
    )
    pasquali_books["qualifiers"]["mentioned_candidate_ids"] = ["cand-12149", "cand-10023", "cand-0025"]
    pasquali_books["qualifiers"]["qualification"] = (
        "This preserves Haskell's explicit comparison of the publication groups; the qualifier 'most' is retained."
    )
    pasquali_books["original_quote"] = (
        "there is a complete lack of the pomp that characterises Albrizzi\u2019s pubheations."
    )

    ideals = by_id["st-chp13-p338-pasquali-ideals-enlightened-bourgeoisie"]
    ideals["object_candidate_id"] = "cand-10019"
    ideals["qualifiers"]["relation_candidate"] = True
    ideals["qualifiers"]["mentioned_candidate_ids"] = ["cand-1844", "cand-10019"]
    ideals["qualifiers"]["qualification"] = (
        "Haskell's broad ideological association is retained as his interpretation, not a claim that all European hopes were uniform."
    )

    zatta = by_id["st-chp13-p338-zatta-third-greater-venetian-publisher"]
    zatta["qualifiers"]["claim"] = "Haskell identifies Antonio Zatta as the third of the greater Venetian publishers."
    zatta["qualifiers"]["qualification"] = (
        "The ordinal follows Haskell's presentation of Albrizzi and Pasquali; it is not a complete census of publishers. "
        "His political characterization is recorded separately."
    )
    zatta["original_quote"] = "The third of the greater Venetian publishers, Antonio Zatta"

    novelli = by_id["st-chp13-p338-novelli-employed-for-goldoni-illustrations"]
    if novelli.get("object_candidate_id") != "cand-1760":
        raise SystemExit("preflight failed: Novelli employment endpoint changed")
    novelli["object_candidate_id"] = "cand-1758"
    novelli["qualifiers"]["claim"] = "Pasquali employed Pietro Antonio Novelli for the Goldoni-edition illustrations."
    novelli["qualifiers"]["qualification"] = (
        "The statement records the employment relation; Novelli's emerging reputation is a separate descriptive statement."
    )
    novelli["qualifiers"]["mentioned_candidate_ids"] = ["cand-1844", "cand-1758", "cand-10013", "cand-1851"]
    novelli["original_quote"] = "For the illustrations Pasquali employed the young Pietro Antonio Novelli"

    statements.extend(additions)
    print(f"segment={SEGMENT_ID}; SHA-256={SEGMENT_SHA256}; original statements={len(local)}; unset classified={len(decisions)}")
    print("split claims: no subscriber list; Zatta political characterization; Pasquali-books audience; authorities' dispute policy; Novelli reputation")
    print("endpoint repairs: authorities -> cand-10017; Novelli person -> cand-1758; depicted class -> cand-10018; ideals -> cand-10019")
    print("new source-bounded candidates: cand-12148 through cand-12153")
    print("mention repairs: Novelli person, frontispiece motifs, and Pasquali book group")
    print(f"new statements={len(additions)}; new mentions=7")
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
