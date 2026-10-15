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
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp1-sec-i-l26-33-20261010"
SEGMENT_ID = "chp-1:01_CHP-1_sec_i:l26-33"
TARGET_ID = "st-chp1-l117-124-church-types"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "105f627f6c25a73e8385ec8393b2832ef98ba265921146923f391feabd772a09",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02-sources/02-Markdown/01_CHP-1_sec_i.md": "fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40",
    "02-sources/02-Markdown/01_CHP-1.md": "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_rows() -> list[dict]:
    return [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def relation_flag(row: dict):
    return row.get("qualifiers", {}).get("relation_candidate")


def bilateral(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    return {
        "statements": len(rows),
        "relation_true": sum(relation_flag(row) is True for row in rows),
        "relation_false": sum(relation_flag(row) is False for row in rows),
        "true_bilateral": sum(relation_flag(row) is True and bilateral(row) for row in rows),
        "true_open": sum(relation_flag(row) is True and not bilateral(row) for row in rows),
        "false_bilateral": sum(relation_flag(row) is False and bilateral(row) for row in rows),
        "unclassified_bilateral": sum(bilateral(row) and relation_flag(row) is None for row in rows),
    }


def preflight() -> dict:
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.exists() and sha256(path) == expected, f"input hash changed: {relative}")

    candidates = {
        row["candidate_id"]: row
        for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
    }
    for candidate_id in ("cand-3131", "cand-3132"):
        require(candidate_id in candidates, f"missing endpoint candidate {candidate_id}")
        require(candidates[candidate_id]["suggested_type"] == "place", f"unexpected type for {candidate_id}")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    rows = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    require(len(rows) == 1 and rows[0].get("disposition") == "reviewed"
            and rows[0].get("migration_status") == "complete", "coverage is not reviewed/complete")

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    mention_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    require({"cand-3131", "cand-3132"} <= mention_candidates, "one or both church endpoints lack a segment mention")

    source = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8").splitlines()
    require("ancient and venerable of basilicas such as S. Maria Maggiore and S. Maria sopra" in source[122],
            "the two basilica examples changed")
    require(source[123].strip() == "Minerva.", "the final basilica name changed")

    all_rows = load_rows()
    by_id = {row.get("statement_id"): row for row in all_rows}
    require(len(by_id) == len(all_rows), "statement IDs are not unique")
    require(TARGET_ID in by_id, "target statement is missing")
    require(counts(all_rows) == {
        "statements": 12692,
        "relation_true": 3874,
        "relation_false": 1796,
        "true_bilateral": 3847,
        "true_open": 27,
        "false_bilateral": 431,
        "unclassified_bilateral": 4211,
    }, "current statement totals changed")

    row = by_id[TARGET_ID]
    q = row.get("qualifiers", {})
    require(row.get("segment_id") == SEGMENT_ID, "segment changed")
    require(row.get("subject_candidate_id") == "cand-3131"
            and row.get("object_candidate_id") == "cand-3132", "endpoint mapping changed")
    require(row.get("predicate") == "church_use_and_antiquity", "predicate changed")
    require(q.get("source_line_start") == 117 and q.get("source_line_end") == 124, "source anchors changed")
    require(relation_flag(row) is None, "target statement is already classified")
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify one first chapter church statement with source-hash preflight.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classification")
    args = parser.parse_args()
    selected = preflight()
    rows = load_rows()
    updated = [dict(row) for row in rows]
    row = next(item for item in updated if item.get("statement_id") == TARGET_ID)
    row["qualifiers"] = dict(row.get("qualifiers", {}))
    row["qualifiers"]["relation_candidate"] = False
    row["qualifiers"]["relation_candidate_note"] = (
        "The two endpoints are Santa Maria Maggiore and Santa Maria sopra Minerva, listed as examples of ancient "
        "basilicas chosen for burial. The passage assigns them a shared function and quality; it does not state "
        "a relation between the two churches themselves. Preserve the authorial generalization without creating a pairwise edge."
    )
    print(f"PREVIEW: {TARGET_ID} -> relation_candidate=false")
    print("  endpoints are co-listed examples, not a relation between the churches")
    print("  counts before:", json.dumps(counts(rows), sort_keys=True))
    print("  counts after: ", json.dumps(counts(updated), sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the classification.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP)
    payload = "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in updated) + "\n"
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
