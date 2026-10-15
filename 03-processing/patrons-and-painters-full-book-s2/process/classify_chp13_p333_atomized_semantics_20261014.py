from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p333_page_review_20261014.png"
SEGMENT = "chp-13:13_CHP-13_intro:l14-19"
BACKUP_SUFFIX = ".bak-s2-ch13-p333-atomized-semantics-20261014"
EXPECTED = {
    TABLE.name: "79ca94b370a7cd2e786da7a4061c87115a07059e9c6841606facb5e170b773c8",
    CANDIDATES.name: "a02c2e265bba818f3b5cbac7b259758e1d478f0c8e3724cd70e4aa53e1a3cb89",
    MENTIONS.name: "e6a221b2fd8a8f948d0ea1a23b4317d631914c551433793878d7de98a32bc306",
    SEGMENTS.name: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE.name: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF.name: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
    IMAGE.name: "9b14143b0d9d755b050dc1f07f47994934d034a1eff4ea75fc01ed168b13eeaf",
}

TARGET_IDS = {
    "st-chp13-p333-anonymous-quotation-on-poem-collections",
    "st-chp13-p333-artists-made-own-engravings",
    "st-chp13-p333-barbarigo-1765-pamphlet-instructions-through-gozzi",
    "st-chp13-p333-collections-popular-and-burdened-poets",
    "st-chp13-p333-commemorative-poetry-for-noble-ceremonies",
    "st-chp13-p333-contemporary-pictures-made-for-engraving",
    "st-chp13-p333-drawings-made-for-book-illustration",
    "st-chp13-p333-four-illustration-production-routes",
    "st-chp13-p333-lovisa-book-sponsored-example",
    "st-chp13-p333-pamphlet-format-and-commissioned-design",
    "st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage",
    "st-chp13-p333-publishers-enabled-high-cost-artist-commissions",
    "st-chp13-p333-publishers-owned-commercial-premises",
    "st-chp13-p333-publishers-sales-employment-and-commissions",
    "st-chp13-p333-reproduction-practice-and-patronage-relevance",
    "st-chp13-p333-subscribers-and-dedications-reveal-target-market",
    "st-chp13-p333-two-categories-of-illustrated-books",
}

UNSET_CLASSIFICATIONS = {
    "st-chp13-p333-anonymous-quotation-on-poem-collections": True,
    "st-chp13-p333-artists-made-own-engravings": False,
    "st-chp13-p333-collections-popular-and-burdened-poets": True,
    "st-chp13-p333-commemorative-poetry-for-noble-ceremonies": True,
    "st-chp13-p333-contemporary-pictures-made-for-engraving": False,
    "st-chp13-p333-drawings-made-for-book-illustration": False,
    "st-chp13-p333-four-illustration-production-routes": False,
    "st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage": True,
    "st-chp13-p333-publishers-enabled-high-cost-artist-commissions": False,
    "st-chp13-p333-publishers-owned-commercial-premises": False,
    "st-chp13-p333-reproduction-practice-and-patronage-relevance": False,
    "st-chp13-p333-subscribers-and-dedications-reveal-target-market": False,
    "st-chp13-p333-two-categories-of-illustrated-books": False,
}

FALSE_NOTES = {
    "st-chp13-p333-artists-made-own-engravings": "This is a general production route; no particular artist or engraving is identified.",
    "st-chp13-p333-contemporary-pictures-made-for-engraving": "This is a production category; no particular picture, painter, or engraver is identified.",
    "st-chp13-p333-drawings-made-for-book-illustration": "This is a general production route; no particular drawing, book, or artist is identified.",
    "st-chp13-p333-four-illustration-production-routes": "This is Haskell's classification of four production routes, not a relation between specific entities.",
    "st-chp13-p333-publishers-enabled-high-cost-artist-commissions": "This describes the capacity required for such ventures; it does not identify an actual commission involving Tiepolo or Piazzetta.",
    "st-chp13-p333-publishers-owned-commercial-premises": "This is a generalization about publishers and commercial premises; no particular owner or premises is identified.",
    "st-chp13-p333-reproduction-practice-and-patronage-relevance": "This is Haskell's assessment of a general practice's relevance to patronage history, not a distinct entity relation.",
    "st-chp13-p333-subscribers-and-dedications-reveal-target-market": "This is a methodological statement about what lists and dedications can reveal; it names no specific subscriber, book, or target market.",
    "st-chp13-p333-two-categories-of-illustrated-books": "This is a two-part genre classification, not a formal relation between identified entities.",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12120", "index_entry_id": "",
        "canonical_name": "Printmakers employed by Venetian publishers", "index_page_range": "",
        "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Source-defined collective of printmakers employed by publishers dealing in loose prints or illustrated books. No individuals or membership list is named.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L17",
    },
    {
        "candidate_id": "cand-12121", "index_entry_id": "",
        "canonical_name": "Artists considered suitable for Venetian publishers' commissions", "index_page_range": "",
        "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Source-defined group of artists whom publishers selected for drawings or sometimes paintings; no individuals or membership list is supplied.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L17",
    },
    {
        "candidate_id": "cand-12122", "index_entry_id": "",
        "canonical_name": "Noble ceremonies commemorated by Venetian verse collections", "index_page_range": "",
        "suggested_type": "event", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell names a source-defined class of ceremonies: processional taking up of office, marriage, entry of a young woman into a convent, and similar occasions. No particular event, date, or participant is identified.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L18",
    },
    {
        "candidate_id": "cand-12123", "index_entry_id": "",
        "canonical_name": "Venetian poets required to contribute verses to commemorative collections", "index_page_range": "",
        "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Source-described collective of Venetian poets required to contribute verses to the commemorative collections. Individuals and membership are not identified.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L19",
    },
    {
        "candidate_id": "cand-12124", "index_entry_id": "",
        "canonical_name": "Fine artists supported by Venetian commemorative collections", "index_page_range": "",
        "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says the collections were the mainstay of many fine artists; he names no artists or membership list.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L19",
    },
    {
        "candidate_id": "cand-12125", "index_entry_id": "",
        "canonical_name": "Public audience for the commemorative verse collections", "index_page_range": "",
        "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "The source says the collections were enormously popular with the public. It supplies no audience composition, count, or individual readers.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L19",
    },
]

NEW_MENTIONS = [
    {"mention_id": "m-s2-ch13-p333-024", "candidate_id": "cand-12120", "surface_form": "print makers", "start_char": 1271, "end_char": 1283, "note": "Group endpoint for the publisher-employment claim; no individuals are named."},
    {"mention_id": "m-s2-ch13-p333-025", "candidate_id": "cand-12121", "surface_form": "the artists they found suitable", "start_char": 1338, "end_char": 1369, "note": "Source-defined group commissioned by publishers; no individuals are named."},
    {"mention_id": "m-s2-ch13-p333-026", "candidate_id": "cand-12122", "surface_form": "specific ceremonies", "start_char": 1860, "end_char": 1879, "note": "Group of event types, not identified individual ceremonies."},
    {"mention_id": "m-s2-ch13-p333-027", "candidate_id": "cand-12123", "surface_form": "Venetian poets", "start_char": 2750, "end_char": 2764, "note": "Source-described group required to contribute verses; individual poets are not identified."},
    {"mention_id": "m-s2-ch13-p333-028", "candidate_id": "cand-12124", "surface_form": "many fine artists", "start_char": 2824, "end_char": 2841, "note": "Source-described beneficiaries; the artists are not individually identified."},
    {"mention_id": "m-s2-ch13-p333-029", "candidate_id": "cand-12125", "surface_form": "the public", "start_char": 2872, "end_char": 2882, "note": "Collective audience named generally; composition and individual readers are unknown."},
]

NEW_STATEMENT_IDS = {
    "st-chp13-p333-publishers-employed-printmakers",
    "st-chp13-p333-publishers-commissioned-suitable-artists",
    "st-chp13-p333-publishers-patronized-printmakers",
    "st-chp13-p333-poem-collections-required-contributions-from-venetian-poets",
    "st-chp13-p333-poem-collections-supported-fine-artists",
    "st-chp13-p333-publishers-depended-on-patronage-for-expensive-ventures",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_csv_rows(path: Path, new_rows: list[dict[str, object]]) -> bytes:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames:
        raise SystemExit(f"missing CSV header: {path.name}")
    out = [dict(row) for row in rows]
    out.extend({key: str(row.get(key, "")) for key in fieldnames} for row in new_rows)
    from io import StringIO
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(out)
    return buffer.getvalue().encode("utf-8")


def new_statement(template: dict, statement_id: str, subject: str | None, object_: str | None,
                  predicate: str, claim: str, quote: str, line: int,
                  mentioned: list[str], qualification: str) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line,
            "source_line_end": line,
            "printed_page": 333,
            "pdf_physical_page": 2,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": True,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Atomize and classify Chapter 13 p.333 S2 statements")
    parser.add_argument("--apply", action="store_true", help="write after exact source, row-set, and offset checks")
    args = parser.parse_args()

    paths = (TABLE, CANDIDATES, MENTIONS, SEGMENTS, SOURCE, PDF, IMAGE)
    actual = {path.name: sha(path) for path in paths}
    if actual != EXPECTED:
        raise SystemExit(f"preflight hash mismatch; no writes made: {actual}")

    rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement_id in table")
    target = [row for row in rows if row.get("segment_id") == SEGMENT]
    if {row["statement_id"] for row in target} != TARGET_IDS:
        raise SystemExit("p.333 statement set changed")
    unset = {row["statement_id"] for row in target if "relation_candidate" not in row.get("qualifiers", {})}
    if unset != set(UNSET_CLASSIFICATIONS):
        raise SystemExit(f"p.333 unset statement set changed: {unset}")
    existing = {row["statement_id"]: row["qualifiers"].get("relation_candidate") for row in target if row["statement_id"] not in UNSET_CLASSIFICATIONS}
    expected_existing = {
        "st-chp13-p333-barbarigo-1765-pamphlet-instructions-through-gozzi": True,
        "st-chp13-p333-lovisa-book-sponsored-example": True,
        "st-chp13-p333-pamphlet-format-and-commissioned-design": True,
        "st-chp13-p333-publishers-sales-employment-and-commissions": False,
    }
    if existing != expected_existing:
        raise SystemExit(f"p.333 already-classified rows changed: {existing}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("one or more planned statement IDs already exist")

    candidates = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
    candidate_ids = {row["candidate_id"] for row in candidates}
    planned_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if candidate_ids & planned_candidate_ids or len(planned_candidate_ids) != len(NEW_CANDIDATES):
        raise SystemExit("planned candidate IDs are not unused and unique")
    mentions = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
    mention_ids = {row["mention_id"] for row in mentions}
    planned_mention_ids = {row["mention_id"] for row in NEW_MENTIONS}
    if mention_ids & planned_mention_ids or len(planned_mention_ids) != len(NEW_MENTIONS):
        raise SystemExit("planned mention IDs are not unused and unique")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_meta = next(row for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()) if row["segment_id"] == SEGMENT)
    segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1:segment_meta["line_end"]])
    if not segment_text.startswith("[Page 333]\n"):
        raise SystemExit("p.333 segment text changed")
    for row in target:
        qualifiers = row["qualifiers"]
        block = "\n".join(source_lines[qualifiers["source_line_start"] - 1:qualifiers["source_line_end"]])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")
    for row in NEW_MENTIONS:
        if segment_text[row["start_char"]:row["end_char"]] != row["surface_form"]:
            raise SystemExit(f"mention offset mismatch: {row['mention_id']}")

    def quote(needle: str) -> str:
        start = segment_text.find(needle)
        if start < 0:
            raise SystemExit(f"source quote not found: {needle}")
        return segment_text[start:start + len(needle)]

    for statement_id, decision in UNSET_CLASSIFICATIONS.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = decision
        if statement_id in FALSE_NOTES:
            by_id[statement_id]["qualifiers"]["qualification"] = FALSE_NOTES[statement_id]

    # The ceremony endpoint is an event group, not the nobility as a social estate.
    ceremony = by_id["st-chp13-p333-commemorative-poetry-for-noble-ceremonies"]
    ceremony["object_candidate_id"] = "cand-12122"
    ceremony["predicate"] = "commemorated_noble_ceremonies"
    ceremony["qualifiers"]["qualification"] = (
        "The source describes a group of ceremony types involving the nobility. "
        "No individual ceremony, date, family, or participant is identified."
    )
    ceremony["qualifiers"]["mentioned_candidate_ids"] = ["cand-9985", "cand-8108", "cand-12122"]

    anonymous = by_id["st-chp13-p333-anonymous-quotation-on-poem-collections"]
    if anonymous.get("object_candidate_id") != "cand-9985" or anonymous.get("subject_candidate_id") is not None:
        raise SystemExit("cross-page quotation endpoints changed")
    anonymous["subject_candidate_id"] = "cand-0369"
    anonymous["predicate"] = "commentator_on"
    anonymous["qualifiers"]["qualification"] = (
        "The p.334 continuation and printed note identify Saverio Bettinelli as the speaker. "
        "His quoted commentary concerns the social use of the commemorative verse collections; "
        "it is an attributed evaluation, not a universal fact about every collection."
    )
    anonymous["qualifiers"]["mentioned_candidate_ids"] = ["cand-0369", "cand-9985"]

    # Keep each group relationship as its own source-backed S2 claim.
    popular = by_id["st-chp13-p333-collections-popular-and-burdened-poets"]
    popular["object_candidate_id"] = "cand-12125"
    popular["predicate"] = "popular_with"
    popular["qualifiers"]["claim"] = "Haskell says the commemorative collections were enormously popular with the public."
    popular["qualifiers"]["qualification"] = "The public is a source-named collective audience; its composition and individual readers are unknown."
    popular["qualifiers"]["mentioned_candidate_ids"] = ["cand-9985", "cand-12125"]
    popular["qualifiers"].pop("ocr_corrections", None)

    sales = by_id["st-chp13-p333-publishers-sales-employment-and-commissions"]
    sales["predicate"] = "dealt_in_loose_prints_or_illustrated_books"
    sales["qualifiers"]["claim"] = "Haskell says publishers dealt either in sets of loose prints or in illustrated books."
    sales["qualifiers"]["qualification"] = "This is a general commercial practice; the entity relations in the next sentence are recorded separately."
    sales["qualifiers"]["mentioned_candidate_ids"] = ["cand-2068"]
    sales["original_quote"] = quote("They dealt either in sets of loose prints or in illustrated books.")

    publisher_patron = by_id["st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage"]
    publisher_patron["object_candidate_id"] = "cand-12121"
    publisher_patron["predicate"] = "acted_as_patron_to"
    publisher_patron["qualifiers"]["claim"] = "Haskell says publishers acted as patrons through their employment and commissioning of artists."
    publisher_patron["qualifiers"]["qualification"] = "The antecedent is the immediately preceding employment and commissioning of source-described artists; no individuals are named."
    publisher_patron["qualifiers"]["mentioned_candidate_ids"] = ["cand-2068", "cand-12121"]
    publisher_patron["original_quote"] = quote("In this way they were considerable patrons in their own right")

    new_statements = [
        new_statement(
            sales, "st-chp13-p333-publishers-employed-printmakers", "cand-2068", "cand-12120",
            "employed_printmakers", "Haskell says publishers employed printmakers.",
            quote("In either case they employed the print makers"), 17,
            ["cand-2068", "cand-12120"],
            "The source identifies a collective employment relation but no individual printmakers.",
        ),
        new_statement(
            sales, "st-chp13-p333-publishers-commissioned-suitable-artists", "cand-2068", "cand-12121",
            "commissioned_work_from_suitable_artists",
            "Haskell says publishers commissioned drawings or sometimes paintings from artists they found suitable.",
            quote("commissioned drawings or sometimes paintings from the artists they found suitable"), 17,
            ["cand-2068", "cand-12121"],
            "The artist group is defined by the source's suitability criterion; no individual commission is identified.",
        ),
        new_statement(
            publisher_patron, "st-chp13-p333-publishers-patronized-printmakers",
            "cand-2068", "cand-12120", "patronized_printmakers",
            "Haskell says publishers acted as patrons through their employment of printmakers.",
            quote("In this way they were considerable patrons in their own right"), 17,
            ["cand-2068", "cand-12120"],
            "The source links publisher patronage to the immediately preceding employment practice; no individual printmakers are named.",
        ),
        new_statement(
            popular, "st-chp13-p333-poem-collections-required-contributions-from-venetian-poets",
            "cand-9985", "cand-12123", "required_verse_contributions_from",
            "Haskell says the collections were the plague of Venetian poets required to contribute verses.",
            quote("These collections, which were the plague of Venetian poets who were required to contribute verses"), 19,
            ["cand-9985", "cand-12123"],
            "This is Haskell's claim about a source-described collective; no individual poets or membership list is supplied.",
        ),
        new_statement(
            popular, "st-chp13-p333-poem-collections-supported-fine-artists",
            "cand-9985", "cand-12124", "supported_many_fine_artists",
            "Haskell says the collections were the mainstay of many fine artists.",
            quote("the mainstay of many fine artists"), 19,
            ["cand-9985", "cand-12124"],
            "The source identifies a beneficiary group but names no artists or membership list.",
        ),
        new_statement(
            publisher_patron, "st-chp13-p333-publishers-depended-on-patronage-for-expensive-ventures",
            "cand-2068", None, "depended_on_patronage_for_expensive_ventures",
            "Haskell says publishers themselves sometimes depended on patronage to make expensive ventures possible.",
            quote("they themselves depended on patronage to make it possible"), 17,
            ["cand-2068"],
            "The source does not identify the patronage providers or a particular funded venture; keep the external endpoint open.",
        ),
    ]

    for row in NEW_CANDIDATES:
        if row["suggested_type"] not in {"term", "event"} or row["status"] != "open":
            raise SystemExit(f"invalid candidate type or status: {row['candidate_id']}")

    new_rows = rows + new_statements
    updated_target = [row for row in new_rows if row.get("segment_id") == SEGMENT]
    totals = {
        "true": sum(row["qualifiers"].get("relation_candidate") is True for row in updated_target),
        "false": sum(row["qualifiers"].get("relation_candidate") is False for row in updated_target),
        "unset": sum("relation_candidate" not in row["qualifiers"] for row in updated_target),
    }
    if len(updated_target) != 23 or totals != {"true": 13, "false": 10, "unset": 0}:
        raise SystemExit(f"unexpected p.333 totals: rows={len(updated_target)}, counts={totals}")

    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in new_rows) + "\n").encode("utf-8")
    candidate_bytes = append_csv_rows(CANDIDATES, NEW_CANDIDATES)
    mention_rows = [{"mention_id": row["mention_id"], "segment_id": SEGMENT, **row} for row in NEW_MENTIONS]
    mention_bytes = append_csv_rows(MENTIONS, mention_rows)
    print("p.333 physical page 2: 17 existing statements classified; 6 atomic relation statements added.")
    print("New source-defined groups: printmakers, suitable artists, ceremony-event group, Venetian poets, fine artists, public audience.")
    print("Corrected the ceremony endpoint; linked Bettinelli to the quoted collection category; left unnamed outside patronage open.")
    print("Counts: 13 relation candidates / 10 non-relational claims / 0 unset across 23 statements.")
    print("Rows after apply: candidates", len(candidates) + len(NEW_CANDIDATES), "mentions", len(mentions) + len(NEW_MENTIONS), "statements", len(new_rows))
    print("planned sha256:", "statements", hashlib.sha256(statement_bytes).hexdigest(), "candidates", hashlib.sha256(candidate_bytes).hexdigest(), "mentions", hashlib.sha256(mention_bytes).hexdigest())
    if not args.apply:
        print("preview only; no files written")
        return 0

    backup_map = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (TABLE, CANDIDATES, MENTIONS)}
    existing_backups = [backup.name for backup in backup_map.values() if backup.exists()]
    if existing_backups:
        raise SystemExit(f"backup already exists; refusing overwrite: {existing_backups}")
    for path, backup in backup_map.items():
        shutil.copy2(path, backup)
    TABLE.write_bytes(statement_bytes)
    CANDIDATES.write_bytes(candidate_bytes)
    MENTIONS.write_bytes(mention_bytes)
    print("applied; backups:", ", ".join(backup.name for backup in backup_map.values()))
    for path in (TABLE, CANDIDATES, MENTIONS):
        print(path.name, sha(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
