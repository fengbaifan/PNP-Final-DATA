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
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp1-sec-i-l15-24-20261010"
SEGMENT_ID = "chp-1:01_CHP-1_sec_i:l15-24"
NEW_ID = "st-chp1-l81-compatriot-domenichino-gregory"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "fa33f485df608935cc7db930bf5c5cfa27a39be12421895fd452e1ae71aa1110",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02-sources/02-Markdown/01_CHP-1_sec_i.md": "fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40",
    "02-sources/02-Markdown/01_CHP-1.md": "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}

TARGETS = {
    "st-chp1-l68-70-peretti-exception": ("cand-2992", "cand-3102", "continued_patronage_after_death", 68, 70),
    "st-chp1-l75-76-maffeo-florence": ("cand-3104", "cand-3397", "attributed_city_affiliation", 75, 76),
    "st-chp1-l77-78-gregory-bologna": ("cand-3061", "cand-3398", "attributed_city_affiliation", 77, 78),
    "st-chp1-l79-82-domenichino-return": ("cand-3024", "cand-3061", "reported_return_after_election", 79, 82),
    "st-chp1-l82-83-ludovico-appointment": ("cand-3024", "cand-3073", "appointed_to_office_by", 82, 83),
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
        "false_bilateral": sum(flag(row) is False and bilateral(row) for row in rows),
        "unclassified_bilateral": sum(bilateral(row) and flag(row) is None for row in rows),
    }


def preflight() -> list[dict]:
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.exists(), f"missing input {relative}")
        require(sha256(path) == expected, f"SHA-256 changed for {relative}")

    expected_types = {
        "cand-2992": "person",
        "cand-3102": "person",
        "cand-3104": "person",
        "cand-3397": "place",
        "cand-3061": "person",
        "cand-3398": "place",
        "cand-3024": "person",
        "cand-3073": "person",
    }
    candidates = {
        row["candidate_id"]: row
        for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
    }
    for candidate_id, expected_type in expected_types.items():
        require(candidate_id in candidates, f"missing candidate {candidate_id}")
        require(candidates[candidate_id]["suggested_type"] == expected_type,
                f"unexpected candidate type for {candidate_id}")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    matching = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    require(len(matching) == 1, "target coverage row must be unique")
    require(matching[0].get("disposition") == "reviewed"
            and matching[0].get("migration_status") == "complete",
            "target segment must be reviewed/complete")

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    mentioned_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    require(set(expected_types) <= mentioned_candidates, "one or more endpoint candidates lack a segment mention")

    source_lines = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8").splitlines()
    require("Cardinal Alessandro Peretti-Montalto" in source_lines[67], "Peretti source anchor changed")
    require("native Florence" in source_lines[75], "Maffeo source anchor changed")
    require("was a Bolognese" in source_lines[76], "Gregory XV source anchor changed")
    require("compatriot of his" in source_lines[80], "compatriot source anchor changed")
    require("Vatican architect" in source_lines[81] and "Ludovico" in source_lines[82],
            "appointment source anchor changed")

    rows = load_jsonl(STATEMENTS)
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(NEW_ID not in by_id, f"new statement already exists: {NEW_ID}")
    require(set(TARGETS) <= set(by_id), "one or more target statement IDs are missing")
    require(counts(rows) == {
        "statements": 12691,
        "relation_true": 3870,
        "relation_false": 1794,
        "true_bilateral": 3843,
        "true_open": 27,
        "false_bilateral": 429,
        "unclassified_bilateral": 4216,
    }, "current statement totals changed")

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
    decisions = {
        "st-chp1-l68-70-peretti-exception": (False,
            "The endpoints are Peretti and Sixtus V. Sixtus V supplies the temporal context of his death; the sentence's separate claim that unnamed artists continued to work for Peretti does not establish a direct relation between these two endpoints."),
        "st-chp1-l75-76-maffeo-florence": (True,
            "The quoted report explicitly identifies Florence as Maffeo Barberini's native city and says he favored artists from there. Keep the statement attributed to the biographical report; this is not independent verification."),
        "st-chp1-l77-78-gregory-bologna": (True,
            "The quoted report explicitly describes Gregory XV as Bolognese. The person-to-place city affiliation is stated directly, with the source attribution retained."),
        "st-chp1-l79-82-domenichino-return": (False,
            "This statement records Domenichino's return to Rome after Gregory XV's election. The person endpoint supplies the event's temporal trigger, not a direct person-to-person relation; the quoted compatriot claim is recorded separately."),
        "st-chp1-l82-83-ludovico-appointment": (True,
            "The source directly says Domenichino was made Vatican architect by Ludovico. The statement records an attributed appointment relation with its stated role."),
    }
    updated = [dict(row) for row in rows]
    for row in updated:
        sid = row.get("statement_id")
        if sid in decisions:
            value, note = decisions[sid]
            row["qualifiers"] = dict(row.get("qualifiers", {}))
            row["qualifiers"]["relation_candidate"] = value
            row["qualifiers"]["relation_candidate_note"] = note

    new_statement = {
        "statement_id": NEW_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-3024",
        "object_candidate_id": "cand-3061",
        "predicate": "compatriot_of",
        "qualifiers": {
            "source_line_start": 81,
            "source_line_end": 81,
            "claim": "The cited biographical account describes Gregory XV as a compatriot of Domenichino.",
            "speaker": "Haskell, reporting a cited biographical account",
            "text_layer": "reported quotation",
            "qualification": "The source attribution is preserved; the cited biographical account has not been independently checked.",
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly calls Gregory XV Domenichino's compatriot. This is a direct person-to-person relation, separate from the subsequent return-to-Rome timeline.",
        },
        "original_quote": "as the new Pope was a compatriot of his",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/01_CHP-1.md",
    }
    insert_after = next(i for i, row in enumerate(updated) if row.get("statement_id") == "st-chp1-l79-82-domenichino-return")
    updated.insert(insert_after + 1, new_statement)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify first chapter section i statements L15-24 with source-hash preflight.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classifications")
    args = parser.parse_args()

    selected = preflight()
    original = load_jsonl(STATEMENTS)
    updated = classify(original)
    print("PREVIEW: chp-1:01_CHP-1_sec_i:l15-24")
    for row in selected:
        print(f"  {row['statement_id']}: {row['predicate']} -> relation_candidate={row['qualifiers'].get('relation_candidate')}")
    print(f"  added explicit relation statement: {NEW_ID} (compatriot_of)")
    print("  no candidate or mention changes; return-to-Rome claim retained separately")
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
