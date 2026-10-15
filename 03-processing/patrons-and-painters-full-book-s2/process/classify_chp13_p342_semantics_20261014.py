from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEGMENT_ID = "chp-13:13_CHP-13_intro:l98-105"
SOURCE = ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md"
PDF = ROOT / "02-sources/01-book/CHP-13.pdf"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
BACKUP = STATEMENTS.with_name(
    "book-statements.jsonl.bak-s2-ch13-p342-semantic-review-20261014"
)

EXPECTED = {
    SOURCE: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
    STATEMENTS: "5394324ccf0d9b55059ec73d17adaf63c2cf1fca5074dad1be256d2501589c0f",
    CANDIDATES: "36ac91154bdd308d1f990c643b9d211649e343ee279ab6970ccb09e945503fe3",
    MENTIONS: "cbac853854d77cdb22e3aa5373ea5c97c07b1463a1a9d7ed304458e34574beb4",
}

DECISIONS = {
    "st-chp13-p342-no_evidence_zanetti_bought_modern_french_or_english_works": (
        False,
        "This reports an absence of evidence, not a confirmed purchase or non-purchase relation.",
    ),
    "st-chp13-p342-swedish_king_refused_tiepolo_sum": (
        True,
        "The reported refusal directly concerns the proposed recruitment of Tiepolo; retain the unidentified monarch and Haskell/Tessin attribution.",
    ),
    "st-chp13-p342-tessin_assessed_gai_as_half_michelangelo": (
        True,
        "This is Tessin's explicit attributed assessment of Gai, not an objective ranking.",
    ),
    "st-chp13-p342-young_protege_died": (
        False,
        "This is a unary biographical event about the unnamed protégé, with no second entity endpoint.",
    ),
    "st-chp13-p342-zanetti_1752_described_print_collection": (
        True,
        "The 1752 quotation explicitly describes Zanetti's print collection.",
    ),
    "st-chp13-p342-zanetti_1752_rare_print_exception_fragment": (
        True,
        "The quotation explicitly singles out the described Bacchanal dish as an exception; preserve the source wording without inferring ownership or why it was excepted.",
    ),
    "st-chp13-p342-zanetti_collections_limited_contemporary_art_outside_venice": (
        False,
        "This is Haskell's qualitative characterization of the collection's scope, without a distinct mapped object relation.",
    ),
    "st-chp13-p342-zanetti_was_proud_of_print_collection": (
        True,
        "The sentence directly attributes Zanetti's pride to the identified print collection.",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all prechecks pass")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"precheck failed: {path.relative_to(ROOT)} sha256={actual}")

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()]
    segment = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment) != 1 or segment[0].get("sha256") != "784beac28408e154b50a6afebd080e5c3de774cd0bd6bc8093bfbee712c4c0a0":
        raise SystemExit("precheck failed: segment row/hash mismatch")

    raw = STATEMENTS.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    had_final_newline = raw.endswith(("\n", "\r"))
    lines = raw.splitlines()
    parsed = [json.loads(line) for line in lines]
    targets = {
        row.get("statement_id"): row
        for row in parsed
        if row.get("segment_id") == SEGMENT_ID
    }
    if len(targets) != 27:
        raise SystemExit(f"precheck failed: expected 27 segment statements, found {len(targets)}")
    unset = {
        sid for sid, row in targets.items()
        if row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(DECISIONS):
        raise SystemExit(f"precheck failed: expected exact unset ID set; got {sorted(unset)}")
    if any(targets[sid].get("qualifiers", {}).get("relation_candidate") is not None for sid in DECISIONS):
        raise SystemExit("precheck failed: one or more target statements is no longer unset")

    print(f"segment={SEGMENT_ID} statements=27 unset={len(DECISIONS)}")
    for sid, (decision, reason) in DECISIONS.items():
        print(f"{sid}: relation_candidate={str(decision).lower()} | {reason}")
    if not args.apply:
        print("dry-run: no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"refusing to overwrite existing recovery copy: {BACKUP.name}")

    shutil.copy2(STATEMENTS, BACKUP)
    for index, row in enumerate(parsed):
        sid = row.get("statement_id")
        if sid in DECISIONS:
            row.setdefault("qualifiers", {})["relation_candidate"] = DECISIONS[sid][0]
            lines[index] = json.dumps(row, ensure_ascii=False, separators=(",", ":"))
    output = newline.join(lines) + (newline if had_final_newline else "")
    STATEMENTS.write_bytes(output.encode("utf-8"))

    after = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines()]
    after_rows = {row.get("statement_id"): row for row in after}
    if any(after_rows[sid].get("qualifiers", {}).get("relation_candidate") is not decision for sid, (decision, _) in DECISIONS.items()):
        shutil.copy2(BACKUP, STATEMENTS)
        raise SystemExit("postcheck failed; restored statements from recovery copy")
    print(f"applied; backup={BACKUP.name}; statements_sha256={sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
