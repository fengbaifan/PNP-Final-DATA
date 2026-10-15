#!/usr/bin/env python3
"""Review p.341 S2 claims, endpoint mappings, and source mentions; dry-run by default."""

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
SEGMENT_ID = "chp-13:13_CHP-13_intro:l90-96"
SEGMENT_SHA256 = "2aedb9d5ab3791a325d38e6b2a6b963d39fe6faab03ddf8930abde4740e74a95"
PRE_HASHES = {
    STATEMENTS.name: "14eec403afa4d272807c69e234f5b5bf6402d063f0b4bf5e2e40c339fa0a9f06",
    CANDIDATES.name: "32d74cc645a0f3c98a8cf6313fd671433d6feffeecf42869ff53276c835d39f6",
    MENTIONS.name: "036e137e0803b7782d7f619164a4e40c5bb51ba210bc4d84048db4f69e909b5d",
}
BACKUP_SUFFIX = ".bak-s2-ch13-p341-semantic-review-20261014"


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks")
    args = parser.parse_args()
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = digest(path)
        if actual != PRE_HASHES[path.name]:
            raise SystemExit(f"preflight failed: {path.name} SHA-256 changed: {actual}")
    segment = next(
        (row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID),
        None,
    )
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("preflight failed: p.341 segment identity/hash changed")

    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    local = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(local) != 29 or len(by_id) != len(statements):
        raise SystemExit(f"preflight failed: expected 29 unique p.341 statements, found {len(local)}")
    decisions = {
        "st-chp13-p341-unnamed_print_trade_patronage": True,
        "st-chp13-p341-zanetti_birth_and_painting_study": False,
        "st-chp13-p341-zanetti_contact_with_leading_artists": True,
        "st-chp13-p341-zanetti_draughtsman_engraver_collector": False,
        "st-chp13-p341-zanetti_in_venetian_connoisseur_world": True,
        "st-chp13-p341-zanetti_known_as_connoisseur_and_collector": False,
        "st-chp13-p341-zanetti_portrait_reference_and_authorial_interest": False,
        "st-chp13-p341-paris_visit_with_carriera_and_pellegrini": True,
        "st-chp13-p341-zanetti_1720_journey_to_paris": True,
        "st-chp13-p341-zanetti_returned_to_venice_and_went_to_vienna": True,
        "st-chp13-p341-zanetti_returned_to_vienna_in_1736": True,
        "st-chp13-p341-zanetti_visited_london_collectors": True,
        "st-chp13-p341-crespi_pastoral_praised": False,
        "st-chp13-p341-tessin_fondness_for_rococo_and_graceful_subjects": True,
    }
    unset = {
        row["statement_id"]
        for row in local
        if row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(decisions):
        raise SystemExit(f"preflight failed: unexpected unset IDs: {sorted(unset ^ set(decisions))}")
    for statement_id, value in decisions.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = value

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[89:96])
    new_candidates = [
        {
            "candidate_id": "cand-12171",
            "canonical_name": "Venetian artistic scene diversified by print-trade patronage",
            "suggested_type": "term",
            "detail": "Haskell’s broad ‘Venetian scene’ in the p.341 statement about the patronage of unnamed men around print sellers and publishers; distinct from the connoisseur circle cand-10061.",
            "source_line": 91,
        },
        {
            "candidate_id": "cand-12172",
            "canonical_name": "Print sellers and publishers referred to from p.340",
            "suggested_type": "term",
            "detail": "Source-bounded anaphoric group of commercial actors discussed on p.340; not a new organization and not the separate group of men around them (cand-10060).",
            "source_line": 91,
        },
    ]
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        candidate_fields = reader.fieldnames
        candidates = list(reader)
    existing_candidate_ids = {row["candidate_id"] for row in candidates}
    if existing_candidate_ids & {row["candidate_id"] for row in new_candidates}:
        raise SystemExit("preflight failed: one or more p.341 candidate IDs already exist")
    for row in new_candidates:
        line = row.pop("source_line")
        candidates.append({
            "candidate_id": row["candidate_id"],
            "index_entry_id": "",
            "canonical_name": row["canonical_name"],
            "index_page_range": "",
            "suggested_type": row["suggested_type"],
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": row["detail"],
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": SEGMENT_ID + f"#L{line}",
        })

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        mention_fields = reader.fieldnames
        mentions = list(reader)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    expected_mappings = {
        "m-s2-ch13-p341-001": "cand-10060",
        "m-s2-ch13-p341-003": "cand-10060",
        "m-s2-ch13-p341-005": "cand-10061",
    }
    for mention_id, candidate_id in expected_mappings.items():
        if mention_id not in mention_by_id or mention_by_id[mention_id]["candidate_id"] != candidate_id:
            raise SystemExit(f"preflight failed: unexpected mapping for {mention_id}")
    mention_by_id["m-s2-ch13-p341-001"]["candidate_id"] = "cand-12172"
    mention_by_id["m-s2-ch13-p341-001"]["note"] = "Anaphoric group of p.340 print sellers and publishers, distinct from the men grouped around them."
    mention_by_id["m-s2-ch13-p341-005"]["candidate_id"] = "cand-12171"
    mention_by_id["m-s2-ch13-p341-005"]["note"] = "The broad Venetian artistic scene, not the connoisseur circle cand-10061."
    # “both activities” is generic activity wording, not an entity mention.
    if mention_by_id.get("m-s2-ch13-p341-003", {}).get("surface_form") != "both activities":
        raise SystemExit("preflight failed: generic activity mention changed")
    mentions.remove(mention_by_id["m-s2-ch13-p341-003"])

    def revise(statement_id: str, *, subject: str, obj: str | None, predicate: str,
               claim: str, quote: str, qualification: str, mentioned: list[str], relation: bool) -> None:
        row = by_id[statement_id]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = obj
        row["predicate"] = predicate
        row["original_quote"] = quote
        q = row["qualifiers"]
        q["claim"] = claim
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = mentioned
        q["relation_candidate"] = relation

    def add_statement(statement_id: str, subject: str, obj: str | None, predicate: str,
                      claim: str, quote: str, line: int, qualification: str,
                      mentioned: list[str], relation: bool) -> None:
        if statement_id in by_id:
            raise SystemExit(f"preflight failed: {statement_id} already exists")
        if quote not in segment_text:
            raise SystemExit(f"preflight failed: statement quote not in S0: {quote!r}")
        row = {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": {
                "source_line_start": line,
                "source_line_end": line,
                "printed_page": 341,
                "pdf_physical_page": 10,
                "claim": claim,
                "speaker": "Haskell",
                "text_layer": "authorial narrative",
                "qualification": qualification,
                "mentioned_candidate_ids": mentioned,
                "ocr_corrections": [],
                "relation_candidate": relation,
            },
            "original_quote": quote,
            "origin": "book",
            "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        }
        statements.append(row)
        by_id[statement_id] = row

    revise(
        "st-chp13-p341-unnamed_print_trade_patronage",
        subject="cand-10060", obj="cand-12171", predicate="patronage_diversified_venetian_artistic_scene",
        claim="Haskell says the patronage of unnamed men around print sellers and publishers was important in diversifying the Venetian scene.",
        quote="Around these printsellers and publishers was grouped a number.of men who sometimes dabbled in both activities, and whose patronage was very important in diversifying the Venetian scene.",
        qualification="The men are an unnamed source-defined group; the ‘Venetian scene’ is a broad artistic context, not the connoisseur circle described in the next sentence.",
        mentioned=["cand-12172", "cand-10060", "cand-12171"], relation=True,
    )
    by_id["st-chp13-p341-unnamed_print_trade_patronage"]["qualifiers"]["ocr_corrections"] = [
        {"source_line": 91, "ocr": "number.of", "print": "number of", "basis": "CHP-13.pdf physical page 10."}
    ]

    revise(
        "st-chp13-p341-zanetti_birth_and_painting_study",
        subject="cand-2838", obj=None, predicate="born_in_1679",
        claim="Haskell says Antonio Maria Zanetti the Elder was born in 1679.",
        quote="He was born in 1679",
        qualification="This is a biographical attribute; painting study in Venice and Bologna is split into separate place relations.",
        mentioned=["cand-2838"], relation=False,
    )
    add_statement(
        "st-chp13-p341-zanetti-studied-painting-in-venice", "cand-2838", "cand-2719",
        "studied_painting_in_venice", "Haskell says Zanetti studied painting in Venice.",
        "studied painting in Venice", 91,
        "The source supplies no dates or institution.", ["cand-2838", "cand-2719"], True,
    )
    add_statement(
        "st-chp13-p341-zanetti-studied-painting-in-bologna", "cand-2838", "cand-3398",
        "later_studied_painting_in_bologna", "Haskell says Zanetti later studied painting in Bologna.",
        "studied painting in Venice and later Bologna", 91,
        "The source supplies no dates or institution.", ["cand-2838", "cand-3398"], True,
    )
    by_id["st-chp13-p341-zanetti_known_as_connoisseur_and_collector"]["qualifiers"]["ocr_corrections"] = [
        {"source_line": 91, "ocr": "ani", "print": "and", "basis": "CHP-13.pdf physical page 10."}
    ]

    revise(
        "st-chp13-p341-zanetti_returned_to_venice_and_went_to_vienna",
        subject="cand-2838", obj="cand-2772", predicate="seems_to_have_gone_to_vienna_after_returning_to_venice_in_1722",
        claim="Soon after returning to Venice in 1722, Zanetti seems to have gone to Vienna.",
        quote="he seems to have gone to Vienna",
        qualification="The Vienna journey is explicitly qualified by ‘seems’; the preceding return to Venice is recorded separately.",
        mentioned=["cand-2838", "cand-2772"], relation=True,
    )
    add_statement(
        "st-chp13-p341-zanetti-returned-to-venice-in-1722", "cand-2838", "cand-2719",
        "returned_to_venice_in_1722", "Haskell says Zanetti returned to Venice in 1722.",
        "his return to Venice in 1722", 93,
        "The source gives the year of return; the subsequent Vienna journey remains qualified separately.",
        ["cand-2838", "cand-2719"], True,
    )

    revise(
        "st-chp13-p341-zanetti_visited_london_collectors",
        subject="cand-2838", obj="cand-10062", predicate="visited_leading_collectors_in_london",
        claim="In London, Zanetti visited leading collectors.",
        quote="where he visited the leading collectors",
        qualification="The collectors are unnamed; the journey from Paris to London is recorded separately.",
        mentioned=["cand-2838", "cand-1422", "cand-10062"], relation=True,
    )
    add_statement(
        "st-chp13-p341-zanetti-travelled-from-paris-to-london", "cand-2838", "cand-1422",
        "travelled_from_paris_to_london", "Haskell says Zanetti went from Paris to London.",
        "From Paris he went to London", 93,
        "This records the stated route; the visits to collectors are a separate claim.",
        ["cand-2838", "cand-4653", "cand-1422"], True,
    )

    additions = [row for row in statements if row.get("segment_id") == SEGMENT_ID and row["statement_id"] not in {r["statement_id"] for r in local}]
    if len(additions) != 4:
        raise SystemExit(f"preflight failed: expected four new statements, found {len(additions)}")
    if any(row["original_quote"] not in segment_text for row in statements if row.get("segment_id") == SEGMENT_ID):
        raise SystemExit("preflight failed: one or more final p.341 quotes do not match S0")

    print(f"segment={SEGMENT_ID}; SHA-256={SEGMENT_SHA256}; original statements={len(local)}; classified={len(decisions)}")
    print("atomization: birth/study locations; return to Venice/Vienna journey; Paris-to-London route/collector visits")
    print("endpoint repairs: Venetian artistic scene vs connoisseur circle; anaphoric print-seller group; specific city and travel endpoints")
    print("OCR corrections: number.of -> number of; ani -> and (print verified on CHP-13.pdf physical page 10)")
    print(f"new candidates={len(new_candidates)}; removed generic non-entity mention=1; new statements={len(additions)}")
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
    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n").encode("utf-8")
    write_atomic(STATEMENTS, statement_bytes)
    write_atomic(CANDIDATES, csv_bytes(candidate_fields, candidates))
    write_atomic(MENTIONS, csv_bytes(mention_fields, mentions))
    print("APPLIED. Backups saved for statements, candidates, and mentions.")
    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        print(f"  {path.name}: {digest(path)}")


if __name__ == "__main__":
    main()
