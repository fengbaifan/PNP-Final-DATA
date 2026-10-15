#!/usr/bin/env python3
"""Resolve remaining S2 classifications and collection mapping in CHP-2 p.28."""
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
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l82-93"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp2-seci-l82-93-20261012"
EXPECTED = {
    "book-statements.jsonl": "4b1f21bb210418c97434d188838c65af7787b39d1120a9db4f419a7bc58ff685",
    "entity-candidates.csv": "fd67cc44fa25b9a12f652e384afe37d263c830dc005b21d83a2a3ff0fd211929",
    "mentions.csv": "ff30b863260bf4b8418473e8193707659e40664347f9d64deb112ce7e58a7865",
    "s2-coverage.csv": "d4b7d813ec64ef7cc6aa353239c1151ad6b82c0b818a06b3d1667124c2f7d34e",
}
SOURCE_SHA = "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6"
SEGMENT_SHA = "e8d171c35c16faef3ca1970ab729409b5c192e154c06f6baa0352c2ef76c139d"
UNSET = {
    "st-chp2-seci-l82-93-borghese-policy-shift",
    "st-chp2-seci-l82-93-classic-reaction",
    "st-chp2-seci-l82-93-collection-representation",
    "st-chp2-seci-l82-93-collection-taste",
    "st-chp2-seci-l82-93-court-desertion",
    "st-chp2-seci-l82-93-del-monte-age",
    "st-chp2-seci-l82-93-del-monte-character",
    "st-chp2-seci-l82-93-del-monte-quote-fragment",
    "st-chp2-seci-l82-93-domenichino-encouraged",
    "st-chp2-seci-l82-93-guercino-modification",
    "st-chp2-seci-l82-93-lifestyle-cultural-impact",
    "st-chp2-seci-l82-93-long-term-impact",
    "st-chp2-seci-l82-93-other-patrons",
    "st-chp2-seci-l82-93-roman-fortune-pattern",
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
    coverage = read_csv(paths["s2-coverage.csv"])
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.28 source segment fingerprint changed")
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {row["statement_id"] for row in statements if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None}
    if unset != UNSET:
        raise SystemExit(f"unexpected p.28 unset statement set: {sorted(unset)}")
    for needed in ("cand-11474", "cand-0394", "cand-4288", "cand-4229", "cand-0544", "cand-2293", "cand-1516"):
        if needed not in candidate_ids:
            raise SystemExit(f"required existing candidate missing: {needed}")

    false_decisions = {
        "st-chp2-seci-l82-93-collection-representation": "The source names broad artist and school categories but no individual works. Preserve those entities as mentions; do not turn the collection profile into unsupported item edges.",
        "st-chp2-seci-l82-93-collection-taste": "This is Haskell’s evaluative description of the collection, not a relation claim.",
        "st-chp2-seci-l82-93-del-monte-age": "Age in 1617 is a personal temporal attribute, not a relation between entities.",
        "st-chp2-seci-l82-93-del-monte-character": "“Corrupt and sophisticated” is Haskell’s authorial characterization, not a relation claim.",
        "st-chp2-seci-l82-93-del-monte-quote-fragment": "This is an incomplete reported description with no identified speaker or entity endpoint; preserve the quote fragment without turning it into a formal relation candidate.",
        "st-chp2-seci-l82-93-guercino-modification": "This is a qualified stylistic assessment of Guercino, not a relation to an identified work or agent; the source does not name either endpoint.",
        "st-chp2-seci-l82-93-roman-fortune-pattern": "This is Haskell’s generalization about Roman changes of fortune, not a specific event or relation between identifiable entities.",
    }
    for statement_id, note in false_decisions.items():
        statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = False
        statement_by_id[statement_id]["qualifiers"]["relation_candidate_note"] = note

    # Point collection claims to the collection candidate rather than the person-index subentry.
    collection_ids = ["st-chp2-seci-l82-93-collection-representation", "st-chp2-seci-l82-93-collection-taste"]
    for statement_id in collection_ids:
        statement_by_id[statement_id]["subject_candidate_id"] = "cand-11474"
    statement_by_id["st-chp2-seci-l82-93-collection-representation"]["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-11474", "cand-4288", "cand-4229", "cand-0544", "cand-2293", "cand-1516"
    ]

    # Preserve source-level transitions and relationships while leaving unnamed endpoints open.
    policy = statement_by_id["st-chp2-seci-l82-93-borghese-policy-shift"]
    policy["predicate"] = "replaced_by_reported"
    policy["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly describes a definite policy replacing the cheerful chaos of Borghese patronage; retain this authorial transition without assigning the policy to one person.",
        "open_endpoint_reason": "The new policy is not named as a distinct entity or attributed to a single agent in this sentence.",
        "mentioned_candidate_ids": ["cand-4293"],
    })

    reaction = statement_by_id["st-chp2-seci-l82-93-classic-reaction"]
    reaction.update({"subject_candidate_id": None, "object_candidate_id": "cand-4301", "predicate": "followed_by_reported"})
    reaction["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell places the classical reaction after the preceding twenty years of wide tolerance; preserve the reported sequence as periodization.",
        "open_endpoint_reason": "The earlier period of wide tolerance is described but not separately identified as an entity.",
        "mentioned_candidate_ids": ["cand-4301"],
    })

    # Preserve the direct collective desertion while leaving anonymous actors open.
    desertion = statement_by_id["st-chp2-seci-l82-93-court-desertion"]
    desertion.update({"predicate": "deserted_by_reported", "subject_candidate_id": None, "object_candidate_id": "cand-0394"})
    desertion["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly says the collective groups that attended Scipione’s banquets and halls deserted him after the succession; this records a group-level event, not individual relations.",
        "open_endpoint_reason": "The cardinals, artists, retainers, and sycophants are not individually identified; no membership or count is supplied.",
        "mentioned_candidate_ids": ["cand-0394"],
    })
    encouraged = statement_by_id["st-chp2-seci-l82-93-domenichino-encouraged"]
    encouraged["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "The source directly reports that Domenichino received encouragement during the new policy period; the agent is not named in this sentence.",
        "open_endpoint_reason": "The person or institution providing the encouragement is not explicitly identified; do not infer Agucchi, the Pope, or Ludovico as sole agent.",
        "mentioned_candidate_ids": ["cand-0932"],
    })

    lifestyle = statement_by_id["st-chp2-seci-l82-93-lifestyle-cultural-impact"]
    lifestyle["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly interprets Scipione’s way of life and carefree patronage as helping bring about a new era; retain this as the author’s historical influence claim.",
        "open_endpoint_reason": "The resulting ‘new era’ is not identified more specifically in this statement.",
        "mentioned_candidate_ids": ["cand-0394", "cand-4293"],
    })

    impact = statement_by_id["st-chp2-seci-l82-93-long-term-impact"]
    impact["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly attributes an important long-term impact to the classical reaction despite few immediate results; preserve the authorial historical assessment.",
        "open_endpoint_reason": "The later field or entities affected by this long-term impact are not specified here.",
        "mentioned_candidate_ids": ["cand-4301"],
    })

    other_patrons = statement_by_id["st-chp2-seci-l82-93-other-patrons"]
    other_patrons.update({"subject_candidate_id": None, "object_candidate_id": "cand-3126", "predicate": "active_and_influential_in_reported"})
    other_patrons["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell states that patrons beyond popes and their nephews were active and influential in Rome; preserve the unnamed collective without inferring its members.",
        "open_endpoint_reason": "The other patrons are not individually identified in this transition.",
        "mentioned_candidate_ids": ["cand-3126"],
    })

    referenced = set()
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row["qualifiers"].get("mentioned_candidate_ids", []))
    missing = sorted(referenced - candidate_ids)
    if missing:
        raise SystemExit(f"missing p.28 candidate foreign keys: {missing}")
    remaining = [row["statement_id"] for row in statements if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None]
    if remaining:
        raise SystemExit(f"p.28 segment still has unset values: {remaining}")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.28 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up classified all fourteen previously unset relation_candidate fields. The two collection claims now point to the source-defined collection candidate cand-11474; "
        "the aggregate contents profile remains non-relational, with the artist and school categories preserved as mentions. Policy replacement, period sequence, collective court desertion, "
        "Domenichino’s encouragement, Scipione’s interpreted influence, the classical reaction’s long-term impact, and unnamed patrons active in Rome remain relation candidates with explicit open endpoints. "
        "Age, authorial characterizations, Guercino’s stylistic assessment, and the generalization about Roman fortunes are non-relational."
    )

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    summary = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2.pdf print p.28 / normalized S0 L82-93",
        "classified_unset_ids": sorted(UNSET),
        "collection_subject_remap": {sid: "cand-11474" for sid in collection_ids},
        "open_relation_candidates": [
            policy["statement_id"], reaction["statement_id"], desertion["statement_id"], encouraged["statement_id"],
            lifestyle["statement_id"], impact["statement_id"], other_patrons["statement_id"],
        ],
        "segment_unset_count": 0,
        "source_unchanged": True,
        "coverage_disposition": coverage_rows[0]["disposition"],
        "coverage_migration_status": coverage_rows[0]["migration_status"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
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
            temp = path.with_name(path.name + ".tmp-s2-chp2-p28")
            if temp.exists():
                raise SystemExit(f"stale temp file exists; refusing overwrite: {temp.name}")
            if name.endswith(".jsonl"):
                write_jsonl(temp, rows)
            else:
                write_csv(temp, rows)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
    except Exception:
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        raise
    summary["backups"] = {name: path.name for name, path in backups.items()}
    summary["post_hashes"] = {name: digest(paths[name]) for name in updated}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
