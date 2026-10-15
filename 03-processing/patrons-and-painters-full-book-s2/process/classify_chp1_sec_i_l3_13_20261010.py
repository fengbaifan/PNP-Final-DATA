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
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp1-sec-i-l3-13-20261010"
SEGMENT_ID = "chp-1:01_CHP-1_sec_i:l3-13"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "fbad36a8f0514e3d69043c4b32c971866897948d3df46de8311b3ed6a1fa602c",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02-sources/02-Markdown/01_CHP-1_sec_i.md": "fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40",
    "02-sources/02-Markdown/01_CHP-1.md": "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}

TARGETS = {
    "st-chp1-l15-18-passeri": ("cand-3044", "cand-3104", "attributed_recollection", 15, 18),
    "st-chp1-l39-40-turnover-context": ("cand-3126", "cand-3104", "political_turnover_context", 39, 40),
    "st-chp1-l40-44-coke-testimony": ("cand-3085", "cand-3092", "attributed_testimony", 40, 44),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
        "unclassified_bilateral": sum(bilateral(row) and flag(row) is None for row in rows),
    }


def preflight() -> list[dict]:
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.exists(), f"missing input {relative}")
        require(sha256(path) == expected, f"SHA-256 changed for {relative}")

    candidates = {
        row["candidate_id"]: row
        for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
    }
    expected_types = {
        "cand-3044": "person",
        "cand-3104": "person",
        "cand-3126": "place",
        "cand-3085": "person",
        "cand-3092": "person",
        "cand-3071": "person",
        "cand-2943": "archive",
    }
    for candidate_id, expected_type in expected_types.items():
        require(candidate_id in candidates, f"missing candidate {candidate_id}")
        require(candidates[candidate_id]["suggested_type"] == expected_type,
                f"unexpected candidate type for {candidate_id}")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    matching_coverage = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    require(len(matching_coverage) == 1, "target coverage row must be unique")
    require(matching_coverage[0].get("disposition") == "reviewed"
            and matching_coverage[0].get("migration_status") == "complete",
            "target segment must be reviewed/complete")

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    mention_keys = {(row.get("segment_id"), row.get("candidate_id"), row.get("surface_form")) for row in mentions}
    required_mentions = {
        (SEGMENT_ID, "cand-3044", "Giambattista Passeri"),
        (SEGMENT_ID, "cand-3104", "Urban VIII"),
        (SEGMENT_ID, "cand-3126", "Roman"),
        (SEGMENT_ID, "cand-3071", "Lord Arundell"),
        (SEGMENT_ID, "cand-3092", "Paul V"),
        ("chp-1:01_CHP-1_intro:l11-13", "cand-3085", "Mr Coke"),
    }
    require(required_mentions <= mention_keys, "one or more source-grounded endpoint mentions changed")

    segment_text = (ROOT / "02-sources/02-Markdown/01_CHP-1_sec_i.md").read_text(encoding="utf-8").splitlines()
    master_text = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8").splitlines()
    require("WHEN Urban VIII became Pope" in segment_text[2], "Passeri quotation segment changed")
    require("For until the election of this Pope" in segment_text[11], "Roman turnover context segment changed")
    require("wrote a correspondent to" in segment_text[11] and "Lord Arundell" in segment_text[12],
            "Coke testimony segment changed")
    require("WHEN Urban. VIII became Pope" in master_text[14], "master quote anchor changed for Passeri")
    require("For until the election of this Pope" in master_text[38], "master quote anchor changed for turnover")
    require("wrote a correspondent to" in master_text[39] and "Lord Arundell" in master_text[40],
            "master quote anchor changed for Coke")

    rows = load_jsonl(STATEMENTS)
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(set(TARGETS) <= set(by_id), "one or more target statement IDs are missing")
    require(counts(rows) == {
        "statements": 12691,
        "relation_true": 3870,
        "relation_false": 1791,
        "true_bilateral": 3843,
        "true_open": 27,
        "unclassified_bilateral": 4219,
    }, "current statement classification totals changed")

    selected = []
    for statement_id, (subject, object_, predicate, start, end) in TARGETS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers", {})
        require(row.get("segment_id") == SEGMENT_ID, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_,
                f"endpoint changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(qualifiers.get("source_line_start") == start and qualifiers.get("source_line_end") == end,
                f"source anchor changed for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        selected.append(row)
    return selected


def classify(rows: list[dict]) -> list[dict]:
    reasons = {
        "st-chp1-l15-18-passeri": (
            "The statement preserves Passeri’s retrospective assessment of Urban VIII and papal patronage. "
            "Its endpoints are the quoted speaker and subject of the account, not a direct historical relation; "
            "do not turn reported speech into a person-to-person edge."
        ),
        "st-chp1-l39-40-turnover-context": (
            "The passage describes political turnover as part of Rome’s historical context before Urban VIII’s election. "
            "Rome and Urban VIII provide place and temporal context here, not a direct relation between the place and person."
        ),
        "st-chp1-l40-44-coke-testimony": (
            "Coke’s attributed letter gives a political opinion about the consequences of a prince’s long rule. "
            "Coke and Paul V are the speaker and subject of that opinion, not a direct historical relation. "
            "Keep the addressee, dated document and source attribution as evidence metadata."
        ),
    }
    updated = [dict(row) for row in rows]
    targets = {row["statement_id"] for row in updated if row.get("statement_id") in TARGETS}
    require(targets == set(TARGETS), "target set changed during apply")
    for row in updated:
        statement_id = row.get("statement_id")
        if statement_id in reasons:
            row["qualifiers"] = dict(row.get("qualifiers", {}))
            row["qualifiers"]["relation_candidate"] = False
            row["qualifiers"]["relation_candidate_note"] = reasons[statement_id]
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify first chapter section i statements L3-13 with source-hash preflight.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classification")
    args = parser.parse_args()

    selected = preflight()
    original = load_jsonl(STATEMENTS)
    updated = classify(original)
    print("PREVIEW: chp-1:01_CHP-1_sec_i:l3-13")
    for row in selected:
        print(f"  {row['statement_id']}: {row['predicate']} -> relation_candidate=false")
    print("  no candidate, mention, endpoint, predicate or statement-count changes")
    print("  counts before:", json.dumps(counts(original), sort_keys=True))
    print("  counts after: ", json.dumps(counts(updated), sort_keys=True))
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
