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
STATEMENTS = TABLES / "book-statements.jsonl"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp1-sec-ii-l118-127-20261010"
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l118-127"
STATEMENT_ID = "st-chp1-secii-l118-127-05"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "2b1152f4604d20ad4b99dcd418fe67baf435c6e1878f5e8a6affc87713d0f311",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    "02-sources/02-Markdown/01_CHP-1.md": "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}

EXPECTED = {
    "subject_candidate_id": "cand-3470",
    "object_candidate_id": "cand-3582",
    "predicate": "brief_financial_benefit_and_academicians_status_concern",
    "source_line_start": 720,
    "source_line_end": 722,
}

DECISION = True
NOTE = (
    "Haskell places the financial benefits from Urban VIII's brief within the account of the Accademia's "
    "tax and public-commission measures, and separately reads the Academicians' complaints as expressing "
    "concern about social status. Preserve this as a source-attributed relation candidate; the brief's "
    "identity, date, beneficiary wording, and precise legal scope remain unresolved."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_jsonl() -> list[dict]:
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def flag(row: dict):
    return row.get("qualifiers", {}).get("relation_candidate")


def bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    return {
        "statements": len(rows),
        "relation_true": sum(flag(row) is True for row in rows),
        "relation_false": sum(flag(row) is False for row in rows),
        "true_bilateral": sum(flag(row) is True and bilateral(row) for row in rows),
        "true_open": sum(flag(row) is True and not bilateral(row) for row in rows),
        "false_bilateral": sum(flag(row) is False and bilateral(row) for row in rows),
        "unclassified_bilateral": sum(bilateral(row) and flag(row) is None for row in rows),
    }


def preflight() -> tuple[list[dict], dict]:
    for relative, expected_hash in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing input: {relative}")
        require(sha256(path) == expected_hash, f"input hash changed: {relative}")

    rows = load_jsonl()
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(STATEMENT_ID in by_id, "target statement is missing")
    row = by_id[STATEMENT_ID]
    require(row.get("segment_id") == SEGMENT_ID, "segment changed")
    require(row.get("subject_candidate_id") == EXPECTED["subject_candidate_id"], "subject endpoint changed")
    require(row.get("object_candidate_id") == EXPECTED["object_candidate_id"], "object endpoint changed")
    require(row.get("predicate") == EXPECTED["predicate"], "predicate changed")
    qualifiers = row.get("qualifiers", {})
    require(qualifiers.get("source_line_start") == EXPECTED["source_line_start"], "source start changed")
    require(qualifiers.get("source_line_end") == EXPECTED["source_line_end"], "source end changed")
    require(flag(row) is None, "target statement is already classified")
    require("Urban VIII’s brief" in row.get("original_quote", ""), "quote anchor changed")
    require("Academicians showed an unresting concern" in row.get("original_quote", ""), "quote ending changed")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    matches = [item for item in coverage if item.get("segment_id") == SEGMENT_ID]
    require(len(matches) == 1 and matches[0].get("disposition") == "reviewed"
            and matches[0].get("migration_status") == "complete", "coverage is not reviewed/complete")

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    segment_candidates = {item.get("candidate_id") for item in mentions if item.get("segment_id") == SEGMENT_ID}
    require({EXPECTED["subject_candidate_id"], EXPECTED["object_candidate_id"]} <= segment_candidates,
            "an endpoint candidate lacks a segment mention")

    source = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8").splitlines()
    require("apart from the financial benefits that accrued from Urban VIII’s brief" in source[719],
            "source line 720 anchor changed")
    require("the Academicians showed an unresting" in source[720], "source line 721 anchor changed")
    require("concern for their own social status." in source[721], "source line 722 anchor changed")

    before = counts(rows)
    require(before == {
        "statements": 12692,
        "relation_true": 3881,
        "relation_false": 1801,
        "true_bilateral": 3854,
        "true_open": 27,
        "false_bilateral": 436,
        "unclassified_bilateral": 4199,
    }, "current statement totals changed")
    return rows, before


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify the remaining bilateral statement in chapter 1 section ii L118-127.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classification")
    args = parser.parse_args()

    rows, before = preflight()
    updated = [dict(row) for row in rows]
    target = next(row for row in updated if row.get("statement_id") == STATEMENT_ID)
    target["qualifiers"] = dict(target.get("qualifiers", {}))
    target["qualifiers"]["relation_candidate"] = DECISION
    target["qualifiers"]["relation_candidate_note"] = NOTE
    after = counts(updated)

    print(f"PREVIEW: {SEGMENT_ID}")
    print(f"  {STATEMENT_ID}: {EXPECTED['predicate']} -> relation_candidate={DECISION}")
    print("  no endpoint, predicate, source quote, candidate, mention or statement-count changes")
    print("  counts before:", json.dumps(before, sort_keys=True))
    print("  counts after: ", json.dumps(after, sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the classification.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP)
    payload = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=STATEMENTS.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, STATEMENTS)
    print(f"APPLIED; backup: {BACKUP.relative_to(ROOT)}")
    print(f"new SHA-256: {sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
