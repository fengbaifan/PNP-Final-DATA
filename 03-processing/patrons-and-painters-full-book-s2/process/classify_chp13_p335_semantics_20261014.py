#!/usr/bin/env python3
"""Review and atomize the p.335 S2 statements; dry-run unless --apply is passed."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l32-39"
SEGMENT_SHA256 = "87b76d69cdd5618e7276f859c5ad8cf89a9ffb947d6e78c6032782e93414fe14"
PRE_HASHES = {
    STATEMENTS.name: "9f16d5de94f4d32aa16bce0fc3b1dd9296808d8b9c47f11dbdef4d65c60c3604",
    CANDIDATES.name: "f9cd9e476ff2386e7a28dfcd4cc40424ac29d42badca14e6b1c1ab226ca48597",
    MENTIONS.name: "911985cf65b82b47834b7f7d7a3001f59bb006018a7138927c826f915fbd541d",
}
BACKUP_SUFFIX = ".bak-s2-chp13-p335-semantic-review-20261014"
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"


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


def new_statement(statement_id: str, *, subject: str | None, obj: str | None,
                  predicate: str, claim: str, quote: str, line_start: int,
                  line_end: int, rc: bool, mentions: list[str],
                  qualification: str, extra: dict | None = None) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 335,
        "pdf_physical_page": 4,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narrative",
        "qualification": qualification,
        "mentioned_candidate_ids": mentions,
        "ocr_corrections": [],
        "relation_candidate": rc,
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after all preflight checks")
    args = parser.parse_args()

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = digest(path)
        expected = PRE_HASHES[path.name]
        if actual != expected:
            raise SystemExit(f"preflight failed: {path.name} SHA-256 {actual} != {expected}")
    segment_rows = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.335 segment identity/hash changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("preflight failed: duplicate statement_id")
    p335 = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {row["statement_id"] for row in p335 if row.get("qualifiers", {}).get("relation_candidate") is None}
    expected_unset = {
        "st-chp13-p335-artist-buried-in-albrizzi-family-vault",
        "st-chp13-p335-bossuet-edition-set-pattern-and-aesthetic",
        "st-chp13-p335-gerusalemme-inspired-next-project-open",
        "st-chp13-p335-gerusalemme-success-in-france",
        "st-chp13-p335-illustrations-for-central-european-readers",
        "st-chp13-p335-maria-teresa-luxury-associated-with-schonbrunn",
        "st-chp13-p335-piazzetta-bossuet-illustration-repertoire",
        "st-chp13-p335-piazzetta-dramatic-and-pastoral-compositions",
        "st-chp13-p335-piazzetta-illustration-style-contrast",
        "st-chp13-p335-piazzetta-style-and-career-sequence",
        "st-chp13-p335-note2-recurti-citation",
        "st-chp13-p335-note4-richard-citation",
    }
    if unset != expected_unset:
        raise SystemExit(f"preflight failed: unexpected unset IDs: {sorted(unset ^ expected_unset)}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidate_reader = csv.DictReader(stream)
        candidate_fields = candidate_reader.fieldnames
        candidates = list(candidate_reader)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(candidate_by_id) != len(candidates):
        raise SystemExit("preflight failed: duplicate candidate_id")
    if candidate_by_id.get("cand-1913", {}).get("suggested_type") != "work":
        raise SystemExit("preflight failed: cand-1913 no longer has the expected index type")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        mention_reader = csv.DictReader(stream)
        mention_fields = mention_reader.fieldnames
        mentions = list(mention_reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("preflight failed: duplicate mention_id")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[31:39])
    def span(surface: str) -> tuple[str, str]:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"preflight failed: mention surface is not unique in segment: {surface!r}")
        return str(start), str(start + len(surface))

    # Classify every pre-existing unset statement in this source segment.
    decisions = {
        "st-chp13-p335-artist-buried-in-albrizzi-family-vault": True,
        "st-chp13-p335-bossuet-edition-set-pattern-and-aesthetic": True,
        "st-chp13-p335-gerusalemme-inspired-next-project-open": True,
        "st-chp13-p335-gerusalemme-success-in-france": True,
        "st-chp13-p335-illustrations-for-central-european-readers": True,
        "st-chp13-p335-maria-teresa-luxury-associated-with-schonbrunn": False,
        "st-chp13-p335-piazzetta-bossuet-illustration-repertoire": False,
        "st-chp13-p335-piazzetta-dramatic-and-pastoral-compositions": False,
        "st-chp13-p335-piazzetta-illustration-style-contrast": False,
        "st-chp13-p335-piazzetta-style-and-career-sequence": False,
        "st-chp13-p335-note2-recurti-citation": False,
        "st-chp13-p335-note4-richard-citation": False,
    }
    for statement_id, value in decisions.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = value

    # Separate the book's precedent claim from Haskell's aesthetic evaluation.
    pattern = by_id["st-chp13-p335-bossuet-edition-set-pattern-and-aesthetic"]
    pattern["object_candidate_id"] = "cand-0025"
    pattern["predicate"] = "set_precedent_for_albrizzi_publication_ventures"
    pattern["original_quote"] = "The book set a pattern for their future ventures"
    pattern["qualifiers"].update({
        "claim": "Haskell says the Bossuet edition set a pattern for Albrizzi and Piazzetta's later publishing ventures.",
        "qualification": "The source names no particular later edition; 'their' refers to the two men's publishing and illustration ventures.",
        "mentioned_candidate_ids": ["cand-9987", "cand-0025", "cand-1907"],
        "cross_reference_segments": ["chp-13:13_CHP-13_intro:l41-50"],
        "relation_candidate": True,
    })
    aesthetic_quote = "in general Albrizzi’s editions are characterised by an opulent, aristocratic elegance, often tinged with melancholy, and weighty even at its most frivolous, that sets them apart from other publications."
    aesthetic = new_statement(
        "st-chp13-p335-albrizzi-editions-aesthetic-characterization",
        subject="cand-0025", obj=None, predicate="haskell_aesthetic_characterization_of_albrizzi_editions",
        claim="Haskell characterizes Albrizzi's editions in general as opulent and aristocratic, often melancholy, and weighty even when frivolous.",
        quote=aesthetic_quote, line_start=34, line_end=34, rc=False,
        mentions=["cand-0025"],
        qualification="This is Haskell's general aesthetic evaluation, not a measured attribute of every edition.",
    )

    # Add explicit claims omitted from the prior p.335 migration.
    opportunity_quote = "This book gave him a wonderful opportunity to achieve his aim."
    opportunity = new_statement(
        "st-chp13-p335-bossuet-book-opportunity-for-albrizzi-aim",
        subject="cand-9987", obj="cand-0025", predicate="provided_opportunity_to_advance_venetian_print_reputation",
        claim="Haskell says the Bossuet book gave Albrizzi an opportunity to advance his previously stated aim of restoring the reputation of Venetian prints.",
        quote=opportunity_quote, line_start=33, line_end=33, rc=True,
        mentions=["cand-9987", "cand-0025", "cand-2719"],
        qualification="'This book' refers to the Bossuet edition; 'his aim' refers back to Albrizzi's plan on p.334. The passage states an opportunity, not proof that the aim was achieved.",
        extra={"cross_reference_statement_ids": ["st-chp13-p334-albrizzi-plan-revive-venetian-prints-open"]},
    )
    discovery_quote = "Albrizzi had not discovered Piazzetta as an illustrator"
    discovery = new_statement(
        "st-chp13-p335-albrizzi-not-first-to-discover-piazzetta",
        subject="cand-0025", obj="cand-1907", predicate="did_not_first_discover_piazzetta_as_illustrator",
        claim="Haskell says Albrizzi was not the person who first discovered Piazzetta as an illustrator; Piazzetta had already made a frontispiece for a Recurti devotional book twelve years before their first joint venture.",
        quote=discovery_quote, line_start=33, line_end=33, rc=False,
        mentions=["cand-0025", "cand-1907", "cand-9993", "cand-2111"],
        qualification="The claim negates a discovery attribution; the prior frontispiece is separately recorded as a positive work and publisher relation.",
        extra={"cross_reference_statement_ids": ["st-chp13-p335-piazzetta-frontispiece-before-albrizzi-enterprise"]},
    )

    # Add source-bounded audience terms and precise mentions for the two distinct groups.
    new_candidate_rows = [
        {
            "candidate_id": "cand-12139", "index_entry_id": "", "canonical_name": "Central European archbishops as intended readers of Albrizzi's Bossuet edition",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-bounded readership group named as beneficiaries of Piazzetta's illustrations for the Bossuet volumes; no individual archbishop is identified.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L33",
        },
        {
            "candidate_id": "cand-12140", "index_entry_id": "", "canonical_name": "Wealthy Central European monasteries as intended readers of Albrizzi's Bossuet edition",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-bounded institutional readership group named as beneficiaries of Piazzetta's illustrations for the Bossuet volumes; no particular monastery is identified.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L33",
        },
        {
            "candidate_id": "cand-12141", "index_entry_id": "", "canonical_name": "International public intended for Albrizzi's 1745 Gerusalemme Liberata edition",
            "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": "Source-bounded intended readership for the 1745 illustrated edition; the source gives no audience membership or national composition beyond calling it international.",
            "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L36",
        },
    ]
    for row in new_candidate_rows:
        if row["candidate_id"] in candidate_by_id:
            raise SystemExit(f"preflight failed: candidate ID already exists: {row['candidate_id']}")

    added_mentions = []
    for mention_id, candidate_id, surface, note in [
        ("m-s2-ch13-p335-038", "cand-12139", "archbishops", "Source-bounded intended readership group; no individual is named."),
        ("m-s2-ch13-p335-039", "cand-12140", "rich monasteries of Central\nEurope", "Source-bounded intended readership group; no particular monastery is named."),
        ("m-s2-ch13-p335-040", "cand-12141", "international public", "Intended readership of the 1745 Gerusalemme Liberata edition; membership is unspecified."),
    ]:
        if mention_id in mention_by_id:
            raise SystemExit(f"preflight failed: mention ID already exists: {mention_id}")
        start, end = span(surface)
        added_mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": start, "end_char": end, "note": note,
        })

    # The two readership classes in the source are distinct endpoints.
    audience = by_id["st-chp13-p335-illustrations-for-central-european-readers"]
    audience["object_candidate_id"] = "cand-12139"
    audience["predicate"] = "illustrations_intended_for_central_european_archbishops"
    audience["qualifiers"].update({
        "claim": "Haskell says Piazzetta's illustrations helped make Bossuet's extensive volumes digestible for Central European archbishops.",
        "qualification": "Source-bounded audience class only; no individual archbishop is identified.",
        "mentioned_candidate_ids": ["cand-9987", "cand-0415", "cand-12139"],
        "relation_candidate": True,
    })
    monasteries_quote = "helped to make digestible the thundering tomes of Bossuet for the archbishops and rich monasteries of Central\nEurope."
    monasteries = new_statement(
        "st-chp13-p335-bossuet-audience-central-europe-monasteries",
        subject="cand-9987", obj="cand-12140", predicate="illustrations_intended_for_wealthy_central_european_monasteries",
        claim="Haskell says Piazzetta's illustrations helped make Bossuet's extensive volumes digestible for wealthy monasteries in Central Europe.",
        quote=monasteries_quote, line_start=33, line_end=34, rc=True,
        mentions=["cand-9987", "cand-0415", "cand-12140"],
        qualification="Source-bounded audience class only; no particular monastery is identified.",
    )

    international_quote = "Like most of his enterprises this too was designed for an international public."
    international = new_statement(
        "st-chp13-p335-gerusalemme-intended-for-international-public",
        subject="cand-9990", obj="cand-12141", predicate="designed_for_international_public",
        claim="Haskell says the 1745 Gerusalemme Liberata edition was designed for an international public.",
        quote=international_quote, line_start=36, line_end=36, rc=True,
        mentions=["cand-9990", "cand-0025", "cand-12141"],
        qualification="This is a statement about intended readership, not evidence that the edition reached or was read by that public.",
    )

    # Separate a narrative criticism from Haskell's explicit comparison with Boucher.
    drawings = by_id["st-chp13-p335-piazzetta-dramatic-and-pastoral-compositions"]
    drawings["subject_candidate_id"] = "cand-9991"
    drawings["object_candidate_id"] = None
    drawings["predicate"] = "dramatic_drawings_reveal_difficulty_in_heroic_narrative"
    drawings["original_quote"] = "the dramatic ones show that inability to tell an heroic story which is apparent in many of his paintings"
    drawings["qualifiers"].update({
        "claim": "Haskell says the dramatic drawings reveal Piazzetta's difficulty in telling heroic stories, a weakness he also sees in many of the artist's paintings.",
        "qualification": "This is an authorial evaluation of the drawings and paintings, not a formal relation between two identified works.",
        "mentioned_candidate_ids": ["cand-9991", "cand-1907"],
        "relation_candidate": False,
    })
    pastoral_quote = "but the pastoral compositions with their elegantly posed shepherds and other country-folk about their ordinary pursuits have some of the quality of Boucher, though Piazzetta’s world is much less artificial."
    pastoral = new_statement(
        "st-chp13-p335-piazzetta-pastoral-compositions-boucher-comparison",
        subject="cand-9991", obj="cand-0421", predicate="pastoral_drawings_compared_with_boucher",
        claim="Haskell compares the pastoral compositions in Piazzetta's Gerusalemme drawings with Boucher's art, while judging Piazzetta's depicted world less artificial.",
        quote=pastoral_quote, line_start=37, line_end=37, rc=True,
        mentions=["cand-9991", "cand-1907", "cand-0421"],
        qualification="This records Haskell's explicit aesthetic comparison only; it does not assert influence, copying, or a relation between specific works.",
    )

    added_statements = [opportunity, discovery, aesthetic, monasteries, international, pastoral]
    for row in added_statements:
        if row["statement_id"] in by_id:
            raise SystemExit(f"preflight failed: statement ID already exists: {row['statement_id']}")

    # Correct the type of this P.csv headword row; keep its identity separate pending S3.
    candidate_by_id["cand-1913"]["suggested_type"] = "person"
    candidate_by_id["cand-1913"]["detail"] = "P.csv headword is Giovanni Battista Piazzetta; this index row's subentry concerns the Gerusalemme illustrations, not a separate work. Keep it distinct from other Piazzetta index rows pending S3 identity alignment."
    candidates.extend(new_candidate_rows)
    mentions.extend(added_mentions)

    # Keep the new p.335 statements adjacent to the existing body statements and before p.336.
    insert_at = next(i for i, row in enumerate(statements) if row["statement_id"] == "st-chp13-p335-recurti-published-devotional-book") + 1
    statements[insert_at:insert_at] = added_statements

    print(f"segment={SEGMENT_ID}; SHA-256={SEGMENT_SHA256}; p335 statements before={len(p335)}")
    print(f"classifications={len(decisions)} existing unset statements; added statements={len(added_statements)}")
    print("decisions:")
    for key, value in decisions.items():
        print(f"  {key}: {value}")
    print("new statement IDs:")
    for row in added_statements:
        print(f"  {row['statement_id']}: {row['qualifiers']['relation_candidate']}")
    print("new candidates:", ", ".join(row["candidate_id"] for row in new_candidate_rows))
    print("new mentions:", ", ".join(row["mention_id"] for row in added_mentions))
    if not args.apply:
        print("DRY RUN only; no files written. Pass --apply to write after review.")
        return

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n").encode("utf-8")
    with tempfile.SpooledTemporaryFile(mode="w+", encoding="utf-8-sig", newline="", max_size=8 * 1024 * 1024) as stream:
        writer = csv.DictWriter(stream, fieldnames=candidate_fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(candidates); stream.seek(0); candidate_text = stream.read()
    with tempfile.SpooledTemporaryFile(mode="w+", encoding="utf-8-sig", newline="", max_size=8 * 1024 * 1024) as stream:
        writer = csv.DictWriter(stream, fieldnames=mention_fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(mentions); stream.seek(0); mention_text = stream.read()
    write_atomic(STATEMENTS, statement_bytes)
    write_atomic(CANDIDATES, candidate_text.encode("utf-8-sig"))
    write_atomic(MENTIONS, mention_text.encode("utf-8-sig"))
    print("APPLIED. Backups saved for statements, candidates, and mentions.")
    print("post-write SHA-256:")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"  {path.name}: {digest(path)}")


if __name__ == "__main__":
    main()
