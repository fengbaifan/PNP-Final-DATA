from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch16-p373-residual-20261015")
EXPECTED_SHA256 = "5e2545465391a256a8ffcf5344d59d9c4f43348c3fbd388f5fd5a9a841158ada"
SEGMENT = "chp-16:16_CHP-16_intro:l3-14"


DECISIONS = {
    "st-chp16-p373-prominent-patrons-influenced-by-lodoli-algarotti": (
        False,
        "This is Haskell's broad retrospective framing of unnamed patrons and unspecified new ideas; Lodoli and Algarotti are named as channels, but no bounded patron-to-idea relation is identified.",
        None,
    ),
    "st-chp16-p373-dealers-perceived-as-agents-and-collectors": (
        False,
        "The claim reports how unnamed lower-status men were perceived, not a documented agency or transaction between identified dealers and foreign embassies.",
        None,
    ),
    "st-chp16-p373-sasso-survived-the-republic": (
        False,
        "This is a chronological biographical statement. It does not identify a distinct survival event or state the Republic's end date.",
        None,
    ),
    "st-chp16-p373-sasso-born-to-poor-parents": (
        False,
        "This is a biographical description; the parents are unnamed and the approximate wording does not support a separately identified family relation.",
        None,
    ),
    "st-chp16-p373-patrons-promoted-functional-or-classical-taste": (
        False,
        "This is an unbounded authorial characterization of a broad patron cohort and alternative taste tendencies, not a relation between independently identified objects.",
        None,
    ),
    "st-chp16-p373-patron-taste-distinct-from-venetian-tradition": (
        False,
        "The sentence is Haskell's comparative evaluation of an unnamed cohort's taste against the Venetian art tradition; it does not identify the taste as a distinct source-level concept.",
        None,
    ),
    "st-chp16-p373-venetian-tradition-carried-by-lower-status-men": (
        True,
        "The text explicitly says that men of lower social position carried on the source-defined Venetian art tradition; retain the unnamed cohort as an open endpoint.",
        "Haskell does not name or enumerate the men who carried on this tradition; the existing Venetian art tradition candidate is cand-11543.",
    ),
    "st-chp16-p373-lower-status-men-and-their-painting-attracted-little-attention": (
        False,
        "This is Haskell's reception and visibility assessment of an unnamed cohort and painting type, not a direct relation between identified entities.",
        None,
    ),
    "st-chp16-p373-dealers-built-small-collections": (
        True,
        "The sentence directly links the source-defined dealers' activity to building private collections; preserve it as a group-level relation without inventing members or inventories.",
        "Neither the dealers nor their separate collections are named, enumerated, or individually bounded in this general statement.",
    ),
    "st-chp16-p373-collections-reflect-distinctive-taste-and-appeal": (
        True,
        "The source directly relates these private collections to a distinctive taste; the possible present-day appeal and comparison with named patrons remain Haskell's evaluation.",
        "The collections and the taste are not individually identified; Farsetti, Memmo, and Querini are comparative references, not endpoints for these collections.",
    ),
    "st-chp16-p373-sasso-bought-and-sold-pictures": (
        True,
        "The passage directly reports Sasso's picture-trading activity; retain the market relation without assigning any unnamed picture or transaction.",
        "No individual picture, seller, buyer, or transaction is identified in this clause.",
    ),
    "st-chp16-p373-sasso-dealt-with-british-agents": (
        True,
        "The passage directly connects Sasso with British agents and describes their alternating conduct toward him; keep the agents unnamed and the account attributed to Haskell.",
        "The British agents are not named or enumerated in this passage.",
    ),
    "st-chp16-p373-sasso-corresponded-with-friends-and-dealers": (
        True,
        "The text directly reports Sasso's extended correspondence with friends and other dealers; preserve the relation without guessing correspondents from other notes.",
        "The friends and other dealers in this sentence are not individually identified.",
    ),
    "st-chp16-p373-sasso-produced-occasional-pamphlets": (
        True,
        "The passage attributes occasional pamphlet production to Sasso; retain the creator-to-publication claim while leaving the works unidentified.",
        "No pamphlet title, date, or surviving copy is identified in this sentence.",
    ),
    "st-chp16-p373-sasso-amassed-facts": (
        False,
        "This is a general biographical characterization of collecting information; no defined body of records, subject, or relation endpoint is identified.",
        None,
    ),
    "st-chp16-p373-sasso-planned-unfinished-book-on-venetian-painting": (
        True,
        "The source explicitly connects Sasso to a planned but unfinished book, represented by the source-level work candidate cand-11544; no title or surviving manuscript is claimed.",
        None,
    ),
    "st-chp16-p373-sasso-life-typical-of-contemporary-figures": (
        False,
        "This is Haskell's unmeasured typological generalization about Sasso's life, not a relation to individually identified contemporary figures.",
        None,
    ),
    "st-chp16-p373-sasso-died-in-1803": (
        False,
        "The year is a biographical date attribute, not a relation candidate; the separate phrase about surviving the Republic does not establish its end date.",
        None,
    ),
    "st-chp16-p373-sasso-studied-painting-briefly": (
        False,
        "This is a brief biographical education detail; no teacher, school, or distinct study event is identified.",
        None,
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_and_validate() -> tuple[list[str], list[dict], str]:
    current_hash = sha256(TABLE)
    if current_hash != EXPECTED_SHA256:
        raise SystemExit(f"table hash mismatch: expected {EXPECTED_SHA256}, got {current_hash}")
    lines = TABLE.read_text(encoding="utf-8").splitlines(keepends=True)
    rows = [json.loads(line) for line in lines]
    selected = {row["statement_id"]: row for row in rows if row["statement_id"] in DECISIONS}
    if set(selected) != set(DECISIONS):
        raise SystemExit(f"statement set mismatch: missing={sorted(set(DECISIONS)-set(selected))}, extra={sorted(set(selected)-set(DECISIONS))}")
    for statement_id, row in selected.items():
        if row["segment_id"] != SEGMENT:
            raise SystemExit(f"wrong segment for {statement_id}: {row['segment_id']}")
        if row["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"statement is no longer unset: {statement_id}")
    return lines, rows, current_hash


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    lines, rows, before_hash = load_and_validate()
    counts = Counter(decision[0] for decision in DECISIONS.values())
    print(f"segment={SEGMENT} pending={len(DECISIONS)} classify_true={counts[True]} classify_false={counts[False]}")
    for statement_id, (value, note, open_reason) in DECISIONS.items():
        print(f"{statement_id}: {str(value).lower()} | {note}")
        if open_reason:
            print(f"  open_endpoint_reason: {open_reason}")
    print(f"before_sha256={before_hash}")
    if args.preview:
        print("preview only; no table or backup written")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    changed_lines: list[str] = []
    seen: set[str] = set()
    for line in lines:
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id not in DECISIONS:
            changed_lines.append(line)
            continue
        value, note, open_reason = DECISIONS[statement_id]
        qualifiers = row["qualifiers"]
        qualifiers["relation_candidate"] = value
        qualifiers["relation_candidate_note"] = note
        if open_reason:
            qualifiers["open_endpoint_reason"] = open_reason
        elif qualifiers.get("open_endpoint_reason"):
            qualifiers.pop("open_endpoint_reason")
        changed_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        seen.add(statement_id)
    if seen != set(DECISIONS):
        raise SystemExit(f"write set mismatch: {sorted(set(DECISIONS)-seen)}")
    if sha256(TABLE) != before_hash:
        raise SystemExit("table changed after validation")

    shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        stream.writelines(changed_lines)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp_path, TABLE)
    print(f"backup={BACKUP}")
    print(f"after_sha256={sha256(TABLE)}")
    print("applied 19 classifications; unrelated statement lines preserved byte-for-byte")


if __name__ == "__main__":
    main()
