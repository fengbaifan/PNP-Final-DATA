#!/usr/bin/env python3
"""Resolve remaining S2 classifications in CHP-2 p.24, lines 3–7.

Default mode is a read-only preview. Pass --apply to write after all checks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l3-7"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp2-seci-l3-7-20261012"
EXPECTED = {
    "book-statements.jsonl": "8787731000387730eb81d7ae5c2fb40aa56a8747b465c8b9e4ec8002058502a5",
    "entity-candidates.csv": "fd67cc44fa25b9a12f652e384afe37d263c830dc005b21d83a2a3ff0fd211929",
    "mentions.csv": "cb77bb92cf06f9c04a245c47664ea92977df6c9ec1255e68173af5fa339b0358",
    "s2-coverage.csv": "f9d8087a0b57f3ce84c02b575f6627725ff05ecf7293b81e805ff140ee8ecad9",
}
SOURCE_SHA = "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6"
SEGMENT_SHA = "e45280dcb6462e09193bcc7a45811c533a3159bcfee168eeb203358a26d93a69"
UNSET_IDS = {
    "st-chp2-seci-l3-7-determination",
    "st-chp2-seci-l3-7-dome-completion",
    "st-chp2-seci-l3-7-education-law",
    "st-chp2-seci-l3-7-greater-ambition",
    "st-chp2-seci-l3-7-marriage-plan",
    "st-chp2-seci-l3-7-sixtus-death-reign",
    "st-chp2-seci-l3-7-taste-assessment",
    "st-chp2-seci-l3-7-urban-character",
}
NEW_STATEMENTS = {
    "st-chp2-seci-l3-7-education-in-rome",
    "st-chp2-seci-l3-7-education-in-pisa",
    "st-chp2-seci-l3-7-monsignor-francesco-uncle-of-maffeo",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def statement(
    statement_id: str,
    predicate: str,
    subject: str,
    obj: str | None,
    claim: str,
    quote: str,
    qualification: str,
    *,
    relation: bool,
    relation_note: str,
    mentioned: list[str],
    open_endpoint_reason: str | None = None,
) -> dict:
    q = {
        "source_line_start": 4,
        "source_line_end": 4,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "narrative",
        "qualification": qualification,
        "print_page": 24,
        "relation_candidate": relation,
        "relation_candidate_note": relation_note,
        "mentioned_candidate_ids": mentioned,
    }
    if open_endpoint_reason:
        q["open_endpoint_reason"] = open_endpoint_reason
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()

    for name, expected in EXPECTED.items():
        actual = digest(TABLES / name)
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected CHP-2 section source changed")

    paths = {name: TABLES / name for name in EXPECTED}
    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected source segment fingerprint changed")
    if len(source_lines) < 7:
        raise SystemExit("protected source range is incomplete")

    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(statement_by_id) != len(statements) or len(candidate_by_id) != len(candidates):
        raise SystemExit("duplicate statement or candidate IDs")
    target_rows = [row for row in statements if row["segment_id"] == SEGMENT_ID]
    unset_now = {row["statement_id"] for row in target_rows if row["qualifiers"].get("relation_candidate") is None}
    if unset_now != UNSET_IDS:
        raise SystemExit(f"unexpected p.24 unset set: {sorted(unset_now)}")
    if NEW_STATEMENTS & set(statement_by_id):
        raise SystemExit("one or more new p.24 statement IDs already exist")

    # These seven statements describe scalar claims or authorial assessments.
    false_notes = {
        "st-chp2-seci-l3-7-determination": "Evaluative statement about Maffeo’s disposition; it records no relation between distinct entities.",
        "st-chp2-seci-l3-7-dome-completion": "A completion date is a work attribute; no completing agent or other relation endpoint is named.",
        "st-chp2-seci-l3-7-greater-ambition": "Haskell’s qualified speculation about an unspecified ambition, not a relation claim.",
        "st-chp2-seci-l3-7-sixtus-death-reign": "Death timing and reign length are person-level temporal attributes, not a relation between entities.",
        "st-chp2-seci-l3-7-taste-assessment": "“Taste” is an authorial evaluation of Maffeo, not a relation or independently identified entity.",
        "st-chp2-seci-l3-7-urban-character": "Aesthetic description of Rome’s buildings and infrastructure; no specific work-to-agent relation is asserted.",
    }
    for statement_id, note in false_notes.items():
        row = statement_by_id[statement_id]
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = note
    marriage = statement_by_id["st-chp2-seci-l3-7-marriage-plan"]
    marriage["qualifiers"]["relation_candidate"] = True
    marriage["qualifiers"]["relation_candidate_note"] = (
        "The source reports a specific intended marriage that came to nothing. Preserve it as a relation candidate for the unrealized plan, not as an established marriage."
    )
    marriage["qualifiers"]["open_endpoint_reason"] = (
        "The intended spouse is not identified, and Haskell says the plan came to nothing; no individual endpoint or completed marriage is asserted."
    )

    # Replace the composite education claim with two place relations and one scalar degree statement.
    education = statement_by_id["st-chp2-seci-l3-7-education-law"]
    education.update({
        "predicate": "took_law_degree",
        "object_candidate_id": None,
        "original_quote": "took a degree in law",
    })
    education["qualifiers"].update({
        "claim": "Maffeo took a degree in law.",
        "qualification": "Haskell names neither the degree-granting institution nor a city where the degree was earned; preserve this as a personal qualification.",
        "relation_candidate": False,
        "relation_candidate_note": "The degree is a personal educational attribute; the institution is unspecified and no entity-to-entity endpoint is asserted.",
    })
    new_statements = [
        statement(
            "st-chp2-seci-l3-7-education-in-rome", "continued_education_in", "cand-3104", "cand-3126",
            "Maffeo continued his education in Rome.", "There and at Pisa he continued his education",
            "“There” refers to Rome in the preceding sentence; no particular school, teacher, or degree institution is identified.",
            relation=True,
            relation_note="The clause explicitly locates Maffeo’s continued education in Rome through the anaphoric “There”; the location is resolved to the Rome named immediately before.",
            mentioned=["cand-3104", "cand-3126"],
        ),
        statement(
            "st-chp2-seci-l3-7-education-in-pisa", "continued_education_in", "cand-3104", "cand-3956",
            "Maffeo continued his education in Pisa.", "at Pisa he continued his education",
            "No particular school, teacher, or degree institution is identified.",
            relation=True,
            relation_note="The clause explicitly locates Maffeo’s continued education in Pisa; the existing Pisa candidate and mention are reused.",
            mentioned=["cand-3104", "cand-3956"],
        ),
        statement(
            "st-chp2-seci-l3-7-monsignor-francesco-uncle-of-maffeo", "uncle_of_reported", "cand-0208", "cand-3104",
            "Haskell identifies Monsignor Francesco as Maffeo Barberini’s uncle.", "his uncle Monsignor Francesco",
            "The named Monsignor Francesco is distinct from the fourteenth-century ancestor Francesco mentioned later in the paragraph.",
            relation=True,
            relation_note="The kinship term “uncle” is explicit and connects two existing person candidates; no further family line is inferred.",
            mentioned=["cand-0208", "cand-3104"],
        ),
    ]

    # Add an exact mention for the anaphoric Rome reference used by the new statement.
    flat_segment = " ".join(" ".join(source_lines[2:7]).split())
    there_start = flat_segment.find("There")
    if there_start < 0 or flat_segment[there_start : there_start + 5] != "There":
        raise SystemExit("anaphoric “There” mention is not in the protected source range")
    new_mentions = [{
        "mention_id": "m-chp2-seci-l3-7-0030",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-3126",
        "surface_form": "There",
        "start_char": str(there_start),
        "end_char": str(there_start + len("There")),
        "note": "Anaphoric place mention resolved to Rome from the preceding clause; used as the location of Maffeo’s continued education.",
    }]

    referenced = set()
    for row in new_statements:
        if row["original_quote"] not in "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1 : row["qualifiers"]["source_line_end"]]):
            raise SystemExit(f"source quote outside L4: {row['statement_id']}")
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row["qualifiers"]["mentioned_candidate_ids"])
    referenced.update(row["candidate_id"] for row in new_mentions)
    missing = sorted(referenced - set(candidate_by_id))
    if missing:
        raise SystemExit(f"missing candidate foreign keys: {missing}")
    mention_ids = {row["mention_id"] for row in mentions}
    if len(mention_ids) != len(mentions) or any(row["mention_id"] in mention_ids for row in new_mentions):
        raise SystemExit("duplicate mention IDs")
    keys = [(row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"]) for row in mentions + new_mentions]
    if len(keys) != len(set(keys)):
        raise SystemExit("new mention conflicts with an existing mention natural key")
    if flat_segment[int(new_mentions[0]["start_char"]) : int(new_mentions[0]["end_char"])] != "There":
        raise SystemExit("anaphoric mention span does not match S0 text")

    statements.extend(new_statements)
    mentions.extend(new_mentions)
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.24 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up on printed p.24 resolved eight formerly unset relation_candidate values. "
        "The education clause is atomized into continued education in Rome and Pisa plus a law-degree fact; “There” is mapped to Rome. "
        "The explicit Monsignor Francesco–Maffeo uncle relationship is recorded. The unfulfilled marriage plan remains an open relation candidate with no named spouse; "
        "authorial evaluations and personal/time attributes are non-relational. No source or KU changed."
    )

    final_target = [row for row in statements if row["segment_id"] == SEGMENT_ID]
    if any(row["qualifiers"].get("relation_candidate") is None for row in final_target):
        raise SystemExit("p.24 segment still has unset relation_candidate fields")
    if len(final_target) != 27 or len(new_statements) != 3 or len(new_mentions) != 1:
        raise SystemExit(f"unexpected p.24 result size: {len(final_target)} statements")
    if marriage["qualifiers"].get("relation_candidate") is not True or not marriage["qualifiers"].get("open_endpoint_reason"):
        raise SystemExit("unrealized marriage plan lacks an explicit open endpoint")
    if education["qualifiers"].get("relation_candidate") is not False or education["object_candidate_id"] is not None:
        raise SystemExit("law degree fact was not separated from place relations")

    updated = {
        "book-statements.jsonl": statements,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    summary = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2.pdf print p.24 / normalized S0 L3-7",
        "classified_unset_statement_ids": sorted(UNSET_IDS),
        "new_statements": [row["statement_id"] for row in new_statements],
        "new_mention": new_mentions[0],
        "segment_statement_count": len(final_target),
        "segment_unset_count": sum(row["qualifiers"].get("relation_candidate") is None for row in final_target),
        "source_unchanged": True,
        "coverage_disposition": coverage_rows[0]["disposition"],
        "coverage_migration_status": coverage_rows[0]["migration_status"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temp_paths: dict[str, Path] = {}
    try:
        for name in updated:
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
        for name, rows in updated.items():
            path = paths[name]
            temp = path.with_name(path.name + ".tmp-s2-chp2-p24")
            if temp.exists():
                raise SystemExit(f"stale temp file exists; refusing overwrite: {temp.name}")
            if name.endswith(".jsonl"):
                write_jsonl(temp, rows)
            else:
                write_csv(temp, rows)
            temp_paths[name] = temp
        for name, temp in temp_paths.items():
            os.replace(temp, paths[name])
    except Exception:
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        for temp in temp_paths.values():
            if temp.exists():
                temp.unlink()
        raise
    summary["backups"] = {name: path.name for name, path in backups.items()}
    summary["post_hashes"] = {name: digest(paths[name]) for name in updated}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
