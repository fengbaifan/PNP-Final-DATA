from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p333_page_review_20261014.png"
SEGMENT = "chp-13:13_CHP-13_intro:l14-19"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch13-p333-semantics-20261014")
EXPECTED = {
    TABLE.name: "79ca94b370a7cd2e786da7a4061c87115a07059e9c6841606facb5e170b773c8",
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

UNSET_IDS = {
    "st-chp13-p333-anonymous-quotation-on-poem-collections",
    "st-chp13-p333-artists-made-own-engravings",
    "st-chp13-p333-collections-popular-and-burdened-poets",
    "st-chp13-p333-commemorative-poetry-for-noble-ceremonies",
    "st-chp13-p333-contemporary-pictures-made-for-engraving",
    "st-chp13-p333-drawings-made-for-book-illustration",
    "st-chp13-p333-four-illustration-production-routes",
    "st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage",
    "st-chp13-p333-publishers-enabled-high-cost-artist-commissions",
    "st-chp13-p333-publishers-owned-commercial-premises",
    "st-chp13-p333-reproduction-practice-and-patronage-relevance",
    "st-chp13-p333-subscribers-and-dedications-reveal-target-market",
    "st-chp13-p333-two-categories-of-illustrated-books",
}

CLASSIFICATIONS = {
    "st-chp13-p333-anonymous-quotation-on-poem-collections": True,
    "st-chp13-p333-artists-made-own-engravings": False,
    "st-chp13-p333-collections-popular-and-burdened-poets": False,
    "st-chp13-p333-commemorative-poetry-for-noble-ceremonies": True,
    "st-chp13-p333-contemporary-pictures-made-for-engraving": False,
    "st-chp13-p333-drawings-made-for-book-illustration": False,
    "st-chp13-p333-four-illustration-production-routes": False,
    "st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage": False,
    "st-chp13-p333-publishers-enabled-high-cost-artist-commissions": False,
    "st-chp13-p333-publishers-owned-commercial-premises": False,
    "st-chp13-p333-reproduction-practice-and-patronage-relevance": False,
    "st-chp13-p333-subscribers-and-dedications-reveal-target-market": False,
    "st-chp13-p333-two-categories-of-illustrated-books": False,
}

FALSE_NOTES = {
    "st-chp13-p333-artists-made-own-engravings": "This names a general production route, not an identified artist or engraving relationship.",
    "st-chp13-p333-collections-popular-and-burdened-poets": "This is Haskell's broad account of popularity and occupational effects; no specific poet, artist, or collection is identified.",
    "st-chp13-p333-contemporary-pictures-made-for-engraving": "This is a production category; no particular picture, painter, or engraver is identified.",
    "st-chp13-p333-drawings-made-for-book-illustration": "This is a general production route; no particular drawing, book, or artist is identified.",
    "st-chp13-p333-four-illustration-production-routes": "This is Haskell's classification of four production routes, not a relation between specific entities.",
    "st-chp13-p333-publishers-as-patrons-and-reliance-on-patronage": "The statement distinguishes publishers' own patronage from unspecified outside patronage; no artist, work, or external patron is named.",
    "st-chp13-p333-publishers-enabled-high-cost-artist-commissions": "This describes the capacity required for such ventures and explicitly does not identify an actual commission involving Tiepolo or Piazzetta.",
    "st-chp13-p333-publishers-owned-commercial-premises": "This is a generalization about classes of publishers and generic shops/printing works; no particular owner or premises is identified.",
    "st-chp13-p333-reproduction-practice-and-patronage-relevance": "This is Haskell's assessment of a general practice's relevance to patronage history, not a distinct entity relation.",
    "st-chp13-p333-subscribers-and-dedications-reveal-target-market": "This is a methodological statement about what lists and dedications can reveal; it names no subscriber, book, or target market.",
    "st-chp13-p333-two-categories-of-illustrated-books": "This is a two-part genre classification, not a formal relation between identified entities.",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify p.333 statements and resolve the cross-page Bettinelli speaker")
    parser.add_argument("--apply", action="store_true", help="write after exact source, row-set, and quote checks")
    args = parser.parse_args()

    actual = {p.name: sha(p) for p in (TABLE, SOURCE, PDF, IMAGE)}
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
    if unset != UNSET_IDS or set(CLASSIFICATIONS) != UNSET_IDS:
        raise SystemExit("p.333 unset statement set changed")
    existing = {row["statement_id"]: row["qualifiers"].get("relation_candidate") for row in target if row["statement_id"] not in UNSET_IDS}
    expected_existing = {
        "st-chp13-p333-barbarigo-1765-pamphlet-instructions-through-gozzi": True,
        "st-chp13-p333-lovisa-book-sponsored-example": True,
        "st-chp13-p333-pamphlet-format-and-commissioned-design": True,
        "st-chp13-p333-publishers-sales-employment-and-commissions": False,
    }
    if existing != expected_existing:
        raise SystemExit(f"p.333 already-classified rows changed: {existing}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if source_lines[13] != "[Page 333]" or not source_lines[18].startswith("Caterina Barbarigo in 1765"):
        raise SystemExit("canonical p.333 source lines changed")
    for row in target:
        q = row["qualifiers"]
        block = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")

    for sid, is_relation in CLASSIFICATIONS.items():
        row = by_id[sid]
        row["qualifiers"]["relation_candidate"] = is_relation
        if sid in FALSE_NOTES:
            row["qualifiers"]["qualification"] = FALSE_NOTES[sid]

    commemoration = by_id["st-chp13-p333-commemorative-poetry-for-noble-ceremonies"]
    commemoration["qualifiers"]["qualification"] = (
        "The source explicitly says this publication category was brought out to commemorate the ceremony group. "
        "The relation stays at genre-to-event-class level; no individual ceremony or publication is identified."
    )

    quote = by_id["st-chp13-p333-anonymous-quotation-on-poem-collections"]
    if quote.get("object_candidate_id") != "cand-9985" or quote.get("subject_candidate_id") is not None:
        raise SystemExit("cross-page quotation endpoints changed")
    quote["subject_candidate_id"] = "cand-0369"
    quote["predicate"] = "commentator_on"
    quote["object_candidate_id"] = "cand-9985"
    quote["qualifiers"]["qualification"] = (
        "The p.334 continuation and printed note identify Saverio Bettinelli as the speaker. "
        "His quoted commentary concerns luxury production and social use of the commemorative verse-book category; "
        "it is an attributed evaluation, not a universal fact about every collection."
    )

    after = [row for row in rows if row.get("segment_id") == SEGMENT]
    counts = {
        "true": sum(row["qualifiers"].get("relation_candidate") is True for row in after),
        "false": sum(row["qualifiers"].get("relation_candidate") is False for row in after),
        "unset": sum("relation_candidate" not in row["qualifiers"] for row in after),
    }
    if counts != {"true": 6, "false": 11, "unset": 0}:
        raise SystemExit(f"unexpected p.333 totals: {counts}")

    output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
    print("p.333 physical page 2: 12 existing unset rows classified; 2 relation candidates added; 0 unset.")
    print("Bettinelli: speaker linked to commemorative verse-book category using commentator_on; p.334 source attribution preserved.")
    print("Counts: 6 true / 11 false / 0 unset; existing four classifications retained.")
    print("planned table sha256:", hashlib.sha256(output).hexdigest())
    if not args.apply:
        print("preview only; no files written")
        return 0
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    TABLE.write_bytes(output)
    print("applied; backup:", BACKUP.name)
    print("written table sha256:", sha(TABLE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
