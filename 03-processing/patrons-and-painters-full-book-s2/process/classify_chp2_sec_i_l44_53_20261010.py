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
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp2-sec-i-l44-53-20261010"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l44-53"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "12ba2cae55510eedc2a35c3fe2ef3837fe4cc7150adae1ff03e91ef680995bbb",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "e6179e8cf85a5313d16bad9b24a2d7a529b6d368a39ff6339270181f084888ad",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE_FILE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}

DECISIONS = {
    "st-chp2-seci-l44-53-castelli-architect": (True, "Haskell identifies Matteo Castelli as architect of the Barberini chapel project; retain the project's source-defined scope."),
    "st-chp2-seci-l44-53-chapel-expenditure": (True, "The source says Maffeo had this family chapel built for himself and reports his expenditure; preserve the boast and uncertain amount as attributed."),
    "st-chp2-seci-l44-53-chapel-site": (True, "Haskell directly says Maffeo chose S. Andrea della Valle for the chapel; retain the candidate's sub-entry identifying the church."),
    "st-chp2-seci-l44-53-del-monte-patronage": (True, "The source directly attributes Caravaggio's emerging attention to Cardinal del Monte's patronage; retain Haskell's attribution."),
    "st-chp2-seci-l44-53-este-treasures-looted": (False, "The passage says art treasures accumulated by the Este were looted during the takeover; the current object endpoint is the Este dynasty, not the unnamed collection or a named work. Preserve the authorial claim without treating the family itself as the looted object or asserting legal ownership."),
    "st-chp2-seci-l44-53-ferrara-mechanism": (True, "Haskell directly describes the diplomacy and pressure by which Ferrara was won; keep the mechanism attributed and do not assign unnamed agents."),
    "st-chp2-seci-l44-53-ferrara-visit": (True, "Maffeo is explicitly said to accompany Clement VIII on the 1598 Ferrara visit and takeover event; preserve the stated purpose and date."),
    "st-chp2-seci-l44-53-florentine-patronage": (True, "The referenced S. Andrea della Valle is the Churches index candidate's sub-entry; the source directly says the Rome-based Florentine colony patronized it. The group's formal organization remains unspecified."),
    "st-chp2-seci-l44-53-governorship": (True, "Haskell reports Maffeo as governor of Fano by 1592 at age 24; retain the reported date and role."),
    "st-chp2-seci-l44-53-inheritance-estimates": (True, "The source reports that Maffeo inherited a fortune from his uncle in 1600; preserve both divergent estimates without resolving the amount."),
    "st-chp2-seci-l44-53-marble-paul-example": (True, "Haskell says Paul V later adopted the described coloured-marble practice at the same basilica; retain the named example and source attribution."),
    "st-chp2-seci-l44-53-marble-sixtus-example": (True, "Haskell attributes an earlier introduction of the described marble practice at S. Maria Maggiore to Sixtus V; preserve the place and attribution."),
    "st-chp2-seci-l44-53-papal-entourage": (True, "The narrative explicitly says Clement VIII and his entourage took advantage of Ferrara after the takeover; retain this as Haskell's event-level claim."),
    "st-chp2-seci-l44-53-portrait-commission": (True, "Haskell reports that Maffeo had his portrait painted by the young Caravaggio around 1595; retain the approximate date and the separate artist attribution."),
    "st-chp2-seci-l44-53-sacrifice-commission": (True, "The source directly says Maffeo later commissioned the Abraham subject from the same artist; retain the work-level endpoint and footnote scope."),
    "st-chp2-seci-l44-53-tentative-portrait-identification": (True, "The source tentatively identifies the described painting as Maffeo's portrait; preserve 'is thought to be' and do not upgrade the identification."),
    "st-chp2-seci-l44-53-titian-influence": (False, "The source says 'these pictures' collectively helped lay foundations for a new style, while the current subject endpoint is only The Worship of Venus. Do not assign the group-level influence to one painting or infer a named style; retain the qualified claim without a single-work relation."),
    "st-chp2-seci-l44-53-urbino-lesson": (True, "Haskell explicitly links the Ferrara episode to Maffeo's later experience of Urbino's transfer to papal control as an interpretive lesson. Preserve the approximate interval and author's causal framing, not an independently proven policy effect."),
}

EXPECTED_ROWS = {
    "st-chp2-seci-l44-53-castelli-architect": ("cand-4252", "cand-0601", "architect_identified", 52, 52, "His architect, Matteo Castelli"),
    "st-chp2-seci-l44-53-chapel-expenditure": ("cand-3104", "cand-4252", "chapel_building_and_expenditure", 52, 52, "rich family chapel built for himself"),
    "st-chp2-seci-l44-53-chapel-site": ("cand-4252", "cand-0697", "chapel_site_selected", 52, 52, "recently begun Theatine church of S. Andrea della Valle"),
    "st-chp2-seci-l44-53-del-monte-patronage": ("cand-3010", "cand-1691", "patronage_reported", 45, 46, "patronage of Cardinal"),
    "st-chp2-seci-l44-53-este-treasures-looted": ("cand-4254", "cand-4247", "art_treasures_looted", 49, 49, "art treasures accumulated by the Este"),
    "st-chp2-seci-l44-53-ferrara-mechanism": ("cand-4254", "cand-1017", "reported_conquest_mechanism", 48, 48, "combination of firm diplomacy and unscrupulous pressure"),
    "st-chp2-seci-l44-53-ferrara-visit": ("cand-3104", "cand-4254", "accompanied_on_papal_visit", 48, 48, "Barberini accompanied Pope Clement VIII"),
    "st-chp2-seci-l44-53-florentine-patronage": ("cand-0697", "cand-4253", "church_patronized_by_community", 52, 52, "much patronised by the Florentine colony"),
    "st-chp2-seci-l44-53-governorship": ("cand-3104", "cand-4246", "governorship_reported", 45, 45, "governor of Fano"),
    "st-chp2-seci-l44-53-inheritance-estimates": ("cand-3104", "cand-0208", "inheritance_reported", 51, 52, "left him a fortune variously estimated"),
    "st-chp2-seci-l44-53-marble-paul-example": ("cand-4256", "cand-0393", "style_adoption_attributed", 53, 53, "adopted by Paul V"),
    "st-chp2-seci-l44-53-marble-sixtus-example": ("cand-4256", "cand-1874", "style_introduction_attributed", 52, 53, "introduced by\nSixtus V"),
    "st-chp2-seci-l44-53-papal-entourage": ("cand-0031", "cand-4254", "papal_entourage_action", 49, 49, "Pope and his entourage took full advantage"),
    "st-chp2-seci-l44-53-portrait-commission": ("cand-3104", "cand-4021", "portrait_commission", 45, 45, "had his portrait painted"),
    "st-chp2-seci-l44-53-sacrifice-commission": ("cand-3104", "cand-4251", "commissioned_subject_from_artist", 46, 46, "commission from him a subject"),
    "st-chp2-seci-l44-53-tentative-portrait-identification": ("cand-4021", "cand-3104", "tentative_portrait_identification", 46, 46, "thought to be this portrait"),
    "st-chp2-seci-l44-53-titian-influence": ("cand-4248", "cand-4255", "authorial_historical_influence", 50, 50, "these pictures attracted little attention"),
    "st-chp2-seci-l44-53-urbino-lesson": ("cand-3104", "cand-2669", "authorial_political_analogy", 48, 48, "learnt another lesson"),
}


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

    for statement_id, (subject, object_id, predicate, line_start, line_end, quote_anchor) in EXPECTED_ROWS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers", {})
        require(row.get("segment_id") == SEGMENT_ID, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_id,
                f"endpoint changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(qualifiers.get("source_line_start") == line_start and qualifiers.get("source_line_end") == line_end,
                f"source line changed for {statement_id}")
        require(flag(row) is None, f"already classified: {statement_id}")
        require(quote_anchor in row.get("original_quote", ""), f"quote anchor changed for {statement_id}")

    with (TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="") as handle:
        coverage = [row for row in csv.DictReader(handle) if row.get("segment_id") == SEGMENT_ID]
    require(len(coverage) == 1 and coverage[0].get("disposition") == "reviewed"
            and coverage[0].get("migration_status") == "complete", "coverage is not reviewed/complete")

    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as handle:
        mentions = list(csv.DictReader(handle))
    segment_candidates = {row.get("candidate_id") for row in mentions if row.get("segment_id") == SEGMENT_ID}
    endpoints = {value for row in EXPECTED_ROWS.values() for value in row[:2]}
    require(endpoints <= segment_candidates, "one or more statement endpoints lack a segment mention")

    source_lines = (ROOT / SOURCE_FILE).read_text(encoding="utf-8").splitlines()
    for statement_id, (_, _, _, line_start, line_end, quote_anchor) in EXPECTED_ROWS.items():
        excerpt = "\n".join(source_lines[line_start - 1:line_end])
        require(quote_anchor in excerpt, f"source anchor changed for {statement_id}")

    before = counts(rows)
    require(before == {
        "statements": 12700,
        "relation_true": 3904,
        "relation_false": 1806,
        "true_bilateral": 3877,
        "true_open": 27,
        "false_bilateral": 441,
        "unclassified_bilateral": 4179,
    }, "current statement totals changed")
    return rows, before


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify 18 bilateral statements in chapter 2 section i L44-53.")
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
