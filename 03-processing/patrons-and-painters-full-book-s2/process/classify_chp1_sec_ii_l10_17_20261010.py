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
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp1-sec-ii-l10-17-20261010"
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l10-17"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "72b580eea9b6c1cf98a4f48fb2065fd957e1d143624a5cca9217795d59c75aa5",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    "02-sources/02-Markdown/01_CHP-1.md": "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}

TARGETS = {
    "st-chp1-secii-l10-17-01": ("cand-2998", "cand-3001", "household_promotion", 195, 198),
    "st-chp1-secii-l10-17-06": ("cand-3044", "cand-3053", "attributed_advice", 209, 210),
    "st-chp1-secii-l10-17-09": ("cand-3074", "cand-3096", "compatriot_patronage_anecdote", 217, 219),
    "st-chp1-secii-l10-17-10": ("cand-3098", "cand-3038", "compatriot_hospitality", 220, 221),
}

DECISIONS = {
    "st-chp1-secii-l10-17-01": (True,
        "The source says Andrea Sacchi entered Cardinal Antonio Barberini's household and was later promoted among its pensioners. This is a direct household-service and promotion relation; retain the distinct dates and role scope."),
    "st-chp1-secii-l10-17-06": (False,
        "Passeri's quotation gives general advice that a painter should seek a patron's protection. Passeri and the generic patron are not participants in a specific relation; retain this as attributed advice."),
    "st-chp1-secii-l10-17-09": (True,
        "Haskell reports that Marcello Sacchetti called Pietro da Cortona a compatriot and housed him in his palace. The person endpoints are directly connected; preserve the reported-source qualification."),
    "st-chp1-secii-l10-17-10": (True,
        "The author directly reports that Cardinal Ottoboni provided rooms for Francesco Trevisani, his Venetian fellow-citizen. Preserve the attributed hospitality relation without adding motive."),
}


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


def preflight() -> list[dict]:
    for relative, expected in EXPECTED_HASHES.items():
        if not expected:
            continue
        path = ROOT / relative
        require(path.exists() and sha256(path) == expected, f"input hash changed: {relative}")

    expected_types = {
        "cand-2998": "person", "cand-3001": "person", "cand-3044": "person", "cand-3053": "person",
        "cand-3074": "person", "cand-3096": "person", "cand-3098": "person", "cand-3038": "person",
    }
    candidates = {
        row["candidate_id"]: row
        for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
    }
    for candidate_id, expected_type in expected_types.items():
        require(candidate_id in candidates, f"missing candidate {candidate_id}")
        require(candidates[candidate_id]["suggested_type"] == expected_type,
                f"unexpected type for {candidate_id}")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    matching = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    require(len(matching) == 1 and matching[0].get("disposition") == "reviewed"
            and matching[0].get("migration_status") == "complete", "coverage must be reviewed/complete")

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    segment_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    require(set(expected_types) <= segment_candidates, "an endpoint candidate lacks a segment mention")

    source = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8").splitlines()
    for line_number, phrase in {
        195: "Andrea Sacchi was placed",
        196: "Cardinal Antonio Barberini",
        209: "To establish one’s name it is",
        217: "Marcello Sacchetti who",
        219: "he called him his compatriot",
        220: "Cardinal Ottoboni provided",
        221: "rooms for his Venetian fellow-citizen Francesco Trevisani",
    }.items():
        require(phrase in source[line_number - 1], f"source anchor changed at line {line_number}")

    rows = load_jsonl()
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(set(TARGETS) <= set(by_id), "one or more target statements are missing")
    require(counts(rows) == {
        "statements": 12692, "relation_true": 3878, "relation_false": 1800,
        "true_bilateral": 3851, "true_open": 27, "false_bilateral": 435,
        "unclassified_bilateral": 4203,
    }, "current statement totals changed")

    selected = []
    for statement_id, (subject, object_, predicate, start, end) in TARGETS.items():
        row = by_id[statement_id]
        q = row.get("qualifiers", {})
        require(row.get("segment_id") == SEGMENT_ID, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_,
                f"endpoints changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(q.get("source_line_start") == start and q.get("source_line_end") == end,
                f"source anchor changed for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        selected.append(row)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify first chapter section ii statements L10-17 with source-hash preflight.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classifications")
    args = parser.parse_args()
    selected = preflight()
    rows = load_jsonl()
    updated = [dict(row) for row in rows]
    for row in updated:
        sid = row.get("statement_id")
        if sid in DECISIONS:
            value, note = DECISIONS[sid]
            row["qualifiers"] = dict(row.get("qualifiers", {}))
            row["qualifiers"]["relation_candidate"] = value
            row["qualifiers"]["relation_candidate_note"] = note

    print("PREVIEW: chp-1:01_CHP-1_sec_ii:l10-17")
    for row in selected:
        print(f"  {row['statement_id']}: {row['predicate']} -> relation_candidate={DECISIONS[row['statement_id']][0]}")
    print("  no endpoint, predicate, source quote, candidate, mention or statement-count changes")
    print("  counts before:", json.dumps(counts(rows), sort_keys=True))
    print("  counts after: ", json.dumps(counts(updated), sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the classifications.")
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
