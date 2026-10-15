from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-i-l3-7-20261010"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l3-7"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "6c97c36779fdb14552057ebf21a90f66e8ec3bb8960f547533f4827f737593c4",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "7981656efea75e28f877a5dfd0ccd6f68785d1a0368998bcf62cd5ac5fdd31fd",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE_FILE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

DECISIONS = {
    "st-chp2-seci-l3-7-church-government": (True, "Haskell directly attributes a change in Church government to Sixtus V; preserve the author's strong characterization as a source claim."),
    "st-chp2-seci-l3-7-city-plan": (True, "The passage directly attributes Rome's redevelopment and long-term city plan to Sixtus V; retain the stated two-century scope."),
    "st-chp2-seci-l3-7-conditional-rome-effect": (True, "Haskell explicitly offers a conditional causal interpretation of Rome's effect on Maffeo. Retain 'If so' and the author's attribution; do not promote it to an independently verified fact."),
    "st-chp2-seci-l3-7-family": (True, "The source directly says Maffeo was born into this merchant family; preserve the family's unnamed status and descriptive claims as Haskell's wording."),
    "st-chp2-seci-l3-7-fontana-power": (False, "Maffeo is described as an observer and Domenico Fontana as the architect whose work he passed. The passage does not state a direct historical relation between the two people; preserve their distinct narrative roles."),
    "st-chp2-seci-l3-7-lawlessness": (True, "The passage directly attributes suppression of lawlessness in the Campagna context to Sixtus V; retain Haskell's account and the stated role of feudal families."),
    "st-chp2-seci-l3-7-neri-prophecy": (True, "Haskell reports a specific prophecy by Philip Neri about Maffeo's future cardinalate. Preserve the attribution and predicted rather than completed status."),
    "st-chp2-seci-l3-7-poetry-ancestor": (True, "Haskell tentatively links Maffeo's poetic interest to the reputation of his ancestor Francesco. Retain 'partly' and 'no doubt' as the author's qualified claim; Francesco's identity remains unresolved."),
    "st-chp2-seci-l3-7-preferment": (True, "The source directly says Maffeo advanced in papal preferment using his uncle's prestige and resources; retain the source's wording and attribution."),
    "st-chp2-seci-l3-7-restore-rome": (True, "The passage directly attributes to Sixtus V the effort to restore Rome's position as a world centre; preserve this as Haskell's historical characterization."),
    "st-chp2-seci-l3-7-school": (True, "The source directly states that Maffeo attended the Jesuit school and showed enthusiasm for classical literature; the school remains unnamed."),
    "st-chp2-seci-l3-7-sistine-rome": (False, "'Sistine Rome' is Haskell's descriptive term for the city under Sixtus V. The current person-to-term endpoints do not state a direct historical relation; preserve the phrase as authorial terminology."),
    "st-chp2-seci-l3-7-summoned": (True, "The source says Maffeo was called to Rome at sixteen by his uncle. Preserve Rome as destination, the age, and the uncle as the stated agent in the claim."),
    "st-chp2-seci-l3-7-uncle-court-posts": (True, "The source directly states that Monsignor Francesco held posts at the papal court; retain the source's nonspecific number of posts."),
    "st-chp2-seci-l3-7-urban-works": (True, "The passage directly attributes the described street, square, and water works to Sixtus V's urban program; retain the source's broad city-level scope."),
}

EXPECTED_ROWS = {
    "st-chp2-seci-l3-7-church-government": ("cand-3102", "cand-4244", "changed_government_of_church", 5, "changing the government of the Church"),
    "st-chp2-seci-l3-7-city-plan": ("cand-3102", "cand-3126", "reshaped_city_and_set_long_term_development", 5, "laying the outlines of its future development"),
    "st-chp2-seci-l3-7-conditional-rome-effect": ("cand-3104", "cand-3126", "conditional_effect_of_living_in_sixtine_rome", 5, "If so, the Rome of Sixtus V"),
    "st-chp2-seci-l3-7-family": ("cand-3104", "cand-0198", "born_into_family", 3, "old, distinguished"),
    "st-chp2-seci-l3-7-fontana-power": ("cand-3104", "cand-1045", "observed_architectural_work_as_example_of_power", 6, "gangs of workmen employed by Sixtus"),
    "st-chp2-seci-l3-7-lawlessness": ("cand-3102", "cand-4243", "suppressed_lawlessness_in_region", 5, "Lawlessness, encouraged by the ancient feudal families"),
    "st-chp2-seci-l3-7-neri-prophecy": ("cand-1898", "cand-3104", "reported_prediction_of_cardinalate", 4, "St Philip Neri prophesied"),
    "st-chp2-seci-l3-7-poetry-ancestor": ("cand-3104", "cand-4242", "poetic_interest_partly_attributed_to_ancestor", 4, "partly stimulated, no doubt"),
    "st-chp2-seci-l3-7-preferment": ("cand-3104", "cand-0208", "advanced_in_papal_preferment_using_uncle_resources", 4, "climb the ladder of papal preferment"),
    "st-chp2-seci-l3-7-restore-rome": ("cand-3102", "cand-3126", "sought_to_restore_world_centrality", 5, "give back to Rome its position as centre of the world"),
    "st-chp2-seci-l3-7-school": ("cand-3104", "cand-4240", "attended_school", 4, "went to a Jesuit school"),
    "st-chp2-seci-l3-7-sistine-rome": ("cand-3102", "cand-4245", "authorially_described_as_creating_sistine_rome", 5, "Sistine Rome"),
    "st-chp2-seci-l3-7-summoned": ("cand-3104", "cand-3126", "summoned_to_at_age", 4, "called to Rome by his uncle"),
    "st-chp2-seci-l3-7-uncle-court-posts": ("cand-0208", "cand-4241", "held_posts_at", 4, "posts at the papal court"),
    "st-chp2-seci-l3-7-urban-works": ("cand-3102", "cand-3126", "transformed_streets_squares_and_residential_areas", 5, "Streets were hacked through the clusters"),
}
EXPECTED_LINE_ENDS = {"st-chp2-seci-l3-7-family": 4}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_rows() -> list[dict]:
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

    rows = load_rows()
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(set(DECISIONS) == set(EXPECTED_ROWS), "decision and target sets differ")
    require(set(DECISIONS) <= set(by_id), "one or more target statements are missing")

    for statement_id, (subject, object_id, predicate, line, quote_anchor) in EXPECTED_ROWS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers", {})
        require(row.get("segment_id") == SEGMENT_ID, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_id,
                f"endpoint changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(qualifiers.get("source_line_start") == line
                and qualifiers.get("source_line_end") == EXPECTED_LINE_ENDS.get(statement_id, line),
                f"source line changed for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        require(quote_anchor in row.get("original_quote", ""), f"quote anchor changed for {statement_id}")

    coverage = [
        row for row in __import__("csv").DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline=""))
        if row.get("segment_id") == SEGMENT_ID
    ]
    require(len(coverage) == 1 and coverage[0].get("disposition") == "reviewed"
            and coverage[0].get("migration_status") == "complete", "coverage is not reviewed/complete")

    import csv
    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    segment_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    endpoints = {value for row in EXPECTED_ROWS.values() for value in row[:2]}
    require(endpoints <= segment_candidates, "one or more statement endpoints lack a segment mention")

    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8").splitlines()
    for statement_id, (_, _, _, line, quote_anchor) in EXPECTED_ROWS.items():
        require(quote_anchor in source_lines[line - 1], f"source anchor changed for {statement_id} at L{line}")

    before = counts(rows)
    require(before == {
        "statements": 12700,
        "relation_true": 3891,
        "relation_false": 1804,
        "true_bilateral": 3864,
        "true_open": 27,
        "false_bilateral": 439,
        "unclassified_bilateral": 4194,
    }, "current statement totals changed")
    return rows, before


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify the 15 bilateral statements in chapter 2 section i L3-7.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted classifications")
    args = parser.parse_args()
    rows, before = preflight()

    updated = [dict(row) for row in rows]
    for row in updated:
        statement_id = row.get("statement_id")
        if statement_id in DECISIONS:
            value, note = DECISIONS[statement_id]
            row["qualifiers"] = dict(row.get("qualifiers", {}))
            row["qualifiers"]["relation_candidate"] = value
            row["qualifiers"]["relation_candidate_note"] = note

    after = counts(updated)
    print(f"PREVIEW: {SEGMENT_ID}")
    for statement_id, (value, _) in DECISIONS.items():
        print(f"  {statement_id}: relation_candidate={value}")
    print("  no endpoint, predicate, source quote, candidate, mention or statement-count changes")
    print("  counts before:", json.dumps(before, sort_keys=True))
    print("  counts after: ", json.dumps(after, sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the classifications.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP)
    payload = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=STATEMENTS.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, STATEMENTS)
    print(f"APPLIED; backup: {BACKUP.relative_to(ROOT)}")
    print(f"new SHA-256: {sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
